/**
 * MultiSelect Component - Multiple selection with checkboxes
 */

import * as terminalKit from 'terminal-kit';
import { ComponentProps, SelectOption, Theme } from '../../types';
import { defaultTheme } from '../../themes/default';

export interface MultiSelectOptions<T = any> extends ComponentProps {
  options: SelectOption<T>[];
  values?: T[];
  placeholder?: string;
  searchable?: boolean;
  maxVisible?: number;
  minSelection?: number;
  maxSelection?: number;
  selectAll?: boolean;
  onChange?: (values: T[], options: SelectOption<T>[]) => void;
  onSubmit?: (values: T[], options: SelectOption<T>[]) => void;
  onCancel?: () => void;
}

export class MultiSelect<T = any> {
  private terminal: terminalKit.Terminal;
  private options: MultiSelectOptions<T>;
  private theme: Theme;
  private filteredOptions: SelectOption<T>[];
  private selectedValues: Set<T> = new Set();
  private currentIndex: number = 0;
  private scrollOffset: number = 0;
  private isOpen: boolean = false;
  private isActive: boolean = false;
  private searchTerm: string = '';

  constructor(terminal: terminalKit.Terminal, options: MultiSelectOptions<T>) {
    this.terminal = terminal;
    this.options = { ...options };
    this.theme = { ...defaultTheme, ...options.theme };
    this.filteredOptions = [...options.options];
    
    // Initialize selected values
    if (options.values) {
      this.selectedValues = new Set(options.values);
    }
  }

  /**
   * Render the multi-select component
   */
  public render(): void {
    if (!this.isOpen) {
      this.renderClosed();
    } else {
      this.renderOpen();
    }
  }

  /**
   * Render closed state (showing selected count)
   */
  private renderClosed(): void {
    const { placeholder = 'Select options...' } = this.options;
    const selectedCount = this.selectedValues.size;
    
    // Clear line
    this.terminal.eraseLine();
    
    // Draw border
    const borderColor = this.isActive ? this.theme.primary : this.theme.border;
    this.terminal.color(borderColor, '[');
    
    // Show selected count or placeholder
    if (selectedCount > 0) {
      this.terminal.color(this.theme.foreground, `${selectedCount} selected`);
      
      // Show first few selected items
      if (selectedCount <= 3) {
        const selectedOptions = this.getSelectedOptions();
        const labels = selectedOptions.map(opt => opt.label).join(', ');
        this.terminal.color(this.theme.muted, `: ${labels}`);
      }
    } else {
      this.terminal.color(this.theme.muted, placeholder);
    }
    
    this.terminal.color(borderColor, ']');
    
    // Show dropdown indicator
    this.terminal.color(this.theme.muted, ' ▼');
  }

