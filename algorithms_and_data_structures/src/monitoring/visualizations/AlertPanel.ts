/**
 * AlertPanel - Alert and notification management system
 * Features: Real-time alerts, severity levels, acknowledgment, filtering
 */

import { systemHealth, SystemAlert } from '../SystemHealth';
import { errorMonitor, ErrorCapture } from '../ErrorMonitor';
import { performanceMonitor, BottleneckAlert } from '../PerformanceMonitor';

export interface AlertPanelConfig {
  position: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';
  maxAlerts: number;
  autoHide: boolean;
  autoHideDelay: number;
  showTimestamp: boolean;
  enableNotifications: boolean;
  enableSound: boolean;
  groupSimilar: boolean;
  persistAlerts: boolean;
  theme: 'light' | 'dark' | 'auto';
}

export interface AlertGroup {
  id: string;
  type: string;
  component: string;
  count: number;
  firstAlert: Date;
  lastAlert: Date;
  severity: 'info' | 'warning' | 'error' | 'critical';
  alerts: Alert[];
  acknowledged: boolean;
}

export interface Alert {
  id: string;
  type: 'system' | 'performance' | 'error' | 'custom';
  severity: 'info' | 'warning' | 'error' | 'critical';
  title: string;
  message: string;
  timestamp: Date;
  component?: string;
  metadata?: Record<string, any>;
  acknowledged: boolean;
  persistent: boolean;
  actions?: AlertAction[];
}

export interface AlertAction {
  id: string;
  label: string;
  action: () => void | Promise<void>;
  style: 'primary' | 'secondary' | 'danger';
}

export interface AlertFilter {
  severity?: ('info' | 'warning' | 'error' | 'critical')[];
  type?: ('system' | 'performance' | 'error' | 'custom')[];
  component?: string[];
  acknowledged?: boolean;
  timeRange?: { start: Date; end: Date };
}

export class AlertPanel {
  private container: HTMLElement;
  private config: AlertPanelConfig;
  private alerts = new Map<string, Alert>();
  private alertGroups = new Map<string, AlertGroup>();
  private observers: Array<(event: string, data: any) => void> = [];
  private panelElement?: HTMLElement;
  private isVisible = true;
  private filter: AlertFilter = {};
  
  // Subscriptions
  private systemHealthSubscription?: () => void;
  private errorSubscription?: () => void;
  private performanceSubscription?: () => void;
  
  // Notification support
  private audioContext?: AudioContext;
  private notificationPermission: NotificationPermission = 'default';

  constructor(container: HTMLElement, config: Partial<AlertPanelConfig> = {}) {
    this.container = container;
    this.config = { ...this.getDefaultConfig(), ...config };
    
    this.init();
  }

  private getDefaultConfig(): AlertPanelConfig {
    return {
      position: 'top-right',
      maxAlerts: 10,
      autoHide: false,
      autoHideDelay: 5000,
      showTimestamp: true,
      enableNotifications: true,
      enableSound: true,
      groupSimilar: true,
      persistAlerts: true,
      theme: 'auto'
    };
  }

  private init(): void {
    this.createPanel();
    this.setupSubscriptions();
    this.setupNotifications();
    this.loadPersistedAlerts();
    this.applyTheme();
  }

  private createPanel(): void {
    this.panelElement = document.createElement('div');
    this.panelElement.className = `alert-panel alert-panel-${this.config.position}`;
    this.panelElement.innerHTML = `
      <div class="alert-panel-header">
        <div class="alert-panel-title">
          <span class="icon">🚨</span>
          <span class="text">Alerts</span>
          <span class="count-badge">0</span>
        </div>
        <div class="alert-panel-controls">
          <button class="btn-filter" title="Filter alerts">🔍</button>
          <button class="btn-clear-all" title="Clear all alerts">🗑️</button>
          <button class="btn-settings" title="Settings">⚙️</button>
          <button class="btn-minimize" title="Minimize">➖</button>
        </div>
      </div>
      
      <div class="alert-panel-content">
        <div class="alerts-container">
          <div class="no-alerts">
            <div class="icon">✅</div>
            <div class="message">No active alerts</div>
          </div>
        </div>
      </div>
      
      <div class="alert-panel-footer">
        <div class="alert-summary">
          <span class="critical-count">0 Critical</span>
          <span class="error-count">0 Errors</span>
          <span class="warning-count">0 Warnings</span>
        </div>
      </div>
    `;
    
    this.container.appendChild(this.panelElement);
    this.setupEventListeners();
  }

