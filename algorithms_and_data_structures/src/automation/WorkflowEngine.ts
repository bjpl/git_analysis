import * as yaml from 'js-yaml';
import { EventEmitter } from 'events';
import { v4 as uuidv4 } from 'uuid';
import { promises as fs } from 'fs';
import * as path from 'path';
import { TaskRunner } from './TaskRunner';
import { SchedulerService } from './SchedulerService';

export interface WorkflowDefinition {
  name: string;
  version: string;
  description?: string;
  variables?: Record<string, any>;
  triggers?: WorkflowTrigger[];
  tasks: WorkflowTask[];
  onSuccess?: WorkflowTask[];
  onFailure?: WorkflowTask[];
  timeout?: number;
  retries?: number;
  rollback?: WorkflowTask[];
}

export interface WorkflowTrigger {
  type: 'cron' | 'event' | 'webhook' | 'manual' | 'file' | 'api';
  config: Record<string, any>;
  conditions?: WorkflowCondition[];
}

export interface WorkflowTask {
  id: string;
  name: string;
  type: string;
  config: Record<string, any>;
  dependsOn?: string[];
  condition?: WorkflowCondition;
  parallel?: boolean;
  timeout?: number;
  retries?: number;
  continueOnError?: boolean;
  variables?: Record<string, any>;
}

export interface WorkflowCondition {
  expression: string;
  variables?: Record<string, any>;
}

export interface WorkflowExecution {
  id: string;
  workflowId: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  startTime: Date;
  endTime?: Date;
  variables: Record<string, any>;
  taskResults: Record<string, any>;
  error?: Error;
  logs: WorkflowLog[];
  version: string;
  triggeredBy: string;
}

export interface WorkflowLog {
  timestamp: Date;
  level: 'info' | 'warn' | 'error' | 'debug';
  message: string;
  taskId?: string;
  data?: any;
}

export class WorkflowEngine extends EventEmitter {
  private workflows = new Map<string, WorkflowDefinition>();
  private executions = new Map<string, WorkflowExecution>();
  private taskRunner: TaskRunner;
  private scheduler: SchedulerService;
  private templatesPath: string;

  constructor(templatesPath: string = './templates/workflows') {
    super();
    this.templatesPath = templatesPath;
    this.taskRunner = new TaskRunner(this);
    this.scheduler = new SchedulerService(this);
    this.setupEventHandlers();
  }

  private setupEventHandlers(): void {
    this.on('workflow:started', this.handleWorkflowStarted.bind(this));
    this.on('workflow:completed', this.handleWorkflowCompleted.bind(this));
    this.on('workflow:failed', this.handleWorkflowFailed.bind(this));
    this.on('task:completed', this.handleTaskCompleted.bind(this));
    this.on('task:failed', this.handleTaskFailed.bind(this));
  }

  /**
   * Load workflow from YAML or JSON file
   */
  async loadWorkflow(filePath: string): Promise<string> {
    try {
      const content = await fs.readFile(filePath, 'utf-8');
      const ext = path.extname(filePath).toLowerCase();
      
      let workflow: WorkflowDefinition;
      if (ext === '.yaml' || ext === '.yml') {
        workflow = yaml.load(content) as WorkflowDefinition;
      } else if (ext === '.json') {
        workflow = JSON.parse(content);
      } else {
        throw new Error(`Unsupported workflow file format: ${ext}`);
      }

      return this.registerWorkflow(workflow);
    } catch (error) {
      throw new Error(`Failed to load workflow from ${filePath}: ${error.message}`);
    }
  }

  /**
   * Register workflow definition
   */
  registerWorkflow(workflow: WorkflowDefinition): string {
    this.validateWorkflow(workflow);
    const workflowId = this.generateWorkflowId(workflow.name);
    this.workflows.set(workflowId, workflow);
    
    // Register triggers with scheduler
    if (workflow.triggers) {
      workflow.triggers.forEach(trigger => {
        this.scheduler.registerTrigger(workflowId, trigger);
      });
    }

    this.emit('workflow:registered', { workflowId, workflow });
    return workflowId;
  }

