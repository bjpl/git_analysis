/**
 * Theme Manager - Central theme loading and switching system
 * Handles theme persistence, validation, and runtime switching
 */

import * as fs from 'fs';
import * as path from 'path';
import { ColorScheme, ColorPalette, ColorBlindSupport, TerminalCapabilities, detectTerminalCapabilities } from './ColorScheme';
import { StyleDefinitions, UIComponentStyles } from './StyleDefinitions';

export interface ThemeDefinition {
  name: string;
  displayName: string;
  description: string;
  author?: string;
  version?: string;
  palette: ColorPalette;
  colorBlindSupport?: ColorBlindSupport;
  customStyles?: Partial<UIComponentStyles>;
  terminalRequirements?: {
    minColors?: number;
    requiresTrueColor?: boolean;
    requiresUnicode?: boolean;
  };
}

export interface ThemeConfig {
  currentTheme: string;
  fallbackTheme: string;
  accessibilityMode?: keyof ColorBlindSupport;
  customThemePaths?: string[];
  userPreferences?: {
    autoDetectTerminal?: boolean;
    gracefulDegradation?: boolean;
    persistSettings?: boolean;
  };
}

export interface ThemeChangeEvent {
  previousTheme: string;
  newTheme: string;
  timestamp: Date;
}

export type ThemeChangeListener = (event: ThemeChangeEvent) => void;

export class ThemeManager {
  private themes: Map<string, ThemeDefinition> = new Map();
  private currentTheme: ThemeDefinition;
  private config: ThemeConfig;
  private configPath: string;
  private terminalCapabilities: TerminalCapabilities;
  private colorScheme: ColorScheme;
  private styleDefinitions: StyleDefinitions;
  private changeListeners: Set<ThemeChangeListener> = new Set();

  constructor(configPath?: string) {
    this.configPath = configPath || path.join(process.cwd(), 'config', 'themes.json');
    this.terminalCapabilities = detectTerminalCapabilities();
    
    // Load built-in themes
    this.loadBuiltInThemes();
    
    // Load configuration
    this.loadConfig();
    
    // Initialize with current theme
    this.initializeTheme();
  }

  /**
   * Get current active theme
   */
  getCurrentTheme(): ThemeDefinition {
    return this.currentTheme;
  }

  /**
   * Get current color scheme
   */
  getColorScheme(): ColorScheme {
    return this.colorScheme;
  }

  /**
   * Get current style definitions
   */
  getStyleDefinitions(): StyleDefinitions {
    return this.styleDefinitions;
  }

  /**
   * Get terminal capabilities
   */
  getTerminalCapabilities(): TerminalCapabilities {
    return this.terminalCapabilities;
  }

  /**
   * List all available themes
   */
  getAvailableThemes(): Array<{ name: string; displayName: string; description: string }> {
    return Array.from(this.themes.values()).map(theme => ({
      name: theme.name,
      displayName: theme.displayName,
      description: theme.description
    }));
  }

  /**
   * Switch to a different theme
   */
  async switchTheme(themeName: string): Promise<boolean> {
    const theme = this.themes.get(themeName);
    if (!theme) {
      console.warn(`Theme '${themeName}' not found`);
      return false;
    }

    // Check terminal compatibility
    if (!this.isThemeCompatible(theme)) {
      console.warn(`Theme '${themeName}' is not compatible with current terminal capabilities`);
      // Attempt graceful degradation if enabled
      if (this.config.userPreferences?.gracefulDegradation) {
        console.info('Attempting graceful degradation...');
      } else {
        return false;
      }
    }

    const previousTheme = this.currentTheme.name;
    this.currentTheme = theme;
    
    // Update color scheme and styles
    this.updateColorScheme();
    this.updateStyleDefinitions();
    
    // Update configuration
    this.config.currentTheme = themeName;
    if (this.config.userPreferences?.persistSettings) {
      await this.saveConfig();
    }

    // Notify listeners
    const event: ThemeChangeEvent = {
      previousTheme,
      newTheme: themeName,
      timestamp: new Date()
    };
    
    this.changeListeners.forEach(listener => {
      try {
        listener(event);
      } catch (error) {
        console.error('Error in theme change listener:', error);
      }
    });

    return true;
  }

