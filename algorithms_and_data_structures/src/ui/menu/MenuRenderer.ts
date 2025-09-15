/**
 * MenuRenderer.ts - Visual rendering engine for interactive menus
 * Features: Multiple styles, smooth scrolling, icons, themes, responsive layout
 */

import {
  MenuItem, MenuStyle, MenuRenderOptions, MenuContext, MenuIcon,
  MenuTransition, MenuAnimation
} from './types.js';
import { MenuAnimations } from './MenuAnimations.js';

interface RenderContext {
  items: MenuItem[];
  container: HTMLElement;
  style: MenuStyle;
  context: MenuContext;
  animations?: MenuAnimations;
}

export class MenuRenderer {
  private currentContainer?: HTMLElement;
  private scrollPosition: number = 0;
  private selectedIndex: number = 0;
  private itemElements: Map<string, HTMLElement> = new Map();
  private resizeObserver?: ResizeObserver;
  private intersectionObserver?: IntersectionObserver;
  private virtualScrolling: boolean = false;
  private itemHeight: number = 40; // Default item height
  private visibleRange: { start: number; end: number } = { start: 0, end: 20 };

  constructor() {
    this.setupObservers();
  }

  // ================================
  // Main Rendering Methods
  // ================================

  public async render(context: RenderContext): Promise<void> {
    const { items, container, style, context: menuContext, animations } = context;
    
    this.currentContainer = container;
    
    // Clear previous content
    container.innerHTML = '';
    this.itemElements.clear();
    
    // Create main menu container
    const menuContainer = this.createMenuContainer(style);
    container.appendChild(menuContainer);
    
    // Render based on style type
    switch (style.type) {
      case 'list':
        await this.renderListStyle(menuContainer, items, style, menuContext, animations);
        break;
      case 'grid':
        await this.renderGridStyle(menuContainer, items, style, menuContext, animations);
        break;
      case 'tree':
        await this.renderTreeStyle(menuContainer, items, style, menuContext, animations);
        break;
      case 'cards':
        await this.renderCardsStyle(menuContainer, items, style, menuContext, animations);
        break;
      default:
        await this.renderListStyle(menuContainer, items, style, menuContext, animations);
    }
    
    // Setup virtual scrolling for large lists
    if (items.length > 100) {
      this.setupVirtualScrolling(menuContainer, items, style);
    }
    
    // Apply theme
    this.applyTheme(menuContainer, style.theme);
    
    // Setup responsive behavior
    this.setupResponsiveLayout(menuContainer, style);
    
    // Initialize scroll position
    this.restoreScrollPosition(menuContainer);
  }

  // ================================
  // Style-specific Rendering
  // ================================

  private async renderListStyle(
    container: HTMLElement,
    items: MenuItem[],
    style: MenuStyle,
    context: MenuContext,
    animations?: MenuAnimations
  ): Promise<void> {
    const listElement = document.createElement('div');
    listElement.className = 'menu-list';
    
    if (style.maxHeight) {
      listElement.style.maxHeight = `${style.maxHeight}px`;
      listElement.style.overflowY = 'auto';
      listElement.style.scrollBehavior = 'smooth';
    }
    
    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      if (item.hidden) continue;
      
      const itemElement = await this.createListItem(item, style, context, i);
      
      // Apply entrance animation
      if (animations && style.animations) {
        await animations.animateItemEntrance(itemElement, i * 50); // Staggered animation
      }
      
      listElement.appendChild(itemElement);
      this.itemElements.set(item.id, itemElement);
    }
    