  /**
   * Execute workflow
   */
  async executeWorkflow(
    workflowId: string, 
    variables: Record<string, any> = {},
    triggeredBy: string = 'manual'
  ): Promise<string> {
    const workflow = this.workflows.get(workflowId);
    if (!workflow) {
      throw new Error(`Workflow not found: ${workflowId}`);
    }

    const executionId = uuidv4();
    const execution: WorkflowExecution = {
      id: executionId,
      workflowId,
      status: 'pending',
      startTime: new Date(),
      variables: { ...workflow.variables, ...variables },
      taskResults: {},
      logs: [],
      version: workflow.version,
      triggeredBy
    };

    this.executions.set(executionId, execution);
    this.emit('workflow:started', execution);

    // Execute workflow asynchronously
    this.runWorkflow(execution).catch(error => {
      execution.status = 'failed';
      execution.error = error;
      execution.endTime = new Date();
      this.emit('workflow:failed', execution);
    });

    return executionId;
  }

  /**
   * Run workflow execution
   */
  private async runWorkflow(execution: WorkflowExecution): Promise<void> {
    try {
      execution.status = 'running';
      const workflow = this.workflows.get(execution.workflowId)!;

      this.log(execution, 'info', `Starting workflow: ${workflow.name}`);

      // Execute tasks based on dependencies
      await this.executeTaskGraph(execution, workflow.tasks);

      // Execute success tasks if provided
      if (workflow.onSuccess) {
        await this.executeTaskGraph(execution, workflow.onSuccess);
      }

      execution.status = 'completed';
      execution.endTime = new Date();
      this.emit('workflow:completed', execution);

      this.log(execution, 'info', 'Workflow completed successfully');

    } catch (error) {
      execution.status = 'failed';
      execution.error = error;
      execution.endTime = new Date();

      const workflow = this.workflows.get(execution.workflowId)!;
      
      // Execute failure tasks if provided
      if (workflow.onFailure) {
        try {
          await this.executeTaskGraph(execution, workflow.onFailure);
        } catch (failureError) {
          this.log(execution, 'error', `Failure handler error: ${failureError.message}`);
        }
      }

      // Execute rollback if provided
      if (workflow.rollback) {
        try {
          this.log(execution, 'info', 'Executing rollback tasks');
          await this.executeTaskGraph(execution, workflow.rollback);
        } catch (rollbackError) {
          this.log(execution, 'error', `Rollback error: ${rollbackError.message}`);
        }
      }

      this.emit('workflow:failed', execution);
      throw error;
    }
  }

  /**
   * Execute task graph with dependency resolution
   */
  private async executeTaskGraph(execution: WorkflowExecution, tasks: WorkflowTask[]): Promise<void> {
    const taskMap = new Map(tasks.map(task => [task.id, task]));
    const completed = new Set<string>();
    const running = new Set<string>();
    const failed = new Set<string>();

    // Find tasks with no dependencies or satisfied dependencies
    const getReadyTasks = (): WorkflowTask[] => {
      return tasks.filter(task => {
        if (completed.has(task.id) || running.has(task.id) || failed.has(task.id)) {
          return false;
        }
        
        if (!task.dependsOn) return true;
        
        return task.dependsOn.every(depId => completed.has(depId));
      });
    };

    // Execute tasks in parallel when possible
    while (completed.size + failed.size < tasks.length) {
      const readyTasks = getReadyTasks();
      
      if (readyTasks.length === 0) {
        const remainingTasks = tasks.filter(t => !completed.has(t.id) && !failed.has(t.id));
        throw new Error(`Circular dependency or failed dependency detected: ${remainingTasks.map(t => t.id).join(', ')}`);
      }

      // Group tasks by parallel execution
      const parallelTasks = readyTasks.filter(task => task.parallel);
      const sequentialTasks = readyTasks.filter(task => !task.parallel);

      // Execute parallel tasks concurrently
      if (parallelTasks.length > 0) {
        const parallelPromises = parallelTasks.map(async (task) => {
          running.add(task.id);
          try {
            await this.executeTask(execution, task);
            completed.add(task.id);
            running.delete(task.id);
          } catch (error) {
            failed.add(task.id);
            running.delete(task.id);
            if (!task.continueOnError) {
              throw error;
            }
          }
        });

        await Promise.all(parallelPromises);
      }

      // Execute sequential tasks one by one
      for (const task of sequentialTasks) {
        running.add(task.id);
        try {
          await this.executeTask(execution, task);
          completed.add(task.id);
          running.delete(task.id);
        } catch (error) {
          failed.add(task.id);
          running.delete(task.id);
          if (!task.continueOnError) {
            throw error;
          }
        }
      }
    }
  }

