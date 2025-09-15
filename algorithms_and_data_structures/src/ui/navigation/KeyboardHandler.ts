/**
 * KeyboardHandler - Keyboard input processing and shortcut management
 * Handles key bindings, input processing, and keyboard navigation
 */

import { EventEmitter } from 'events';
import {
  KeyBinding,
  NavigationConfig,
  NavigationEvent
} from '../../types/navigation.js';

export interface KeyboardState {
  currentModifiers: {
    ctrl: boolean;
    alt: boolean;
    shift: boolean;
    meta: boolean;
  };
  lastKeyPress?: KeyPress;
  isComposing: boolean;
  repeatCount: number;
}

export interface KeyPress {
  key: string;
  code: string;
  modifiers: {
    ctrl: boolean;
    alt: boolean;
    shift: boolean;
    meta: boolean;
  };
  timestamp: number;
  repeat: boolean;
}

export interface KeySequence {
  keys: KeyPress[];
  timeout: number;
  description?: string;
}

export class KeyboardHandler extends EventEmitter {
  private config: NavigationConfig;
  private state: KeyboardState;
  private keyBindings: Map<string, KeyBinding> = new Map();
  private sequenceBindings: Map<string, KeySequence> = new Map();
  private inputBuffer: string = '';
  private sequenceBuffer: KeyPress[] = [];
  private sequenceTimeout?: NodeJS.Timeout;
  private isActive: boolean = false;

  constructor(config: NavigationConfig) {
    super();
    
    this.config = config;
    this.state = {
      currentModifiers: {
        ctrl: false,
        alt: false,
        shift: false,
        meta: false
      },
      isComposing: false,
      repeatCount: 0
    };

    this.initializeDefaultBindings();
    this.setupEventListeners();
  }

  /**
   * Initialize default key bindings
   */
  private initializeDefaultBindings(): void {
    // Navigation bindings
    this.addBinding('navigate-up', { key: 'ArrowUp', description: 'Navigate up' });
    this.addBinding('navigate-down', { key: 'ArrowDown', description: 'Navigate down' });
    this.addBinding('navigate-left', { key: 'ArrowLeft', description: 'Navigate left/back' });
    this.addBinding('navigate-right', { key: 'ArrowRight', description: 'Navigate right/forward' });

    // Selection bindings
    this.addBinding('select', { key: 'Enter', description: 'Select current item' });
    this.addBinding('select-alt', { key: 'Space', description: 'Alternative select' });

    // Menu navigation
    this.addBinding('menu-back', { key: 'Escape', description: 'Go back/close menu' });
    this.addBinding('menu-home', { key: 'Home', description: 'Go to beginning' });
    this.addBinding('menu-end', { key: 'End', description: 'Go to end' });
    this.addBinding('page-up', { key: 'PageUp', description: 'Page up' });
    this.addBinding('page-down', { key: 'PageDown', description: 'Page down' });

    // Search and filter
    this.addBinding('search', { key: '/', ctrl: true, description: 'Start search' });
    this.addBinding('search-alt', { key: 's', ctrl: true, description: 'Alternative search' });
    this.addBinding('clear-search', { key: 'Escape', description: 'Clear search' });
    this.addBinding('filter', { key: 'f', ctrl: true, description: 'Open filter' });

    // Help and info
    this.addBinding('help', { key: 'F1', description: 'Show help' });
    this.addBinding('help-alt', { key: '?', description: 'Alternative help' });
    this.addBinding('info', { key: 'i', ctrl: true, description: 'Show info' });

    // Tab navigation
    this.addBinding('next-tab', { key: 'Tab', description: 'Next tab/section' });
    this.addBinding('prev-tab', { key: 'Tab', shift: true, description: 'Previous tab/section' });

    // Quick actions
    this.addBinding('refresh', { key: 'F5', description: 'Refresh' });
    this.addBinding('refresh-alt', { key: 'r', ctrl: true, description: 'Alternative refresh' });

    // Copy configuration bindings
    Object.entries(this.config.keyBindings).forEach(([action, binding]) => {
      this.addBinding(action, binding);
    });

    // Multi-key sequences
    this.addSequence('goto-line', [
      { key: 'g' },
      { key: 'g' }
    ], 1000, 'Go to line (vim-style)');

    this.addSequence('command-palette', [
      { key: 'p', ctrl: true },
      { key: 'p', ctrl: true }
    ], 800, 'Open command palette');
  }

