/**
 * Keyboard Shortcuts for Notes Management
 * Handles keyboard shortcuts and hotkey management
 */

const SHORTCUT_KEYS = {
  NEW_NOTE: { key: 'n', meta: true, description: 'Create new note' },
  SAVE_NOTE: { key: 's', meta: true, description: 'Save current note' },
  TOGGLE_NOTES: { key: '/', meta: true, description: 'Toggle notes panel' },
  SEARCH_NOTES: { key: 'f', meta: true, description: 'Search notes' },
  CLOSE_EDITOR: { key: 'Escape', description: 'Close note editor' },
  DELETE_NOTE: { key: 'Delete', meta: true, description: 'Delete selected note' },
  ARCHIVE_NOTE: { key: 'a', meta: true, description: 'Archive/unarchive note' },
  PIN_NOTE: { key: 'p', meta: true, description: 'Pin/unpin note' },
  DUPLICATE_NOTE: { key: 'd', meta: true, description: 'Duplicate current note' },
  EXPORT_NOTES: { key: 'e', meta: true, shift: true, description: 'Export notes' },
  IMPORT_NOTES: { key: 'i', meta: true, shift: true, description: 'Import notes' },
  TOGGLE_SIDEBAR: { key: '[', meta: true, description: 'Toggle sidebar' },
  FOCUS_EDITOR: { key: 't', meta: true, description: 'Focus note editor' },
  QUICK_SWITCHER: { key: 'k', meta: true, description: 'Quick note switcher' },
  NEXT_NOTE: { key: 'ArrowDown', meta: true, description: 'Select next note' },
  PREV_NOTE: { key: 'ArrowUp', meta: true, description: 'Select previous note' },
  UNDO: { key: 'z', meta: true, description: 'Undo last action' },
  REDO: { key: 'z', meta: true, shift: true, description: 'Redo last action' },
  SELECT_ALL: { key: 'a', meta: true, shift: true, description: 'Select all notes' },
  BOLD_TEXT: { key: 'b', meta: true, description: 'Bold selected text' },
  ITALIC_TEXT: { key: 'i', meta: true, description: 'Italicize selected text' },
  CODE_TEXT: { key: '`', meta: true, description: 'Code format selected text' }
};

class NoteShortcuts {
  constructor() {
    this.shortcuts = new Map();
    this.isEnabled = true;
    this.listeners = new Set();
    
    // Bind methods
    this.handleKeyDown = this.handleKeyDown.bind(this);
    this.handleKeyUp = this.handleKeyUp.bind(this);
    
    // Track pressed keys for combinations
    this.pressedKeys = new Set();
    
    // Initialize default shortcuts
    this.initializeDefaults();
  }

  /**
   * Initialize default keyboard shortcuts
   */
  initializeDefaults() {
    Object.entries(SHORTCUT_KEYS).forEach(([name, config]) => {
      this.register(name, config);
    });
  }

  /**
   * Register a keyboard shortcut
   */
  register(name, config, callback = null) {
    const shortcut = {
      name,
      key: config.key,
      meta: config.meta || false,
      ctrl: config.ctrl || false,
      shift: config.shift || false,
      alt: config.alt || false,
      description: config.description || '',
      callback,
      enabled: true,
      context: config.context || 'global' // 'global', 'editor', 'list'
    };

    this.shortcuts.set(name, shortcut);
    return this;
  }

  /**
   * Unregister a keyboard shortcut
   */
  unregister(name) {
    this.shortcuts.delete(name);
    return this;
  }

  /**
   * Update shortcut configuration
   */
  updateShortcut(name, updates) {
    const shortcut = this.shortcuts.get(name);
    if (shortcut) {
      this.shortcuts.set(name, { ...shortcut, ...updates });
    }
    return this;
  }

  /**
   * Enable or disable a specific shortcut
   */
  toggleShortcut(name, enabled = undefined) {
    const shortcut = this.shortcuts.get(name);
    if (shortcut) {
      shortcut.enabled = enabled !== undefined ? enabled : !shortcut.enabled;
    }
    return this;
  }

