/**
 * ProgressBar Component - Progress indication with various styles
 */

import * as terminalKit from 'terminal-kit';
import { ComponentProps, Theme } from '../../types';
import { defaultTheme } from '../../themes/default';

export interface ProgressBarOptions extends ComponentProps {
  value: number;
  max?: number;
  min?: number;
  width?: number;
  height?: number;
  showPercentage?: boolean;
  showValue?: boolean;
  showETA?: boolean;
  label?: string;
  style?: 'bar' | 'dots' | 'blocks' | 'gradient' | 'minimal';
  animate?: boolean;
  color?: string;
  backgroundColor?: string;
  borderStyle?: 'single' | 'double' | 'rounded' | 'none';
  onComplete?: () => void;
  onUpdate?: (value: number, percentage: number) => void;
}

export class ProgressBar {
  private terminal: terminalKit.Terminal;
  private options: ProgressBarOptions;
  private theme: Theme;
  private startTime: number;
  private lastUpdateTime: number;
  private animationFrame?: NodeJS.Timeout;
  private animationOffset: number = 0;

  constructor(terminal: terminalKit.Terminal, options: ProgressBarOptions) {
    this.terminal = terminal;
    this.options = {
      max: 100,
      min: 0,
      width: 40,
      height: 1,
      showPercentage: true,
      showValue: false,
      showETA: false,
      style: 'bar',
      animate: false,
      borderStyle: 'single',
      ...options
    };
    this.theme = { ...defaultTheme, ...options.theme };
    
    this.startTime = Date.now();
    this.lastUpdateTime = this.startTime;
    
    if (this.options.animate) {
      this.startAnimation();
    }
  }

  /**
   * Render the progress bar
   */
  public render(): void {
    const { style, height } = this.options;
    
    // Clear area
    this.terminal.eraseLine();
    
    // Render label if provided
    if (this.options.label) {
      this.renderLabel();
      this.terminal.nextLine();
    }
    
    // Render progress bar based on style
    for (let row = 0; row < height!; row++) {
      this.renderProgressRow(row);
      if (row < height! - 1) {
        this.terminal.nextLine();
      }
    }
    
    // Render additional info
    this.renderInfo();
  }

  /**
   * Render label
   */
  private renderLabel(): void {
    const { label } = this.options;
    this.terminal.color(this.theme.foreground, label!);
  }

  /**
   * Render progress bar row
   */
  private renderProgressRow(row: number): void {
    const { style, borderStyle, width } = this.options;
    
    // Render border if enabled
    if (borderStyle !== 'none') {
      this.renderBorder('start', row);
    }
    
    // Render progress content
    switch (style) {
      case 'dots':
        this.renderDotsProgress();
        break;
      case 'blocks':
        this.renderBlocksProgress();
        break;
      case 'gradient':
        this.renderGradientProgress();
        break;
      case 'minimal':
        this.renderMinimalProgress();
        break;
      default: // bar
        this.renderBarProgress();
        break;
    }
    
    // Render border end if enabled
    if (borderStyle !== 'none') {
      this.renderBorder('end', row);
    }
  }

  /**
   * Render border characters
   */
  private renderBorder(position: 'start' | 'end', row: number): void {
    const { borderStyle, height } = this.options;
    let char = '';
    
    switch (borderStyle) {
      case 'double':
        char = position === 'start' ? '║' : '║';
        break;
      case 'rounded':
        if (height === 1) {
          char = position === 'start' ? '(' : ')';
        } else {
          char = position === 'start' ? '│' : '│';
        }
        break;
      default: // single
        char = position === 'start' ? '│' : '│';
        break;
    }
    
    this.terminal.color(this.theme.border, char);
  }

  /**
   * Render bar-style progress
   */
  private renderBarProgress(): void {
    const { width, animate } = this.options;
    const percentage = this.getPercentage();
    const fillWidth = Math.floor((width! * percentage) / 100);
    const emptyWidth = width! - fillWidth;
    
    // Filled portion
    let fillChar = '█';
    let fillColor = this.options.color || this.theme.primary;
    
    if (animate && percentage < 100) {
      const animatedChars = ['█', '▉', '▊', '▋', '▌', '▍', '▎', '▏'];
      fillChar = animatedChars[this.animationOffset % animatedChars.length];
    }
    
    this.terminal.color(fillColor, fillChar.repeat(fillWidth));
    
    // Empty portion
    const emptyChar = '░';
    const emptyColor = this.options.backgroundColor || this.theme.muted;
    this.terminal.color(emptyColor, emptyChar.repeat(emptyWidth));
  }

  /**
   * Render dots-style progress
   */
  private renderDotsProgress(): void {
    const { width } = this.options;
    const percentage = this.getPercentage();
    const fillWidth = Math.floor((width! * percentage) / 100);
    
    for (let i = 0; i < width!; i++) {
      if (i < fillWidth) {
        this.terminal.color(this.theme.primary, '●');
      } else {
        this.terminal.color(this.theme.muted, '○');
      }
    }
  }

  /**
   * Render blocks-style progress
   */
  private renderBlocksProgress(): void {
    const { width } = this.options;
    const percentage = this.getPercentage();
    const fillWidth = Math.floor((width! * percentage) / 100);
    
    for (let i = 0; i < width!; i++) {
      if (i < fillWidth) {
        this.terminal.color(this.theme.primary, '▓');
      } else {
        this.terminal.color(this.theme.muted, '░');
      }
    }
  }

