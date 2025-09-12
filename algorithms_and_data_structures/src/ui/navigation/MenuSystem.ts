/**
 * MenuSystem - Menu rendering and interaction management
 * Handles visual presentation, interaction logic, and menu state
 */

import { EventEmitter } from 'events';
import {
  MenuItem,
  NavigationNode,
  NavigationConfig,
  NavigationTheme,
  BreadcrumbItem,
  FilterOptions,
  SortOptions
} from '../../types/navigation.js';

export interface MenuDisplayOptions {
  showIcons: boolean;
  showShortcuts: boolean;
  showDescriptions: boolean;
  maxWidth?: number;
  maxHeight?: number;
  showBreadcrumbs: boolean;
  showSearchBox: boolean;
  highlightMatches: boolean;
}

export interface MenuState {
  selectedIndex: number;
  scrollOffset: number;
  isOpen: boolean;
  expandedItems: Set<string>;
  searchQuery: string;
  filteredItems: MenuItem[];
  originalItems: MenuItem[];
}

export class MenuSystem extends EventEmitter {
  private config: NavigationConfig;
  private displayOptions: MenuDisplayOptions;
  private state: MenuState;
  private theme: NavigationTheme;

  constructor(
    config: NavigationConfig,
    displayOptions: Partial<MenuDisplayOptions> = {}
  ) {
    super();
    
    this.config = config;
    this.theme = config.theme;
    
    this.displayOptions = {
      showIcons: true,
      showShortcuts: true,
      showDescriptions: true,
      showBreadcrumbs: true,
      showSearchBox: true,
      highlightMatches: true,
      ...displayOptions
    };

    this.state = {
      selectedIndex: 0,
      scrollOffset: 0,
      isOpen: false,
      expandedItems: new Set(),
      searchQuery: '',
      filteredItems: [],
      originalItems: []
    };
  }

  /**
   * Convert navigation nodes to menu items
   */
  nodesToMenuItems(nodes: NavigationNode[]): MenuItem[] {
    return nodes.map(node => this.nodeToMenuItem(node));
  }

  /**
   * Convert a single navigation node to menu item
   */
  private nodeToMenuItem(node: NavigationNode): MenuItem {
    const hasChildren = node.children && node.children.length > 0;
    
    return {
      id: node.id,
      label: node.label,
      description: node.description,
      command: node.command,
      shortcut: node.shortcut ? { key: node.shortcut } : undefined,
      icon: node.icon,
      type: hasChildren ? 'submenu' : (node.command ? 'command' : 'header'),
      children: [], // Children loaded dynamically
      isVisible: node.isVisible,
      isEnabled: node.isEnabled,
      onSelect: () => this.handleItemSelect(node),
      onHover: () => this.handleItemHover(node)
    };
  }

  /**
   * Render menu to string output
   */
  renderMenu(items: MenuItem[], breadcrumbs?: BreadcrumbItem[]): string {
    let output = '';

    // Render breadcrumbs if enabled
    if (this.displayOptions.showBreadcrumbs && breadcrumbs?.length) {
      output += this.renderBreadcrumbs(breadcrumbs) + '\\n\\n';
    }

    // Render search box if enabled
    if (this.displayOptions.showSearchBox) {
      output += this.renderSearchBox() + '\\n';
    }

    // Render menu items
    output += this.renderMenuItems(items);

    // Render help footer
    output += '\\n' + this.renderHelpFooter();

    return output;
  }

  /**
   * Render breadcrumb navigation
   */
  private renderBreadcrumbs(breadcrumbs: BreadcrumbItem[]): string {
    const separator = this.config.breadcrumbSeparator;
    const breadcrumbText = breadcrumbs
      .map((crumb, index) => {
        const isLast = index === breadcrumbs.length - 1;
        const style = isLast ? 
          this.colorize(crumb.label, 'text') : 
          this.colorize(crumb.label, 'textMuted');
        
        return crumb.isClickable && !isLast ? 
          this.makeClickable(style, `nav:${crumb.path}`) : 
          style;
      })
      .join(this.colorize(separator, 'textMuted'));

    return this.colorize('📍 ', 'accent') + breadcrumbText;
  }

  /**
   * Render search box
   */
  private renderSearchBox(): string {
    const searchIcon = this.theme.icons.search;
    const placeholder = this.state.searchQuery || 'Type to search...';
    const box = `${searchIcon} ${placeholder}`;
    
    return this.colorize('─'.repeat(Math.max(box.length + 4, 50)), 'border') + '\\n' +
           this.colorize(`│ ${box}`, 'border') + '\\n' +
           this.colorize('─'.repeat(Math.max(box.length + 4, 50)), 'border');
  }

