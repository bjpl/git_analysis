/**
 * Alert Component - Success/error/warning/info messages
 */

import * as terminalKit from 'terminal-kit';
import { ComponentProps, AlertType, Theme } from '../../types';
import { defaultTheme } from '../../themes/default';

export interface AlertOptions extends ComponentProps, AlertType {
  dismissible?: boolean;
  showIcon?: boolean;
  showTimestamp?: boolean;
  borderStyle?: 'single' | 'double' | 'rounded' | 'none';
  width?: number;
  multiline?: boolean;
  onDismiss?: () => void;
  onShow?: () => void;
  onHide?: () => void;
}

export class Alert {
  private terminal: terminalKit.Terminal;
  private options: AlertOptions;
  private theme: Theme;
  private isVisible: boolean = false;
  private autoHideTimer?: NodeJS.Timeout;
  private createdAt: Date;

  private readonly icons = {
    success: '✅',
    error: '❌',
    warning: '⚠️',
    info: 'ℹ️'
  };

  private readonly colors = {
    success: 'success',
    error: 'error',
    warning: 'warning',
    info: 'info'
  } as const;

  constructor(terminal: terminalKit.Terminal, options: AlertOptions) {
    this.terminal = terminal;
    this.options = {
      showIcon: true,
      showTimestamp: false,
      dismissible: false,
      borderStyle: 'single',
      multiline: true,
      persistent: false,
      duration: 3000,
      ...options
    };
    this.theme = { ...defaultTheme, ...options.theme };
    this.createdAt = new Date();
  }

  /**
   * Show the alert
   */
  public show(): Alert {
    if (this.isVisible) return this;

    this.isVisible = true;
    this.render();
    
    // Auto-hide if not persistent
    if (!this.options.persistent && this.options.duration) {
      this.scheduleAutoHide();
    }

    this.options.onShow?.();
    return this;
  }

  /**
   * Hide the alert
   */
  public hide(): Alert {
    if (!this.isVisible) return this;

    this.isVisible = false;
    this.clearAutoHide();
    this.clearAlert();
    
    this.options.onHide?.();
    return this;
  }

  /**
   * Dismiss the alert (hide with callback)
   */
  public dismiss(): Alert {
    this.options.onDismiss?.();
    return this.hide();
  }

  /**
   * Render the alert
   */
  public render(): void {
    if (!this.isVisible) return;

    const { type, message, borderStyle, width, multiline } = this.options;
    const color = this.theme[this.colors[type]];
    
    // Calculate content width
    const contentWidth = width || Math.min(this.terminal.width - 4, 80);
    
    // Process message text
    const lines = this.processMessage(message, contentWidth);
    
    // Render border top
    if (borderStyle !== 'none') {
      this.renderBorder('top', contentWidth, color);
    }
    
    // Render content lines
    lines.forEach((line, index) => {
      this.renderContentLine(line, contentWidth, color, index === 0);
    });
    
    // Render border bottom
    if (borderStyle !== 'none') {
      this.renderBorder('bottom', contentWidth, color);
    } else {
      this.terminal.nextLine();
    }
  }

  /**
   * Process message text into lines
   */
  private processMessage(message: string, maxWidth: number): string[] {
    const { multiline, showIcon, showTimestamp, dismissible } = this.options;
    
    // Calculate available width for message text
    let availableWidth = maxWidth - 4; // Account for borders and padding
    
    if (showIcon) availableWidth -= 3; // Icon + space
    if (dismissible) availableWidth -= 4; // [X] + space
    if (showTimestamp) availableWidth -= 10; // Timestamp format
    
    const lines: string[] = [];
    
    if (multiline) {
      // Split by newlines first
      const paragraphs = message.split('\n');
      
      paragraphs.forEach(paragraph => {
        if (paragraph.length <= availableWidth) {
          lines.push(paragraph);
        } else {
          // Word wrap
          const words = paragraph.split(' ');
          let currentLine = '';
          
          words.forEach(word => {
            if (currentLine.length + word.length + 1 <= availableWidth) {
              currentLine += (currentLine ? ' ' : '') + word;
            } else {
              if (currentLine) lines.push(currentLine);
              currentLine = word;
            }
          });
          
          if (currentLine) lines.push(currentLine);
        }
      });
    } else {
      // Single line, truncate if necessary
      if (message.length <= availableWidth) {
        lines.push(message);
      } else {
        lines.push(message.slice(0, availableWidth - 3) + '...');
      }
    }
    
    return lines;
  }

