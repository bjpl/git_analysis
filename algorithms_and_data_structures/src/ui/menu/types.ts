/**
 * Comprehensive TypeScript types for the Interactive Menu System
 * Supports nested menus, animations, state management, and configuration
 */

export interface MenuKeyboardShortcut {
  key: string;
  ctrl?: boolean;
  alt?: boolean;
  shift?: boolean;
  description: string;
}

export interface MenuIcon {
  type: 'emoji' | 'unicode' | 'ascii';
  value: string;
  color?: string;
}

export interface MenuItem {
  id: string;
  title: string;
  description?: string;
  icon?: MenuIcon;
  shortcut?: MenuKeyboardShortcut;
  action?: string | (() => void | Promise<void>);
  submenu?: MenuItem[];
  disabled?: boolean;
  hidden?: boolean;
  badge?: string | number;
  metadata?: Record<string, any>;
}

export interface MenuStyle {
  type: 'list' | 'grid' | 'tree' | 'cards';
  theme: 'default' | 'dark' | 'light' | 'colorful';
  itemsPerRow?: number; // for grid layout
  maxHeight?: number;
  showIcons?: boolean;
  showShortcuts?: boolean;
  showDescriptions?: boolean;
  animations?: boolean;
}

export interface MenuConfiguration {
  id: string;
  title: string;
  description?: string;
  items: MenuItem[];
  style?: Partial<MenuStyle>;
  searchable?: boolean;
  sortable?: boolean;
  filterable?: boolean;
  breadcrumbs?: boolean;
  validation?: MenuValidationRules;
}

export interface MenuValidationRules {
  maxDepth?: number;
  maxItems?: number;
  requiredFields?: string[];
  customValidators?: ((item: MenuItem) => boolean)[];
}

export interface MenuState {
  currentMenuId: string;
  selectedItemId?: string;
  navigationHistory: string[];
  searchQuery?: string;
  filterCriteria?: Record<string, any>;
  bookmarks: string[];
  recentItems: string[];
  preferences: MenuPreferences;
  isLoading: boolean;
  error?: string;
}

export interface MenuPreferences {
  defaultStyle: MenuStyle;
  animationsEnabled: boolean;
  keyboardNavigationEnabled: boolean;
  mouseNavigationEnabled: boolean;
  autoSave: boolean;
  maxHistoryItems: number;
  maxRecentItems: number;
}

export interface MenuBreadcrumb {
  id: string;
  title: string;
  menuId: string;
}

export interface MenuAnimation {
  type: 'fade' | 'slide' | 'zoom' | 'flip' | 'bounce';
  duration: number;
  easing: 'linear' | 'ease' | 'ease-in' | 'ease-out' | 'ease-in-out';
  direction?: 'up' | 'down' | 'left' | 'right';
}

export interface MenuTransition {
  enter: MenuAnimation;
  exit: MenuAnimation;
  hover?: MenuAnimation;
  select?: MenuAnimation;
}

export interface MenuRenderOptions {
  width?: number;
  height?: number;
  x?: number;
  y?: number;
  style: MenuStyle;
  transition?: MenuTransition;
  scrollPosition?: number;
}

export interface MenuSearchResult {
  item: MenuItem;
  menuPath: string[];
  relevanceScore: number;
  highlightedText?: string;
}

export interface MenuEventHandlers {
  onItemSelect?: (item: MenuItem, path: string[]) => void;
  onItemHover?: (item: MenuItem) => void;
  onMenuChange?: (menuId: string) => void;
  onSearchChange?: (query: string, results: MenuSearchResult[]) => void;
  onError?: (error: string) => void;
  onStateChange?: (state: MenuState) => void;
}

export interface MenuPlugin {
  name: string;
  version: string;
  initialize: (menu: InteractiveMenu) => void;
  destroy?: () => void;
  onItemSelect?: (item: MenuItem) => void;
  onMenuRender?: (items: MenuItem[]) => MenuItem[];
}

// Re-export for easier importing
export type MenuItemAction = string | (() => void | Promise<void>);
export type MenuValidator = (item: MenuItem) => boolean;
export type MenuItemId = string;
export type MenuPath = string[];

// Utility types
export interface MenuContext {
  currentPath: MenuPath;
  selectedItem?: MenuItem;
  searchActive: boolean;
  filterActive: boolean;
  isNested: boolean;
  depth: number;
}

export interface MenuPerformanceMetrics {
  renderTime: number;
  searchTime: number;
  navigationTime: number;
  memoryUsage: number;
  itemsProcessed: number;
}

// Forward declaration for circular dependency
export interface InteractiveMenu {
  // This will be fully defined in InteractiveMenu.ts
  state: MenuState;
  config: MenuConfiguration;
  plugins: MenuPlugin[];
}