    container.appendChild(listElement);
  }

  private async renderGridStyle(
    container: HTMLElement,
    items: MenuItem[],
    style: MenuStyle,
    context: MenuContext,
    animations?: MenuAnimations
  ): Promise<void> {
    const gridElement = document.createElement('div');
    gridElement.className = 'menu-grid';
    
    const itemsPerRow = style.itemsPerRow || 3;
    gridElement.style.display = 'grid';
    gridElement.style.gridTemplateColumns = `repeat(${itemsPerRow}, 1fr)`;
    gridElement.style.gap = '12px';
    gridElement.style.padding = '16px';
    
    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      if (item.hidden) continue;
      
      const itemElement = await this.createGridItem(item, style, context);
      
      if (animations && style.animations) {
        await animations.animateItemEntrance(itemElement, i * 30);
      }
      
      gridElement.appendChild(itemElement);
      this.itemElements.set(item.id, itemElement);
    }
    
    container.appendChild(gridElement);
  }

  private async renderTreeStyle(
    container: HTMLElement,
    items: MenuItem[],
    style: MenuStyle,
    context: MenuContext,
    animations?: MenuAnimations
  ): Promise<void> {
    const treeElement = document.createElement('div');
    treeElement.className = 'menu-tree';
    
    await this.renderTreeItems(treeElement, items, style, context, 0, animations);
    container.appendChild(treeElement);
  }

  private async renderTreeItems(
    container: HTMLElement,
    items: MenuItem[],
    style: MenuStyle,
    context: MenuContext,
    depth: number,
    animations?: MenuAnimations
  ): Promise<void> {
    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      if (item.hidden) continue;
      
      const itemElement = await this.createTreeItem(item, style, context, depth);
      
      if (animations && style.animations) {
        await animations.animateItemEntrance(itemElement, i * 25);
      }
      
      container.appendChild(itemElement);
      this.itemElements.set(item.id, itemElement);
      
      // Render submenu items
      if (item.submenu && item.submenu.length > 0) {
        const submenuContainer = document.createElement('div');
        submenuContainer.className = 'menu-tree-submenu';
        submenuContainer.style.marginLeft = '20px';
        submenuContainer.style.borderLeft = '2px solid var(--border-color, #e2e8f0)';
        submenuContainer.style.paddingLeft = '12px';
        
        await this.renderTreeItems(submenuContainer, item.submenu, style, context, depth + 1, animations);
        container.appendChild(submenuContainer);
      }
    }
  }

  private async renderCardsStyle(
    container: HTMLElement,
    items: MenuItem[],
    style: MenuStyle,
    context: MenuContext,
    animations?: MenuAnimations
  ): Promise<void> {
    const cardsContainer = document.createElement('div');
    cardsContainer.className = 'menu-cards';
    cardsContainer.style.display = 'flex';
    cardsContainer.style.flexWrap = 'wrap';
    cardsContainer.style.gap = '16px';
    cardsContainer.style.padding = '16px';
    
    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      if (item.hidden) continue;
      
      const cardElement = await this.createCardItem(item, style, context);
      
      if (animations && style.animations) {
        await animations.animateItemEntrance(cardElement, i * 40);
      }
      
      cardsContainer.appendChild(cardElement);
      this.itemElements.set(item.id, cardElement);
    }
    
    container.appendChild(cardsContainer);
  }

  // ================================
  // Item Creation Methods
  // ================================

  private async createListItem(
    item: MenuItem,
    style: MenuStyle,
    context: MenuContext,
    index: number
  ): Promise<HTMLElement> {
    const itemElement = document.createElement('div');
    itemElement.className = 'menu-item menu-item-list';
    itemElement.setAttribute('data-item-id', item.id);
    itemElement.setAttribute('data-index', index.toString());
    
    // Apply disabled state
    if (item.disabled) {
      itemElement.classList.add('menu-item-disabled');
      itemElement.setAttribute('aria-disabled', 'true');
    }
    
    // Create item layout
    const layout = document.createElement('div');
    layout.className = 'menu-item-layout';
    layout.style.display = 'flex';
    layout.style.alignItems = 'center';
    layout.style.padding = '8px 16px';
    layout.style.cursor = item.disabled ? 'not-allowed' : 'pointer';
    layout.style.transition = 'all 0.2s ease';
    
    // Icon
    if (style.showIcons && item.icon) {
      const iconElement = this.createIcon(item.icon);
      iconElement.style.marginRight = '12px';
      layout.appendChild(iconElement);
    }
    
    // Content area
    const contentArea = document.createElement('div');
    contentArea.className = 'menu-item-content';
    contentArea.style.flex = '1';
    
    // Title
    const titleElement = document.createElement('div');
    titleElement.className = 'menu-item-title';
    titleElement.textContent = item.title;
    titleElement.style.fontWeight = '500';
    titleElement.style.fontSize = '14px';
    contentArea.appendChild(titleElement);
    
    // Description
    if (style.showDescriptions && item.description) {
      const descElement = document.createElement('div');
      descElement.className = 'menu-item-description';
      descElement.textContent = item.description;
      descElement.style.fontSize = '12px';
      descElement.style.opacity = '0.7';
      descElement.style.marginTop = '2px';
      contentArea.appendChild(descElement);
    }
    
    layout.appendChild(contentArea);
    
    // Badge
    if (item.badge) {
      const badgeElement = this.createBadge(item.badge);
      badgeElement.style.marginLeft = '8px';
      layout.appendChild(badgeElement);
    }
    
    // Shortcut
    if (style.showShortcuts && item.shortcut) {
      const shortcutElement = this.createShortcut(item.shortcut);
      shortcutElement.style.marginLeft = '8px';
      layout.appendChild(shortcutElement);
    }
    
    // Submenu indicator
    if (item.submenu && item.submenu.length > 0) {
      const indicator = document.createElement('span');
      indicator.className = 'submenu-indicator';
      indicator.textContent = '▶';
      indicator.style.marginLeft = '8px';
      indicator.style.fontSize = '10px';
      indicator.style.opacity = '0.6';
      layout.appendChild(indicator);
    }
    
    itemElement.appendChild(layout);
    
    // Add hover effects
    this.addItemInteractivity(itemElement, item);
    
    return itemElement;
  }

  private async createGridItem(
    item: MenuItem,
    style: MenuStyle,
    context: MenuContext
  ): Promise<HTMLElement> {
    const itemElement = document.createElement('div');
    itemElement.className = 'menu-item menu-item-grid';
    itemElement.setAttribute('data-item-id', item.id);
    
    itemElement.style.display = 'flex';
    itemElement.style.flexDirection = 'column';
    itemElement.style.alignItems = 'center';
    itemElement.style.padding = '16px';
    itemElement.style.border = '1px solid var(--border-color, #e2e8f0)';
    itemElement.style.borderRadius = '8px';
    itemElement.style.cursor = item.disabled ? 'not-allowed' : 'pointer';
    itemElement.style.transition = 'all 0.2s ease';
    
    if (item.disabled) {
      itemElement.classList.add('menu-item-disabled');
      itemElement.style.opacity = '0.5';
    }
    
    // Icon (larger for grid)
    if (item.icon) {
      const iconElement = this.createIcon(item.icon);
      iconElement.style.fontSize = '24px';
      iconElement.style.marginBottom = '8px';
      itemElement.appendChild(iconElement);
    }
    
    // Title
    const titleElement = document.createElement('div');
    titleElement.className = 'menu-item-title';
    titleElement.textContent = item.title;
    titleElement.style.fontWeight = '500';
    titleElement.style.fontSize = '14px';
    titleElement.style.textAlign = 'center';
    titleElement.style.marginBottom = '4px';
    itemElement.appendChild(titleElement);
    
    // Description (truncated)
    if (item.description) {
      const descElement = document.createElement('div');
      descElement.className = 'menu-item-description';
      descElement.textContent = item.description.length > 50 
        ? item.description.substring(0, 47) + '...' 
        : item.description;
      descElement.style.fontSize = '12px';
      descElement.style.opacity = '0.7';
      descElement.style.textAlign = 'center';
      itemElement.appendChild(descElement);
    }
    
    // Badge
    if (item.badge) {
      const badgeElement = this.createBadge(item.badge);
      badgeElement.style.position = 'absolute';
      badgeElement.style.top = '8px';
      badgeElement.style.right = '8px';
      itemElement.style.position = 'relative';
      itemElement.appendChild(badgeElement);
    }
    
    this.addItemInteractivity(itemElement, item);
    
    return itemElement;
  }

  private async createTreeItem(
    item: MenuItem,
    style: MenuStyle,
    context: MenuContext,
    depth: number
  ): Promise<HTMLElement> {
    const itemElement = document.createElement('div');
    itemElement.className = 'menu-item menu-item-tree';
    itemElement.setAttribute('data-item-id', item.id);
    itemElement.setAttribute('data-depth', depth.toString());
    
    const layout = document.createElement('div');
    layout.style.display = 'flex';
    layout.style.alignItems = 'center';
    layout.style.padding = '4px 8px';
    layout.style.cursor = item.disabled ? 'not-allowed' : 'pointer';
    
    // Depth indentation
    if (depth > 0) {
      layout.style.paddingLeft = `${8 + (depth * 16)}px`;
    }
    
    // Expand/collapse indicator for items with submenus
    if (item.submenu && item.submenu.length > 0) {
      const expandIndicator = document.createElement('span');
      expandIndicator.className = 'expand-indicator';
      expandIndicator.textContent = '▼';
      expandIndicator.style.fontSize = '10px';
      expandIndicator.style.marginRight = '6px';
      expandIndicator.style.cursor = 'pointer';
      layout.appendChild(expandIndicator);
    }
    
    // Icon
    if (item.icon) {
      const iconElement = this.createIcon(item.icon);
      iconElement.style.marginRight = '8px';
      iconElement.style.fontSize = '12px';
      layout.appendChild(iconElement);
    }
    
    // Title
    const titleElement = document.createElement('span');
    titleElement.className = 'menu-item-title';
    titleElement.textContent = item.title;
    titleElement.style.fontSize = '13px';
    titleElement.style.fontWeight = depth === 0 ? '500' : '400';
    layout.appendChild(titleElement);
    
    itemElement.appendChild(layout);
    this.addItemInteractivity(itemElement, item);
    
    return itemElement;
  }

  private async createCardItem(
    item: MenuItem,
    style: MenuStyle,
    context: MenuContext
  ): Promise<HTMLElement> {
    const cardElement = document.createElement('div');
    cardElement.className = 'menu-item menu-item-card';
    cardElement.setAttribute('data-item-id', item.id);
    
    cardElement.style.display = 'flex';
    cardElement.style.flexDirection = 'column';
    cardElement.style.width = '200px';
    cardElement.style.minHeight = '120px';
    cardElement.style.padding = '16px';
    cardElement.style.border = '1px solid var(--border-color, #e2e8f0)';
    cardElement.style.borderRadius = '12px';
    cardElement.style.backgroundColor = 'var(--card-bg, #ffffff)';
    cardElement.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
    cardElement.style.cursor = item.disabled ? 'not-allowed' : 'pointer';
    cardElement.style.transition = 'all 0.2s ease';
    
    if (item.disabled) {
      cardElement.classList.add('menu-item-disabled');
      cardElement.style.opacity = '0.6';
    }
    
    // Header with icon and badge
    const header = document.createElement('div');
    header.style.display = 'flex';
    header.style.justifyContent = 'space-between';
    header.style.alignItems = 'flex-start';
    header.style.marginBottom = '12px';
    
    if (item.icon) {
      const iconElement = this.createIcon(item.icon);
      iconElement.style.fontSize = '20px';
      header.appendChild(iconElement);
    }
    
    if (item.badge) {
      const badgeElement = this.createBadge(item.badge);
      header.appendChild(badgeElement);
    }
    
    cardElement.appendChild(header);
    
    // Content
    const content = document.createElement('div');
    content.style.flex = '1';
    
    // Title
    const titleElement = document.createElement('div');
    titleElement.className = 'menu-item-title';
    titleElement.textContent = item.title;
    titleElement.style.fontWeight = '600';
    titleElement.style.fontSize = '16px';
    titleElement.style.marginBottom = '8px';
    content.appendChild(titleElement);
    
    // Description
    if (item.description) {
      const descElement = document.createElement('div');
      descElement.className = 'menu-item-description';
      descElement.textContent = item.description;
      descElement.style.fontSize = '13px';
      descElement.style.opacity = '0.8';
      descElement.style.lineHeight = '1.4';
      content.appendChild(descElement);
    }
    
    cardElement.appendChild(content);
    
    // Footer with shortcut or submenu indicator
    const footer = document.createElement('div');
    footer.style.display = 'flex';
    footer.style.justifyContent = 'space-between';
    footer.style.alignItems = 'center';
    footer.style.marginTop = '12px';
    footer.style.paddingTop = '8px';
    footer.style.borderTop = '1px solid var(--border-color, #e2e8f0)';
    
    if (item.shortcut) {
      const shortcutElement = this.createShortcut(item.shortcut);
      footer.appendChild(shortcutElement);
    }
    
    if (item.submenu && item.submenu.length > 0) {
      const submenuInfo = document.createElement('span');
      submenuInfo.textContent = `${item.submenu.length} items`;
      submenuInfo.style.fontSize = '11px';
      submenuInfo.style.opacity = '0.6';
      footer.appendChild(submenuInfo);
    }
    
    cardElement.appendChild(footer);
    this.addItemInteractivity(cardElement, item);
    
    return cardElement;
  }

  // ================================
  // Helper Methods for UI Elements
  // ================================

  private createIcon(icon: MenuIcon): HTMLElement {
    const iconElement = document.createElement('span');
    iconElement.className = 'menu-item-icon';
    
    switch (icon.type) {
      case 'emoji':
        iconElement.textContent = icon.value;
        break;
      case 'unicode':
        iconElement.innerHTML = icon.value;
        break;
      case 'ascii':
        iconElement.textContent = icon.value;
        iconElement.style.fontFamily = 'monospace';
        break;
      default:
        iconElement.textContent = icon.value;
    }
    
    if (icon.color) {
      iconElement.style.color = icon.color;
    }
    
    return iconElement;
  }

  private createBadge(badge: string | number): HTMLElement {
    const badgeElement = document.createElement('span');
    badgeElement.className = 'menu-item-badge';
    badgeElement.textContent = badge.toString();
    
    badgeElement.style.fontSize = '10px';
    badgeElement.style.padding = '2px 6px';
    badgeElement.style.backgroundColor = 'var(--badge-bg, #ef4444)';
    badgeElement.style.color = 'white';
    badgeElement.style.borderRadius = '10px';
    badgeElement.style.fontWeight = '600';
    badgeElement.style.lineHeight = '1';
    
    return badgeElement;
  }

  private createShortcut(shortcut: any): HTMLElement {
    const shortcutElement = document.createElement('span');
    shortcutElement.className = 'menu-item-shortcut';
    
    const keys = [];
    if (shortcut.ctrl) keys.push('Ctrl');
    if (shortcut.alt) keys.push('Alt');
    if (shortcut.shift) keys.push('Shift');
    keys.push(shortcut.key);
    
    shortcutElement.textContent = keys.join('+');
    shortcutElement.style.fontSize = '10px';
    shortcutElement.style.padding = '2px 6px';
    shortcutElement.style.backgroundColor = 'var(--shortcut-bg, #f1f5f9)';
    shortcutElement.style.color = 'var(--shortcut-text, #64748b)';
    shortcutElement.style.borderRadius = '4px';
    shortcutElement.style.fontFamily = 'monospace';
    
    return shortcutElement;
  }

  // ================================
  // Layout and Theme Methods
  // ================================

  private createMenuContainer(style: MenuStyle): HTMLElement {
    const container = document.createElement('div');
    container.className = `menu-container menu-${style.type}`;
    
    // Base styles
    container.style.width = '100%';
    container.style.height = '100%';
    container.style.overflow = 'hidden';
    container.style.position = 'relative';
    
    return container;
  }

  private applyTheme(container: HTMLElement, theme: string): void {
    container.setAttribute('data-theme', theme);
    
    // Apply CSS custom properties based on theme
    const themes = {
      default: {
        '--bg-color': '#ffffff',
        '--text-color': '#1f2937',
        '--border-color': '#e5e7eb',
        '--hover-bg': '#f9fafb',
        '--selected-bg': '#eff6ff',
        '--badge-bg': '#ef4444',
        '--card-bg': '#ffffff'
      },
      dark: {
        '--bg-color': '#1f2937',
        '--text-color': '#f9fafb',
        '--border-color': '#374151',
        '--hover-bg': '#374151',
        '--selected-bg': '#1e40af',
        '--badge-bg': '#dc2626',
        '--card-bg': '#111827'
      },
      light: {
        '--bg-color': '#fefefe',
        '--text-color': '#0f172a',
        '--border-color': '#cbd5e1',
        '--hover-bg': '#f8fafc',
        '--selected-bg': '#dbeafe',
        '--badge-bg': '#3b82f6',
        '--card-bg': '#ffffff'
      },
      colorful: {
        '--bg-color': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        '--text-color': '#ffffff',
        '--border-color': 'rgba(255,255,255,0.2)',
        '--hover-bg': 'rgba(255,255,255,0.1)',
        '--selected-bg': 'rgba(255,255,255,0.2)',
        '--badge-bg': '#f59e0b',
        '--card-bg': 'rgba(255,255,255,0.1)'
      }
    };
    
    const themeProps = themes[theme as keyof typeof themes] || themes.default;
    
    Object.entries(themeProps).forEach(([prop, value]) => {
      container.style.setProperty(prop, value);
    });
  }

  // ================================
  // Interactivity and Events
  // ================================

  private addItemInteractivity(element: HTMLElement, item: MenuItem): void {
    if (item.disabled) return;
    
    // Hover effects
    element.addEventListener('mouseenter', () => {
      element.style.backgroundColor = 'var(--hover-bg, #f9fafb)';
      element.style.transform = 'translateX(2px)';
    });
    
    element.addEventListener('mouseleave', () => {
      element.style.backgroundColor = '';
      element.style.transform = '';
    });
    
    // Click handling
    element.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      
      // Visual feedback
      element.style.backgroundColor = 'var(--selected-bg, #eff6ff)';
      
      // Emit custom event
      const selectEvent = new CustomEvent('menuItemSelect', {
        detail: { item, element },
        bubbles: true
      });
      element.dispatchEvent(selectEvent);
      
      // Reset visual state after short delay
      setTimeout(() => {
        element.style.backgroundColor = '';
      }, 150);
    });
    
    // Keyboard handling
    element.setAttribute('tabindex', '0');
    element.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        element.click();
      }
    });
  }

  // ================================
  // Virtual Scrolling and Performance
  // ================================

  private setupVirtualScrolling(
    container: HTMLElement,
    items: MenuItem[],
    style: MenuStyle
  ): void {
    this.virtualScrolling = true;
    
    // Create virtual scroll container
    const virtualContainer = document.createElement('div');
    virtualContainer.style.height = `${items.length * this.itemHeight}px`;
    virtualContainer.style.position = 'relative';
    
    // Create visible items container
    const visibleContainer = document.createElement('div');
    visibleContainer.style.position = 'absolute';
    visibleContainer.style.top = '0';
    visibleContainer.style.width = '100%';
    
    container.appendChild(virtualContainer);
    virtualContainer.appendChild(visibleContainer);
    
    // Setup scroll listener
    container.addEventListener('scroll', () => {
      this.updateVisibleItems(container, visibleContainer, items, style);
    });
    
    // Initial render
    this.updateVisibleItems(container, visibleContainer, items, style);
  }

  private updateVisibleItems(
    scrollContainer: HTMLElement,
    visibleContainer: HTMLElement,
    items: MenuItem[],
    style: MenuStyle
  ): void {
    const scrollTop = scrollContainer.scrollTop;
    const containerHeight = scrollContainer.clientHeight;
    
    const startIndex = Math.floor(scrollTop / this.itemHeight);
    const endIndex = Math.min(
      startIndex + Math.ceil(containerHeight / this.itemHeight) + 1,
      items.length
    );
    
    this.visibleRange = { start: startIndex, end: endIndex };
    
    // Clear and render visible items
    visibleContainer.innerHTML = '';
    visibleContainer.style.transform = `translateY(${startIndex * this.itemHeight}px)`;
    
    for (let i = startIndex; i < endIndex; i++) {
      const item = items[i];
      if (!item || item.hidden) continue;
      
      // Create item element (simplified for performance)
      const itemElement = document.createElement('div');
      itemElement.style.height = `${this.itemHeight}px`;
      itemElement.textContent = item.title;
      
      this.addItemInteractivity(itemElement, item);
      visibleContainer.appendChild(itemElement);
    }
  }

  // ================================
  // Responsive Layout
  // ================================

  private setupResponsiveLayout(container: HTMLElement, style: MenuStyle): void {
    if (!this.resizeObserver) return;
    
    this.resizeObserver.observe(container);
    
    // Initial responsive adjustments
    this.adjustLayoutForSize(container, style);
  }

  private adjustLayoutForSize(container: HTMLElement, style: MenuStyle): void {
    const width = container.clientWidth;
    
    // Adjust grid columns based on width
    if (style.type === 'grid') {
      const gridElement = container.querySelector('.menu-grid') as HTMLElement;
      if (gridElement) {
        let columns = style.itemsPerRow || 3;
        if (width < 600) columns = 2;
        if (width < 400) columns = 1;
        
        gridElement.style.gridTemplateColumns = `repeat(${columns}, 1fr)`;
      }
    }
    
    // Adjust card width
    if (style.type === 'cards') {
      const cardElements = container.querySelectorAll('.menu-item-card') as NodeListOf<HTMLElement>;
      cardElements.forEach(card => {
        if (width < 500) {
          card.style.width = '100%';
        } else {
          card.style.width = '200px';
        }
      });
    }
  }

  // ================================
  // Observer Setup
  // ================================

  private setupObservers(): void {
    // Resize observer for responsive behavior
    if (typeof ResizeObserver !== 'undefined') {
      this.resizeObserver = new ResizeObserver((entries) => {
        for (const entry of entries) {
          const container = entry.target as HTMLElement;
          const style = this.getStyleFromContainer(container);
          this.adjustLayoutForSize(container, style);
        }
      });
    }
    
    // Intersection observer for scroll performance
    if (typeof IntersectionObserver !== 'undefined') {
      this.intersectionObserver = new IntersectionObserver(
        (entries) => {
          entries.forEach(entry => {
            const element = entry.target as HTMLElement;
            if (entry.isIntersecting) {
              element.style.opacity = '1';
              element.style.transform = 'translateY(0)';
            }
          });
        },
        { threshold: 0.1 }
      );
    }
  }

  private getStyleFromContainer(container: HTMLElement): MenuStyle {
    // Extract style information from container attributes
    const type = container.className.includes('grid') ? 'grid' :
                 container.className.includes('tree') ? 'tree' :
                 container.className.includes('cards') ? 'cards' : 'list';
    
    return {
      type: type as any,
      theme: container.getAttribute('data-theme') as any || 'default',
      animations: true,
      showIcons: true,
      showShortcuts: true,
      showDescriptions: true
    };
  }

  // ================================
  // Scroll Management
  // ================================

  private restoreScrollPosition(container: HTMLElement): void {
    if (this.scrollPosition > 0) {
      container.scrollTop = this.scrollPosition;
    }
  }

  public saveScrollPosition(): void {
    if (this.currentContainer) {
      this.scrollPosition = this.currentContainer.scrollTop;
    }
  }

  public scrollToItem(itemId: string): void {
    const element = this.itemElements.get(itemId);
    if (element && this.currentContainer) {
      element.scrollIntoView({
        behavior: 'smooth',
        block: 'center',
        inline: 'nearest'
      });
    }
  }

  // ================================
  // Cleanup
  // ================================

  public destroy(): void {
    if (this.resizeObserver) {
      this.resizeObserver.disconnect();
    }
    
    if (this.intersectionObserver) {
      this.intersectionObserver.disconnect();
    }
    
    this.itemElements.clear();
    this.currentContainer = undefined;
  }
}

export default MenuRenderer;
