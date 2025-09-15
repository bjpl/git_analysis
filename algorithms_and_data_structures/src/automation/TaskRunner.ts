import { EventEmitter } from 'events';
import { promises as fs } from 'fs';
import { exec } from 'child_process';
import { promisify } from 'util';
import axios, { AxiosRequestConfig } from 'axios';
import * as path from 'path';
import { v4 as uuidv4 } from 'uuid';

const execAsync = promisify(exec);

export interface TaskContext {
  executionId: string;
  taskId: string;
  variables: Record<string, any>;
  timeout?: number;
  retries?: number;
}

export interface TaskResult {
  success: boolean;
  output?: any;
  error?: string;
  duration: number;
  retryCount: number;
}

export interface TaskDefinition {
  name: string;
  description: string;
  inputs: Record<string, any>;
  outputs: Record<string, any>;
  handler: TaskHandler;
}

export type TaskHandler = (config: any, context: TaskContext) => Promise<any>;

export class TaskRunner extends EventEmitter {
  private tasks = new Map<string, TaskDefinition>();
  private activeExecutions = new Map<string, AbortController>();
  private resourcePools = new Map<string, ResourcePool>();

  constructor(private workflowEngine?: any) {
    super();
    this.registerBuiltInTasks();
    this.setupResourcePools();
  }

  /**
   * Register built-in task types
   */
  private registerBuiltInTasks(): void {
    // File Operations
    this.registerTask('file:read', {
      name: 'Read File',
      description: 'Read content from a file',
      inputs: { path: 'string', encoding: 'string?' },
      outputs: { content: 'string' },
      handler: this.handleFileRead.bind(this)
    });

    this.registerTask('file:write', {
      name: 'Write File',
      description: 'Write content to a file',
      inputs: { path: 'string', content: 'string', encoding: 'string?' },
      outputs: { bytesWritten: 'number' },
      handler: this.handleFileWrite.bind(this)
    });

    this.registerTask('file:copy', {
      name: 'Copy File',
      description: 'Copy a file from source to destination',
      inputs: { source: 'string', destination: 'string' },
      outputs: { success: 'boolean' },
      handler: this.handleFileCopy.bind(this)
    });

    this.registerTask('file:delete', {
      name: 'Delete File',
      description: 'Delete a file or directory',
      inputs: { path: 'string', recursive: 'boolean?' },
      outputs: { success: 'boolean' },
      handler: this.handleFileDelete.bind(this)
    });

    // Shell Commands
    this.registerTask('shell:exec', {
      name: 'Execute Shell Command',
      description: 'Execute a shell command',
      inputs: { command: 'string', cwd: 'string?', env: 'object?', shell: 'string?' },
      outputs: { stdout: 'string', stderr: 'string', exitCode: 'number' },
      handler: this.handleShellExec.bind(this)
    });

    // HTTP Operations
    this.registerTask('http:request', {
      name: 'HTTP Request',
      description: 'Make an HTTP request',
      inputs: { 
        url: 'string', 
        method: 'string', 
        headers: 'object?', 
        data: 'any?', 
        timeout: 'number?' 
      },
      outputs: { status: 'number', headers: 'object', data: 'any' },
      handler: this.handleHttpRequest.bind(this)
    });

    // Data Operations
    this.registerTask('data:transform', {
      name: 'Transform Data',
      description: 'Transform data using JavaScript expression',
      inputs: { data: 'any', expression: 'string' },
      outputs: { result: 'any' },
      handler: this.handleDataTransform.bind(this)
    });

    this.registerTask('data:validate', {
      name: 'Validate Data',
      description: 'Validate data against a schema',
      inputs: { data: 'any', schema: 'object' },
      outputs: { valid: 'boolean', errors: 'array?' },
      handler: this.handleDataValidate.bind(this)
    });

    // Control Flow
    this.registerTask('flow:condition', {
      name: 'Conditional Branch',
      description: 'Execute tasks based on condition',
      inputs: { condition: 'string', trueTasks: 'array?', falseTasks: 'array?' },
      outputs: { branch: 'string', executed: 'array' },
      handler: this.handleFlowCondition.bind(this)
    });

    this.registerTask('flow:loop', {
      name: 'Loop Execution',
      description: 'Execute tasks in a loop',
      inputs: { items: 'array', tasks: 'array', parallel: 'boolean?' },
      outputs: { results: 'array', iterations: 'number' },
      handler: this.handleFlowLoop.bind(this)
    });

    // Utility Tasks
    this.registerTask('util:wait', {
      name: 'Wait/Sleep',
      description: 'Wait for specified duration',
      inputs: { duration: 'number', unit: 'string?' },
      outputs: { waited: 'number' },
      handler: this.handleUtilWait.bind(this)
    });

    this.registerTask('util:log', {
      name: 'Log Message',
      description: 'Log a message',
      inputs: { message: 'string', level: 'string?', data: 'any?' },
      outputs: { logged: 'boolean' },
      handler: this.handleUtilLog.bind(this)
    });

    // Git Operations
    this.registerTask('git:clone', {
      name: 'Git Clone',
      description: 'Clone a git repository',
      inputs: { url: 'string', path: 'string', branch: 'string?', depth: 'number?' },
      outputs: { success: 'boolean', path: 'string' },
      handler: this.handleGitClone.bind(this)
    });

    this.registerTask('git:commit', {
      name: 'Git Commit',
      description: 'Create a git commit',
      inputs: { message: 'string', files: 'array?', author: 'string?', cwd: 'string?' },
      outputs: { hash: 'string', success: 'boolean' },
      handler: this.handleGitCommit.bind(this)
    });

    // Package Management
    this.registerTask('npm:install', {
      name: 'NPM Install',
      description: 'Install npm packages',
      inputs: { packages: 'array?', dev: 'boolean?', cwd: 'string?' },
      outputs: { success: 'boolean', installed: 'array' },
      handler: this.handleNpmInstall.bind(this)
    });

    this.registerTask('npm:script', {
      name: 'NPM Script',
      description: 'Run npm script',
      inputs: { script: 'string', args: 'array?', cwd: 'string?' },
      outputs: { success: 'boolean', output: 'string' },
      handler: this.handleNpmScript.bind(this)
    });
  }