  /**
   * Render menu items list
   */
  private renderMenuItems(items: MenuItem[]): string {
    if (!items.length) {
      return this.colorize('  No items to display', 'textMuted');
    }

    const visibleItems = items.filter(item => item.isVisible !== false);
    const startIndex = Math.max(0, this.state.scrollOffset);
    const maxDisplayItems = this.displayOptions.maxHeight || 20;
    const displayItems = visibleItems.slice(startIndex, startIndex + maxDisplayItems);

    let output = '';
    
    for (let i = 0; i < displayItems.length; i++) {
      const item = displayItems[i];
      const globalIndex = startIndex + i;
      const isSelected = globalIndex === this.state.selectedIndex;
      
      output += this.renderMenuItem(item, isSelected, globalIndex) + '\\n';
    }

    // Show scroll indicators if needed
    if (startIndex > 0) {
      output = this.colorize('  ▲ More items above', 'textMuted') + '\\n' + output;
    }
    
    if (startIndex + maxDisplayItems < visibleItems.length) {
      output += this.colorize('  ▼ More items below', 'textMuted');
    }

    return output.trimEnd();
  }

  /**
   * Render a single menu item
   */
  private renderMenuItem(item: MenuItem, isSelected: boolean, index: number): string {
    let line = '';
    
    // Selection indicator
    const indicator = isSelected ? '▶' : ' ';
    line += this.colorize(indicator + ' ', isSelected ? 'accent' : 'textMuted');

    // Icon
    if (this.displayOptions.showIcons && item.icon) {
      line += item.icon + ' ';
    } else if (this.displayOptions.showIcons) {
      const defaultIcon = this.getDefaultIcon(item.type);
      line += defaultIcon + ' ';
    }

    // Label with highlighting
    const labelText = this.highlightMatches(item.label, this.state.searchQuery);
    const labelColor = isSelected ? 'selected' : 
                      item.isEnabled === false ? 'disabled' : 'text';
    line += this.colorize(labelText, labelColor);

    // Submenu indicator
    if (item.type === 'submenu') {
      const isExpanded = this.state.expandedItems.has(item.id);
      const expandIcon = isExpanded ? '▼' : '▶';
      line += ' ' + this.colorize(expandIcon, 'textMuted');
    }

    // Shortcut
    if (this.displayOptions.showShortcuts && item.shortcut) {
      const shortcutText = this.formatShortcut(item.shortcut);
      line += ' ' + this.colorize(`(${shortcutText})`, 'textMuted');
    }

    // Description on new line if enabled
    if (this.displayOptions.showDescriptions && item.description && isSelected) {
      const description = this.highlightMatches(item.description, this.state.searchQuery);
      line += '\\n    ' + this.colorize(description, 'textMuted');
    }

    // Background color for selected item
    if (isSelected) {
      line = this.addBackground(line, 'hover');
    }

    return line;
  }

  /**
   * Get default icon for item type
   */
  private getDefaultIcon(type: string): string {
    switch (type) {
      case 'command': return this.theme.icons.command;
      case 'submenu': return this.theme.icons.folder;
      case 'separator': return '─';
      case 'header': return this.theme.icons.file;
      default: return this.theme.icons.file;
    }
  }

  /**
   * Highlight search matches in text
   */
  private highlightMatches(text: string, query: string): string {
    if (!query || !this.displayOptions.highlightMatches) {
      return text;
    }

    const queryLower = query.toLowerCase();
    const textLower = text.toLowerCase();
    const index = textLower.indexOf(queryLower);
    
    if (index === -1) return text;

    const before = text.substring(0, index);
    const match = text.substring(index, index + query.length);
    const after = text.substring(index + query.length);
    
    return before + this.colorize(match, 'accent') + after;
  }

  /**
   * Format keyboard shortcut for display
   */
  private formatShortcut(shortcut: any): string {
    const parts = [];
    
    if (shortcut.ctrl) parts.push('Ctrl');
    if (shortcut.alt) parts.push('Alt');
    if (shortcut.shift) parts.push('Shift');
    if (shortcut.meta) parts.push('Cmd');
    
    parts.push(shortcut.key);
    
    return parts.join('+');
  }

  /**
   * Render help footer
   */
  private renderHelpFooter(): string {
    const shortcuts = [
      '↑↓ Navigate',
      'Enter Select',
      'Esc Back',
      'Ctrl+/ Search',
      'F1 Help'
    ];

    const helpText = shortcuts
      .map(shortcut => this.colorize(shortcut, 'textMuted'))
      .join('  │  ');

    return this.colorize('─'.repeat(60), 'border') + '\\n' +
           this.colorize(helpText, 'textMuted');
  }

  /**
   * Handle menu item selection
   */
  private handleItemSelect(node: NavigationNode): void {
    this.emit('item-selected', {
      node,
      index: this.state.selectedIndex,
      timestamp: Date.now()
    });
  }

  /**
   * Handle menu item hover
   */
  private handleItemHover(node: NavigationNode): void {
    this.emit('item-hovered', {
      node,
      index: this.state.selectedIndex,
      timestamp: Date.now()
    });
  }