  /**
   * Setup event listeners for keyboard input
   */
  private setupEventListeners(): void {
    // In a real implementation, this would attach to process.stdin or similar
    // For now, we'll simulate with a basic event system
  }

  /**
   * Add a key binding
   */
  addBinding(action: string, binding: KeyBinding): void {
    const key = this.createBindingKey(binding);
    this.keyBindings.set(key, { ...binding, description: binding.description || action });
    this.emit('binding-added', { action, binding });
  }

  /**
   * Remove a key binding
   */
  removeBinding(action: string): boolean {
    const binding = Array.from(this.keyBindings.entries())
      .find(([, b]) => b.description === action);
    
    if (binding) {
      this.keyBindings.delete(binding[0]);
      this.emit('binding-removed', action);
      return true;
    }
    
    return false;
  }

  /**
   * Add a key sequence binding
   */
  addSequence(action: string, keys: Partial<KeyPress>[], timeout: number = 1000, description?: string): void {
    const keyPresses = keys.map(k => ({
      key: k.key || '',
      code: k.code || '',
      modifiers: {
        ctrl: k.modifiers?.ctrl || false,
        alt: k.modifiers?.alt || false,
        shift: k.modifiers?.shift || false,
        meta: k.modifiers?.meta || false
      },
      timestamp: 0,
      repeat: false
    }));

    this.sequenceBindings.set(action, {
      keys: keyPresses,
      timeout,
      description
    });

    this.emit('sequence-added', { action, keys: keyPresses, timeout, description });
  }

  /**
   * Create a unique key for binding lookup
   */
  private createBindingKey(binding: KeyBinding): string {
    const parts = [];
    
    if (binding.ctrl) parts.push('ctrl');
    if (binding.alt) parts.push('alt');
    if (binding.shift) parts.push('shift');
    if (binding.meta) parts.push('meta');
    
    parts.push(binding.key.toLowerCase());
    
    return parts.join('+');
  }

  /**
   * Process keyboard input
   */
  processInput(input: string): void {
    if (!this.isActive) return;

    // Handle character input (for search, etc.)
    if (input.length === 1 && this.isCharacterInput(input)) {
      this.inputBuffer += input;
      this.emit('input-character', {
        character: input,
        buffer: this.inputBuffer,
        timestamp: Date.now()
      });
      return;
    }

    // Handle special keys
    this.processSpecialKey(input);
  }

  /**
   * Process key press event
   */
  processKeyPress(keyPress: KeyPress): void {
    if (!this.isActive) return;

    this.state.lastKeyPress = keyPress;
    this.updateModifierState(keyPress);

    // Check for direct key bindings
    const bindingKey = this.createBindingKeyFromPress(keyPress);
    const binding = this.keyBindings.get(bindingKey);
    
    if (binding) {
      this.executeBinding(binding, keyPress);
      return;
    }

    // Check for key sequences
    this.processKeySequence(keyPress);
  }

  /**
   * Create binding key from key press
   */
  private createBindingKeyFromPress(keyPress: KeyPress): string {
    const parts = [];
    
    if (keyPress.modifiers.ctrl) parts.push('ctrl');
    if (keyPress.modifiers.alt) parts.push('alt');
    if (keyPress.modifiers.shift) parts.push('shift');
    if (keyPress.modifiers.meta) parts.push('meta');
    
    parts.push(keyPress.key.toLowerCase());
    
    return parts.join('+');
  }

  /**
   * Update modifier key state
   */
  private updateModifierState(keyPress: KeyPress): void {
    this.state.currentModifiers = { ...keyPress.modifiers };
  }

  /**
   * Execute a key binding
   */
  private executeBinding(binding: KeyBinding, keyPress: KeyPress): void {
    const event: NavigationEvent = {
      type: 'shortcut',
      data: {
        binding,
        keyPress,
        action: binding.description
      },
      timestamp: Date.now(),
      source: 'keyboard'
    };

    this.emit('key-binding-executed', event);
    this.emit('navigation-event', event);
  }

