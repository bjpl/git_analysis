/**
 * Real-Time Metrics Dashboard
 * WebSocket-based live metrics with alerts and historical data
 */

export interface MetricDefinition {
  name: string;
  type: 'gauge' | 'counter' | 'histogram' | 'summary';
  description: string;
  unit?: string;
  labels?: string[];
  thresholds?: {
    warning?: number;
    critical?: number;
    min?: number;
    max?: number;
  };
}

export interface MetricValue {
  name: string;
  value: number;
  timestamp: number;
  labels?: Record<string, string>;
  metadata?: Record<string, any>;
}

export interface MetricSeries {
  metric: string;
  values: MetricValue[];
  aggregation?: 'avg' | 'sum' | 'min' | 'max' | 'count';
  window?: number; // Time window in ms
}

export interface Alert {
  id: string;
  metric: string;
  type: 'threshold' | 'anomaly' | 'missing_data' | 'rate_change';
  severity: 'info' | 'warning' | 'critical' | 'emergency';
  message: string;
  value: number;
  threshold?: number;
  timestamp: number;
  acknowledged: boolean;
  resolved: boolean;
  metadata?: Record<string, any>;
}

export interface DashboardConfig {
  title: string;
  refreshInterval: number;
  timeRange: number;
  metrics: string[];
  layout: {
    rows: number;
    columns: number;
    widgets: Array<{
      metric: string;
      type: 'line' | 'bar' | 'gauge' | 'number' | 'table';
      position: { row: number; col: number };
      size: { width: number; height: number };
      config?: Record<string, any>;
    }>;
  };
}

export class RealTimeMetrics {
  private metrics: Map<string, MetricDefinition> = new Map();
  private values: Map<string, MetricValue[]> = new Map();
  private alerts: Map<string, Alert> = new Map();
  private subscribers: Map<string, Set<(data: any) => void>> = new Map();
  private wsServer?: any; // WebSocket server instance
  private isRunning: boolean = false;
  private updateInterval?: NodeJS.Timeout;
  private alertCheckInterval?: NodeJS.Timeout;
  
  // Configuration
  private config = {
    maxValuesPerMetric: 1000,
    defaultTimeWindow: 5 * 60 * 1000, // 5 minutes\n    alertCheckInterval: 5000, // 5 seconds
    updateInterval: 1000, // 1 second
    retention: 24 * 60 * 60 * 1000, // 24 hours
    compression: {
      enabled: true,
      threshold: 100, // Compress after 100 values
      ratio: 0.5 // Keep 50% of values when compressing
    }
  };

  constructor() {
    this.initializeDefaultMetrics();
  }

  private initializeDefaultMetrics(): void {
    // Define default system metrics
    const defaultMetrics: MetricDefinition[] = [
      {
        name: 'system.cpu.usage',
        type: 'gauge',
        description: 'CPU usage percentage',
        unit: '%',
        thresholds: { warning: 70, critical: 90 }
      },
      {
        name: 'system.memory.usage',
        type: 'gauge',
        description: 'Memory usage percentage',
        unit: '%',
        thresholds: { warning: 80, critical: 95 }
      },
      {
        name: 'system.network.latency',
        type: 'histogram',
        description: 'Network latency',
        unit: 'ms',
        thresholds: { warning: 200, critical: 500 }
      },
      {
        name: 'application.response.time',
        type: 'histogram',
        description: 'Application response time',
        unit: 'ms',
        thresholds: { warning: 100, critical: 250 }
      },
      {
        name: 'application.error.count',
        type: 'counter',
        description: 'Total error count',
        thresholds: { warning: 10, critical: 25 }
      },
      {
        name: 'ui.fps',
        type: 'gauge',
        description: 'Frames per second',
        unit: 'fps',
        thresholds: { warning: 30, critical: 15, min: 0, max: 60 }
      },
      {
        name: 'commands.executed',
        type: 'counter',
        description: 'Total commands executed'
      },
      {
        name: 'session.duration',
        type: 'gauge',\n        description: 'Current session duration',
        unit: 'ms'
      }
    ];

    defaultMetrics.forEach(metric => {
      this.defineMetric(metric);
    });
  }

  // Metric Definition Management
  public defineMetric(definition: MetricDefinition): void {
    this.metrics.set(definition.name, definition);
    
    if (!this.values.has(definition.name)) {
      this.values.set(definition.name, []);
    }
    
    this.broadcast('metric_defined', { definition });
  }

  public getMetricDefinition(name: string): MetricDefinition | undefined {
    return this.metrics.get(name);
  }

  public getAllMetrics(): MetricDefinition[] {
    return Array.from(this.metrics.values());
  }