  /**
   * Navigate menu selection
   */
  navigateUp(): void {
    if (this.state.selectedIndex > 0) {
      this.state.selectedIndex--;
      this.updateScrollPosition();
      this.emit('selection-changed', this.state.selectedIndex);
    }
  }

  navigateDown(): void {
    const maxIndex = this.state.filteredItems.length - 1;
    if (this.state.selectedIndex < maxIndex) {
      this.state.selectedIndex++;
      this.updateScrollPosition();
      this.emit('selection-changed', this.state.selectedIndex);
    }
  }

  /**
   * Update scroll position based on selection
   */
  private updateScrollPosition(): void {
    const maxDisplayItems = this.displayOptions.maxHeight || 20;
    const selectedIndex = this.state.selectedIndex;
    
    // Scroll down if selection is below visible area
    if (selectedIndex >= this.state.scrollOffset + maxDisplayItems) {
      this.state.scrollOffset = selectedIndex - maxDisplayItems + 1;
    }
    
    // Scroll up if selection is above visible area
    if (selectedIndex < this.state.scrollOffset) {
      this.state.scrollOffset = selectedIndex;
    }
  }

  /**
   * Select current menu item
   */
  selectCurrent(): void {
    const selectedItem = this.state.filteredItems[this.state.selectedIndex];
    if (selectedItem?.onSelect) {
      selectedItem.onSelect();
    }
  }

  /**
   * Toggle submenu expansion
   */
  toggleExpansion(itemId: string): void {
    if (this.state.expandedItems.has(itemId)) {
      this.state.expandedItems.delete(itemId);
    } else {
      this.state.expandedItems.add(itemId);
    }
    this.emit('expansion-changed', { itemId, expanded: this.state.expandedItems.has(itemId) });
  }

  /**
   * Update search query and filter items
   */
  updateSearch(query: string): void {
    this.state.searchQuery = query;
    this.filterItems();
    this.state.selectedIndex = 0;
    this.state.scrollOffset = 0;
    this.emit('search-updated', query);
  }

  /**
   * Filter menu items based on search query
   */
  private filterItems(): void {
    const query = this.state.searchQuery.toLowerCase();
    
    if (!query) {
      this.state.filteredItems = [...this.state.originalItems];
      return;
    }

    this.state.filteredItems = this.state.originalItems.filter(item => {
      const labelMatch = item.label.toLowerCase().includes(query);
      const descriptionMatch = item.description?.toLowerCase().includes(query);
      const commandMatch = item.command?.toLowerCase().includes(query);
      
      return labelMatch || descriptionMatch || commandMatch;
    });
  }

  /**
   * Set menu items
   */
  setItems(items: MenuItem[]): void {
    this.state.originalItems = items;
    this.state.filteredItems = [...items];
    this.state.selectedIndex = 0;
    this.state.scrollOffset = 0;
    this.emit('items-changed', items);
  }

  /**
   * Apply color to text
   */
  private colorize(text: string, colorKey: keyof NavigationTheme['colors']): string {
    const color = this.theme.colors[colorKey];
    // In a real CLI, this would apply ANSI color codes
    // For now, return the text as-is
    return text;
  }

  /**
   * Add background color to text
   */
  private addBackground(text: string, colorKey: keyof NavigationTheme['colors']): string {
    // In a real CLI, this would apply ANSI background codes
    return text;
  }

  /**
   * Make text clickable (for future mouse support)
   */
  private makeClickable(text: string, action: string): string {
    // Future implementation for mouse support
    return text;
  }

  /**
   * Open menu
   */
  open(): void {
    this.state.isOpen = true;
    this.emit('menu-opened');
  }

  /**
   * Close menu
   */
  close(): void {
    this.state.isOpen = false;
    this.state.selectedIndex = 0;
    this.state.scrollOffset = 0;
    this.state.searchQuery = '';
    this.emit('menu-closed');
  }

  /**
   * Check if menu is open
   */
  isOpen(): boolean {
    return this.state.isOpen;
  }

  /**
   * Get current menu state
   */
  getState(): MenuState {
    return { ...this.state };
  }

  /**
   * Update display options
   */
  updateDisplayOptions(options: Partial<MenuDisplayOptions>): void {
    this.displayOptions = { ...this.displayOptions, ...options };
    this.emit('display-options-updated', this.displayOptions);
  }

  /**
   * Get current display options
   */
  getDisplayOptions(): MenuDisplayOptions {
    return { ...this.displayOptions };
  }

  /**
   * Clear menu state
   */
  clear(): void {
    this.state.originalItems = [];
    this.state.filteredItems = [];
    this.state.selectedIndex = 0;
    this.state.scrollOffset = 0;
    this.state.searchQuery = '';
    this.state.expandedItems.clear();
    this.emit('menu-cleared');
  }

  /**
   * Destroy menu system
   */
  destroy(): void {
    this.clear();
    this.removeAllListeners();
  }
}