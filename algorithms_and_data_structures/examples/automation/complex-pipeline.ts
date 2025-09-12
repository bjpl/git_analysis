/**
 * Complex Pipeline Example
 * 
 * This example demonstrates a sophisticated CI/CD pipeline with multiple stages,
 * parallel execution, conditional logic, error handling, and integration points.
 */

import { WorkflowEngine, WorkflowDefinition } from '../../src/automation/WorkflowEngine';
import { AutomationBuilder } from '../../src/automation/AutomationBuilder';
import { IntegrationHub } from '../../src/automation/IntegrationHub';
import { SchedulerService } from '../../src/automation/SchedulerService';

async function complexPipelineExample() {
  console.log('🏗️ Complex Pipeline Automation Example');

  const workflowEngine = new WorkflowEngine();
  const automationBuilder = new AutomationBuilder();
  const integrationHub = new IntegrationHub();
  const scheduler = new SchedulerService();

  // Connect services
  scheduler.setWorkflowEngine(workflowEngine);

  // Define a complex CI/CD pipeline workflow
  const complexPipeline: WorkflowDefinition = {
    name: 'complex-cicd-pipeline',
    version: '2.0.0',
    description: 'Full-featured CI/CD pipeline with multiple environments and integration points',
    variables: {
      repository: 'https://github.com/company/application.git',
      branch: 'main',
      environment: 'production',
      notification_slack_webhook: '${SLACK_WEBHOOK_URL}',
      docker_registry: 'registry.company.com',
      k8s_namespace: 'production',
      performance_threshold: 500,
      coverage_threshold: 85,
      security_scan_enabled: true
    },
    triggers: [
      {
        type: 'webhook',
        config: {
          path: '/webhook/pipeline',
          secret: '${PIPELINE_WEBHOOK_SECRET}',
          events: ['push', 'pull_request']
        }
      },
      {
        type: 'schedule',
        config: {
          cron: '0 2 * * *' // Daily at 2 AM
        }
      }
    ],
    tasks: [
      // Stage 1: Setup and Validation
      {
        id: 'pipeline_init',
        name: 'Initialize Pipeline',
        type: 'log',
        config: {
          level: 'info',
          message: 'Starting complex CI/CD pipeline for ${repository} branch ${branch}'
        }
      },
      {
        id: 'validate_environment',
        name: 'Validate Environment Variables',
        type: 'condition',
        depends_on: ['pipeline_init'],
        config: {
          condition: 'DOCKER_REGISTRY && K8S_CONFIG && SLACK_WEBHOOK_URL'
        }
      },
      {
        id: 'checkout_source',
        name: 'Checkout Source Code',
        type: 'git',
        depends_on: ['validate_environment'],
        config: {
          action: 'clone',
          repository: '${repository}',
          branch: '${branch}',
          path: '/tmp/pipeline-workspace'
        },
        retry: {
          max_attempts: 3,
          delay: 5000,
          backoff_factor: 2
        }
      },

      // Stage 2: Build and Test (Parallel)
      {
        id: 'install_dependencies',
        name: 'Install Dependencies',
        type: 'shell',
        depends_on: ['checkout_source'],
        config: {
          command: 'npm ci --production=false',
          cwd: '/tmp/pipeline-workspace'
        },
        timeout: 300000
      },
      {
        id: 'lint_code',
        name: 'Lint Source Code',
        type: 'shell',
        depends_on: ['install_dependencies'],
        config: {
          command: 'npm run lint -- --format=json --output-file=lint-results.json',
          cwd: '/tmp/pipeline-workspace'
        },
        parallel: true
      },
      {
        id: 'type_check',
        name: 'TypeScript Type Checking',
        type: 'shell',
        depends_on: ['install_dependencies'],
        config: {
          command: 'npm run type-check',
          cwd: '/tmp/pipeline-workspace'
        },
        parallel: true
      },
      {
        id: 'unit_tests',
        name: 'Run Unit Tests',
        type: 'shell',
        depends_on: ['install_dependencies'],
        config: {
          command: 'npm run test:unit -- --coverage --coverageReporters=json',
          cwd: '/tmp/pipeline-workspace',
          env: {
            NODE_ENV: 'test',
            CI: 'true'
          }
        },
        parallel: true,
        timeout: 600000
      },
      {
        id: 'integration_tests',
        name: 'Run Integration Tests',
        type: 'shell',
        depends_on: ['install_dependencies'],
        config: {
          command: 'npm run test:integration',
          cwd: '/tmp/pipeline-workspace',
          env: {
            DATABASE_URL: '${TEST_DATABASE_URL}',
            REDIS_URL: '${TEST_REDIS_URL}'
          }
        },
        parallel: true,
        timeout: 900000
      },

      // Stage 3: Quality Gates
      {
        id: 'validate_coverage',
        name: 'Validate Test Coverage',
        type: 'shell',
        depends_on: ['unit_tests'],
        config: {
          command: |
            COVERAGE=$(cat coverage/coverage-summary.json | jq '.total.lines.pct')
            if (( $(echo "$COVERAGE < ${coverage_threshold}" | bc -l) )); then
              echo "Coverage $COVERAGE% is below threshold ${coverage_threshold}%"
              exit 1
            fi
            echo "Coverage validation passed: $COVERAGE%"
        }
      },
      {
        id: 'security_scan',
        name: 'Security Vulnerability Scan',
        type: 'shell',
        depends_on: ['lint_code', 'type_check'],
        config: {
          command: |
            npm audit --audit-level=moderate --json > security-audit.json
            VULNERABILITIES=$(cat security-audit.json | jq '.metadata.vulnerabilities.total')
            if [ $VULNERABILITIES -gt 0 ]; then
              echo "Security vulnerabilities found: $VULNERABILITIES"
              exit 1
            fi
        },
        condition: '${security_scan_enabled} == true'
      },

      // Stage 4: Build and Package
      {
        id: 'build_application',
        name: 'Build Application',
        type: 'shell',
        depends_on: ['validate_coverage', 'security_scan', 'integration_tests'],
        config: {
          command: 'npm run build',
          cwd: '/tmp/pipeline-workspace',
          env: {
            NODE_ENV: 'production',
            BUILD_VERSION: '${BUILD_NUMBER}',
            GIT_COMMIT: '${GIT_SHA}'
          }
        },
        timeout: 600000
      },
      {
        id: 'build_docker_image',
        name: 'Build Docker Image',
        type: 'shell',
        depends_on: ['build_application'],
        config: {
          command: |
            IMAGE_TAG="${docker_registry}/application:${BUILD_NUMBER}"
            docker build -t $IMAGE_TAG .
            docker tag $IMAGE_TAG ${docker_registry}/application:latest
            echo "IMAGE_TAG=$IMAGE_TAG" >> pipeline.env
          cwd: '/tmp/pipeline-workspace'
        }
      },
      {
        id: 'scan_docker_image',
        name: 'Scan Docker Image for Vulnerabilities',
        type: 'shell',
        depends_on: ['build_docker_image'],
        config: {
          command: |
            source pipeline.env
            trivy image --exit-code 1 --severity HIGH,CRITICAL $IMAGE_TAG
        },
        condition: '${security_scan_enabled} == true'
      },

      // Stage 5: Deploy to Staging
      {
        id: 'push_docker_image',
        name: 'Push Docker Image',
        type: 'shell',
        depends_on: ['scan_docker_image'],
        config: {
          command: |
            source pipeline.env
            docker push $IMAGE_TAG
            docker push ${docker_registry}/application:latest
        }
      },
      {
        id: 'deploy_staging',
        name: 'Deploy to Staging Environment',
        type: 'shell',
        depends_on: ['push_docker_image'],
        config: {
          command: |
            source pipeline.env
            helm upgrade --install application-staging ./helm-chart \
              --namespace staging \
              --set image.repository=${docker_registry}/application \
              --set image.tag=${BUILD_NUMBER} \
              --set environment=staging \
              --wait --timeout=10m
        }
      },

      // Stage 6: Staging Tests
      {
        id: 'staging_health_check',
        name: 'Staging Health Check',
        type: 'http_request',
        depends_on: ['deploy_staging'],
        config: {
          url: 'https://staging.application.company.com/health',
          method: 'GET',
          timeout: 30000
        },
        retry: {
          max_attempts: 10,
          delay: 15000,
          backoff_factor: 1.5
        }
      },
      {
        id: 'e2e_tests_staging',
        name: 'End-to-End Tests on Staging',
        type: 'shell',
        depends_on: ['staging_health_check'],
        config: {
          command: 'npm run test:e2e',
          cwd: '/tmp/pipeline-workspace',
          env: {
            BASE_URL: 'https://staging.application.company.com',
            HEADLESS: 'true',
            BROWSER: 'chrome'
          }
        },
        timeout: 1800000 // 30 minutes
      },
      {
        id: 'performance_tests_staging',
        name: 'Performance Tests on Staging',
        type: 'shell',
        depends_on: ['staging_health_check'],
        config: {
          command: |
            k6 run --out json=performance-results.json performance-test.js
            AVG_RESPONSE=$(cat performance-results.json | jq '.metrics.http_req_duration.avg')
            if (( $(echo "$AVG_RESPONSE > ${performance_threshold}" | bc -l) )); then
              echo "Performance test failed: ${AVG_RESPONSE}ms > ${performance_threshold}ms"
              exit 1
            fi
            echo "Performance test passed: ${AVG_RESPONSE}ms"
          cwd: '/tmp/pipeline-workspace',
          env: {
            BASE_URL: 'https://staging.application.company.com'
          }
        },
        parallel: true
      },

      // Stage 7: Production Deployment (Conditional)
      {
        id: 'production_approval',
        name: 'Production Deployment Approval',
        type: 'wait',
        depends_on: ['e2e_tests_staging', 'performance_tests_staging'],
        config: {
          duration: 300000 // 5 minutes manual approval window
        },
        condition: '${environment} == "production" && ${branch} == "main"'
      },
      {
        id: 'deploy_production',
        name: 'Deploy to Production Environment',
        type: 'shell',
        depends_on: ['production_approval'],
        config: {
          command: |
            source pipeline.env
            helm upgrade --install application-prod ./helm-chart \
              --namespace ${k8s_namespace} \
              --set image.repository=${docker_registry}/application \
              --set image.tag=${BUILD_NUMBER} \
              --set environment=production \
              --set replicas=3 \
              --wait --timeout=15m
        },
        condition: '${environment} == "production"',
        timeout: 1200000 // 20 minutes
      },

      // Stage 8: Production Validation
      {
        id: 'production_health_check',
        name: 'Production Health Check',
        type: 'http_request',
        depends_on: ['deploy_production'],
        config: {
          url: 'https://api.application.company.com/health',
          method: 'GET',
          timeout: 30000
        },
        retry: {
          max_attempts: 15,
          delay: 20000,
          backoff_factor: 1.2
        },
        condition: '${environment} == "production"'
      },
      {
        id: 'smoke_tests_production',
        name: 'Smoke Tests on Production',
        type: 'shell',
        depends_on: ['production_health_check'],
        config: {
          command: 'npm run test:smoke',
          cwd: '/tmp/pipeline-workspace',
          env: {
            BASE_URL: 'https://api.application.company.com'
          }
        },
        condition: '${environment} == "production"'
      },

      // Stage 9: Notifications and Cleanup
      {
        id: 'notify_success',
        name: 'Notify Deployment Success',
        type: 'http_request',
        depends_on: ['smoke_tests_production'],
        config: {
          url: '${notification_slack_webhook}',
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: {
            text: '✅ Pipeline completed successfully!',
            blocks: [
              {
                type: 'section',
                text: {
                  type: 'markdown',
                  text: `*Deployment Complete*\n` +
                        `Repository: ${repository}\n` +
                        `Branch: ${branch}\n` +
                        `Environment: ${environment}\n` +
                        `Build: ${BUILD_NUMBER}\n` +
                        `Commit: ${GIT_SHA}`
                }
              }
            ]
          }
        }
      },
      {
        id: 'cleanup_workspace',
        name: 'Cleanup Pipeline Workspace',
        type: 'shell',
        depends_on: ['notify_success'],
        config: {
          command: 'rm -rf /tmp/pipeline-workspace'
        }
      },
      {
        id: 'update_deployment_status',
        name: 'Update Deployment Status',
        type: 'http_request',
        depends_on: ['cleanup_workspace'],
        config: {
          url: 'https://api.company.com/deployments',
          method: 'POST',
          headers: {
            'Authorization': 'Bearer ${DEPLOYMENT_API_TOKEN}',
            'Content-Type': 'application/json'
          },
          body: {
            application: 'application',
            version: '${BUILD_NUMBER}',
            environment: '${environment}',
            status: 'success',
            deployed_at: '${new Date().toISOString()}',
            commit_sha: '${GIT_SHA}',
            pipeline_duration: '${duration_ms}'
          }
        }
      }
    ],
    error_handling: {
      on_failure: 'rollback',
      notify: ['devops-team@company.com', 'tech-leads@company.com']
    },
    rollback: {
      enabled: true,
      steps: [
        'rollback_deployment',
        'notify_rollback',
        'cleanup_failed_artifacts'
      ]
    }
  };

  try {
    console.log('📋 Loading complex pipeline workflow...');
    await workflowEngine.loadWorkflow(JSON.stringify(complexPipeline), 'json');

    // Set up comprehensive event monitoring
    setupEventMonitoring(workflowEngine);

    // Register GitHub integration for webhook handling
    await setupGitHubIntegration(integrationHub);

    console.log('▶️  Executing complex pipeline...');
    const workflowId = await workflowEngine.executeWorkflow(
      'complex-cicd-pipeline',
      {
        repository: 'https://github.com/company/sample-app.git',
        branch: 'main',
        environment: 'staging', // Start with staging for demo
        BUILD_NUMBER: `${Date.now()}`,
        GIT_SHA: 'abc123def456',
        coverage_threshold: 80,
        performance_threshold: 1000,
        security_scan_enabled: true,
        notification_slack_webhook: 'https://hooks.slack.com/webhook-url'
      }
    );

    // Monitor execution
    await monitorWorkflowExecution(workflowEngine, workflowId);

    console.log('🎉 Complex pipeline example completed successfully!');

  } catch (error) {
    console.error('❌ Error in complex pipeline example:', error);
    throw error;
  }
}