  /**
   * Execute individual task
   */
  private async executeTask(execution: WorkflowExecution, task: WorkflowTask): Promise<void> {
    this.log(execution, 'info', `Executing task: ${task.name}`, task.id);

    // Check condition if specified
    if (task.condition && !this.evaluateCondition(task.condition, execution.variables)) {
      this.log(execution, 'info', `Task skipped due to condition: ${task.name}`, task.id);
      return;
    }

    const taskVariables = { ...execution.variables, ...task.variables };
    const processedConfig = this.processTemplates(task.config, taskVariables);

    try {
      const result = await this.taskRunner.executeTask(task.type, processedConfig, {
        executionId: execution.id,
        taskId: task.id,
        variables: taskVariables,
        timeout: task.timeout,
        retries: task.retries || 0
      });

      execution.taskResults[task.id] = result;
      this.emit('task:completed', { execution, task, result });
      this.log(execution, 'info', `Task completed: ${task.name}`, task.id);

    } catch (error) {
      this.log(execution, 'error', `Task failed: ${task.name} - ${error.message}`, task.id);
      this.emit('task:failed', { execution, task, error });
      throw error;
    }
  }

  /**
   * Process template variables in configuration
   */
  private processTemplates(config: any, variables: Record<string, any>): any {
    const processValue = (value: any): any => {
      if (typeof value === 'string') {
        return value.replace(/\{\{([^}]+)\}\}/g, (match, expr) => {
          const trimmed = expr.trim();
          return this.evaluateExpression(trimmed, variables);
        });
      } else if (Array.isArray(value)) {
        return value.map(processValue);
      } else if (value && typeof value === 'object') {
        const processed: any = {};
        for (const [key, val] of Object.entries(value)) {
          processed[key] = processValue(val);
        }
        return processed;
      }
      return value;
    };

