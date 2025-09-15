/**
 * MenuSystem Tests
 * Comprehensive test suite for the menu system
 */

import { describe, it, expect, beforeEach, afterEach } from '@jest/globals';
import { MenuSystem } from '../../../src/ui/navigation/MenuSystem.js';
import {
  MenuItem,
  NavigationNode,
  NavigationConfig,
  BreadcrumbItem
} from '../../../src/types/navigation.js';

describe('MenuSystem', () => {
  let menuSystem: MenuSystem;
  let mockConfig: NavigationConfig;

  beforeEach(() => {
    mockConfig = {
      maxHistorySize: 50,
      searchDebounceMs: 200,
      fuzzySearchThreshold: 0.3,
      breadcrumbSeparator: ' › ',
      enableAnimations: true,
      keyBindings: {},
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

    menuSystem = new MenuSystem(mockConfig, {
      showIcons: true,
      showShortcuts: true,
      showDescriptions: true,
      maxHeight: 10
    });
  });

  afterEach(() => {
    menuSystem.destroy();
  });

  describe('Menu Item Conversion', () => {
    it('should convert navigation nodes to menu items', () => {
      const nodes: NavigationNode[] = [
        {
          id: 'node1',
          label: 'Test Node 1',
          description: 'First test node',
          command: 'test1',
          shortcut: 'ctrl+1',
          icon: '🔧'
        },
        {
          id: 'node2',
          label: 'Test Node 2',
          description: 'Second test node',
          children: ['child1']
        }
      ];

      const menuItems = menuSystem.nodesToMenuItems(nodes);

      expect(menuItems).toHaveLength(2);
      expect(menuItems[0].id).toBe('node1');
      expect(menuItems[0].label).toBe('Test Node 1');
      expect(menuItems[0].type).toBe('command');
      expect(menuItems[1].id).toBe('node2');
      expect(menuItems[1].type).toBe('submenu');
    });

    it('should handle nodes without commands as headers', () => {
      const nodes: NavigationNode[] = [
        {
          id: 'header',
          label: 'Header Node',
          description: 'A header node'
        }
      ];

      const menuItems = menuSystem.nodesToMenuItems(nodes);

      expect(menuItems[0].type).toBe('header');
    });
  });

  describe('Menu Rendering', () => {
    let testMenuItems: MenuItem[];

    beforeEach(() => {
      testMenuItems = [
        {
          id: 'item1',
          label: 'First Item',
          description: 'Description for first item',
          type: 'command',
          command: 'first',
          shortcut: { key: '1', ctrl: true },
          icon: '📝',
          isVisible: true,
          isEnabled: true
        },
        {
          id: 'item2',
          label: 'Second Item',
          description: 'Description for second item',
          type: 'submenu',
          icon: '📁',
          children: [],
          isVisible: true,
          isEnabled: true
        },
        {
          id: 'item3',
          label: 'Disabled Item',
          description: 'This item is disabled',
          type: 'command',
          command: 'disabled',
          isVisible: true,
          isEnabled: false
        }
      ];

      menuSystem.setItems(testMenuItems);
    });

    it('should render basic menu structure', () => {
      const output = menuSystem.renderMenu(testMenuItems);

      expect(output).toContain('First Item');
      expect(output).toContain('Second Item');
      expect(output).toContain('Disabled Item');
    });

    it('should render breadcrumbs when enabled', () => {
      const breadcrumbs: BreadcrumbItem[] = [
        { id: 'root', label: 'Home', path: '', isClickable: true },
        { id: 'level1', label: 'Level 1', path: 'level1', isClickable: true },
        { id: 'level2', label: 'Level 2', path: 'level1/level2', isClickable: false }
      ];

      const output = menuSystem.renderMenu(testMenuItems, breadcrumbs);

      expect(output).toContain('Home');
      expect(output).toContain('Level 1');
      expect(output).toContain('Level 2');
      expect(output).toContain('›'); // breadcrumb separator
    });

    it('should render search box when enabled', () => {
      const output = menuSystem.renderMenu(testMenuItems);

      expect(output).toContain('🔍'); // search icon
      expect(output).toContain('Type to search');
    });

    it('should show help footer', () => {
      const output = menuSystem.renderMenu(testMenuItems);

      expect(output).toContain('Navigate');
      expect(output).toContain('Select');
      expect(output).toContain('Back');
      expect(output).toContain('Search');
      expect(output).toContain('Help');
    });

    it('should handle empty menu items', () => {
      const output = menuSystem.renderMenu([]);

      expect(output).toContain('No items to display');
    });

    it('should show scroll indicators when items exceed max height', () => {
      // Create more items than maxHeight
      const manyItems: MenuItem[] = Array.from({ length: 15 }, (_, i) => ({
        id: `item${i}`,
        label: `Item ${i}`,
        type: 'command' as const,
        isVisible: true,
        isEnabled: true
      }));

      menuSystem.setItems(manyItems);
      const output = menuSystem.renderMenu(manyItems);

      expect(output).toContain('More items below');
    });
  });

  describe('Menu Navigation', () => {
    beforeEach(() => {
      const testItems: MenuItem[] = [
        { id: 'item1', label: 'Item 1', type: 'command', isVisible: true, isEnabled: true },
        { id: 'item2', label: 'Item 2', type: 'command', isVisible: true, isEnabled: true },
        { id: 'item3', label: 'Item 3', type: 'command', isVisible: true, isEnabled: true }
      ];

      menuSystem.setItems(testItems);
    });

    it('should navigate up and down', () => {
      const initialState = menuSystem.getState();
      expect(initialState.selectedIndex).toBe(0);

      menuSystem.navigateDown();
      expect(menuSystem.getState().selectedIndex).toBe(1);

      menuSystem.navigateDown();
      expect(menuSystem.getState().selectedIndex).toBe(2);

      menuSystem.navigateUp();
      expect(menuSystem.getState().selectedIndex).toBe(1);

      menuSystem.navigateUp();
      expect(menuSystem.getState().selectedIndex).toBe(0);
    });

    it('should not navigate beyond bounds', () => {
      // Try to navigate up from first item
      menuSystem.navigateUp();
      expect(menuSystem.getState().selectedIndex).toBe(0);

      // Navigate to last item and try to go beyond
      menuSystem.navigateDown();
      menuSystem.navigateDown();
      menuSystem.navigateDown(); // Should stay at index 2
      expect(menuSystem.getState().selectedIndex).toBe(2);
    });

    it('should emit selection-changed events', (done) => {
      menuSystem.on('selection-changed', (index) => {
        expect(index).toBe(1);
        done();
      });

      menuSystem.navigateDown();
    });
  });

  describe('Search and Filtering', () => {
    beforeEach(() => {
      const searchableItems: MenuItem[] = [
        {
          id: 'algorithm',
          label: 'Sorting Algorithm',
          description: 'Various sorting methods',
          type: 'command',
          command: 'sort',
          isVisible: true,
          isEnabled: true
        },
        {
          id: 'structure',
          label: 'Data Structure',
          description: 'Trees, lists, and arrays',
          type: 'submenu',
          children: [],
          isVisible: true,
          isEnabled: true
        },
        {
          id: 'pattern',
          label: 'Design Pattern',
          description: 'Software design patterns',
          type: 'command',
          command: 'pattern',
          isVisible: true,
          isEnabled: true
        }
      ];

      menuSystem.setItems(searchableItems);
    });

    it('should filter items by search query', () => {
      menuSystem.updateSearch('sort');
      const state = menuSystem.getState();

      expect(state.filteredItems).toHaveLength(1);
      expect(state.filteredItems[0].id).toBe('algorithm');
    });

    it('should filter by label, description, and command', () => {
      // Test label match
      menuSystem.updateSearch('algorithm');
      expect(menuSystem.getState().filteredItems).toHaveLength(1);

      // Test description match
      menuSystem.updateSearch('trees');
      expect(menuSystem.getState().filteredItems).toHaveLength(1);
      expect(menuSystem.getState().filteredItems[0].id).toBe('structure');

      // Test command match
      menuSystem.updateSearch('pattern');
      expect(menuSystem.getState().filteredItems).toHaveLength(1);
      expect(menuSystem.getState().filteredItems[0].id).toBe('pattern');
    });

    it('should be case insensitive', () => {
      menuSystem.updateSearch('SORTING');
      const state = menuSystem.getState();

      expect(state.filteredItems).toHaveLength(1);
      expect(state.filteredItems[0].id).toBe('algorithm');
    });

    it('should reset selection when search changes', () => {
      menuSystem.navigateDown(); // Move to index 1
      expect(menuSystem.getState().selectedIndex).toBe(1);

      menuSystem.updateSearch('sort');
      expect(menuSystem.getState().selectedIndex).toBe(0);
    });

    it('should clear filter when search is empty', () => {
      menuSystem.updateSearch('sort');
      expect(menuSystem.getState().filteredItems).toHaveLength(1);

      menuSystem.updateSearch('');
      expect(menuSystem.getState().filteredItems).toHaveLength(3);
    });

    it('should emit search-updated events', (done) => {
      menuSystem.on('search-updated', (query) => {
        expect(query).toBe('test');
        done();
      });

      menuSystem.updateSearch('test');
    });
  });

  describe('Menu State Management', () => {
    it('should open and close menu', () => {
      expect(menuSystem.isOpen()).toBe(false);

      menuSystem.open();
      expect(menuSystem.isOpen()).toBe(true);

      menuSystem.close();
      expect(menuSystem.isOpen()).toBe(false);
    });

    it('should reset state on close', () => {
      const testItems: MenuItem[] = [
        { id: 'item1', label: 'Item 1', type: 'command', isVisible: true, isEnabled: true },
        { id: 'item2', label: 'Item 2', type: 'command', isVisible: true, isEnabled: true }
      ];

      menuSystem.setItems(testItems);
      menuSystem.navigateDown();
      menuSystem.updateSearch('test');

      expect(menuSystem.getState().selectedIndex).toBe(1);
      expect(menuSystem.getState().searchQuery).toBe('test');

      menuSystem.close();
      const state = menuSystem.getState();

      expect(state.selectedIndex).toBe(0);
      expect(state.searchQuery).toBe('');
    });

    it('should emit menu open/close events', () => {
      const openSpy = jest.fn();
      const closeSpy = jest.fn();

      menuSystem.on('menu-opened', openSpy);
      menuSystem.on('menu-closed', closeSpy);

      menuSystem.open();
      expect(openSpy).toHaveBeenCalled();

      menuSystem.close();
      expect(closeSpy).toHaveBeenCalled();
    });
  });

  describe('Item Selection and Interaction', () => {
    let testItems: MenuItem[];

    beforeEach(() => {
      testItems = [
        {
          id: 'selectable',
          label: 'Selectable Item',
          type: 'command',
          isVisible: true,
          isEnabled: true,
          onSelect: jest.fn()
        },
        {
          id: 'hoverable',
          label: 'Hoverable Item',
          type: 'command',
          isVisible: true,
          isEnabled: true,
          onHover: jest.fn()
        }
      ];

      menuSystem.setItems(testItems);
    });

    it('should call onSelect when item is selected', () => {
      menuSystem.selectCurrent();
      
      expect(testItems[0].onSelect).toHaveBeenCalled();
    });

    it('should emit item-selected events', (done) => {
      menuSystem.on('item-selected', (event) => {
        expect(event).toHaveProperty('timestamp');
        done();
      });

      // Simulate selection by calling the onSelect handler
      testItems[0].onSelect!();
    });

    it('should emit item-hovered events', (done) => {
      menuSystem.on('item-hovered', (event) => {
        expect(event).toHaveProperty('timestamp');
        done();
      });

      // Simulate hover by calling the onHover handler
      testItems[1].onHover!();
    });
  });

  describe('Submenu Expansion', () => {
    it('should toggle submenu expansion', () => {
      const state = menuSystem.getState();
      expect(state.expandedItems.has('submenu1')).toBe(false);

      menuSystem.toggleExpansion('submenu1');
      expect(menuSystem.getState().expandedItems.has('submenu1')).toBe(true);

      menuSystem.toggleExpansion('submenu1');
      expect(menuSystem.getState().expandedItems.has('submenu1')).toBe(false);
    });

    it('should emit expansion-changed events', (done) => {
      menuSystem.on('expansion-changed', (event) => {
        expect(event.itemId).toBe('submenu1');
        expect(event.expanded).toBe(true);
        done();
      });

      menuSystem.toggleExpansion('submenu1');
    });
  });

  describe('Display Options', () => {
    it('should update display options', () => {
      const initialOptions = menuSystem.getDisplayOptions();
      expect(initialOptions.showIcons).toBe(true);

      menuSystem.updateDisplayOptions({ showIcons: false });
      const updatedOptions = menuSystem.getDisplayOptions();
      expect(updatedOptions.showIcons).toBe(false);
    });

    it('should emit display-options-updated events', (done) => {
      menuSystem.on('display-options-updated', (options) => {
        expect(options.showShortcuts).toBe(false);
        done();
      });

      menuSystem.updateDisplayOptions({ showShortcuts: false });
    });
  });

  describe('Menu Clearing and Reset', () => {
    beforeEach(() => {
      const testItems: MenuItem[] = [
        { id: 'item1', label: 'Item 1', type: 'command', isVisible: true, isEnabled: true }
      ];

      menuSystem.setItems(testItems);
      menuSystem.navigateDown();
      menuSystem.updateSearch('test');
      menuSystem.toggleExpansion('submenu');
    });

    it('should clear all menu state', () => {
      menuSystem.clear();
      const state = menuSystem.getState();

      expect(state.originalItems).toEqual([]);
      expect(state.filteredItems).toEqual([]);
      expect(state.selectedIndex).toBe(0);
      expect(state.scrollOffset).toBe(0);
      expect(state.searchQuery).toBe('');
      expect(state.expandedItems.size).toBe(0);
    });

    it('should emit menu-cleared events', (done) => {
      menuSystem.on('menu-cleared', () => {
        done();
      });

      menuSystem.clear();
    });
  });

  describe('Scroll Management', () => {
    beforeEach(() => {
      // Create many items to test scrolling
      const manyItems: MenuItem[] = Array.from({ length: 20 }, (_, i) => ({
        id: `item${i}`,
        label: `Item ${i}`,
        type: 'command' as const,
        isVisible: true,
        isEnabled: true
      }));

      menuSystem.setItems(manyItems);
    });

    it('should scroll when selection moves beyond visible area', () => {
      const initialState = menuSystem.getState();
      expect(initialState.scrollOffset).toBe(0);

      // Navigate beyond visible area (maxHeight = 10)
      for (let i = 0; i < 12; i++) {
        menuSystem.navigateDown();
      }

      const finalState = menuSystem.getState();
      expect(finalState.scrollOffset).toBeGreaterThan(0);
    });

    it('should scroll up when selection moves above visible area', () => {
      // First navigate down to create scroll
      for (let i = 0; i < 15; i++) {
        menuSystem.navigateDown();
      }

      const scrolledState = menuSystem.getState();
      const scrollOffset = scrolledState.scrollOffset;

      // Navigate back up
      for (let i = 0; i < 10; i++) {
        menuSystem.navigateUp();
      }

      const finalState = menuSystem.getState();
      expect(finalState.scrollOffset).toBeLessThan(scrollOffset);
    });
  });

  describe('Error Handling and Edge Cases', () => {
    it('should handle selection when no items exist', () => {
      menuSystem.setItems([]);
      
      // These should not throw errors
      menuSystem.navigateUp();
      menuSystem.navigateDown();
      menuSystem.selectCurrent();
    });

    it('should handle invisible items correctly', () => {
      const itemsWithInvisible: MenuItem[] = [
        { id: 'visible1', label: 'Visible 1', type: 'command', isVisible: true, isEnabled: true },
        { id: 'invisible', label: 'Invisible', type: 'command', isVisible: false, isEnabled: true },
        { id: 'visible2', label: 'Visible 2', type: 'command', isVisible: true, isEnabled: true }
      ];

      menuSystem.setItems(itemsWithInvisible);
      const output = menuSystem.renderMenu(itemsWithInvisible);

      expect(output).toContain('Visible 1');
      expect(output).not.toContain('Invisible');
      expect(output).toContain('Visible 2');
    });

    it('should handle items with missing properties gracefully', () => {
      const minimalItems: MenuItem[] = [
        { id: 'minimal', label: 'Minimal', type: 'command' }
      ];

      menuSystem.setItems(minimalItems);
      const output = menuSystem.renderMenu(minimalItems);

      expect(output).toContain('Minimal');
    });
  });
});