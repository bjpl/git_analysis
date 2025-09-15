/**
 * Menu System Index - Main entry point for the Interactive Menu System
 * Exports all components and provides convenient factory functions
 */

// Core components
export { InteractiveMenu } from './InteractiveMenu.js';
export { MenuRenderer } from './MenuRenderer.js';
export { MenuStateManager } from './MenuState.js';
export { MenuAnimations } from './MenuAnimations.js';
export { MenuConfigLoader } from './MenuConfig.js';

// Types and interfaces
export * from './types.js';

// Re-export commonly used types
export type {
  MenuItem,
  MenuConfiguration,
  MenuState,
  MenuStyle,
  MenuEventHandlers,
  MenuPlugin,
  MenuAnimation,
  MenuTransition,
  MenuSearchResult,
  MenuBreadcrumb,
  MenuContext,
  MenuPreferences,
  MenuPerformanceMetrics
} from './types.js';

import { InteractiveMenu } from './InteractiveMenu.js';
import { MenuConfigLoader } from './MenuConfig.js';
import { MenuConfiguration, MenuEventHandlers } from './types.js';

// ================================
// Factory Functions
// ================================

/**
 * Create a new interactive menu from configuration
 */
export async function createMenu(
  config: MenuConfiguration | string,
  container?: HTMLElement,
  eventHandlers?: MenuEventHandlers
): Promise<InteractiveMenu> {
  let menuConfig: MenuConfiguration;
  
  if (typeof config === 'string') {
    const loader = new MenuConfigLoader();
    menuConfig = await loader.load(config);
  } else {
    menuConfig = config;
  }
  
  const menu = new InteractiveMenu(menuConfig, container);
  
  // Register event handlers if provided
  if (eventHandlers) {
    Object.entries(eventHandlers).forEach(([event, handler]) => {
      menu.on(event as any, handler as any);
    });
  }
  
  return menu;
}

/**
 * Create a menu from one of the example configurations
 */
export async function createExampleMenu(
  type: 'main' | 'settings' | 'tools',
  container?: HTMLElement,
  eventHandlers?: MenuEventHandlers
): Promise<InteractiveMenu> {
  const configPath = `/examples/menus/${type}-menu.json`;
  return createMenu(configPath, container, eventHandlers);
}

/**
 * Quick setup function for common use cases
 */
export async function quickSetup(options: {
  type?: 'main' | 'settings' | 'tools';
  container?: HTMLElement | string;
  style?: Partial<MenuStyle>;
  theme?: 'default' | 'dark' | 'light' | 'colorful';
  animations?: boolean;
  onItemSelect?: (item: MenuItem, path: string[]) => void;
  onError?: (error: string) => void;
} = {}): Promise<InteractiveMenu> {
  const {
    type = 'main',
    container,
    style = {},
    theme = 'default',
    animations = true,
    onItemSelect,
    onError
  } = options;
  
  // Resolve container
  let targetContainer: HTMLElement | undefined;
  if (typeof container === 'string') {
    const element = document.querySelector(container);
    if (!element) {
      throw new Error(`Container not found: ${container}`);
    }
    targetContainer = element as HTMLElement;
  } else {
    targetContainer = container;
  }
  
  // Load example configuration
  const menu = await createExampleMenu(type, targetContainer);
  
  // Apply style overrides
  if (Object.keys(style).length > 0 || theme !== 'default' || animations !== true) {
    const config = menu.getConfig();
    config.style = {
      ...config.style,
      ...style,
      theme,
      animations
    };
  }
  
  // Register event handlers
  if (onItemSelect) {
    menu.on('itemSelect', onItemSelect);
  }
  
  if (onError) {
    menu.on('error', onError);
  }
  
  return menu;
}

// ================================
// Utility Functions
// ================================

/**
 * Validate a menu configuration
 */
export async function validateMenuConfig(
  config: MenuConfiguration | string
): Promise<{ valid: boolean; errors: string[]; warnings: string[] }> {
  const loader = new MenuConfigLoader();
  
  try {
    let menuConfig: MenuConfiguration;
    
    if (typeof config === 'string') {
      menuConfig = await loader.load(config);
    } else {
      menuConfig = config;
    }
    
    const result = await loader.validateConfig(menuConfig);
    
    return {
      valid: result.errors.length === 0,
      errors: result.errors.map(e => e.message),
      warnings: result.warnings.map(w => w.message)
    };
  } catch (error) {
    return {
      valid: false,
      errors: [`Validation failed: ${error}`],
      warnings: []
    };
  }
}

/**
 * Load and parse a menu configuration file
 */
export async function loadMenuConfig(path: string): Promise<MenuConfiguration> {
  const loader = new MenuConfigLoader();
  return loader.load(path);
}

/**
 * Register CSS animations for the menu system
 */
