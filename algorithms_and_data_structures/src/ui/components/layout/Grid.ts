/**
 * Grid Component - Grid layout system for organizing components
 */

import * as terminalKit from 'terminal-kit';
import { ComponentProps, Theme, GridCell, GridRow } from '../../types';
import { defaultTheme } from '../../themes/default';

export interface GridOptions extends ComponentProps {
  columns: number;
  rows?: number;
  columnWidths?: (number | 'auto' | 'fr')[];
  rowHeights?: (number | 'auto')[];
  gap?: number | { row?: number; column?: number };
  padding?: number | { top?: number; right?: number; bottom?: number; left?: number };
  borderStyle?: 'single' | 'double' | 'rounded' | 'none';
  showHeaders?: boolean;
  showRowNumbers?: boolean;
  responsive?: boolean;
  minColumnWidth?: number;
  maxWidth?: number;
}

interface NormalizedSpacing {
  top: number;
  right: number;
  bottom: number;
  left: number;
}

interface NormalizedGap {
  row: number;
  column: number;
}

interface ColumnInfo {
  width: number;
  isFlexible: boolean;
}

export class Grid {
  private terminal: terminalKit.Terminal;
  private options: GridOptions;
  private theme: Theme;
  private cells: Map<string, GridCell> = new Map();
  private calculatedColumnWidths: number[] = [];
  private calculatedRowHeights: number[] = [];
  private totalWidth: number = 0;
  private totalHeight: number = 0;

  private readonly borderChars = {
    single: {
      topLeft: '┌', topRight: '┐', bottomLeft: '└', bottomRight: '┘',
      horizontal: '─', vertical: '│',
      cross: '┼', topJoin: '┬', bottomJoin: '┴', leftJoin: '├', rightJoin: '┤'
    },
    double: {
      topLeft: '╔', topRight: '╗', bottomLeft: '╚', bottomRight: '╝',
      horizontal: '═', vertical: '║',
      cross: '╬', topJoin: '╦', bottomJoin: '╩', leftJoin: '╠', rightJoin: '╣'
    },
    rounded: {
      topLeft: '╭', topRight: '╮', bottomLeft: '╰', bottomRight: '╯',
      horizontal: '─', vertical: '│',
      cross: '┼', topJoin: '┬', bottomJoin: '┴', leftJoin: '├', rightJoin: '┤'
    }
  };

  constructor(terminal: terminalKit.Terminal, options: GridOptions) {
    this.terminal = terminal;
    this.options = {
      rows: 3,
      gap: 1,
      padding: 0,
      borderStyle: 'single',
      showHeaders: false,
      showRowNumbers: false,
      responsive: true,
      minColumnWidth: 8,
      maxWidth: this.terminal.width - 4,
      ...options
    };
    this.theme = { ...defaultTheme, ...options.theme };
    
    this.calculateLayout();
  }

  /**
   * Render the grid
   */
  public render(): void {
    const { borderStyle, showHeaders, showRowNumbers } = this.options;
    const padding = this.normalizeSpacing(this.options.padding || 0);
    
    // Apply top padding
    if (padding.top > 0) {
      for (let i = 0; i < padding.top; i++) {
        this.terminal.nextLine();
      }
    }
    
    // Apply left padding for each row
    const leftPadding = ' '.repeat(padding.left);
    
    // Render headers if enabled
    if (showHeaders) {
      this.renderHeaders(leftPadding);
    }
    
    // Render top border
    if (borderStyle !== 'none') {
      this.renderTopBorder(leftPadding);
    }
    
    // Render content rows
    for (let row = 0; row < this.options.rows!; row++) {
      this.renderRow(row, leftPadding);
      
      // Render row separator (except for last row)
      if (row < this.options.rows! - 1 && borderStyle !== 'none') {
        this.renderRowSeparator(leftPadding);
      }
    }
    
    // Render bottom border
    if (borderStyle !== 'none') {
      this.renderBottomBorder(leftPadding);
    }
    
    // Apply bottom padding
    if (padding.bottom > 0) {
      for (let i = 0; i < padding.bottom; i++) {
        this.terminal.nextLine();
      }
    }
  }

  /**
   * Render column headers
   */
  private renderHeaders(leftPadding: string): void {
    this.terminal(leftPadding);
    
    if (this.options.showRowNumbers) {
      this.terminal(' '.repeat(4)); // Row number column space
    }
    
    for (let col = 0; col < this.options.columns; col++) {
      const width = this.calculatedColumnWidths[col];
      const header = String.fromCharCode(65 + col); // A, B, C, etc.
      
      this.terminal.color(this.theme.primary, this.centerText(header, width));
      
      if (col < this.options.columns - 1) {
        this.renderColumnGap();
      }
    }
    
    this.terminal.nextLine();
  }

