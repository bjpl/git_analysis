/**
 * MenuState.ts - State management for interactive menus
 * Features: Persistence, undo/redo, bookmarks, preferences
 */

import {
  MenuState, MenuPreferences, MenuItem, MenuItemId, MenuPath
} from './types.js';

interface StateSnapshot {
  timestamp: number;
  state: MenuState;
  description: string;
}

interface StorageAdapter {
  get(key: string): Promise<any>;
  set(key: string, value: any): Promise<void>;
  remove(key: string): Promise<void>;
  clear(): Promise<void>;
}

class LocalStorageAdapter implements StorageAdapter {
  private prefix = 'menu-state-';
  
  async get(key: string): Promise<any> {
    const item = localStorage.getItem(this.prefix + key);
    return item ? JSON.parse(item) : null;
  }
  
  async set(key: string, value: any): Promise<void> {
    localStorage.setItem(this.prefix + key, JSON.stringify(value));
  }
  
  async remove(key: string): Promise<void> {
    localStorage.removeItem(this.prefix + key);
  }
  
  async clear(): Promise<void> {
    const keys = Object.keys(localStorage);
    keys.forEach(key => {
      if (key.startsWith(this.prefix)) {
        localStorage.removeItem(key);
      }
    });
  }
}

class IndexedDBAdapter implements StorageAdapter {
  private dbName = 'MenuStateDB';
  private version = 1;
  private db?: IDBDatabase;
  
  async initialize(): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.version);
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };
      
      request.onupgradeneeded = () => {
        const db = request.result;
        if (!db.objectStoreNames.contains('state')) {
          db.createObjectStore('state', { keyPath: 'key' });
        }
      };
    });
  }
  
  async get(key: string): Promise<any> {
    if (!this.db) await this.initialize();
    
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['state'], 'readonly');
      const store = transaction.objectStore('state');
      const request = store.get(key);
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        resolve(request.result ? request.result.value : null);
      };
    });
  }
  
  async set(key: string, value: any): Promise<void> {
    if (!this.db) await this.initialize();
    
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['state'], 'readwrite');
      const store = transaction.objectStore('state');
      const request = store.put({ key, value });
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve();
    });
  }
  
  async remove(key: string): Promise<void> {
    if (!this.db) await this.initialize();
    
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['state'], 'readwrite');
      const store = transaction.objectStore('state');
      const request = store.delete(key);
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve();
    });
  }
  
  async clear(): Promise<void> {
    if (!this.db) await this.initialize();
    
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['state'], 'readwrite');
      const store = transaction.objectStore('state');
      const request = store.clear();
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve();
    });
  }
}

export class MenuStateManager {
  private currentState: MenuState;
  private stateHistory: StateSnapshot[] = [];
  private historyIndex: number = -1;
  private maxHistorySize: number = 50;
  private storage: StorageAdapter;
  private autoSaveEnabled: boolean = true;
  private autoSaveDelay: number = 1000;
  private autoSaveTimer?: NodeJS.Timeout;
  private listeners: Map<string, (state: MenuState) => void> = new Map();
  private changeQueue: Array<() => void> = [];
  private processingQueue: boolean = false;
  
  constructor(
    initialState?: Partial<MenuState>,
    useIndexedDB: boolean = true
  ) {
    this.storage = useIndexedDB ? new IndexedDBAdapter() : new LocalStorageAdapter();
    
    // Initialize with default state
    this.currentState = {
      currentMenuId: '',
      navigationHistory: [],
      bookmarks: [],
      recentItems: [],
      preferences: this.getDefaultPreferences(),
      isLoading: false,
      ...initialState
    };
  }
  
  // ================================
  // Initialization and Setup
  // ================================
  
  public async initialize(): Promise<void> {
    try {
      // Initialize storage adapter
      if (this.storage instanceof IndexedDBAdapter) {
        await (this.storage as IndexedDBAdapter).initialize();
      }
      
      // Load persisted state
      await this.loadPersistedState();
      
      // Setup auto-save if enabled
      if (this.autoSaveEnabled) {
        this.setupAutoSave();
      }
      
      // Load preferences
      await this.loadPreferences();
      
    } catch (error) {
      console.error('Failed to initialize MenuStateManager:', error);
      // Continue with default state
    }
  }
  
  // ================================
  // State Management
  // ================================
  
  public getState(): MenuState {
    return { ...this.currentState };
  }
  
  public setState(newState: Partial<MenuState>, description?: string): void {
    this.queueChange(() => {
      this.setStateInternal(newState, description);
    });
  }
  
