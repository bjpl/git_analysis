/**
 * InteractiveMenu.ts - Main menu controller with sophisticated navigation and interaction
 * Features: Nested menus, keyboard/mouse support, search, history, bookmarks
 */

import {
  MenuItem, MenuConfiguration, MenuState, MenuEventHandlers, MenuPlugin,
  MenuSearchResult, MenuBreadcrumb, MenuContext, MenuPreferences,
  MenuPerformanceMetrics, MenuPath, MenuItemId
} from './types.js';
import { MenuRenderer } from './MenuRenderer.js';
import { MenuStateManager } from './MenuState.js';
import { MenuAnimations } from './MenuAnimations.js';
import { MenuConfigLoader } from './MenuConfig.js';

export class InteractiveMenu {
  private renderer: MenuRenderer;
  private stateManager: MenuStateManager;
  private animations: MenuAnimations;
  private configLoader: MenuConfigLoader;
  private plugins: Map<string, MenuPlugin> = new Map();
  private eventHandlers: MenuEventHandlers = {};
  private performanceMetrics: MenuPerformanceMetrics;
  private keyboardListeners: Map<string, (event: KeyboardEvent) => void> = new Map();
  private mouseListeners: Map<string, (event: MouseEvent) => void> = new Map();
  private searchIndex: Map<string, MenuSearchResult[]> = new Map();
  private isInitialized: boolean = false;

  constructor(
    public config: MenuConfiguration,
    private container?: HTMLElement
  ) {
    this.renderer = new MenuRenderer();
    this.stateManager = new MenuStateManager();
    this.animations = new MenuAnimations();
    this.configLoader = new MenuConfigLoader();
    
    this.performanceMetrics = {
      renderTime: 0,
      searchTime: 0,
      navigationTime: 0,
      memoryUsage: 0,
      itemsProcessed: 0
    };

    this.initialize();
  }

  // ================================
  // Initialization and Setup
  // ================================

  private async initialize(): Promise<void> {
    if (this.isInitialized) return;

    try {
      // Validate configuration
      await this.validateConfiguration();
      
      // Initialize state
      await this.stateManager.initialize();
      
      // Build search index
      this.buildSearchIndex();
      
      // Setup event listeners
      this.setupEventListeners();
      
      // Initialize plugins
      await this.initializePlugins();
      
      // Set initial state
      this.stateManager.setState({
        currentMenuId: this.config.id,
        navigationHistory: [this.config.id],
        bookmarks: [],
        recentItems: [],
        preferences: this.getDefaultPreferences(),
        isLoading: false
      });

      this.isInitialized = true;
      this.emit('initialized', this);
    } catch (error) {
      this.handleError(`Failed to initialize menu: ${error}`);
    }
  }

  private async validateConfiguration(): Promise<void> {
    if (!this.config.id) {
      throw new Error('Menu configuration must have an id');
    }

    if (!this.config.items || this.config.items.length === 0) {
      throw new Error('Menu must have at least one item');
    }

    if (this.config.validation) {
      this.validateMenuItems(this.config.items, 0);
    }
  }

  private validateMenuItems(items: MenuItem[], depth: number): void {
    const validation = this.config.validation!;
    
    if (validation.maxDepth && depth > validation.maxDepth) {
      throw new Error(`Menu depth exceeds maximum of ${validation.maxDepth}`);
    }

    if (validation.maxItems && items.length > validation.maxItems) {
      throw new Error(`Menu items exceed maximum of ${validation.maxItems}`);
    }

    for (const item of items) {
      // Check required fields
      if (validation.requiredFields) {
        for (const field of validation.requiredFields) {
          if (!(field in item) || !item[field as keyof MenuItem]) {
            throw new Error(`Menu item '${item.id}' missing required field: ${field}`);
          }
        }
      }

      // Run custom validators
      if (validation.customValidators) {
        for (const validator of validation.customValidators) {
          if (!validator(item)) {
            throw new Error(`Menu item '${item.id}' failed custom validation`);
          }
        }
      }

      // Recursively validate submenu items
      if (item.submenu) {
        this.validateMenuItems(item.submenu, depth + 1);
      }
    }
  }

  // ================================
  // Navigation and Interaction
  // ================================