  // Value Recording
  public recordValue(name: string, value: number, labels?: Record<string, string>, metadata?: Record<string, any>): void {
    const definition = this.metrics.get(name);
    if (!definition) {
      console.warn(`Metric '${name}' not defined. Defining automatically.`);
      this.defineMetric({
        name,
        type: 'gauge',
        description: `Auto-generated metric: ${name}`
      });
    }

    const metricValue: MetricValue = {
      name,
      value,
      timestamp: Date.now(),
      labels,
      metadata
    };

    let values = this.values.get(name) || [];
    values.push(metricValue);
    
    // Limit values per metric to prevent memory bloat
    if (values.length > this.config.maxValuesPerMetric) {
      if (this.config.compression.enabled) {
        values = this.compressValues(values);
      } else {
        values = values.slice(-this.config.maxValuesPerMetric);
      }
    }
    
    this.values.set(name, values);
    
    // Check for alerts
    this.checkAlerts(name, metricValue);
    
    // Broadcast to subscribers
    this.broadcast('metric_update', { metric: name, value: metricValue });
  }

  private compressValues(values: MetricValue[]): MetricValue[] {
    const threshold = this.config.compression.threshold;
    const ratio = this.config.compression.ratio;
    
    if (values.length <= threshold) return values;
    
    const keepCount = Math.floor(values.length * ratio);
    const step = Math.floor(values.length / keepCount);
    
    const compressed: MetricValue[] = [];
    
    for (let i = 0; i < values.length; i += step) {
      // Take average of values in this step
      const chunk = values.slice(i, Math.min(i + step, values.length));
      const avgValue = chunk.reduce((sum, v) => sum + v.value, 0) / chunk.length;
      
      compressed.push({
        name: values[i].name,
        value: avgValue,
        timestamp: chunk[Math.floor(chunk.length / 2)].timestamp,
        labels: values[i].labels,
        metadata: { ...values[i].metadata, compressed: true, samples: chunk.length }
      });
    }
    
    // Always keep recent values uncompressed
    const recentCount = Math.min(50, Math.floor(threshold * 0.1));
    const recentValues = values.slice(-recentCount);
    
    return [...compressed, ...recentValues];
  }

  // Data Retrieval
  public getValues(name: string, timeRange?: number, aggregation?: 'avg' | 'sum' | 'min' | 'max' | 'count'): MetricValue[] {
    const values = this.values.get(name) || [];
    
    // Filter by time range
    let filteredValues = values;
    if (timeRange) {
      const cutoff = Date.now() - timeRange;
      filteredValues = values.filter(v => v.timestamp >= cutoff);
    }
    
    // Apply aggregation if requested
    if (aggregation && filteredValues.length > 0) {
      const aggregated = this.aggregateValues(filteredValues, aggregation);
      return [aggregated];
    }
    
    return filteredValues;
  }

  private aggregateValues(values: MetricValue[], aggregation: 'avg' | 'sum' | 'min' | 'max' | 'count'): MetricValue {
    const name = values[0].name;
    const timestamp = Date.now();
    
    let aggregatedValue: number;
    
    switch (aggregation) {
      case 'avg':
        aggregatedValue = values.reduce((sum, v) => sum + v.value, 0) / values.length;
        break;
      case 'sum':
        aggregatedValue = values.reduce((sum, v) => sum + v.value, 0);
        break;
      case 'min':
        aggregatedValue = Math.min(...values.map(v => v.value));
        break;
      case 'max':
        aggregatedValue = Math.max(...values.map(v => v.value));
        break;
      case 'count':
        aggregatedValue = values.length;
        break;
      default:
        aggregatedValue = values[values.length - 1]?.value || 0;
    }
    
    return {
      name,
      value: aggregatedValue,
      timestamp,
      metadata: { aggregation, samples: values.length }
    };
  }

  public getLatestValue(name: string): MetricValue | undefined {
    const values = this.values.get(name);
    return values && values.length > 0 ? values[values.length - 1] : undefined;
  }

  public getMetricSeries(names: string[], timeRange?: number): MetricSeries[] {
    return names.map(name => ({
      metric: name,
      values: this.getValues(name, timeRange),
      window: timeRange
    }));
  }

