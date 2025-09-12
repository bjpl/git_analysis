/**
 * KeyboardHandler Tests
 * Comprehensive test suite for keyboard input handling
 */

import { describe, it, expect, beforeEach, afterEach } from '@jest/globals';
import { KeyboardHandler, KeyPress } from '../../../src/ui/navigation/KeyboardHandler.js';
import { NavigationConfig, KeyBinding } from '../../../src/types/navigation.js';

describe('KeyboardHandler', () => {
  let handler: KeyboardHandler;
  let mockConfig: NavigationConfig;

  beforeEach(() => {
    mockConfig = {
      maxHistorySize: 50,
      searchDebounceMs: 200,
      fuzzySearchThreshold: 0.3,
      breadcrumbSeparator: ' › ',
      enableAnimations: true,
      keyBindings: {
        'custom-action': { key: 'c', ctrl: true, description: 'Custom action' }
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
      }
    };

    handler = new KeyboardHandler(mockConfig);
    handler.activate();
  });

  afterEach(() => {
    handler.destroy();
  });

  describe('Initialization', () => {
    it('should initialize with default bindings', () => {
      const bindings = handler.getBindings();
      
      expect(bindings.has('arrowup')).toBe(true);
      expect(bindings.has('arrowdown')).toBe(true);
      expect(bindings.has('enter')).toBe(true);
      expect(bindings.has('escape')).toBe(true);
      expect(bindings.has('ctrl+/')).toBe(true);
    });

    it('should include config bindings', () => {
      const bindings = handler.getBindings();
      
      expect(bindings.has('ctrl+c')).toBe(true);
      expect(bindings.get('ctrl+c')?.description).toBe('Custom action');
    });

    it('should initialize with default sequences', () => {
      const sequences = handler.getSequenceBindings();
      
      expect(sequences.has('goto-line')).toBe(true);
      expect(sequences.has('command-palette')).toBe(true);
    });

    it('should be inactive by default', () => {
      const newHandler = new KeyboardHandler(mockConfig);
      expect(newHandler.isHandlerActive()).toBe(false);
      newHandler.destroy();
    });
  });

  describe('Binding Management', () => {
    it('should add custom key bindings', () => {
      const binding: KeyBinding = {
        key: 'x',
        ctrl: true,
        shift: true,
        description: 'Test binding'
      };

      handler.addBinding('test-action', binding);
      const bindings = handler.getBindings();

      expect(bindings.has('ctrl+shift+x')).toBe(true);
      expect(bindings.get('ctrl+shift+x')?.description).toBe('Test binding');
    });

    it('should remove bindings by action', () => {
      const binding: KeyBinding = {
        key: 'r',
        alt: true,
        description: 'removable-action'
      };

      handler.addBinding('removable-action', binding);
      expect(handler.getBindings().has('alt+r')).toBe(true);

      const removed = handler.removeBinding('removable-action');
      expect(removed).toBe(true);
      expect(handler.getBindings().has('alt+r')).toBe(false);
    });

    it('should return false when removing non-existent binding', () => {
      const removed = handler.removeBinding('non-existent');
      expect(removed).toBe(false);
    });

    it('should emit binding events', () => {
      const addSpy = jest.fn();
      const removeSpy = jest.fn();

      handler.on('binding-added', addSpy);
      handler.on('binding-removed', removeSpy);

      const binding: KeyBinding = {
        key: 't',
        description: 'test'
      };

      handler.addBinding('test', binding);
      expect(addSpy).toHaveBeenCalledWith({ action: 'test', binding });

      handler.removeBinding('test');
      expect(removeSpy).toHaveBeenCalledWith('test');
    });
  });

  describe('Key Sequence Management', () => {
    it('should add key sequences', () => {
      const keys = [
        { key: 'a' },
        { key: 'b' }
      ];

      handler.addSequence('test-sequence', keys, 500, 'Test sequence');
      const sequences = handler.getSequenceBindings();

      expect(sequences.has('test-sequence')).toBe(true);
      expect(sequences.get('test-sequence')?.timeout).toBe(500);
    });

    it('should emit sequence-added events', () => {
      const spy = jest.fn();
      handler.on('sequence-added', spy);

      const keys = [{ key: 'x' }, { key: 'y' }];
      handler.addSequence('xy-sequence', keys);

      expect(spy).toHaveBeenCalledWith(
        expect.objectContaining({
          action: 'xy-sequence',
          keys: expect.any(Array)
        })
      );
    });
  });

  describe('Key Press Processing', () => {
    it('should process single key presses', () => {
      const eventSpy = jest.fn();
      handler.on('key-binding-executed', eventSpy);

      const keyPress: KeyPress = {
        key: 'Enter',
        code: 'Enter',
        modifiers: { ctrl: false, alt: false, shift: false, meta: false },
        timestamp: Date.now(),
        repeat: false
      };

      handler.processKeyPress(keyPress);

      expect(eventSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'shortcut',
          data: expect.objectContaining({
            keyPress,
            binding: expect.any(Object)
          })
        })
      );
    });

    it('should process modifier combinations', () => {
      const eventSpy = jest.fn();
      handler.on('key-binding-executed', eventSpy);

      const keyPress: KeyPress = {
        key: '/',
        code: 'Slash',
        modifiers: { ctrl: true, alt: false, shift: false, meta: false },
        timestamp: Date.now(),
        repeat: false
      };

      handler.processKeyPress(keyPress);

      expect(eventSpy).toHaveBeenCalled();
    });

    it('should ignore unbound keys', () => {
      const eventSpy = jest.fn();
      handler.on('key-binding-executed', eventSpy);

      const keyPress: KeyPress = {
        key: 'z',
        code: 'KeyZ',
        modifiers: { ctrl: false, alt: false, shift: false, meta: false },
        timestamp: Date.now(),
        repeat: false
      };

      handler.processKeyPress(keyPress);

      expect(eventSpy).not.toHaveBeenCalled();
    });

    it('should not process keys when inactive', () => {
      handler.deactivate();
      
      const eventSpy = jest.fn();
      handler.on('key-binding-executed', eventSpy);

      const keyPress: KeyPress = {
        key: 'Enter',
        code: 'Enter',
        modifiers: { ctrl: false, alt: false, shift: false, meta: false },
        timestamp: Date.now(),
        repeat: false
      };

      handler.processKeyPress(keyPress);

      expect(eventSpy).not.toHaveBeenCalled();
    });
  });

  describe('Key Sequence Processing', () => {
    it('should detect complete sequences', () => {
      const eventSpy = jest.fn();
      handler.on('sequence-executed', eventSpy);

      // Simulate 'gg' sequence for goto-line
      const keyPress1: KeyPress = {
        key: 'g',
        code: 'KeyG',
        modifiers: { ctrl: false, alt: false, shift: false, meta: false },
        timestamp: Date.now(),
        repeat: false
      };

      const keyPress2: KeyPress = {
        key: 'g',
        code: 'KeyG',
        modifiers: { ctrl: false, alt: false, shift: false, meta: false },
        timestamp: Date.now() + 100,
        repeat: false
      };

      handler.processKeyPress(keyPress1);
      handler.processKeyPress(keyPress2);

      expect(eventSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'shortcut',
          data: expect.objectContaining({
            action: 'goto-line'
          })
        })
      );
    });

    it('should emit partial sequence events', () => {
      const partialSpy = jest.fn();
      handler.on('sequence-partial', partialSpy);

      const keyPress: KeyPress = {
        key: 'g',
        code: 'KeyG',
        modifiers: { ctrl: false, alt: false, shift: false, meta: false },
        timestamp: Date.now(),
        repeat: false
      };

      handler.processKeyPress(keyPress);

      expect(partialSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          buffer: expect.any(Array),
          possibleMatches: expect.arrayContaining(['goto-line'])
        })
      );
    });

    it('should clear sequence buffer on timeout', (done) => {
      const keyPress: KeyPress = {
        key: 'g',
        code: 'KeyG',
        modifiers: { ctrl: false, alt: false, shift: false, meta: false },
        timestamp: Date.now(),
        repeat: false
      };

      handler.processKeyPress(keyPress);

      // Wait for timeout to clear buffer
      setTimeout(() => {
        const keyPress2: KeyPress = {
          key: 'g',
          code: 'KeyG',
          modifiers: { ctrl: false, alt: false, shift: false, meta: false },
          timestamp: Date.now(),
          repeat: false
        };

        const eventSpy = jest.fn();
        handler.on('sequence-executed', eventSpy);
        
        handler.processKeyPress(keyPress2);
        
        // Should not execute because buffer was cleared
        expect(eventSpy).not.toHaveBeenCalled();
        done();
      }, 1100); // Longer than default timeout
    });
  });

  describe('Input Buffer Management', () => {
    it('should handle character input', () => {
      const eventSpy = jest.fn();
      handler.on('input-character', eventSpy);

      handler.processInput('a');

      expect(handler.getInputBuffer()).toBe('a');
      expect(eventSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          character: 'a',
          buffer: 'a'
        })
      );
    });

    it('should accumulate characters in buffer', () => {
      handler.processInput('h');
      handler.processInput('e');
      handler.processInput('l');
      handler.processInput('l');
      handler.processInput('o');

      expect(handler.getInputBuffer()).toBe('hello');
    });

    it('should handle backspace', () => {
      handler.setInputBuffer('test');
      
      const eventSpy = jest.fn();
      handler.on('input-backspace', eventSpy);

      handler.handleBackspace();

      expect(handler.getInputBuffer()).toBe('tes');
      expect(eventSpy).toHaveBeenCalledWith('tes');
    });

    it('should not backspace empty buffer', () => {
      const eventSpy = jest.fn();
      handler.on('input-backspace', eventSpy);

      handler.handleBackspace();

      expect(handler.getInputBuffer()).toBe('');
      expect(eventSpy).not.toHaveBeenCalled();
    });

    it('should clear input buffer', () => {
      handler.setInputBuffer('test content');
      
      const eventSpy = jest.fn();
      handler.on('input-cleared', eventSpy);

      handler.clearInputBuffer();

      expect(handler.getInputBuffer()).toBe('');
      expect(eventSpy).toHaveBeenCalled();
    });

    it('should set input buffer', () => {
      const eventSpy = jest.fn();
      handler.on('input-changed', eventSpy);

      handler.setInputBuffer('new content');

      expect(handler.getInputBuffer()).toBe('new content');
      expect(eventSpy).toHaveBeenCalledWith('new content');
    });
  });

  describe('Binding Detection', () => {
    it('should detect if key combination is bound', () => {
      expect(handler.isBound('Enter')).toBe(true);
      expect(handler.isBound('/', { ctrl: true })).toBe(true);
      expect(handler.isBound('ArrowUp')).toBe(true);
      expect(handler.isBound('z')).toBe(false);
    });

    it('should detect bound keys with modifiers', () => {
      expect(handler.isBound('c', { ctrl: true })).toBe(true);
      expect(handler.isBound('c', { ctrl: false })).toBe(false);
      expect(handler.isBound('/', { ctrl: true })).toBe(true);
      expect(handler.isBound('/', { alt: true })).toBe(false);
    });
  });

  describe('State Management', () => {
    it('should track keyboard state', () => {
      const keyPress: KeyPress = {
        key: 'a',
        code: 'KeyA',
        modifiers: { ctrl: true, alt: false, shift: false, meta: false },
        timestamp: Date.now(),
        repeat: false
      };

      handler.processKeyPress(keyPress);
      const state = handler.getState();

      expect(state.currentModifiers.ctrl).toBe(true);
      expect(state.lastKeyPress).toEqual(keyPress);
    });

    it('should track composing state', () => {
      const state = handler.getState();
      expect(state.isComposing).toBe(false);
    });
  });

  describe('Activation and Deactivation', () => {
    it('should activate and deactivate', () => {
      handler.deactivate();
      expect(handler.isHandlerActive()).toBe(false);

      handler.activate();
      expect(handler.isHandlerActive()).toBe(true);
    });

    it('should emit activation events', () => {
      const activatedSpy = jest.fn();
      const deactivatedSpy = jest.fn();

      handler.on('activated', activatedSpy);
      handler.on('deactivated', deactivatedSpy);

      handler.deactivate();
      expect(deactivatedSpy).toHaveBeenCalled();

      handler.activate();
      expect(activatedSpy).toHaveBeenCalled();
    });

    it('should clear buffers on deactivation', () => {
      handler.setInputBuffer('test');
      expect(handler.getInputBuffer()).toBe('test');

      handler.deactivate();
      expect(handler.getInputBuffer()).toBe('');
    });
  });

  describe('Help System Integration', () => {
    it('should generate help text', () => {
      const helpLines = handler.getHelpText();

      expect(helpLines).toContain('Keyboard Shortcuts:');
      expect(helpLines.some(line => line.includes('Navigation:'))).toBe(true);
      expect(helpLines.some(line => line.includes('Selection:'))).toBe(true);
      expect(helpLines.some(line => line.includes('Search:'))).toBe(true);
    });

    it('should include key sequences in help', () => {
      const helpLines = handler.getHelpText();
      
      expect(helpLines.some(line => line.includes('Key Sequences:'))).toBe(true);
      expect(helpLines.some(line => line.includes('g g'))).toBe(true);
    });

    it('should format shortcuts correctly in help', () => {
      const helpLines = handler.getHelpText();
      
      // Should contain formatted shortcuts like "Ctrl+/"
      expect(helpLines.some(line => line.includes('Ctrl+/'))).toBe(true);
      expect(helpLines.some(line => line.includes('F1'))).toBe(true);
    });
  });

  describe('Event Emission', () => {
    it('should emit navigation events for shortcuts', () => {
      const navigationSpy = jest.fn();
      handler.on('navigation-event', navigationSpy);

      const keyPress: KeyPress = {
        key: 'Enter',
        code: 'Enter',
        modifiers: { ctrl: false, alt: false, shift: false, meta: false },
        timestamp: Date.now(),
        repeat: false
      };

      handler.processKeyPress(keyPress);

      expect(navigationSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'shortcut',
          source: 'keyboard'
        })
      );
    });

    it('should emit navigation events for sequences', () => {
      const navigationSpy = jest.fn();
      handler.on('navigation-event', navigationSpy);

      // Complete 'gg' sequence
      const keyPress1: KeyPress = {
        key: 'g',
        code: 'KeyG',
        modifiers: { ctrl: false, alt: false, shift: false, meta: false },
        timestamp: Date.now(),
        repeat: false
      };

      const keyPress2: KeyPress = {
        key: 'g',
        code: 'KeyG',
        modifiers: { ctrl: false, alt: false, shift: false, meta: false },
        timestamp: Date.now() + 50,
        repeat: false
      };

      handler.processKeyPress(keyPress1);
      handler.processKeyPress(keyPress2);

      expect(navigationSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'shortcut',
          source: 'keyboard',
          data: expect.objectContaining({
            action: 'goto-line'
          })
        })
      );
    });
  });

  describe('Error Handling and Edge Cases', () => {
    it('should handle invalid key presses gracefully', () => {
      const invalidKeyPress = {
        key: '',
        code: '',
        modifiers: { ctrl: false, alt: false, shift: false, meta: false },
        timestamp: Date.now(),
        repeat: false
      } as KeyPress;

      // Should not throw
      expect(() => {
        handler.processKeyPress(invalidKeyPress);
      }).not.toThrow();
    });

    it('should handle special characters in input', () => {
      const specialChars = ['!', '@', '#', '$', '%', '^', '&', '*'];
      
      specialChars.forEach(char => {
        handler.clearInputBuffer();
        handler.processInput(char);
        expect(handler.getInputBuffer()).toBe(char);
      });
    });

    it('should ignore non-character input for buffer', () => {
      const initialBuffer = handler.getInputBuffer();
      
      // Non-character inputs should not be added to buffer
      handler.processInput('\\x00'); // null character
      handler.processInput('\\x1B'); // escape character
      
      expect(handler.getInputBuffer()).toBe(initialBuffer);
    });
  });

  describe('Memory Management', () => {
    it('should clean up resources on destroy', () => {
      // Add some state
      handler.addBinding('temp', { key: 't' });
      handler.addSequence('temp-seq', [{ key: 'x' }]);
      handler.setInputBuffer('temp');

      handler.destroy();

      expect(handler.getBindings().size).toBe(0);
      expect(handler.getSequenceBindings().size).toBe(0);
      expect(handler.getInputBuffer()).toBe('');
      expect(handler.isHandlerActive()).toBe(false);
    });

    it('should remove all event listeners on destroy', () => {
      const spy = jest.fn();
      handler.on('test-event', spy);

      handler.destroy();
      handler.emit('test-event');

      expect(spy).not.toHaveBeenCalled();
    });
  });
});