  /**
   * Render top border
   */
  private renderTopBorder(leftPadding: string): void {
    const chars = this.borderChars[this.options.borderStyle!];
    const gap = this.normalizeGap(this.options.gap || 0);
    
    this.terminal(leftPadding);
    this.terminal.color(this.theme.border, chars.topLeft);
    
    for (let col = 0; col < this.options.columns; col++) {
      const width = this.calculatedColumnWidths[col];
      this.terminal.color(this.theme.border, chars.horizontal.repeat(width));
      
      if (col < this.options.columns - 1) {
        this.terminal.color(this.theme.border, chars.topJoin);
      }
    }
    
    this.terminal.color(this.theme.border, chars.topRight);
    this.terminal.nextLine();
  }

  /**
   * Render bottom border
   */
  private renderBottomBorder(leftPadding: string): void {
    const chars = this.borderChars[this.options.borderStyle!];
    
    this.terminal(leftPadding);
    this.terminal.color(this.theme.border, chars.bottomLeft);
    
    for (let col = 0; col < this.options.columns; col++) {
      const width = this.calculatedColumnWidths[col];
      this.terminal.color(this.theme.border, chars.horizontal.repeat(width));
      
      if (col < this.options.columns - 1) {
        this.terminal.color(this.theme.border, chars.bottomJoin);
      }
    }
    
    this.terminal.color(this.theme.border, chars.bottomRight);
    this.terminal.nextLine();
  }

  /**
   * Render row separator
   */
  private renderRowSeparator(leftPadding: string): void {
    const chars = this.borderChars[this.options.borderStyle!];
    
    this.terminal(leftPadding);
    this.terminal.color(this.theme.border, chars.leftJoin);
    
    for (let col = 0; col < this.options.columns; col++) {
      const width = this.calculatedColumnWidths[col];
      this.terminal.color(this.theme.border, chars.horizontal.repeat(width));
      
      if (col < this.options.columns - 1) {
        this.terminal.color(this.theme.border, chars.cross);
      }
    }
    
    this.terminal.color(this.theme.border, chars.rightJoin);
    this.terminal.nextLine();
  }

  /**
   * Render a single row
   */
  private renderRow(row: number, leftPadding: string): void {
    const { borderStyle, showRowNumbers } = this.options;
    const rowHeight = this.calculatedRowHeights[row] || 1;
    
    for (let line = 0; line < rowHeight; line++) {
      this.terminal(leftPadding);
      
      // Row number
      if (showRowNumbers && line === 0) {
        this.terminal.color(this.theme.muted, ` ${row + 1} `.padStart(4, ' '));
      } else if (showRowNumbers) {
        this.terminal(' '.repeat(4));
      }
      
      // Border
      if (borderStyle !== 'none') {
        this.terminal.color(this.theme.border, '│');
      }
      
      // Cells
      for (let col = 0; col < this.options.columns; col++) {
        this.renderCell(row, col, line);
        
        if (col < this.options.columns - 1) {
          if (borderStyle !== 'none') {
            this.terminal.color(this.theme.border, '│');
          } else {
            this.renderColumnGap();
          }
        }
      }
      
      // Right border
      if (borderStyle !== 'none') {
        this.terminal.color(this.theme.border, '│');
      }
      
      this.terminal.nextLine();
    }
  }

  /**
   * Render a single cell
   */
  private renderCell(row: number, col: number, line: number): void {
    const cellKey = `${row},${col}`;
    const cell = this.cells.get(cellKey);
    const width = this.calculatedColumnWidths[col];
    
    if (cell) {
      const lines = this.splitCellContent(cell.content, width);
      const cellLine = lines[line] || '';
      const span = cell.span || 1;
      
      // Calculate total width including spanned columns
      let totalWidth = width;
      for (let i = 1; i < span && col + i < this.options.columns; i++) {
        totalWidth += this.calculatedColumnWidths[col + i] + 1; // +1 for border
      }
      
      // Apply cell styling
      if (cell.style) {
        if (cell.style.backgroundColor) {
          this.terminal.bgColor(cell.style.backgroundColor);
        }
        if (cell.style.color) {
          this.terminal.color(cell.style.color, this.padText(cellLine, totalWidth));
        } else {
          this.terminal(this.padText(cellLine, totalWidth));
        }
        if (cell.style.backgroundColor) {
          this.terminal.bgDefaultColor();
        }
      } else {
        this.terminal.color(this.theme.foreground, this.padText(cellLine, totalWidth));
      }
    } else {
      // Empty cell
      this.terminal(' '.repeat(width));
    }
  }

  /**
   * Render column gap
   */
  private renderColumnGap(): void {
    const gap = this.normalizeGap(this.options.gap || 0);
    if (gap.column > 0) {
      this.terminal(' '.repeat(gap.column));
    }
  }