  private setStateInternal(newState: Partial<MenuState>, description?: string): void {
    // Create snapshot for undo functionality
    if (description) {
      this.createSnapshot(description);
    }
    
    // Update state
    const previousState = { ...this.currentState };
    this.currentState = {
      ...this.currentState,
      ...newState
    };
    
    // Validate state
    this.validateState();
    
    // Notify listeners
    this.notifyStateChange(previousState, this.currentState);
    
    // Trigger auto-save
    if (this.autoSaveEnabled) {
      this.scheduleAutoSave();
    }
  }
  
  public updateState(updates: Partial<MenuState>, description?: string): void {
    this.setState(updates, description);
  }
  
  public resetState(): void {
    this.setState({
      currentMenuId: '',
      selectedItemId: undefined,
      navigationHistory: [],
      searchQuery: undefined,
      filterCriteria: undefined,
      bookmarks: [],
      recentItems: [],
      isLoading: false,
      error: undefined
    }, 'Reset state');
  }
  
  // ================================
  // History Management (Undo/Redo)
  // ================================
  
  private createSnapshot(description: string): void {
    // Remove any future history if we're not at the end
    if (this.historyIndex < this.stateHistory.length - 1) {
      this.stateHistory = this.stateHistory.slice(0, this.historyIndex + 1);
    }
    
    // Add new snapshot
    const snapshot: StateSnapshot = {
      timestamp: Date.now(),
      state: { ...this.currentState },
      description
    };
    
    this.stateHistory.push(snapshot);
    this.historyIndex = this.stateHistory.length - 1;
    
    // Limit history size
    if (this.stateHistory.length > this.maxHistorySize) {
      this.stateHistory.shift();
      this.historyIndex--;
    }
  }
  
  public canUndo(): boolean {
    return this.historyIndex > 0;
  }
  
  public canRedo(): boolean {
    return this.historyIndex < this.stateHistory.length - 1;
  }
  
  public undo(): boolean {
    if (!this.canUndo()) return false;
    
    this.historyIndex--;
    const snapshot = this.stateHistory[this.historyIndex];
    
    this.currentState = { ...snapshot.state };
    this.notifyStateChange(this.currentState, this.currentState);
    
    return true;
  }
  
  public redo(): boolean {
    if (!this.canRedo()) return false;
    
    this.historyIndex++;
    const snapshot = this.stateHistory[this.historyIndex];
    
    this.currentState = { ...snapshot.state };
    this.notifyStateChange(this.currentState, this.currentState);
    
    return true;
  }
  
  public getHistory(): StateSnapshot[] {
    return [...this.stateHistory];
  }
  
  public clearHistory(): void {
    this.stateHistory = [];
    this.historyIndex = -1;
  }
  
  // ================================
  // Bookmarks Management
  // ================================
  
  public addBookmark(itemId: MenuItemId): void {
    const bookmarks = [...this.currentState.bookmarks];
    if (!bookmarks.includes(itemId)) {
      bookmarks.push(itemId);
      this.updateState({ bookmarks }, `Add bookmark: ${itemId}`);
    }
  }
  
  public removeBookmark(itemId: MenuItemId): void {
    const bookmarks = this.currentState.bookmarks.filter(id => id !== itemId);
    this.updateState({ bookmarks }, `Remove bookmark: ${itemId}`);
  }
  
  public toggleBookmark(itemId: MenuItemId): void {
    if (this.isBookmarked(itemId)) {
      this.removeBookmark(itemId);
    } else {
      this.addBookmark(itemId);
    }
  }
  
  public isBookmarked(itemId: MenuItemId): boolean {
    return this.currentState.bookmarks.includes(itemId);
  }
  
  public getBookmarks(): MenuItemId[] {
    return [...this.currentState.bookmarks];
  }
  
  public clearBookmarks(): void {
    this.updateState({ bookmarks: [] }, 'Clear all bookmarks');
  }
  
  // ================================
  // Recent Items Management
  // ================================
  
  public addRecentItem(itemId: MenuItemId): void {
    const recentItems = [itemId, ...this.currentState.recentItems.filter(id => id !== itemId)];
    const maxRecent = this.currentState.preferences.maxRecentItems || 10;
    
    this.updateState({
      recentItems: recentItems.slice(0, maxRecent)
    });
  }
  
  public removeRecentItem(itemId: MenuItemId): void {
    const recentItems = this.currentState.recentItems.filter(id => id !== itemId);
    this.updateState({ recentItems });
  }
  
  public getRecentItems(): MenuItemId[] {
    return [...this.currentState.recentItems];
  }
  
  public clearRecentItems(): void {
    this.updateState({ recentItems: [] }, 'Clear recent items');
  }
  