function setupEventMonitoring(workflowEngine: WorkflowEngine) {
  const startTime = Date.now();

  workflowEngine.on('workflow_started', (data) => {
    console.log(`🚀 Pipeline started: ${data.id}`);
  });

  workflowEngine.on('task_started', (data) => {
    console.log(`⚙️  Stage started: ${data.taskId}`);
  });

  workflowEngine.on('task_completed', (data) => {
    const duration = data.result.duration;
    console.log(`✅ Stage completed: ${data.taskId} (${duration}ms)`);
  });

  workflowEngine.on('task_failed', (data) => {
    console.error(`❌ Stage failed: ${data.taskId} - ${data.error}`);
  });

  workflowEngine.on('workflow_completed', (data) => {
    const totalDuration = Date.now() - startTime;
    console.log(`🏁 Pipeline completed: ${data.id} (Total: ${totalDuration}ms)`);
    
    // Log pipeline metrics
    const taskCount = Object.keys(data.results).length;
    const successfulTasks = Object.values(data.results).filter((r: any) => r.success).length;
    
    console.log(`📊 Pipeline Metrics:`);
    console.log(`   Total Tasks: ${taskCount}`);
    console.log(`   Successful: ${successfulTasks}`);
    console.log(`   Success Rate: ${((successfulTasks / taskCount) * 100).toFixed(1)}%`);
    console.log(`   Duration: ${totalDuration}ms`);
  });

  workflowEngine.on('workflow_rollback_started', (data) => {
    console.warn(`🔄 Rollback initiated for workflow: ${data.id}`);
  });

  workflowEngine.on('workflow_rollback_completed', (data) => {
    console.log(`↩️  Rollback completed for workflow: ${data.id}`);
  });
}

