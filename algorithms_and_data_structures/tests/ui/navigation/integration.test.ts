/**
 * Navigation System Integration Tests
 * Tests the complete navigation system working together
 */

import { describe, it, expect, beforeEach, afterEach } from '@jest/globals';
import { NavigationManager } from '../../../src/ui/navigation/NavigationManager.js';
import { MenuSystem } from '../../../src/ui/navigation/MenuSystem.js';
import { KeyboardHandler } from '../../../src/ui/navigation/KeyboardHandler.js';
import { HelpSystem } from '../../../src/ui/navigation/HelpSystem.js';
import {
  NavigationNode,
  NavigationConfig,
  MenuItem,
  KeyPress
} from '../../../src/types/navigation.js';

describe('Navigation System Integration', () => {
  let navigationManager: NavigationManager;
  let menuSystem: MenuSystem;
  let keyboardHandler: KeyboardHandler;
  let helpSystem: HelpSystem;
  let mockConfig: NavigationConfig;

  beforeEach(() => {
    mockConfig = {
      maxHistorySize: 50,
      searchDebounceMs: 100,
      fuzzySearchThreshold: 0.3,
      breadcrumbSeparator: ' › ',
      enableAnimations: false,
      keyBindings: {
        'custom-search': { key: 's', ctrl: true, description: 'Custom search' }
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

    // Initialize all components
    navigationManager = new NavigationManager(mockConfig);
    menuSystem = new MenuSystem(mockConfig);
    keyboardHandler = new KeyboardHandler(mockConfig);
    helpSystem = new HelpSystem(mockConfig);

    keyboardHandler.activate();
    
    setupTestData();
  });

  afterEach(() => {
    navigationManager.destroy();
    menuSystem.destroy();
    keyboardHandler.destroy();
    helpSystem.destroy();
  });

  function setupTestData(): void {
    // Add test navigation nodes
    const testNodes: NavigationNode[] = [
      {
        id: 'algorithms',
        label: 'Algorithms',
        description: 'Algorithm implementations and tutorials',
        category: 'learning',
        tags: ['algorithms', 'learning'],
        children: ['sorting', 'searching'],
        weight: 10
      },
      {
        id: 'sorting',
        label: 'Sorting Algorithms',
        description: 'Various sorting algorithm implementations',
        parent: 'algorithms',
        category: 'algorithms',
        tags: ['sort', 'algorithms'],
        command: 'show-sorting',
        shortcut: 'ctrl+s',
        weight: 8
      },
      {
        id: 'searching',
        label: 'Search Algorithms',
        description: 'Binary search, linear search implementations',
        parent: 'algorithms',
        category: 'algorithms',
        tags: ['search', 'algorithms'],
        command: 'show-searching',
        weight: 7
      },
      {
        id: 'data-structures',
        label: 'Data Structures',
        description: 'Data structure implementations',
        category: 'learning',
        tags: ['data', 'structures'],
        children: ['arrays', 'trees'],
        weight: 9
      },
      {
        id: 'arrays',
        label: 'Arrays',
        description: 'Array operations and algorithms',
        parent: 'data-structures',
        category: 'data-structures',
        tags: ['array', 'data'],
        command: 'show-arrays',
        weight: 6
      },
      {
        id: 'trees',
        label: 'Trees',
        description: 'Binary trees, BST, AVL trees',
        parent: 'data-structures',
        category: 'data-structures',
        tags: ['tree', 'data'],
        command: 'show-trees',
        weight: 5
      }
    ];

    testNodes.forEach(node => navigationManager.addNode(node));
  }

  describe('Complete Navigation Flow', () => {
    it('should handle complete navigation workflow', async () => {
      // 1. Navigate to algorithms section
      navigationManager.navigateToPath('algorithms');
      const state1 = navigationManager.getState();
      
      expect(state1.currentPath).toEqual(['algorithms']);
      expect(state1.breadcrumbs).toHaveLength(2); // Home + Algorithms

      // 2. Get children for menu display
      const children = navigationManager.getChildren('algorithms');
      const menuItems = menuSystem.nodesToMenuItems(children);
      menuSystem.setItems(menuItems);

      expect(menuItems).toHaveLength(2);
      expect(menuItems.map(item => item.id)).toEqual(['sorting', 'searching']);

      // 3. Render menu with breadcrumbs
      const menuOutput = menuSystem.renderMenu(menuItems, state1.breadcrumbs);
      
      expect(menuOutput).toContain('Sorting Algorithms');
      expect(menuOutput).toContain('Search Algorithms');
      expect(menuOutput).toContain('Home › Algorithms'); // Breadcrumbs

      // 4. Navigate deeper via command
      await navigationManager.executeCommand('cd algorithms/sorting');
      const state2 = navigationManager.getState();

      expect(state2.currentPath).toEqual(['algorithms', 'sorting']);
      expect(state2.breadcrumbs).toHaveLength(3);
    });

    it('should integrate search across all components', async () => {
      // 1. Perform search via navigation manager
      const searchResults = navigationManager.executeSearch('sort');
      
      expect(searchResults).toHaveLength(1);
      expect(searchResults[0].id).toBe('sorting');

      // 2. Convert to menu items
      const menuItems = menuSystem.nodesToMenuItems(searchResults);
      menuSystem.setItems(menuItems);

      // 3. Update menu search
      menuSystem.updateSearch('sort');
      const menuState = menuSystem.getState();

      expect(menuState.filteredItems).toHaveLength(1);
      expect(menuState.filteredItems[0].id).toBe('sorting');

      // 4. Search in help system
      const helpResults = helpSystem.searchHelp({
        query: 'sort',
        includeExamples: false,
        fuzzyThreshold: 0.1
      });

      expect(helpResults.length).toBeGreaterThan(0);
    });

    it('should handle keyboard navigation flow', () => {
      // Set up menu with test items
      const nodes = navigationManager.getChildren();
      const menuItems = menuSystem.nodesToMenuItems(nodes);
      menuSystem.setItems(menuItems);
      menuSystem.open();

      const initialState = menuSystem.getState();
      expect(initialState.selectedIndex).toBe(0);

      // Simulate arrow key navigation
      const arrowDownPress: KeyPress = {
        key: 'ArrowDown',
        code: 'ArrowDown',
        modifiers: { ctrl: false, alt: false, shift: false, meta: false },
        timestamp: Date.now(),
        repeat: false
      };

      // Capture navigation events
      let keyboardNavEvent: any = null;
      keyboardHandler.on('navigation-event', (event) => {
        keyboardNavEvent = event;
      });

      keyboardHandler.processKeyPress(arrowDownPress);

      expect(keyboardNavEvent).not.toBeNull();
      expect(keyboardNavEvent.type).toBe('shortcut');
      expect(keyboardNavEvent.data.binding.description).toContain('Navigate');
    });

    it('should provide contextual help integration', () => {
      // Navigate to a specific context
      navigationManager.navigateToPath('algorithms/sorting');
      const currentContext = navigationManager.getCurrentContext();
      
      // Get contextual help
      const helpContext = {
        currentNode: currentContext.node,
        availableCommands: ['show-sorting', 'back', 'home'],
        shortcuts: Object.values(mockConfig.keyBindings),
        suggestions: []
      };

      const contextualHelp = helpSystem.getContextualHelp(helpContext);

      expect(contextualHelp.primary.length).toBeGreaterThan(0);
      expect(contextualHelp.quickActions.length).toBeGreaterThan(0);
      expect(contextualHelp.shortcuts.length).toBeGreaterThan(0);
    });
  });

  describe('Cross-Component Event Handling', () => {
    it('should propagate navigation events between components', (done) => {
      let eventCount = 0;
      
      const checkComplete = () => {
        eventCount++;
        if (eventCount === 2) {
          done();
        }
      };

      // Listen for events from both components
      navigationManager.on('navigation-event', (event) => {
        expect(event.type).toBe('navigate');
        checkComplete();
      });

      keyboardHandler.on('navigation-event', (event) => {
        expect(event.type).toBe('shortcut');
        checkComplete();
      });

      // Trigger navigation from manager
      navigationManager.navigateToPath('algorithms');

      // Trigger keyboard shortcut
      const keyPress: KeyPress = {
        key: 'F1',
        code: 'F1',
        modifiers: { ctrl: false, alt: false, shift: false, meta: false },
        timestamp: Date.now(),
        repeat: false
      };

      keyboardHandler.processKeyPress(keyPress);
    });

    it('should handle menu selection triggering navigation', () => {
      const nodes = navigationManager.getChildren();
      const menuItems = menuSystem.nodesToMenuItems(nodes);
      
      // Track navigation changes
      let navigationTriggered = false;
      navigationManager.on('navigation-event', () => {
        navigationTriggered = true;
      });

      // Simulate menu item selection by calling its handler
      const algorithmItem = menuItems.find(item => item.id === 'algorithms');
      if (algorithmItem?.onSelect) {
        algorithmItem.onSelect();
      }

      expect(navigationTriggered).toBe(true);
    });
  });

  describe('State Synchronization', () => {
    it('should maintain consistent state across components', async () => {
      // Start with navigation
      navigationManager.navigateToPath('data-structures/arrays');
      const navState = navigationManager.getState();

      // Update menu to reflect navigation
      const children = navigationManager.getChildren('arrays');
      const menuItems = menuSystem.nodesToMenuItems(children);
      menuSystem.setItems(menuItems);

      // Perform search
      await navigationManager.executeCommand('search array');
      
      // Update menu search to match
      menuSystem.updateSearch('array');
      const menuState = menuSystem.getState();

      // States should be related
      expect(navState.currentPath).toEqual(['data-structures', 'arrays']);
      expect(menuState.searchQuery).toBe('array');
      expect(menuState.filteredItems.length).toBeGreaterThanOrEqual(0);
    });

    it('should handle back navigation across components', async () => {
      // Navigate to deep path
      navigationManager.navigateToPath('algorithms/sorting');
      
      // Execute back command
      await navigationManager.executeCommand('back');
      const state = navigationManager.getState();

      expect(state.currentPath).toEqual(['algorithms']);

      // Menu should update to show children of algorithms
      const children = navigationManager.getChildren('algorithms');
      expect(children).toHaveLength(2);
    });
  });

  describe('Performance and Efficiency', () => {
    it('should handle large datasets efficiently', () => {
      // Add many nodes
      const manyNodes: NavigationNode[] = Array.from({ length: 100 }, (_, i) => ({
        id: `node-${i}`,
        label: `Node ${i}`,
        description: `Description for node ${i}`,
        category: 'performance-test',
        tags: [`tag${i % 10}`],
        weight: i
      }));

      const startTime = Date.now();
      manyNodes.forEach(node => navigationManager.addNode(node));
      const addTime = Date.now() - startTime;

      // Should handle 100 nodes quickly
      expect(addTime).toBeLessThan(100);

      // Search should be efficient
      const searchStart = Date.now();
      const results = navigationManager.executeSearch('node');
      const searchTime = Date.now() - searchStart;

      expect(results.length).toBe(100);
      expect(searchTime).toBeLessThan(50);
    });

    it('should handle rapid keyboard input', () => {
      keyboardHandler.activate();
      
      const startTime = Date.now();
      
      // Simulate rapid typing
      for (let i = 0; i < 20; i++) {
        keyboardHandler.processInput(String.fromCharCode(97 + i % 26));
      }

      const endTime = Date.now();
      expect(endTime - startTime).toBeLessThan(50);
      expect(keyboardHandler.getInputBuffer().length).toBe(20);
    });
  });

  describe('Error Handling and Recovery', () => {
    it('should handle invalid navigation gracefully', async () => {
      // Try to navigate to non-existent path
      navigationManager.navigateToPath('invalid/path/here');
      
      // Should not crash and maintain state
      const state = navigationManager.getState();
      expect(state.currentPath).toEqual(['invalid', 'path', 'here']);
      
      // Breadcrumbs should still work
      expect(state.breadcrumbs.length).toBeGreaterThan(0);
    });

    it('should handle menu errors gracefully', () => {
      // Set invalid menu items
      const invalidItems: MenuItem[] = [
        {
          id: 'broken',
          label: 'Broken Item',
          type: 'command',
          onSelect: () => { throw new Error('Test error'); }
        }
      ];

      menuSystem.setItems(invalidItems);
      
      // Should not crash when selecting broken item
      expect(() => {
        menuSystem.selectCurrent();
      }).not.toThrow();
    });

    it('should recover from component failures', () => {
      // Simulate component destruction and recreation
      const originalNodeCount = Array.from(navigationManager['nodes'].keys()).length;
      
      // Destroy and recreate navigation manager
      navigationManager.destroy();
      navigationManager = new NavigationManager(mockConfig);
      
      // Should start fresh but not crash
      expect(navigationManager.getState().currentPath).toEqual([]);
      
      // Can add nodes again
      navigationManager.addNode({
        id: 'recovery-test',
        label: 'Recovery Test'
      });

      expect(navigationManager.getNode('recovery-test')).toBeDefined();
    });
  });

  describe('Accessibility and Usability', () => {
    it('should provide comprehensive help information', () => {
      // Test help integration
      const keyboardHelp = keyboardHandler.getHelpText();
      expect(keyboardHelp.length).toBeGreaterThan(10);
      expect(keyboardHelp.some(line => line.includes('Navigation:'))).toBe(true);

      // Test contextual help
      const context = navigationManager.getCurrentContext();
      const helpContext = {
        currentNode: context.node,
        availableCommands: Object.keys(mockConfig.keyBindings),
        shortcuts: Object.values(mockConfig.keyBindings),
        suggestions: []
      };

      const contextualHelp = helpSystem.getContextualHelp(helpContext);
      expect(contextualHelp.tips?.length).toBeGreaterThan(0);
    });

    it('should handle different interaction modes', () => {
      // Test keyboard-only interaction
      const keyboardOnlyFlow = () => {
        keyboardHandler.processInput('/'); // Start search
        keyboardHandler.processInput('s');
        keyboardHandler.processInput('o');
        keyboardHandler.processInput('r');
        keyboardHandler.processInput('t');
        
        return keyboardHandler.getInputBuffer();
      };

      expect(keyboardOnlyFlow()).toBe('/sort');

      // Test programmatic interaction
      const programmaticFlow = async () => {
        await navigationManager.executeCommand('search sort');
        return navigationManager.executeSearch('sort');
      };

      expect(programmaticFlow()).resolves.toHaveLength(1);
    });
  });
});