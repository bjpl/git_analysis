/**
 * Box Component - Container with borders and padding
 */

import * as terminalKit from 'terminal-kit';
import { ComponentProps, Theme, Position, Size } from '../../types';
import { defaultTheme } from '../../themes/default';

export interface BoxOptions extends ComponentProps {
  title?: string;
  content?: string;
  width?: number;
  height?: number;
  padding?: number | { top?: number; right?: number; bottom?: number; left?: number };
  margin?: number | { top?: number; right?: number; bottom?: number; left?: number };
  borderStyle?: 'single' | 'double' | 'rounded' | 'thick' | 'dotted' | 'none';
  borderColor?: string;
  backgroundColor?: string;
  titleAlign?: 'left' | 'center' | 'right';
  contentAlign?: 'left' | 'center' | 'right';
  scrollable?: boolean;
  focusable?: boolean;
  shadow?: boolean;
  onFocus?: () => void;
  onBlur?: () => void;
  onResize?: (size: Size) => void;
}

interface NormalizedSpacing {
  top: number;
  right: number;
  bottom: number;
  left: number;
}

export class Box {
  private terminal: terminalKit.Terminal;
  private options: BoxOptions;
  private theme: Theme;
  private isFocused: boolean = false;
  private contentLines: string[] = [];
  private scrollOffset: number = 0;

  private readonly borderChars = {
    single: {
      topLeft: '┌', topRight: '┐', bottomLeft: '└', bottomRight: '┘',
      horizontal: '─', vertical: '│',
      topJoin: '┬', bottomJoin: '┴', leftJoin: '├', rightJoin: '┤'
    },
    double: {
      topLeft: '╔', topRight: '╗', bottomLeft: '╚', bottomRight: '╝',
      horizontal: '═', vertical: '║',
      topJoin: '╦', bottomJoin: '╩', leftJoin: '╠', rightJoin: '╣'
    },
    rounded: {
      topLeft: '╭', topRight: '╮', bottomLeft: '╰', bottomRight: '╯',
      horizontal: '─', vertical: '│',
      topJoin: '┬', bottomJoin: '┴', leftJoin: '├', rightJoin: '┤'
    },
    thick: {
      topLeft: '┏', topRight: '┓', bottomLeft: '┗', bottomRight: '┛',
      horizontal: '━', vertical: '┃',
      topJoin: '┳', bottomJoin: '┻', leftJoin: '┣', rightJoin: '┫'
    },
    dotted: {
      topLeft: '┌', topRight: '┐', bottomLeft: '└', bottomRight: '┘',
      horizontal: '┈', vertical: '┊',
      topJoin: '┬', bottomJoin: '┴', leftJoin: '├', rightJoin: '┤'
    }
  };

  constructor(terminal: terminalKit.Terminal, options: BoxOptions) {
    this.terminal = terminal;
    this.options = {
      width: 40,
      height: 10,
      padding: 1,
      margin: 0,
      borderStyle: 'single',
      titleAlign: 'left',
      contentAlign: 'left',
      scrollable: false,
      focusable: false,
      shadow: false,
      ...options
    };
    this.theme = { ...defaultTheme, ...options.theme };
    
    this.processContent();
  }

  /**
   * Render the box
   */
  public render(): void {
    const { position } = this.options;
    const margin = this.normalizeSpacing(this.options.margin || 0);
    
    // Save cursor position
    this.terminal.saveCursor();
    
    // Apply position if specified
    if (position) {
      this.terminal.moveTo(
        (position.x || 0) + margin.left + 1, 
        (position.y || 0) + margin.top + 1
      );
    }
    
    // Render shadow first
    if (this.options.shadow) {
      this.renderShadow();
    }
    
    // Render box
    this.renderBox();
    
    // Restore cursor position
    this.terminal.restoreCursor();
  }

  /**
   * Render shadow effect
   */
  private renderShadow(): void {
    const { width, height } = this.options;
    const shadowColor = this.theme.muted;
    
    // Shadow is offset by 1 right and 1 down
    for (let y = 1; y <= height!; y++) {
      this.terminal.moveTo(this.terminal.x + width! + 1, this.terminal.y + y);
      this.terminal.color(shadowColor, '█');
    }
    
    // Bottom shadow
    this.terminal.moveTo(this.terminal.x + 1, this.terminal.y + height! + 1);
    this.terminal.color(shadowColor, '█'.repeat(width! + 1));
  }

  /**
   * Render the main box
   */
  private renderBox(): void {
    const { width, height, borderStyle, title } = this.options;
    
    if (borderStyle === 'none') {
      this.renderBorderlessBox();
      return;
    }
    
    const chars = this.borderChars[borderStyle!];
    const borderColor = this.getBorderColor();
    
    // Top border with title
    this.renderTopBorder(chars, borderColor);
    
    // Content area
    for (let row = 1; row < height! - 1; row++) {
      this.renderContentRow(row - 1, chars, borderColor);
    }
    
    // Bottom border
    this.renderBottomBorder(chars, borderColor);
  }

