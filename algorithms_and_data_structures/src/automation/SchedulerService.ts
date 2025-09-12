import { EventEmitter } from 'events';
import * as cron from 'node-cron';
import { promises as fs } from 'fs';
import * as path from 'path';
import { v4 as uuidv4 } from 'uuid';
import { WorkflowTrigger, WorkflowEngine } from './WorkflowEngine';

export interface ScheduledJob {
  id: string;
  workflowId: string;
  trigger: WorkflowTrigger;
  schedule?: string; // cron expression
  nextRun?: Date;
  lastRun?: Date;
  enabled: boolean;
  runCount: number;
  failureCount: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface EventTrigger {
  id: string;
  workflowId: string;
  eventType: string;
  conditions?: Record<string, any>;
  handler: Function;
  enabled: boolean;
}

export interface DelayedExecution {
  id: string;
  workflowId: string;
  executionTime: Date;
  variables?: Record<string, any>;
  priority: number;
  recurring?: {
    interval: number;
    unit: 'ms' | 's' | 'm' | 'h' | 'd';
    endDate?: Date;
    maxRuns?: number;
  };
}

export interface QueueStats {
  pending: number;
  running: number;
  completed: number;
  failed: number;
  totalExecutions: number;
}

export class SchedulerService extends EventEmitter {
  private jobs = new Map<string, ScheduledJob>();
  private cronTasks = new Map<string, cron.ScheduledTask>();
  private eventTriggers = new Map<string, EventTrigger>();
  private delayedExecutions = new Map<string, DelayedExecution>();
  private priorityQueue: DelayedExecution[] = [];
  private queueProcessor: NodeJS.Timeout | null = null;
  private isProcessing = false;
  private stats: QueueStats = {
    pending: 0,
    running: 0,
    completed: 0,
    failed: 0,
    totalExecutions: 0
  };

  constructor(private workflowEngine: WorkflowEngine) {
    super();
    this.startQueueProcessor();
    this.setupEventListeners();
  }

  /**
   * Register a workflow trigger
   */
  registerTrigger(workflowId: string, trigger: WorkflowTrigger): string {
    const jobId = uuidv4();
    
    const job: ScheduledJob = {
      id: jobId,
      workflowId,
      trigger,
      enabled: true,
      runCount: 0,
      failureCount: 0,
      createdAt: new Date(),
      updatedAt: new Date()
    };

    this.jobs.set(jobId, job);

    switch (trigger.type) {
      case 'cron':
        this.registerCronTrigger(job);
        break;
      case 'event':
        this.registerEventTrigger(job);
        break;
      case 'webhook':
        this.registerWebhookTrigger(job);
        break;
      case 'file':
        this.registerFileTrigger(job);
        break;
      case 'api':
        this.registerApiTrigger(job);
        break;
      default:
        console.warn(`Unknown trigger type: ${trigger.type}`);
    }

    this.emit('trigger:registered', job);
    return jobId;
  }

  /**
   * Register cron-based trigger
   */
  private registerCronTrigger(job: ScheduledJob): void {
    const { schedule } = job.trigger.config;
    
    if (!schedule || !cron.validate(schedule)) {
      throw new Error(`Invalid cron schedule: ${schedule}`);
    }

    job.schedule = schedule;
    job.nextRun = this.calculateNextRun(schedule);

    const task = cron.schedule(schedule, async () => {
      await this.executeTrigger(job);
    }, {
      scheduled: false,
      timezone: job.trigger.config.timezone || 'UTC'
    });

    this.cronTasks.set(job.id, task);
    
    if (job.enabled) {
      task.start();
    }
  }

  /**
   * Register event-based trigger
   */
  private registerEventTrigger(job: ScheduledJob): void {
    const { eventType, conditions } = job.trigger.config;
    
    const eventTrigger: EventTrigger = {
      id: job.id,
      workflowId: job.workflowId,
      eventType,
      conditions,
      enabled: job.enabled,
      handler: async (eventData: any) => {
        if (this.matchesConditions(eventData, conditions)) {
          await this.executeTrigger(job, { eventData });
        }
      }
    };

    this.eventTriggers.set(job.id, eventTrigger);
    this.workflowEngine.on(eventType, eventTrigger.handler);
  }

  /**
   * Register webhook trigger
   */
  private registerWebhookTrigger(job: ScheduledJob): void {
    const { path, method = 'POST', auth } = job.trigger.config;
    
    // This would integrate with a web server (Express, Fastify, etc.)
    // For now, we'll emit an event that can be handled by the application
    this.emit('webhook:register', {
      jobId: job.id,
      path,
      method,
      auth,
      handler: async (req: any, res: any) => {
        const variables = {
          headers: req.headers,
          body: req.body,
          query: req.query,
          params: req.params
        };
        
        await this.executeTrigger(job, variables);
        res.status(200).json({ success: true, jobId: job.id });
      }
    });
  }

