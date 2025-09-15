/**
 * Divider Component - Visual separators for organizing content
 */

import * as terminalKit from 'terminal-kit';
import { ComponentProps, Theme } from '../../types';
import { defaultTheme } from '../../themes/default';

export interface DividerOptions extends ComponentProps {
  text?: string;
  width?: number;
  style?: 'solid' | 'dashed' | 'dotted' | 'double' | 'thick' | 'gradient';
  orientation?: 'horizontal' | 'vertical';
  align?: 'left' | 'center' | 'right';
  character?: string;
  color?: string;
  textColor?: string;
  margin?: number | { top?: number; bottom?: number; left?: number; right?: number };
  padding?: number | { top?: number; bottom?: number; left?: number; right?: number };
  animated?: boolean;
  gradient?: boolean;
}

interface NormalizedSpacing {
  top: number;
  right: number;
  bottom: number;
  left: number;
}

export class Divider {
  private terminal: terminalKit.Terminal;
  private options: DividerOptions;
  private theme: Theme;
  private animationFrame?: NodeJS.Timeout;
  private animationOffset: number = 0;

  private readonly styleChars = {
    solid: '─',
    dashed: '┈',
    dotted: '┄',
    double: '═',
    thick: '━',
    gradient: '▬'
  };

  private readonly verticalStyleChars = {
    solid: '│',
    dashed: '┊',
    dotted: '┆',
    double: '║',
    thick: '┃',
    gradient: '▬'
  };

  private readonly gradientChars = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█'];

  constructor(terminal: terminalKit.Terminal, options: DividerOptions = {}) {
    this.terminal = terminal;
    this.options = {
      width: terminal.width - 2,
      style: 'solid',
      orientation: 'horizontal',
      align: 'center',
      color: 'border',
      textColor: 'foreground',
      margin: { top: 0, bottom: 0, left: 0, right: 0 },
      padding: { top: 0, bottom: 0, left: 0, right: 0 },
      animated: false,
      gradient: false,
      ...options
    };
    this.theme = { ...defaultTheme, ...options.theme };
    
    if (this.options.animated) {
      this.startAnimation();
    }
  }

  /**
   * Render the divider
   */
  public render(): void {
    const { orientation } = this.options;
    
    if (orientation === 'vertical') {
      this.renderVertical();
    } else {
      this.renderHorizontal();
    }
  }

  /**
   * Render horizontal divider
   */
  private renderHorizontal(): void {
    const margin = this.normalizeSpacing(this.options.margin || 0);
    const padding = this.normalizeSpacing(this.options.padding || 0);
    
    // Apply top margin
    this.applyVerticalSpacing(margin.top);
    
    // Apply top padding
    this.applyVerticalSpacing(padding.top);
    
    // Render the divider line
    this.renderHorizontalLine();
    
    // Apply bottom padding
    this.applyVerticalSpacing(padding.bottom);
    
    // Apply bottom margin
    this.applyVerticalSpacing(margin.bottom);
  }

  /**
   * Render vertical divider
   */
  private renderVertical(): void {
    const margin = this.normalizeSpacing(this.options.margin || 0);
    const padding = this.normalizeSpacing(this.options.padding || 0);
    const { width = 1 } = this.options;
    
    // Calculate height - for vertical dividers, width option represents height
    const height = width;
    
    // Apply left margin
    if (margin.left > 0) {
      this.terminal(' '.repeat(margin.left));
    }
    
    // Apply left padding
    if (padding.left > 0) {
      this.terminal(' '.repeat(padding.left));
    }
    
    // Render vertical lines
    const startX = this.terminal.x;
    const startY = this.terminal.y;
    
    for (let i = 0; i < height; i++) {
      this.terminal.moveTo(startX, startY + i);
      this.renderVerticalChar(i);
    }
    
    // Move cursor to end position
    this.terminal.moveTo(startX + 1 + padding.right + margin.right, startY);
  }

  /**
   * Render horizontal divider line
   */
  private renderHorizontalLine(): void {
    const { text, width, align } = this.options;
    const margin = this.normalizeSpacing(this.options.margin || 0);
    
    // Apply left margin
    if (margin.left > 0) {
      this.terminal(' '.repeat(margin.left));
    }
    
    if (text) {
      this.renderDividerWithText();
    } else {
      this.renderPlainDivider();
    }
    
    this.terminal.nextLine();
  }

  /**
   * Render divider with text label
   */
  private renderDividerWithText(): void {
    const { text, width, align, textColor } = this.options;
    const textLength = text!.length;
    const availableWidth = width! - textLength - 2; // -2 for spaces around text
    
    if (availableWidth <= 0) {
      // Not enough space for text, just render plain divider
      this.renderPlainDivider();
      return;
    }
    
    let leftWidth: number, rightWidth: number;
    
    switch (align) {
      case 'left':
        leftWidth = 2;
        rightWidth = availableWidth - leftWidth;
        break;
      case 'right':
        rightWidth = 2;
        leftWidth = availableWidth - rightWidth;
        break;
      default: // center
        leftWidth = Math.floor(availableWidth / 2);
        rightWidth = availableWidth - leftWidth;
    }
    
    // Left part
    this.renderDividerChars(leftWidth);
    
    // Text with padding
    this.terminal(' ');
    this.terminal.color(this.theme[textColor! as keyof Theme] || textColor!, text!);
    this.terminal(' ');
    
    // Right part
    this.renderDividerChars(rightWidth);
  }

  /**
   * Render plain divider without text
   */
  private renderPlainDivider(): void {
    const { width } = this.options;
    this.renderDividerChars(width!);
  }