  /**
   * Render content line
   */
  private renderContentLine(text: string, width: number, color: string, isFirstLine: boolean): void {
    const { borderStyle, showIcon, showTimestamp, dismissible, type } = this.options;
    
    // Start line
    if (borderStyle !== 'none') {
      this.terminal.color(color, '│ ');
    } else {
      this.terminal('  ');
    }
    
    let lineContent = '';
    
    // Add icon on first line
    if (isFirstLine && showIcon) {
      const icon = this.icons[type];
      lineContent += `${icon} `;
    } else if (showIcon) {
      lineContent += '   '; // Maintain alignment
    }
    
    // Add message text
    lineContent += text;
    
    // Add timestamp on first line
    if (isFirstLine && showTimestamp) {
      const timestamp = this.formatTimestamp();
      const padding = Math.max(0, width - lineContent.length - timestamp.length - 4);
      lineContent += ' '.repeat(padding) + timestamp;
    }
    
    // Add dismiss button on first line
    if (isFirstLine && dismissible) {
      const dismissBtn = '[×]';
      const padding = Math.max(0, width - lineContent.length - dismissBtn.length - 4);
      lineContent += ' '.repeat(padding);
      this.terminal.color(this.theme.foreground, lineContent);
      this.terminal.color(this.theme.muted, dismissBtn);
    } else {
      this.terminal.color(this.theme.foreground, lineContent);
    }
    
    // End line
    if (borderStyle !== 'none') {
      const remaining = Math.max(0, width - lineContent.length - 2);
      this.terminal(' '.repeat(remaining));
      this.terminal.color(color, ' │');
    }
    
    this.terminal.nextLine();
  }

  /**
   * Render border
   */
  private renderBorder(position: 'top' | 'bottom', width: number, color: string): void {
    const { borderStyle } = this.options;
    
    let leftChar: string, rightChar: string, horizontalChar: string;
    
    switch (borderStyle) {
      case 'double':
        horizontalChar = '═';
        leftChar = position === 'top' ? '╔' : '╚';
        rightChar = position === 'top' ? '╗' : '╝';
        break;
      case 'rounded':
        horizontalChar = '─';
        leftChar = position === 'top' ? '╭' : '╰';
        rightChar = position === 'top' ? '╮' : '╯';
        break;
      default: // single
        horizontalChar = '─';
        leftChar = position === 'top' ? '┌' : '└';
        rightChar = position === 'top' ? '┐' : '┘';
    }
    
    this.terminal.color(color, leftChar);
    this.terminal.color(color, horizontalChar.repeat(width));
    this.terminal.color(color, rightChar);
    this.terminal.nextLine();
  }

  /**
   * Format timestamp
   */
  private formatTimestamp(): string {
    const now = new Date();
    const hours = now.getHours().toString().padStart(2, '0');
    const minutes = now.getMinutes().toString().padStart(2, '0');
    const seconds = now.getSeconds().toString().padStart(2, '0');
    return `${hours}:${minutes}:${seconds}`;
  }

  /**
   * Schedule auto-hide
   */
  private scheduleAutoHide(): void {
    if (this.autoHideTimer) {
      clearTimeout(this.autoHideTimer);
    }
    
    this.autoHideTimer = setTimeout(() => {
      this.hide();
    }, this.options.duration);
  }

  /**
   * Clear auto-hide timer
   */
  private clearAutoHide(): void {
    if (this.autoHideTimer) {
      clearTimeout(this.autoHideTimer);
      this.autoHideTimer = undefined;
    }
  }

  /**
   * Clear alert from terminal
   */
  private clearAlert(): void {
    // Move cursor up and clear lines
    // This is a simplified implementation - in practice, you'd need to track
    // the exact number of lines rendered and clear them properly
    this.terminal.eraseDisplayAbove();
  }

  /**
   * Update alert message
   */
  public setMessage(message: string): Alert {
    this.options.message = message;
    if (this.isVisible) {
      this.render();
    }
    return this;
  }

  /**
   * Update alert type
   */
  public setType(type: AlertType['type']): Alert {
    this.options.type = type;
    if (this.isVisible) {
      this.render();
    }
    return this;
  }

  /**
   * Set dismissible state
   */
  public setDismissible(dismissible: boolean): Alert {
    this.options.dismissible = dismissible;
    if (this.isVisible) {
      this.render();
    }
    return this;
  }

  /**
   * Check if alert is currently visible
   */
  public isShown(): boolean {
    return this.isVisible;
  }

  /**
   * Get alert creation time
   */
  public getCreatedAt(): Date {
    return this.createdAt;
  }

  /**
   * Get alert age in milliseconds
   */
  public getAge(): number {
    return Date.now() - this.createdAt.getTime();
  }
}

