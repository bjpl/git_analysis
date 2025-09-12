/**
 * Color Scheme Management System
 * Handles color palette definitions with support for various terminal capabilities
 */

export interface ColorDefinition {
  /** RGB hex value (e.g., "#FF5733") */
  hex: string;
  /** 256-color terminal code */
  ansi256?: number;
  /** 16-color fallback */
  ansi16?: number;
  /** Basic 8-color fallback */
  ansi8?: number;
  /** Human readable name */
  name?: string;
}

export interface ColorPalette {
  // Primary colors
  primary: ColorDefinition;
  secondary: ColorDefinition;
  tertiary: ColorDefinition;
  
  // Status colors
  success: ColorDefinition;
  warning: ColorDefinition;
  error: ColorDefinition;
  info: ColorDefinition;
  
  // Neutral colors
  background: ColorDefinition;
  surface: ColorDefinition;
  text: ColorDefinition;
  textSecondary: ColorDefinition;
  textDisabled: ColorDefinition;
  border: ColorDefinition;
  
  // Semantic colors
  accent: ColorDefinition;
  highlight: ColorDefinition;
  muted: ColorDefinition;
  
  // Syntax highlighting
  syntax?: {
    keyword: ColorDefinition;
    string: ColorDefinition;
    number: ColorDefinition;
    comment: ColorDefinition;
    operator: ColorDefinition;
    function: ColorDefinition;
    variable: ColorDefinition;
    type: ColorDefinition;
  };
}

export interface ColorBlindSupport {
  /** Protanopia (red-green colorblind) alternative colors */
  protanopia?: Partial<ColorPalette>;
  /** Deuteranopia (red-green colorblind) alternative colors */
  deuteranopia?: Partial<ColorPalette>;
  /** Tritanopia (blue-yellow colorblind) alternative colors */
  tritanopia?: Partial<ColorPalette>;
  /** High contrast mode */
  highContrast?: Partial<ColorPalette>;
}

export class ColorScheme {
  private palette: ColorPalette;
  private colorBlindSupport?: ColorBlindSupport;
  private currentAccessibilityMode?: keyof ColorBlindSupport;

  constructor(palette: ColorPalette, colorBlindSupport?: ColorBlindSupport) {
    this.palette = palette;
    this.colorBlindSupport = colorBlindSupport;
  }

  /**
   * Get color definition with terminal capability detection
   */
  getColor(colorKey: keyof ColorPalette | string): ColorDefinition {
    // Handle nested syntax colors
    if (colorKey.includes('.')) {
      const [category, subKey] = colorKey.split('.');
      if (category === 'syntax' && this.palette.syntax) {
        return this.palette.syntax[subKey as keyof typeof this.palette.syntax] || this.palette.text;
      }
    }

    // Apply accessibility mode if active
    if (this.currentAccessibilityMode && this.colorBlindSupport) {
      const accessiblePalette = this.colorBlindSupport[this.currentAccessibilityMode];
      if (accessiblePalette && colorKey in accessiblePalette) {
        return accessiblePalette[colorKey as keyof ColorPalette]!;
      }
    }

    return this.palette[colorKey as keyof ColorPalette] || this.palette.text;
  }

  /**
   * Get ANSI color code based on terminal capabilities
   */
  getAnsiCode(colorKey: keyof ColorPalette | string, terminalCapabilities: TerminalCapabilities): string {
    const color = this.getColor(colorKey);
    
    if (terminalCapabilities.trueColor && color.hex) {
      return this.hexToAnsiTrueColor(color.hex);
    } else if (terminalCapabilities.color256 && color.ansi256) {
      return `\x1b[38;5;${color.ansi256}m`;
    } else if (terminalCapabilities.color16 && color.ansi16) {
      return `\x1b[${color.ansi16}m`;
    } else if (color.ansi8) {
      return `\x1b[${color.ansi8}m`;
    }
    
    return ''; // No color support
  }