    return processValue(config);
  }

  /**
   * Evaluate condition expression
   */
  private evaluateCondition(condition: WorkflowCondition, variables: Record<string, any>): boolean {
    const conditionVariables = { ...variables, ...condition.variables };
    try {
      return this.evaluateExpression(condition.expression, conditionVariables);
    } catch (error) {
      this.emit('error', new Error(`Condition evaluation failed: ${error.message}`));
      return false;
    }
  }

  /**
   * Safe expression evaluation
   */
  private evaluateExpression(expression: string, variables: Record<string, any>): any {
    // Simple variable substitution for now
    // In production, use a safe expression evaluator like JSONata
    const varPattern = /([a-zA-Z_][a-zA-Z0-9_]*)/g;
    let result = expression;
    
    result = result.replace(varPattern, (match) => {
      if (variables.hasOwnProperty(match)) {
        const value = variables[match];
        return typeof value === 'string' ? `"${value}"` : String(value);
      }
      return match;
    });

    try {
      // Basic evaluation - in production use a proper expression engine
      return Function(`"use strict"; return (${result})`)();
    } catch (error) {
      throw new Error(`Expression evaluation failed: ${expression}`);
    }
  }

  /**
   * Validate workflow definition
   */
  private validateWorkflow(workflow: WorkflowDefinition): void {
    if (!workflow.name || !workflow.version || !workflow.tasks) {
      throw new Error('Workflow must have name, version, and tasks');
    }

    // Validate task dependencies
    const taskIds = new Set(workflow.tasks.map(task => task.id));
    for (const task of workflow.tasks) {
      if (task.dependsOn) {
        for (const depId of task.dependsOn) {
          if (!taskIds.has(depId)) {
            throw new Error(`Task ${task.id} depends on non-existent task: ${depId}`);
          }
        }
      }
    }

    // Check for circular dependencies
    this.detectCircularDependencies(workflow.tasks);
  }

  /**
   * Detect circular dependencies in task graph
   */
  private detectCircularDependencies(tasks: WorkflowTask[]): void {
    const visited = new Set<string>();
    const recursionStack = new Set<string>();

    const hasCycle = (taskId: string, taskMap: Map<string, WorkflowTask>): boolean => {
      if (recursionStack.has(taskId)) return true;
      if (visited.has(taskId)) return false;

      visited.add(taskId);
      recursionStack.add(taskId);

      const task = taskMap.get(taskId);
      if (task?.dependsOn) {
        for (const depId of task.dependsOn) {
          if (hasCycle(depId, taskMap)) return true;
        }
      }

      recursionStack.delete(taskId);
      return false;
    };

    const taskMap = new Map(tasks.map(task => [task.id, task]));
    
    for (const task of tasks) {
      if (hasCycle(task.id, taskMap)) {
        throw new Error(`Circular dependency detected in task: ${task.id}`);
      }
    }
  }

  /**
   * Generate unique workflow ID
   */
  private generateWorkflowId(name: string): string {
    const sanitized = name.toLowerCase().replace(/[^a-z0-9]/g, '-');
    return `${sanitized}-${Date.now()}`;
  }

  /**
   * Log workflow execution event
   */
  private log(
    execution: WorkflowExecution, 
    level: 'info' | 'warn' | 'error' | 'debug', 
    message: string, 
    taskId?: string,
    data?: any
  ): void {
    const logEntry: WorkflowLog = {
      timestamp: new Date(),
      level,
      message,
      taskId,
      data
    };
    
    execution.logs.push(logEntry);
    this.emit('log', logEntry);
  }

  // Event handlers
  private handleWorkflowStarted(execution: WorkflowExecution): void {
    console.log(`Workflow started: ${execution.workflowId} (${execution.id})`);
  }

  private handleWorkflowCompleted(execution: WorkflowExecution): void {
    console.log(`Workflow completed: ${execution.workflowId} (${execution.id})`);
  }

  private handleWorkflowFailed(execution: WorkflowExecution): void {
    console.error(`Workflow failed: ${execution.workflowId} (${execution.id})`, execution.error);
  }

  private handleTaskCompleted(data: { execution: WorkflowExecution; task: WorkflowTask; result: any }): void {
    console.log(`Task completed: ${data.task.name} in workflow ${data.execution.workflowId}`);
  }

  private handleTaskFailed(data: { execution: WorkflowExecution; task: WorkflowTask; error: Error }): void {
    console.error(`Task failed: ${data.task.name} in workflow ${data.execution.workflowId}`, data.error);
  }

  // Public API methods
  getWorkflow(workflowId: string): WorkflowDefinition | undefined {
    return this.workflows.get(workflowId);
  }

  getExecution(executionId: string): WorkflowExecution | undefined {
    return this.executions.get(executionId);
  }

  listWorkflows(): Map<string, WorkflowDefinition> {
    return new Map(this.workflows);
  }

  listExecutions(): Map<string, WorkflowExecution> {
    return new Map(this.executions);
  }

  async cancelExecution(executionId: string): Promise<boolean> {
    const execution = this.executions.get(executionId);
    if (!execution || execution.status === 'completed' || execution.status === 'failed') {
      return false;
    }

    execution.status = 'cancelled';
    execution.endTime = new Date();
    this.emit('workflow:cancelled', execution);
    return true;
  }

  async saveWorkflow(workflow: WorkflowDefinition, format: 'yaml' | 'json' = 'yaml'): Promise<string> {
    const filename = `${workflow.name.toLowerCase().replace(/[^a-z0-9]/g, '-')}.${format}`;
    const filepath = path.join(this.templatesPath, filename);

    let content: string;
    if (format === 'yaml') {
      content = yaml.dump(workflow, { indent: 2, lineWidth: -1 });
    } else {
      content = JSON.stringify(workflow, null, 2);
    }

    await fs.writeFile(filepath, content, 'utf-8');
    return filepath;
  }

  getTaskRunner(): TaskRunner {
    return this.taskRunner;
  }

  getScheduler(): SchedulerService {
    return this.scheduler;
  }

  async shutdown(): Promise<void> {
    await this.scheduler.shutdown();
    this.removeAllListeners();
  }
}