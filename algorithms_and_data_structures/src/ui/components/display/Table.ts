/**
 * Table Component - Data table with sorting and filtering
 */

import * as terminalKit from 'terminal-kit';
import { ComponentProps, TableColumn, TableData, Theme } from '../../types';
import { defaultTheme } from '../../themes/default';

export interface TableOptions<T = any> extends ComponentProps {
  data: TableData<T>;
  sortable?: boolean;
  filterable?: boolean;
  selectable?: boolean;
  multiSelect?: boolean;
  pageSize?: number;
  showHeader?: boolean;
  showFooter?: boolean;
  minColumnWidth?: number;
  maxColumnWidth?: number;
  borderStyle?: 'single' | 'double' | 'rounded' | 'none';
  onSort?: (column: keyof T, direction: 'asc' | 'desc') => void;
  onFilter?: (filters: Record<string, string>) => void;
  onSelect?: (rows: T[], indices: number[]) => void;
  onRowClick?: (row: T, index: number) => void;
}

interface SortState<T> {
  column: keyof T | null;
  direction: 'asc' | 'desc';
}

interface FilterState {
  [key: string]: string;
}

export class Table<T = any> {
  private terminal: terminalKit.Terminal;
  private options: TableOptions<T>;
  private theme: Theme;
  private sortState: SortState<T> = { column: null, direction: 'asc' };
  private filterState: FilterState = {};
  private selectedRows: Set<number> = new Set();
  private currentPage: number = 0;
  private currentRow: number = 0;
  private isActive: boolean = false;
  private filteredData: T[] = [];
  private sortedData: T[] = [];

  constructor(terminal: terminalKit.Terminal, options: TableOptions<T>) {
    this.terminal = terminal;
    this.options = {
      sortable: true,
      filterable: false,
      selectable: false,
      multiSelect: false,
      pageSize: 10,
      showHeader: true,
      showFooter: true,
      minColumnWidth: 8,
      maxColumnWidth: 40,
      borderStyle: 'single',
      ...options
    };
    this.theme = { ...defaultTheme, ...options.theme };
    
    this.processData();
  }

  /**
   * Render the table
   */
  public render(): void {
    // Clear area
    this.terminal.eraseDisplayBelow();
    
    const { showHeader, showFooter } = this.options;
    
    // Render filter row if enabled
    if (this.options.filterable) {
      this.renderFilterRow();
    }
    
    // Render header
    if (showHeader) {
      this.renderHeader();
      this.renderHeaderSeparator();
    }
    
    // Render data rows
    this.renderRows();
    
    // Render footer separator
    if (showFooter) {
      this.renderFooterSeparator();
      this.renderFooter();
    }
  }

  /**
   * Render filter row
   */
  private renderFilterRow(): void {
    const { data } = this.options;
    const columnWidths = this.calculateColumnWidths();
    
    this.renderRowBorder('top');
    
    // Filter inputs
    this.terminal('│');
    data.columns.forEach((column, index) => {
      const width = columnWidths[index];
      const filter = this.filterState[column.key as string] || '';
      const padding = Math.max(0, width - filter.length - 2);
      
      this.terminal.color(this.theme.muted, ` ${filter}`);
      this.terminal(' '.repeat(padding));
      
      if (index < data.columns.length - 1) {
        this.terminal('│');
      }
    });
    this.terminal('│');
    this.terminal.nextLine();
  }

  /**
   * Render table header
   */
  private renderHeader(): void {
    const { data, sortable } = this.options;
    const columnWidths = this.calculateColumnWidths();
    
    this.renderRowBorder('top');
    
    // Header content
    this.terminal('│');
    data.columns.forEach((column, index) => {
      const width = columnWidths[index];
      let headerText = column.label;
      
      // Add sort indicator
      if (sortable && this.sortState.column === column.key) {
        const indicator = this.sortState.direction === 'asc' ? '↑' : '↓';
        headerText += ` ${indicator}`;
      }
      
      // Apply alignment and padding
      const alignedText = this.alignText(headerText, width, column.align || 'left');
      
      this.terminal.color(this.theme.primary, alignedText);
      
      if (index < data.columns.length - 1) {
        this.terminal('│');
      }
    });
    this.terminal('│');
    this.terminal.nextLine();
  }

  /**
   * Render header separator
   */
  private renderHeaderSeparator(): void {
    this.renderRowBorder('middle');
  }

  /**
   * Render footer separator
   */
  private renderFooterSeparator(): void {
    this.renderRowBorder('bottom');
  }