  /**
   * Get background ANSI color code
   */
  getBgAnsiCode(colorKey: keyof ColorPalette | string, terminalCapabilities: TerminalCapabilities): string {
    const color = this.getColor(colorKey);
    
    if (terminalCapabilities.trueColor && color.hex) {
      return this.hexToAnsiBgTrueColor(color.hex);
    } else if (terminalCapabilities.color256 && color.ansi256) {
      return `\x1b[48;5;${color.ansi256}m`;
    } else if (terminalCapabilities.color16 && color.ansi16) {
      return `\x1b[${color.ansi16 + 10}m`; // Background codes are +10
    } else if (color.ansi8) {
      return `\x1b[${color.ansi8 + 10}m`;
    }
    
    return '';
  }

  /**
   * Set accessibility mode for color blind users
   */
  setAccessibilityMode(mode: keyof ColorBlindSupport | null): void {
    this.currentAccessibilityMode = mode || undefined;
  }

  /**
   * Get current accessibility mode
   */
  getAccessibilityMode(): keyof ColorBlindSupport | undefined {
    return this.currentAccessibilityMode;
  }

  /**
   * Get all available colors as a flat object
   */
  getAllColors(): Record<string, ColorDefinition> {
    const colors: Record<string, ColorDefinition> = {};
    
    // Add main palette colors
    Object.entries(this.palette).forEach(([key, value]) => {
      if (key === 'syntax' && value && typeof value === 'object') {
        // Handle syntax colors separately
        Object.entries(value).forEach(([syntaxKey, syntaxValue]) => {
          colors[`syntax.${syntaxKey}`] = syntaxValue;
        });
      } else if (value && 'hex' in value) {
        colors[key] = value;
      }
    });
    
    return colors;
  }

  /**
   * Convert hex color to ANSI true color escape sequence
   */
  private hexToAnsiTrueColor(hex: string): string {
    const rgb = this.hexToRgb(hex);
    return `\x1b[38;2;${rgb.r};${rgb.g};${rgb.b}m`;
  }

  /**
   * Convert hex color to ANSI true color background escape sequence
   */
  private hexToAnsiBgTrueColor(hex: string): string {
    const rgb = this.hexToRgb(hex);
    return `\x1b[48;2;${rgb.r};${rgb.g};${rgb.b}m`;
  }

  /**
   * Convert hex to RGB values
   */
  private hexToRgb(hex: string): { r: number; g: number; b: number } {
    const sanitizedHex = hex.replace('#', '');
    const r = parseInt(sanitizedHex.substr(0, 2), 16);
    const g = parseInt(sanitizedHex.substr(2, 2), 16);
    const b = parseInt(sanitizedHex.substr(4, 2), 16);
    return { r, g, b };
  }
}

export interface TerminalCapabilities {
  /** Supports 24-bit true color */
  trueColor: boolean;
  /** Supports 256 colors */
  color256: boolean;
  /** Supports 16 colors */
  color16: boolean;
  /** Supports 8 colors */
  color8: boolean;
  /** Terminal width */
  columns: number;
  /** Terminal height */
  rows: number;
  /** Supports Unicode */
  unicode: boolean;
}

/**
 * Detect terminal color capabilities
 */
export function detectTerminalCapabilities(): TerminalCapabilities {
  const env = process.env;
  const term = env.TERM || '';
  const colorTerm = env.COLORTERM || '';
  
  // Check for true color support
  const trueColor = !!(
    colorTerm === 'truecolor' ||
    colorTerm === '24bit' ||
    term.includes('24bit') ||
    env.TERM_PROGRAM === 'iTerm.app' ||
    env.TERM_PROGRAM === 'vscode' ||
    env.WT_SESSION // Windows Terminal
  );
  
  // Check for 256 color support
  const color256 = !!(
    trueColor ||
    term.includes('256') ||
    term.includes('xterm') ||
    term === 'screen-256color'
  );
  
  // Check for 16 color support
  const color16 = !!(
    color256 ||
    term.includes('color') ||
    env.COLORTERM
  );
  
  // Basic color support
  const color8 = color16 || term !== 'dumb';
  
  return {
    trueColor,
    color256,
    color16,
    color8,
    columns: process.stdout.columns || 80,
    rows: process.stdout.rows || 24,
    unicode: !env.LC_CTYPE || env.LC_CTYPE.toLowerCase().includes('utf')
  };
}