/**
 * Theme System Entry Point
 * Exports all theme-related functionality
 */

// Core theme system
export { ThemeManager, themeManager, type ThemeDefinition, type ThemeConfig } from './ThemeManager';
export { ColorScheme, type ColorPalette, type ColorDefinition, type ColorBlindSupport, type TerminalCapabilities, detectTerminalCapabilities } from './ColorScheme';
export { StyleDefinitions, type TextStyle, type ComponentStyle, type UIComponentStyles, type LayoutStyle, type SyntaxHighlightStyles } from './StyleDefinitions';

// Built-in themes
export { defaultTheme } from './default.theme';
export { darkTheme } from './dark.theme';
export { highContrastTheme } from './high-contrast.theme';
export { customTheme, createCustomTheme, customThemePresets } from './custom.theme';

// Theme utilities
export * from './utils';

/**
 * Quick start function to initialize theme system
 */
export function initializeThemeSystem(configPath?: string) {
  const manager = new ThemeManager(configPath);
  
  // Register built-in themes
  manager.registerTheme(defaultTheme);
  manager.registerTheme(darkTheme);
  manager.registerTheme(highContrastTheme);
  manager.registerTheme(customTheme);
  
  return manager;
}

/**
 * Get the singleton theme manager instance
 */
export function getThemeManager(): ThemeManager {
  return themeManager;
}

/**
 * Quick theme switching helper
 */
export async function switchTheme(themeName: string): Promise<boolean> {
  return await themeManager.switchTheme(themeName);
}

/**
 * Quick accessibility mode helper
 */
export function setAccessibilityMode(mode: keyof ColorBlindSupport | null): void {
  themeManager.setAccessibilityMode(mode);
}

/**
 * Get styled text helper
 */
export function styledText(text: string, style: TextStyle): string {
  const styleDefinitions = themeManager.getStyleDefinitions();
  return styleDefinitions.applyStyle(text, style);
}

/**
 * Get component style helper
 */
export function getComponentStyle(component: keyof UIComponentStyles, state: keyof ComponentStyle = 'default'): TextStyle {
  const styleDefinitions = themeManager.getStyleDefinitions();
  return styleDefinitions.getComponentStyle(component, state);
}

/**
 * Apply component style to text
 */
export function styledComponent(text: string, component: keyof UIComponentStyles, state: keyof ComponentStyle = 'default'): string {
  const style = getComponentStyle(component, state);
  return styledText(text, style);
}

/**
 * Terminal capability detection helper
 */
export function getTerminalInfo() {
  const capabilities = themeManager.getTerminalCapabilities();
  const currentTheme = themeManager.getCurrentTheme();
  const compatibility = themeManager.getThemeCompatibility(currentTheme.name);
  
  return {
    capabilities,
    currentTheme: currentTheme.name,
    compatibility
  };
}

// Re-export types for convenience
export type {
  ThemeDefinition,
  ThemeConfig,
  ColorPalette,
  ColorDefinition,
  ColorBlindSupport,
  TerminalCapabilities,
  TextStyle,
  ComponentStyle,
  UIComponentStyles,
  LayoutStyle,
  SyntaxHighlightStyles
};