  /**
   * Set accessibility mode
   */
  setAccessibilityMode(mode: keyof ColorBlindSupport | null): void {
    this.colorScheme.setAccessibilityMode(mode);
    this.config.accessibilityMode = mode || undefined;
    
    if (this.config.userPreferences?.persistSettings) {
      this.saveConfig();
    }
  }

  /**
   * Load theme from file
   */
  async loadThemeFromFile(filePath: string): Promise<boolean> {
    try {
      const themeData = JSON.parse(await fs.promises.readFile(filePath, 'utf-8'));
      const theme = this.validateTheme(themeData);
      
      if (theme) {
        this.themes.set(theme.name, theme);
        return true;
      }
      
      return false;
    } catch (error) {
      console.error(`Failed to load theme from ${filePath}:`, error);
      return false;
    }
  }

  /**
   * Register a custom theme
   */
  registerTheme(theme: ThemeDefinition): boolean {
    if (this.validateTheme(theme)) {
      this.themes.set(theme.name, theme);
      return true;
    }
    return false;
  }

  /**
   * Add theme change listener
   */
  onThemeChange(listener: ThemeChangeListener): () => void {
    this.changeListeners.add(listener);
    
    // Return unsubscribe function
    return () => {
      this.changeListeners.delete(listener);
    };
  }

  /**
   * Create a custom theme based on the current theme
   */
  createCustomTheme(
    name: string,
    displayName: string,
    customizations: Partial<ColorPalette & { customStyles?: Partial<UIComponentStyles> }>
  ): ThemeDefinition {
    const baseTheme = this.currentTheme;
    const customPalette = { ...baseTheme.palette, ...customizations };
    
    const customTheme: ThemeDefinition = {
      name,
      displayName,
      description: `Custom theme based on ${baseTheme.displayName}`,
      palette: customPalette,
      colorBlindSupport: baseTheme.colorBlindSupport,
      customStyles: {
        ...baseTheme.customStyles,
        ...customizations.customStyles
      }
    };

    return customTheme;
  }

  /**
   * Export current theme configuration
   */
  exportTheme(): ThemeDefinition {
    return { ...this.currentTheme };
  }

  /**
   * Reset to default theme
   */
  async resetToDefault(): Promise<boolean> {
    return await this.switchTheme('default');
  }

  /**
   * Get theme compatibility information
   */
  getThemeCompatibility(themeName: string): {
    compatible: boolean;
    issues: string[];
    recommendations: string[];
  } {
    const theme = this.themes.get(themeName);
    const issues: string[] = [];
    const recommendations: string[] = [];

    if (!theme) {
      return {
        compatible: false,
        issues: ['Theme not found'],
        recommendations: ['Choose an available theme']
      };
    }

    const requirements = theme.terminalRequirements;
    if (requirements) {
      if (requirements.requiresTrueColor && !this.terminalCapabilities.trueColor) {
        issues.push('Theme requires true color support');
        recommendations.push('Use a terminal that supports 24-bit color');
      }

      if (requirements.minColors) {
        let supportedColors = 0;
        if (this.terminalCapabilities.trueColor) supportedColors = 16777216;
        else if (this.terminalCapabilities.color256) supportedColors = 256;
        else if (this.terminalCapabilities.color16) supportedColors = 16;
        else if (this.terminalCapabilities.color8) supportedColors = 8;

        if (supportedColors < requirements.minColors) {
          issues.push(`Theme requires ${requirements.minColors} colors, terminal supports ${supportedColors}`);
          recommendations.push('Upgrade terminal or choose a simpler theme');
        }
      }

      if (requirements.requiresUnicode && !this.terminalCapabilities.unicode) {
        issues.push('Theme requires Unicode support');
        recommendations.push('Set locale to UTF-8 or choose ASCII-compatible theme');
      }
    }

    return {
      compatible: issues.length === 0,
      issues,
      recommendations
    };
  }