  /**
   * Process key sequence matching
   */
  private processKeySequence(keyPress: KeyPress): void {
    this.sequenceBuffer.push(keyPress);
    
    // Clear old sequence timeout
    if (this.sequenceTimeout) {
      clearTimeout(this.sequenceTimeout);
    }

    // Check for sequence matches
    const matchedSequence = this.findMatchingSequence();
    
    if (matchedSequence) {
      const [action, sequence] = matchedSequence;
      this.executeSequence(action, sequence, [...this.sequenceBuffer]);
      this.clearSequenceBuffer();
      return;
    }

    // Set timeout to clear buffer
    this.sequenceTimeout = setTimeout(() => {
      this.clearSequenceBuffer();
    }, 1000);

    // Emit partial sequence event
    this.emit('sequence-partial', {
      buffer: [...this.sequenceBuffer],
      possibleMatches: this.getPossibleSequenceMatches()
    });
  }

  /**
   * Find matching key sequence
   */
  private findMatchingSequence(): [string, KeySequence] | null {
    for (const [action, sequence] of this.sequenceBindings) {
      if (this.sequenceMatches(sequence)) {
        return [action, sequence];
      }
    }
    return null;
  }

  /**
   * Check if current buffer matches sequence
   */
  private sequenceMatches(sequence: KeySequence): boolean {
    if (this.sequenceBuffer.length !== sequence.keys.length) {
      return false;
    }

    for (let i = 0; i < sequence.keys.length; i++) {
      const bufferKey = this.sequenceBuffer[i];
      const sequenceKey = sequence.keys[i];

      if (!this.keyPressMatches(bufferKey, sequenceKey)) {
        return false;
      }
    }

    return true;
  }

  /**
   * Check if key press matches expected key
   */
  private keyPressMatches(actual: KeyPress, expected: KeyPress): boolean {
    return actual.key.toLowerCase() === expected.key.toLowerCase() &&
           actual.modifiers.ctrl === expected.modifiers.ctrl &&
           actual.modifiers.alt === expected.modifiers.alt &&
           actual.modifiers.shift === expected.modifiers.shift &&
           actual.modifiers.meta === expected.modifiers.meta;
  }

  /**
   * Get possible sequence matches for current buffer
   */
  private getPossibleSequenceMatches(): string[] {
    const matches = [];
    
    for (const [action, sequence] of this.sequenceBindings) {
      if (this.isPartialSequenceMatch(sequence)) {
        matches.push(action);
      }
    }

    return matches;
  }

  /**
   * Check if current buffer is partial match for sequence
   */
  private isPartialSequenceMatch(sequence: KeySequence): boolean {
    if (this.sequenceBuffer.length >= sequence.keys.length) {
      return false;
    }

    for (let i = 0; i < this.sequenceBuffer.length; i++) {
      const bufferKey = this.sequenceBuffer[i];
      const sequenceKey = sequence.keys[i];

      if (!this.keyPressMatches(bufferKey, sequenceKey)) {
        return false;
      }
    }

    return true;
  }

  /**
   * Execute a key sequence
   */
  private executeSequence(action: string, sequence: KeySequence, keyPresses: KeyPress[]): void {
    const event: NavigationEvent = {
      type: 'shortcut',
      data: {
        action,
        sequence,
        keyPresses
      },
      timestamp: Date.now(),
      source: 'keyboard'
    };

    this.emit('sequence-executed', event);
    this.emit('navigation-event', event);
  }

  /**
   * Clear sequence buffer
   */
  private clearSequenceBuffer(): void {
    this.sequenceBuffer = [];
    if (this.sequenceTimeout) {
      clearTimeout(this.sequenceTimeout);
      this.sequenceTimeout = undefined;
    }
  }