  // Alert Management
  private checkAlerts(metricName: string, value: MetricValue): void {
    const definition = this.metrics.get(metricName);
    if (!definition?.thresholds) return;
    
    const thresholds = definition.thresholds;
    const alertId = `${metricName}_threshold`;
    
    // Check threshold violations
    if (thresholds.critical !== undefined && 
        ((thresholds.max !== undefined && value.value > thresholds.critical) ||
         (thresholds.max === undefined && value.value > thresholds.critical))) {
      this.createAlert(alertId, metricName, 'threshold', 'critical', 
        `${metricName} exceeded critical threshold: ${value.value} > ${thresholds.critical}`,
        value.value, thresholds.critical);
    } else if (thresholds.warning !== undefined && 
               ((thresholds.max !== undefined && value.value > thresholds.warning) ||
                (thresholds.max === undefined && value.value > thresholds.warning))) {
      this.createAlert(alertId, metricName, 'threshold', 'warning',
        `${metricName} exceeded warning threshold: ${value.value} > ${thresholds.warning}`,
        value.value, thresholds.warning);
    } else {
      // Clear existing alert if value is back to normal
      this.resolveAlert(alertId);
    }
    
    // Check for minimum thresholds
    if (thresholds.min !== undefined && value.value < thresholds.min) {
      const minAlertId = `${metricName}_min_threshold`;
      this.createAlert(minAlertId, metricName, 'threshold', 'warning',
        `${metricName} below minimum threshold: ${value.value} < ${thresholds.min}`,
        value.value, thresholds.min);
    }
    
    // Anomaly detection (simple spike detection)
    this.checkAnomalies(metricName, value);
  }

  private checkAnomalies(metricName: string, currentValue: MetricValue): void {
    const values = this.values.get(metricName) || [];
    if (values.length < 10) return; // Need sufficient history
    
    const recent = values.slice(-10, -1); // Last 9 values (excluding current)
    const average = recent.reduce((sum, v) => sum + v.value, 0) / recent.length;
    const stdDev = Math.sqrt(recent.reduce((sum, v) => sum + Math.pow(v.value - average, 2), 0) / recent.length);
    
    // Detect spike (value > 3 standard deviations from average)
    if (Math.abs(currentValue.value - average) > 3 * stdDev) {
      const anomalyId = `${metricName}_anomaly`;
      this.createAlert(anomalyId, metricName, 'anomaly', 'warning',
        `Anomalous value detected for ${metricName}: ${currentValue.value} (expected ~${average.toFixed(2)})`,
        currentValue.value, average);
    }
  }

  private createAlert(id: string, metric: string, type: Alert['type'], severity: Alert['severity'], 
                     message: string, value: number, threshold?: number): void {
    const existing = this.alerts.get(id);
    
    // Don't create duplicate alerts
    if (existing && !existing.resolved) return;
    
    const alert: Alert = {
      id,
      metric,
      type,
      severity,
      message,
      value,
      threshold,
      timestamp: Date.now(),
      acknowledged: false,
      resolved: false
    };
    
    this.alerts.set(id, alert);
    this.broadcast('alert_created', { alert });
    
    console.warn(`ALERT [${severity.toUpperCase()}]: ${message}`);
  }

  public resolveAlert(id: string): void {
    const alert = this.alerts.get(id);
    if (alert && !alert.resolved) {
      alert.resolved = true;
      this.broadcast('alert_resolved', { alert });
    }
  }

  public acknowledgeAlert(id: string): void {
    const alert = this.alerts.get(id);
    if (alert) {
      alert.acknowledged = true;
      this.broadcast('alert_acknowledged', { alert });
    }
  }

  public getAlerts(includeResolved: boolean = false): Alert[] {
    return Array.from(this.alerts.values())
      .filter(alert => includeResolved || !alert.resolved)
      .sort((a, b) => b.timestamp - a.timestamp);
  }

  // WebSocket Real-time Updates
  public startRealTimeUpdates(port?: number): void {
    if (this.isRunning) return;
    
    try {\n      // Initialize WebSocket server (simplified for CLI environment)
      this.isRunning = true;
      
      // Start periodic updates
      this.updateInterval = setInterval(() => {
        this.collectSystemMetrics();
      }, this.config.updateInterval);
      
      // Start alert checking
      this.alertCheckInterval = setInterval(() => {
        this.checkMissingDataAlerts();
      }, this.config.alertCheckInterval);
      
      console.log('Real-time metrics started');
      this.broadcast('system_started', { timestamp: Date.now() });
      
    } catch (error) {
      console.error('Failed to start real-time updates:', error);
    }
  }

  public stopRealTimeUpdates(): void {
    this.isRunning = false;
    
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
      this.updateInterval = undefined;
    }
    
    if (this.alertCheckInterval) {
      clearInterval(this.alertCheckInterval);
      this.alertCheckInterval = undefined;
    }
    
    if (this.wsServer) {
      // Close WebSocket server
      try {
        this.wsServer.close();
      } catch (error) {
        console.error('Error closing WebSocket server:', error);
      }
    }
    