  private loadBuiltInThemes(): void {
    // These will be loaded from separate theme files
    const builtInThemes = ['default', 'dark', 'high-contrast', 'custom'];
    
    builtInThemes.forEach(themeName => {
      try {
        const themePath = path.join(__dirname, `${themeName}.theme.ts`);
        // In a real implementation, we'd dynamically import these
        // For now, we'll load them via require or static imports
      } catch (error) {
        console.warn(`Could not load built-in theme: ${themeName}`);
      }
    });
  }

  private loadConfig(): void {
    try {
      if (fs.existsSync(this.configPath)) {
        const configData = fs.readFileSync(this.configPath, 'utf-8');
        this.config = JSON.parse(configData);
      } else {
        this.config = this.getDefaultConfig();
      }
    } catch (error) {
      console.warn('Failed to load theme config, using defaults');
      this.config = this.getDefaultConfig();
    }
  }

  private async saveConfig(): Promise<void> {
    try {
      const configDir = path.dirname(this.configPath);
      await fs.promises.mkdir(configDir, { recursive: true });
      await fs.promises.writeFile(this.configPath, JSON.stringify(this.config, null, 2));
    } catch (error) {
      console.error('Failed to save theme config:', error);
    }
  }

  private getDefaultConfig(): ThemeConfig {
    return {
      currentTheme: 'default',
      fallbackTheme: 'default',
      userPreferences: {
        autoDetectTerminal: true,
        gracefulDegradation: true,
        persistSettings: true
      }
    };
  }

  private initializeTheme(): void {
    let initialTheme = this.themes.get(this.config.currentTheme);
    
    if (!initialTheme || !this.isThemeCompatible(initialTheme)) {
      initialTheme = this.themes.get(this.config.fallbackTheme) || this.themes.values().next().value;
    }
    
    this.currentTheme = initialTheme;
    this.updateColorScheme();
    this.updateStyleDefinitions();
    
    if (this.config.accessibilityMode) {
      this.colorScheme.setAccessibilityMode(this.config.accessibilityMode);
    }
  }

  private updateColorScheme(): void {
    this.colorScheme = new ColorScheme(
      this.currentTheme.palette,
      this.currentTheme.colorBlindSupport
    );
  }

  private updateStyleDefinitions(): void {
    this.styleDefinitions = new StyleDefinitions(
      this.colorScheme,
      this.terminalCapabilities,
      this.currentTheme.customStyles
    );
  }

  private isThemeCompatible(theme: ThemeDefinition): boolean {
    const requirements = theme.terminalRequirements;
    if (!requirements) return true;

    if (requirements.requiresTrueColor && !this.terminalCapabilities.trueColor) {
      return false;
    }

    if (requirements.requiresUnicode && !this.terminalCapabilities.unicode) {
      return false;
    }

    if (requirements.minColors) {
      let supportedColors = 0;
      if (this.terminalCapabilities.trueColor) supportedColors = 16777216;
      else if (this.terminalCapabilities.color256) supportedColors = 256;
      else if (this.terminalCapabilities.color16) supportedColors = 16;
      else if (this.terminalCapabilities.color8) supportedColors = 8;

      if (supportedColors < requirements.minColors) {
        return false;
      }
    }

    return true;
  }

  private validateTheme(theme: any): ThemeDefinition | null {
    if (!theme || typeof theme !== 'object') return null;
    if (!theme.name || !theme.displayName || !theme.palette) return null;
    
    // Basic validation - in production, you'd want more thorough validation
    return theme as ThemeDefinition;
  }
}

// Export singleton instance
export const themeManager = new ThemeManager();