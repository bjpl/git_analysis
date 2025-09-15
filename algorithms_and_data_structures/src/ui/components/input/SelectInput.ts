/**
 * SelectInput Component - Selection from list with arrow navigation
 */

import * as terminalKit from 'terminal-kit';
import { ComponentProps, SelectOption, Theme } from '../../types';
import { defaultTheme } from '../../themes/default';

export interface SelectInputOptions<T = any> extends ComponentProps {
  options: SelectOption<T>[];
  value?: T;
  placeholder?: string;
  searchable?: boolean;
  maxVisible?: number;
  allowEmpty?: boolean;
  onChange?: (value: T, option: SelectOption<T>) => void;
  onSubmit?: (value: T, option: SelectOption<T>) => void;
  onCancel?: () => void;
}

export class SelectInput<T = any> {
  private terminal: terminalKit.Terminal;
  private options: SelectInputOptions<T>;
  private theme: Theme;
  private filteredOptions: SelectOption<T>[];
  private selectedIndex: number = 0;
  private scrollOffset: number = 0;
  private isOpen: boolean = false;
  private isActive: boolean = false;
  private searchTerm: string = '';

  constructor(terminal: terminalKit.Terminal, options: SelectInputOptions<T>) {
    this.terminal = terminal;
    this.options = { ...options };
    this.theme = { ...defaultTheme, ...options.theme };
    this.filteredOptions = [...options.options];
    
    // Find initial selected index
    if (options.value !== undefined) {
      const index = this.options.options.findIndex(opt => opt.value === options.value);
      if (index >= 0) {
        this.selectedIndex = index;
      }
    }
  }

  /**
   * Render the select component
   */
  public render(): void {
    if (!this.isOpen) {
      this.renderClosed();
    } else {
      this.renderOpen();
    }
  }

  /**
   * Render closed state (showing selected value)
   */
  private renderClosed(): void {
    const { placeholder = 'Select an option...' } = this.options;
    const selectedOption = this.getSelectedOption();
    
    // Clear line
    this.terminal.eraseLine();
    
    // Draw border
    const borderColor = this.isActive ? this.theme.primary : this.theme.border;
    this.terminal.color(borderColor, '[');
    
    // Show selected value or placeholder
    if (selectedOption) {
      this.terminal.color(this.theme.foreground, selectedOption.label);
      if (selectedOption.icon) {
        this.terminal.color(this.theme.accent, ` ${selectedOption.icon}`);
      }
    } else {
      this.terminal.color(this.theme.muted, placeholder);
    }
    
    this.terminal.color(borderColor, ']');
    
    // Show dropdown indicator
    this.terminal.color(this.theme.muted, ' ▼');
  }

  /**
   * Render open state (showing options list)
   */
  private renderOpen(): void {
    const { maxVisible = 10, searchable } = this.options;
    
    // Clear area
    this.terminal.eraseDisplayBelow();
    
    // Show search if enabled
    if (searchable) {
      this.renderSearch();
      this.terminal.nextLine();
    }
    
    // Calculate visible range
    const visibleCount = Math.min(maxVisible, this.filteredOptions.length);
    const startIndex = this.scrollOffset;
    const endIndex = startIndex + visibleCount;
    
    // Render options
    for (let i = startIndex; i < endIndex; i++) {
      const option = this.filteredOptions[i];
      const isSelected = i === this.selectedIndex;
      const isDisabled = option.disabled || false;
      
      this.renderOption(option, isSelected, isDisabled);
      
      if (i < endIndex - 1) {
        this.terminal.nextLine();
      }
    }
    
    // Show scroll indicators
    if (this.filteredOptions.length > maxVisible) {
      this.renderScrollIndicators();
    }
  }

  /**
   * Render search input
   */
  private renderSearch(): void {
    this.terminal.color(this.theme.muted, 'Search: ');
    this.terminal.color(this.theme.foreground, this.searchTerm);
    this.terminal.color(this.theme.primary, '|'); // Cursor
  }

  /**
   * Render individual option
   */
  private renderOption(option: SelectOption<T>, isSelected: boolean, isDisabled: boolean): void {
    // Selection indicator
    if (isSelected) {
      this.terminal.color(this.theme.primary, '▶ ');
    } else {
      this.terminal('  ');
    }
    
    // Option content
    let textColor = this.theme.foreground;
    if (isDisabled) {
      textColor = this.theme.muted;
    } else if (isSelected) {
      textColor = this.theme.primary;
    }
    
    // Icon
    if (option.icon) {
      this.terminal.color(this.theme.accent, `${option.icon} `);
    }
    
    // Label
    this.terminal.color(textColor, option.label);
    
    // Description
    if (option.description) {
      this.terminal.color(this.theme.muted, ` - ${option.description}`);
    }
    
    // Background for selected
    if (isSelected && !isDisabled) {
      // Move back and apply background (terminal-kit specific styling)
      this.terminal.left(option.label.length + (option.icon ? 2 : 0));
      this.terminal.bgColor(this.theme.primary);
      this.terminal.color(this.theme.background, option.label);
      this.terminal.bgDefaultColor();
    }
  }

  /**
   * Render scroll indicators
   */
  private renderScrollIndicators(): void {
    const { maxVisible = 10 } = this.options;
    
    this.terminal.nextLine();
    
    // Up indicator
    if (this.scrollOffset > 0) {
      this.terminal.color(this.theme.muted, '  ↑ More options above');
      this.terminal.nextLine();
    }
    
    // Down indicator
    if (this.scrollOffset + maxVisible < this.filteredOptions.length) {
      this.terminal.color(this.theme.muted, '  ↓ More options below');
    }
  }