  /**
   * Set callback for a shortcut
   */
  setCallback(name, callback) {
    const shortcut = this.shortcuts.get(name);
    if (shortcut) {
      shortcut.callback = callback;
    }
    return this;
  }

  /**
   * Enable/disable all shortcuts
   */
  setEnabled(enabled) {
    this.isEnabled = enabled;
    return this;
  }

  /**
   * Start listening for keyboard events
   */
  start() {
    if (typeof window !== 'undefined') {
      document.addEventListener('keydown', this.handleKeyDown, true);
      document.addEventListener('keyup', this.handleKeyUp, true);
    }
    return this;
  }

  /**
   * Stop listening for keyboard events
   */
  stop() {
    if (typeof window !== 'undefined') {
      document.removeEventListener('keydown', this.handleKeyDown, true);
      document.removeEventListener('keyup', this.handleKeyUp, true);
    }
    this.pressedKeys.clear();
    return this;
  }

  /**
   * Handle keydown events
   */
  handleKeyDown(event) {
    if (!this.isEnabled) return;

    // Track pressed keys
    this.pressedKeys.add(event.key);

    // Get current context
    const context = this.getCurrentContext(event.target);

    // Find matching shortcuts
    const matchingShortcuts = this.findMatchingShortcuts(event, context);

    if (matchingShortcuts.length > 0) {
      // Prevent default behavior for recognized shortcuts
      event.preventDefault();
      event.stopPropagation();

      // Execute the first matching shortcut
      const shortcut = matchingShortcuts[0];
      this.executeShortcut(shortcut, event);
    }
  }

  /**
   * Handle keyup events
   */
  handleKeyUp(event) {
    this.pressedKeys.delete(event.key);
  }

  /**
   * Find shortcuts matching the current key event
   */
  findMatchingShortcuts(event, context) {
    const matches = [];

    for (const shortcut of this.shortcuts.values()) {
      if (!shortcut.enabled) continue;
      
      // Check context
      if (shortcut.context !== 'global' && shortcut.context !== context) {
        continue;
      }

      // Check key match
      if (shortcut.key !== event.key) continue;

      // Check modifiers
      const metaKey = event.metaKey || event.ctrlKey; // Handle both Mac and PC
      
      if (shortcut.meta && !metaKey) continue;
      if (!shortcut.meta && metaKey && shortcut.key !== 'Meta') continue;
      
      if (shortcut.shift && !event.shiftKey) continue;
      if (!shortcut.shift && event.shiftKey && !this.isShiftIgnoredKey(shortcut.key)) continue;
      
      if (shortcut.alt && !event.altKey) continue;
      if (!shortcut.alt && event.altKey) continue;

      matches.push(shortcut);
    }

    return matches;
  }

  /**
   * Execute a shortcut
   */
  executeShortcut(shortcut, event) {
    try {
      // Notify listeners
      this.notifyListeners({
        type: 'shortcut_executed',
        shortcut: shortcut.name,
        event
      });

      // Execute callback if available
      if (shortcut.callback) {
        shortcut.callback(event, shortcut);
      } else {
        // Execute default action
        this.executeDefaultAction(shortcut.name, event);
      }

    } catch (error) {
      console.error(`Error executing shortcut ${shortcut.name}:`, error);
    }
  }