  /**
   * Setup resource pools for rate limiting
   */
  private setupResourcePools(): void {
    this.resourcePools.set('http', new ResourcePool(10)); // Max 10 concurrent HTTP requests
    this.resourcePools.set('shell', new ResourcePool(5)); // Max 5 concurrent shell commands
    this.resourcePools.set('file', new ResourcePool(20)); // Max 20 concurrent file operations
  }

  /**
   * Register a custom task
   */
  registerTask(type: string, definition: TaskDefinition): void {
    this.tasks.set(type, definition);
    this.emit('task:registered', { type, definition });
  }

  /**
   * Execute a task with retry logic
   */
  async executeTask(type: string, config: any, context: TaskContext): Promise<TaskResult> {
    const definition = this.tasks.get(type);
    if (!definition) {
      throw new Error(`Unknown task type: ${type}`);
    }

    const startTime = Date.now();
    let retryCount = 0;
    const maxRetries = context.retries || 0;
    const executionKey = `${context.executionId}-${context.taskId}`;

    // Create abort controller for cancellation
    const abortController = new AbortController();
    this.activeExecutions.set(executionKey, abortController);

    try {
      while (retryCount <= maxRetries) {
        try {
          // Get resource pool for task type
          const poolType = this.getResourcePoolType(type);
          const pool = this.resourcePools.get(poolType);

          // Acquire resource if pool exists
          let resource: any;
          if (pool) {
            resource = await pool.acquire();
          }

          try {
            // Execute task with timeout
            const result = await this.executeWithTimeout(
              definition.handler(config, context),
              context.timeout || 30000,
              abortController.signal
            );

            const duration = Date.now() - startTime;
            const taskResult: TaskResult = {
              success: true,
              output: result,
              duration,
              retryCount
            };

            this.emit('task:success', { type, config, context, result: taskResult });
            return taskResult;

          } finally {
            // Release resource
            if (pool && resource) {
              pool.release(resource);
            }
          }

        } catch (error) {
          retryCount++;
          
          if (retryCount > maxRetries) {
            const duration = Date.now() - startTime;
            const taskResult: TaskResult = {
              success: false,
              error: error.message,
              duration,
              retryCount: retryCount - 1
            };

            this.emit('task:failed', { type, config, context, result: taskResult });
            throw error;
          }

          // Wait before retry with exponential backoff
          const delay = Math.min(1000 * Math.pow(2, retryCount - 1), 30000);
          await new Promise(resolve => setTimeout(resolve, delay));

          this.emit('task:retry', { type, config, context, attempt: retryCount, error });
        }
      }
    } finally {
      this.activeExecutions.delete(executionKey);
    }

    throw new Error('Task execution failed after all retries');
  }

  /**
   * Execute with timeout and cancellation support
   */
  private executeWithTimeout<T>(
    promise: Promise<T>, 
    timeout: number, 
    signal: AbortSignal
  ): Promise<T> {
    return new Promise((resolve, reject) => {
      const timeoutId = setTimeout(() => {
        reject(new Error(`Task execution timed out after ${timeout}ms`));
      }, timeout);

      signal.addEventListener('abort', () => {
        clearTimeout(timeoutId);
        reject(new Error('Task execution was cancelled'));
      });

      promise
        .then(result => {
          clearTimeout(timeoutId);
          resolve(result);
        })
        .catch(error => {
          clearTimeout(timeoutId);
          reject(error);
        });
    });
  }

