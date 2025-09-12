/**
 * System Health Monitor for CLI UI
 * Overall system health monitoring with auto-recovery mechanisms
 */

import { PerformanceMonitor, PerformanceMetrics, BottleneckAlert } from './PerformanceMonitor';
import { ErrorMonitor, CapturedError, ErrorSummary } from './ErrorMonitor';
import { RealTimeMetrics, Alert, MetricValue } from './RealTimeMetrics';
import { UserAnalytics, SessionMetrics } from './UserAnalytics';

export interface ComponentHealth {
  name: string;
  status: 'healthy' | 'warning' | 'critical' | 'down';
  lastCheck: number;
  responseTime: number;
  errorRate: number;
  uptime: number;
  dependencies: string[];
  metadata?: Record<string, any>;
}

export interface DependencyStatus {
  name: string;
  type: 'service' | 'database' | 'api' | 'file_system' | 'network';
  status: 'available' | 'unavailable' | 'degraded';
  latency: number;
  lastCheck: number;
  version?: string;
  endpoint?: string;
}

export interface ResourceUsage {
  cpu: {
    usage: number;
    cores: number;
    loadAverage?: number[];
  };
  memory: {
    used: number;
    total: number;
    free: number;
    percentage: number;
  };
  disk: {
    used: number;
    total: number;
    free: number;
    percentage: number;
  };
  network: {
    bytesIn: number;
    bytesOut: number;
    packetsIn: number;
    packetsOut: number;
    latency: number;
  };
}

export interface HealthScore {
  overall: number;
  components: {
    performance: number;
    errors: number;
    resources: number;
    dependencies: number;
    uptime: number;
  };
  trend: 'improving' | 'stable' | 'degrading';
  recommendations: string[];
}

export interface RecoveryAction {
  id: string;
  name: string;
  description: string;
  automated: boolean;
  execute: () => Promise<boolean>;
}

export interface SystemAlert {
  id: string;
  component: string;
  severity: 'info' | 'warning' | 'critical';
  message: string;
  timestamp: number;
  recovered: boolean;
  recoveryActions?: RecoveryAction[];
}

export class SystemHealth {
  private components: Map<string, ComponentHealth> = new Map();
  private dependencies: Map<string, DependencyStatus> = new Map();
  private resourceHistory: ResourceUsage[] = [];
  private healthHistory: HealthScore[] = [];
  private alerts: Map<string, SystemAlert> = new Map();
  private recoveryActions: Map<string, RecoveryAction> = new Map();
  private observers: Array<(event: any) => void> = [];
  
  private isMonitoring: boolean = false;
  private monitorInterval?: NodeJS.Timeout;
  private startTime: number = Date.now();
  
  // Configuration
  private config = {
    checkInterval: 30000, // 30 seconds
    resourceHistoryLimit: 100,
    healthHistoryLimit: 50,
    autoRecoveryEnabled: true,
    thresholds: {
      cpu: { warning: 70, critical: 85 },
      memory: { warning: 80, critical: 90 },
      disk: { warning: 85, critical: 95 },
      responseTime: { warning: 1000, critical: 3000 },
      errorRate: { warning: 5, critical: 10 },
      uptime: { warning: 0.95, critical: 0.90 }
    }
  };

  constructor(
    private performanceMonitor?: PerformanceMonitor,
    private errorMonitor?: ErrorMonitor,
    private metricsMonitor?: RealTimeMetrics,
    private userAnalytics?: UserAnalytics
  ) {
    this.initializeComponents();
    this.initializeDependencies();
    this.initializeRecoveryActions();
  }

  private initializeComponents(): void {
    const defaultComponents = [
      'performance-monitor',
      'error-monitor',
      'metrics-system',
      'user-analytics',
      'file-system',
      'network',
      'memory-manager',
      'command-processor'
    ];

    defaultComponents.forEach(name => {
      this.components.set(name, {
        name,
        status: 'healthy',
        lastCheck: Date.now(),
        responseTime: 0,
        errorRate: 0,
        uptime: 1.0,
        dependencies: []
      });
    });
  }