    console.log('Real-time metrics stopped');
    this.broadcast('system_stopped', { timestamp: Date.now() });
  }

  private collectSystemMetrics(): void {
    // Collect basic system metrics
    if (typeof process !== 'undefined') {
      const memUsage = process.memoryUsage();
      this.recordValue('system.memory.usage', 
        (memUsage.rss / (memUsage.rss + memUsage.external)) * 100);
      
      const cpuUsage = process.cpuUsage();
      this.recordValue('system.cpu.usage', 
        Math.min(100, (cpuUsage.user + cpuUsage.system) / 10000));
    }
    
    // Record current timestamp for session duration
    this.recordValue('system.timestamp', Date.now());
  }

  private checkMissingDataAlerts(): void {
    const now = Date.now();
    const timeout = 30000; // 30 seconds
    
    this.metrics.forEach((definition, name) => {
      const values = this.values.get(name);
      const latest = values && values.length > 0 ? values[values.length - 1] : null;
      
      if (!latest || (now - latest.timestamp) > timeout) {
        const alertId = `${name}_missing_data`;
        this.createAlert(alertId, name, 'missing_data', 'warning',
          `No data received for ${name} in the last ${timeout/1000} seconds`,
          0);
      }
    });
  }

  // Subscription Management
  public subscribe(event: string, callback: (data: any) => void): () => void {
    if (!this.subscribers.has(event)) {
      this.subscribers.set(event, new Set());
    }
    
    this.subscribers.get(event)!.add(callback);
    
    // Return unsubscribe function
    return () => {
      const eventSubscribers = this.subscribers.get(event);
      if (eventSubscribers) {
        eventSubscribers.delete(callback);
        if (eventSubscribers.size === 0) {
          this.subscribers.delete(event);
        }
      }
    };
  }

  private broadcast(event: string, data: any): void {
    const subscribers = this.subscribers.get(event);
    if (subscribers) {
      subscribers.forEach(callback => {
        try {
          callback({ event, data, timestamp: Date.now() });
        } catch (error) {\n          console.error(`Error in subscriber for event '${event}':`, error);
        }
      });
    }
    
    // Also broadcast to 'all' subscribers
    const allSubscribers = this.subscribers.get('all');
    if (allSubscribers) {
      allSubscribers.forEach(callback => {
        try {
          callback({ event, data, timestamp: Date.now() });
        } catch (error) {
          console.error(`Error in 'all' subscriber:`, error);
        }
      });
    }
  }

  // Export and Import
  public exportData(format: 'json' | 'csv' = 'json', timeRange?: number): string {
    const data = {
      metrics: Array.from(this.metrics.entries()),
      values: Array.from(this.values.entries()).map(([name, values]) => [
        name, 
        timeRange ? values.filter(v => v.timestamp >= (Date.now() - timeRange)) : values
      ]),
      alerts: Array.from(this.alerts.entries()),
      exportedAt: Date.now(),
      timeRange
    };
    
    if (format === 'json') {
      return JSON.stringify(data, null, 2);
    } else {
      // Convert to CSV format
      let csv = 'metric,timestamp,value,labels,metadata\\n';
      
      for (const [name, values] of data.values as any) {
        for (const value of values) {
          const labels = value.labels ? JSON.stringify(value.labels) : '';
          const metadata = value.metadata ? JSON.stringify(value.metadata) : '';
          csv += `${name},${value.timestamp},${value.value},"${labels}","${metadata}"\\n`;
        }
      }
      
      return csv;
    }
  }

  public importData(jsonData: string): void {
    try {
      const data = JSON.parse(jsonData);
      
      if (data.metrics) {
        this.metrics = new Map(data.metrics);
      }
      
      if (data.values) {
        this.values = new Map(data.values);
      }
      
      if (data.alerts) {
        this.alerts = new Map(data.alerts);
      }
      
      console.log('Metrics data imported successfully');
      this.broadcast('data_imported', { timestamp: Date.now() });
      
    } catch (error) {
      console.error('Failed to import metrics data:', error);
    }
  }

  // Dashboard Configuration
  public createDashboard(config: DashboardConfig): void {
    // Store dashboard configuration
    this.broadcast('dashboard_created', { config });
  }

  public getDashboardData(metrics: string[], timeRange: number): Record<string, MetricValue[]> {
    const data: Record<string, MetricValue[]> = {};
    
    metrics.forEach(metric => {
      data[metric] = this.getValues(metric, timeRange);
    });
    
    return data;
  }

  // Utility Methods
  public getHealthStatus(): {
    status: 'healthy' | 'warning' | 'critical';
    activeAlerts: number;
    metricsCount: number;
    uptime: number;
  } {
    const activeAlerts = this.getAlerts().length;
    const criticalAlerts = this.getAlerts().filter(a => a.severity === 'critical').length;
    
    let status: 'healthy' | 'warning' | 'critical' = 'healthy';
    if (criticalAlerts > 0) {
      status = 'critical';
    } else if (activeAlerts > 0) {
      status = 'warning';
    }
    
    return {
      status,
      activeAlerts,
      metricsCount: this.metrics.size,
      uptime: this.isRunning ? Date.now() : 0
    };
  }

  public dispose(): void {
    this.stopRealTimeUpdates();
    this.metrics.clear();
    this.values.clear();
    this.alerts.clear();
    this.subscribers.clear();
  }
}

export default RealTimeMetrics;