async function setupGitHubIntegration(integrationHub: IntegrationHub) {
  console.log('🔗 Setting up GitHub integration...');

  const githubIntegrationId = await integrationHub.registerIntegration({
    name: 'GitHub CI/CD Integration',
    type: 'github',
    config: {
      endpoint: 'https://api.github.com',
      authentication: {
        type: 'bearer',
        credentials: {
          token: process.env.GITHUB_TOKEN || 'mock-github-token'
        }
      },
      rateLimiting: {
        maxRequests: 5000,
        windowMs: 3600000,
        strategy: 'sliding'
      }
    },
    enabled: true,
    metadata: {
      purpose: 'CI/CD Pipeline Integration',
      created_at: new Date().toISOString()
    }
  });

  integrationHub.on('integration_registered', (data) => {
    console.log(`📡 GitHub integration registered: ${data.integrationId}`);
  });

  return githubIntegrationId;
}

async function monitorWorkflowExecution(workflowEngine: WorkflowEngine, workflowId: string) {
  return new Promise<void>((resolve, reject) => {
    const checkStatus = () => {
      const context = workflowEngine.getWorkflowStatus(workflowId);
      if (!context) {
        reject(new Error('Workflow context not found'));
        return;
      }

      if (context.status === 'completed') {
        resolve();
      } else if (context.status === 'failed') {
        reject(new Error(`Workflow failed: ${context.errors.map(e => e.message).join(', ')}`));
      } else {
        // Still running, check again
        setTimeout(checkStatus, 1000);
      }
    };

    checkStatus();
  });
}

