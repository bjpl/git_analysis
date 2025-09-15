/**
 * Theme System Utilities
 * Helper functions for theme management and styling
 */

import { ThemeManager, ThemeDefinition } from './ThemeManager';
import { ColorScheme, ColorDefinition, TerminalCapabilities, detectTerminalCapabilities } from './ColorScheme';
import { StyleDefinitions, TextStyle, ComponentStyle, UIComponentStyles } from './StyleDefinitions';

/**
 * Color utility functions
 */
export class ColorUtils {
  /**
   * Convert RGB to hex
   */
  static rgbToHex(r: number, g: number, b: number): string {
    return '#' + [r, g, b].map(x => {
      const hex = x.toString(16);
      return hex.length === 1 ? '0' + hex : hex;
    }).join('');
  }

  /**
   * Convert hex to RGB
   */
  static hexToRgb(hex: string): { r: number; g: number; b: number } | null {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : null;
  }

  /**
   * Calculate color brightness (0-255)
   */
  static getBrightness(hex: string): number {
    const rgb = this.hexToRgb(hex);
    if (!rgb) return 0;
    return (rgb.r * 299 + rgb.g * 587 + rgb.b * 114) / 1000;
  }

  /**
   * Check if color is light or dark
   */
  static isLight(hex: string): boolean {
    return this.getBrightness(hex) > 127;
  }

  /**
   * Get contrasting color (black or white)
   */
  static getContrastColor(hex: string): string {
    return this.isLight(hex) ? '#000000' : '#FFFFFF';
  }

  /**
   * Calculate color contrast ratio
   */
  static getContrastRatio(color1: string, color2: string): number {
    const l1 = this.getRelativeLuminance(color1);
    const l2 = this.getRelativeLuminance(color2);
    
    const bright = Math.max(l1, l2);
    const dark = Math.min(l1, l2);
    
    return (bright + 0.05) / (dark + 0.05);
  }

  /**
   * Get relative luminance for contrast calculations
   */
  static getRelativeLuminance(hex: string): number {
    const rgb = this.hexToRgb(hex);
    if (!rgb) return 0;

    const [r, g, b] = [rgb.r, rgb.g, rgb.b].map(c => {
      c = c / 255;
      return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    });

    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  }

  /**
   * Generate color variations (lighter/darker)
   */
  static generateVariations(hex: string, steps: number = 5): string[] {
    const rgb = this.hexToRgb(hex);
    if (!rgb) return [hex];

    const variations: string[] = [];
    
    for (let i = -steps; i <= steps; i++) {
      const factor = i * 0.1;
      const newRgb = {
        r: Math.max(0, Math.min(255, rgb.r + (255 - rgb.r) * factor)),
        g: Math.max(0, Math.min(255, rgb.g + (255 - rgb.g) * factor)),
        b: Math.max(0, Math.min(255, rgb.b + (255 - rgb.b) * factor))
      };
      
      variations.push(this.rgbToHex(Math.round(newRgb.r), Math.round(newRgb.g), Math.round(newRgb.b)));
    }
    
    return variations;
  }

  /**
   * Blend two colors
   */
  static blendColors(color1: string, color2: string, ratio: number = 0.5): string {
    const rgb1 = this.hexToRgb(color1);
    const rgb2 = this.hexToRgb(color2);
    
    if (!rgb1 || !rgb2) return color1;

    const blended = {
      r: Math.round(rgb1.r * (1 - ratio) + rgb2.r * ratio),
      g: Math.round(rgb1.g * (1 - ratio) + rgb2.g * ratio),
      b: Math.round(rgb1.b * (1 - ratio) + rgb2.b * ratio)
    };

    return this.rgbToHex(blended.r, blended.g, blended.b);
  }
}

/**
 * Terminal detection utilities
 */
export class TerminalUtils {
  /**
   * Detect terminal type and capabilities
   */
  static detectTerminal(): {
    name: string;
    capabilities: TerminalCapabilities;
    profile: string;
  } {
    const env = process.env;
    const capabilities = detectTerminalCapabilities();
    
    let name = 'Unknown Terminal';
    let profile = 'basic';

    // Detect specific terminals
    if (env.TERM_PROGRAM === 'vscode') {
      name = 'VS Code Terminal';
      profile = 'vscode';
    } else if (env.TERM_PROGRAM === 'iTerm.app') {
      name = 'iTerm2';
      profile = 'iterm2';
    } else if (env.WT_SESSION) {
      name = 'Windows Terminal';
      profile = 'windowsTerminal';
    } else if (env.GNOME_TERMINAL_SCREEN) {
      name = 'GNOME Terminal';
      profile = 'gnomeTerminal';
    } else if (env.TERM?.includes('256')) {
      profile = 'basic';
    } else {
      profile = 'minimal';
    }

    return { name, capabilities, profile };
  }

  /**
   * Get recommended themes for current terminal
   */
  static getRecommendedThemes(themeManager: ThemeManager): string[] {
    const terminalInfo = this.detectTerminal();
    const availableThemes = themeManager.getAvailableThemes();
    
    return availableThemes
      .filter(theme => {
        const compatibility = themeManager.getThemeCompatibility(theme.name);
        return compatibility.compatible;
      })
      .map(theme => theme.name);
  }

  /**
   * Test terminal color support
   */
  static testColorSupport(): {
    supports8Color: boolean;
    supports16Color: boolean;
    supports256Color: boolean;
    supportsTrueColor: boolean;
  } {
    const capabilities = detectTerminalCapabilities();
    
    return {
      supports8Color: capabilities.color8,
      supports16Color: capabilities.color16,
      supports256Color: capabilities.color256,
      supportsTrueColor: capabilities.trueColor
    };
  }
}

