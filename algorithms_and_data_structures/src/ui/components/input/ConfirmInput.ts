/**
 * ConfirmInput Component - Yes/No confirmation prompts
 */

import * as terminalKit from 'terminal-kit';
import { ComponentProps, Theme } from '../../types';
import { defaultTheme } from '../../themes/default';

export interface ConfirmInputOptions extends ComponentProps {
  message: string;
  defaultValue?: boolean;
  yesLabel?: string;
  noLabel?: string;
  showButtons?: boolean;
  dangerMode?: boolean;
  onChange?: (value: boolean) => void;
  onSubmit?: (value: boolean) => void;
  onCancel?: () => void;
}

export class ConfirmInput {
  private terminal: terminalKit.Terminal;
  private options: ConfirmInputOptions;
  private theme: Theme;
  private currentValue: boolean;
  private isActive: boolean = false;

  constructor(terminal: terminalKit.Terminal, options: ConfirmInputOptions) {
    this.terminal = terminal;
    this.options = { 
      yesLabel: 'Yes',
      noLabel: 'No',
      showButtons: true,
      dangerMode: false,
      ...options 
    };
    this.theme = { ...defaultTheme, ...options.theme };
    this.currentValue = options.defaultValue ?? false;
  }

  /**
   * Render the confirmation prompt
   */
  public render(): void {
    // Clear area
    this.terminal.eraseLine();
    
    // Show message
    this.renderMessage();
    this.terminal(' ');
    
    // Show options
    if (this.options.showButtons) {
      this.renderButtons();
    } else {
      this.renderInline();
    }
  }

  /**
   * Render the message with appropriate styling
   */
  private renderMessage(): void {
    const { message, dangerMode } = this.options;
    
    // Warning icon for danger mode
    if (dangerMode) {
      this.terminal.color(this.theme.error, '⚠ ');
    }
    
    // Message text
    const messageColor = dangerMode ? this.theme.error : this.theme.foreground;
    this.terminal.color(messageColor, message);
  }

  /**
   * Render button-style options
   */
  private renderButtons(): void {
    const { yesLabel, noLabel, dangerMode } = this.options;
    
    this.terminal.nextLine();
    
    // Yes button
    const yesSelected = this.currentValue;
    const yesStyle = yesSelected ? 
      (dangerMode ? this.theme.error : this.theme.success) : 
      this.theme.muted;
    const yesBg = yesSelected ? 
      (dangerMode ? this.theme.error : this.theme.success) : 
      this.theme.background;
    
    if (yesSelected) {
      this.terminal.bgColor(yesBg);
      this.terminal.color(this.theme.background, ` ${yesLabel} `);
      this.terminal.bgDefaultColor();
    } else {
      this.terminal.color(yesStyle, `[${yesLabel}]`);
    }
    
    this.terminal('  ');
    
    // No button
    const noSelected = !this.currentValue;
    const noStyle = noSelected ? this.theme.primary : this.theme.muted;
    const noBg = noSelected ? this.theme.primary : this.theme.background;
    
    if (noSelected) {
      this.terminal.bgColor(noBg);
      this.terminal.color(this.theme.background, ` ${noLabel} `);
      this.terminal.bgDefaultColor();
    } else {
      this.terminal.color(noStyle, `[${noLabel}]`);
    }
    
    // Instructions
    this.terminal.nextLine();
    this.terminal.color(this.theme.muted, 'Use arrow keys or Tab to switch, Enter to confirm, Esc to cancel');
  }

  /**
   * Render inline Y/N options
   */
  private renderInline(): void {
    const { yesLabel, noLabel } = this.options;
    
    this.terminal('(');
    
    // Yes option
    if (this.currentValue) {
      this.terminal.color(this.theme.success, yesLabel?.charAt(0).toUpperCase());
    } else {
      this.terminal.color(this.theme.muted, yesLabel?.charAt(0).toLowerCase());
    }
    
    this.terminal.color(this.theme.muted, '/');
    
    // No option
    if (!this.currentValue) {
      this.terminal.color(this.theme.primary, noLabel?.charAt(0).toUpperCase());
    } else {
      this.terminal.color(this.theme.muted, noLabel?.charAt(0).toLowerCase());
    }
    
    this.terminal(')');
    
    // Show current selection
    this.terminal(' ');
    const selectedLabel = this.currentValue ? yesLabel : noLabel;
    const selectedColor = this.currentValue ? 
      (this.options.dangerMode ? this.theme.error : this.theme.success) : 
      this.theme.primary;
    
    this.terminal.color(selectedColor, `[${selectedLabel}]`);
  }