  // ================================
  // Navigation History
  // ================================
  
  public pushToHistory(menuId: string): void {
    const history = [...this.currentState.navigationHistory];
    
    // Don't add if it's the same as the last item
    if (history[history.length - 1] !== menuId) {
      history.push(menuId);
      
      // Limit history size
      const maxHistory = this.currentState.preferences.maxHistoryItems || 50;
      if (history.length > maxHistory) {
        history.shift();
      }
      
      this.updateState({ navigationHistory: history });
    }
  }
  
  public popFromHistory(): string | undefined {
    const history = [...this.currentState.navigationHistory];
    const current = history.pop();
    
    this.updateState({ navigationHistory: history });
    return current;
  }
  
  public getNavigationHistory(): string[] {
    return [...this.currentState.navigationHistory];
  }
  
  public clearNavigationHistory(): void {
    this.updateState({ navigationHistory: [] }, 'Clear navigation history');
  }
  
  // ================================
  // Preferences Management
  // ================================
  
  public updatePreferences(updates: Partial<MenuPreferences>): void {
    const preferences = {
      ...this.currentState.preferences,
      ...updates
    };
    
    this.updateState({ preferences }, 'Update preferences');
    
    // Save preferences separately for faster loading
    this.savePreferences();
  }
  
  public getPreferences(): MenuPreferences {
    return { ...this.currentState.preferences };
  }
  
  public resetPreferences(): void {
    this.updateState({ preferences: this.getDefaultPreferences() }, 'Reset preferences');
  }
  
  private getDefaultPreferences(): MenuPreferences {
    return {
      defaultStyle: {
        type: 'list',
        theme: 'default',
        showIcons: true,
        showShortcuts: true,
        showDescriptions: true,
        animations: true
      },
      animationsEnabled: true,
      keyboardNavigationEnabled: true,
      mouseNavigationEnabled: true,
      autoSave: true,
      maxHistoryItems: 50,
      maxRecentItems: 10
    };
  }
  
  // ================================
  // Search and Filter State
  // ================================
  
  public setSearchQuery(query?: string): void {
    this.updateState({ searchQuery: query });
  }
  
  public setFilterCriteria(criteria?: Record<string, any>): void {
    this.updateState({ filterCriteria: criteria });
  }
  
  public clearSearchAndFilter(): void {
    this.updateState({
      searchQuery: undefined,
      filterCriteria: undefined
    }, 'Clear search and filter');
  }
  
  // ================================
  // Loading and Error State
  // ================================
  
  public setLoading(loading: boolean): void {
    this.updateState({ isLoading: loading });
  }
  
  public setError(error?: string): void {
    this.updateState({ error });
  }
  
  public clearError(): void {
    this.updateState({ error: undefined });
  }
  
  // ================================
  // Persistence
  // ================================
  
  private async loadPersistedState(): Promise<void> {
    try {
      const saved = await this.storage.get('currentState');
      if (saved) {
        // Merge with current state, preserving any newer properties
        this.currentState = {
          ...this.currentState,
          ...saved,
          // Don't restore loading state
          isLoading: false
        };
      }
    } catch (error) {
      console.error('Failed to load persisted state:', error);
    }
  }
  
  private async saveState(): Promise<void> {
    try {
      await this.storage.set('currentState', this.currentState);
    } catch (error) {
      console.error('Failed to save state:', error);
    }
  }
  
  private async loadPreferences(): Promise<void> {
    try {
      const saved = await this.storage.get('preferences');
      if (saved) {
        this.currentState.preferences = {
          ...this.currentState.preferences,
          ...saved
        };
      }
    } catch (error) {
      console.error('Failed to load preferences:', error);
    }
  }
  
  private async savePreferences(): Promise<void> {
    try {
      await this.storage.set('preferences', this.currentState.preferences);
    } catch (error) {
      console.error('Failed to save preferences:', error);
    }
  }
  
  public async exportState(): Promise<string> {
    const exportData = {
      state: this.currentState,
      history: this.stateHistory,
      timestamp: Date.now(),
      version: '1.0.0'
    };
    
    return JSON.stringify(exportData, null, 2);
  }
  
  public async importState(jsonData: string): Promise<void> {
    try {
      const importData = JSON.parse(jsonData);
      
      if (importData.version !== '1.0.0') {
        throw new Error('Unsupported state version');
      }
      
      this.currentState = importData.state;
      this.stateHistory = importData.history || [];
      this.historyIndex = this.stateHistory.length - 1;
      
      await this.saveState();
      this.notifyStateChange(this.currentState, this.currentState);
      
    } catch (error) {
      throw new Error(`Failed to import state: ${error}`);
    }
  }
  