  /**
   * Render table rows
   */
  private renderRows(): void {
    const { pageSize } = this.options;
    const startIndex = this.currentPage * pageSize!;
    const endIndex = Math.min(startIndex + pageSize!, this.sortedData.length);
    const columnWidths = this.calculateColumnWidths();
    
    for (let i = startIndex; i < endIndex; i++) {
      const row = this.sortedData[i];
      const isSelected = this.selectedRows.has(i);
      const isCurrentRow = this.isActive && i === this.currentRow;
      
      this.renderRow(row, i, isSelected, isCurrentRow, columnWidths);
      
      if (i < endIndex - 1) {
        this.terminal.nextLine();
      }
    }
  }

  /**
   * Render individual row
   */
  private renderRow(
    row: T, 
    rowIndex: number, 
    isSelected: boolean, 
    isCurrentRow: boolean, 
    columnWidths: number[]
  ): void {
    const { data, selectable } = this.options;
    
    // Row start
    this.terminal('│');
    
    // Selection indicator
    if (selectable) {
      const indicator = isSelected ? '☑' : '☐';
      const color = isSelected ? this.theme.success : this.theme.muted;
      this.terminal.color(color, indicator + ' ');
    }
    
    // Row data
    data.columns.forEach((column, columnIndex) => {
      const width = columnWidths[columnIndex];
      let cellValue = row[column.key];
      
      // Apply custom render function
      if (column.render) {
        cellValue = column.render(cellValue, row, rowIndex);
      } else {
        cellValue = String(cellValue || '');
      }
      
      // Apply alignment and padding
      const alignedText = this.alignText(cellValue, width, column.align || 'left');
      
      // Apply styling
      let textColor = this.theme.foreground;
      if (isCurrentRow) {
        textColor = this.theme.primary;
      } else if (isSelected) {
        textColor = this.theme.success;
      }
      
      if (isCurrentRow) {
        this.terminal.bgColor(this.theme.primary);
        this.terminal.color(this.theme.background, alignedText);
        this.terminal.bgDefaultColor();
      } else {
        this.terminal.color(textColor, alignedText);
      }
      
      if (columnIndex < data.columns.length - 1) {
        this.terminal('│');
      }
    });
    
    // Row end
    this.terminal('│');
  }

  /**
   * Render footer with pagination and info
   */
  private renderFooter(): void {
    const { pageSize } = this.options;
    const totalRows = this.sortedData.length;
    const totalPages = Math.ceil(totalRows / pageSize!);
    const startRow = this.currentPage * pageSize! + 1;
    const endRow = Math.min(startRow + pageSize! - 1, totalRows);
    
    // Pagination info
    const paginationInfo = `Page ${this.currentPage + 1} of ${totalPages} | Rows ${startRow}-${endRow} of ${totalRows}`;
    
    // Selection info
    let selectionInfo = '';
    if (this.options.selectable && this.selectedRows.size > 0) {
      selectionInfo = ` | ${this.selectedRows.size} selected`;
    }
    
    const footerText = paginationInfo + selectionInfo;
    
    this.terminal.color(this.theme.muted, footerText);
    this.terminal.nextLine();
    
    // Navigation help
    if (this.isActive) {
      this.terminal.color(this.theme.muted, 'Arrow keys: navigate • Space: select • Enter: confirm • S: sort • F: filter');
    }
  }

  /**
   * Render row borders
   */
  private renderRowBorder(position: 'top' | 'middle' | 'bottom'): void {
    const { borderStyle } = this.options;
    const columnWidths = this.calculateColumnWidths();
    
    if (borderStyle === 'none') return;
    
    let leftChar: string, rightChar: string, middleChar: string, horizontalChar: string;
    
    switch (borderStyle) {
      case 'double':
        horizontalChar = '═';
        if (position === 'top') {
          leftChar = '╔'; rightChar = '╗'; middleChar = '╦';
        } else if (position === 'middle') {
          leftChar = '╠'; rightChar = '╣'; middleChar = '╬';
        } else {
          leftChar = '╚'; rightChar = '╝'; middleChar = '╩';
        }
        break;
      case 'rounded':
        horizontalChar = '─';
        if (position === 'top') {
          leftChar = '╭'; rightChar = '╮'; middleChar = '┬';
        } else if (position === 'middle') {
          leftChar = '├'; rightChar = '┤'; middleChar = '┼';
        } else {
          leftChar = '╰'; rightChar = '╯'; middleChar = '┴';
        }
        break;
      default: // single
        horizontalChar = '─';
        if (position === 'top') {
          leftChar = '┌'; rightChar = '┐'; middleChar = '┬';
        } else if (position === 'middle') {
          leftChar = '├'; rightChar = '┤'; middleChar = '┼';
        } else {
          leftChar = '└'; rightChar = '┘'; middleChar = '┴';
        }
    }
    
    this.terminal.color(this.theme.border, leftChar);
    
    columnWidths.forEach((width, index) => {
      this.terminal.color(this.theme.border, horizontalChar.repeat(width + 2));
      if (index < columnWidths.length - 1) {
        this.terminal.color(this.theme.border, middleChar);
      }
    });
    
    this.terminal.color(this.theme.border, rightChar);
    this.terminal.nextLine();
  }