  /**
   * Register file system trigger
   */
  private registerFileTrigger(job: ScheduledJob): void {
    const { path: watchPath, events = ['change'] } = job.trigger.config;
    
    // This would use fs.watch or chokidar for file watching
    // For now, we'll emit an event that can be handled by the application
    this.emit('file:watch', {
      jobId: job.id,
      path: watchPath,
      events,
      handler: async (event: string, filename: string) => {
        if (events.includes(event)) {
          const variables = { event, filename, path: watchPath };
          await this.executeTrigger(job, variables);
        }
      }
    });
  }

  /**
   * Register API trigger
   */
  private registerApiTrigger(job: ScheduledJob): void {
    const { endpoint, method = 'GET', headers, auth } = job.trigger.config;
    
    // This would set up API monitoring/polling
    // For now, we'll create a simple HTTP endpoint check
    this.emit('api:monitor', {
      jobId: job.id,
      endpoint,
      method,
      headers,
      auth,
      handler: async (responseData: any) => {
        const variables = { response: responseData };
        await this.executeTrigger(job, variables);
      }
    });
  }

  /**
   * Execute trigger
   */
  private async executeTrigger(job: ScheduledJob, variables: Record<string, any> = {}): Promise<void> {
    if (!job.enabled) {
      return;
    }

    try {
      job.runCount++;
      job.lastRun = new Date();
      job.updatedAt = new Date();

      // Update next run time for cron jobs
      if (job.schedule) {
        job.nextRun = this.calculateNextRun(job.schedule);
      }

      this.emit('trigger:executing', job);

      // Check trigger conditions
      if (job.trigger.conditions && !this.evaluateConditions(job.trigger.conditions, variables)) {
        this.emit('trigger:skipped', job);
        return;
      }

      // Execute workflow
      const executionId = await this.workflowEngine.executeWorkflow(
        job.workflowId,
        { ...job.trigger.config.variables, ...variables },
        `trigger:${job.id}`
      );

      this.stats.totalExecutions++;
      this.emit('trigger:completed', { job, executionId });

    } catch (error) {
      job.failureCount++;
      job.updatedAt = new Date();
      this.stats.failed++;
      this.emit('trigger:failed', { job, error });
    }
  }

  /**
   * Schedule delayed execution
   */
  scheduleDelayed(
    workflowId: string,
    delay: number,
    variables?: Record<string, any>,
    priority: number = 0,
    recurring?: DelayedExecution['recurring']
  ): string {
    const id = uuidv4();
    const executionTime = new Date(Date.now() + delay);

    const delayedExecution: DelayedExecution = {
      id,
      workflowId,
      executionTime,
      variables,
      priority,
      recurring
    };

    this.delayedExecutions.set(id, delayedExecution);
    this.addToPriorityQueue(delayedExecution);
    this.stats.pending++;

    this.emit('delayed:scheduled', delayedExecution);
    return id;
  }

  /**
   * Schedule recurring execution
   */
  scheduleRecurring(
    workflowId: string,
    interval: number,
    unit: 'ms' | 's' | 'm' | 'h' | 'd',
    variables?: Record<string, any>,
    endDate?: Date,
    maxRuns?: number
  ): string {
    let intervalMs = interval;
    
    switch (unit) {
      case 's': intervalMs *= 1000; break;
      case 'm': intervalMs *= 60 * 1000; break;
      case 'h': intervalMs *= 60 * 60 * 1000; break;
      case 'd': intervalMs *= 24 * 60 * 60 * 1000; break;
    }

    return this.scheduleDelayed(workflowId, intervalMs, variables, 0, {
      interval: intervalMs,
      unit: 'ms',
      endDate,
      maxRuns
    });
  }

  /**
   * Add to priority queue maintaining order
   */
  private addToPriorityQueue(execution: DelayedExecution): void {
    const index = this.priorityQueue.findIndex(item => 
      item.executionTime > execution.executionTime || 
      (item.executionTime.getTime() === execution.executionTime.getTime() && item.priority < execution.priority)
    );

    if (index === -1) {
      this.priorityQueue.push(execution);
    } else {
      this.priorityQueue.splice(index, 0, execution);
    }
  }