/**
 * Theme validation utilities
 */
export class ThemeValidator {
  /**
   * Validate theme definition
   */
  static validateTheme(theme: any): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    // Check required fields
    if (!theme.name) errors.push('Theme name is required');
    if (!theme.displayName) errors.push('Theme display name is required');
    if (!theme.palette) errors.push('Theme palette is required');

    // Validate palette
    if (theme.palette) {
      const requiredColors = ['primary', 'secondary', 'success', 'warning', 'error', 'info', 'background', 'text'];
      
      for (const color of requiredColors) {
        if (!theme.palette[color]) {
          errors.push(`Required color '${color}' is missing`);
        } else {
          const colorDef = theme.palette[color];
          if (!colorDef.hex) errors.push(`Color '${color}' missing hex value`);
          if (colorDef.hex && !this.isValidHex(colorDef.hex)) {
            errors.push(`Color '${color}' has invalid hex value`);
          }
        }
      }
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }

  /**
   * Validate hex color
   */
  static isValidHex(hex: string): boolean {
    return /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/.test(hex);
  }

  /**
   * Check theme accessibility
   */
  static checkAccessibility(theme: ThemeDefinition): {
    score: number;
    issues: string[];
    recommendations: string[];
  } {
    const issues: string[] = [];
    const recommendations: string[] = [];
    let score = 100;

    // Check contrast ratios
    const textBgRatio = ColorUtils.getContrastRatio(theme.palette.text.hex, theme.palette.background.hex);
    const primaryBgRatio = ColorUtils.getContrastRatio(theme.palette.primary.hex, theme.palette.background.hex);

    if (textBgRatio < 4.5) {
      issues.push('Text contrast ratio is below WCAG AA standard (4.5:1)');
      recommendations.push('Increase contrast between text and background colors');
      score -= 20;
    }

    if (primaryBgRatio < 3) {
      issues.push('Primary color contrast ratio is below WCAG AA standard for large text (3:1)');
      recommendations.push('Increase contrast for primary color');
      score -= 10;
    }

    // Check color blind support
    if (!theme.colorBlindSupport) {
      issues.push('No color blind support provided');
      recommendations.push('Add color blind support for better accessibility');
      score -= 15;
    }

    return { score: Math.max(0, score), issues, recommendations };
  }
}

/**
 * Style building utilities
 */
export class StyleBuilder {
  private styles: TextStyle = {};

  constructor(initialStyle?: TextStyle) {
    if (initialStyle) {
      this.styles = { ...initialStyle };
    }
  }

  /**
   * Set text color
   */
  color(color: string): StyleBuilder {
    this.styles.color = color;
    return this;
  }

  /**
   * Set background color
   */
  backgroundColor(color: string): StyleBuilder {
    this.styles.backgroundColor = color;
    return this;
  }

  /**
   * Make text bold
   */
  bold(enabled: boolean = true): StyleBuilder {
    this.styles.bold = enabled;
    return this;
  }

  /**
   * Make text italic
   */
  italic(enabled: boolean = true): StyleBuilder {
    this.styles.italic = enabled;
    return this;
  }

  /**
   * Underline text
   */
  underline(enabled: boolean = true): StyleBuilder {
    this.styles.underline = enabled;
    return this;
  }

  /**
   * Make text dim
   */
  dim(enabled: boolean = true): StyleBuilder {
    this.styles.dim = enabled;
    return this;
  }

  /**
   * Reverse colors
   */
  reverse(enabled: boolean = true): StyleBuilder {
    this.styles.reverse = enabled;
    return this;
  }

  /**
   * Build the style object
   */
  build(): TextStyle {
    return { ...this.styles };
  }

  /**
   * Apply style to text using theme manager
   */
  apply(text: string, themeManager: ThemeManager): string {
    const styleDefinitions = themeManager.getStyleDefinitions();
    return styleDefinitions.applyStyle(text, this.styles);
  }
}

/**
 * Create a new style builder
 */
export function createStyle(initialStyle?: TextStyle): StyleBuilder {
  return new StyleBuilder(initialStyle);
}

/**
 * Quick style helpers
 */
export const styles = {
  bold: (text: string) => createStyle().bold().build(),
  italic: (text: string) => createStyle().italic().build(),
  underline: (text: string) => createStyle().underline().build(),
  dim: (text: string) => createStyle().dim().build(),
  
  primary: (text: string) => createStyle().color('primary').build(),
  success: (text: string) => createStyle().color('success').bold().build(),
  warning: (text: string) => createStyle().color('warning').bold().build(),
  error: (text: string) => createStyle().color('error').bold().build(),
  info: (text: string) => createStyle().color('info').bold().build()
};

/**
 * Theme migration utilities
 */
export class ThemeMigration {
  /**
   * Migrate theme from old format to new format
   */
  static migrateTheme(oldTheme: any): ThemeDefinition | null {
    try {
      // Add migration logic here for different theme versions
      // This is a placeholder for future theme format changes
      return oldTheme as ThemeDefinition;
    } catch (error) {
      console.error('Theme migration failed:', error);
      return null;
    }
  }

  /**
   * Check if theme needs migration
   */
  static needsMigration(theme: any): boolean {
    // Check for version or format indicators
    return !theme.version || theme.version < '1.0.0';
  }
}