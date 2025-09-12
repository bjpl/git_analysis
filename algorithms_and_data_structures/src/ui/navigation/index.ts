/**
 * Navigation System - Main Export File
 * Provides a unified interface for the comprehensive CLI navigation system
 */

// Core Components
export { NavigationManager } from './NavigationManager.js';
export { MenuSystem } from './MenuSystem.js';
export { KeyboardHandler } from './KeyboardHandler.js';
export { HelpSystem } from './HelpSystem.js';

// Types and Interfaces
export * from '../../types/navigation.js';

// Additional Types from Components
export type { MenuDisplayOptions, MenuState } from './MenuSystem.js';
export type { KeyboardState, KeyPress, KeySequence } from './KeyboardHandler.js';
export type { 
  HelpEntry, 
  ContextualHelp, 
  QuickAction, 
  HelpSearchOptions 
} from './HelpSystem.js';

/**
 * Complete Navigation System
 * Integrates all navigation components into a unified system
 */
export class NavigationSystem {
  public readonly manager: NavigationManager;
  public readonly menu: MenuSystem;
  public readonly keyboard: KeyboardHandler;
  public readonly help: HelpSystem;

  constructor(config: Partial<NavigationConfig> = {}) {
    // Initialize all components with shared config
    this.manager = new NavigationManager(config);
    this.menu = new MenuSystem(this.manager.getConfig());
    this.keyboard = new KeyboardHandler(this.manager.getConfig());
    this.help = new HelpSystem(this.manager.getConfig());

    this.setupIntegrations();
  }

  /**
   * Set up integrations between components
   */
  private setupIntegrations(): void {
    // Navigation Manager -> Menu System
    this.manager.on('navigation-event', (event) => {
      if (event.type === 'navigate') {
        this.updateMenuForCurrentPath();
      }
    });

    // Navigation Manager -> Help System
    this.manager.on('node-added', (node) => {
      this.help.addHelpEntry({
        id: `node-${node.id}`,
        title: node.label,
        content: node.description || `Information about ${node.label}`,
        category: node.category || 'general',
        tags: node.tags || []
      });
    });

    // Keyboard Handler -> Navigation Manager
    this.keyboard.on('navigation-event', async (event) => {
      if (event.type === 'shortcut') {
        await this.handleKeyboardShortcut(event);
      }
    });

    // Keyboard Handler -> Menu System
    this.keyboard.on('key-binding-executed', (event) => {
      const action = event.data.binding.description?.toLowerCase();
      
      if (action?.includes('navigate up')) {
        this.menu.navigateUp();
      } else if (action?.includes('navigate down')) {
        this.menu.navigateDown();
      } else if (action?.includes('select')) {
        this.menu.selectCurrent();
      }
    });

    // Keyboard Handler -> Menu Search
    this.keyboard.on('input-character', (event) => {
      if (this.keyboard.getState().currentModifiers.ctrl && event.character === '/') {
        // Start search mode
        this.menu.updateSearch('');
      } else if (this.menu.getState().searchQuery !== undefined) {
        // Update search
        this.menu.updateSearch(this.keyboard.getInputBuffer());
      }
    });

    // Menu System -> Navigation Manager
    this.menu.on('item-selected', (event) => {
      if (event.node.command) {
        this.manager.executeCommand(event.node.command);
      } else {
        this.manager.navigateToPath(event.node.id);
      }
    });
  }

  /**
   * Handle keyboard shortcuts
   */
  private async handleKeyboardShortcut(event: NavigationEvent): Promise<void> {
    const binding = event.data.binding;
    const action = binding.description?.toLowerCase();

    if (action?.includes('search')) {
      this.startSearch();
    } else if (action?.includes('help')) {
      this.showHelp();
    } else if (action?.includes('back')) {
      await this.manager.executeCommand('back');
    } else if (action?.includes('home')) {
      await this.manager.executeCommand('home');
    }
  }

  /**
   * Update menu to show current path children
   */
  private updateMenuForCurrentPath(): void {
    const context = this.manager.getCurrentContext();
    const children = context.children || [];
    const menuItems = this.menu.nodesToMenuItems(children);
    
    this.menu.setItems(menuItems);
  }

  /**
   * Start search mode
   */
  startSearch(): void {
    this.menu.updateSearch('');
    this.keyboard.clearInputBuffer();
  }