  /**
   * Render divider characters
   */
  private renderDividerChars(length: number): void {
    const { style, gradient, animated, color } = this.options;
    const dividerColor = this.theme[color! as keyof Theme] || color!;
    
    if (gradient && style === 'gradient') {
      this.renderGradientChars(length);
    } else if (animated) {
      this.renderAnimatedChars(length);
    } else {
      const char = this.options.character || this.styleChars[style!];
      this.terminal.color(dividerColor, char.repeat(length));
    }
  }

  /**
   * Render gradient effect
   */
  private renderGradientChars(length: number): void {
    const { color } = this.options;
    const baseColor = this.theme[color! as keyof Theme] || color!;
    
    for (let i = 0; i < length; i++) {
      const intensity = Math.floor((i / length) * (this.gradientChars.length - 1));
      const char = this.gradientChars[intensity];
      this.terminal.color(baseColor, char);
    }
  }

  /**
   * Render animated characters
   */
  private renderAnimatedChars(length: number): void {
    const { style, color } = this.options;
    const dividerColor = this.theme[color! as keyof Theme] || color!;
    const chars = this.getAnimationChars(style!);
    
    for (let i = 0; i < length; i++) {
      const charIndex = (i + this.animationOffset) % chars.length;
      this.terminal.color(dividerColor, chars[charIndex]);
    }
  }

  /**
   * Render vertical character
   */
  private renderVerticalChar(index: number): void {
    const { style, animated, color } = this.options;
    const dividerColor = this.theme[color! as keyof Theme] || color!;
    
    if (animated) {
      const chars = this.getAnimationChars(style!);
      const charIndex = (index + this.animationOffset) % chars.length;
      this.terminal.color(dividerColor, chars[charIndex]);
    } else {
      const char = this.verticalStyleChars[style!];
      this.terminal.color(dividerColor, char);
    }
  }

  /**
   * Get animation characters for style
   */
  private getAnimationChars(style: string): string[] {
    switch (style) {
      case 'dashed':
        return ['┈', '┉', '┈', ' '];
      case 'dotted':
        return ['┄', '┅', '┄', ' '];
      case 'gradient':
        return this.gradientChars;
      default:
        return [this.styleChars[style], ' '];
    }
  }

  /**
   * Apply vertical spacing (margins/padding)
   */
  private applyVerticalSpacing(spacing: number): void {
    for (let i = 0; i < spacing; i++) {
      this.terminal.nextLine();
    }
  }

  /**
   * Start animation
   */
  private startAnimation(): void {
    this.animationFrame = setInterval(() => {
      this.animationOffset = (this.animationOffset + 1) % 8;
      this.render();
    }, 200);
  }

  /**
   * Stop animation
   */
  private stopAnimation(): void {
    if (this.animationFrame) {
      clearInterval(this.animationFrame);
      this.animationFrame = undefined;
    }
  }

  /**
   * Normalize spacing values
   */
  private normalizeSpacing(
    spacing: number | { top?: number; bottom?: number; left?: number; right?: number }
  ): NormalizedSpacing {
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
   * Set divider text
   */
  public setText(text: string): Divider {
    this.options.text = text;
    return this;
  }

  /**
   * Set divider width
   */
  public setWidth(width: number): Divider {
    this.options.width = width;
    return this;
  }

  /**
   * Set divider style
   */
  public setStyle(style: DividerOptions['style']): Divider {
    this.options.style = style;
    return this;
  }

  /**
   * Set divider color
   */
  public setColor(color: string): Divider {
    this.options.color = color;
    return this;
  }

  /**
   * Enable/disable animation
   */
  public setAnimated(animated: boolean): Divider {
    const wasAnimated = this.options.animated;
    this.options.animated = animated;
    
    if (animated && !wasAnimated) {
      this.startAnimation();
    } else if (!animated && wasAnimated) {
      this.stopAnimation();
    }
    
    return this;
  }

  /**
   * Destroy divider and cleanup
   */
  public destroy(): void {
    this.stopAnimation();
  }
}

// Factory function for easier usage
export function createDivider(
  terminal: terminalKit.Terminal,
  options: DividerOptions = {}
): Divider {
  return new Divider(terminal, options);
}

// Convenience functions for common divider types
export function createHorizontalDivider(
  terminal: terminalKit.Terminal,
  text?: string,
  options: Partial<DividerOptions> = {}
): Divider {
  return new Divider(terminal, {
    text,
    orientation: 'horizontal',
    style: 'solid',
    ...options
  });
}

export function createVerticalDivider(
  terminal: terminalKit.Terminal,
  height: number = 5,
  options: Partial<DividerOptions> = {}
): Divider {
  return new Divider(terminal, {
    width: height, // For vertical dividers, width represents height
    orientation: 'vertical',
    style: 'solid',
    ...options
  });
}

export function createSectionDivider(
  terminal: terminalKit.Terminal,
  sectionName: string,
  options: Partial<DividerOptions> = {}
): Divider {
  return new Divider(terminal, {
    text: `─── ${sectionName} ───`,
    style: 'solid',
    align: 'center',
    color: 'primary',
    margin: { top: 1, bottom: 1 },
    ...options
  });
}

export function createAnimatedDivider(
  terminal: terminalKit.Terminal,
  text?: string,
  options: Partial<DividerOptions> = {}
): Divider {
  return new Divider(terminal, {
    text,
    style: 'gradient',
    animated: true,
    gradient: true,
    color: 'primary',
    ...options
  });
}

export function createThickDivider(
  terminal: terminalKit.Terminal,
  options: Partial<DividerOptions> = {}
): Divider {
  return new Divider(terminal, {
    style: 'thick',
    color: 'accent',
    margin: { top: 1, bottom: 1 },
    ...options
  });
}