  /**
   * Execute default actions for built-in shortcuts
   */
  executeDefaultAction(shortcutName, event) {
    switch (shortcutName) {
      case 'NEW_NOTE':
        this.notifyListeners({ type: 'new_note_requested' });
        break;
      
      case 'SAVE_NOTE':
        this.notifyListeners({ type: 'save_note_requested' });
        break;
      
      case 'TOGGLE_NOTES':
        this.notifyListeners({ type: 'toggle_notes_panel' });
        break;
      
      case 'SEARCH_NOTES':
        this.notifyListeners({ type: 'search_notes_requested' });
        break;
      
      case 'CLOSE_EDITOR':
        this.notifyListeners({ type: 'close_editor_requested' });
        break;
      
      case 'DELETE_NOTE':
        this.notifyListeners({ type: 'delete_note_requested' });
        break;
      
      case 'ARCHIVE_NOTE':
        this.notifyListeners({ type: 'archive_note_requested' });
        break;
      
      case 'PIN_NOTE':
        this.notifyListeners({ type: 'pin_note_requested' });
        break;
      
      case 'DUPLICATE_NOTE':
        this.notifyListeners({ type: 'duplicate_note_requested' });
        break;
      
      case 'EXPORT_NOTES':
        this.notifyListeners({ type: 'export_notes_requested' });
        break;
      
      case 'IMPORT_NOTES':
        this.notifyListeners({ type: 'import_notes_requested' });
        break;
      
      case 'TOGGLE_SIDEBAR':
        this.notifyListeners({ type: 'toggle_sidebar' });
        break;
      
      case 'FOCUS_EDITOR':
        this.notifyListeners({ type: 'focus_editor_requested' });
        break;
      
      case 'QUICK_SWITCHER':
        this.notifyListeners({ type: 'quick_switcher_requested' });
        break;
      
      case 'NEXT_NOTE':
        this.notifyListeners({ type: 'next_note_requested' });
        break;
      
      case 'PREV_NOTE':
        this.notifyListeners({ type: 'prev_note_requested' });
        break;
      
      case 'UNDO':
        this.notifyListeners({ type: 'undo_requested' });
        break;
      
      case 'REDO':
        this.notifyListeners({ type: 'redo_requested' });
        break;
      
      case 'SELECT_ALL':
        this.notifyListeners({ type: 'select_all_notes' });
        break;
      
      case 'BOLD_TEXT':
        this.applyTextFormat('**', '**');
        break;
      
      case 'ITALIC_TEXT':
        this.applyTextFormat('*', '*');
        break;
      
      case 'CODE_TEXT':
        this.applyTextFormat('`', '`');
        break;
      
      default:
        console.warn(`No default action for shortcut: ${shortcutName}`);
    }
  }

  /**
   * Apply text formatting in the current editor
   */
  applyTextFormat(prefix, suffix = null) {
    const activeElement = document.activeElement;
    
    if (!activeElement || (activeElement.tagName !== 'TEXTAREA' && activeElement.tagName !== 'INPUT')) {
      return;
    }

    const start = activeElement.selectionStart;
    const end = activeElement.selectionEnd;
    const selectedText = activeElement.value.substring(start, end);
    const suffixToUse = suffix || prefix;
    
    let newText;
    let newSelectionStart;
    let newSelectionEnd;
    
    if (selectedText) {
      // Text is selected, wrap it
      newText = prefix + selectedText + suffixToUse;
      newSelectionStart = start + prefix.length;
      newSelectionEnd = end + prefix.length;
    } else {
      // No selection, insert markers
      newText = prefix + suffixToUse;
      newSelectionStart = newSelectionEnd = start + prefix.length;
    }
    
    // Replace selected text
    const value = activeElement.value;
    activeElement.value = value.substring(0, start) + newText + value.substring(end);
    
    // Restore selection
    activeElement.setSelectionRange(newSelectionStart, newSelectionEnd);
    
    // Notify of change
    const event = new Event('input', { bubbles: true });
    activeElement.dispatchEvent(event);
  }

  /**
   * Get current context based on the active element
   */
  getCurrentContext(target) {
    if (!target) return 'global';
    
    // Check if we're in an editor
    if (target.classList.contains('note-editor') || 
        target.closest('.note-editor') ||
        (target.tagName === 'TEXTAREA' && target.classList.contains('editor'))) {
      return 'editor';
    }
    
    // Check if we're in the notes list
    if (target.closest('.notes-list') || target.classList.contains('note-item')) {
      return 'list';
    }
    
    return 'global';
  }

  /**
   * Check if shift key should be ignored for certain keys
   */
  isShiftIgnoredKey(key) {
    const shiftIgnoredKeys = ['`', '/', '[', ']'];
    return shiftIgnoredKeys.includes(key);
  }