  // ================================
  // Auto-save Management
  // ================================
  
  private setupAutoSave(): void {
    this.autoSaveEnabled = this.currentState.preferences.autoSave;
  }
  
  private scheduleAutoSave(): void {
    if (this.autoSaveTimer) {
      clearTimeout(this.autoSaveTimer);
    }
    
    this.autoSaveTimer = setTimeout(() => {
      this.saveState();
    }, this.autoSaveDelay);
  }
  
  public enableAutoSave(enabled: boolean = true): void {
    this.autoSaveEnabled = enabled;
    this.updatePreferences({ autoSave: enabled });
    
    if (enabled) {
      this.scheduleAutoSave();
    } else if (this.autoSaveTimer) {
      clearTimeout(this.autoSaveTimer);
    }
  }
  
  public async forceSave(): Promise<void> {
    await this.saveState();
  }
  
  // ================================
  // Event System
  // ================================
  
  public subscribe(id: string, callback: (state: MenuState) => void): void {
    this.listeners.set(id, callback);
  }
  
  public unsubscribe(id: string): void {
    this.listeners.delete(id);
  }
  
  private notifyStateChange(previousState: MenuState, currentState: MenuState): void {
    for (const callback of this.listeners.values()) {
      try {
        callback(currentState);
      } catch (error) {
        console.error('Error in state change callback:', error);
      }
    }
  }
  
  // ================================
  // Queue System for State Changes
  // ================================
  
  private queueChange(change: () => void): void {
    this.changeQueue.push(change);
    
    if (!this.processingQueue) {
      this.processQueue();
    }
  }
  
  private async processQueue(): Promise<void> {
    if (this.processingQueue) return;
    
    this.processingQueue = true;
    
    while (this.changeQueue.length > 0) {
      const change = this.changeQueue.shift();
      if (change) {
        try {
          change();
          // Small delay to prevent overwhelming the system
          await new Promise(resolve => setTimeout(resolve, 1));
        } catch (error) {
          console.error('Error processing state change:', error);
        }
      }
    }
    
    this.processingQueue = false;
  }
  
  // ================================
  // Validation
  // ================================
  
  private validateState(): void {
    // Ensure required fields exist
    if (!this.currentState.currentMenuId) {
      console.warn('MenuState: currentMenuId is empty');
    }
    
    if (!Array.isArray(this.currentState.navigationHistory)) {
      this.currentState.navigationHistory = [];
    }
    
    if (!Array.isArray(this.currentState.bookmarks)) {
      this.currentState.bookmarks = [];
    }
    
    if (!Array.isArray(this.currentState.recentItems)) {
      this.currentState.recentItems = [];
    }
    
    if (!this.currentState.preferences) {
      this.currentState.preferences = this.getDefaultPreferences();
    }
    
    // Remove duplicates from arrays
    this.currentState.bookmarks = [...new Set(this.currentState.bookmarks)];
    this.currentState.recentItems = [...new Set(this.currentState.recentItems)];
    this.currentState.navigationHistory = [...new Set(this.currentState.navigationHistory)];
  }
  
  // ================================
  // Debug and Metrics
  // ================================
  
  public getDebugInfo(): any {
    return {
      currentState: this.currentState,
      historyLength: this.stateHistory.length,
      historyIndex: this.historyIndex,
      canUndo: this.canUndo(),
      canRedo: this.canRedo(),
      autoSaveEnabled: this.autoSaveEnabled,
      listenerCount: this.listeners.size,
      queueLength: this.changeQueue.length,
      processingQueue: this.processingQueue
    };
  }
  
  public getMetrics(): any {
    return {
      stateChanges: this.stateHistory.length,
      bookmarksCount: this.currentState.bookmarks.length,
      recentItemsCount: this.currentState.recentItems.length,
      navigationDepth: this.currentState.navigationHistory.length,
      memoryUsage: JSON.stringify(this.currentState).length
    };
  }
  
  // ================================
  // Cleanup
  // ================================
  
  public async destroy(): Promise<void> {
    // Clear auto-save timer
    if (this.autoSaveTimer) {
      clearTimeout(this.autoSaveTimer);
    }
    
    // Save final state
    if (this.autoSaveEnabled) {
      await this.forceSave();
    }
    
    // Clear listeners
    this.listeners.clear();
    
    // Clear queue
    this.changeQueue = [];
    
    // Clear history
    this.stateHistory = [];
    this.historyIndex = -1;
  }
}

export default MenuStateManager;
