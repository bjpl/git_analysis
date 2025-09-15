/**
 * NavigationManager - Core navigation logic and state management
 * Handles routing, state transitions, and coordination between navigation components
 */

import { EventEmitter } from 'events';
import {
  NavigationNode,
  NavigationState,
  NavigationConfig,
  CommandRoute,
  NavigationEvent,
  NavigationEventHandler,
  BreadcrumbItem,
  FilterOptions,
  SortOptions,
  NavigationError,
  CommandNotFoundError,
  InvalidRouteError
} from '../../types/navigation.js';

export class NavigationManager extends EventEmitter {
  private nodes: Map<string, NavigationNode> = new Map();
  private routes: Map<string, CommandRoute> = new Map();
  private state: NavigationState;
  private config: NavigationConfig;
  private eventHandlers: Map<string, NavigationEventHandler[]> = new Map();

  constructor(config: Partial<NavigationConfig> = {}) {
    super();
    
    this.config = {
      maxHistorySize: 100,
      searchDebounceMs: 200,
      fuzzySearchThreshold: 0.3,
      breadcrumbSeparator: ' › ',
      enableAnimations: true,
      keyBindings: {
        'navigate-back': { key: 'ArrowLeft', alt: true, description: 'Navigate back' },
        'navigate-forward': { key: 'ArrowRight', alt: true, description: 'Navigate forward' },
        'search': { key: '/', ctrl: true, description: 'Open search' },
        'help': { key: 'F1', description: 'Show help' },
        'home': { key: 'Home', description: 'Go to root' },
        'escape': { key: 'Escape', description: 'Cancel current action' }
      },
      theme: {
        colors: {
          primary: '#007acc',
          secondary: '#6c757d',
          accent: '#28a745',
          background: '#1e1e1e',
          text: '#d4d4d4',
          textMuted: '#868e96',
          border: '#454545',
          hover: '#2d2d30',
          selected: '#094771',
          disabled: '#6c757d'
        },
        icons: {
          folder: '📁',
          file: '📄',
          command: '⚡',
          shortcut: '⌨️',
          search: '🔍',
          help: '❓',
          back: '←',
          forward: '→',
          home: '🏠'
        }
      },
      ...config
    };

    this.state = {
      currentPath: [],
      history: [],
      breadcrumbs: [],
      isSearchMode: false,
      isHelpMode: false
    };

    this.initializeDefaultRoutes();
  }

  /**
   * Initialize default command routes
   */
  private initializeDefaultRoutes(): void {
    const defaultRoutes: CommandRoute[] = [
      {
        pattern: /^help(?:\s+(.+))?$/,
        handler: 'showHelp',
        parameters: [
          { name: 'topic', type: 'string', required: false, description: 'Help topic' }
        ],
        description: 'Show help information'
      },
      {
        pattern: /^search\s+(.+)$/,
        handler: 'executeSearch',
        parameters: [
          { name: 'query', type: 'string', required: true, description: 'Search query' }
        ],
        description: 'Search for commands or content'
      },
      {
        pattern: /^cd(?:\s+(.+))?$/,
        handler: 'navigateToPath',
        parameters: [
          { name: 'path', type: 'string', required: false, description: 'Path to navigate to' }
        ],
        description: 'Change current directory/context'
      },
      {
        pattern: /^back$/,
        handler: 'navigateBack',
        description: 'Navigate to previous location'
      },
      {
        pattern: /^forward$/,
        handler: 'navigateForward',
        description: 'Navigate to next location'
      },
      {
        pattern: /^home$/,
        handler: 'navigateToHome',
        description: 'Navigate to root/home'
      }
    ];

    defaultRoutes.forEach(route => this.addRoute(route));
  }

  /**
   * Add a navigation node to the system
   */
  addNode(node: NavigationNode): void {
    this.nodes.set(node.id, { 
      isVisible: true, 
      isEnabled: true, 
      weight: 0,
      ...node 
    });

    // Update parent-child relationships
    if (node.parent) {
      const parent = this.nodes.get(node.parent);
      if (parent) {
        parent.children = parent.children || [];
        if (!parent.children.includes(node.id)) {
          parent.children.push(node.id);
        }
      }
    }

    this.emit('node-added', node);
  }

  /**
   * Remove a navigation node
   */
  removeNode(nodeId: string): boolean {
    const node = this.nodes.get(nodeId);
    if (!node) return false;

    // Remove from parent's children
    if (node.parent) {
      const parent = this.nodes.get(node.parent);
      if (parent?.children) {
        parent.children = parent.children.filter(id => id !== nodeId);
      }
    }

    // Remove children recursively
    if (node.children) {
      node.children.forEach(childId => this.removeNode(childId));
    }

    this.nodes.delete(nodeId);
    this.emit('node-removed', nodeId);
    return true;
  }

  /**
   * Get a navigation node by ID
   */
  getNode(nodeId: string): NavigationNode | undefined {
    return this.nodes.get(nodeId);
  }

