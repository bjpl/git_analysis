/**
 * Comprehensive Real-Time Monitoring System
 * 
 * This module provides a complete monitoring solution for CLI UI applications
 * with real-time performance tracking, user analytics, error monitoring,
 * system health checks, and interactive visualizations.
 * 
 * @example
 * ```typescript
 * import { 
 *   performanceMonitor, 
 *   userAnalytics, 
 *   realTimeMetrics, 
 *   errorMonitor, 
 *   systemHealth,
 *   createMetricsDashboard,
 *   createAlertPanel 
 * } from './src/monitoring';
 * 
 * // Start monitoring
 * performanceMonitor.start();
 * systemHealth.startMonitoring();
 * 
 * // Create dashboard
 * const dashboard = createMetricsDashboard(containerElement);
 * dashboard.start();
 * 
 * // Create alert panel
 * const alertPanel = createAlertPanel(document.body);
 * ```
 */

// Core monitoring systems
export { 
  PerformanceMonitor, 
  performanceMonitor,
  type PerformanceMetrics,
  type BottleneckAlert
} from './PerformanceMonitor';

export { 
  UserAnalytics, 
  userAnalytics,
  type CommandUsage,
  type NavigationFlow,
  type SessionMetrics,
  type FeatureAdoption,
  type ABTestConfig,
  type ABTestResult,
  type UserPreference
} from './UserAnalytics';

export { 
  RealTimeMetrics, 
  realTimeMetrics,
  type MetricDefinition,
  type MetricValue,
  type HistoricalData,
  type Alert,
  type DashboardConfig
} from './RealTimeMetrics';

export { 
  ErrorMonitor, 
  errorMonitor,
  type ErrorCapture,
  type ErrorPattern,
  type RecoverySuggestion,
  type ErrorAnalysis
} from './ErrorMonitor';

export { 
  SystemHealth, 
  systemHealth,
  type HealthCheckConfig,
  type HealthCheckResult,
  type SystemStatus,
  type SystemAlert,
  type RecoveryAction
} from './SystemHealth';

// Visualization components
export { 
  PerformanceChart,
  createPerformanceChart,
  type ChartConfig,
  type ChartData,
  type ChartRenderer
} from './visualizations/PerformanceChart';

export { 
  MetricsDashboard,
  createMetricsDashboard,
  type DashboardConfig as MetricsDashboardConfig,
  type WidgetConfig,
  type FilterConfig,
  type DashboardState
} from './visualizations/MetricsDashboard';

export { 
  AlertPanel,
  createAlertPanel,
  type AlertPanelConfig,
  type Alert as PanelAlert,
  type AlertGroup,
  type AlertAction,
  type AlertFilter
} from './visualizations/AlertPanel';

