/**
 * PerformanceMonitor - Comprehensive performance tracking system
 * Features: FPS monitoring, memory tracking, CPU utilization, bottleneck detection
 */

export interface PerformanceMetrics {
  fps: number;
  frameTime: number;
  memoryUsage: {
    used: number;
    total: number;
    heapUsed: number;
    heapTotal: number;
    external: number;
  };
  cpuUsage: {
    user: number;
    system: number;
    idle: number;
  };
  renderMetrics: {
    drawCalls: number;
    triangles: number;
    geometries: number;
    textures: number;
  };
  networkLatency: number;
  customMarks: Map<string, number>;
}

export interface BottleneckAlert {
  type: 'memory' | 'cpu' | 'fps' | 'network' | 'render';
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  timestamp: number;
  metrics: Partial<PerformanceMetrics>;
  suggestions: string[];
}

export class PerformanceMonitor {
  private metrics: PerformanceMetrics;
  private observers: Array<(metrics: PerformanceMetrics) => void> = [];
  private alertCallbacks: Array<(alert: BottleneckAlert) => void> = [];
  private isRunning = false;
  private updateInterval = 100; // 10 FPS for monitoring
  private intervalId?: NodeJS.Timeout;
  private frameCount = 0;
  private lastFrameTime = performance.now();
  private fpsBuffer: number[] = [];
  private memoryHistory: number[] = [];
  private customMarks = new Map<string, number>();
  
  // Performance thresholds
  private thresholds = {
    fps: { warning: 30, critical: 15 },
    memory: { warning: 0.8, critical: 0.95 }, // Percentage of total
    cpu: { warning: 80, critical: 95 },
    networkLatency: { warning: 200, critical: 1000 }, // ms
    frameTime: { warning: 33, critical: 66 } // ms (30fps, 15fps)
  };

  constructor() {
    this.metrics = this.initializeMetrics();
    this.setupPerformanceObserver();
  }

  private initializeMetrics(): PerformanceMetrics {
    return {
      fps: 0,
      frameTime: 0,
      memoryUsage: {
        used: 0,
        total: 0,
        heapUsed: 0,
        heapTotal: 0,
        external: 0
      },
      cpuUsage: {
        user: 0,
        system: 0,
        idle: 0
      },
      renderMetrics: {
        drawCalls: 0,
        triangles: 0,
        geometries: 0,
        textures: 0
      },
      networkLatency: 0,
      customMarks: new Map()
    };
  }