  /**
   * Get all child nodes of a parent
   */
  getChildren(parentId?: string): NavigationNode[] {
    if (!parentId) {
      // Return root nodes
      return Array.from(this.nodes.values()).filter(node => !node.parent);
    }

    const parent = this.nodes.get(parentId);
    if (!parent?.children) return [];

    return parent.children
      .map(childId => this.nodes.get(childId))
      .filter((node): node is NavigationNode => node !== undefined)
      .filter(node => node.isVisible)
      .sort((a, b) => (b.weight || 0) - (a.weight || 0));
  }

  /**
   * Add a command route
   */
  addRoute(route: CommandRoute): void {
    const key = typeof route.pattern === 'string' ? route.pattern : route.pattern.source;
    this.routes.set(key, route);
    this.emit('route-added', route);
  }

  /**
   * Execute a command through routing system
   */
  async executeCommand(command: string): Promise<any> {
    const route = this.findRoute(command);
    if (!route) {
      throw new CommandNotFoundError(command);
    }

    const event: NavigationEvent = {
      type: 'select',
      data: { command, route },
      timestamp: Date.now(),
      source: 'programmatic'
    };

    this.emitNavigationEvent(event);
    return this.handleRoute(route, command);
  }

  /**
   * Find matching route for command
   */
  private findRoute(command: string): CommandRoute | null {
    for (const [, route] of this.routes) {
      if (typeof route.pattern === 'string') {
        if (route.pattern === command) return route;
      } else if (route.pattern.test(command)) {
        return route;
      }
    }
    return null;
  }

  /**
   * Handle route execution
   */
  private async handleRoute(route: CommandRoute, command: string): Promise<any> {
    // Extract parameters if pattern is regex
    let parameters: any = {};
    if (route.pattern instanceof RegExp) {
      const match = command.match(route.pattern);
      if (match && route.parameters) {
        route.parameters.forEach((param, index) => {
          parameters[param.name] = match[index + 1];
        });
      }
    }

    // Execute middleware if any
    if (route.middleware) {
      for (const middleware of route.middleware) {
        await this.executeMiddleware(middleware, parameters);
      }
    }

    // Execute handler
    return this.executeHandler(route.handler, parameters);
  }

  /**
   * Execute middleware function
   */
  private async executeMiddleware(middleware: string, parameters: any): Promise<void> {
    // Middleware execution logic - can be extended
    console.log(`Executing middleware: ${middleware}`, parameters);
  }

  /**
   * Execute route handler
   */
  private async executeHandler(handler: string, parameters: any): Promise<any> {
    switch (handler) {
      case 'showHelp':
        return this.showHelp(parameters.topic);
      case 'executeSearch':
        return this.executeSearch(parameters.query);
      case 'navigateToPath':
        return this.navigateToPath(parameters.path || '');
      case 'navigateBack':
        return this.navigateBack();
      case 'navigateForward':
        return this.navigateForward();
      case 'navigateToHome':
        return this.navigateToHome();
      default:
        throw new NavigationError(`Unknown handler: ${handler}`, 'UNKNOWN_HANDLER');
    }
  }

  /**
   * Navigate to a specific path
   */
  navigateToPath(path: string): void {
    const pathArray = path ? path.split('/').filter(p => p) : [];
    const previousPath = [...this.state.currentPath];
    
    this.state.currentPath = pathArray;
    this.updateHistory(pathArray.join('/'));
    this.updateBreadcrumbs();

    const event: NavigationEvent = {
      type: 'navigate',
      data: { from: previousPath, to: pathArray },
      timestamp: Date.now(),
      source: 'programmatic'
    };

    this.emitNavigationEvent(event);
  }

  /**
   * Navigate back in history
   */
  navigateBack(): void {
    if (this.state.history.length > 1) {
      const currentIndex = this.state.history.length - 1;
      const previousPath = this.state.history[currentIndex - 1];
      this.navigateToPath(previousPath);
    }
  }

  /**
   * Navigate forward in history
   */
  navigateForward(): void {
    // Implementation for forward navigation
    // This would require tracking forward history separately
    console.log('Forward navigation not yet implemented');
  }

  /**
   * Navigate to home/root
   */
  navigateToHome(): void {
    this.navigateToPath('');
  }

  /**
   * Update navigation history
   */
  private updateHistory(path: string): void {
    // Avoid duplicate consecutive entries
    if (this.state.history[this.state.history.length - 1] !== path) {
      this.state.history.push(path);
      
      // Limit history size
      if (this.state.history.length > this.config.maxHistorySize) {
        this.state.history = this.state.history.slice(-this.config.maxHistorySize);
      }
    }
  }

  /**
   * Update breadcrumb navigation
   */
  private updateBreadcrumbs(): void {
    const breadcrumbs: BreadcrumbItem[] = [];
    
    // Add root breadcrumb
    breadcrumbs.push({
      id: 'root',
      label: 'Home',
      path: '',
      isClickable: true
    });

    // Add path breadcrumbs
    let currentPath = '';
    for (let i = 0; i < this.state.currentPath.length; i++) {
      const segment = this.state.currentPath[i];
      currentPath = currentPath ? `${currentPath}/${segment}` : segment;
      
      const node = this.findNodeByPath(currentPath);
      breadcrumbs.push({
        id: node?.id || `path-${i}`,
        label: node?.label || segment,
        path: currentPath,
        isClickable: i < this.state.currentPath.length - 1
      });
    }

    this.state.breadcrumbs = breadcrumbs;
  }