  /**
   * Start queue processor
   */
  private startQueueProcessor(): void {
    this.queueProcessor = setInterval(async () => {
      if (this.isProcessing || this.priorityQueue.length === 0) {
        return;
      }

      this.isProcessing = true;

      try {
        const now = new Date();
        const readyExecutions: DelayedExecution[] = [];

        // Find all executions that are ready
        while (this.priorityQueue.length > 0 && this.priorityQueue[0].executionTime <= now) {
          readyExecutions.push(this.priorityQueue.shift()!);
        }

        // Execute ready workflows
        for (const execution of readyExecutions) {
          try {
            this.stats.pending--;
            this.stats.running++;

            const executionId = await this.workflowEngine.executeWorkflow(
              execution.workflowId,
              execution.variables,
              `delayed:${execution.id}`
            );

            this.stats.running--;
            this.stats.completed++;
            this.stats.totalExecutions++;

            this.emit('delayed:executed', { execution, executionId });

            // Schedule next run if recurring
            if (execution.recurring) {
              await this.handleRecurringExecution(execution);
            }

          } catch (error) {
            this.stats.running--;
            this.stats.failed++;
            this.emit('delayed:failed', { execution, error });
          }

          this.delayedExecutions.delete(execution.id);
        }

      } finally {
        this.isProcessing = false;
      }
    }, 1000); // Check every second
  }

  /**
   * Handle recurring execution scheduling
   */
  private async handleRecurringExecution(execution: DelayedExecution): Promise<void> {
    const { recurring } = execution;
    if (!recurring) return;

    const now = new Date();
    
    // Check end conditions
    if (recurring.endDate && now > recurring.endDate) {
      this.emit('recurring:ended', execution);
      return;
    }

    if (recurring.maxRuns && execution.workflowId.split(':').length >= recurring.maxRuns) {
      this.emit('recurring:maxruns', execution);
      return;
    }

    // Schedule next execution
    const nextExecution: DelayedExecution = {
      ...execution,
      id: uuidv4(),
      executionTime: new Date(now.getTime() + recurring.interval)
    };

    this.delayedExecutions.set(nextExecution.id, nextExecution);
    this.addToPriorityQueue(nextExecution);
    this.stats.pending++;

    this.emit('recurring:scheduled', nextExecution);
  }

  /**
   * Setup event listeners
   */
  private setupEventListeners(): void {
    this.workflowEngine.on('workflow:completed', (execution: any) => {
      this.emit('workflow:completed', execution);
    });

    this.workflowEngine.on('workflow:failed', (execution: any) => {
      this.emit('workflow:failed', execution);
    });
  }

  /**
   * Calculate next run time for cron expression
   */
  private calculateNextRun(schedule: string): Date {
    // This is a simplified implementation
    // In production, use a proper cron parser library
    const task = cron.schedule(schedule, () => {}, { scheduled: false });
    return task.getStatus() === 'scheduled' ? new Date(Date.now() + 60000) : new Date();
  }

  /**
   * Check if event data matches conditions
   */
  private matchesConditions(eventData: any, conditions?: Record<string, any>): boolean {
    if (!conditions) return true;

    for (const [key, expectedValue] of Object.entries(conditions)) {
      const actualValue = this.getNestedValue(eventData, key);
      
      if (this.isConditionObject(expectedValue)) {
        if (!this.evaluateConditionObject(actualValue, expectedValue)) {
          return false;
        }
      } else if (actualValue !== expectedValue) {
        return false;
      }
    }

    return true;
  }

  /**
   * Evaluate trigger conditions
   */
  private evaluateConditions(conditions: any[], variables: Record<string, any>): boolean {
    return conditions.every(condition => {
      try {
        const func = new Function('vars', `with(vars) { return ${condition.expression}; }`);
        return func({ ...variables, ...condition.variables });
      } catch (error) {
        console.warn('Condition evaluation failed:', condition, error);
        return false;
      }
    });
  }

  /**
   * Get nested value from object using dot notation
   */
  private getNestedValue(obj: any, path: string): any {
    return path.split('.').reduce((current, key) => current?.[key], obj);
  }

  /**
   * Check if value is a condition object
   */
  private isConditionObject(value: any): boolean {
    return value && typeof value === 'object' && (
      value.hasOwnProperty('$eq') ||
      value.hasOwnProperty('$ne') ||
      value.hasOwnProperty('$gt') ||
      value.hasOwnProperty('$gte') ||
      value.hasOwnProperty('$lt') ||
      value.hasOwnProperty('$lte') ||
      value.hasOwnProperty('$in') ||
      value.hasOwnProperty('$nin') ||
      value.hasOwnProperty('$regex')
    );
  }

  /**
   * Evaluate condition object
   */
  private evaluateConditionObject(actualValue: any, condition: any): boolean {
    if (condition.$eq !== undefined) return actualValue === condition.$eq;
    if (condition.$ne !== undefined) return actualValue !== condition.$ne;
    if (condition.$gt !== undefined) return actualValue > condition.$gt;
    if (condition.$gte !== undefined) return actualValue >= condition.$gte;
    if (condition.$lt !== undefined) return actualValue < condition.$lt;
    if (condition.$lte !== undefined) return actualValue <= condition.$lte;
    if (condition.$in !== undefined) return condition.$in.includes(actualValue);
    if (condition.$nin !== undefined) return !condition.$nin.includes(actualValue);
    if (condition.$regex !== undefined) {
      const regex = new RegExp(condition.$regex, condition.$options || '');
      return regex.test(String(actualValue));
    }
    
    return false;
  }