  /**
   * Calculate grid layout dimensions
   */
  private calculateLayout(): void {
    this.calculateColumnWidths();
    this.calculateRowHeights();
  }

  /**
   * Calculate column widths
   */
  private calculateColumnWidths(): void {
    const { columns, columnWidths, maxWidth, minColumnWidth, responsive } = this.options;
    const gap = this.normalizeGap(this.options.gap || 0);
    const padding = this.normalizeSpacing(this.options.padding || 0);
    
    // Available width for content
    const availableWidth = maxWidth! - padding.left - padding.right;
    const gapWidth = (columns - 1) * gap.column;
    const borderWidth = this.options.borderStyle !== 'none' ? columns + 1 : 0;
    const contentWidth = availableWidth - gapWidth - borderWidth;
    
    this.calculatedColumnWidths = [];
    
    if (columnWidths && columnWidths.length >= columns) {
      // Use specified widths
      let flexibleCount = 0;
      let fixedWidth = 0;
      
      // First pass: calculate fixed widths and count flexible columns
      for (let i = 0; i < columns; i++) {
        const width = columnWidths[i];
        if (typeof width === 'number') {
          this.calculatedColumnWidths[i] = width;
          fixedWidth += width;
        } else if (width === 'fr') {
          flexibleCount++;
        } else { // 'auto'
          this.calculatedColumnWidths[i] = minColumnWidth!;
          fixedWidth += minColumnWidth!;
        }
      }
      
      // Second pass: distribute remaining width to flexible columns
      const remainingWidth = Math.max(0, contentWidth - fixedWidth);
      const flexWidth = flexibleCount > 0 ? Math.floor(remainingWidth / flexibleCount) : 0;
      
      for (let i = 0; i < columns; i++) {
        if (columnWidths[i] === 'fr') {
          this.calculatedColumnWidths[i] = Math.max(minColumnWidth!, flexWidth);
        }
      }
    } else {
      // Equal width distribution
      const equalWidth = Math.max(minColumnWidth!, Math.floor(contentWidth / columns));
      this.calculatedColumnWidths = new Array(columns).fill(equalWidth);
    }
    
    // Responsive adjustment
    if (responsive) {
      const totalCalculated = this.calculatedColumnWidths.reduce((sum, w) => sum + w, 0);
      if (totalCalculated > contentWidth) {
        const scale = contentWidth / totalCalculated;
        this.calculatedColumnWidths = this.calculatedColumnWidths.map(w => 
          Math.max(minColumnWidth!, Math.floor(w * scale))
        );
      }
    }
    
    this.totalWidth = this.calculatedColumnWidths.reduce((sum, w) => sum + w, 0) + gapWidth + borderWidth;
  }

  /**
   * Calculate row heights
   */
  private calculateRowHeights(): void {
    const { rows, rowHeights } = this.options;
    
    if (rowHeights && rowHeights.length >= rows!) {
      this.calculatedRowHeights = rowHeights.map(h => typeof h === 'number' ? h : 1);
    } else {
      // Default height of 1 for all rows
      this.calculatedRowHeights = new Array(rows!).fill(1);
      
      // Calculate auto heights based on content
      for (const [key, cell] of this.cells) {
        const [row] = key.split(',').map(Number);
        const width = this.calculatedColumnWidths[row % this.options.columns];
        const lines = this.splitCellContent(cell.content, width);
        this.calculatedRowHeights[row] = Math.max(this.calculatedRowHeights[row], lines.length);
      }
    }
    
    this.totalHeight = this.calculatedRowHeights.reduce((sum, h) => sum + h, 0);
  }

  /**
   * Split cell content into lines that fit within width
   */
  private splitCellContent(content: string, width: number): string[] {
    if (!content) return [''];
    
    const lines: string[] = [];
    const paragraphs = content.split('\n');
    
    paragraphs.forEach(paragraph => {
      if (paragraph.length <= width) {
        lines.push(paragraph);
      } else {
        // Word wrap
        const words = paragraph.split(' ');
        let currentLine = '';
        
        words.forEach(word => {
          if (currentLine.length + word.length + 1 <= width) {
            currentLine += (currentLine ? ' ' : '') + word;
          } else {
            if (currentLine) lines.push(currentLine);
            currentLine = word.length > width ? word.slice(0, width) : word;
          }
        });
        
        if (currentLine) lines.push(currentLine);
      }
    });
    
    return lines.length > 0 ? lines : [''];
  }

  /**
   * Pad text to specified width
   */
  private padText(text: string, width: number): string {
    if (text.length >= width) {
      return text.slice(0, width);
    }
    return text + ' '.repeat(width - text.length);
  }