  public async navigate(itemId: MenuItemId): Promise<void> {
    const startTime = performance.now();
    
    try {
      const item = this.findMenuItem(itemId);
      if (!item) {
        throw new Error(`Menu item not found: ${itemId}`);
      }

      if (item.disabled) {
        this.emit('itemDisabled', item);
        return;
      }

      // Update navigation history
      const currentState = this.stateManager.getState();
      const newHistory = [...currentState.navigationHistory];
      
      if (newHistory[newHistory.length - 1] !== itemId) {
        newHistory.push(itemId);
        
        // Limit history size
        const maxHistory = currentState.preferences.maxHistoryItems || 50;
        if (newHistory.length > maxHistory) {
          newHistory.shift();
        }
      }

      // Update recent items
      const recentItems = [itemId, ...currentState.recentItems.filter(id => id !== itemId)];
      const maxRecent = currentState.preferences.maxRecentItems || 10;
      
      this.stateManager.updateState({
        selectedItemId: itemId,
        navigationHistory: newHistory,
        recentItems: recentItems.slice(0, maxRecent)
      });

      // Handle item action
      if (item.action) {
        await this.executeItemAction(item);
      }

      // Navigate to submenu if exists
      if (item.submenu && item.submenu.length > 0) {
        await this.openSubmenu(item);
      }

      this.emit('itemSelect', item, this.getCurrentPath());
    } catch (error) {
      this.handleError(`Navigation failed: ${error}`);
    } finally {
      this.performanceMetrics.navigationTime += performance.now() - startTime;
    }
  }

  private async executeItemAction(item: MenuItem): Promise<void> {
    if (typeof item.action === 'string') {
      // Handle string actions (could be commands, URLs, etc.)
      this.emit('actionExecute', item.action, item);
    } else if (typeof item.action === 'function') {
      try {
        await item.action();
      } catch (error) {
        this.handleError(`Action execution failed for '${item.id}': ${error}`);
      }
    }
  }

  private async openSubmenu(parentItem: MenuItem): Promise<void> {
    if (!parentItem.submenu) return;

    const submenuConfig: MenuConfiguration = {
      id: `${this.config.id}-${parentItem.id}-submenu`,
      title: parentItem.title,
      description: parentItem.description,
      items: parentItem.submenu,
      style: this.config.style,
      searchable: this.config.searchable,
      breadcrumbs: this.config.breadcrumbs
    };

    this.stateManager.updateState({
      currentMenuId: submenuConfig.id
    });

    await this.render();
    this.emit('submenuOpen', parentItem, submenuConfig);
  }

  public goBack(): void {
    const state = this.stateManager.getState();
    const history = state.navigationHistory;
    
    if (history.length > 1) {
      const newHistory = history.slice(0, -1);
      const previousMenuId = newHistory[newHistory.length - 1];
      
      this.stateManager.updateState({
        currentMenuId: previousMenuId,
        navigationHistory: newHistory,
        selectedItemId: undefined
      });
      
      this.render();
      this.emit('navigationBack', previousMenuId);
    }
  }

  public goToRoot(): void {
    this.stateManager.updateState({
      currentMenuId: this.config.id,
      navigationHistory: [this.config.id],
      selectedItemId: undefined
    });
    
    this.render();
    this.emit('navigationRoot');
  }

  // ================================
  // Search and Filtering
  // ================================

  public async search(query: string): Promise<MenuSearchResult[]> {
    const startTime = performance.now();
    
    try {
      if (!query.trim()) {
        this.stateManager.updateState({ searchQuery: undefined });
        return [];
      }

      const normalizedQuery = query.toLowerCase().trim();
      let results: MenuSearchResult[] = [];

      // Check cache first
      if (this.searchIndex.has(normalizedQuery)) {
        results = this.searchIndex.get(normalizedQuery)!;
      } else {
        results = this.performSearch(normalizedQuery);
        this.searchIndex.set(normalizedQuery, results);
      }

      this.stateManager.updateState({ searchQuery: query });
      this.emit('searchChange', query, results);
      
      return results;
    } finally {
      this.performanceMetrics.searchTime += performance.now() - startTime;
    }
  }

  private performSearch(query: string): MenuSearchResult[] {
    const results: MenuSearchResult[] = [];
    
    const searchItems = (items: MenuItem[], path: string[] = []): void => {
      for (const item of items) {
        if (item.hidden) continue;
        
        const currentPath = [...path, item.id];
        let relevanceScore = 0;
        let highlightedText = '';
        
        // Search in title
        const titleMatch = item.title.toLowerCase().includes(query);
        if (titleMatch) {
          relevanceScore += 10;
          highlightedText = this.highlightMatch(item.title, query);
        }
        
        // Search in description
        if (item.description) {
          const descMatch = item.description.toLowerCase().includes(query);
          if (descMatch) {
            relevanceScore += 5;
            if (!highlightedText) {
              highlightedText = this.highlightMatch(item.description, query);
            }
          }
        }
        
        // Search in metadata
        if (item.metadata) {
          const metadataText = JSON.stringify(item.metadata).toLowerCase();
          if (metadataText.includes(query)) {
            relevanceScore += 2;
          }
        }
        
        if (relevanceScore > 0) {
          results.push({
            item,
            menuPath: currentPath,
            relevanceScore,
            highlightedText
          });
        }
        
        // Search in submenu items
        if (item.submenu) {
          searchItems(item.submenu, currentPath);
        }
      }
    };
    
    searchItems(this.config.items);
    
    // Sort by relevance score (highest first)
    return results.sort((a, b) => b.relevanceScore - a.relevanceScore);
  }