  /**
   * Calculate column widths based on content and constraints
   */
  private calculateColumnWidths(): number[] {
    const { data, minColumnWidth, maxColumnWidth } = this.options;
    const terminalWidth = this.terminal.width - 4; // Account for borders and padding
    const columnWidths: number[] = [];
    
    // Calculate ideal widths
    data.columns.forEach((column, index) => {
      let maxWidth = column.label.length;
      
      // Check data rows for max content width
      this.sortedData.forEach(row => {
        let cellValue = row[column.key];
        if (column.render) {
          cellValue = column.render(cellValue, row, index);
        }
        const cellLength = String(cellValue || '').length;
        maxWidth = Math.max(maxWidth, cellLength);
      });
      
      // Apply constraints
      if (column.width) {
        columnWidths.push(column.width);
      } else {
        const constrainedWidth = Math.max(
          minColumnWidth!,
          Math.min(maxColumnWidth!, maxWidth)
        );
        columnWidths.push(constrainedWidth);
      }
    });
    
    // Adjust if total width exceeds terminal width
    const totalWidth = columnWidths.reduce((sum, width) => sum + width, 0);
    if (totalWidth > terminalWidth) {
      const scaleFactor = terminalWidth / totalWidth;
      columnWidths.forEach((width, index) => {
        columnWidths[index] = Math.floor(width * scaleFactor);
      });
    }
    
    return columnWidths;
  }

  /**
   * Align text within specified width
   */
  private alignText(text: string, width: number, align: 'left' | 'center' | 'right'): string {
    if (text.length >= width) {
      return text.slice(0, width - 3) + '...';
    }
    
    const padding = width - text.length;
    
    switch (align) {
      case 'center':
        const leftPad = Math.floor(padding / 2);
        const rightPad = padding - leftPad;
        return ' '.repeat(leftPad) + text + ' '.repeat(rightPad);
      case 'right':
        return ' '.repeat(padding) + text;
      default: // left
        return text + ' '.repeat(padding);
    }
  }

  /**
   * Process data (filter, sort, paginate)
   */
  private processData(): void {
    // Apply filters
    this.filteredData = this.applyFilters(this.options.data.rows);
    
    // Apply sorting
    this.sortedData = this.applySorting(this.filteredData);
    
    // Reset current row if out of bounds
    if (this.currentRow >= this.sortedData.length) {
      this.currentRow = Math.max(0, this.sortedData.length - 1);
    }
  }

  /**
   * Apply filters to data
   */
  private applyFilters(data: T[]): T[] {
    if (Object.keys(this.filterState).length === 0) {
      return data;
    }
    
    return data.filter(row => {
      return Object.entries(this.filterState).every(([key, filter]) => {
        if (!filter) return true;
        
        const cellValue = String(row[key as keyof T] || '').toLowerCase();
        const filterValue = filter.toLowerCase();
        
        return cellValue.includes(filterValue);
      });
    });
  }

  /**
   * Apply sorting to data
   */
  private applySorting(data: T[]): T[] {
    if (!this.sortState.column) {
      return data;
    }
    
    return [...data].sort((a, b) => {
      const aValue = a[this.sortState.column!];
      const bValue = b[this.sortState.column!];
      
      let comparison = 0;
      if (aValue < bValue) comparison = -1;
      else if (aValue > bValue) comparison = 1;
      
      return this.sortState.direction === 'desc' ? -comparison : comparison;
    });
  }

