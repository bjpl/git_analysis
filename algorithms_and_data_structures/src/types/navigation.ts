/**
 * Navigation System Types and Interfaces
 * Defines the core types for the comprehensive CLI navigation system
 */

export interface NavigationNode {
  id: string;
  label: string;
  description?: string;
  parent?: string;
  children?: string[];
  command?: string;
  shortcut?: string;
  icon?: string;
  category?: string;
  tags?: string[];
  weight?: number; // For sorting priority
  isVisible?: boolean;
  isEnabled?: boolean;
  metadata?: Record<string, any>;
}

export interface MenuItem {
  id: string;
  label: string;
  description?: string;
  command?: string;
  shortcut?: KeyBinding;
  icon?: string;
  type: 'command' | 'submenu' | 'separator' | 'header';
  children?: MenuItem[];
  isVisible?: boolean;
  isEnabled?: boolean;
  onSelect?: () => void;
  onHover?: () => void;
}

export interface KeyBinding {
  key: string;
  ctrl?: boolean;
  alt?: boolean;
  shift?: boolean;
  meta?: boolean;
  description?: string;
}

export interface NavigationState {
  currentPath: string[];
  history: string[];
  searchQuery?: string;
  filterTags?: string[];
  breadcrumbs: BreadcrumbItem[];
  selectedItemId?: string;
  isSearchMode: boolean;
  isHelpMode: boolean;
}

export interface BreadcrumbItem {
  id: string;
  label: string;
  path: string;
  isClickable: boolean;
}

export interface SearchResult {
  item: NavigationNode;
  score: number;
  matchType: 'exact' | 'prefix' | 'fuzzy' | 'tag' | 'description';
  highlights?: SearchHighlight[];
}

export interface SearchHighlight {
  field: 'label' | 'description' | 'command' | 'tags';
  start: number;
  end: number;
}

export interface HelpContext {
  currentNode?: NavigationNode;
  availableCommands: string[];
  shortcuts: KeyBinding[];
  suggestions: string[];
  examples?: HelpExample[];
}

export interface HelpExample {
  command: string;
  description: string;
  usage: string;
}

export interface NavigationConfig {
  maxHistorySize: number;
  searchDebounceMs: number;
  fuzzySearchThreshold: number;
  breadcrumbSeparator: string;
  enableAnimations: boolean;
  keyBindings: Record<string, KeyBinding>;
  theme: NavigationTheme;
}

export interface NavigationTheme {
  colors: {
    primary: string;
    secondary: string;
    accent: string;
    background: string;
    text: string;
    textMuted: string;
    border: string;
    hover: string;
    selected: string;
    disabled: string;
  };
  icons: {
    folder: string;
    file: string;
    command: string;
    shortcut: string;
    search: string;
    help: string;
    back: string;
    forward: string;
    home: string;
  };
}

export interface CommandRoute {
  pattern: string | RegExp;
  handler: string;
  parameters?: RouteParameter[];
  middleware?: string[];
  description?: string;
  examples?: string[];
}

export interface RouteParameter {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'enum';
  required: boolean;
  description?: string;
  defaultValue?: any;
  enum?: string[];
  validation?: RegExp;
}

export interface NavigationEvent {
  type: 'navigate' | 'search' | 'select' | 'back' | 'forward' | 'help' | 'shortcut';
  data: any;
  timestamp: number;
  source: 'keyboard' | 'mouse' | 'programmatic';
}

export type NavigationEventHandler = (event: NavigationEvent) => void;

export interface FilterOptions {
  categories?: string[];
  tags?: string[];
  enabled?: boolean;
  visible?: boolean;
  hasCommand?: boolean;
  hasShortcut?: boolean;
}

export interface SortOptions {
  field: 'label' | 'weight' | 'lastUsed' | 'alphabetical';
  direction: 'asc' | 'desc';
}

// Error types
export class NavigationError extends Error {
  constructor(message: string, public code: string, public context?: any) {
    super(message);
    this.name = 'NavigationError';
  }
}

export class CommandNotFoundError extends NavigationError {
  constructor(command: string) {
    super(`Command not found: ${command}`, 'COMMAND_NOT_FOUND', { command });
  }
}

export class InvalidRouteError extends NavigationError {
  constructor(route: string, reason: string) {
    super(`Invalid route: ${route} - ${reason}`, 'INVALID_ROUTE', { route, reason });
  }
}