export function registerMenuStyles(): void {
  if (typeof document === 'undefined') {
    return; // Not in browser environment
  }
  
  const styleId = 'interactive-menu-styles';
  
  // Check if styles are already registered
  if (document.getElementById(styleId)) {
    return;
  }
  
  const style = document.createElement('style');
  style.id = styleId;
  style.textContent = `
    /* Interactive Menu System Styles */
    
    .menu-container {
      --bg-color: #ffffff;
      --text-color: #1f2937;
      --border-color: #e5e7eb;
      --hover-bg: #f9fafb;
      --selected-bg: #eff6ff;
      --badge-bg: #ef4444;
      --card-bg: #ffffff;
      --shortcut-bg: #f1f5f9;
      --shortcut-text: #64748b;
      --highlight-color: #fef3c7;
      --highlight-color-active: #fde047;
      --success-color: #10b981;
      --error-color: #ef4444;
      
      font-family: system-ui, -apple-system, sans-serif;
      color: var(--text-color);
      background: var(--bg-color);
    }
    
    .menu-container[data-theme="dark"] {
      --bg-color: #1f2937;
      --text-color: #f9fafb;
      --border-color: #374151;
      --hover-bg: #374151;
      --selected-bg: #1e40af;
      --badge-bg: #dc2626;
      --card-bg: #111827;
    }
    
    .menu-container[data-theme="light"] {
      --bg-color: #fefefe;
      --text-color: #0f172a;
      --border-color: #cbd5e1;
      --hover-bg: #f8fafc;
      --selected-bg: #dbeafe;
      --badge-bg: #3b82f6;
      --card-bg: #ffffff;
    }
    
    .menu-item {
      border-radius: 6px;
      transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
      user-select: none;
      outline: none;
    }
    
    .menu-item:focus {
      box-shadow: 0 0 0 2px var(--selected-bg);
    }
    
    .menu-item:hover:not(.menu-item-disabled) {
      background-color: var(--hover-bg);
    }
    
    .menu-item-disabled {
      opacity: 0.5;
      cursor: not-allowed !important;
    }
    
    .menu-item-title {
      font-weight: 500;
      font-size: 14px;
      line-height: 1.4;
    }
    
    .menu-item-description {
      font-size: 12px;
      opacity: 0.7;
      margin-top: 2px;
      line-height: 1.3;
    }
    
    .menu-item-icon {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font-size: 16px;
    }
    
    .menu-item-badge {
      font-size: 10px;
      padding: 2px 6px;
      background-color: var(--badge-bg);
      color: white;
      border-radius: 10px;
      font-weight: 600;
      line-height: 1;
    }
    
    .menu-item-shortcut {
      font-size: 10px;
      padding: 2px 6px;
      background-color: var(--shortcut-bg);
      color: var(--shortcut-text);
      border-radius: 4px;
      font-family: ui-monospace, monospace;
    }
    
    .submenu-indicator {
      font-size: 10px;
      opacity: 0.6;
      transition: transform 0.2s ease;
    }
    
    .search-highlight {
      background-color: var(--highlight-color);
      padding: 0 2px;
      border-radius: 2px;
      font-weight: 600;
    }
    
    /* Grid layout */
    .menu-grid {
      display: grid;
      gap: 12px;
      padding: 16px;
    }
    
    /* Cards layout */
    .menu-cards {
      display: flex;
      flex-wrap: wrap;
      gap: 16px;
      padding: 16px;
    }
    
    .menu-item-card {
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      transition: all 0.2s ease;
    }
    
    .menu-item-card:hover:not(.menu-item-disabled) {
      box-shadow: 0 4px 8px rgba(0,0,0,0.15);
      transform: translateY(-1px);
    }
    
    /* Tree layout */
    .menu-tree {
      padding: 8px;
    }
    
    .menu-tree-submenu {
      margin-left: 20px;
      border-left: 2px solid var(--border-color);
      padding-left: 12px;
      margin-top: 4px;
    }
    
    .expand-indicator {
      cursor: pointer;
      transition: transform 0.2s ease;
    }
    
    .expand-indicator.expanded {
      transform: rotate(180deg);
    }
    
    /* Animations */
    @keyframes menuFadeIn {
      from {
        opacity: 0;
        transform: translateY(10px) scale(0.95);
      }
      to {
        opacity: 1;
        transform: translateY(0) scale(1);
      }
    }
    
    @keyframes menuSlideIn {
      from {
        transform: translateX(100%);
      }
      to {
        transform: translateX(0);
      }
    }
    
    @keyframes blink {
      0%, 50% { opacity: 1; }
      51%, 100% { opacity: 0; }
    }
    
    /* Accessibility */
    @media (prefers-reduced-motion: reduce) {
      .menu-item,
      .submenu-indicator,
      .expand-indicator {
        transition: none !important;
        animation: none !important;
      }
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
      .menu-grid {
        grid-template-columns: 1fr !important;
      }
      
      .menu-item-card {
        width: 100% !important;
        max-width: none !important;
      }
    }
    
    /* High contrast mode */
    @media (prefers-contrast: high) {
      .menu-container {
        --border-color: #000000;
        --hover-bg: #ffff00;
        --selected-bg: #0000ff;
        --text-color: #000000;
      }
    }
  `;
  
  document.head.appendChild(style);
}

// ================================
// Auto-initialization
// ================================

/**
 * Auto-initialize menu system when DOM is ready
 */
if (typeof document !== 'undefined') {
  // Register styles immediately
  registerMenuStyles();
  
  // Auto-initialize if data attributes are found
  document.addEventListener('DOMContentLoaded', async () => {
    const autoMenus = document.querySelectorAll('[data-menu-config]');
    
    for (const element of autoMenus) {
      try {
        const configPath = element.getAttribute('data-menu-config');
        const theme = element.getAttribute('data-menu-theme') || 'default';
        const style = element.getAttribute('data-menu-style') || 'list';
        const animations = element.getAttribute('data-menu-animations') !== 'false';
        
        if (configPath) {
          await quickSetup({
            container: element as HTMLElement,
            style: { type: style as any, theme: theme as any, animations },
            onError: (error) => console.error('Menu error:', error)
          });
        }
      } catch (error) {
        console.error('Failed to auto-initialize menu:', error);
      }
    }
  });
}

// ================================
// Default Export
// ================================

export default {
  InteractiveMenu,
  MenuRenderer,
  MenuStateManager,
  MenuAnimations,
  MenuConfigLoader,
  createMenu,
  createExampleMenu,
  quickSetup,
  validateMenuConfig,
  loadMenuConfig,
  registerMenuStyles
};
