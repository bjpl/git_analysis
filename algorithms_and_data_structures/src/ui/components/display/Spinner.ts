/**
 * Spinner Component - Loading indicators with various animations
 */

import * as terminalKit from 'terminal-kit';
import { ComponentProps, Theme } from '../../types';
import { defaultTheme } from '../../themes/default';

export interface SpinnerOptions extends ComponentProps {
  text?: string;
  style?: 'dots' | 'line' | 'pipe' | 'star' | 'arrow' | 'bounce' | 'pulse' | 'clock' | 'moon' | 'runner';
  color?: string;
  speed?: number;
  hideText?: boolean;
  indent?: number;
  onComplete?: () => void;
}

interface SpinnerFrame {
  frames: string[];
  interval: number;
}

export class Spinner {
  private terminal: terminalKit.Terminal;
  private options: SpinnerOptions;
  private theme: Theme;
  private currentFrame: number = 0;
  private animationTimer?: NodeJS.Timeout;
  private isSpinning: boolean = false;
  private startTime: number = 0;

  private readonly spinnerStyles: Record<string, SpinnerFrame> = {
    dots: {
      frames: ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'],
      interval: 80
    },
    line: {
      frames: ['|', '/', '-', '\\'],
      interval: 100
    },
    pipe: {
      frames: ['┤', '┘', '┴', '└', '├', '┌', '┬', '┐'],
      interval: 100
    },
    star: {
      frames: ['✶', '✸', '✹', '✺', '✹', '✷'],
      interval: 120
    },
    arrow: {
      frames: ['←', '↖', '↑', '↗', '→', '↘', '↓', '↙'],
      interval: 120
    },
    bounce: {
      frames: ['⠁', '⠂', '⠄', '⠂'],
      interval: 300
    },
    pulse: {
      frames: ['●', '○', '◉', '○'],
      interval: 200
    },
    clock: {
      frames: ['🕐', '🕑', '🕒', '🕓', '🕔', '🕕', '🕖', '🕗', '🕘', '🕙', '🕚', '🕛'],
      interval: 100
    },
    moon: {
      frames: ['🌑', '🌒', '🌓', '🌔', '🌕', '🌖', '🌗', '🌘'],
      interval: 200
    },
    runner: {
      frames: ['🚶', '🏃'],
      interval: 200
    }
  };

  constructor(terminal: terminalKit.Terminal, options: SpinnerOptions = {}) {
    this.terminal = terminal;
    this.options = {
      text: 'Loading...',
      style: 'dots',
      speed: 1,
      hideText: false,
      indent: 0,
      ...options
    };
    this.theme = { ...defaultTheme, ...options.theme };
  }

  /**
   * Start the spinner animation
   */
  public start(text?: string): Spinner {
    if (text) {
      this.options.text = text;
    }

    if (this.isSpinning) {
      this.stop();
    }

    this.isSpinning = true;
    this.startTime = Date.now();
    this.currentFrame = 0;
    
    // Hide cursor during animation
    this.terminal.hideCursor();
    
    this.render();
    this.scheduleNextFrame();

    return this;
  }

  /**
   * Stop the spinner animation
   */
  public stop(): Spinner {
    if (this.animationTimer) {
      clearTimeout(this.animationTimer);
      this.animationTimer = undefined;
    }

    this.isSpinning = false;
    
    // Show cursor again
    this.terminal.showCursor();
    
    // Clear the spinner line
    this.clearLine();

    return this;
  }

  /**
   * Update the spinner text without stopping animation
   */
  public setText(text: string): Spinner {
    this.options.text = text;
    return this;
  }

  /**
   * Change spinner style
   */
  public setStyle(style: SpinnerOptions['style']): Spinner {
    this.options.style = style;
    this.currentFrame = 0;
    return this;
  }

  /**
   * Update spinner color
   */
  public setColor(color: string): Spinner {
    this.options.color = color;
    return this;
  }

  /**
   * Success completion
   */
  public succeed(text?: string): Spinner {
    this.stop();
    this.renderCompletion('✅', text || this.options.text, this.theme.success);
    this.options.onComplete?.();
    return this;
  }

  /**
   * Failure completion
   */
  public fail(text?: string): Spinner {
    this.stop();
    this.renderCompletion('❌', text || this.options.text, this.theme.error);
    return this;
  }

  /**
   * Warning completion
   */
  public warn(text?: string): Spinner {
    this.stop();
    this.renderCompletion('⚠️', text || this.options.text, this.theme.warning);
    return this;
  }

  /**
   * Info completion
   */
  public info(text?: string): Spinner {
    this.stop();
    this.renderCompletion('ℹ️', text || this.options.text, this.theme.info);
    return this;
  }

  /**
   * Custom completion with icon
   */
  public complete(icon: string, text?: string, color?: string): Spinner {
    this.stop();
    this.renderCompletion(icon, text || this.options.text, color || this.theme.foreground);
    this.options.onComplete?.();
    return this;
  }

  /**
   * Get current spinner state
   */
  public isActive(): boolean {
    return this.isSpinning;
  }

  /**
   * Get elapsed time since start
   */
  public getElapsedTime(): number {
    return this.isSpinning ? Date.now() - this.startTime : 0;
  }