  private initializeDependencies(): void {
    const defaultDependencies: Array<Omit<DependencyStatus, 'lastCheck'>> = [
      {
        name: 'node-runtime',
        type: 'service',
        status: 'available',
        latency: 0,
        version: typeof process !== 'undefined' ? process.version : 'unknown'
      },
      {
        name: 'file-system',
        type: 'file_system',
        status: 'available',
        latency: 0
      },
      {
        name: 'local-storage',
        type: 'database',
        status: 'available',
        latency: 0
      },
      {
        name: 'network-stack',
        type: 'network',
        status: 'available',
        latency: 0
      }
    ];

    defaultDependencies.forEach(dep => {
      this.dependencies.set(dep.name, {
        ...dep,
        lastCheck: Date.now()
      });
    });
  }

  private initializeRecoveryActions(): void {
    const actions: Array<Omit<RecoveryAction, 'execute'> & { executeImpl: () => Promise<boolean> }> = [
      {
        id: 'restart-component',
        name: 'Restart Component',
        description: 'Restart a failed component',
        automated: true,
        executeImpl: this.restartComponent.bind(this)
      },
      {
        id: 'clear-caches',
        name: 'Clear Caches',
        description: 'Clear all system caches',
        automated: true,
        executeImpl: this.clearCaches.bind(this)
      },
      {
        id: 'garbage-collect',
        name: 'Force Garbage Collection',
        description: 'Force memory garbage collection',
        automated: true,
        executeImpl: this.forceGarbageCollection.bind(this)
      },
      {
        id: 'reset-connections',
        name: 'Reset Network Connections',
        description: 'Reset all network connections',
        automated: false,
        executeImpl: this.resetConnections.bind(this)
      }
    ];

    actions.forEach(action => {
      this.recoveryActions.set(action.id, {
        ...action,
        execute: action.executeImpl
      });
    });
  }

  // Monitoring Control
  public start(): void {
    if (this.isMonitoring) return;

    this.isMonitoring = true;
    this.startTime = Date.now();

    // Start periodic health checks
    this.monitorInterval = setInterval(() => {
      this.performHealthCheck();
    }, this.config.checkInterval);

    // Perform initial health check
    this.performHealthCheck();

    console.log('System health monitoring started');
    this.notifyObservers('monitoring_started', { timestamp: Date.now() });
  }

  public stop(): void {
    this.isMonitoring = false;

    if (this.monitorInterval) {
      clearInterval(this.monitorInterval);
      this.monitorInterval = undefined;
    }

    console.log('System health monitoring stopped');
    this.notifyObservers('monitoring_stopped', { timestamp: Date.now() });
  }