// Demonstration of AutomationBuilder usage
async function automationBuilderExample() {
  console.log('🏗️ AutomationBuilder Visual Workflow Example');

  const builder = new AutomationBuilder();

  // Create a new workflow
  const workflow = builder.createWorkflow(
    'Visual Pipeline Builder Demo',
    'Demonstrates visual workflow building capabilities'
  );

  // Add workflow variables
  workflow.setVariable('api_endpoint', 'https://api.example.com');
  workflow.setVariable('timeout', 30000);

  // Add nodes to create a visual workflow
  const apiTestNode = {
    id: 'api_test',
    type: 'task' as const,
    position: { x: 200, y: 150 },
    data: {
      name: 'API Health Check',
      type: 'http_request',
      config: {
        url: '${api_endpoint}/health',
        method: 'GET',
        timeout: '${timeout}'
      }
    },
    connections: []
  };

  const validationNode = {
    id: 'validate_response',
    type: 'task' as const,
    position: { x: 350, y: 150 },
    data: {
      name: 'Validate API Response',
      type: 'condition',
      config: {
        condition: 'results.api_test.status == 200'
      }
    },
    connections: []
  };

  workflow.addNode(apiTestNode);
  workflow.addNode(validationNode);

  // Connect the nodes
  workflow.connect('start', 'api_test', 'success');
  workflow.connect('api_test', 'validate_response', 'success');
  workflow.connect('validate_response', 'end', 'success');

  // Validate the workflow
  console.log('🔍 Validating visual workflow...');
  const validationErrors = builder.validateWorkflow(workflow);
  
  if (validationErrors.length > 0) {
    console.log('⚠️  Validation warnings:');
    validationErrors.forEach(error => {
      console.log(`   ${error.type.toUpperCase()}: ${error.message}`);
    });
  } else {
    console.log('✅ Workflow validation passed');
  }

  // Generate code from visual workflow
  console.log('📄 Generating workflow code...');
  const generatedCode = builder.generateCode(workflow, 'json');
  console.log('Generated workflow definition:');
  console.log(generatedCode);

  // Test the workflow
  console.log('🧪 Testing visual workflow...');
  const testResult = await builder.testWorkflow(workflow, {
    api_endpoint: 'https://httpbin.org',
    timeout: 5000
  });

  console.log(`Test Result: ${testResult.success ? 'PASSED' : 'FAILED'}`);
  console.log(`Coverage: ${testResult.coverage.toFixed(1)}%`);
  console.log(`Duration: ${testResult.duration}ms`);

  if (testResult.errors.length > 0) {
    console.log('Test Errors:');
    testResult.errors.forEach(error => {
      console.log(`   ${error.type}: ${error.message}`);
    });
  }

  console.log('🏗️ AutomationBuilder example completed!');
}

// Main execution
async function main() {
  try {
    console.log('🎬 Starting Complex Pipeline Examples\n');

    await complexPipelineExample();
    console.log('\n' + '='.repeat(80) + '\n');

    await automationBuilderExample();

    console.log('\n🏆 All complex pipeline examples completed successfully!');
  } catch (error) {
    console.error('💥 Error running complex pipeline examples:', error);
    process.exit(1);
  }
}

// Run if this file is executed directly
if (require.main === module) {
  main();
}

export {
  complexPipelineExample,
  automationBuilderExample
};