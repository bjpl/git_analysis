import { WorkflowEngine } from '../../src/automation/WorkflowEngine';
import { TaskRunner } from '../../src/automation/TaskRunner';
import { SchedulerService } from '../../src/automation/SchedulerService';
import { AutomationBuilder } from '../../src/automation/AutomationBuilder';
import * as path from 'path';

/**
 * Simple Automation Example
 * 
 * This example demonstrates:
 * - Creating a basic workflow programmatically
 * - Using built-in tasks (file operations, HTTP requests)
 * - Variable substitution and templating
 * - Error handling and retries
 */

async function runSimpleAutomationExample() {
    console.log('🚀 Starting Simple Automation Example...\n');

    // Initialize the workflow engine
    const templatesPath = path.join(__dirname, '../../templates/workflows');
    const engine = new WorkflowEngine(templatesPath);

    try {
        // Example 1: Simple file processing workflow
        console.log('📝 Example 1: Simple File Processing');
        console.log('=====================================');
        
        const fileProcessingWorkflow = {
            name: 'Simple File Processing',
            version: '1.0.0',
            description: 'Read a file, transform it, and save the result',
            variables: {
                inputFile: path.join(__dirname, 'sample-input.txt'),
                outputFile: path.join(__dirname, 'processed-output.txt'),
                transformType: 'uppercase'
            },
            tasks: [
                {
                    id: 'create-input',
                    name: 'Create Input File',
                    type: 'file:write',
                    config: {
                        path: '{{inputFile}}',
                        content: 'Hello World!\nThis is a sample file.\nAutomation is awesome!'
                    }
                },
                {
                    id: 'read-file',
                    name: 'Read Input File',
                    type: 'file:read',
                    config: {
                        path: '{{inputFile}}',
                        encoding: 'utf8'
                    },
                    dependsOn: ['create-input'],
                    timeout: 5000,
                    retries: 2
                },
                {
                    id: 'transform-content',
                    name: 'Transform Content',
                    type: 'data:transform',
                    config: {
                        data: '{{read-file.content}}',
                        expression: 'data.toUpperCase()'
                    },
                    dependsOn: ['read-file']
                },
                {
                    id: 'write-result',
                    name: 'Write Processed File',
                    type: 'file:write',
                    config: {
                        path: '{{outputFile}}',
                        content: 'Processed Content:\n{{transform-content.result}}\n\nProcessed at: {{new Date().toISOString()}}'
                    },
                    dependsOn: ['transform-content']
                },
                {
                    id: 'log-completion',
                    name: 'Log Completion',
                    type: 'util:log',
                    config: {
                        message: 'File processing completed successfully!',
                        level: 'info',
                        data: {
                            inputFile: '{{inputFile}}',
                            outputFile: '{{outputFile}}',
                            processedAt: '{{new Date().toISOString()}}'
                        }
                    },
                    dependsOn: ['write-result']
                }
            ]
        };

        // Register and execute the workflow
        const workflowId = engine.registerWorkflow(fileProcessingWorkflow);
        console.log(`✅ Registered workflow: ${workflowId}`);

        const executionId = await engine.executeWorkflow(workflowId);
        console.log(`🚀 Started execution: ${executionId}`);

        // Wait for completion (in a real app, you'd use events)
        await waitForCompletion(engine, executionId);
        console.log('✅ File processing workflow completed!\n');

        // Example 2: HTTP API workflow with error handling
        console.log('🌐 Example 2: HTTP API Workflow');
        console.log('=================================');

        const apiWorkflow = {
            name: 'API Data Processing',
            version: '1.0.0',
            description: 'Fetch data from API and process it',
            variables: {
                apiUrl: 'https://jsonplaceholder.typicode.com/users',
                outputPath: path.join(__dirname, 'api-data.json')
            },
            tasks: [
                {
                    id: 'fetch-users',
                    name: 'Fetch Users from API',
                    type: 'http:request',
                    config: {
                        url: '{{apiUrl}}',
                        method: 'GET',
                        headers: {
                            'User-Agent': 'Automation-Example/1.0',
                            'Accept': 'application/json'
                        },
                        timeout: 10000
                    },
                    retries: 3
                },
                {
                    id: 'validate-response',
                    name: 'Validate API Response',
                    type: 'data:validate',
                    config: {
                        data: '{{fetch-users.data}}',
                        schema: {
                            type: 'array',
                            minItems: 1
                        }
                    },
                    dependsOn: ['fetch-users']
                },
                {
                    id: 'transform-users',
                    name: 'Transform User Data',
                    type: 'data:transform',
                    config: {
                        data: '{{fetch-users.data}}',
                        expression: `
                            data.map(user => ({
                                id: user.id,
                                name: user.name,
                                email: user.email,
                                company: user.company.name,
                                website: user.website
                            }))
                        `
                    },
                    dependsOn: ['validate-response']
                },
                {
                    id: 'save-data',
                    name: 'Save Processed Data',
                    type: 'file:write',
                    config: {
                        path: '{{outputPath}}',
                        content: JSON.stringify({
                            fetchedAt: '{{new Date().toISOString()}}',
                            userCount: '{{transform-users.result.length}}',
                            users: '{{transform-users.result}}'
                        }, null, 2)
                    },
                    dependsOn: ['transform-users']
                },
                {
                    id: 'generate-summary',
                    name: 'Generate Summary',
                    type: 'data:transform',
                    config: {
                        data: '{{transform-users.result}}',
                        expression: `({
                            totalUsers: data.length,
                            domains: [...new Set(data.map(u => u.email.split('@')[1]))],
                            companies: [...new Set(data.map(u => u.company))]
                        })`
                    },
                    dependsOn: ['transform-users']
                },
                {
                    id: 'log-summary',
                    name: 'Log Processing Summary',
                    type: 'util:log',
                    config: {
                        message: 'API data processing completed',
                        level: 'info',
                        data: '{{generate-summary.result}}'
                    },
                    dependsOn: ['save-data', 'generate-summary']
                }
            ],
            onFailure: [
                {
                    id: 'log-error',
                    name: 'Log Error',
                    type: 'util:log',
                    config: {
                        message: 'API workflow failed: {{error.message}}',
                        level: 'error',
                        data: {
                            error: '{{error}}',
                            timestamp: '{{new Date().toISOString()}}'
                        }
                    }
                }
            ]
        };

        const apiWorkflowId = engine.registerWorkflow(apiWorkflow);
        console.log(`✅ Registered API workflow: ${apiWorkflowId}`);

        const apiExecutionId = await engine.executeWorkflow(apiWorkflowId);
        console.log(`🚀 Started API execution: ${apiExecutionId}`);

        await waitForCompletion(engine, apiExecutionId);
        console.log('✅ API workflow completed!\n');

        // Example 3: Scheduled workflow
        console.log('⏰ Example 3: Scheduled Workflow');
        console.log('=================================');

        const scheduledWorkflow = {
            name: 'Scheduled Health Check',
            version: '1.0.0',
            description: 'Periodic health check with notifications',
            variables: {
                checkInterval: 30000, // 30 seconds for demo
                healthUrl: 'https://httpstat.us/200'
            },
            triggers: [
                {
                    type: 'cron',
                    config: {
                        schedule: '*/30 * * * * *', // Every 30 seconds for demo
                        timezone: 'UTC'
                    }
                }
            ],
            tasks: [
                {
                    id: 'health-check',
                    name: 'Perform Health Check',
                    type: 'http:request',
                    config: {
                        url: '{{healthUrl}}',
                        method: 'GET',
                        timeout: 5000
                    },
                    retries: 2
                },
                {
                    id: 'evaluate-health',
                    name: 'Evaluate Health Status',
                    type: 'data:transform',
                    config: {
                        data: '{{health-check}}',
                        expression: `({
                            healthy: data.status >= 200 && data.status < 300,
                            status: data.status,
                            timestamp: new Date().toISOString(),
                            responseTime: 'N/A'
                        })`
                    },
                    dependsOn: ['health-check']
                },
                {
                    id: 'log-status',
                    name: 'Log Health Status',
                    type: 'util:log',
                    config: {
                        message: 'Health check: {{evaluate-health.result.healthy ? "HEALTHY" : "UNHEALTHY"}}',
                        level: '{{evaluate-health.result.healthy ? "info" : "error"}}',
                        data: '{{evaluate-health.result}}'
                    },
                    dependsOn: ['evaluate-health']
                }
            ],
            timeout: 30000
        };

        const scheduledWorkflowId = engine.registerWorkflow(scheduledWorkflow);
        console.log(`✅ Registered scheduled workflow: ${scheduledWorkflowId}`);

        // Let it run for a few cycles
        console.log('⏳ Letting scheduled workflow run for 2 minutes...');
        await new Promise(resolve => setTimeout(resolve, 120000));

        console.log('✅ Scheduled workflow demonstration completed!\n');

        // Example 4: Using AutomationBuilder for visual workflow creation
        console.log('🎨 Example 4: Visual Workflow Builder');
        console.log('=====================================');

        const builder = new AutomationBuilder();
        
        // Create nodes programmatically
        const startNodeId = builder.addNode('start', { x: 100, y: 100 });
        const readNodeId = builder.addNode('task', { x: 300, y: 100 }, {
            name: 'Read Config',
            taskType: 'file:read',
            config: {
                path: 'config.json',
                encoding: 'utf8'
            }
        });
        const processNodeId = builder.addNode('task', { x: 500, y: 100 }, {
            name: 'Process Config',
            taskType: 'data:transform',
            config: {
                data: '{{read-config.content}}',
                expression: 'JSON.parse(data)'
            }
        });
        const endNodeId = builder.addNode('end', { x: 700, y: 100 });

        // Connect nodes
        builder.addConnection(startNodeId, readNodeId);
        builder.addConnection(readNodeId, processNodeId);
        builder.addConnection(processNodeId, endNodeId);

        // Set workflow metadata
        builder.setState({
            ...builder.getState(),
            variables: {
                environment: 'development',
                version: '1.0.0'
            },
            metadata: {
                name: 'Config Processing Workflow',
                description: 'Process configuration file'
            }
        });

        // Generate workflow definition
        const generatedWorkflow = builder.generateWorkflowDefinition();
        console.log('✅ Generated workflow from visual builder:');
        console.log(JSON.stringify(generatedWorkflow, null, 2));

        // Export as YAML
        const yamlExport = builder.exportAsYAML();
        console.log('\n📄 YAML Export:');
        console.log(yamlExport);

        console.log('\n✅ Visual workflow builder example completed!');

    } catch (error) {
        console.error('❌ Error in simple automation example:', error);
    } finally {
        // Cleanup
        console.log('\n🧹 Cleaning up...');
        await engine.shutdown();
        
        // Clean up example files
        const fs = require('fs').promises;
        try {
            await fs.unlink(path.join(__dirname, 'sample-input.txt'));
            await fs.unlink(path.join(__dirname, 'processed-output.txt'));
            await fs.unlink(path.join(__dirname, 'api-data.json'));
        } catch (e) {
            // Files might not exist, ignore errors
        }
        
        console.log('✅ Cleanup completed!');
    }
}