  /**
   * Start interactive table session
   */
  public async interact(): Promise<void> {
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
            resolve();
          }
        } catch (error) {
          cleanup();
          reject(error);
        }
      });

      this.terminal.on('key', (name: string) => {
        if (name === 'CTRL_C') {
          cleanup();
          reject(new Error('Table interaction cancelled'));
        }
      });
    });
  }

  /**
   * Handle key press events
   */
  private handleKeyPress(name: string, matches: any, data: any): boolean {
    const { pageSize, selectable, multiSelect } = this.options;

    switch (name) {
      case 'ENTER':
        if (selectable && this.selectedRows.size > 0) {
          const selectedData = Array.from(this.selectedRows).map(i => this.sortedData[i]);
          this.options.onSelect?.(selectedData, Array.from(this.selectedRows));
        } else if (this.currentRow < this.sortedData.length) {
          this.options.onRowClick?.(this.sortedData[this.currentRow], this.currentRow);
        }
        return true;

      case 'ESCAPE':
        return true;

      case 'UP':
        if (this.currentRow > 0) {
          this.currentRow--;
          this.updatePageForCurrentRow();
        }
        break;

      case 'DOWN':
        if (this.currentRow < this.sortedData.length - 1) {
          this.currentRow++;
          this.updatePageForCurrentRow();
        }
        break;

      case 'PAGE_UP':
        this.currentPage = Math.max(0, this.currentPage - 1);
        this.currentRow = this.currentPage * pageSize!;
        break;

      case 'PAGE_DOWN':
        const totalPages = Math.ceil(this.sortedData.length / pageSize!);
        this.currentPage = Math.min(totalPages - 1, this.currentPage + 1);
        this.currentRow = this.currentPage * pageSize!;
        break;

      case 'HOME':
        this.currentRow = 0;
        this.currentPage = 0;
        break;

      case 'END':
        this.currentRow = this.sortedData.length - 1;
        this.currentPage = Math.floor(this.currentRow / pageSize!);
        break;

      case 'SPACE':
        if (selectable) {
          this.toggleRowSelection(this.currentRow);
        }
        break;

      default:
        // Handle alphabetic shortcuts
        if (data && data.isCharacter) {
          const char = String.fromCharCode(data.codepoint).toLowerCase();
          
          if (char === 's' && this.options.sortable) {
            this.showSortDialog();
          } else if (char === 'f' && this.options.filterable) {
            this.showFilterDialog();
          }
        }
        break;
    }

    this.render();
    return false;
  }

  /**
   * Toggle row selection
   */
  private toggleRowSelection(rowIndex: number): void {
    const { multiSelect } = this.options;
    
    if (this.selectedRows.has(rowIndex)) {
      this.selectedRows.delete(rowIndex);
    } else {
      if (!multiSelect) {
        this.selectedRows.clear();
      }
      this.selectedRows.add(rowIndex);
    }
  }

  /**
   * Update current page based on current row
   */
  private updatePageForCurrentRow(): void {
    const { pageSize } = this.options;
    this.currentPage = Math.floor(this.currentRow / pageSize!);
  }

  /**
   * Show sort dialog (simplified implementation)
   */
  private showSortDialog(): void {
    // This would typically open a dialog to select sort column and direction
    // For now, cycle through columns
    const { data } = this.options;
    const sortableColumns = data.columns.filter(col => col.sortable !== false);
    
    if (sortableColumns.length === 0) return;
    
    let nextColumnIndex = 0;
    if (this.sortState.column) {
      const currentIndex = sortableColumns.findIndex(col => col.key === this.sortState.column);
      if (currentIndex >= 0) {
        if (this.sortState.direction === 'asc') {
          this.sortState.direction = 'desc';
          return;
        } else {
          nextColumnIndex = (currentIndex + 1) % sortableColumns.length;
        }
      }
    }
    
    this.sortState.column = sortableColumns[nextColumnIndex].key;
    this.sortState.direction = 'asc';
    
    this.processData();
    this.options.onSort?.(this.sortState.column, this.sortState.direction);
  }

  /**
   * Show filter dialog (simplified implementation)
   */
  private showFilterDialog(): void {
    // This would typically open a dialog to set filters
    // For now, this is a placeholder
    this.terminal.nextLine();
    this.terminal.color(this.theme.info, 'Filter dialog would open here');
    setTimeout(() => this.render(), 1000);
  }

  /**
   * Update table data
   */
  public setData(data: TableData<T>): void {
    this.options.data = data;
    this.currentRow = 0;
    this.currentPage = 0;
    this.selectedRows.clear();
    this.processData();
    this.render();
  }

  /**
   * Get selected rows
   */
  public getSelectedRows(): T[] {
    return Array.from(this.selectedRows).map(index => this.sortedData[index]);
  }

  /**
   * Set filter values
   */
  public setFilters(filters: FilterState): void {
    this.filterState = { ...filters };
    this.processData();
    this.options.onFilter?.(this.filterState);
    this.render();
  }

  /**
   * Set sort state
   */
  public setSort(column: keyof T, direction: 'asc' | 'desc'): void {
    this.sortState = { column, direction };
    this.processData();
    this.options.onSort?.(column, direction);
    this.render();
  }
}

// Factory function for easier usage
export function createTable<T = any>(
  terminal: terminalKit.Terminal,
  options: TableOptions<T>
): Table<T> {
  return new Table(terminal, options);
}