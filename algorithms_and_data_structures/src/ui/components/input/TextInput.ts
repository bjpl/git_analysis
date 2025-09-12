/**
 * TextInput Component - Single line text input with validation
 */

import * as terminalKit from 'terminal-kit';
import { InputProps, ValidationRule, Theme } from '../../types';
import { defaultTheme } from '../../themes/default';

export interface TextInputOptions extends InputProps {
  maxLength?: number;
  minLength?: number;
  mask?: boolean;
  validation?: ValidationRule[];
  autoComplete?: string[];
  history?: string[];
}

export class TextInput {
  private terminal: terminalKit.Terminal;
  private options: TextInputOptions;
  private theme: Theme;
  private currentValue: string = '';
  private cursorPosition: number = 0;
  private isActive: boolean = false;
  private errors: string[] = [];

  constructor(terminal: terminalKit.Terminal, options: TextInputOptions = {}) {
    this.terminal = terminal;
    this.options = { ...options };
    this.theme = { ...defaultTheme, ...options.theme };
    this.currentValue = options.value || '';
    this.cursorPosition = this.currentValue.length;
  }

  /**
   * Render the input field
   */
  public render(): void {
    const { placeholder = '', disabled = false } = this.options;
    
    // Clear current line
    this.terminal.eraseLine();
    
    // Draw input box
    this.drawInputBox();
    
    // Show value or placeholder
    const displayValue = this.currentValue || placeholder;
    const valueColor = this.currentValue ? this.theme.foreground : this.theme.muted;
    
    if (disabled) {
      this.terminal.color256(8, displayValue);
    } else {
      this.terminal.color(valueColor, displayValue);
    }
    
    // Show cursor if active
    if (this.isActive && !disabled) {
      this.showCursor();
    }
    
    // Show validation errors
    if (this.errors.length > 0) {
      this.showErrors();
    }
  }

  /**
   * Start input session
   */
  public async input(): Promise<string> {
    return new Promise((resolve, reject) => {
      this.isActive = true;
      this.render();
      
      const cleanup = () => {
        this.isActive = false;
        this.terminal.removeAllListeners('key');
      };

      this.terminal.on('key', (name: string, matches: any, data: any) => {
        try {
          if (this.handleKeyPress(name, matches, data)) {
            cleanup();
            
            if (this.validate()) {
              this.options.onSubmit?.(this.currentValue);
              resolve(this.currentValue);
            } else {
              reject(new Error(this.errors.join(', ')));
            }
          }
        } catch (error) {
          cleanup();
          reject(error);
        }
      });

      // Handle Ctrl+C
      this.terminal.on('key', (name: string) => {
        if (name === 'CTRL_C') {
          cleanup();
          this.options.onCancel?.();
          reject(new Error('Input cancelled'));
        }
      });
    });
  }

  /**
   * Handle key press events
   */
  private handleKeyPress(name: string, matches: any, data: any): boolean {
    const { maxLength, disabled } = this.options;
    
    if (disabled) return false;

    switch (name) {
      case 'ENTER':
        return true; // Submit

      case 'BACKSPACE':
        if (this.cursorPosition > 0) {
          this.currentValue = 
            this.currentValue.slice(0, this.cursorPosition - 1) + 
            this.currentValue.slice(this.cursorPosition);
          this.cursorPosition--;
          this.onChange();
        }
        break;

      case 'DELETE':
        if (this.cursorPosition < this.currentValue.length) {
          this.currentValue = 
            this.currentValue.slice(0, this.cursorPosition) + 
            this.currentValue.slice(this.cursorPosition + 1);
          this.onChange();
        }
        break;

      case 'LEFT':
        if (this.cursorPosition > 0) {
          this.cursorPosition--;
        }
        break;

      case 'RIGHT':
        if (this.cursorPosition < this.currentValue.length) {
          this.cursorPosition++;
        }
        break;

      case 'HOME':
        this.cursorPosition = 0;
        break;

      case 'END':
        this.cursorPosition = this.currentValue.length;
        break;

      default:
        // Handle printable characters
        if (data && data.isCharacter && (!maxLength || this.currentValue.length < maxLength)) {
          const char = String.fromCharCode(data.codepoint);
          this.currentValue = 
            this.currentValue.slice(0, this.cursorPosition) + 
            char + 
            this.currentValue.slice(this.cursorPosition);
          this.cursorPosition++;
          this.onChange();
        }
        break;
    }

    this.render();
    return false;
  }

  /**
   * Validate current value
   */
  private validate(): boolean {
    this.errors = [];
    const { required, minLength, validation } = this.options;
    
    // Required validation
    if (required && !this.currentValue.trim()) {
      this.errors.push('This field is required');
    }
    
    // Minimum length validation
    if (minLength && this.currentValue.length < minLength) {
      this.errors.push(`Minimum length is ${minLength} characters`);
    }
    
    // Custom validation rules
    if (validation) {
      for (const rule of validation) {
        if (!rule.test(this.currentValue)) {
          this.errors.push(rule.message);
        }
      }
    }
    
    return this.errors.length === 0;
  }

  /**
   * Handle value change
   */
  private onChange(): void {
    this.options.onChange?.(this.currentValue);
    this.validate(); // Update errors in real-time
  }

  /**
   * Draw input box border
   */
  private drawInputBox(): void {
    const hasError = this.errors.length > 0;
    const borderColor = hasError ? this.theme.error : this.theme.border;
    
    this.terminal.color(borderColor, '[');
    this.terminal.color(borderColor, ']');
    this.terminal.left(1);
  }

  /**
   * Show cursor at current position
   */
  private showCursor(): void {
    const displayValue = this.currentValue || this.options.placeholder || '';
    this.terminal.left(displayValue.length - this.cursorPosition);
    this.terminal.color(this.theme.accent, '|');
  }

  /**
   * Show validation errors
   */
  private showErrors(): void {
    this.terminal.nextLine();
    for (const error of this.errors) {
      this.terminal.color(this.theme.error, `  ⚠ ${error}\n`);
    }
    this.terminal.up(this.errors.length + 1);
  }

  /**
   * Set value programmatically
   */
  public setValue(value: string): void {
    this.currentValue = value;
    this.cursorPosition = value.length;
    this.onChange();
    this.render();
  }

  /**
   * Get current value
   */
  public getValue(): string {
    return this.currentValue;
  }

  /**
   * Focus the input
   */
  public focus(): void {
    this.isActive = true;
    this.options.onFocus?.();
    this.render();
  }

  /**
   * Blur the input
   */
  public blur(): void {
    this.isActive = false;
    this.options.onBlur?.();
    this.render();
  }

  /**
   * Enable/disable the input
   */
  public setDisabled(disabled: boolean): void {
    this.options.disabled = disabled;
    this.render();
  }
}

// Factory function for easier usage
export function createTextInput(
  terminal: terminalKit.Terminal, 
  options: TextInputOptions = {}
): TextInput {
  return new TextInput(terminal, options);
}