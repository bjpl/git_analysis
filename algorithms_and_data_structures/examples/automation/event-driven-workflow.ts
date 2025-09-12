/**
 * Event-Driven Workflow Example
 * 
 * This example demonstrates event-driven automation using webhooks, event triggers,
 * and real-time workflow orchestration based on external events.
 */

import { WorkflowEngine, WorkflowDefinition } from '../../src/automation/WorkflowEngine';
import { SchedulerService, EventTrigger } from '../../src/automation/SchedulerService';
import { IntegrationHub, WebhookEvent } from '../../src/automation/IntegrationHub';

// Event-driven workflow definitions
const eventWorkflows: Record<string, WorkflowDefinition> = {
  'user-signup': {
    name: 'user-signup-workflow',
    version: '1.0.0',
    description: 'Automated workflow triggered when a new user signs up',
    variables: {
      welcome_email_template: 'welcome_template',
      user_onboarding_checklist: 'basic_onboarding',
      notification_channels: ['email', 'slack']
    },
    tasks: [
      {
        id: 'validate_user_data',
        name: 'Validate User Registration Data',
        type: 'condition',
        config: {
          condition: 'user_email && user_name && user_email.includes("@")'
        }
      },
      {
        id: 'create_user_profile',
        name: 'Create User Profile',
        type: 'http_request',
        depends_on: ['validate_user_data'],
        config: {
          url: 'https://api.company.com/users',
          method: 'POST',
          headers: {
            'Authorization': 'Bearer ${USER_API_TOKEN}',
            'Content-Type': 'application/json'
          },
          body: {
            email: '${user_email}',
            name: '${user_name}',
            signup_date: '${signup_timestamp}',
            source: '${signup_source}'
          }
        }
      },
      {
        id: 'setup_user_workspace',
        name: 'Setup User Workspace',
        type: 'http_request',
        depends_on: ['create_user_profile'],
        config: {
          url: 'https://api.company.com/workspaces',
          method: 'POST',
          body: {
            user_id: '${results.create_user_profile.body.id}',
            template: '${user_onboarding_checklist}'
          }
        },
        parallel: true
      },
      {
        id: 'send_welcome_email',
        name: 'Send Welcome Email',
        type: 'send_email',
        depends_on: ['create_user_profile'],
        config: {
          to: '${user_email}',
          template: '${welcome_email_template}',
          data: {
            user_name: '${user_name}',
            welcome_link: 'https://app.company.com/onboarding',
            support_email: 'support@company.com'
          }
        },
        parallel: true
      },
      {
        id: 'notify_sales_team',
        name: 'Notify Sales Team',
        type: 'http_request',
        depends_on: ['create_user_profile'],
        config: {
          url: '${SLACK_WEBHOOK_SALES}',
          method: 'POST',
          body: {
            text: '🎉 New user signup!',
            blocks: [
              {
                type: 'section',
                text: {
                  type: 'markdown',
                  text: `*New User Registered*\n` +
                        `Name: ${user_name}\n` +
                        `Email: ${user_email}\n` +
                        `Source: ${signup_source}\n` +
                        `Time: ${signup_timestamp}`
                }
              }
            ]
          }
        },
        condition: '${notify_sales} == true',
        parallel: true
      },
      {
        id: 'add_to_marketing_list',
        name: 'Add to Marketing Email List',
        type: 'http_request',
        depends_on: ['create_user_profile'],
        config: {
          url: 'https://api.mailchimp.com/3.0/lists/${MAILCHIMP_LIST_ID}/members',
          method: 'POST',
          headers: {
            'Authorization': 'Bearer ${MAILCHIMP_API_KEY}'
          },
          body: {
            email_address: '${user_email}',
            status: 'subscribed',
            merge_fields: {
              FNAME: '${user_name}',
              SIGNUP_SRC: '${signup_source}'
            }
          }
        },
        condition: '${add_to_marketing} == true',
        parallel: true
      },
      {
        id: 'schedule_follow_up',
        name: 'Schedule Follow-up Actions',
        type: 'set_variable',
        depends_on: ['send_welcome_email', 'setup_user_workspace'],
        config: {
          name: 'follow_up_scheduled',
          value: true
        }
      }
    ],
    error_handling: {
      on_failure: 'continue',
      notify: ['support@company.com']
    }
  },

  'deployment-complete': {
    name: 'deployment-complete-workflow',
    version: '1.0.0',
    description: 'Post-deployment workflow for monitoring and validation',
    variables: {
      monitoring_duration: 300000, // 5 minutes
      health_check_interval: 30000, // 30 seconds
      rollback_threshold: 5 // 5 failed health checks
    },
    tasks: [
      {
        id: 'initial_health_check',
        name: 'Initial Deployment Health Check',
        type: 'http_request',
        config: {
          url: '${deployment_url}/health',
          method: 'GET',
          timeout: 10000
        },
        retry: {
          max_attempts: 5,
          delay: 10000,
          backoff_factor: 1.5
        }
      },
      {
        id: 'update_monitoring_alerts',
        name: 'Update Monitoring Alerts',
        type: 'http_request',
        depends_on: ['initial_health_check'],
        config: {
          url: 'https://api.monitoring.com/alerts',
          method: 'POST',
          body: {
            service: '${service_name}',
            version: '${deployment_version}',
            environment: '${environment}',
            status: 'deployed',
            monitoring_enabled: true
          }
        }
      },
      {
        id: 'continuous_monitoring',
        name: 'Continuous Health Monitoring',
        type: 'loop',
        depends_on: ['update_monitoring_alerts'],
        config: {
          items: Array.from({ length: 10 }, (_, i) => i), // Monitor for 10 intervals
          tasks: [
            {
              type: 'wait',
              config: { duration: '${health_check_interval}' }
            },
            {
              type: 'http_request',
              config: {
                url: '${deployment_url}/health',
                method: 'GET'
              }
            }
          ]
        }
      },
      {
        id: 'performance_baseline',
        name: 'Establish Performance Baseline',
        type: 'shell',
        depends_on: ['continuous_monitoring'],
        config: {
          command: |
            curl -w "@curl-format.txt" -o /dev/null -s "${deployment_url}/api/status"
            echo "Performance baseline established"
        }
      },
      {
        id: 'smoke_test_suite',
        name: 'Execute Smoke Test Suite',
        type: 'shell',
        depends_on: ['performance_baseline'],
        config: {
          command: 'npm run test:smoke:post-deploy',
          env: {
            BASE_URL: '${deployment_url}',
            SERVICE_VERSION: '${deployment_version}'
          }
        },
        parallel: true
      },
      {
        id: 'security_validation',
        name: 'Security Validation Check',
        type: 'shell',
        depends_on: ['performance_baseline'],
        config: {
          command: 'nmap -sS -O ${deployment_url} | grep -E "(open|filtered)"',
          timeout: 120000
        },
        parallel: true
      },
      {
        id: 'notify_deployment_success',
        name: 'Notify Deployment Success',
        type: 'http_request',
        depends_on: ['smoke_test_suite', 'security_validation'],
        config: {
          url: '${SLACK_WEBHOOK_DEVOPS}',
          method: 'POST',
          body: {
            text: '✅ Deployment validation completed successfully!',
            blocks: [
              {
                type: 'section',
                text: {
                  type: 'markdown',
                  text: `*Deployment Validated*\n` +
                        `Service: ${service_name}\n` +
                        `Version: ${deployment_version}\n` +
                        `Environment: ${environment}\n` +
                        `Health Status: Healthy\n` +
                        `Smoke Tests: Passed\n` +
                        `Security Check: Passed`
                }
              }
            ]
          }
        }
      }
    ],
    error_handling: {
      on_failure: 'rollback',
      notify: ['devops-team@company.com', 'oncall@company.com']
    }
  },

  'system-alert': {
    name: 'system-alert-workflow',
    version: '1.0.0',
    description: 'Automated response to system alerts and incidents',
    variables: {
      alert_severity_threshold: 'high',
      auto_remediation_enabled: true,
      escalation_timeout: 900000 // 15 minutes
    },
    tasks: [
      {
        id: 'classify_alert',
        name: 'Classify Alert Severity',
        type: 'condition',
        config: {
          condition: 'alert_severity == "critical" || alert_severity == "high"'
        }
      },
      {
        id: 'immediate_notification',
        name: 'Immediate Alert Notification',
        type: 'http_request',
        depends_on: ['classify_alert'],
        config: {
          url: '${PAGERDUTY_WEBHOOK}',
          method: 'POST',
          body: {
            incident_key: '${alert_id}',
            event_type: 'trigger',
            description: '${alert_message}',
            details: {
              severity: '${alert_severity}',
              source: '${alert_source}',
              timestamp: '${alert_timestamp}',
              affected_service: '${affected_service}'
            }
          }
        },
        condition: 'alert_severity == "critical"'
      },
      {
        id: 'gather_diagnostics',
        name: 'Gather System Diagnostics',
        type: 'parallel',
        depends_on: ['classify_alert'],
        config: {
          tasks: [
            {
              name: 'system_metrics',
              type: 'http_request',
              config: {
                url: 'https://monitoring.company.com/api/metrics',
                method: 'GET',
                params: {
                  service: '${affected_service}',
                  timerange: '30m'
                }
              }
            },
            {
              name: 'application_logs',
              type: 'shell',
              config: {
                command: 'kubectl logs -n ${namespace} -l app=${affected_service} --tail=100'
              }
            },
            {
              name: 'infrastructure_status',
              type: 'shell',
              config: {
                command: 'kubectl get pods,svc,ingress -n ${namespace}'
              }
            }
          ]
        }
      },
      {
        id: 'auto_remediation_attempt',
        name: 'Attempt Automated Remediation',
        type: 'condition',
        depends_on: ['gather_diagnostics'],
        config: {
          condition: '${auto_remediation_enabled} == true && alert_type == "service_down"'
        }
      },
      {
        id: 'restart_service',
        name: 'Restart Affected Service',
        type: 'shell',
        depends_on: ['auto_remediation_attempt'],
        config: {
          command: 'kubectl rollout restart deployment/${affected_service} -n ${namespace}',
          timeout: 180000
        },
        condition: 'results.auto_remediation_attempt.result == true'
      },
      {
        id: 'validate_remediation',
        name: 'Validate Remediation Success',
        type: 'http_request',
        depends_on: ['restart_service'],
        config: {
          url: 'https://${affected_service}.company.com/health',
          method: 'GET'
        },
        retry: {
          max_attempts: 10,
          delay: 15000
        }
      },
      {
        id: 'escalate_if_failed',
        name: 'Escalate if Remediation Failed',
        type: 'http_request',
        depends_on: ['validate_remediation'],
        config: {
          url: '${SLACK_WEBHOOK_ONCALL}',
          method: 'POST',
          body: {
            text: '🚨 ESCALATION: Automated remediation failed',
            blocks: [
              {
                type: 'section',
                text: {
                  type: 'markdown',
                  text: `*Alert Escalation Required*\n` +
                        `Alert ID: ${alert_id}\n` +
                        `Severity: ${alert_severity}\n` +
                        `Service: ${affected_service}\n` +
                        `Auto-remediation: FAILED\n` +
                        `Manual intervention required`
                }
              }
            ]
          }
        },
        condition: 'results.validate_remediation.success == false'
      },
      {
        id: 'create_incident_report',
        name: 'Create Incident Report',
        type: 'template',
        depends_on: ['escalate_if_failed', 'validate_remediation'],
        config: {
          template: |
            # Incident Report: {{alert_id}}
            
            **Date:** {{alert_timestamp}}
            **Severity:** {{alert_severity}}
            **Affected Service:** {{affected_service}}
            **Duration:** {{incident_duration}}
            
            ## Alert Details
            {{alert_message}}
            
            ## Diagnostics Collected
            {{#each diagnostics}}
            ### {{name}}
            ```
            {{output}}
            ```
            {{/each}}
            
            ## Remediation Actions
            {{#if auto_remediation_attempted}}
            - Automated restart attempted: {{restart_success}}
            {{#if restart_success}}
            - Service restored automatically
            {{else}}
            - Escalated to on-call team
            {{/if}}
            {{else}}
            - Manual investigation required
            {{/if}}
            
            ## Follow-up Actions
            - [ ] Review alert thresholds
            - [ ] Update runbooks if needed
            - [ ] Implement additional monitoring
          output_file: 'incidents/incident-${alert_id}.md'
        }
      }
    ],
    error_handling: {
      on_failure: 'continue',
      notify: ['sre-team@company.com']
    }
  }
};

export async function eventDrivenWorkflowExample() {
  console.log('🎯 Event-Driven Workflow Automation Example');

  const workflowEngine = new WorkflowEngine();
  const scheduler = new SchedulerService();
  const integrationHub = new IntegrationHub();

  // Connect services
  scheduler.setWorkflowEngine(workflowEngine);

  try {
    // Load all event-driven workflows
    console.log('📋 Loading event-driven workflows...');
    for (const [name, workflow] of Object.entries(eventWorkflows)) {
      await workflowEngine.loadWorkflow(JSON.stringify(workflow), 'json');
      console.log(`   ✅ Loaded: ${name}`);
    }

    // Set up event monitoring
    setupEventMonitoring(workflowEngine, scheduler, integrationHub);

    // Configure event triggers
    await setupEventTriggers(scheduler);

    // Set up webhook server for receiving events
    await integrationHub.startWebhookServer(3001);

    // Register webhook handlers
    setupWebhookHandlers(integrationHub, scheduler);

    console.log('🎯 Event-driven system is now active and listening for events...');

    // Simulate some events for demonstration
    await simulateEvents(scheduler, integrationHub);

    console.log('✨ Event-driven workflow example completed!');

  } catch (error) {
    console.error('❌ Error in event-driven workflow example:', error);
    throw error;
  } finally {
    // Cleanup
    await integrationHub.stopWebhookServer();
    scheduler.stop();
  }
}

function setupEventMonitoring(
  workflowEngine: WorkflowEngine,
  scheduler: SchedulerService,
  integrationHub: IntegrationHub
) {
  // Workflow Engine Events
  workflowEngine.on('workflow_started', (data) => {
    console.log(`🚀 Event-triggered workflow started: ${data.workflow} (${data.id})`);
  });

  workflowEngine.on('workflow_completed', (data) => {
    console.log(`✅ Event-triggered workflow completed: ${data.id}`);
  });

  workflowEngine.on('workflow_failed', (data) => {
    console.error(`❌ Event-triggered workflow failed: ${data.id} - ${data.error}`);
  });

  // Scheduler Events
  scheduler.on('event_trigger_added', (data) => {
    console.log(`📡 Event trigger added: ${data.event} (${data.triggerId})`);
  });

  scheduler.on('scheduled_execution_started', (data) => {
    console.log(`⏰ Scheduled execution started: ${data.workflow} (${data.workflowId})`);
  });

  // Integration Hub Events
  integrationHub.on('webhook_received', (data) => {
    console.log(`📨 Webhook received: ${data.event.event} from ${data.integrationId}`);
  });

  integrationHub.on('webhook_server_started', (data) => {
    console.log(`🌐 Webhook server started on port ${data.port}`);
  });
}

async function setupEventTriggers(scheduler: SchedulerService) {
  console.log('⚙️  Setting up event triggers...');

  const triggers: EventTrigger[] = [
    {
      id: 'user_signup_trigger',
      event: 'user.signup',
      workflow: 'user-signup-workflow',
      enabled: true,
      variables: {
        notify_sales: true,
        add_to_marketing: true,
        welcome_email_template: 'premium_welcome'
      },
      condition: 'user_email && user_name'
    },
    {
      id: 'deployment_trigger',
      event: 'deployment.complete',
      workflow: 'deployment-complete-workflow',
      enabled: true,
      variables: {
        monitoring_duration: 600000, // 10 minutes for production
        health_check_interval: 20000  // 20 seconds
      },
      condition: 'deployment_status == "success" && environment == "production"'
    },
    {
      id: 'critical_alert_trigger',
      event: 'system.alert.critical',
      workflow: 'system-alert-workflow',
      enabled: true,
      variables: {
        auto_remediation_enabled: true,
        alert_severity_threshold: 'critical'
      }
    },
    {
      id: 'high_alert_trigger',
      event: 'system.alert.high',
      workflow: 'system-alert-workflow',
      enabled: true,
      variables: {
        auto_remediation_enabled: false,
        alert_severity_threshold: 'high'
      }
    }
  ];

  for (const trigger of triggers) {
    scheduler.addEventTrigger(trigger);
    console.log(`   🎯 Added trigger: ${trigger.event} → ${trigger.workflow}`);
  }
}

function setupWebhookHandlers(integrationHub: IntegrationHub, scheduler: SchedulerService) {
  console.log('🔗 Setting up webhook handlers...');

  // User signup webhook
  integrationHub.registerWebhookHandler('/webhook/user-signup', {
    path: '/webhook/user-signup',
    events: ['user.created'],
    handle: (event: WebhookEvent) => {
      const { user_email, user_name, signup_source } = event.payload;
      
      console.log(`👤 User signup webhook received: ${user_email}`);
      
      // Trigger user signup workflow
      scheduler.triggerEvent('user.signup', {
        user_email,
        user_name,
        signup_source: signup_source || 'website',
        signup_timestamp: new Date().toISOString()
      });
    }
  });

  // Deployment webhook
  integrationHub.registerWebhookHandler('/webhook/deployment', {
    path: '/webhook/deployment',
    events: ['deployment.complete'],
    handle: (event: WebhookEvent) => {
      const { service_name, version, environment, deployment_url } = event.payload;
      
      console.log(`🚀 Deployment webhook received: ${service_name} v${version} to ${environment}`);
      
      // Trigger deployment workflow
      scheduler.triggerEvent('deployment.complete', {
        service_name,
        deployment_version: version,
        environment,
        deployment_url,
        deployment_timestamp: new Date().toISOString()
      });
    }
  });

  // System alert webhook
  integrationHub.registerWebhookHandler('/webhook/alerts', {
    path: '/webhook/alerts',
    events: ['alert.triggered'],
    handle: (event: WebhookEvent) => {
      const { alert_id, severity, message, source, affected_service } = event.payload;
      
      console.log(`🚨 Alert webhook received: ${severity} - ${message}`);
      
      // Trigger appropriate alert workflow based on severity
      const eventName = severity === 'critical' 
        ? 'system.alert.critical' 
        : 'system.alert.high';
        
      scheduler.triggerEvent(eventName, {
        alert_id,
        alert_severity: severity,
        alert_message: message,
        alert_source: source,
        affected_service,
        alert_timestamp: new Date().toISOString()
      });
    }
  });

  console.log('   ✅ Webhook handlers configured');
}

async function simulateEvents(scheduler: SchedulerService, integrationHub: IntegrationHub) {
  console.log('🎭 Simulating events for demonstration...');

  // Wait a moment for setup to complete
  await new Promise(resolve => setTimeout(resolve, 1000));

  // Simulate user signup event
  console.log('\n📧 Simulating user signup event...');
  await scheduler.triggerEvent('user.signup', {
    user_email: 'demo.user@example.com',
    user_name: 'Demo User',
    signup_source: 'demo',
    signup_timestamp: new Date().toISOString()
  });

  // Wait for workflow to process
  await new Promise(resolve => setTimeout(resolve, 2000));

  // Simulate deployment completion
  console.log('\n🚀 Simulating deployment completion event...');
  await scheduler.triggerEvent('deployment.complete', {
    service_name: 'demo-service',
    deployment_version: 'v1.2.3',
    environment: 'production',
    deployment_url: 'https://demo-service.company.com',
    deployment_status: 'success',
    deployment_timestamp: new Date().toISOString()
  });

  // Wait for workflow to process
  await new Promise(resolve => setTimeout(resolve, 2000));

  // Simulate system alert
  console.log('\n🚨 Simulating system alert event...');
  await scheduler.triggerEvent('system.alert.high', {
    alert_id: 'ALERT-' + Math.random().toString(36).substr(2, 9),
    alert_severity: 'high',
    alert_message: 'High CPU usage detected on demo-service',
    alert_source: 'prometheus',
    affected_service: 'demo-service',
    alert_timestamp: new Date().toISOString(),
    alert_type: 'cpu_threshold'
  });

  // Wait for workflows to complete
  await new Promise(resolve => setTimeout(resolve, 5000));

  console.log('✨ Event simulation completed');
}

// Real-time event monitoring example
export async function realTimeMonitoringExample() {
  console.log('📊 Real-Time Event Monitoring Example');

  const workflowEngine = new WorkflowEngine();
  const scheduler = new SchedulerService();

  scheduler.setWorkflowEngine(workflowEngine);

  // Load monitoring workflow
  const monitoringWorkflow: WorkflowDefinition = {
    name: 'real-time-monitoring',
    version: '1.0.0',
    description: 'Real-time system monitoring with automated responses',
    variables: {
      check_interval: 30000,
      alert_threshold: 80,
      monitoring_endpoints: [
        'https://api.service1.com/health',
        'https://api.service2.com/health',
        'https://api.service3.com/health'
      ]
    },
    tasks: [
      {
        id: 'monitor_services',
        name: 'Monitor Service Health',
        type: 'loop',
        config: {
          items: '${monitoring_endpoints}',
          tasks: [
            {
              type: 'http_request',
              config: {
                url: '${item}',
                method: 'GET',
                timeout: 10000
              }
            }
          ]
        }
      },
      {
        id: 'evaluate_health',
        name: 'Evaluate Overall Health',
        type: 'condition',
        depends_on: ['monitor_services'],
        config: {
          condition: 'results.monitor_services.filter(r => !r.success).length == 0'
        }
      },
      {
        id: 'trigger_alerts',
        name: 'Trigger Alerts if Needed',
        type: 'http_request',
        depends_on: ['evaluate_health'],
        config: {
          url: 'https://hooks.slack.com/webhook-url',
          method: 'POST',
          body: {
            text: '⚠️  Service health check failed',
            blocks: [
              {
                type: 'section',
                text: {
                  type: 'markdown',
                  text: 'One or more services are not responding to health checks'
                }
              }
            ]
          }
        },
        condition: 'results.evaluate_health.result == false'
      }
    ]
  };

  await workflowEngine.loadWorkflow(JSON.stringify(monitoringWorkflow), 'json');

  // Set up recurring monitoring
  const monitoringScheduleId = scheduler.scheduleRecurringExecution(
    'real-time-monitoring',
    30000, // Every 30 seconds
    {},
    100 // Run 100 times (50 minutes)
  );

  console.log(`📊 Real-time monitoring started (Schedule ID: ${monitoringScheduleId})`);

  // Monitor for a short demo period
  await new Promise(resolve => setTimeout(resolve, 10000)); // 10 seconds

  scheduler.disableSchedule(monitoringScheduleId);
  scheduler.stop();

  console.log('📊 Real-time monitoring example completed');
}

// Main execution
async function main() {
  try {
    console.log('🎬 Starting Event-Driven Workflow Examples\n');

    await eventDrivenWorkflowExample();
    console.log('\n' + '='.repeat(80) + '\n');

    await realTimeMonitoringExample();

    console.log('\n🏆 All event-driven workflow examples completed successfully!');
  } catch (error) {
    console.error('💥 Error running event-driven workflow examples:', error);
    process.exit(1);
  }
}

// Run if this file is executed directly
if (require.main === module) {
  main();
}

export {
  eventDrivenWorkflowExample,
  realTimeMonitoringExample
};