  /**
   * Get appropriate resource pool type for task
   */
  private getResourcePoolType(taskType: string): string {
    if (taskType.startsWith('http:')) return 'http';
    if (taskType.startsWith('shell:') || taskType.startsWith('git:') || taskType.startsWith('npm:')) return 'shell';
    if (taskType.startsWith('file:')) return 'file';
    return 'default';
  }

  /**
   * Cancel task execution
   */
  cancelTask(executionId: string, taskId: string): boolean {
    const executionKey = `${executionId}-${taskId}`;
    const controller = this.activeExecutions.get(executionKey);
    
    if (controller) {
      controller.abort();
      this.activeExecutions.delete(executionKey);
      return true;
    }
    
    return false;
  }

  /**
   * Get task definition
   */
  getTaskDefinition(type: string): TaskDefinition | undefined {
    return this.tasks.get(type);
  }

  /**
   * List all registered tasks
   */
  listTasks(): Map<string, TaskDefinition> {
    return new Map(this.tasks);
  }

  // Built-in task handlers

  private async handleFileRead(config: any, context: TaskContext): Promise<string> {
    const { path: filePath, encoding = 'utf8' } = config;
    return await fs.readFile(filePath, encoding);
  }

  private async handleFileWrite(config: any, context: TaskContext): Promise<number> {
    const { path: filePath, content, encoding = 'utf8' } = config;
    await fs.writeFile(filePath, content, encoding);
    return Buffer.byteLength(content, encoding);
  }

  private async handleFileCopy(config: any, context: TaskContext): Promise<boolean> {
    const { source, destination } = config;
    await fs.copyFile(source, destination);
    return true;
  }

  private async handleFileDelete(config: any, context: TaskContext): Promise<boolean> {
    const { path: filePath, recursive = false } = config;
    await fs.rm(filePath, { recursive, force: true });
    return true;
  }

  private async handleShellExec(config: any, context: TaskContext): Promise<any> {
    const { command, cwd, env, shell } = config;
    const options: any = {};
    
    if (cwd) options.cwd = cwd;
    if (env) options.env = { ...process.env, ...env };
    if (shell) options.shell = shell;

    const result = await execAsync(command, options);
    return {
      stdout: result.stdout,
      stderr: result.stderr,
      exitCode: 0
    };
  }

  private async handleHttpRequest(config: any, context: TaskContext): Promise<any> {
    const { url, method = 'GET', headers, data, timeout = 30000 } = config;
    
    const axiosConfig: AxiosRequestConfig = {
      url,
      method,
      headers,
      data,
      timeout,
      validateStatus: () => true // Don't throw on HTTP error status
    };

    const response = await axios(axiosConfig);
    
    return {
      status: response.status,
      headers: response.headers,
      data: response.data
    };
  }

  private async handleDataTransform(config: any, context: TaskContext): Promise<any> {
    const { data, expression } = config;
    
    // Simple transform using Function constructor
    // In production, use a safer expression evaluator
    const transform = new Function('data', 'context', `return ${expression}`);
    return transform(data, context.variables);
  }

  private async handleDataValidate(config: any, context: TaskContext): Promise<any> {
    const { data, schema } = config;
    
    // Basic validation - in production use a proper schema validator like Ajv
    const errors: string[] = [];
    
    if (schema.required) {
      for (const field of schema.required) {
        if (!(field in data)) {
          errors.push(`Missing required field: ${field}`);
        }
      }
    }
    
    return {
      valid: errors.length === 0,
      errors: errors.length > 0 ? errors : undefined
    };
  }

  private async handleFlowCondition(config: any, context: TaskContext): Promise<any> {
    const { condition, trueTasks = [], falseTasks = [] } = config;
    
    // Evaluate condition
    const result = this.evaluateCondition(condition, context.variables);
    const tasksToExecute = result ? trueTasks : falseTasks;
    const branch = result ? 'true' : 'false';
    
    // Execute selected tasks if workflow engine is available
    const executed: string[] = [];
    if (this.workflowEngine && tasksToExecute.length > 0) {
      // This would require integration with workflow engine
      // For now, just return the tasks that would be executed
      executed.push(...tasksToExecute.map((task: any) => task.id));
    }
    
    return { branch, executed };
  }

  private async handleFlowLoop(config: any, context: TaskContext): Promise<any> {
    const { items, tasks, parallel = false } = config;
    const results: any[] = [];
    
    if (parallel) {
      const promises = items.map(async (item: any, index: number) => {
        const itemContext = {
          ...context,
          variables: { ...context.variables, item, index }
        };
        
        // Execute tasks for this item
        // This would require integration with workflow engine
        return { item, index, completed: tasks.length };
      });
      
      results.push(...await Promise.all(promises));
    } else {
      for (let index = 0; index < items.length; index++) {
        const item = items[index];
        const itemContext = {
          ...context,
          variables: { ...context.variables, item, index }
        };
        
        // Execute tasks for this item
        results.push({ item, index, completed: tasks.length });
      }
    }
    
    return {
      results,
      iterations: items.length
    };
  }

