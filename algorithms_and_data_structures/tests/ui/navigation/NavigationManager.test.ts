/**
 * NavigationManager Tests
 * Comprehensive test suite for the navigation manager
 */

import { describe, it, expect, beforeEach, afterEach } from '@jest/globals';
import { NavigationManager } from '../../../src/ui/navigation/NavigationManager.js';
import {
  NavigationNode,
  NavigationConfig,
  CommandNotFoundError,
  InvalidRouteError
} from '../../../src/types/navigation.js';

describe('NavigationManager', () => {
  let manager: NavigationManager;
  let mockConfig: Partial<NavigationConfig>;

  beforeEach(() => {
    mockConfig = {
      maxHistorySize: 10,
      searchDebounceMs: 100,
      fuzzySearchThreshold: 0.5,
      breadcrumbSeparator: ' > ',
      enableAnimations: false
    };

    manager = new NavigationManager(mockConfig);
  });

  afterEach(() => {
    manager.destroy();
  });

  describe('Node Management', () => {
    it('should add and retrieve nodes', () => {
      const node: NavigationNode = {
        id: 'test-node',
        label: 'Test Node',
        description: 'A test node',
        command: 'test',
        category: 'test'
      };

      manager.addNode(node);
      const retrieved = manager.getNode('test-node');

      expect(retrieved).toBeDefined();
      expect(retrieved!.id).toBe('test-node');
      expect(retrieved!.label).toBe('Test Node');
      expect(retrieved!.isVisible).toBe(true);
      expect(retrieved!.isEnabled).toBe(true);
    });

    it('should handle parent-child relationships', () => {
      const parent: NavigationNode = {
        id: 'parent',
        label: 'Parent Node'
      };

      const child: NavigationNode = {
        id: 'child',
        label: 'Child Node',
        parent: 'parent'
      };

      manager.addNode(parent);
      manager.addNode(child);

      const parentNode = manager.getNode('parent');
      const children = manager.getChildren('parent');

      expect(parentNode!.children).toContain('child');
      expect(children).toHaveLength(1);
      expect(children[0].id).toBe('child');
    });

    it('should remove nodes and clean up relationships', () => {
      const parent: NavigationNode = {
        id: 'parent',
        label: 'Parent Node'
      };

      const child: NavigationNode = {
        id: 'child',
        label: 'Child Node',
        parent: 'parent'
      };

      manager.addNode(parent);
      manager.addNode(child);

      const removed = manager.removeNode('child');
      const parentNode = manager.getNode('parent');
      const children = manager.getChildren('parent');

      expect(removed).toBe(true);
      expect(parentNode!.children).toHaveLength(0);
      expect(children).toHaveLength(0);
      expect(manager.getNode('child')).toBeUndefined();
    });

    it('should get root nodes when no parent specified', () => {
      const root1: NavigationNode = {
        id: 'root1',
        label: 'Root 1'
      };

      const root2: NavigationNode = {
        id: 'root2',
        label: 'Root 2'
      };

      const child: NavigationNode = {
        id: 'child',
        label: 'Child',
        parent: 'root1'
      };

      manager.addNode(root1);
      manager.addNode(root2);
      manager.addNode(child);

      const rootNodes = manager.getChildren();

      expect(rootNodes).toHaveLength(2);
      expect(rootNodes.map(n => n.id)).toEqual(expect.arrayContaining(['root1', 'root2']));
    });
  });

  describe('Command Routing', () => {
    it('should execute help command', async () => {
      const result = await manager.executeCommand('help');

      expect(result).toHaveProperty('availableCommands');
      expect(result).toHaveProperty('shortcuts');
      expect(result).toHaveProperty('currentContext');
    });

    it('should execute help with topic', async () => {
      // Add a test node first
      manager.addNode({
        id: 'test-topic',
        label: 'Test Topic',
        description: 'Test description'
      });

      const result = await manager.executeCommand('help test-topic');

      expect(result).toHaveProperty('topic', 'test-topic');
      expect(result).toHaveProperty('available', true);
    });

    it('should execute search command', async () => {
      // Add test nodes
      manager.addNode({
        id: 'search-test',
        label: 'Search Test',
        description: 'A test for searching'
      });

      const result = await manager.executeCommand('search test');

      expect(Array.isArray(result)).toBe(true);
      expect(result.length).toBeGreaterThan(0);
      expect(result[0].id).toBe('search-test');
    });

    it('should throw error for unknown command', async () => {
      await expect(manager.executeCommand('unknown-command'))
        .rejects.toThrow(CommandNotFoundError);
    });

    it('should navigate using cd command', async () => {
      const initialPath = manager.getState().currentPath;
      await manager.executeCommand('cd test/path');
      const newPath = manager.getState().currentPath;

      expect(initialPath).not.toEqual(newPath);
      expect(newPath).toEqual(['test', 'path']);
    });
  });

  describe('Navigation and History', () => {
    it('should update current path on navigation', () => {
      manager.navigateToPath('algorithms/sorting');
      const state = manager.getState();

      expect(state.currentPath).toEqual(['algorithms', 'sorting']);
    });

    it('should maintain navigation history', () => {
      manager.navigateToPath('path1');
      manager.navigateToPath('path2');
      manager.navigateToPath('path3');

      const state = manager.getState();
      expect(state.history).toContain('path1');
      expect(state.history).toContain('path2');
      expect(state.history).toContain('path3');
    });

    it('should navigate back in history', () => {
      manager.navigateToPath('path1');
      manager.navigateToPath('path2');
      manager.navigateBack();

      const state = manager.getState();
      expect(state.currentPath).toEqual(['path1']);
    });

    it('should update breadcrumbs on navigation', () => {
      manager.navigateToPath('level1/level2/level3');
      const state = manager.getState();

      expect(state.breadcrumbs).toHaveLength(4); // root + 3 levels
      expect(state.breadcrumbs[0].label).toBe('Home');
      expect(state.breadcrumbs[1].path).toBe('level1');
      expect(state.breadcrumbs[2].path).toBe('level1/level2');
      expect(state.breadcrumbs[3].path).toBe('level1/level2/level3');
    });

    it('should navigate to home', () => {
      manager.navigateToPath('some/deep/path');
      manager.navigateToHome();

      const state = manager.getState();
      expect(state.currentPath).toEqual([]);
    });

    it('should limit history size', () => {
      // Navigate to more paths than the limit
      for (let i = 0; i < 15; i++) {
        manager.navigateToPath(`path${i}`);
      }

      const state = manager.getState();
      expect(state.history.length).toBeLessThanOrEqual(mockConfig.maxHistorySize!);
    });
  });

  describe('Search Functionality', () => {
    beforeEach(() => {
      // Add test nodes for searching
      const testNodes: NavigationNode[] = [
        {
          id: 'algo-sort',
          label: 'Sorting Algorithms',
          description: 'Various sorting algorithms',
          category: 'algorithms',
          tags: ['sort', 'algorithm']
        },
        {
          id: 'algo-search',
          label: 'Search Algorithms',
          description: 'Binary search, linear search, etc.',
          category: 'algorithms',
          tags: ['search', 'algorithm']
        },
        {
          id: 'data-structures',
          label: 'Data Structures',
          description: 'Arrays, linked lists, trees',
          category: 'data',
          tags: ['structure', 'data']
        }
      ];

      testNodes.forEach(node => manager.addNode(node));
    });

    it('should find nodes by label', () => {
      const results = manager.executeSearch('sorting');

      expect(results.length).toBeGreaterThan(0);
      expect(results[0].id).toBe('algo-sort');
    });

    it('should find nodes by description', () => {
      const results = manager.executeSearch('binary');

      expect(results.length).toBeGreaterThan(0);
      expect(results[0].id).toBe('algo-search');
    });

    it('should find nodes by tags', () => {
      const results = manager.executeSearch('algorithm');

      expect(results.length).toBe(2);
      expect(results.map(r => r.id)).toEqual(
        expect.arrayContaining(['algo-sort', 'algo-search'])
      );
    });

    it('should return empty array for no matches', () => {
      const results = manager.executeSearch('nonexistent');

      expect(results).toEqual([]);
    });

    it('should be case insensitive', () => {
      const results = manager.executeSearch('SORTING');

      expect(results.length).toBeGreaterThan(0);
      expect(results[0].id).toBe('algo-sort');
    });
  });

  describe('Filtering and Sorting', () => {
    beforeEach(() => {
      const testNodes: NavigationNode[] = [
        {
          id: 'node1',
          label: 'Node 1',
          category: 'cat1',
          tags: ['tag1'],
          weight: 10,
          isEnabled: true,
          isVisible: true,
          command: 'command1'
        },
        {
          id: 'node2',
          label: 'Node 2',
          category: 'cat2',
          tags: ['tag2'],
          weight: 5,
          isEnabled: false,
          isVisible: true
        },
        {
          id: 'node3',
          label: 'Node 3',
          category: 'cat1',
          tags: ['tag1', 'tag3'],
          weight: 15,
          isEnabled: true,
          isVisible: false,
          shortcut: 'n3'
        }
      ];

      testNodes.forEach(node => manager.addNode(node));
    });

    it('should filter by category', () => {
      const filtered = manager.filterNodes({ categories: ['cat1'] });

      expect(filtered).toHaveLength(2);
      expect(filtered.map(n => n.id)).toEqual(
        expect.arrayContaining(['node1', 'node3'])
      );
    });

    it('should filter by enabled status', () => {
      const filtered = manager.filterNodes({ enabled: true });

      expect(filtered).toHaveLength(2);
      expect(filtered.map(n => n.id)).toEqual(
        expect.arrayContaining(['node1', 'node3'])
      );
    });

    it('should filter by visibility', () => {
      const filtered = manager.filterNodes({ visible: true });

      expect(filtered).toHaveLength(2);
      expect(filtered.map(n => n.id)).toEqual(
        expect.arrayContaining(['node1', 'node2'])
      );
    });

    it('should filter by tags', () => {
      const filtered = manager.filterNodes({ tags: ['tag1'] });

      expect(filtered).toHaveLength(2);
      expect(filtered.map(n => n.id)).toEqual(
        expect.arrayContaining(['node1', 'node3'])
      );
    });

    it('should filter by command presence', () => {
      const filtered = manager.filterNodes({ hasCommand: true });

      expect(filtered).toHaveLength(1);
      expect(filtered[0].id).toBe('node1');
    });

    it('should filter by shortcut presence', () => {
      const filtered = manager.filterNodes({ hasShortcut: true });

      expect(filtered).toHaveLength(1);
      expect(filtered[0].id).toBe('node3');
    });

    it('should sort by weight ascending', () => {
      const nodes = [
        manager.getNode('node1')!,
        manager.getNode('node2')!,
        manager.getNode('node3')!
      ];

      const sorted = manager.sortNodes(nodes, { field: 'weight', direction: 'asc' });

      expect(sorted.map(n => n.weight)).toEqual([5, 10, 15]);
    });

    it('should sort by weight descending', () => {
      const nodes = [
        manager.getNode('node1')!,
        manager.getNode('node2')!,
        manager.getNode('node3')!
      ];

      const sorted = manager.sortNodes(nodes, { field: 'weight', direction: 'desc' });

      expect(sorted.map(n => n.weight)).toEqual([15, 10, 5]);
    });

    it('should sort alphabetically', () => {
      const nodes = [
        manager.getNode('node3')!,
        manager.getNode('node1')!,
        manager.getNode('node2')!
      ];

      const sorted = manager.sortNodes(nodes, { field: 'alphabetical', direction: 'asc' });

      expect(sorted.map(n => n.label)).toEqual(['Node 1', 'Node 2', 'Node 3']);
    });
  });

  describe('Event Handling', () => {
    it('should emit navigation events', (done) => {
      manager.on('navigation-event', (event) => {
        expect(event.type).toBe('navigate');
        expect(event.data).toHaveProperty('to');
        expect(event.source).toBe('programmatic');
        done();
      });

      manager.navigateToPath('test/path');
    });

    it('should emit node-added events', (done) => {
      manager.on('node-added', (node) => {
        expect(node.id).toBe('test-node');
        done();
      });

      manager.addNode({
        id: 'test-node',
        label: 'Test Node'
      });
    });

    it('should allow registering custom event handlers', (done) => {
      manager.onNavigationEvent('navigate', (event) => {
        expect(event.type).toBe('navigate');
        done();
      });

      manager.navigateToPath('custom/path');
    });
  });

  describe('Configuration Management', () => {
    it('should return current configuration', () => {
      const config = manager.getConfig();

      expect(config.maxHistorySize).toBe(mockConfig.maxHistorySize);
      expect(config.breadcrumbSeparator).toBe(mockConfig.breadcrumbSeparator);
    });

    it('should update configuration', () => {
      manager.updateConfig({ maxHistorySize: 20 });
      const config = manager.getConfig();

      expect(config.maxHistorySize).toBe(20);
    });

    it('should emit config-updated events', (done) => {
      manager.on('config-updated', (config) => {
        expect(config.maxHistorySize).toBe(25);
        done();
      });

      manager.updateConfig({ maxHistorySize: 25 });
    });
  });

  describe('State Management', () => {
    it('should return current state', () => {
      manager.navigateToPath('test/path');
      const state = manager.getState();

      expect(state.currentPath).toEqual(['test', 'path']);
      expect(state.history).toContain('test/path');
      expect(state.breadcrumbs.length).toBeGreaterThan(0);
    });

    it('should reset state', () => {
      manager.navigateToPath('test/path');
      manager.reset();
      const state = manager.getState();

      expect(state.currentPath).toEqual([]);
      expect(state.history).toEqual([]);
      expect(state.breadcrumbs).toEqual([]);
    });
  });

  describe('Context Information', () => {
    it('should provide current context', () => {
      // Add test node
      manager.addNode({
        id: 'context-test',
        label: 'Context Test',
        children: ['child1', 'child2']
      });

      // Add child nodes
      manager.addNode({
        id: 'child1',
        label: 'Child 1',
        parent: 'context-test'
      });

      manager.addNode({
        id: 'child2',
        label: 'Child 2',
        parent: 'context-test'
      });

      manager.navigateToPath('context-test');
      const context = manager.getCurrentContext();

      expect(context.path).toEqual(['context-test']);
      expect(context.children).toHaveLength(2);
      expect(context.breadcrumbs.length).toBeGreaterThan(0);
    });
  });
});