/**
 * Helper function to wait for workflow completion
 */
async function waitForCompletion(engine: WorkflowEngine, executionId: string): Promise<void> {
    return new Promise((resolve, reject) => {
        const checkStatus = () => {
            const execution = engine.getExecution(executionId);
            if (!execution) {
                reject(new Error('Execution not found'));
                return;
            }

            if (execution.status === 'completed') {
                console.log(`✅ Execution ${executionId} completed successfully`);
                resolve();
            } else if (execution.status === 'failed') {
                console.error(`❌ Execution ${executionId} failed:`, execution.error);
                reject(execution.error);
            } else {
                // Still running, check again
                setTimeout(checkStatus, 1000);
            }
        };

        checkStatus();
    });
}

/**
 * Example event handlers for workflow monitoring
 */
function setupEventHandlers(engine: WorkflowEngine) {
    engine.on('workflow:started', (execution) => {
        console.log(`🚀 Workflow started: ${execution.workflowId} (${execution.id})`);
    });

    engine.on('workflow:completed', (execution) => {
        console.log(`✅ Workflow completed: ${execution.workflowId} (${execution.id})`);
        console.log(`   Duration: ${execution.endTime!.getTime() - execution.startTime.getTime()}ms`);
    });

    engine.on('workflow:failed', (execution) => {
        console.error(`❌ Workflow failed: ${execution.workflowId} (${execution.id})`);
        console.error(`   Error: ${execution.error?.message}`);
    });

    engine.on('task:completed', (data) => {
        console.log(`   ✓ Task completed: ${data.task.name}`);
    });

    engine.on('task:failed', (data) => {
        console.error(`   ✗ Task failed: ${data.task.name} - ${data.error.message}`);
    });

    engine.on('log', (logEntry) => {
        const timestamp = logEntry.timestamp.toISOString();
        const level = logEntry.level.toUpperCase();
        const taskInfo = logEntry.taskId ? ` [${logEntry.taskId}]` : '';
        console.log(`[${timestamp}] ${level}${taskInfo}: ${logEntry.message}`);
    });
}

// Run the example if this file is executed directly
if (require.main === module) {
    runSimpleAutomationExample()
        .then(() => {
            console.log('\n🎉 Simple automation example completed successfully!');
            process.exit(0);
        })
        .catch((error) => {
            console.error('\n💥 Simple automation example failed:', error);
            process.exit(1);
        });
}

export { runSimpleAutomationExample };