  private async handleUtilWait(config: any, context: TaskContext): Promise<any> {
    const { duration, unit = 'ms' } = config;
    
    let waitTime = duration;
    if (unit === 's' || unit === 'seconds') waitTime *= 1000;
    if (unit === 'm' || unit === 'minutes') waitTime *= 60000;
    if (unit === 'h' || unit === 'hours') waitTime *= 3600000;
    
    await new Promise(resolve => setTimeout(resolve, waitTime));
    return { waited: waitTime };
  }

  private async handleUtilLog(config: any, context: TaskContext): Promise<any> {
    const { message, level = 'info', data } = config;
    
    const logMessage = `[${level.toUpperCase()}] ${message}`;
    if (data) {
      console.log(logMessage, data);
    } else {
      console.log(logMessage);
    }
    
    return { logged: true };
  }

  private async handleGitClone(config: any, context: TaskContext): Promise<any> {
    const { url, path: targetPath, branch, depth } = config;
    
    let command = `git clone ${url} ${targetPath}`;
    if (branch) command += ` --branch ${branch}`;
    if (depth) command += ` --depth ${depth}`;
    
    await execAsync(command);
    return { success: true, path: targetPath };
  }

  private async handleGitCommit(config: any, context: TaskContext): Promise<any> {
    const { message, files, author, cwd } = config;
    
    const options: any = {};
    if (cwd) options.cwd = cwd;
    
    // Add files
    if (files && files.length > 0) {
      for (const file of files) {
        await execAsync(`git add ${file}`, options);
      }
    } else {
      await execAsync('git add .', options);
    }
    
    // Set author if specified
    let commitCommand = `git commit -m "${message}"`;
    if (author) {
      commitCommand = `git -c user.name="${author}" -c user.email="${author}@example.com" commit -m "${message}"`;
    }
    
    const result = await execAsync(commitCommand, options);
    
    // Extract commit hash
    const hashResult = await execAsync('git rev-parse HEAD', options);
    const hash = hashResult.stdout.trim();
    
    return { hash, success: true };
  }

  private async handleNpmInstall(config: any, context: TaskContext): Promise<any> {
    const { packages = [], dev = false, cwd } = config;
    
    const options: any = {};
    if (cwd) options.cwd = cwd;
    
    let command = 'npm install';
    if (packages.length > 0) {
      command += ` ${packages.join(' ')}`;
    }
    if (dev) command += ' --save-dev';
    
    await execAsync(command, options);
    return { success: true, installed: packages };
  }

  private async handleNpmScript(config: any, context: TaskContext): Promise<any> {
    const { script, args = [], cwd } = config;
    
    const options: any = {};
    if (cwd) options.cwd = cwd;
    
    let command = `npm run ${script}`;
    if (args.length > 0) {
      command += ` -- ${args.join(' ')}`;
    }
    
    const result = await execAsync(command, options);
    return { success: true, output: result.stdout };
  }

  /**
   * Evaluate simple condition
   */
  private evaluateCondition(condition: string, variables: Record<string, any>): boolean {
    // Simple condition evaluation - in production use a proper expression evaluator
    try {
      const func = new Function('vars', `with(vars) { return ${condition}; }`);
      return func(variables);
    } catch (error) {
      console.warn(`Condition evaluation failed: ${condition}`, error);
      return false;
    }
  }
}

/**
 * Resource pool for limiting concurrent operations
 */
class ResourcePool {
  private resources: any[] = [];
  private waitingQueue: Array<{ resolve: Function; reject: Function }> = [];
  private activeCount = 0;

  constructor(private maxSize: number) {
    // Initialize pool with simple resources
    for (let i = 0; i < maxSize; i++) {
      this.resources.push({ id: i });
    }
  }

  async acquire(): Promise<any> {
    if (this.resources.length > 0) {
      this.activeCount++;
      return this.resources.pop();
    }

    return new Promise((resolve, reject) => {
      this.waitingQueue.push({ resolve, reject });
    });
  }

  release(resource: any): void {
    this.activeCount--;
    
    if (this.waitingQueue.length > 0) {
      const { resolve } = this.waitingQueue.shift()!;
      this.activeCount++;
      resolve(resource);
    } else {
      this.resources.push(resource);
    }
  }

  getStats() {
    return {
      active: this.activeCount,
      available: this.resources.length,
      waiting: this.waitingQueue.length,
      maxSize: this.maxSize
    };
  }
}