  // Public API methods

  /**
   * Enable/disable job
   */
  setJobEnabled(jobId: string, enabled: boolean): boolean {
    const job = this.jobs.get(jobId);
    if (!job) return false;

    job.enabled = enabled;
    job.updatedAt = new Date();

    // Update cron task
    const cronTask = this.cronTasks.get(jobId);
    if (cronTask) {
      if (enabled) {
        cronTask.start();
      } else {
        cronTask.stop();
      }
    }

    // Update event trigger
    const eventTrigger = this.eventTriggers.get(jobId);
    if (eventTrigger) {
      eventTrigger.enabled = enabled;
    }

    this.emit('job:updated', job);
    return true;
  }

  /**
   * Remove job
   */
  removeJob(jobId: string): boolean {
    const job = this.jobs.get(jobId);
    if (!job) return false;

    // Remove cron task
    const cronTask = this.cronTasks.get(jobId);
    if (cronTask) {
      cronTask.destroy();
      this.cronTasks.delete(jobId);
    }

    // Remove event trigger
    const eventTrigger = this.eventTriggers.get(jobId);
    if (eventTrigger) {
      this.workflowEngine.removeListener(eventTrigger.eventType, eventTrigger.handler);
      this.eventTriggers.delete(jobId);
    }

    this.jobs.delete(jobId);
    this.emit('job:removed', job);
    return true;
  }

  /**
   * Cancel delayed execution
   */
  cancelDelayed(executionId: string): boolean {
    const execution = this.delayedExecutions.get(executionId);
    if (!execution) return false;

    // Remove from priority queue
    const index = this.priorityQueue.findIndex(item => item.id === executionId);
    if (index !== -1) {
      this.priorityQueue.splice(index, 1);
      this.stats.pending--;
    }

    this.delayedExecutions.delete(executionId);
    this.emit('delayed:cancelled', execution);
    return true;
  }

  /**
   * Get job by ID
   */
  getJob(jobId: string): ScheduledJob | undefined {
    return this.jobs.get(jobId);
  }

  /**
   * List all jobs
   */
  listJobs(): ScheduledJob[] {
    return Array.from(this.jobs.values());
  }

  /**
   * Get delayed execution
   */
  getDelayedExecution(executionId: string): DelayedExecution | undefined {
    return this.delayedExecutions.get(executionId);
  }

  /**
   * List all delayed executions
   */
  listDelayedExecutions(): DelayedExecution[] {
    return Array.from(this.delayedExecutions.values());
  }

  /**
   * Get scheduler statistics
   */
  getStats(): QueueStats {
    return { ...this.stats };
  }

  /**
   * Get next scheduled executions
   */
  getUpcoming(limit: number = 10): Array<{ jobId: string; nextRun: Date; workflowId: string }> {
    const upcoming: Array<{ jobId: string; nextRun: Date; workflowId: string }> = [];
    
    // Add cron jobs
    for (const [jobId, job] of this.jobs.entries()) {
      if (job.enabled && job.nextRun) {
        upcoming.push({
          jobId,
          nextRun: job.nextRun,
          workflowId: job.workflowId
        });
      }
    }

    // Add delayed executions
    for (const execution of this.priorityQueue.slice(0, limit)) {
      upcoming.push({
        jobId: execution.id,
        nextRun: execution.executionTime,
        workflowId: execution.workflowId
      });
    }

    // Sort by execution time and return top results
    return upcoming
      .sort((a, b) => a.nextRun.getTime() - b.nextRun.getTime())
      .slice(0, limit);
  }

  /**
   * Trigger manual execution
   */
  async triggerManual(jobId: string, variables?: Record<string, any>): Promise<string | null> {
    const job = this.jobs.get(jobId);
    if (!job) return null;

    return await this.workflowEngine.executeWorkflow(
      job.workflowId,
      { ...job.trigger.config.variables, ...variables },
      `manual:${jobId}`
    );
  }

  /**
   * Shutdown scheduler
   */
  async shutdown(): Promise<void> {
    // Stop queue processor
    if (this.queueProcessor) {
      clearInterval(this.queueProcessor);
      this.queueProcessor = null;
    }

    // Stop all cron tasks
    for (const task of this.cronTasks.values()) {
      task.destroy();
    }
    this.cronTasks.clear();

    // Remove event listeners
    for (const trigger of this.eventTriggers.values()) {
      this.workflowEngine.removeListener(trigger.eventType, trigger.handler);
    }
    this.eventTriggers.clear();

    // Clear all data
    this.jobs.clear();
    this.delayedExecutions.clear();
    this.priorityQueue = [];

    this.removeAllListeners();
    this.emit('scheduler:shutdown');
  }
}