  /**
   * Start confirmation session
   */
  public async confirm(): Promise<boolean> {
    return new Promise((resolve, reject) => {
      this.isActive = true;
      this.render();
      
      const cleanup = () => {
        this.isActive = false;
        this.terminal.removeAllListeners('key');
      };

      this.terminal.on('key', (name: string, matches: any, data: any) => {
        try {
          const result = this.handleKeyPress(name, matches, data);
          
          if (result === 'submit') {
            cleanup();
            this.options.onSubmit?.(this.currentValue);
            resolve(this.currentValue);
          } else if (result === 'cancel') {
            cleanup();
            this.options.onCancel?.();
            resolve(false);
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
          reject(new Error('Confirmation cancelled'));
        }
      });
    });
  }

  /**
   * Handle key press events
   */
  private handleKeyPress(name: string, matches: any, data: any): string | null {
    const { yesLabel, noLabel } = this.options;

    switch (name) {
      case 'ENTER':
        return 'submit';

      case 'ESCAPE':
        return 'cancel';

      case 'LEFT':
      case 'RIGHT':
      case 'TAB':
        this.toggle();
        break;

      case 'y':
      case 'Y':
        this.setValue(true);
        break;

      case 'n':
      case 'N':
        this.setValue(false);
        break;

      default:
        // Handle first letter shortcuts
        if (data && data.isCharacter) {
          const char = String.fromCharCode(data.codepoint).toLowerCase();
          const yesChar = yesLabel?.charAt(0).toLowerCase();
          const noChar = noLabel?.charAt(0).toLowerCase();
          
          if (char === yesChar) {
            this.setValue(true);
          } else if (char === noChar) {
            this.setValue(false);
          }
        }
        break;
    }

    this.render();
    return null;
  }

  /**
   * Toggle current value
   */
  private toggle(): void {
    this.setValue(!this.currentValue);
  }

  /**
   * Set value and trigger events
   */
  private setValue(value: boolean): void {
    if (this.currentValue !== value) {
      this.currentValue = value;
      this.options.onChange?.(value);
    }
  }

  /**
   * Get current value
   */
  public getValue(): boolean {
    return this.currentValue;
  }

  /**
   * Set value programmatically
   */
  public setConfirmValue(value: boolean): void {
    this.setValue(value);
    this.render();
  }

  /**
   * Update message
   */
  public setMessage(message: string): void {
    this.options.message = message;
    this.render();
  }

  /**
   * Enable/disable danger mode
   */
  public setDangerMode(dangerMode: boolean): void {
    this.options.dangerMode = dangerMode;
    this.render();
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
}

// Factory function for easier usage
export function createConfirmInput(
  terminal: terminalKit.Terminal,
  options: ConfirmInputOptions
): ConfirmInput {
  return new ConfirmInput(terminal, options);
}

// Convenience functions for common confirmation patterns
export async function confirmAction(
  terminal: terminalKit.Terminal,
  message: string,
  dangerMode: boolean = false
): Promise<boolean> {
  const confirm = new ConfirmInput(terminal, {
    message,
    dangerMode,
    defaultValue: !dangerMode
  });
  
  return confirm.confirm();
}

export async function confirmDelete(
  terminal: terminalKit.Terminal,
  itemName: string
): Promise<boolean> {
  return confirmAction(
    terminal,
    `Are you sure you want to delete "${itemName}"? This action cannot be undone.`,
    true
  );
}

export async function confirmContinue(
  terminal: terminalKit.Terminal,
  message: string
): Promise<boolean> {
  return confirmAction(
    terminal,
    `${message} Do you want to continue?`,
    false
  );
}