  /**
   * Start selection session
   */
  public async select(): Promise<T | null> {
    return new Promise((resolve, reject) => {
      this.isActive = true;
      this.isOpen = true;
      this.render();
      
      const cleanup = () => {
        this.isActive = false;
        this.isOpen = false;
        this.terminal.removeAllListeners('key');
      };

      this.terminal.on('key', (name: string, matches: any, data: any) => {
        try {
          const result = this.handleKeyPress(name, matches, data);
          
          if (result === 'submit') {
            const selectedOption = this.getSelectedOption();
            cleanup();
            
            if (selectedOption) {
              this.options.onSubmit?.(selectedOption.value, selectedOption);
              resolve(selectedOption.value);
            } else if (this.options.allowEmpty) {
              resolve(null);
            }
          } else if (result === 'cancel') {
            cleanup();
            this.options.onCancel?.();
            resolve(null);
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
          reject(new Error('Selection cancelled'));
        }
      });
    });
  }

  /**
   * Handle key press events
   */
  private handleKeyPress(name: string, matches: any, data: any): string | null {
    const { searchable, maxVisible = 10 } = this.options;

    switch (name) {
      case 'ENTER':
        const selectedOption = this.getSelectedOption();
        if (selectedOption && !selectedOption.disabled) {
          return 'submit';
        }
        break;

      case 'ESCAPE':
        return 'cancel';

      case 'UP':
        this.moveSelection(-1);
        break;

      case 'DOWN':
        this.moveSelection(1);
        break;

      case 'PAGE_UP':
        this.moveSelection(-maxVisible);
        break;

      case 'PAGE_DOWN':
        this.moveSelection(maxVisible);
        break;

      case 'HOME':
        this.selectedIndex = 0;
        this.updateScrollOffset();
        break;

      case 'END':
        this.selectedIndex = this.filteredOptions.length - 1;
        this.updateScrollOffset();
        break;

      case 'BACKSPACE':
        if (searchable && this.searchTerm.length > 0) {
          this.searchTerm = this.searchTerm.slice(0, -1);
          this.filterOptions();
        }
        break;

      default:
        // Handle search input
        if (searchable && data && data.isCharacter) {
          const char = String.fromCharCode(data.codepoint);
          this.searchTerm += char;
          this.filterOptions();
        }
        break;
    }

    this.render();
    return null;
  }

  /**
   * Move selection up or down
   */
  private moveSelection(delta: number): void {
    const newIndex = Math.max(0, Math.min(this.filteredOptions.length - 1, this.selectedIndex + delta));
    
    // Skip disabled options
    let targetIndex = newIndex;
    const direction = delta > 0 ? 1 : -1;
    
    while (targetIndex >= 0 && targetIndex < this.filteredOptions.length) {
      if (!this.filteredOptions[targetIndex].disabled) {
        this.selectedIndex = targetIndex;
        break;
      }
      targetIndex += direction;
    }
    
    this.updateScrollOffset();
    
    // Trigger change event
    const selectedOption = this.getSelectedOption();
    if (selectedOption) {
      this.options.onChange?.(selectedOption.value, selectedOption);
    }
  }

  /**
   * Update scroll offset based on current selection
   */
  private updateScrollOffset(): void {
    const { maxVisible = 10 } = this.options;
    
    if (this.selectedIndex < this.scrollOffset) {
      this.scrollOffset = this.selectedIndex;
    } else if (this.selectedIndex >= this.scrollOffset + maxVisible) {
      this.scrollOffset = this.selectedIndex - maxVisible + 1;
    }
  }

  /**
   * Filter options based on search term
   */
  private filterOptions(): void {
    if (!this.searchTerm) {
      this.filteredOptions = [...this.options.options];
    } else {
      const searchLower = this.searchTerm.toLowerCase();
      this.filteredOptions = this.options.options.filter(option =>
        option.label.toLowerCase().includes(searchLower) ||
        option.description?.toLowerCase().includes(searchLower)
      );
    }
    
    // Reset selection
    this.selectedIndex = 0;
    this.scrollOffset = 0;
  }

  /**
   * Get currently selected option
   */
  private getSelectedOption(): SelectOption<T> | null {
    return this.filteredOptions[this.selectedIndex] || null;
  }

  /**
   * Set value programmatically
   */
  public setValue(value: T): void {
    const index = this.options.options.findIndex(opt => opt.value === value);
    if (index >= 0) {
      this.selectedIndex = index;
      this.updateScrollOffset();
      this.render();
    }
  }

  /**
   * Get current value
   */
  public getValue(): T | null {
    const selectedOption = this.getSelectedOption();
    return selectedOption ? selectedOption.value : null;
  }

  /**
   * Update options
   */
  public setOptions(options: SelectOption<T>[]): void {
    this.options.options = options;
    this.filteredOptions = [...options];
    this.selectedIndex = 0;
    this.scrollOffset = 0;
    this.render();
  }
}

// Factory function for easier usage
export function createSelectInput<T = any>(
  terminal: terminalKit.Terminal,
  options: SelectInputOptions<T>
): SelectInput<T> {
  return new SelectInput(terminal, options);
}