  private highlightMatch(text: string, query: string): string {
    const regex = new RegExp(`(${query})`, 'gi');
    return text.replace(regex, '**$1**'); // Markdown-style highlighting
  }

  // ================================
  // Event System
  // ================================

  public on<K extends keyof MenuEventHandlers>(event: K, handler: MenuEventHandlers[K]): void {
    if (!this.eventHandlers[event]) {
      this.eventHandlers[event] = handler;
    }
  }

  public off<K extends keyof MenuEventHandlers>(event: K): void {
    delete this.eventHandlers[event];
  }

  private emit<K extends keyof MenuEventHandlers>(event: K, ...args: any[]): void {
    const handler = this.eventHandlers[event];
    if (handler) {
      try {
        (handler as any)(...args);
      } catch (error) {
        console.error(`Error in event handler for '${event}':`, error);
      }
    }
  }

  // ================================
  // Keyboard and Mouse Handling
  // ================================

  private setupEventListeners(): void {
    // Keyboard navigation
    this.addKeyboardListener('ArrowUp', (e) => {
      e.preventDefault();
      this.navigateUp();
    });
    
    this.addKeyboardListener('ArrowDown', (e) => {
      e.preventDefault();
      this.navigateDown();
    });
    
    this.addKeyboardListener('Enter', (e) => {
      e.preventDefault();
      this.selectCurrentItem();
    });
    
    this.addKeyboardListener('Escape', (e) => {
      e.preventDefault();
      this.goBack();
    });
    
    this.addKeyboardListener('Backspace', (e) => {
      if (e.ctrlKey) {
        e.preventDefault();
        this.goToRoot();
      }
    });
    
    // Search shortcut
    this.addKeyboardListener('/', (e) => {
      e.preventDefault();
      this.startSearch();
    });
    
    // Bookmarks
    this.addKeyboardListener('b', (e) => {
      if (e.ctrlKey) {
        e.preventDefault();
        this.toggleBookmark();
      }
    });
  }

  private addKeyboardListener(key: string, handler: (event: KeyboardEvent) => void): void {
    this.keyboardListeners.set(key, handler);
    document.addEventListener('keydown', (e) => {
      if (e.key === key) {
        handler(e);
      }
    });
  }

  private navigateUp(): void {
    // Implementation depends on current menu rendering
    this.emit('navigationUp');
  }

  private navigateDown(): void {
    // Implementation depends on current menu rendering
    this.emit('navigationDown');
  }

  private selectCurrentItem(): void {
    const state = this.stateManager.getState();
    if (state.selectedItemId) {
      this.navigate(state.selectedItemId);
    }
  }

  private startSearch(): void {
    this.emit('searchStart');
  }

  // ================================
  // Bookmarks and Favorites
  // ================================

  public addBookmark(itemId: MenuItemId): void {
    const state = this.stateManager.getState();
    const bookmarks = state.bookmarks;
    
    if (!bookmarks.includes(itemId)) {
      this.stateManager.updateState({
        bookmarks: [...bookmarks, itemId]
      });
      this.emit('bookmarkAdded', itemId);
    }
  }

  public removeBookmark(itemId: MenuItemId): void {
    const state = this.stateManager.getState();
    const bookmarks = state.bookmarks.filter(id => id !== itemId);
    
    this.stateManager.updateState({ bookmarks });
    this.emit('bookmarkRemoved', itemId);
  }

  public toggleBookmark(itemId?: MenuItemId): void {
    const state = this.stateManager.getState();
    const targetId = itemId || state.selectedItemId;
    
    if (!targetId) return;
    
    if (state.bookmarks.includes(targetId)) {
      this.removeBookmark(targetId);
    } else {
      this.addBookmark(targetId);
    }
  }

  public getBookmarks(): MenuItem[] {
    const state = this.stateManager.getState();
    return state.bookmarks
      .map(id => this.findMenuItem(id))
      .filter(item => item !== null) as MenuItem[];
  }

  // ================================
  // Plugin System
  // ================================

  public addPlugin(plugin: MenuPlugin): void {
    if (this.plugins.has(plugin.name)) {
      console.warn(`Plugin '${plugin.name}' is already registered`);
      return;
    }
    
    this.plugins.set(plugin.name, plugin);
    plugin.initialize(this as any);
    this.emit('pluginAdded', plugin);
  }

  public removePlugin(pluginName: string): void {
    const plugin = this.plugins.get(pluginName);
    if (plugin) {
      if (plugin.destroy) {
        plugin.destroy();
      }
      this.plugins.delete(pluginName);
      this.emit('pluginRemoved', plugin);
    }
  }