  /**
   * Render borderless box (content only)
   */
  private renderBorderlessBox(): void {
    const { width, height } = this.options;
    const padding = this.normalizeSpacing(this.options.padding || 0);
    const contentWidth = width! - padding.left - padding.right;
    const contentHeight = height! - padding.top - padding.bottom;
    
    // Apply background color
    if (this.options.backgroundColor) {
      this.terminal.bgColor(this.options.backgroundColor);
    }
    
    for (let row = 0; row < height!; row++) {
      if (row >= padding.top && row < height! - padding.bottom) {
        const contentRow = row - padding.top;
        this.renderContentLine(contentRow, contentWidth, padding.left);
      } else {
        // Padding rows
        this.terminal(' '.repeat(width!));
      }
      
      if (row < height! - 1) {
        this.terminal.nextLine();
        this.terminal.column(this.terminal.x);
      }
    }
    
    if (this.options.backgroundColor) {
      this.terminal.bgDefaultColor();
    }
  }

  /**
   * Render top border with optional title
   */
  private renderTopBorder(chars: any, borderColor: string): void {
    const { width, title, titleAlign } = this.options;
    
    this.terminal.color(borderColor, chars.topLeft);
    
    if (title) {
      const titleSpace = width! - 2; // Account for corners
      const renderedTitle = this.renderTitle(title, titleSpace, titleAlign!);
      
      // Calculate title positioning
      let leftPadding = 0;
      let rightPadding = 0;
      const titleLength = renderedTitle.length + 2; // +2 for spaces around title
      
      if (titleAlign === 'center') {
        leftPadding = Math.floor((titleSpace - titleLength) / 2);
        rightPadding = titleSpace - titleLength - leftPadding;
      } else if (titleAlign === 'right') {
        leftPadding = titleSpace - titleLength;
      } else {
        rightPadding = titleSpace - titleLength;
      }
      
      this.terminal.color(borderColor, chars.horizontal.repeat(Math.max(0, leftPadding)));
      if (titleLength <= titleSpace) {
        this.terminal.color(borderColor, ' ');
        this.terminal.color(this.theme.primary, renderedTitle);
        this.terminal.color(borderColor, ' ');
      }
      this.terminal.color(borderColor, chars.horizontal.repeat(Math.max(0, rightPadding)));
    } else {
      this.terminal.color(borderColor, chars.horizontal.repeat(width! - 2));
    }
    
    this.terminal.color(borderColor, chars.topRight);
    this.terminal.nextLine();
  }

  /**
   * Render bottom border
   */
  private renderBottomBorder(chars: any, borderColor: string): void {
    const { width } = this.options;
    
    this.terminal.color(borderColor, chars.bottomLeft);
    this.terminal.color(borderColor, chars.horizontal.repeat(width! - 2));
    this.terminal.color(borderColor, chars.bottomRight);
  }

  /**
   * Render content row
   */
  private renderContentRow(contentRow: number, chars: any, borderColor: string): void {
    const { width } = this.options;
    const padding = this.normalizeSpacing(this.options.padding || 0);
    const contentWidth = width! - 2 - padding.left - padding.right; // -2 for borders
    
    this.terminal.color(borderColor, chars.vertical);
    
    // Apply background color
    if (this.options.backgroundColor) {
      this.terminal.bgColor(this.options.backgroundColor);
    }
    
    if (contentRow < padding.top || contentRow >= this.contentLines.length + padding.top) {
      // Padding or empty row
      this.terminal(' '.repeat(width! - 2));
    } else {
      // Content row
      const lineIndex = contentRow - padding.top + this.scrollOffset;
      this.renderContentLine(lineIndex, contentWidth, padding.left);
    }
    
    if (this.options.backgroundColor) {
      this.terminal.bgDefaultColor();
    }
    
    this.terminal.color(borderColor, chars.vertical);
    this.terminal.nextLine();
  }

  /**
   * Render content line
   */
  private renderContentLine(lineIndex: number, contentWidth: number, leftPadding: number): void {
    const { contentAlign } = this.options;
    
    // Left padding
    this.terminal(' '.repeat(leftPadding));
    
    // Content
    let line = '';
    if (lineIndex >= 0 && lineIndex < this.contentLines.length) {
      line = this.contentLines[lineIndex];
    }
    
    // Apply alignment
    const alignedLine = this.alignText(line, contentWidth, contentAlign!);
    this.terminal.color(this.theme.foreground, alignedLine);
    
    // Right padding to fill remaining width
    const totalUsed = leftPadding + alignedLine.length;
    const rightPadding = Math.max(0, contentWidth + leftPadding - totalUsed);
    this.terminal(' '.repeat(rightPadding));
  }