  /**
   * Render gradient-style progress
   */
  private renderGradientProgress(): void {
    const { width } = this.options;
    const percentage = this.getPercentage();
    const fillWidth = Math.floor((width! * percentage) / 100);
    
    const gradientChars = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█'];
    
    for (let i = 0; i < width!; i++) {
      if (i < fillWidth) {
        const intensity = Math.floor((i / fillWidth) * (gradientChars.length - 1));
        this.terminal.color(this.theme.primary, gradientChars[intensity]);
      } else {
        this.terminal.color(this.theme.muted, '▁');
      }
    }
  }

  /**
   * Render minimal-style progress
   */
  private renderMinimalProgress(): void {
    const { width } = this.options;
    const percentage = this.getPercentage();
    const position = Math.floor((width! * percentage) / 100);
    
    for (let i = 0; i < width!; i++) {
      if (i === position && percentage < 100) {
        this.terminal.color(this.theme.primary, '▶');
      } else if (i < position) {
        this.terminal.color(this.theme.success, '─');
      } else {
        this.terminal.color(this.theme.muted, '─');
      }
    }
  }

  /**
   * Render additional information
   */
  private renderInfo(): void {
    const { showPercentage, showValue, showETA } = this.options;
    let info = '';
    
    // Add percentage
    if (showPercentage) {
      info += ` ${this.getPercentage().toFixed(1)}%`;
    }
    
    // Add value
    if (showValue) {
      info += ` (${this.options.value}/${this.options.max})`;
    }
    
    // Add ETA
    if (showETA) {
      const eta = this.calculateETA();
      if (eta) {
        info += ` ETA: ${eta}`;
      }
    }
    
    if (info) {
      this.terminal.color(this.theme.muted, info);
    }
  }

  /**
   * Calculate percentage
   */
  private getPercentage(): number {
    const { value, min, max } = this.options;
    const range = max! - min!;
    const adjustedValue = Math.max(min!, Math.min(max!, value));
    return ((adjustedValue - min!) / range) * 100;
  }

  /**
   * Calculate estimated time of arrival
   */
  private calculateETA(): string | null {
    const { value, max } = this.options;
    const elapsed = Date.now() - this.startTime;
    const progress = value / max!;
    
    if (progress <= 0 || progress >= 1) return null;
    
    const totalTime = elapsed / progress;
    const remainingTime = totalTime - elapsed;
    
    return this.formatDuration(remainingTime);
  }

  /**
   * Format duration in human-readable format
   */
  private formatDuration(ms: number): string {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes % 60}m`;
    } else if (minutes > 0) {
      return `${minutes}m ${seconds % 60}s`;
    } else {
      return `${seconds}s`;
    }
  }

  /**
   * Start animation loop
   */
  private startAnimation(): void {
    this.animationFrame = setInterval(() => {
      this.animationOffset++;
      if (this.getPercentage() < 100) {
        this.render();
      }
    }, 100);
  }

  /**
   * Stop animation loop
   */
  private stopAnimation(): void {
    if (this.animationFrame) {
      clearInterval(this.animationFrame);
      this.animationFrame = undefined;
    }
  }

  /**
   * Update progress value
   */
  public setValue(value: number): void {
    const oldValue = this.options.value;
    this.options.value = Math.max(this.options.min!, Math.min(this.options.max!, value));
    this.lastUpdateTime = Date.now();
    
    const percentage = this.getPercentage();
    
    // Trigger events
    this.options.onUpdate?.(this.options.value, percentage);
    
    if (percentage >= 100 && oldValue < this.options.max!) {
      this.stopAnimation();
      this.options.onComplete?.();
    }
    
    this.render();
  }

  /**
   * Increment progress by specified amount
   */
  public increment(amount: number = 1): void {
    this.setValue(this.options.value + amount);
  }

  /**
   * Reset progress to minimum value
   */
  public reset(): void {
    this.options.value = this.options.min!;
    this.startTime = Date.now();
    this.lastUpdateTime = this.startTime;
    this.animationOffset = 0;
    
    if (this.options.animate && !this.animationFrame) {
      this.startAnimation();
    }
    
    this.render();
  }

  /**
   * Complete progress (set to maximum)
   */
  public complete(): void {
    this.setValue(this.options.max!);
  }

  /**
   * Get current value
   */
  public getValue(): number {
    return this.options.value;
  }

  /**
   * Get current percentage
   */
  public getPercentageValue(): number {
    return this.getPercentage();
  }

  /**
   * Set maximum value
   */
  public setMax(max: number): void {
    this.options.max = max;
    this.render();
  }

  /**
   * Set label
   */
  public setLabel(label: string): void {
    this.options.label = label;
    this.render();
  }

  /**
   * Enable/disable animation
   */
  public setAnimate(animate: boolean): void {
    this.options.animate = animate;
    
    if (animate && !this.animationFrame && this.getPercentage() < 100) {
      this.startAnimation();
    } else if (!animate && this.animationFrame) {
      this.stopAnimation();
    }
  }

  /**
   * Destroy progress bar and cleanup
   */
  public destroy(): void {
    this.stopAnimation();
  }
}

// Factory function for easier usage
export function createProgressBar(
  terminal: terminalKit.Terminal,
  options: ProgressBarOptions
): ProgressBar {
  return new ProgressBar(terminal, options);
}

// Convenience function for simple progress indication
export async function showProgress<T>(
  terminal: terminalKit.Terminal,
  task: (progressBar: ProgressBar) => Promise<T>,
  options: Partial<ProgressBarOptions> = {}
): Promise<T> {
  const progressBar = new ProgressBar(terminal, {
    value: 0,
    max: 100,
    ...options
  });
  
  try {
    const result = await task(progressBar);
    progressBar.complete();
    return result;
  } finally {
    progressBar.destroy();
  }
}