  /**
   * Show contextual help
   */
  showHelp(): void {
    const context = this.manager.getCurrentContext();
    const helpContext = {
      currentNode: context.node,
      availableCommands: this.getAvailableCommands(),
      shortcuts: Object.values(this.manager.getConfig().keyBindings),
      suggestions: []
    };

    const contextualHelp = this.help.getContextualHelp(helpContext);
    this.displayHelp(contextualHelp);
  }

  /**
   * Get available commands for current context
   */
  private getAvailableCommands(): string[] {
    const context = this.manager.getCurrentContext();
    const commands = ['help', 'search', 'back', 'home'];
    
    if (context.node?.command) {
      commands.push(context.node.command);
    }
    
    if (context.children) {
      context.children.forEach(child => {
        if (child.command) {
          commands.push(child.command);
        }
      });
    }

    return commands;
  }

  /**
   * Display help information
   */
  private displayHelp(help: ContextualHelp): void {
    console.log('=== Help Information ===');
    
    if (help.primary.length > 0) {
      console.log('\\nPrimary Help:');
      help.primary.forEach(entry => {
        console.log(`• ${entry.title}: ${entry.content.substring(0, 100)}...`);
      });
    }

    if (help.quickActions.length > 0) {
      console.log('\\nQuick Actions:');
      help.quickActions.forEach(action => {
        console.log(`• ${action.label}: ${action.description}`);
      });
    }

    if (help.shortcuts.length > 0) {
      console.log('\\nKeyboard Shortcuts:');
      help.shortcuts.forEach(shortcut => {
        const keys = [];
        if (shortcut.ctrl) keys.push('Ctrl');
        if (shortcut.alt) keys.push('Alt');
        if (shortcut.shift) keys.push('Shift');
        keys.push(shortcut.key);
        console.log(`• ${keys.join('+')}: ${shortcut.description}`);
      });
    }

    if (help.tips && help.tips.length > 0) {
      console.log('\\nTips:');
      help.tips.forEach(tip => {
        console.log(`• ${tip}`);
      });
    }
  }

  /**
   * Render the complete navigation interface
   */
  render(): string {
    const state = this.manager.getState();
    const menuItems = this.menu.getState().filteredItems;
    
    return this.menu.renderMenu(menuItems, state.breadcrumbs);
  }

  /**
   * Process user input
   */
  processInput(input: string): void {
    this.keyboard.processInput(input);
  }

  /**
   * Process key press
   */
  processKeyPress(keyPress: KeyPress): void {
    this.keyboard.processKeyPress(keyPress);
  }

  /**
   * Execute command
   */
  async executeCommand(command: string): Promise<any> {
    return this.manager.executeCommand(command);
  }

  /**
   * Navigate to path
   */
  navigateTo(path: string): void {
    this.manager.navigateToPath(path);
  }

  /**
   * Add navigation node
   */
  addNode(node: NavigationNode): void {
    this.manager.addNode(node);
  }

  /**
   * Search for nodes
   */
  search(query: string): NavigationNode[] {
    return this.manager.executeSearch(query);
  }

  /**
   * Get current navigation state
   */
  getState(): {
    navigation: NavigationState;
    menu: MenuState;
    keyboard: KeyboardState;
  } {
    return {
      navigation: this.manager.getState(),
      menu: this.menu.getState(),
      keyboard: this.keyboard.getState()
    };
  }

  /**
   * Get system statistics
   */
  getStatistics(): {
    navigation: any;
    help: any;
  } {
    return {
      navigation: {
        totalNodes: this.manager['nodes'].size,
        currentPath: this.manager.getState().currentPath,
        historySize: this.manager.getState().history.length
      },
      help: this.help.getStatistics()
    };
  }

  /**
   * Activate the navigation system
   */
  activate(): void {
    this.keyboard.activate();
    this.menu.open();
  }

  /**
   * Deactivate the navigation system
   */
  deactivate(): void {
    this.keyboard.deactivate();
    this.menu.close();
  }

  /**
   * Check if system is active
   */
  isActive(): boolean {
    return this.keyboard.isHandlerActive() && this.menu.isOpen();
  }

  /**
   * Destroy all components and clean up resources
   */
  destroy(): void {
    this.manager.destroy();
    this.menu.destroy();
    this.keyboard.destroy();
    this.help.destroy();
  }
}

// Default export for convenience
export default NavigationSystem;