  private setupPerformanceObserver(): void {
    // Setup Performance Observer for custom marks and measures
    if (typeof PerformanceObserver !== 'undefined') {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.entryType === 'mark') {
            this.customMarks.set(entry.name, entry.startTime);
          } else if (entry.entryType === 'measure') {
            this.customMarks.set(entry.name, entry.duration);
          }
        }
        this.metrics.customMarks = new Map(this.customMarks);
      });
      
      observer.observe({ entryTypes: ['mark', 'measure'] });
    }
  }

  public start(): void {
    if (this.isRunning) return;
    
    this.isRunning = true;
    this.lastFrameTime = performance.now();
    
    this.intervalId = setInterval(() => {
      this.updateMetrics();
      this.checkForBottlenecks();
      this.notifyObservers();
    }, this.updateInterval);
    
    // Setup RAF for FPS calculation
    this.requestFrame();
  }

  public stop(): void {
    this.isRunning = false;
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = undefined;
    }
  }

  private requestFrame(): void {
    if (!this.isRunning) return;
    
    requestAnimationFrame((timestamp) => {
      this.frameCount++;
      const deltaTime = timestamp - this.lastFrameTime;
      
      // Calculate FPS using a sliding window
      this.fpsBuffer.push(1000 / deltaTime);
      if (this.fpsBuffer.length > 60) { // Keep 1 second of data at 60fps
        this.fpsBuffer.shift();
      }
      
      this.metrics.fps = this.fpsBuffer.reduce((a, b) => a + b, 0) / this.fpsBuffer.length;
      this.metrics.frameTime = deltaTime;
      this.lastFrameTime = timestamp;
      
      this.requestFrame();
    });
  }

  private updateMetrics(): void {
    this.updateMemoryUsage();
    this.updateCPUUsage();
    this.updateNetworkLatency();
    this.updateRenderMetrics();
  }

  private updateMemoryUsage(): void {
    if (typeof process !== 'undefined' && process.memoryUsage) {
      const memUsage = process.memoryUsage();
      this.metrics.memoryUsage = {
        used: memUsage.rss,
        total: memUsage.rss + memUsage.external,
        heapUsed: memUsage.heapUsed,
        heapTotal: memUsage.heapTotal,
        external: memUsage.external
      };
      
      // Keep memory history for trend analysis
      this.memoryHistory.push(memUsage.heapUsed);
      if (this.memoryHistory.length > 300) { // Keep 30 seconds of data
        this.memoryHistory.shift();
      }
    } else if (typeof window !== 'undefined' && 'memory' in performance) {
      const mem = (performance as any).memory;
      this.metrics.memoryUsage = {
        used: mem.usedJSHeapSize,
        total: mem.totalJSHeapSize,
        heapUsed: mem.usedJSHeapSize,
        heapTotal: mem.totalJSHeapSize,
        external: 0
      };
    }
  }

  private updateCPUUsage(): void {
    if (typeof process !== 'undefined' && process.cpuUsage) {
      const cpuUsage = process.cpuUsage();
      const total = cpuUsage.user + cpuUsage.system;
      
      this.metrics.cpuUsage = {
        user: (cpuUsage.user / total) * 100,
        system: (cpuUsage.system / total) * 100,
        idle: 100 - ((cpuUsage.user + cpuUsage.system) / total) * 100
      };
    }
  }

  private async updateNetworkLatency(): Promise<void> {
    try {
      const start = performance.now();
      // Simple latency test - you might want to ping a specific endpoint
      await fetch('data:text/plain,ping', { method: 'HEAD' });
      this.metrics.networkLatency = performance.now() - start;
    } catch (error) {
      this.metrics.networkLatency = -1; // Error state
    }
  }

  private updateRenderMetrics(): void {
    // This would be populated by your rendering system
    // For now, we'll simulate some metrics
    this.metrics.renderMetrics = {
      drawCalls: Math.floor(Math.random() * 100),
      triangles: Math.floor(Math.random() * 10000),
      geometries: Math.floor(Math.random() * 50),
      textures: Math.floor(Math.random() * 20)
    };
  }

  private checkForBottlenecks(): void {
    const alerts: BottleneckAlert[] = [];
    
    // FPS bottleneck detection
    if (this.metrics.fps < this.thresholds.fps.critical) {
      alerts.push({
        type: 'fps',
        severity: 'critical',
        message: `Critical FPS drop: ${this.metrics.fps.toFixed(1)} fps`,
        timestamp: Date.now(),
        metrics: { fps: this.metrics.fps, frameTime: this.metrics.frameTime },
        suggestions: [
          'Reduce render complexity',
          'Optimize rendering pipeline',
          'Check for infinite loops',
          'Profile JavaScript execution'
        ]
      });
    } else if (this.metrics.fps < this.thresholds.fps.warning) {
      alerts.push({
        type: 'fps',
        severity: 'medium',
        message: `Low FPS detected: ${this.metrics.fps.toFixed(1)} fps`,
        timestamp: Date.now(),
        metrics: { fps: this.metrics.fps },
        suggestions: [
          'Check for expensive operations',
          'Optimize animations',
          'Reduce DOM manipulations'
        ]
      });
    }
    
    // Memory bottleneck detection
    const memoryUsagePercent = this.metrics.memoryUsage.heapUsed / this.metrics.memoryUsage.heapTotal;
    if (memoryUsagePercent > this.thresholds.memory.critical) {
      alerts.push({
        type: 'memory',
        severity: 'critical',
        message: `Critical memory usage: ${(memoryUsagePercent * 100).toFixed(1)}%`,
        timestamp: Date.now(),
        metrics: { memoryUsage: this.metrics.memoryUsage },
        suggestions: [
          'Check for memory leaks',
          'Clear unused objects',
          'Optimize data structures',
          'Force garbage collection'
        ]
      });
    }
    
    // CPU bottleneck detection
    const totalCPU = this.metrics.cpuUsage.user + this.metrics.cpuUsage.system;
    if (totalCPU > this.thresholds.cpu.critical) {
      alerts.push({
        type: 'cpu',
        severity: 'critical',
        message: `High CPU usage: ${totalCPU.toFixed(1)}%`,
        timestamp: Date.now(),
        metrics: { cpuUsage: this.metrics.cpuUsage },
        suggestions: [
          'Profile CPU-intensive operations',
          'Optimize algorithms',
          'Use web workers for heavy tasks',
          'Implement throttling'
        ]
      });
    }
    
    // Network latency detection
    if (this.metrics.networkLatency > this.thresholds.networkLatency.critical) {
      alerts.push({
        type: 'network',
        severity: 'high',
        message: `High network latency: ${this.metrics.networkLatency.toFixed(0)}ms`,
        timestamp: Date.now(),
        metrics: { networkLatency: this.metrics.networkLatency },
        suggestions: [
          'Check network connection',
          'Implement request caching',
          'Optimize API calls',
          'Use CDN for static assets'
        ]
      });
    }
    
    // Fire alerts
    alerts.forEach(alert => this.fireAlert(alert));
  }

  private fireAlert(alert: BottleneckAlert): void {
    this.alertCallbacks.forEach(callback => callback(alert));
  }

  // Custom performance marks
  public mark(name: string): void {
    performance.mark(name);
  }

  public measure(name: string, startMark: string, endMark?: string): void {
    if (endMark) {
      performance.measure(name, startMark, endMark);
    } else {
      performance.measure(name, startMark);
    }
  }

  // Heap snapshot (Node.js only)
  public takeHeapSnapshot(): Promise<any> {
    return new Promise((resolve, reject) => {
      if (typeof process !== 'undefined' && process.versions && process.versions.node) {
        try {
          const v8 = require('v8');
          const heapSnapshot = v8.getHeapSnapshot();
          resolve(heapSnapshot);
        } catch (error) {
          reject(error);
        }
      } else {
        reject(new Error('Heap snapshots only available in Node.js environment'));
      }
    });
  }

  // Observer pattern for metrics updates
  public subscribe(callback: (metrics: PerformanceMetrics) => void): () => void {
    this.observers.push(callback);
    return () => {
      const index = this.observers.indexOf(callback);
      if (index > -1) {
        this.observers.splice(index, 1);
      }
    };
  }

  public subscribeToAlerts(callback: (alert: BottleneckAlert) => void): () => void {
    this.alertCallbacks.push(callback);
    return () => {
      const index = this.alertCallbacks.indexOf(callback);
      if (index > -1) {
        this.alertCallbacks.splice(index, 1);
      }
    };
  }

  private notifyObservers(): void {
    this.observers.forEach(callback => callback(this.metrics));
  }

  public getMetrics(): PerformanceMetrics {
    return { ...this.metrics };
  }

  public getMemoryTrend(): number[] {
    return [...this.memoryHistory];
  }

  public updateThresholds(newThresholds: Partial<typeof this.thresholds>): void {
    this.thresholds = { ...this.thresholds, ...newThresholds };
  }

  public reset(): void {
    this.metrics = this.initializeMetrics();
    this.fpsBuffer = [];
    this.memoryHistory = [];
    this.customMarks.clear();
    this.frameCount = 0;
  }
}

// Singleton instance
export const performanceMonitor = new PerformanceMonitor();