  /**
   * Render the current frame
   */
  private render(): void {
    if (!this.isSpinning) return;

    const style = this.spinnerStyles[this.options.style!];
    const frame = style.frames[this.currentFrame];
    
    // Clear current line
    this.clearLine();
    
    // Apply indentation
    if (this.options.indent! > 0) {
      this.terminal(' '.repeat(this.options.indent!));
    }
    
    // Render spinner frame
    const spinnerColor = this.options.color || this.theme.primary;
    this.terminal.color(spinnerColor, frame);
    
    // Render text if not hidden
    if (!this.options.hideText && this.options.text) {
      this.terminal(' ');
      this.terminal.color(this.theme.foreground, this.options.text);
      
      // Add elapsed time for long operations
      const elapsed = this.getElapsedTime();
      if (elapsed > 5000) { // Show time after 5 seconds
        const seconds = Math.floor(elapsed / 1000);
        this.terminal.color(this.theme.muted, ` (${seconds}s)`);
      }
    }
  }

  /**
   * Schedule the next animation frame
   */
  private scheduleNextFrame(): void {
    if (!this.isSpinning) return;

    const style = this.spinnerStyles[this.options.style!];
    const interval = Math.floor(style.interval / this.options.speed!);

    this.animationTimer = setTimeout(() => {
      this.currentFrame = (this.currentFrame + 1) % style.frames.length;
      this.render();
      this.scheduleNextFrame();
    }, interval);
  }

  /**
   * Clear the current line
   */
  private clearLine(): void {
    this.terminal.eraseLine();
    this.terminal.column(1);
  }

  /**
   * Render completion message
   */
  private renderCompletion(icon: string, text: string, color: string): void {
    // Apply indentation
    if (this.options.indent! > 0) {
      this.terminal(' '.repeat(this.options.indent!));
    }
    
    // Render completion icon and text
    this.terminal.color(color, `${icon} ${text}`);
    this.terminal.nextLine();
  }
}

// Factory function for easier usage
export function createSpinner(
  terminal: terminalKit.Terminal,
  options: SpinnerOptions = {}
): Spinner {
  return new Spinner(terminal, options);
}

// Convenience function for wrapping async operations
export async function withSpinner<T>(
  terminal: terminalKit.Terminal,
  task: () => Promise<T>,
  options: SpinnerOptions = {}
): Promise<T> {
  const spinner = new Spinner(terminal, options);
  
  try {
    spinner.start();
    const result = await task();
    spinner.succeed();
    return result;
  } catch (error) {
    spinner.fail();
    throw error;
  }
}

// Multiple spinners manager for complex operations
export class MultiSpinner {
  private terminal: terminalKit.Terminal;
  private spinners: Map<string, Spinner> = new Map();
  private options: SpinnerOptions;

  constructor(terminal: terminalKit.Terminal, options: SpinnerOptions = {}) {
    this.terminal = terminal;
    this.options = options;
  }

  /**
   * Add a new spinner
   */
  public add(key: string, text: string, options: Partial<SpinnerOptions> = {}): Spinner {
    const spinner = new Spinner(this.terminal, {
      ...this.options,
      ...options,
      text,
      indent: (this.options.indent || 0) + 2
    });
    
    this.spinners.set(key, spinner);
    return spinner;
  }

  /**
   * Start a specific spinner
   */
  public start(key: string, text?: string): boolean {
    const spinner = this.spinners.get(key);
    if (spinner) {
      spinner.start(text);
      return true;
    }
    return false;
  }

  /**
   * Stop a specific spinner
   */
  public stop(key: string): boolean {
    const spinner = this.spinners.get(key);
    if (spinner) {
      spinner.stop();
      return true;
    }
    return false;
  }

  /**
   * Complete a specific spinner with success
   */
  public succeed(key: string, text?: string): boolean {
    const spinner = this.spinners.get(key);
    if (spinner) {
      spinner.succeed(text);
      return true;
    }
    return false;
  }

  /**
   * Complete a specific spinner with failure
   */
  public fail(key: string, text?: string): boolean {
    const spinner = this.spinners.get(key);
    if (spinner) {
      spinner.fail(text);
      return true;
    }
    return false;
  }

  /**
   * Update text for a specific spinner
   */
  public setText(key: string, text: string): boolean {
    const spinner = this.spinners.get(key);
    if (spinner) {
      spinner.setText(text);
      return true;
    }
    return false;
  }

  /**
   * Start all spinners
   */
  public startAll(): void {
    this.spinners.forEach(spinner => spinner.start());
  }

  /**
   * Stop all spinners
   */
  public stopAll(): void {
    this.spinners.forEach(spinner => spinner.stop());
  }

  /**
   * Get all active spinners
   */
  public getActive(): string[] {
    const active: string[] = [];
    this.spinners.forEach((spinner, key) => {
      if (spinner.isActive()) {
        active.push(key);
      }
    });
    return active;
  }

  /**
   * Remove a spinner
   */
  public remove(key: string): boolean {
    const spinner = this.spinners.get(key);
    if (spinner) {
      spinner.stop();
      this.spinners.delete(key);
      return true;
    }
    return false;
  }

  /**
   * Clear all spinners
   */
  public clear(): void {
    this.stopAll();
    this.spinners.clear();
  }
}

// Factory function for multi-spinner
export function createMultiSpinner(
  terminal: terminalKit.Terminal,
  options: SpinnerOptions = {}
): MultiSpinner {
  return new MultiSpinner(terminal, options);
}