  /**
   * Render open state (showing options list with checkboxes)
   */
  private renderOpen(): void {
    const { maxVisible = 10, searchable, selectAll } = this.options;
    
    // Clear area
    this.terminal.eraseDisplayBelow();
    
    // Show search if enabled
    if (searchable) {
      this.renderSearch();
      this.terminal.nextLine();
    }
    
    // Show select all option
    if (selectAll) {
      this.renderSelectAllOption();
      this.terminal.nextLine();
    }
    
    // Calculate visible range
    const visibleCount = Math.min(maxVisible, this.filteredOptions.length);
    const startIndex = this.scrollOffset;
    const endIndex = startIndex + visibleCount;
    
    // Render options
    for (let i = startIndex; i < endIndex; i++) {
      const option = this.filteredOptions[i];
      const isCurrentItem = i === this.currentIndex;
      const isSelected = this.selectedValues.has(option.value);
      const isDisabled = option.disabled || false;
      
      this.renderOption(option, isCurrentItem, isSelected, isDisabled);
      
      if (i < endIndex - 1) {
        this.terminal.nextLine();
      }
    }
    
    // Show scroll indicators
    if (this.filteredOptions.length > maxVisible) {
      this.renderScrollIndicators();
    }
    
    // Show instructions
    this.terminal.nextLine(2);
    this.terminal.color(this.theme.muted, 'Space: toggle • Enter: confirm • Esc: cancel');
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
   * Render select all option
   */
  private renderSelectAllOption(): void {
    const allSelected = this.filteredOptions.every(opt => 
      this.selectedValues.has(opt.value) || opt.disabled
    );
    const someSelected = this.filteredOptions.some(opt => 
      this.selectedValues.has(opt.value)
    );
    
    let checkbox = '☐'; // Empty
    if (allSelected) {
      checkbox = '☑'; // Checked
    } else if (someSelected) {
      checkbox = '☒'; // Indeterminate
    }
    
    this.terminal.color(this.theme.accent, `${checkbox} `);
    this.terminal.color(this.theme.foreground, 'Select All');
  }

  /**
   * Render individual option with checkbox
   */
  private renderOption(
    option: SelectOption<T>, 
    isCurrent: boolean, 
    isSelected: boolean, 
    isDisabled: boolean
  ): void {
    // Current item indicator
    if (isCurrent) {
      this.terminal.color(this.theme.primary, '▶ ');
    } else {
      this.terminal('  ');
    }
    
    // Checkbox
    let checkbox = isSelected ? '☑' : '☐';
    let checkboxColor = isSelected ? this.theme.success : this.theme.muted;
    
    if (isDisabled) {
      checkbox = '☒';
      checkboxColor = this.theme.muted;
    }
    
    this.terminal.color(checkboxColor, `${checkbox} `);
    
    // Option content
    let textColor = this.theme.foreground;
    if (isDisabled) {
      textColor = this.theme.muted;
    } else if (isCurrent) {
      textColor = this.theme.primary;
    } else if (isSelected) {
      textColor = this.theme.success;
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
    
    // Background for current item
    if (isCurrent && !isDisabled) {
      // Visual highlighting for current item
      this.terminal.left(option.label.length + (option.icon ? 2 : 0) + 2);
      this.terminal.bgColor(this.theme.primary);
      this.terminal.color(this.theme.background, `${checkbox} ${option.label}`);
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
   * Start multi-selection session
   */
  public async select(): Promise<T[]> {
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
            cleanup();
            const values = Array.from(this.selectedValues);
            const options = this.getSelectedOptions();
            this.options.onSubmit?.(values, options);
            resolve(values);
          } else if (result === 'cancel') {
            cleanup();
            this.options.onCancel?.();
            resolve([]);
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
          reject(new Error('Multi-selection cancelled'));
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
        if (this.validateSelection()) {
          return 'submit';
        } else {
          this.showValidationError();
        }
        break;

      case 'ESCAPE':
        return 'cancel';

      case 'SPACE':
        this.toggleCurrentOption();
        break;

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
        this.currentIndex = 0;
        this.updateScrollOffset();
        break;

      case 'END':
        this.currentIndex = this.filteredOptions.length - 1;
        this.updateScrollOffset();
        break;

      case 'CTRL_A':
        this.selectAllOptions();
        break;

      case 'CTRL_D':
        this.deselectAllOptions();
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
   * Toggle selection of current option
   */
  private toggleCurrentOption(): void {
    const currentOption = this.filteredOptions[this.currentIndex];
    if (!currentOption || currentOption.disabled) return;

    if (this.selectedValues.has(currentOption.value)) {
      this.selectedValues.delete(currentOption.value);
    } else {
      // Check max selection limit
      const { maxSelection } = this.options;
      if (maxSelection && this.selectedValues.size >= maxSelection) {
        this.showMaxSelectionError();
        return;
      }
      
      this.selectedValues.add(currentOption.value);
    }

    // Trigger change event
    const values = Array.from(this.selectedValues);
    const options = this.getSelectedOptions();
    this.options.onChange?.(values, options);
  }

  /**
   * Select all available options
   */
  private selectAllOptions(): void {
    const { maxSelection } = this.options;
    
    for (const option of this.filteredOptions) {
      if (!option.disabled) {
        if (maxSelection && this.selectedValues.size >= maxSelection) break;
        this.selectedValues.add(option.value);
      }
    }
    
    this.triggerChange();
  }

  /**
   * Deselect all options
   */
  private deselectAllOptions(): void {
    this.selectedValues.clear();
    this.triggerChange();
  }

  /**
   * Move selection up or down
   */
  private moveSelection(delta: number): void {
    const newIndex = Math.max(0, Math.min(this.filteredOptions.length - 1, this.currentIndex + delta));
    
    // Skip disabled options
    let targetIndex = newIndex;
    const direction = delta > 0 ? 1 : -1;
    
    while (targetIndex >= 0 && targetIndex < this.filteredOptions.length) {
      if (!this.filteredOptions[targetIndex].disabled) {
        this.currentIndex = targetIndex;
        break;
      }
      targetIndex += direction;
    }
    
    this.updateScrollOffset();
  }

  /**
   * Update scroll offset based on current selection
   */
  private updateScrollOffset(): void {
    const { maxVisible = 10 } = this.options;
    
    if (this.currentIndex < this.scrollOffset) {
      this.scrollOffset = this.currentIndex;
    } else if (this.currentIndex >= this.scrollOffset + maxVisible) {
      this.scrollOffset = this.currentIndex - maxVisible + 1;
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
    this.currentIndex = 0;
    this.scrollOffset = 0;
  }

  /**
   * Validate current selection against constraints
   */
  private validateSelection(): boolean {
    const { minSelection, maxSelection } = this.options;
    const count = this.selectedValues.size;
    
    if (minSelection && count < minSelection) return false;
    if (maxSelection && count > maxSelection) return false;
    
    return true;
  }

  /**
   * Show validation error
   */
  private showValidationError(): void {
    const { minSelection, maxSelection } = this.options;
    const count = this.selectedValues.size;
    
    this.terminal.nextLine();
    
    if (minSelection && count < minSelection) {
      this.terminal.color(this.theme.error, `⚠ Please select at least ${minSelection} option(s)`);
    } else if (maxSelection && count > maxSelection) {
      this.terminal.color(this.theme.error, `⚠ Please select no more than ${maxSelection} option(s)`);
    }
    
    setTimeout(() => this.render(), 2000);
  }

  /**
   * Show max selection error
   */
  private showMaxSelectionError(): void {
    const { maxSelection } = this.options;
    this.terminal.nextLine();
    this.terminal.color(this.theme.error, `⚠ Maximum ${maxSelection} selections allowed`);
    setTimeout(() => this.render(), 1500);
  }

  /**
   * Get currently selected options
   */
  private getSelectedOptions(): SelectOption<T>[] {
    return this.options.options.filter(option => this.selectedValues.has(option.value));
  }

  /**
   * Trigger change event
   */
  private triggerChange(): void {
    const values = Array.from(this.selectedValues);
    const options = this.getSelectedOptions();
    this.options.onChange?.(values, options);
  }

  /**
   * Set values programmatically
   */
  public setValues(values: T[]): void {
    this.selectedValues = new Set(values);
    this.triggerChange();
    this.render();
  }

  /**
   * Get current values
   */
  public getValues(): T[] {
    return Array.from(this.selectedValues);
  }

  /**
   * Update options
   */
  public setOptions(options: SelectOption<T>[]): void {
    this.options.options = options;
    this.filteredOptions = [...options];
    this.currentIndex = 0;
    this.scrollOffset = 0;
    
    // Remove selected values that are no longer available
    const availableValues = new Set(options.map(opt => opt.value));
    this.selectedValues = new Set(
      Array.from(this.selectedValues).filter(value => availableValues.has(value))
    );
    
    this.render();
  }
}

// Factory function for easier usage
export function createMultiSelect<T = any>(
  terminal: terminalKit.Terminal,
  options: MultiSelectOptions<T>
): MultiSelect<T> {
  return new MultiSelect(terminal, options);
}