  /**
   * Center text within specified width
   */
  private centerText(text: string, width: number): string {
    if (text.length >= width) {
      return text.slice(0, width);
    }
    
    const padding = width - text.length;
    const leftPad = Math.floor(padding / 2);
    const rightPad = padding - leftPad;
    
    return ' '.repeat(leftPad) + text + ' '.repeat(rightPad);
  }

  /**
   * Normalize spacing values
   */
  private normalizeSpacing(spacing: number | { top?: number; right?: number; bottom?: number; left?: number }): NormalizedSpacing {
    if (typeof spacing === 'number') {
      return { top: spacing, right: spacing, bottom: spacing, left: spacing };
    }
    
    return {
      top: spacing.top || 0,
      right: spacing.right || 0,
      bottom: spacing.bottom || 0,
      left: spacing.left || 0
    };
  }

  /**
   * Normalize gap values
   */
  private normalizeGap(gap: number | { row?: number; column?: number }): NormalizedGap {
    if (typeof gap === 'number') {
      return { row: gap, column: gap };
    }
    
    return {
      row: gap.row || 0,
      column: gap.column || 0
    };
  }

  /**
   * Set cell content
   */
  public setCell(row: number, col: number, cell: GridCell): Grid {
    if (row >= 0 && row < this.options.rows! && col >= 0 && col < this.options.columns) {
      const key = `${row},${col}`;
      this.cells.set(key, cell);
      
      // Recalculate layout if content affects dimensions
      this.calculateLayout();
    }
    
    return this;
  }

  /**
   * Get cell content
   */
  public getCell(row: number, col: number): GridCell | undefined {
    const key = `${row},${col}`;
    return this.cells.get(key);
  }

  /**
   * Set multiple cells at once
   */
  public setCells(cells: { row: number; col: number; cell: GridCell }[]): Grid {
    cells.forEach(({ row, col, cell }) => {
      this.setCell(row, col, cell);
    });
    
    return this;
  }

  /**
   * Clear cell
   */
  public clearCell(row: number, col: number): Grid {
    const key = `${row},${col}`;
    this.cells.delete(key);
    return this;
  }

  /**
   * Clear all cells
   */
  public clearAll(): Grid {
    this.cells.clear();
    return this;
  }

  /**
   * Resize grid
   */
  public resize(columns: number, rows: number): Grid {
    this.options.columns = columns;
    this.options.rows = rows;
    
    // Remove cells that are now out of bounds
    for (const [key] of this.cells) {
      const [row, col] = key.split(',').map(Number);
      if (row >= rows || col >= columns) {
        this.cells.delete(key);
      }
    }
    
    this.calculateLayout();
    return this;
  }

  /**
   * Get grid dimensions
   */
  public getDimensions(): { columns: number; rows: number; width: number; height: number } {
    return {
      columns: this.options.columns,
      rows: this.options.rows!,
      width: this.totalWidth,
      height: this.totalHeight
    };
  }

  /**
   * Get calculated column widths
   */
  public getColumnWidths(): number[] {
    return [...this.calculatedColumnWidths];
  }

  /**
   * Get calculated row heights
   */
  public getRowHeights(): number[] {
    return [...this.calculatedRowHeights];
  }
}

// Factory function for easier usage
export function createGrid(
  terminal: terminalKit.Terminal,
  options: GridOptions
): Grid {
  return new Grid(terminal, options);
}

// Convenience functions for common grid layouts
export function createDataGrid(
  terminal: terminalKit.Terminal,
  data: string[][],
  headers?: string[],
  options: Partial<GridOptions> = {}
): Grid {
  const columns = data[0]?.length || 0;
  const rows = data.length + (headers ? 1 : 0);
  
  const grid = new Grid(terminal, {
    columns,
    rows,
    showHeaders: Boolean(headers),
    borderStyle: 'single',
    ...options
  });
  
  // Add headers if provided
  if (headers) {
    headers.forEach((header, col) => {
      grid.setCell(0, col, {
        content: header,
        style: { color: 'primary', bold: true }
      });
    });
  }
  
  // Add data
  const startRow = headers ? 1 : 0;
  data.forEach((row, rowIndex) => {
    row.forEach((cell, colIndex) => {
      grid.setCell(startRow + rowIndex, colIndex, { content: cell });
    });
  });
  
  return grid;
}

export function createFormGrid(
  terminal: terminalKit.Terminal,
  fields: { label: string; value: string }[],
  options: Partial<GridOptions> = {}
): Grid {
  const grid = new Grid(terminal, {
    columns: 2,
    rows: fields.length,
    columnWidths: ['auto', 'fr'],
    borderStyle: 'none',
    gap: { row: 0, column: 2 },
    ...options
  });
  
  fields.forEach((field, index) => {
    grid.setCell(index, 0, {
      content: field.label + ':',
      style: { color: 'muted' }
    });
    grid.setCell(index, 1, {
      content: field.value
    });
  });
  
  return grid;
}