  /**
   * Find node by path
   */
  private findNodeByPath(path: string): NavigationNode | undefined {
    // Simple path-to-node mapping - can be enhanced
    return Array.from(this.nodes.values()).find(node => 
      node.command === path || node.id === path
    );
  }

  /**
   * Execute search
   */
  executeSearch(query: string): NavigationNode[] {
    const results: NavigationNode[] = [];
    const queryLower = query.toLowerCase();

    for (const node of this.nodes.values()) {
      if (!node.isVisible) continue;

      const labelMatch = node.label.toLowerCase().includes(queryLower);
      const descriptionMatch = node.description?.toLowerCase().includes(queryLower);
      const commandMatch = node.command?.toLowerCase().includes(queryLower);
      const tagMatch = node.tags?.some(tag => tag.toLowerCase().includes(queryLower));

      if (labelMatch || descriptionMatch || commandMatch || tagMatch) {
        results.push(node);
      }
    }

    return results.sort((a, b) => (b.weight || 0) - (a.weight || 0));
  }

  /**
   * Show help information
   */
  showHelp(topic?: string): any {
    if (topic) {
      const node = this.nodes.get(topic) || 
                   Array.from(this.nodes.values()).find(n => 
                     n.label.toLowerCase() === topic.toLowerCase()
                   );
      
      return {
        topic,
        node,
        available: !!node
      };
    }

    return {
      availableCommands: Array.from(this.routes.keys()),
      shortcuts: Object.values(this.config.keyBindings),
      currentContext: this.getCurrentContext()
    };
  }

  /**
   * Get current navigation context
   */
  getCurrentContext(): any {
    const currentNodeId = this.state.currentPath[this.state.currentPath.length - 1];
    const currentNode = currentNodeId ? this.nodes.get(currentNodeId) : null;
    const children = this.getChildren(currentNodeId);

    return {
      path: this.state.currentPath,
      node: currentNode,
      children,
      breadcrumbs: this.state.breadcrumbs
    };
  }

  /**
   * Filter nodes based on criteria
   */
  filterNodes(filter: FilterOptions): NavigationNode[] {
    return Array.from(this.nodes.values()).filter(node => {
      if (filter.categories && !filter.categories.includes(node.category || '')) {
        return false;
      }
      
      if (filter.tags && !node.tags?.some(tag => filter.tags!.includes(tag))) {
        return false;
      }
      
      if (filter.enabled !== undefined && node.isEnabled !== filter.enabled) {
        return false;
      }
      
      if (filter.visible !== undefined && node.isVisible !== filter.visible) {
        return false;
      }
      
      if (filter.hasCommand !== undefined && (!!node.command) !== filter.hasCommand) {
        return false;
      }
      
      if (filter.hasShortcut !== undefined && (!!node.shortcut) !== filter.hasShortcut) {
        return false;
      }

      return true;
    });
  }

  /**
   * Sort nodes based on criteria
   */
  sortNodes(nodes: NavigationNode[], sort: SortOptions): NavigationNode[] {
    return [...nodes].sort((a, b) => {
      let comparison = 0;
      
      switch (sort.field) {
        case 'label':
          comparison = a.label.localeCompare(b.label);
          break;
        case 'weight':
          comparison = (a.weight || 0) - (b.weight || 0);
          break;
        case 'alphabetical':
          comparison = a.label.localeCompare(b.label);
          break;
        default:
          comparison = 0;
      }

      return sort.direction === 'desc' ? -comparison : comparison;
    });
  }

  /**
   * Emit navigation event
   */
  private emitNavigationEvent(event: NavigationEvent): void {
    this.emit('navigation-event', event);
    
    // Call registered handlers
    const handlers = this.eventHandlers.get(event.type) || [];
    handlers.forEach(handler => handler(event));
  }

  /**
   * Register event handler
   */
  onNavigationEvent(type: string, handler: NavigationEventHandler): void {
    if (!this.eventHandlers.has(type)) {
      this.eventHandlers.set(type, []);
    }
    this.eventHandlers.get(type)!.push(handler);
  }

  /**
   * Get current state
   */
  getState(): NavigationState {
    return { ...this.state };
  }

  /**
   * Get configuration
   */
  getConfig(): NavigationConfig {
    return { ...this.config };
  }

  /**
   * Update configuration
   */
  updateConfig(config: Partial<NavigationConfig>): void {
    this.config = { ...this.config, ...config };
    this.emit('config-updated', this.config);
  }

  /**
   * Reset navigation state
   */
  reset(): void {
    this.state = {
      currentPath: [],
      history: [],
      breadcrumbs: [],
      isSearchMode: false,
      isHelpMode: false
    };
    this.emit('navigation-reset');
  }

  /**
   * Destroy navigation manager and clean up resources
   */
  destroy(): void {
    this.nodes.clear();
    this.routes.clear();
    this.eventHandlers.clear();
    this.removeAllListeners();
  }
}