  /**
   * Get all registered shortcuts
   */
  getShortcuts(context = null) {
    const shortcuts = Array.from(this.shortcuts.values());
    
    if (context) {
      return shortcuts.filter(s => s.context === context || s.context === 'global');
    }
    
    return shortcuts;
  }

  /**
   * Get shortcut by name
   */
  getShortcut(name) {
    return this.shortcuts.get(name);
  }

  /**
   * Format shortcut for display
   */
  formatShortcut(shortcut) {
    const parts = [];
    
    if (shortcut.meta) {
      parts.push(this.isMac() ? '⌘' : 'Ctrl');
    }
    
    if (shortcut.shift) {
      parts.push(this.isMac() ? '⇧' : 'Shift');
    }
    
    if (shortcut.alt) {
      parts.push(this.isMac() ? '⌥' : 'Alt');
    }
    
    // Format key name
    let keyName = shortcut.key;
    const keyMap = {
      'ArrowUp': '↑',
      'ArrowDown': '↓',
      'ArrowLeft': '←',
      'ArrowRight': '→',
      'Escape': 'Esc',
      'Delete': 'Del',
      ' ': 'Space'
    };
    
    if (keyMap[keyName]) {
      keyName = keyMap[keyName];
    }
    
    parts.push(keyName);
    
    return parts.join(this.isMac() ? '' : '+');
  }

  /**
   * Check if running on Mac
   */
  isMac() {
    return typeof window !== 'undefined' && 
           /Mac|iPod|iPhone|iPad/.test(window.navigator.platform);
  }

  /**
   * Add event listener
   */
  addEventListener(callback) {
    this.listeners.add(callback);
    return () => this.listeners.delete(callback);
  }

  /**
   * Remove event listener
   */
  removeEventListener(callback) {
    this.listeners.delete(callback);
  }

  /**
   * Notify all listeners
   */
  notifyListeners(event) {
    this.listeners.forEach(callback => {
      try {
        callback(event);
      } catch (error) {
        console.error('Error in shortcut listener:', error);
      }
    });
  }

  /**
   * Create a help dialog content
   */
  getHelpContent() {
    const shortcuts = this.getShortcuts();
    const contexts = ['global', 'editor', 'list'];
    
    const help = {};
    
    contexts.forEach(context => {
      help[context] = shortcuts
        .filter(s => s.context === context)
        .map(s => ({
          name: s.name,
          shortcut: this.formatShortcut(s),
          description: s.description
        }));
    });
    
    return help;
  }

  /**
   * Export shortcut configuration
   */
  exportConfig() {
    const config = {};
    
    this.shortcuts.forEach((shortcut, name) => {
      config[name] = {
        key: shortcut.key,
        meta: shortcut.meta,
        ctrl: shortcut.ctrl,
        shift: shortcut.shift,
        alt: shortcut.alt,
        enabled: shortcut.enabled,
        context: shortcut.context,
        description: shortcut.description
      };
    });
    
    return config;
  }

  /**
   * Import shortcut configuration
   */
  importConfig(config) {
    Object.entries(config).forEach(([name, shortcutConfig]) => {
      this.register(name, shortcutConfig);
    });
    
    return this;
  }
}

// Create singleton instance
const noteShortcuts = new NoteShortcuts();

// React hook for using shortcuts
export function useNoteShortcuts(callbacks = {}) {
  const React = require('react');
  const { useEffect } = React;
  
  useEffect(() => {
    // Register callbacks
    Object.entries(callbacks).forEach(([shortcutName, callback]) => {
      noteShortcuts.setCallback(shortcutName, callback);
    });

    // Start listening
    noteShortcuts.start();

    // Cleanup
    return () => {
      noteShortcuts.stop();
    };
  }, [callbacks]);

  return {
    shortcuts: noteShortcuts,
    registerShortcut: (name, config, callback) => noteShortcuts.register(name, config, callback),
    getShortcuts: () => noteShortcuts.getShortcuts(),
    formatShortcut: (shortcut) => noteShortcuts.formatShortcut(shortcut),
    getHelpContent: () => noteShortcuts.getHelpContent()
  };
}

export { noteShortcuts, SHORTCUT_KEYS };
export default NoteShortcuts;