  private setupEventListeners(): void {
    if (!this.panelElement) return;
    
    // Minimize/maximize
    const minimizeBtn = this.panelElement.querySelector('.btn-minimize') as HTMLButtonElement;
    minimizeBtn?.addEventListener('click', () => {
      this.toggleMinimize();
    });
    
    // Clear all alerts
    const clearAllBtn = this.panelElement.querySelector('.btn-clear-all') as HTMLButtonElement;
    clearAllBtn?.addEventListener('click', () => {
      this.clearAllAlerts();
    });
    
    // Filter button
    const filterBtn = this.panelElement.querySelector('.btn-filter') as HTMLButtonElement;
    filterBtn?.addEventListener('click', () => {
      this.showFilterDialog();
    });
    
    // Settings button
    const settingsBtn = this.panelElement.querySelector('.btn-settings') as HTMLButtonElement;
    settingsBtn?.addEventListener('click', () => {
      this.showSettingsDialog();
    });
  }

  private setupSubscriptions(): void {
    // System health alerts
    this.systemHealthSubscription = systemHealth.subscribeToAlerts((alert: SystemAlert) => {
      this.addAlert({
        id: alert.id,
        type: 'system',
        severity: this.mapSeverity(alert.severity),
        title: `${alert.component} ${alert.type}`,
        message: alert.message,
        timestamp: new Date(alert.timestamp),
        component: alert.component,
        metadata: alert.metadata,
        acknowledged: alert.acknowledged,
        persistent: alert.severity === 'critical',
        actions: this.createSystemAlertActions(alert)
      });
    });
    
    // Error monitor alerts
    this.errorSubscription = errorMonitor.subscribe((error: ErrorCapture) => {
      this.addAlert({
        id: error.id,
        type: 'error',
        severity: this.mapErrorSeverity(error.severity),
        title: `${error.type} Error`,
        message: error.message,
        timestamp: new Date(error.timestamp),
        component: error.context.component,
        metadata: {
          stack: error.stack,
          context: error.context,
          category: error.category
        },
        acknowledged: false,
        persistent: error.severity === 'critical',
        actions: this.createErrorAlertActions(error)
      });
    });
    
    // Performance monitor alerts
    this.performanceSubscription = performanceMonitor.subscribeToAlerts((alert: BottleneckAlert) => {
      this.addAlert({
        id: `perf_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        type: 'performance',
        severity: this.mapPerformanceSeverity(alert.severity),
        title: `${alert.type.toUpperCase()} Performance Alert`,
        message: alert.message,
        timestamp: new Date(alert.timestamp),
        component: alert.type,
        metadata: {
          metrics: alert.metrics,
          suggestions: alert.suggestions
        },
        acknowledged: false,
        persistent: alert.severity === 'critical',
        actions: this.createPerformanceAlertActions(alert)
      });
    });
  }

  private setupNotifications(): void {
    if (this.config.enableNotifications && 'Notification' in window) {
      Notification.requestPermission().then(permission => {
        this.notificationPermission = permission;
      });
    }
    
    if (this.config.enableSound && 'AudioContext' in window) {
      this.audioContext = new AudioContext();
    }
  }

  private mapSeverity(severity: string): Alert['severity'] {
    switch (severity) {
      case 'critical': return 'critical';
      case 'error': return 'error';
      case 'warning': return 'warning';
      default: return 'info';
    }
  }

  private mapErrorSeverity(severity: string): Alert['severity'] {
    switch (severity) {
      case 'critical': return 'critical';
      case 'high': return 'error';
      case 'medium': return 'warning';
      default: return 'info';
    }
  }

  private mapPerformanceSeverity(severity: string): Alert['severity'] {
    switch (severity) {
      case 'critical': return 'critical';
      case 'high': return 'error';
      case 'medium': return 'warning';
      default: return 'info';
    }
  }

  private createSystemAlertActions(alert: SystemAlert): AlertAction[] {
    const actions: AlertAction[] = [
      {
        id: 'acknowledge',
        label: 'Acknowledge',
        action: () => {
          systemHealth.acknowledgeAlert(alert.id);
          this.acknowledgeAlert(alert.id);
        },
        style: 'secondary'
      }
    ];
    
    if (alert.component === 'memory_usage') {
      actions.push({
        id: 'cleanup',
        label: 'Cleanup Memory',
        action: async () => {
          // Trigger memory cleanup
          if (typeof global !== 'undefined' && global.gc) {
            global.gc();
          }
          this.showToast('Memory cleanup attempted', 'success');
        },
        style: 'primary'
      });
    }
    
    return actions;
  }

  private createErrorAlertActions(error: ErrorCapture): AlertAction[] {
    return [
      {
        id: 'acknowledge',
        label: 'Acknowledge',
        action: () => {
          this.acknowledgeAlert(error.id);
        },
        style: 'secondary'
      },
      {
        id: 'view_details',
        label: 'View Details',
        action: () => {
          this.showErrorDetails(error);
        },
        style: 'primary'
      }
    ];
  }

  private createPerformanceAlertActions(alert: BottleneckAlert): AlertAction[] {
    const actions: AlertAction[] = [
      {
        id: 'acknowledge',
        label: 'Acknowledge',
        action: () => {
          this.acknowledgeAlert(`perf_${alert.timestamp}`);
        },
        style: 'secondary'
      }
    ];
    
    // Add suggestion-based actions
    if (alert.suggestions.includes('Force garbage collection')) {
      actions.push({
        id: 'gc',
        label: 'Force GC',
        action: () => {
          if (typeof global !== 'undefined' && global.gc) {
            global.gc();
            this.showToast('Garbage collection triggered', 'success');
          }
        },
        style: 'primary'
      });
    }
    
    return actions;
  }

  public addAlert(alert: Alert): void {
    // Check if we should group similar alerts
    if (this.config.groupSimilar) {
      const existingGroup = this.findSimilarGroup(alert);
      if (existingGroup) {
        this.addToGroup(existingGroup, alert);
        this.updatePanel();
        return;
      }
    }
    
    this.alerts.set(alert.id, alert);
    
    // Create new group if grouping is enabled
    if (this.config.groupSimilar) {
      const group: AlertGroup = {
        id: `group_${alert.id}`,
        type: alert.type,
        component: alert.component || 'unknown',
        count: 1,
        firstAlert: alert.timestamp,
        lastAlert: alert.timestamp,
        severity: alert.severity,
        alerts: [alert],
        acknowledged: false
      };
      
      this.alertGroups.set(group.id, group);
    }
    
    // Trim alerts if over limit
    if (this.alerts.size > this.config.maxAlerts) {
      const oldestId = Array.from(this.alerts.keys())[0];
      this.alerts.delete(oldestId);
    }
    
    // Show notification
    if (this.config.enableNotifications) {
      this.showNotification(alert);
    }
    
    // Play sound
    if (this.config.enableSound) {
      this.playAlertSound(alert.severity);
    }
    
    // Auto-hide if configured
    if (this.config.autoHide && !alert.persistent) {
      setTimeout(() => {
        this.removeAlert(alert.id);
      }, this.config.autoHideDelay);
    }
    
    this.updatePanel();
    this.persistAlerts();
    
    this.notifyObservers('alertAdded', alert);
  }

  private findSimilarGroup(alert: Alert): AlertGroup | undefined {
    return Array.from(this.alertGroups.values()).find(group => 
      group.type === alert.type &&
      group.component === alert.component &&
      Math.abs(group.lastAlert.getTime() - alert.timestamp.getTime()) < 60000 // Within 1 minute
    );
  }

  private addToGroup(group: AlertGroup, alert: Alert): void {
    group.count++;
    group.lastAlert = alert.timestamp;
    group.alerts.push(alert);
    
    // Update severity to highest
    const severityOrder = ['info', 'warning', 'error', 'critical'];
    if (severityOrder.indexOf(alert.severity) > severityOrder.indexOf(group.severity)) {
      group.severity = alert.severity;
    }
    
    this.alerts.set(alert.id, alert);
  }

  public removeAlert(alertId: string): void {
    const alert = this.alerts.get(alertId);
    if (!alert) return;
    
    this.alerts.delete(alertId);
    
    // Remove from groups
    for (const [groupId, group] of this.alertGroups.entries()) {
      group.alerts = group.alerts.filter(a => a.id !== alertId);
      if (group.alerts.length === 0) {
        this.alertGroups.delete(groupId);
      } else {
        group.count = group.alerts.length;
      }
    }
    
    this.updatePanel();
    this.persistAlerts();
    
    this.notifyObservers('alertRemoved', { alertId, alert });
  }

  public acknowledgeAlert(alertId: string): void {
    const alert = this.alerts.get(alertId);
    if (alert) {
      alert.acknowledged = true;
      
      // Update group acknowledgment
      for (const group of this.alertGroups.values()) {
        if (group.alerts.some(a => a.id === alertId)) {
          group.acknowledged = group.alerts.every(a => a.acknowledged);
          break;
        }
      }
      
      this.updatePanel();
      this.persistAlerts();
      
      this.notifyObservers('alertAcknowledged', { alertId, alert });
    }
  }

  public clearAllAlerts(): void {
    this.alerts.clear();
    this.alertGroups.clear();
    this.updatePanel();
    this.persistAlerts();
    
    this.notifyObservers('allAlertsCleared', {});
  }

  private updatePanel(): void {
    if (!this.panelElement) return;
    
    const alertsContainer = this.panelElement.querySelector('.alerts-container') as HTMLElement;
    const countBadge = this.panelElement.querySelector('.count-badge') as HTMLElement;
    const noAlertsElement = this.panelElement.querySelector('.no-alerts') as HTMLElement;
    
    const filteredAlerts = this.getFilteredAlerts();
    const filteredGroups = this.getFilteredGroups();
    
    // Update count
    const totalCount = this.config.groupSimilar ? filteredGroups.length : filteredAlerts.length;
    countBadge.textContent = totalCount.toString();
    
    // Show/hide no alerts message
    if (totalCount === 0) {
      noAlertsElement.style.display = 'flex';
      alertsContainer.innerHTML = '';
      alertsContainer.appendChild(noAlertsElement);
    } else {
      noAlertsElement.style.display = 'none';
      this.renderAlerts(alertsContainer, filteredAlerts, filteredGroups);
    }
    
    // Update summary
    this.updateSummary(filteredAlerts);
  }

  private renderAlerts(container: HTMLElement, alerts: Alert[], groups: AlertGroup[]): void {
    container.innerHTML = '';
    
    if (this.config.groupSimilar && groups.length > 0) {
      groups.forEach(group => {
        const groupElement = this.createGroupElement(group);
        container.appendChild(groupElement);
      });
    } else {
      alerts.forEach(alert => {
        const alertElement = this.createAlertElement(alert);
        container.appendChild(alertElement);
      });
    }
  }

  private createAlertElement(alert: Alert): HTMLElement {
    const alertElement = document.createElement('div');
    alertElement.className = `alert-item severity-${alert.severity} ${alert.acknowledged ? 'acknowledged' : ''}`;
    alertElement.dataset.alertId = alert.id;
    
    alertElement.innerHTML = `
      <div class="alert-header">
        <div class="alert-icon">${this.getSeverityIcon(alert.severity)}</div>
        <div class="alert-title">${alert.title}</div>
        <div class="alert-time">${this.formatTime(alert.timestamp)}</div>
      </div>
      
      <div class="alert-content">
        <div class="alert-message">${alert.message}</div>
        ${alert.component ? `<div class="alert-component">Component: ${alert.component}</div>` : ''}
      </div>
      
      <div class="alert-actions">
        ${alert.actions?.map(action => 
          `<button class="alert-action btn-${action.style}" data-action="${action.id}">
            ${action.label}
           </button>`
        ).join('') || ''}
        <button class="alert-dismiss" title="Dismiss">✕</button>
      </div>
    `;
    
    // Setup action handlers
    alertElement.addEventListener('click', (e) => {
      const target = e.target as HTMLElement;
      
      if (target.classList.contains('alert-dismiss')) {
        this.removeAlert(alert.id);
      } else if (target.classList.contains('alert-action')) {
        const actionId = target.dataset.action;
        const action = alert.actions?.find(a => a.id === actionId);
        if (action) {
          action.action();
        }
      }
    });
    
    return alertElement;
  }

  private createGroupElement(group: AlertGroup): HTMLElement {
    const groupElement = document.createElement('div');
    groupElement.className = `alert-group severity-${group.severity} ${group.acknowledged ? 'acknowledged' : ''}`;
    
    const latestAlert = group.alerts[group.alerts.length - 1];
    
    groupElement.innerHTML = `
      <div class="group-header">
        <div class="group-icon">${this.getSeverityIcon(group.severity)}</div>
        <div class="group-title">${latestAlert.title}</div>
        <div class="group-count">${group.count}</div>
        <div class="group-time">${this.formatTime(group.lastAlert)}</div>
      </div>
      
      <div class="group-content">
        <div class="group-message">${latestAlert.message}</div>
        <div class="group-summary">
          First: ${this.formatTime(group.firstAlert)} | 
          Component: ${group.component}
        </div>
      </div>
      
      <div class="group-actions">
        <button class="group-expand">Expand (${group.count})</button>
        <button class="group-acknowledge">Acknowledge All</button>
        <button class="group-dismiss">Dismiss All</button>
      </div>
      
      <div class="group-details" style="display: none;">
        ${group.alerts.map(alert => `
          <div class="group-alert-item">
            <span class="time">${this.formatTime(alert.timestamp)}</span>
            <span class="message">${alert.message}</span>
          </div>
        `).join('')}
      </div>
    `;
    
    // Setup group handlers
    groupElement.addEventListener('click', (e) => {
      const target = e.target as HTMLElement;
      
      if (target.classList.contains('group-expand')) {
        const details = groupElement.querySelector('.group-details') as HTMLElement;
        const isVisible = details.style.display !== 'none';
        details.style.display = isVisible ? 'none' : 'block';
        target.textContent = isVisible ? `Expand (${group.count})` : `Collapse (${group.count})`;
      } else if (target.classList.contains('group-acknowledge')) {
        group.alerts.forEach(alert => this.acknowledgeAlert(alert.id));
      } else if (target.classList.contains('group-dismiss')) {
        group.alerts.forEach(alert => this.removeAlert(alert.id));
      }
    });
    
    return groupElement;
  }

  private getSeverityIcon(severity: Alert['severity']): string {
    switch (severity) {
      case 'critical': return '🔴';
      case 'error': return '❌';
      case 'warning': return '⚠️';
      default: return 'ℹ️';
    }
  }

  private formatTime(timestamp: Date): string {
    if (this.config.showTimestamp) {
      const now = new Date();
      const diff = now.getTime() - timestamp.getTime();
      
      if (diff < 60000) return 'Just now';
      if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
      if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
      
      return timestamp.toLocaleString();
    }
    
    return '';
  }

  private updateSummary(alerts: Alert[]): void {
    if (!this.panelElement) return;
    
    const criticalCount = alerts.filter(a => a.severity === 'critical').length;
    const errorCount = alerts.filter(a => a.severity === 'error').length;
    const warningCount = alerts.filter(a => a.severity === 'warning').length;
    
    const criticalElement = this.panelElement.querySelector('.critical-count') as HTMLElement;
    const errorElement = this.panelElement.querySelector('.error-count') as HTMLElement;
    const warningElement = this.panelElement.querySelector('.warning-count') as HTMLElement;
    
    if (criticalElement) criticalElement.textContent = `${criticalCount} Critical`;
    if (errorElement) errorElement.textContent = `${errorCount} Errors`;
    if (warningElement) warningElement.textContent = `${warningCount} Warnings`;
  }

  private getFilteredAlerts(): Alert[] {
    let alerts = Array.from(this.alerts.values());
    
    if (this.filter.severity && this.filter.severity.length > 0) {
      alerts = alerts.filter(a => this.filter.severity!.includes(a.severity));
    }
    
    if (this.filter.type && this.filter.type.length > 0) {
      alerts = alerts.filter(a => this.filter.type!.includes(a.type));
    }
    
    if (this.filter.component && this.filter.component.length > 0) {
      alerts = alerts.filter(a => a.component && this.filter.component!.includes(a.component));
    }
    
    if (this.filter.acknowledged !== undefined) {
      alerts = alerts.filter(a => a.acknowledged === this.filter.acknowledged);
    }
    
    if (this.filter.timeRange) {
      alerts = alerts.filter(a => 
        a.timestamp >= this.filter.timeRange!.start && 
        a.timestamp <= this.filter.timeRange!.end
      );
    }
    
    return alerts.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
  }

  private getFilteredGroups(): AlertGroup[] {
    return Array.from(this.alertGroups.values())
      .filter(group => group.alerts.some(alert => this.getFilteredAlerts().includes(alert)))
      .sort((a, b) => b.lastAlert.getTime() - a.lastAlert.getTime());
  }

  private showNotification(alert: Alert): void {
    if (this.notificationPermission !== 'granted') return;
    
    const notification = new Notification(alert.title, {
      body: alert.message,
      icon: this.getSeverityIcon(alert.severity),
      tag: alert.id,
      requireInteraction: alert.severity === 'critical'
    });
    
    notification.addEventListener('click', () => {
      window.focus();
      this.showAlertDetails(alert);
      notification.close();
    });
    
    // Auto-close non-critical notifications
    if (alert.severity !== 'critical') {
      setTimeout(() => {
        notification.close();
      }, 5000);
    }
  }

  private playAlertSound(severity: Alert['severity']): void {
    if (!this.audioContext) return;
    
    const frequency = severity === 'critical' ? 800 : severity === 'error' ? 600 : 400;
    const duration = severity === 'critical' ? 500 : 200;
    
    const oscillator = this.audioContext.createOscillator();
    const gainNode = this.audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(this.audioContext.destination);
    
    oscillator.frequency.value = frequency;
    oscillator.type = 'square';
    
    gainNode.gain.setValueAtTime(0.1, this.audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + duration / 1000);
    
    oscillator.start(this.audioContext.currentTime);
    oscillator.stop(this.audioContext.currentTime + duration / 1000);
  }

  private showAlertDetails(alert: Alert): void {
    // Implementation would show a detailed modal
    console.log('Show alert details', alert);
  }

  private showErrorDetails(error: ErrorCapture): void {
    // Implementation would show error details modal
    console.log('Show error details', error);
  }

  private showToast(message: string, type: 'success' | 'error' | 'info'): void {
    // Implementation would show a toast notification
    console.log(`Toast (${type}): ${message}`);
  }

  private toggleMinimize(): void {
    if (!this.panelElement) return;
    
    this.panelElement.classList.toggle('minimized');
    
    const minimizeBtn = this.panelElement.querySelector('.btn-minimize') as HTMLElement;
    minimizeBtn.textContent = this.panelElement.classList.contains('minimized') ? '➕' : '➖';
  }

  private showFilterDialog(): void {
    // Implementation would show filter dialog
    console.log('Show filter dialog');
  }

  private showSettingsDialog(): void {
    // Implementation would show settings dialog
    console.log('Show settings dialog');
  }

  private persistAlerts(): void {
    if (!this.config.persistAlerts) return;
    
    try {
      const data = {
        alerts: Array.from(this.alerts.entries()),
        groups: Array.from(this.alertGroups.entries())
      };
      
      localStorage.setItem('alertPanel', JSON.stringify(data));
    } catch (error) {
      console.warn('Failed to persist alerts:', error);
    }
  }

  private loadPersistedAlerts(): void {
    if (!this.config.persistAlerts) return;
    
    try {
      const data = localStorage.getItem('alertPanel');
      if (!data) return;
      
      const parsed = JSON.parse(data);
      
      this.alerts = new Map(parsed.alerts.map(([id, alert]: [string, any]) => [
        id, 
        { ...alert, timestamp: new Date(alert.timestamp) }
      ]));
      
      this.alertGroups = new Map(parsed.groups.map(([id, group]: [string, any]) => [
        id,
        {
          ...group,
          firstAlert: new Date(group.firstAlert),
          lastAlert: new Date(group.lastAlert),
          alerts: group.alerts.map((a: any) => ({ ...a, timestamp: new Date(a.timestamp) }))
        }
      ]));
      
      this.updatePanel();
    } catch (error) {
      console.warn('Failed to load persisted alerts:', error);
    }
  }

  private applyTheme(): void {
    if (!this.panelElement) return;
    
    const theme = this.config.theme === 'auto' ? 
      (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light') :
      this.config.theme;
    
    this.panelElement.setAttribute('data-theme', theme);
  }

  public setFilter(filter: AlertFilter): void {
    this.filter = filter;
    this.updatePanel();
    this.notifyObservers('filterChanged', filter);
  }

  public getAlerts(): Alert[] {
    return Array.from(this.alerts.values());
  }

  public getAlert(id: string): Alert | undefined {
    return this.alerts.get(id);
  }

  public subscribe(callback: (event: string, data: any) => void): () => void {
    this.observers.push(callback);
    return () => {
      const index = this.observers.indexOf(callback);
      if (index > -1) {
        this.observers.splice(index, 1);
      }
    };
  }

  private notifyObservers(event: string, data: any): void {
    this.observers.forEach(callback => callback(event, data));
  }

  public dispose(): void {
    // Clean up subscriptions
    this.systemHealthSubscription?.();
    this.errorSubscription?.();
    this.performanceSubscription?.();
    
    // Remove panel from DOM
    if (this.panelElement) {
      this.panelElement.remove();
    }
    
    this.observers = [];
  }
}

// Factory function
export function createAlertPanel(
  container: HTMLElement,
  config?: Partial<AlertPanelConfig>
): AlertPanel {
  return new AlertPanel(container, config);
}