// Utility functions for quick setup
export const MonitoringSystem = {
  /**
   * Initialize the complete monitoring system with default configuration
   */
  async init(options: {
    container?: HTMLElement;
    enablePerformance?: boolean;
    enableAnalytics?: boolean;
    enableErrors?: boolean;
    enableHealth?: boolean;
    enableDashboard?: boolean;
    enableAlerts?: boolean;
  } = {}) {
    const {
      container = document.body,
      enablePerformance = true,
      enableAnalytics = true,
      enableErrors = true,
      enableHealth = true,
      enableDashboard = true,
      enableAlerts = true
    } = options;

    const instances: any = {};

    // Start core monitors
    if (enablePerformance) {
      performanceMonitor.start();
      instances.performanceMonitor = performanceMonitor;
    }

    if (enableHealth) {
      systemHealth.startMonitoring();
      instances.systemHealth = systemHealth;
    }

    if (enableAnalytics) {
      // User analytics starts automatically
      instances.userAnalytics = userAnalytics;
    }

    if (enableErrors) {
      // Error monitor starts automatically
      instances.errorMonitor = errorMonitor;
    }

    // Create dashboard
    if (enableDashboard && container) {
      const dashboardContainer = document.createElement('div');
      dashboardContainer.className = 'monitoring-dashboard-container';
      dashboardContainer.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 1000;
        background: rgba(0, 0, 0, 0.9);
        display: none;
        pointer-events: none;
      `;
      
      const dashboard = createMetricsDashboard(dashboardContainer);
      dashboard.start();
      container.appendChild(dashboardContainer);
      instances.dashboard = dashboard;

      // Add toggle button
      const toggleButton = document.createElement('button');
      toggleButton.textContent = '📊';
      toggleButton.title = 'Toggle Monitoring Dashboard';
      toggleButton.style.cssText = `
        position: fixed;
        top: 10px;
        right: 10px;
        z-index: 1001;
        background: #3b82f6;
        color: white;
        border: none;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        font-size: 18px;
        cursor: pointer;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
      `;
      
      let dashboardVisible = false;
      toggleButton.addEventListener('click', () => {
        dashboardVisible = !dashboardVisible;
        dashboardContainer.style.display = dashboardVisible ? 'block' : 'none';
        dashboardContainer.style.pointerEvents = dashboardVisible ? 'auto' : 'none';
      });
      
      container.appendChild(toggleButton);
    }

    // Create alert panel
    if (enableAlerts && container) {
      const alertPanel = createAlertPanel(container, {
        position: 'top-right',
        enableNotifications: true,
        enableSound: true,
        persistAlerts: true
      });
      instances.alertPanel = alertPanel;
    }

    // Add CSS styles for monitoring components
    if (!document.querySelector('#monitoring-styles')) {
      const styles = document.createElement('style');
      styles.id = 'monitoring-styles';
      styles.textContent = this.getDefaultStyles();
      document.head.appendChild(styles);
    }

    return instances;
  },

  /**
   * Get default CSS styles for monitoring components
   */
  getDefaultStyles(): string {
    return `
      /* Monitoring System Default Styles */
      .metrics-dashboard {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: var(--bg-color, #ffffff);
        color: var(--text-color, #111827);
        height: 100vh;
        display: flex;
        flex-direction: column;
      }

      .metrics-dashboard[data-theme="dark"] {
        --bg-color: #111827;
        --text-color: #f9fafb;
        --border-color: #374151;
        --grid-color: #4b5563;
      }

      .dashboard-header {
        padding: 1rem;
        border-bottom: 1px solid var(--border-color, #e5e7eb);
        display: flex;
        justify-content: space-between;
        align-items: center;
      }

      .dashboard-content {
        flex: 1;
        padding: 1rem;
        overflow: auto;
      }

      .charts-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
        gap: 1rem;
        margin-bottom: 2rem;
      }

      .chart-wrapper {
        background: var(--bg-color, #ffffff);
        border: 1px solid var(--border-color, #e5e7eb);
        border-radius: 8px;
        padding: 1rem;
        min-height: 300px;
      }

      .chart-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
      }

      .chart-content {
        height: 250px;
      }

      .chart-canvas {
        width: 100%;
        height: 100%;
      }

      .widgets-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1rem;
      }

      .dashboard-widget {
        background: var(--bg-color, #ffffff);
        border: 1px solid var(--border-color, #e5e7eb);
        border-radius: 8px;
        padding: 1rem;
      }

      .alert-panel {
        position: fixed;
        width: 320px;
        max-height: 500px;
        background: var(--bg-color, #ffffff);
        border: 1px solid var(--border-color, #e5e7eb);
        border-radius: 8px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        z-index: 1000;
        overflow: hidden;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      }

      .alert-panel-top-right {
        top: 20px;
        right: 20px;
      }

      .alert-panel-top-left {
        top: 20px;
        left: 20px;
      }

      .alert-panel-bottom-right {
        bottom: 20px;
        right: 20px;
      }

      .alert-panel-bottom-left {
        bottom: 20px;
        left: 20px;
      }

      .alert-panel.minimized .alert-panel-content,
      .alert-panel.minimized .alert-panel-footer {
        display: none;
      }

      .alert-item {
        border-left: 4px solid;
        margin: 0.5rem 0;
        padding: 0.75rem;
        background: rgba(0, 0, 0, 0.02);
        border-radius: 4px;
      }

      .alert-item.severity-critical {
        border-left-color: #dc2626;
        background: rgba(220, 38, 38, 0.05);
      }

      .alert-item.severity-error {
        border-left-color: #ef4444;
        background: rgba(239, 68, 68, 0.05);
      }

      .alert-item.severity-warning {
        border-left-color: #f59e0b;
        background: rgba(245, 158, 11, 0.05);
      }

      .alert-item.severity-info {
        border-left-color: #3b82f6;
        background: rgba(59, 130, 246, 0.05);
      }

      .no-alerts {
        text-align: center;
        padding: 2rem;
        color: var(--text-color, #6b7280);
      }

      .performance-chart-tooltip {
        background: rgba(0, 0, 0, 0.9);
        color: white;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 12px;
        pointer-events: none;
        z-index: 1000;
        white-space: nowrap;
      }

      /* Responsive design */
      @media (max-width: 768px) {
        .charts-container {
          grid-template-columns: 1fr;
        }
        
        .alert-panel {
          width: calc(100vw - 40px);
          left: 20px !important;
          right: 20px !important;
        }
        
        .metrics-dashboard {
          font-size: 14px;
        }
      }

      /* Animation utilities */
      .fade-in {
        animation: fadeIn 0.3s ease-in;
      }

      @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
      }

      .slide-up {
        animation: slideUp 0.3s ease-out;
      }

      @keyframes slideUp {
        from { transform: translateY(20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
      }
    `;
  },

  /**
   * Create a minimal monitoring setup with performance tracking only
   */
  minimal(container?: HTMLElement) {
    return this.init({
      container,
      enablePerformance: true,
      enableAnalytics: false,
      enableErrors: true,
      enableHealth: false,
      enableDashboard: false,
      enableAlerts: true
    });
  },

  /**
   * Create a full-featured monitoring setup
   */
  complete(container?: HTMLElement) {
    return this.init({
      container,
      enablePerformance: true,
      enableAnalytics: true,
      enableErrors: true,
      enableHealth: true,
      enableDashboard: true,
      enableAlerts: true
    });
  },

  /**
   * Stop all monitoring and cleanup resources
   */
  dispose() {
    performanceMonitor.stop();
    systemHealth.stopMonitoring();
    userAnalytics.dispose();
    errorMonitor.dispose();
    realTimeMetrics.dispose();
  }
};

// Default export for convenience
export default MonitoringSystem;