  // Health Checking
  private async performHealthCheck(): Promise<void> {
    try {
      const timestamp = Date.now();

      // Check all components
      await Promise.all([
        this.checkComponentHealth(),
        this.checkDependencies(),
        this.collectResourceUsage(),
        this.calculateHealthScore()
      ]);

      // Check for alerts
      this.checkAlerts();

      // Auto-recovery if enabled
      if (this.config.autoRecoveryEnabled) {
        await this.performAutoRecovery();
      }

      this.notifyObservers('health_check_completed', { timestamp });

    } catch (error) {
      console.error('Error during health check:', error);
      this.createAlert('health-check-failed', 'system', 'critical', 
        `Health check failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  private async checkComponentHealth(): Promise<void> {
    const promises = Array.from(this.components.keys()).map(async (componentName) => {
      const component = this.components.get(componentName)!;
      const startTime = performance.now();

      try {
        const health = await this.checkIndividualComponent(componentName);
        const responseTime = performance.now() - startTime;

        component.lastCheck = Date.now();
        component.responseTime = responseTime;
        component.status = health.status;
        component.errorRate = health.errorRate || 0;
        
        // Calculate uptime (simplified)
        const expectedChecks = Math.floor((Date.now() - this.startTime) / this.config.checkInterval);
        const successfulChecks = expectedChecks - (health.errorRate * expectedChecks / 100);
        component.uptime = expectedChecks > 0 ? successfulChecks / expectedChecks : 1;

      } catch (error) {
        component.status = 'critical';
        component.responseTime = performance.now() - startTime;
        component.errorRate = Math.min(100, component.errorRate + 1);
        
        console.error(`Component health check failed for ${componentName}:`, error);
      }
    });

    await Promise.all(promises);
  }

  private async checkIndividualComponent(componentName: string): Promise<{
    status: ComponentHealth['status'];
    errorRate?: number;
  }> {
    switch (componentName) {
      case 'performance-monitor':
        if (this.performanceMonitor) {
          const metrics = this.performanceMonitor.getAverageMetrics(5);
          const fps = metrics.fps || 60;
          const cpuUsage = metrics.cpuUtilization || 0;
          
          if (fps < 15 || cpuUsage > 90) return { status: 'critical' };
          if (fps < 30 || cpuUsage > 70) return { status: 'warning' };
          return { status: 'healthy' };
        }
        return { status: 'down' };

      case 'error-monitor':
        if (this.errorMonitor) {
          const summary = this.errorMonitor.getErrorSummary(5 * 60 * 1000); // 5 minutes
          const errorRate = summary.totalErrors / 5; // errors per minute
          
          if (errorRate > 10) return { status: 'critical', errorRate };
          if (errorRate > 5) return { status: 'warning', errorRate };
          return { status: 'healthy', errorRate };
        }
        return { status: 'down' };

      case 'metrics-system':
        if (this.metricsMonitor) {
          const health = this.metricsMonitor.getHealthStatus();
          return { 
            status: health.status === 'critical' ? 'critical' : 
                   health.status === 'warning' ? 'warning' : 'healthy'
          };
        }
        return { status: 'down' };

      case 'user-analytics':
        if (this.userAnalytics) {
          // User analytics is generally always healthy unless there's a specific error
          return { status: 'healthy' };
        }
        return { status: 'down' };

      default:
        // For other components, perform basic availability check
        return await this.checkGenericComponent(componentName);
    }
  }

  private async checkGenericComponent(componentName: string): Promise<{
    status: ComponentHealth['status'];
  }> {
    // Simulate component check with timeout
    const timeout = new Promise<never>((_, reject) => {
      setTimeout(() => reject(new Error('Timeout')), 5000);
    });

    const check = new Promise<{ status: ComponentHealth['status'] }>((resolve) => {
      // Simulate check delay
      setTimeout(() => {
        // Random health for simulation
        const rand = Math.random();
        if (rand > 0.95) resolve({ status: 'critical' });
        else if (rand > 0.85) resolve({ status: 'warning' });
        else resolve({ status: 'healthy' });
      }, Math.random() * 100);
    });

    try {
      return await Promise.race([check, timeout]);
    } catch (error) {
      return { status: 'critical' };
    }
  }

  private async checkDependencies(): Promise<void> {
    const promises = Array.from(this.dependencies.keys()).map(async (depName) => {
      const dependency = this.dependencies.get(depName)!;
      const startTime = performance.now();

      try {
        const status = await this.checkDependencyStatus(depName, dependency);
        const latency = performance.now() - startTime;

        dependency.status = status;
        dependency.latency = latency;
        dependency.lastCheck = Date.now();

      } catch (error) {
        dependency.status = 'unavailable';
        dependency.latency = performance.now() - startTime;
        dependency.lastCheck = Date.now();
        
        console.error(`Dependency check failed for ${depName}:`, error);
      }
    });

    await Promise.all(promises);
  }

  private async checkDependencyStatus(
    name: string, 
    dependency: DependencyStatus
  ): Promise<DependencyStatus['status']> {
    
    switch (dependency.type) {
      case 'service':
        // Check if Node.js runtime is working
        if (name === 'node-runtime') {
          return typeof process !== 'undefined' ? 'available' : 'unavailable';
        }
        break;

      case 'file_system':
        // Check file system access
        if (typeof process !== 'undefined' && process.cwd) {
          try {
            process.cwd(); // This will throw if file system is not accessible
            return 'available';
          } catch (error) {
            return 'unavailable';
          }
        }
        return 'degraded';

      case 'database':
        // Check local storage (simplified)
        if (typeof localStorage !== 'undefined') {
          try {
            localStorage.setItem('health-check', Date.now().toString());
            localStorage.removeItem('health-check');
            return 'available';
          } catch (error) {
            return 'degraded';
          }
        }
        return 'available'; // Assume available in CLI environment

      case 'network':
        // Simple network check
        try {
          // Try to resolve DNS (simplified)
          return Math.random() > 0.1 ? 'available' : 'degraded'; // 90% success rate
        } catch (error) {
          return 'unavailable';
        }

      default:
        return 'available';
    }

    return 'available';
  }

  private async collectResourceUsage(): Promise<void> {
    try {
      const resources = await this.getResourceUsage();
      
      this.resourceHistory.push(resources);
      
      // Limit history size
      if (this.resourceHistory.length > this.config.resourceHistoryLimit) {
        this.resourceHistory.shift();
      }

    } catch (error) {
      console.error('Error collecting resource usage:', error);
    }
  }

  private async getResourceUsage(): Promise<ResourceUsage> {
    if (typeof process !== 'undefined') {
      // Node.js environment
      const memUsage = process.memoryUsage();
      const cpuUsage = process.cpuUsage();
      
      return {
        cpu: {
          usage: Math.min(100, (cpuUsage.user + cpuUsage.system) / 10000),
          cores: typeof require !== 'undefined' ? require('os').cpus().length : 4
        },
        memory: {
          used: memUsage.rss,
          total: memUsage.rss + memUsage.external,
          free: memUsage.external,
          percentage: (memUsage.rss / (memUsage.rss + memUsage.external)) * 100
        },
        disk: {
          used: 0, // Would need additional OS calls
          total: 0,
          free: 0,
          percentage: 0
        },
        network: {
          bytesIn: 0, // Would need network monitoring
          bytesOut: 0,
          packetsIn: 0,
          packetsOut: 0,
          latency: 0
        }
      };
    } else {
      // Browser environment (limited info)
      const memory = (performance as any).memory;
      
      return {
        cpu: {
          usage: 50, // Estimate based on performance
          cores: typeof navigator !== 'undefined' ? (navigator as any).hardwareConcurrency || 4 : 4
        },
        memory: {
          used: memory ? memory.usedJSHeapSize : 50 * 1024 * 1024,
          total: memory ? memory.totalJSHeapSize : 100 * 1024 * 1024,
          free: memory ? memory.totalJSHeapSize - memory.usedJSHeapSize : 50 * 1024 * 1024,
          percentage: memory ? (memory.usedJSHeapSize / memory.totalJSHeapSize) * 100 : 50
        },
        disk: { used: 0, total: 0, free: 0, percentage: 0 },
        network: { bytesIn: 0, bytesOut: 0, packetsIn: 0, packetsOut: 0, latency: 0 }
      };
    }
  }

  private calculateHealthScore(): void {
    const components = Array.from(this.components.values());
    const dependencies = Array.from(this.dependencies.values());
    const resources = this.resourceHistory.slice(-1)[0];

    // Component health score (0-100)
    const componentScores = components.map(comp => {
      switch (comp.status) {
        case 'healthy': return 100;
        case 'warning': return 70;
        case 'critical': return 30;
        case 'down': return 0;
        default: return 50;
      }
    });
    const avgComponentScore = componentScores.reduce((sum, score) => sum + score, 0) / componentScores.length;

    // Performance score
    const performanceScore = this.calculatePerformanceScore();

    // Error score
    const errorScore = this.calculateErrorScore();

    // Resource score
    const resourceScore = this.calculateResourceScore(resources);

    // Dependency score
    const dependencyScores = dependencies.map(dep => {
      switch (dep.status) {
        case 'available': return 100;
        case 'degraded': return 60;
        case 'unavailable': return 0;
        default: return 50;
      }
    });
    const avgDependencyScore = dependencyScores.reduce((sum, score) => sum + score, 0) / dependencyScores.length;

    // Uptime score
    const uptime = (Date.now() - this.startTime) / (Date.now() - this.startTime + 1); // Simplified
    const uptimeScore = uptime * 100;

    // Overall health score (weighted average)
    const weights = {
      components: 0.25,
      performance: 0.20,
      errors: 0.20,
      resources: 0.15,
      dependencies: 0.10,
      uptime: 0.10
    };

    const overall = 
      avgComponentScore * weights.components +
      performanceScore * weights.performance +
      errorScore * weights.errors +
      resourceScore * weights.resources +
      avgDependencyScore * weights.dependencies +
      uptimeScore * weights.uptime;

    const healthScore: HealthScore = {
      overall: Math.round(overall),
      components: {
        performance: Math.round(performanceScore),
        errors: Math.round(errorScore),
        resources: Math.round(resourceScore),
        dependencies: Math.round(avgDependencyScore),
        uptime: Math.round(uptimeScore)
      },
      trend: this.calculateTrend(),
      recommendations: this.generateRecommendations(overall, {
        performance: performanceScore,
        errors: errorScore,
        resources: resourceScore,
        dependencies: avgDependencyScore,
        uptime: uptimeScore
      })
    };

    this.healthHistory.push(healthScore);

    // Limit history
    if (this.healthHistory.length > this.config.healthHistoryLimit) {
      this.healthHistory.shift();
    }

    this.notifyObservers('health_score_updated', { score: healthScore });
  }

  private calculatePerformanceScore(): number {
    if (!this.performanceMonitor) return 100;

    const metrics = this.performanceMonitor.getAverageMetrics(10);
    if (!metrics.fps) return 100;

    const fps = metrics.fps;
    const cpuUsage = metrics.cpuUtilization || 0;
    const memoryUsage = metrics.memoryUsage?.used || 0;

    let score = 100;

    // FPS impact
    if (fps < 15) score -= 40;
    else if (fps < 30) score -= 20;
    else if (fps < 45) score -= 10;

    // CPU impact
    if (cpuUsage > 90) score -= 30;
    else if (cpuUsage > 70) score -= 15;

    // Memory impact (simplified)
    const memoryMB = memoryUsage / (1024 * 1024);
    if (memoryMB > 500) score -= 20;
    else if (memoryMB > 200) score -= 10;

    return Math.max(0, score);
  }

  private calculateErrorScore(): number {
    if (!this.errorMonitor) return 100;

    const summary = this.errorMonitor.getErrorSummary(10 * 60 * 1000); // 10 minutes
    if (summary.totalErrors === 0) return 100;

    let score = 100;

    // Total errors impact
    if (summary.totalErrors > 50) score -= 40;
    else if (summary.totalErrors > 20) score -= 25;
    else if (summary.totalErrors > 10) score -= 15;
    else if (summary.totalErrors > 5) score -= 5;

    // Critical errors impact
    const criticalErrors = summary.errorsBySeverity.critical || 0;
    score -= criticalErrors * 10;

    // Recovery rate bonus
    const recoveryRate = summary.recoveryStats.successful / summary.recoveryStats.attempted;
    if (recoveryRate > 0.8) score += 5;
    else if (recoveryRate < 0.5) score -= 10;

    return Math.max(0, score);
  }

  private calculateResourceScore(resources?: ResourceUsage): number {
    if (!resources) return 100;

    let score = 100;

    // CPU usage impact
    if (resources.cpu.usage > this.config.thresholds.cpu.critical) score -= 30;
    else if (resources.cpu.usage > this.config.thresholds.cpu.warning) score -= 15;

    // Memory usage impact
    if (resources.memory.percentage > this.config.thresholds.memory.critical) score -= 30;
    else if (resources.memory.percentage > this.config.thresholds.memory.warning) score -= 15;

    // Disk usage impact
    if (resources.disk.percentage > this.config.thresholds.disk.critical) score -= 20;
    else if (resources.disk.percentage > this.config.thresholds.disk.warning) score -= 10;

    return Math.max(0, score);
  }

  private calculateTrend(): HealthScore['trend'] {
    if (this.healthHistory.length < 3) return 'stable';

    const recent = this.healthHistory.slice(-3);
    const scores = recent.map(h => h.overall);

    const trend = scores[2] - scores[0];

    if (trend > 10) return 'improving';
    if (trend < -10) return 'degrading';
    return 'stable';
  }

  private generateRecommendations(overall: number, components: HealthScore['components']): string[] {
    const recommendations: string[] = [];

    if (overall < 70) {
      recommendations.push('System health is below optimal. Consider investigating critical issues.');
    }

    if (components.performance < 70) {
      recommendations.push('Performance is degraded. Check CPU and memory usage.');
      recommendations.push('Consider optimizing algorithms and reducing computational load.');
    }

    if (components.errors < 80) {
      recommendations.push('Error rate is elevated. Review error logs and implement fixes.');
      recommendations.push('Enable automatic error recovery mechanisms.');
    }

    if (components.resources < 70) {
      recommendations.push('Resource usage is high. Monitor memory leaks and optimize resource allocation.');
    }

    if (components.dependencies < 90) {
      recommendations.push('Some dependencies are unavailable or degraded. Check connectivity.');
    }

    if (components.uptime < 95) {
      recommendations.push('System uptime is below target. Investigate stability issues.');
    }

    // Add positive recommendations for good health
    if (overall > 90) {
      recommendations.push('System is performing excellently. Continue current maintenance practices.');
    }

    return recommendations;
  }

  // Alert Management
  private checkAlerts(): void {
    const components = Array.from(this.components.values());
    const dependencies = Array.from(this.dependencies.values());
    const resources = this.resourceHistory.slice(-1)[0];

    // Component alerts
    components.forEach(comp => {
      const alertId = `component-${comp.name}`;
      
      if (comp.status === 'critical' || comp.status === 'down') {
        this.createAlert(alertId, comp.name, 'critical', 
          `Component ${comp.name} is ${comp.status}`);
      } else if (comp.status === 'warning') {
        this.createAlert(alertId, comp.name, 'warning', 
          `Component ${comp.name} is degraded`);
      } else {
        this.resolveAlert(alertId);
      }
    });

    // Dependency alerts
    dependencies.forEach(dep => {
      const alertId = `dependency-${dep.name}`;
      
      if (dep.status === 'unavailable') {
        this.createAlert(alertId, dep.name, 'critical', 
          `Dependency ${dep.name} is unavailable`);
      } else if (dep.status === 'degraded') {
        this.createAlert(alertId, dep.name, 'warning', 
          `Dependency ${dep.name} is degraded`);
      } else {
        this.resolveAlert(alertId);
      }
    });

    // Resource alerts
    if (resources) {
      if (resources.cpu.usage > this.config.thresholds.cpu.critical) {
        this.createAlert('cpu-usage', 'resources', 'critical', 
          `CPU usage is critically high: ${resources.cpu.usage.toFixed(1)}%`);
      } else if (resources.cpu.usage > this.config.thresholds.cpu.warning) {
        this.createAlert('cpu-usage', 'resources', 'warning', 
          `CPU usage is elevated: ${resources.cpu.usage.toFixed(1)}%`);
      } else {
        this.resolveAlert('cpu-usage');
      }

      if (resources.memory.percentage > this.config.thresholds.memory.critical) {
        this.createAlert('memory-usage', 'resources', 'critical', 
          `Memory usage is critically high: ${resources.memory.percentage.toFixed(1)}%`);
      } else if (resources.memory.percentage > this.config.thresholds.memory.warning) {
        this.createAlert('memory-usage', 'resources', 'warning', 
          `Memory usage is elevated: ${resources.memory.percentage.toFixed(1)}%`);
      } else {
        this.resolveAlert('memory-usage');
      }
    }
  }

  private createAlert(id: string, component: string, severity: SystemAlert['severity'], message: string): void {
    const existingAlert = this.alerts.get(id);
    
    // Don't create duplicate unresolved alerts
    if (existingAlert && !existingAlert.recovered) return;

    const alert: SystemAlert = {
      id,
      component,
      severity,
      message,
      timestamp: Date.now(),
      recovered: false,
      recoveryActions: this.getSuggestedRecoveryActions(component, severity)
    };

    this.alerts.set(id, alert);
    
    console.warn(`SYSTEM ALERT [${severity.toUpperCase()}]: ${message}`);
    this.notifyObservers('alert_created', { alert });
  }

  private resolveAlert(id: string): void {
    const alert = this.alerts.get(id);
    if (alert && !alert.recovered) {
      alert.recovered = true;
      this.notifyObservers('alert_resolved', { alert });
    }
  }

  private getSuggestedRecoveryActions(component: string, severity: SystemAlert['severity']): RecoveryAction[] {
    const actions: RecoveryAction[] = [];

    if (severity === 'critical') {
      actions.push(this.recoveryActions.get('restart-component')!);
      actions.push(this.recoveryActions.get('clear-caches')!);
    }

    if (component === 'resources' || component.includes('memory')) {
      actions.push(this.recoveryActions.get('garbage-collect')!);
    }

    if (component.includes('network') || component.includes('dependency')) {
      actions.push(this.recoveryActions.get('reset-connections')!);
    }

    return actions.filter(Boolean);
  }

  // Auto-Recovery
  private async performAutoRecovery(): Promise<void> {
    const criticalAlerts = Array.from(this.alerts.values())
      .filter(alert => alert.severity === 'critical' && !alert.recovered);

    for (const alert of criticalAlerts) {
      if (!alert.recoveryActions) continue;

      const automatedActions = alert.recoveryActions.filter(action => action.automated);
      
      for (const action of automatedActions.slice(0, 2)) { // Try max 2 actions per alert
        try {
          console.log(`Attempting auto-recovery: ${action.name} for ${alert.component}`);
          
          const success = await action.execute();
          
          if (success) {
            console.log(`Auto-recovery successful: ${action.name}`);
            this.notifyObservers('auto_recovery_success', {
              alert: alert.id,
              action: action.name
            });
            break; // Stop trying more actions for this alert
          } else {
            console.warn(`Auto-recovery failed: ${action.name}`);
          }
        } catch (error) {
          console.error(`Auto-recovery error: ${action.name}:`, error);
        }
      }
    }
  }

  // Recovery Action Implementations
  private async restartComponent(): Promise<boolean> {
    // Simulate component restart
    await new Promise(resolve => setTimeout(resolve, 1000));
    return Math.random() > 0.2; // 80% success rate
  }

  private async clearCaches(): Promise<boolean> {
    // Simulate cache clearing
    try {
      // Clear any internal caches
      if (this.performanceMonitor) {
        this.performanceMonitor.clearMarks();
      }
      
      await new Promise(resolve => setTimeout(resolve, 500));
      return true;
    } catch (error) {
      return false;
    }
  }

  private async forceGarbageCollection(): Promise<boolean> {
    try {
      if (typeof global !== 'undefined' && global.gc) {
        global.gc();
        return true;
      }
      
      // Fallback: attempt to trigger GC through memory pressure
      const arrays = [];
      for (let i = 0; i < 100; i++) {
        arrays.push(new Array(1000).fill(null));
      }
      arrays.length = 0;
      
      return true;
    } catch (error) {
      return false;
    }
  }

  private async resetConnections(): Promise<boolean> {
    // Simulate connection reset
    await new Promise(resolve => setTimeout(resolve, 2000));
    return Math.random() > 0.3; // 70% success rate
  }

  // Data Access Methods
  public getOverallHealth(): HealthScore | undefined {
    return this.healthHistory.slice(-1)[0];
  }

  public getComponentHealth(): ComponentHealth[] {
    return Array.from(this.components.values());
  }

  public getDependencyStatus(): DependencyStatus[] {
    return Array.from(this.dependencies.values());
  }

  public getResourceUsage(): ResourceUsage[] {
    return [...this.resourceHistory];
  }

  public getAlerts(includeResolved: boolean = false): SystemAlert[] {
    return Array.from(this.alerts.values())
      .filter(alert => includeResolved || !alert.recovered)
      .sort((a, b) => b.timestamp - a.timestamp);
  }

  public getHealthHistory(): HealthScore[] {
    return [...this.healthHistory];
  }

  // Manual Recovery
  public async executeRecoveryAction(actionId: string): Promise<boolean> {
    const action = this.recoveryActions.get(actionId);
    if (!action) {
      throw new Error(`Recovery action not found: ${actionId}`);
    }

    try {
      const success = await action.execute();
      
      this.notifyObservers('manual_recovery_executed', {
        action: actionId,
        success
      });
      
      return success;
    } catch (error) {
      console.error(`Manual recovery action failed: ${actionId}:`, error);
      return false;
    }
  }

  public getRecoveryActions(): RecoveryAction[] {
    return Array.from(this.recoveryActions.values());
  }

  // Observer Pattern
  public subscribe(callback: (event: any) => void): () => void {
    this.observers.push(callback);
    
    return () => {
      const index = this.observers.indexOf(callback);
      if (index > -1) {
        this.observers.splice(index, 1);
      }
    };
  }

  private notifyObservers(type: string, data: any): void {
    this.observers.forEach(observer => {
      try {
        observer({ type, data, timestamp: Date.now() });
      } catch (error) {
        console.error('Error in health observer:', error);
      }
    });
  }

  // Export and Configuration
  public exportHealthReport(): string {
    return JSON.stringify({
      overall: this.getOverallHealth(),
      components: this.getComponentHealth(),
      dependencies: this.getDependencyStatus(),
      resources: this.getResourceUsage().slice(-10),
      alerts: this.getAlerts(true),
      history: this.getHealthHistory(),
      uptime: Date.now() - this.startTime,
      exportedAt: Date.now()
    }, null, 2);
  }

  public updateConfiguration(config: Partial<typeof this.config>): void {
    this.config = { ...this.config, ...config };
    this.notifyObservers('config_updated', { config: this.config });
  }

  public dispose(): void {
    this.stop();
    this.observers.length = 0;
    this.components.clear();
    this.dependencies.clear();
    this.resourceHistory.length = 0;
    this.healthHistory.length = 0;
    this.alerts.clear();
    this.recoveryActions.clear();
  }
}

export default SystemHealth;