/**
 * MenuConfig.ts - Configuration system for interactive menus
 * Features: JSON/YAML loading, validation, plugin system, hot-reloading
 */

import {
  MenuConfiguration, MenuItem, MenuValidationRules, MenuPlugin,
  MenuStyle, MenuValidator
} from './types.js';

interface ConfigSource {
  type: 'json' | 'yaml' | 'javascript' | 'url' | 'inline';
  source: string | object;
  lastModified?: number;
}

interface ConfigWatcher {
  source: string;
  callback: (config: MenuConfiguration) => void;
  interval: NodeJS.Timeout;
}

interface ValidationError {
  path: string;
  message: string;
  severity: 'error' | 'warning' | 'info';
}

export class MenuConfigLoader {
  private configCache: Map<string, { config: MenuConfiguration; timestamp: number }> = new Map();
  private watchers: Map<string, ConfigWatcher> = new Map();
  private validators: Map<string, MenuValidator> = new Map();
  private plugins: Map<string, MenuPlugin> = new Map();
  private defaultValidators: MenuValidator[];
  private schemaValidation: boolean = true;
  private hotReloadEnabled: boolean = false;
  private cacheEnabled: boolean = true;
  private cacheTTL: number = 300000; // 5 minutes
  
  constructor() {
    this.setupDefaultValidators();
    this.setupDefaultPlugins();
  }
  
  // ================================
  // Configuration Loading
  // ================================
  
  public async load(source: string | ConfigSource): Promise<MenuConfiguration> {
    const configSource = this.normalizeSource(source);
    const cacheKey = this.getCacheKey(configSource);
    
    // Check cache first
    if (this.cacheEnabled) {
      const cached = this.getCachedConfig(cacheKey);
      if (cached) {
        return cached;
      }
    }
    
    try {
      let rawConfig: any;
      
      switch (configSource.type) {
        case 'json':
          rawConfig = await this.loadJSON(configSource.source as string);
          break;
        case 'yaml':
          rawConfig = await this.loadYAML(configSource.source as string);
          break;
        case 'javascript':
          rawConfig = await this.loadJavaScript(configSource.source as string);
          break;
        case 'url':
          rawConfig = await this.loadFromURL(configSource.source as string);
          break;
        case 'inline':
          rawConfig = configSource.source as object;
          break;
        default:
          throw new Error(`Unsupported config type: ${configSource.type}`);
      }
      
      // Process and validate configuration
      const config = await this.processConfig(rawConfig);
      const validationResult = await this.validateConfig(config);
      
      if (validationResult.errors.length > 0) {
        throw new Error(`Configuration validation failed: ${validationResult.errors.map(e => e.message).join(', ')}`);
      }
      
      // Cache the configuration
      if (this.cacheEnabled) {
        this.cacheConfig(cacheKey, config);
      }
      
      // Setup watching if hot reload is enabled
      if (this.hotReloadEnabled && typeof configSource.source === 'string') {
        this.watchConfig(configSource.source, config);
      }
      
      return config;
    } catch (error) {
      throw new Error(`Failed to load configuration: ${error}`);
    }
  }
  
  private async loadJSON(path: string): Promise<any> {
    if (typeof window !== 'undefined') {
      // Browser environment
      const response = await fetch(path);
      if (!response.ok) {
        throw new Error(`Failed to fetch JSON config: ${response.statusText}`);
      }
      return response.json();
    } else {
      // Node.js environment
      const fs = await import('fs/promises');
      const content = await fs.readFile(path, 'utf-8');
      return JSON.parse(content);
    }
  }
  
  private async loadYAML(path: string): Promise<any> {
    try {
      // Try to load YAML parser
      const yaml = await import('js-yaml');
      
      let content: string;
      if (typeof window !== 'undefined') {
        // Browser environment
        const response = await fetch(path);
        if (!response.ok) {
          throw new Error(`Failed to fetch YAML config: ${response.statusText}`);
        }
        content = await response.text();
      } else {
        // Node.js environment
        const fs = await import('fs/promises');
        content = await fs.readFile(path, 'utf-8');
      }
      
      return yaml.load(content);
    } catch (error) {
      if (error instanceof Error && error.message.includes('Cannot resolve module')) {
        throw new Error('YAML support requires js-yaml package to be installed');
      }
      throw error;
    }
  }
  