  /**
   * Render title with proper truncation
   */
  private renderTitle(title: string, maxWidth: number, align: string): string {
    if (title.length > maxWidth - 2) {
      return title.slice(0, maxWidth - 5) + '...';
    }
    return title;
  }

  /**
   * Align text within specified width
   */
  private alignText(text: string, width: number, align: string): string {
    if (text.length >= width) {
      return text.slice(0, width);
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
   * Get border color based on focus state
   */
  private getBorderColor(): string {
    if (this.options.borderColor) {
      return this.options.borderColor;
    }
    
    return this.isFocused ? this.theme.primary : this.theme.border;
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
   * Process content into lines
   */
  private processContent(): void {
    const { content, width } = this.options;
    
    if (!content) {
      this.contentLines = [];
      return;
    }
    
    const padding = this.normalizeSpacing(this.options.padding || 0);
    const contentWidth = width! - 2 - padding.left - padding.right; // Account for borders and padding
    
    // Split content by newlines and wrap long lines
    const paragraphs = content.split('\n');
    this.contentLines = [];
    
    paragraphs.forEach(paragraph => {
      if (paragraph.length <= contentWidth) {
        this.contentLines.push(paragraph);
      } else {
        // Word wrap
        const words = paragraph.split(' ');
        let currentLine = '';
        
        words.forEach(word => {
          if (currentLine.length + word.length + 1 <= contentWidth) {
            currentLine += (currentLine ? ' ' : '') + word;
          } else {
            if (currentLine) this.contentLines.push(currentLine);
            currentLine = word;
          }
        });
        
        if (currentLine) this.contentLines.push(currentLine);
      }
    });
  }

  /**
   * Set content
   */
  public setContent(content: string): Box {
    this.options.content = content;
    this.processContent();
    return this;
  }

  /**
   * Set title
   */
  public setTitle(title: string): Box {
    this.options.title = title;
    return this;
  }

  /**
   * Resize box
   */
  public resize(width: number, height: number): Box {
    const oldSize = { width: this.options.width!, height: this.options.height! };
    this.options.width = width;
    this.options.height = height;
    
    this.processContent(); // Reprocess content for new width
    
    this.options.onResize?.({ width, height });
    return this;
  }

  /**
   * Scroll content
   */
  public scroll(delta: number): Box {
    if (!this.options.scrollable) return this;
    
    const maxScroll = Math.max(0, this.contentLines.length - this.getContentHeight());
    this.scrollOffset = Math.max(0, Math.min(maxScroll, this.scrollOffset + delta));
    
    return this;
  }

  /**
   * Focus the box
   */
  public focus(): Box {
    if (!this.options.focusable) return this;
    
    this.isFocused = true;
    this.options.onFocus?.();
    return this;
  }

  /**
   * Blur the box
   */
  public blur(): Box {
    this.isFocused = false;
    this.options.onBlur?.();
    return this;
  }

  /**
   * Get content area height
   */
  private getContentHeight(): number {
    const padding = this.normalizeSpacing(this.options.padding || 0);
    return this.options.height! - 2 - padding.top - padding.bottom; // -2 for borders
  }

  /**
   * Get current size
   */
  public getSize(): Size {
    return { width: this.options.width!, height: this.options.height! };
  }

  /**
   * Get content lines count
   */
  public getContentLines(): number {
    return this.contentLines.length;
  }

  /**
   * Check if focused
   */
  public isFocusedState(): boolean {
    return this.isFocused;
  }

  /**
   * Check if scrollable content
   */
  public hasScrollableContent(): boolean {
    return this.options.scrollable && this.contentLines.length > this.getContentHeight();
  }
}

// Factory function for easier usage
export function createBox(
  terminal: terminalKit.Terminal,
  options: BoxOptions
): Box {
  return new Box(terminal, options);
}

// Convenience functions for common box types
export function createInfoBox(
  terminal: terminalKit.Terminal,
  title: string,
  content: string,
  options: Partial<BoxOptions> = {}
): Box {
  return new Box(terminal, {
    title,
    content,
    borderStyle: 'single',
    borderColor: 'info',
    ...options
  });
}

export function createWarningBox(
  terminal: terminalKit.Terminal,
  title: string,
  content: string,
  options: Partial<BoxOptions> = {}
): Box {
  return new Box(terminal, {
    title,
    content,
    borderStyle: 'double',
    borderColor: 'warning',
    ...options
  });
}

export function createErrorBox(
  terminal: terminalKit.Terminal,
  title: string,
  content: string,
  options: Partial<BoxOptions> = {}
): Box {
  return new Box(terminal, {
    title,
    content,
    borderStyle: 'thick',
    borderColor: 'error',
    ...options
  });
}