// Factory functions for different alert types
export function createAlert(
  terminal: terminalKit.Terminal,
  options: AlertOptions
): Alert {
  return new Alert(terminal, options);
}

export function createSuccessAlert(
  terminal: terminalKit.Terminal,
  message: string,
  options: Partial<AlertOptions> = {}
): Alert {
  return new Alert(terminal, {
    type: 'success',
    message,
    ...options
  });
}

export function createErrorAlert(
  terminal: terminalKit.Terminal,
  message: string,
  options: Partial<AlertOptions> = {}
): Alert {
  return new Alert(terminal, {
    type: 'error',
    message,
    persistent: true, // Errors should be persistent by default
    ...options
  });
}

export function createWarningAlert(
  terminal: terminalKit.Terminal,
  message: string,
  options: Partial<AlertOptions> = {}
): Alert {
  return new Alert(terminal, {
    type: 'warning',
    message,
    duration: 5000, // Warnings stay longer
    ...options
  });
}

export function createInfoAlert(
  terminal: terminalKit.Terminal,
  message: string,
  options: Partial<AlertOptions> = {}
): Alert {
  return new Alert(terminal, {
    type: 'info',
    message,
    ...options
  });
}

// Alert Manager for handling multiple alerts
export class AlertManager {
  private terminal: terminalKit.Terminal;
  private alerts: Map<string, Alert> = new Map();
  private queue: Alert[] = [];
  private maxVisible: number;
  private currentVisible: number = 0;

  constructor(terminal: terminalKit.Terminal, maxVisible: number = 3) {
    this.terminal = terminal;
    this.maxVisible = maxVisible;
  }

  /**
   * Add alert to manager
   */
  public add(id: string, alert: Alert): Alert {
    this.alerts.set(id, alert);
    
    if (this.currentVisible < this.maxVisible) {
      alert.show();
      this.currentVisible++;
    } else {
      this.queue.push(alert);
    }
    
    // Set up dismiss handler
    const originalOnHide = alert.options.onHide;
    alert.options.onHide = () => {
      this.currentVisible--;
      this.showNext();
      originalOnHide?.();
    };
    
    return alert;
  }

  /**
   * Show next queued alert
   */
  private showNext(): void {
    if (this.queue.length > 0 && this.currentVisible < this.maxVisible) {
      const nextAlert = this.queue.shift()!;
      nextAlert.show();
      this.currentVisible++;
    }
  }

  /**
   * Remove alert by ID
   */
  public remove(id: string): boolean {
    const alert = this.alerts.get(id);
    if (alert) {
      alert.hide();
      this.alerts.delete(id);
      return true;
    }
    return false;
  }

  /**
   * Clear all alerts
   */
  public clear(): void {
    this.alerts.forEach(alert => alert.hide());
    this.alerts.clear();
    this.queue.length = 0;
    this.currentVisible = 0;
  }

  /**
   * Get alert by ID
   */
  public get(id: string): Alert | undefined {
    return this.alerts.get(id);
  }

  /**
   * Get all visible alerts
   */
  public getVisible(): Alert[] {
    return Array.from(this.alerts.values()).filter(alert => alert.isShown());
  }

  /**
   * Get queue size
   */
  public getQueueSize(): number {
    return this.queue.length;
  }
}

// Factory function for alert manager
export function createAlertManager(
  terminal: terminalKit.Terminal,
  maxVisible: number = 3
): AlertManager {
  return new AlertManager(terminal, maxVisible);
}

// Convenience functions for quick alerts
export async function showSuccess(
  terminal: terminalKit.Terminal,
  message: string,
  duration: number = 2000
): Promise<void> {
  const alert = createSuccessAlert(terminal, message, { duration });
  alert.show();
  
  return new Promise(resolve => {
    setTimeout(resolve, duration);
  });
}

export async function showError(
  terminal: terminalKit.Terminal,
  message: string
): Promise<void> {
  const alert = createErrorAlert(terminal, message, {
    dismissible: true,
    persistent: true
  });
  alert.show();
  
  return new Promise(resolve => {
    alert.options.onDismiss = resolve;
  });
}

export async function showWarning(
  terminal: terminalKit.Terminal,
  message: string,
  duration: number = 4000
): Promise<void> {
  const alert = createWarningAlert(terminal, message, { duration });
  alert.show();
  
  return new Promise(resolve => {
    setTimeout(resolve, duration);
  });
}

export async function showInfo(
  terminal: terminalKit.Terminal,
  message: string,
  duration: number = 3000
): Promise<void> {
  const alert = createInfoAlert(terminal, message, { duration });
  alert.show();
  
  return new Promise(resolve => {
    setTimeout(resolve, duration);
  });
}