  private async initializePlugins(): Promise<void> {
    // Auto-load plugins from configuration if specified
    // This could load plugins from the config or discover them
  }

  // ================================
  // Rendering and Display
  // ================================

  public async render(container?: HTMLElement): Promise<void> {
    const startTime = performance.now();
    
    try {
      const targetContainer = container || this.container;
      if (!targetContainer) {
        throw new Error('No container specified for rendering');
      }

      const state = this.stateManager.getState();
      const currentItems = this.getCurrentMenuItems();
      const context = this.buildContext();
      
      // Apply plugin transformations
      const transformedItems = this.applyPluginTransformations(currentItems);
      
      await this.renderer.render({
        items: transformedItems,
        container: targetContainer,
        style: { ...this.getDefaultStyle(), ...this.config.style },
        context,
        animations: this.animations
      });
      
      this.performanceMetrics.itemsProcessed = transformedItems.length;
      this.emit('rendered', transformedItems, context);
    } catch (error) {
      this.handleError(`Rendering failed: ${error}`);
    } finally {
      this.performanceMetrics.renderTime += performance.now() - startTime;
    }
  }

  // ================================
  // Utility Methods
  // ================================

  private findMenuItem(itemId: MenuItemId, items?: MenuItem[]): MenuItem | null {
    const searchItems = items || this.config.items;
    
    for (const item of searchItems) {
      if (item.id === itemId) {
        return item;
      }
      
      if (item.submenu) {
        const found = this.findMenuItem(itemId, item.submenu);
        if (found) {
          return found;
        }
      }
    }
    
    return null;
  }

  private getCurrentMenuItems(): MenuItem[] {
    const state = this.stateManager.getState();
    
    if (state.currentMenuId === this.config.id) {
      return this.config.items;
    }
    
    // Handle submenu items
    // This would need more complex logic to traverse to the current submenu
    return this.config.items;
  }

  private getCurrentPath(): MenuPath {
    const state = this.stateManager.getState();
    return state.navigationHistory;
  }

  private buildContext(): MenuContext {
    const state = this.stateManager.getState();
    
    return {
      currentPath: this.getCurrentPath(),
      selectedItem: state.selectedItemId ? this.findMenuItem(state.selectedItemId) || undefined : undefined,
      searchActive: !!state.searchQuery,
      filterActive: !!state.filterCriteria,
      isNested: state.navigationHistory.length > 1,
      depth: state.navigationHistory.length - 1
    };
  }

  private buildSearchIndex(): void {
    // Pre-build common searches for better performance
    this.searchIndex.clear();
  }

  private applyPluginTransformations(items: MenuItem[]): MenuItem[] {
    let transformedItems = [...items];
    
    for (const plugin of this.plugins.values()) {
      if (plugin.onMenuRender) {
        transformedItems = plugin.onMenuRender(transformedItems);
      }
    }
    
    return transformedItems;
  }

  private getDefaultPreferences(): MenuPreferences {
    return {
      defaultStyle: this.getDefaultStyle(),
      animationsEnabled: true,
      keyboardNavigationEnabled: true,
      mouseNavigationEnabled: true,
      autoSave: true,
      maxHistoryItems: 50,
      maxRecentItems: 10
    };
  }

  private getDefaultStyle(): any {
    return {
      type: 'list',
      theme: 'default',
      showIcons: true,
      showShortcuts: true,
      showDescriptions: true,
      animations: true
    };
  }

  private handleError(message: string): void {
    console.error(`[InteractiveMenu] ${message}`);
    this.stateManager.updateState({ error: message });
    this.emit('error', message);
  }

  // ================================
  // Public API
  // ================================

  public getState(): MenuState {
    return this.stateManager.getState();
  }

  public getConfig(): MenuConfiguration {
    return { ...this.config };
  }

  public getMetrics(): MenuPerformanceMetrics {
    return { ...this.performanceMetrics };
  }

  public async loadConfig(configPath: string): Promise<void> {
    try {
      const newConfig = await this.configLoader.load(configPath);
      this.config = newConfig;
      await this.initialize();
      await this.render();
    } catch (error) {
      this.handleError(`Failed to load config: ${error}`);
    }
  }

  public destroy(): void {
    // Clean up event listeners
    for (const [key, listener] of this.keyboardListeners) {
      document.removeEventListener('keydown', listener);
    }
    
    // Destroy plugins
    for (const plugin of this.plugins.values()) {
      if (plugin.destroy) {
        plugin.destroy();
      }
    }
    
    // Clear state
    this.stateManager.destroy();
    
    this.isInitialized = false;
    this.emit('destroyed');
  }
}

export default InteractiveMenu;