  /**
   * Check if input is a character (for text input)
   */
  private isCharacterInput(input: string): boolean {
    return /^[\\w\\s\\-_.@#$%^&*()+={}\\[\\]|\\\\:";'<>?,./`~]$/.test(input);
  }

  /**
   * Process special key input
   */
  private processSpecialKey(key: string): void {
    const keyPress: KeyPress = {
      key,
      code: key,
      modifiers: { ...this.state.currentModifiers },
      timestamp: Date.now(),
      repeat: false
    };

    this.processKeyPress(keyPress);
  }

  /**
   * Clear input buffer
   */
  clearInputBuffer(): void {
    this.inputBuffer = '';
    this.emit('input-cleared');
  }

  /**
   * Get current input buffer
   */
  getInputBuffer(): string {
    return this.inputBuffer;
  }

  /**
   * Set input buffer
   */
  setInputBuffer(buffer: string): void {
    this.inputBuffer = buffer;
    this.emit('input-changed', buffer);
  }

  /**
   * Handle backspace in input
   */
  handleBackspace(): void {
    if (this.inputBuffer.length > 0) {
      this.inputBuffer = this.inputBuffer.slice(0, -1);
      this.emit('input-backspace', this.inputBuffer);
    }
  }

  /**
   * Get all key bindings
   */
  getBindings(): Map<string, KeyBinding> {
    return new Map(this.keyBindings);
  }

  /**
   * Get all sequence bindings
   */
  getSequenceBindings(): Map<string, KeySequence> {
    return new Map(this.sequenceBindings);
  }

  /**
   * Check if a key combination is bound
   */
  isBound(key: string, modifiers?: Partial<KeyBinding>): boolean {
    const binding: KeyBinding = {
      key,
      ctrl: modifiers?.ctrl || false,
      alt: modifiers?.alt || false,
      shift: modifiers?.shift || false,
      meta: modifiers?.meta || false
    };

    const bindingKey = this.createBindingKey(binding);
    return this.keyBindings.has(bindingKey);
  }

  /**
   * Get keyboard state
   */
  getState(): KeyboardState {
    return { ...this.state };
  }

  /**
   * Activate keyboard handler
   */
  activate(): void {
    this.isActive = true;
    this.emit('activated');
  }

  /**
   * Deactivate keyboard handler
   */
  deactivate(): void {
    this.isActive = false;
    this.clearInputBuffer();
    this.clearSequenceBuffer();
    this.emit('deactivated');
  }

  /**
   * Check if handler is active
   */
  isHandlerActive(): boolean {
    return this.isActive;
  }

  /**
   * Get help text for key bindings
   */
  getHelpText(): string[] {
    const lines = [];
    lines.push('Keyboard Shortcuts:');
    lines.push('==================');

    // Group bindings by category
    const categories: { [key: string]: KeyBinding[] } = {
      'Navigation': [],
      'Selection': [],
      'Search': [],
      'Help': [],
      'Other': []
    };

    for (const binding of this.keyBindings.values()) {
      const description = binding.description || 'Unknown';
      
      if (description.includes('navigate') || description.includes('Navigate')) {
        categories.Navigation.push(binding);
      } else if (description.includes('select') || description.includes('Select')) {
        categories.Selection.push(binding);
      } else if (description.includes('search') || description.includes('Search')) {
        categories.Search.push(binding);
      } else if (description.includes('help') || description.includes('Help')) {
        categories.Help.push(binding);
      } else {
        categories.Other.push(binding);
      }
    }

    // Format each category
    for (const [category, bindings] of Object.entries(categories)) {
      if (bindings.length === 0) continue;
      
      lines.push('');
      lines.push(`${category}:`);
      lines.push('-'.repeat(category.length + 1));
      
      for (const binding of bindings) {
        const shortcut = this.formatShortcut(binding);
        const description = binding.description || 'No description';
        lines.push(`  ${shortcut.padEnd(20)} ${description}`);
      }
    }

    // Add sequences
    if (this.sequenceBindings.size > 0) {
      lines.push('');
      lines.push('Key Sequences:');
      lines.push('==============');
      
      for (const [action, sequence] of this.sequenceBindings) {
        const keys = sequence.keys.map(k => k.key).join(' ');
        const description = sequence.description || action;
        lines.push(`  ${keys.padEnd(20)} ${description}`);
      }
    }

    return lines;
  }

  /**
   * Format shortcut for display
   */
  private formatShortcut(binding: KeyBinding): string {
    const parts = [];
    
    if (binding.ctrl) parts.push('Ctrl');
    if (binding.alt) parts.push('Alt');
    if (binding.shift) parts.push('Shift');
    if (binding.meta) parts.push('Cmd');
    
    parts.push(binding.key);
    
    return parts.join('+');
  }

  /**
   * Destroy keyboard handler
   */
  destroy(): void {
    this.deactivate();
    this.keyBindings.clear();
    this.sequenceBindings.clear();
    this.clearSequenceBuffer();
    this.removeAllListeners();
  }
}