  private async loadJavaScript(path: string): Promise<any> {
    if (typeof window !== 'undefined') {
      // Browser environment - dynamic import
      const module = await import(path);
      return module.default || module;
    } else {
      // Node.js environment
      const module = await import(path);
      return module.default || module;
    }
  }
  
  private async loadFromURL(url: string): Promise<any> {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Failed to fetch config from URL: ${response.statusText}`);
    }
    
    const contentType = response.headers.get('content-type') || '';
    
    if (contentType.includes('application/json')) {
      return response.json();
    } else if (contentType.includes('yaml') || url.endsWith('.yml') || url.endsWith('.yaml')) {
      const text = await response.text();
      const yaml = await import('js-yaml');
      return yaml.load(text);
    } else {
      throw new Error(`Unsupported content type: ${contentType}`);
    }
  }
  
  // ================================
  // Configuration Processing
  // ================================
  
  private async processConfig(rawConfig: any): Promise<MenuConfiguration> {
    // Apply transformations and enhancements
    let config = { ...rawConfig };
    
    // Process inheritance
    if (config.extends) {
      config = await this.processInheritance(config);
    }
    
    // Process variables and templating
    if (config.variables || this.hasTemplateExpressions(config)) {
      config = this.processTemplates(config);
    }
    
    // Process includes
    if (this.hasIncludes(config)) {
      config = await this.processIncludes(config);
    }
    
    // Apply plugin transformations
    for (const plugin of this.plugins.values()) {
      if (plugin.onMenuRender) {
        // Apply plugin transformations to items
        config.items = plugin.onMenuRender(config.items);
      }
    }
    
    // Set defaults
    config = this.applyDefaults(config);
    
    return config as MenuConfiguration;
  }
  
  private async processInheritance(config: any): Promise<any> {
    const baseConfigPath = config.extends;
    const baseConfig = await this.load(baseConfigPath);
    
    // Deep merge base config with current config
    return this.deepMerge(baseConfig, config);
  }
  
  private processTemplates(config: any): any {
    const variables = config.variables || {};
    const jsonString = JSON.stringify(config);
    
    // Replace template expressions like {{variableName}}
    const processed = jsonString.replace(/\{\{([^}]+)\}\}/g, (match, variableName) => {
      const value = this.getNestedValue(variables, variableName.trim());
      return value !== undefined ? JSON.stringify(value) : match;
    });
    
    return JSON.parse(processed);
  }
  
  private async processIncludes(config: any): Promise<any> {
    const processItem = async (item: any): Promise<any> => {
      if (item.include) {
        // Load and merge included configuration
        const includedConfig = await this.load(item.include);
        return this.deepMerge(includedConfig, item);
      }
      
      if (item.submenu) {
        item.submenu = await Promise.all(item.submenu.map(processItem));
      }
      
      return item;
    };
    
    if (config.items) {
      config.items = await Promise.all(config.items.map(processItem));
    }
    
    return config;
  }
  
  private applyDefaults(config: any): MenuConfiguration {
    const defaults: Partial<MenuConfiguration> = {
      searchable: true,
      sortable: false,
      filterable: false,
      breadcrumbs: true,
      style: {
        type: 'list',
        theme: 'default',
        showIcons: true,
        showShortcuts: true,
        showDescriptions: true,
        animations: true
      }
    };
    
    return this.deepMerge(defaults, config) as MenuConfiguration;
  }
  
  // ================================
  // Validation System
  // ================================
  
  public async validateConfig(config: MenuConfiguration): Promise<{ errors: ValidationError[]; warnings: ValidationError[] }> {
    const errors: ValidationError[] = [];
    const warnings: ValidationError[] = [];
    
    try {
      // Schema validation
      if (this.schemaValidation) {
        const schemaErrors = this.validateSchema(config);
        errors.push(...schemaErrors);
      }
      
      // Custom validation rules
      if (config.validation) {
        const ruleErrors = this.validateRules(config, config.validation);
        errors.push(...ruleErrors);
      }
      
      // Default validators
      for (const validator of this.defaultValidators) {
        this.validateWithCustomValidator(config, validator, errors, warnings);
      }
      
      // Plugin validators
      for (const validator of this.validators.values()) {
        this.validateWithCustomValidator(config, validator, errors, warnings);
      }
      
    } catch (error) {
      errors.push({
        path: 'root',
        message: `Validation error: ${error}`,
        severity: 'error'
      });
    }
    
    return { errors, warnings };
  }
  
  private validateSchema(config: MenuConfiguration): ValidationError[] {
    const errors: ValidationError[] = [];
    
    // Required fields
    if (!config.id) {
      errors.push({ path: 'id', message: 'Menu ID is required', severity: 'error' });
    }
    
    if (!config.title) {
      errors.push({ path: 'title', message: 'Menu title is required', severity: 'error' });
    }
    
    if (!config.items || !Array.isArray(config.items) || config.items.length === 0) {
      errors.push({ path: 'items', message: 'Menu must have at least one item', severity: 'error' });
    }
    
    // Validate items
    if (config.items) {
      this.validateItems(config.items, 'items', errors);
    }
    
    return errors;
  }
  
  private validateItems(items: MenuItem[], path: string, errors: ValidationError[]): void {
    items.forEach((item, index) => {
      const itemPath = `${path}[${index}]`;
      
      if (!item.id) {
        errors.push({ path: `${itemPath}.id`, message: 'Menu item ID is required', severity: 'error' });
      }
      
      if (!item.title) {
        errors.push({ path: `${itemPath}.title`, message: 'Menu item title is required', severity: 'error' });
      }
      
      // Check for duplicate IDs
      const duplicates = items.filter(i => i.id === item.id);
      if (duplicates.length > 1) {
        errors.push({ path: `${itemPath}.id`, message: `Duplicate menu item ID: ${item.id}`, severity: 'error' });
      }
      
      // Validate submenu items recursively
      if (item.submenu && item.submenu.length > 0) {
        this.validateItems(item.submenu, `${itemPath}.submenu`, errors);
      }
    });
  }
  
  private validateRules(config: MenuConfiguration, rules: MenuValidationRules): ValidationError[] {
    const errors: ValidationError[] = [];
    
    if (rules.maxDepth) {
      const maxDepth = this.calculateMaxDepth(config.items);
      if (maxDepth > rules.maxDepth) {
        errors.push({
          path: 'items',
          message: `Menu depth ${maxDepth} exceeds maximum allowed depth of ${rules.maxDepth}`,
          severity: 'error'
        });
      }
    }
    
    if (rules.maxItems) {
      const totalItems = this.countItems(config.items);
      if (totalItems > rules.maxItems) {
        errors.push({
          path: 'items',
          message: `Total items ${totalItems} exceeds maximum allowed items of ${rules.maxItems}`,
          severity: 'error'
        });
      }
    }
    
    return errors;
  }
  
  private validateWithCustomValidator(
    config: MenuConfiguration,
    validator: MenuValidator,
    errors: ValidationError[],
    warnings: ValidationError[]
  ): void {
    try {
      config.items.forEach((item, index) => {
        if (!validator(item)) {
          errors.push({
            path: `items[${index}]`,
            message: `Custom validation failed for item: ${item.id}`,
            severity: 'error'
          });
        }
      });
    } catch (error) {
      warnings.push({
        path: 'validation',
        message: `Custom validator error: ${error}`,
        severity: 'warning'
      });
    }
  }
  
  // ================================
  // Hot Reloading and Watching
  // ================================
  
  public enableHotReload(enabled: boolean = true): void {
    this.hotReloadEnabled = enabled;
  }
  
  private async watchConfig(path: string, config: MenuConfiguration): Promise<void> {
    if (this.watchers.has(path)) {
      return; // Already watching
    }
    
    const watcher: ConfigWatcher = {
      source: path,
      callback: () => {}, // Will be set by subscriber
      interval: setInterval(async () => {
        try {
          const newConfig = await this.load(path);
          if (JSON.stringify(newConfig) !== JSON.stringify(config)) {
            watcher.callback(newConfig);
          }
        } catch (error) {
          console.error(`Error watching config ${path}:`, error);
        }
      }, 1000) // Check every second
    };
    
    this.watchers.set(path, watcher);
  }
  
  public onConfigChange(path: string, callback: (config: MenuConfiguration) => void): void {
    const watcher = this.watchers.get(path);
    if (watcher) {
      watcher.callback = callback;
    }
  }
  
  public stopWatching(path?: string): void {
    if (path) {
      const watcher = this.watchers.get(path);
      if (watcher) {
        clearInterval(watcher.interval);
        this.watchers.delete(path);
      }
    } else {
      // Stop all watchers
      for (const watcher of this.watchers.values()) {
        clearInterval(watcher.interval);
      }
      this.watchers.clear();
    }
  }
  
  // ================================
  // Plugin System
  // ================================
  
  public addValidator(name: string, validator: MenuValidator): void {
    this.validators.set(name, validator);
  }
  
  public removeValidator(name: string): void {
    this.validators.delete(name);
  }
  
  public addPlugin(plugin: MenuPlugin): void {
    this.plugins.set(plugin.name, plugin);
  }
  
  public removePlugin(name: string): void {
    this.plugins.delete(name);
  }
  
  private setupDefaultValidators(): void {
    this.defaultValidators = [
      // Validate required fields
      (item: MenuItem) => !!item.id && !!item.title,
      
      // Validate action format
      (item: MenuItem) => {
        if (item.action) {
          return typeof item.action === 'string' || typeof item.action === 'function';
        }
        return true;
      },
      
      // Validate icon format
      (item: MenuItem) => {
        if (item.icon) {
          return item.icon.type && item.icon.value;
        }
        return true;
      },
      
      // Validate shortcut format
      (item: MenuItem) => {
        if (item.shortcut) {
          return !!item.shortcut.key;
        }
        return true;
      }
    ];
  }
  
  private setupDefaultPlugins(): void {
    // Icon resolver plugin
    const iconResolverPlugin: MenuPlugin = {
      name: 'icon-resolver',
      version: '1.0.0',
      initialize: () => {},
      onMenuRender: (items: MenuItem[]) => {
        return items.map(item => {
          if (item.icon && !item.icon.value && item.metadata?.iconName) {
            // Resolve icon from metadata
            item.icon.value = this.resolveIcon(item.metadata.iconName);
          }
          
          if (item.submenu) {
            item.submenu = iconResolverPlugin.onMenuRender!(item.submenu);
          }
          
          return item;
        });
      }
    };
    
    this.addPlugin(iconResolverPlugin);
  }
  
  // ================================
  // Utility Methods
  // ================================
  
  private normalizeSource(source: string | ConfigSource): ConfigSource {
    if (typeof source === 'string') {
      // Detect type from file extension or URL
      if (source.startsWith('http://') || source.startsWith('https://')) {
        return { type: 'url', source };
      } else if (source.endsWith('.json')) {
        return { type: 'json', source };
      } else if (source.endsWith('.yml') || source.endsWith('.yaml')) {
        return { type: 'yaml', source };
      } else if (source.endsWith('.js') || source.endsWith('.ts')) {
        return { type: 'javascript', source };
      } else {
        // Default to JSON
        return { type: 'json', source };
      }
    }
    
    return source;
  }
  
  private getCacheKey(source: ConfigSource): string {
    if (typeof source.source === 'string') {
      return `${source.type}:${source.source}`;
    }
    return `${source.type}:${JSON.stringify(source.source)}`;
  }
  
  private getCachedConfig(key: string): MenuConfiguration | null {
    const cached = this.configCache.get(key);
    if (cached && (Date.now() - cached.timestamp) < this.cacheTTL) {
      return cached.config;
    }
    return null;
  }
  
  private cacheConfig(key: string, config: MenuConfiguration): void {
    this.configCache.set(key, {
      config,
      timestamp: Date.now()
    });
  }
  
  private deepMerge(target: any, source: any): any {
    const result = { ...target };
    
    for (const key in source) {
      if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
        result[key] = this.deepMerge(result[key] || {}, source[key]);
      } else {
        result[key] = source[key];
      }
    }
    
    return result;
  }
  
  private getNestedValue(obj: any, path: string): any {
    return path.split('.').reduce((current, key) => current?.[key], obj);
  }
  
  private hasTemplateExpressions(config: any): boolean {
    const jsonString = JSON.stringify(config);
    return /\{\{[^}]+\}\}/.test(jsonString);
  }
  
  private hasIncludes(config: any): boolean {
    const jsonString = JSON.stringify(config);
    return jsonString.includes('"include"');
  }
  
  private calculateMaxDepth(items: MenuItem[], currentDepth: number = 0): number {
    let maxDepth = currentDepth;
    
    for (const item of items) {
      if (item.submenu && item.submenu.length > 0) {
        const submenuDepth = this.calculateMaxDepth(item.submenu, currentDepth + 1);
        maxDepth = Math.max(maxDepth, submenuDepth);
      }
    }
    
    return maxDepth;
  }
  
  private countItems(items: MenuItem[]): number {
    let count = items.length;
    
    for (const item of items) {
      if (item.submenu) {
        count += this.countItems(item.submenu);
      }
    }
    
    return count;
  }
  
  private resolveIcon(iconName: string): string {
    // Simple icon resolution - can be extended
    const iconMap: Record<string, string> = {
      'home': '🏠',
      'settings': '⚙️',
      'user': '👤',
      'file': '📄',
      'folder': '📁',
      'search': '🔍',
      'edit': '✏️',
      'delete': '🗑️',
      'add': '➕',
      'remove': '➖'
    };
    
    return iconMap[iconName] || '📋';
  }
  
  // ================================
  // Export and Import
  // ================================
  
  public async exportConfig(config: MenuConfiguration, format: 'json' | 'yaml' = 'json'): Promise<string> {
    if (format === 'yaml') {
      const yaml = await import('js-yaml');
      return yaml.dump(config, { indent: 2 });
    }
    
    return JSON.stringify(config, null, 2);
  }
  
  public async saveConfig(config: MenuConfiguration, path: string): Promise<void> {
    const format = path.endsWith('.yml') || path.endsWith('.yaml') ? 'yaml' : 'json';
    const content = await this.exportConfig(config, format);
    
    if (typeof window === 'undefined') {
      // Node.js environment
      const fs = await import('fs/promises');
      await fs.writeFile(path, content, 'utf-8');
    } else {
      // Browser environment - download file
      const blob = new Blob([content], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      
      const a = document.createElement('a');
      a.href = url;
      a.download = path;
      document.body.appendChild(a);
      a.click();
      
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  }
  
  // ================================
  // Cache Management
  // ================================
  
  public clearCache(): void {
    this.configCache.clear();
  }
  
  public setCacheEnabled(enabled: boolean): void {
    this.cacheEnabled = enabled;
    if (!enabled) {
      this.clearCache();
    }
  }
  
  public setCacheTTL(ttl: number): void {
    this.cacheTTL = ttl;
  }
  
  // ================================
  // Debug and Metrics
  // ================================
  
  public getMetrics(): any {
    return {
      cachedConfigs: this.configCache.size,
      activeWatchers: this.watchers.size,
      registeredValidators: this.validators.size,
      registeredPlugins: this.plugins.size,
      hotReloadEnabled: this.hotReloadEnabled,
      cacheEnabled: this.cacheEnabled,
      cacheTTL: this.cacheTTL
    };
  }
  
  // ================================
  // Cleanup
  // ================================
  
  public destroy(): void {
    this.stopWatching();
    this.clearCache();
    this.validators.clear();
    this.plugins.clear();
  }
}

export default MenuConfigLoader;
