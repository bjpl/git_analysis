/**
 * HelpSystem Tests
 * Comprehensive test suite for the help system
 */

import { describe, it, expect, beforeEach, afterEach } from '@jest/globals';
import { HelpSystem } from '../../../src/ui/navigation/HelpSystem.js';
import {
  NavigationConfig,
  HelpContext,
  NavigationNode
} from '../../../src/types/navigation.js';

describe('HelpSystem', () => {
  let helpSystem: HelpSystem;
  let mockConfig: NavigationConfig;

  beforeEach(() => {
    mockConfig = {
      maxHistorySize: 50,
      searchDebounceMs: 200,
      fuzzySearchThreshold: 0.3,
      breadcrumbSeparator: ' › ',
      enableAnimations: true,
      keyBindings: {
        'search': { key: '/', ctrl: true, description: 'Search' },
        'help': { key: 'F1', description: 'Help' }
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

    helpSystem = new HelpSystem(mockConfig);
  });

  afterEach(() => {
    helpSystem.destroy();
  });

  describe('Initialization', () => {
    it('should initialize with default help entries', () => {
      const stats = helpSystem.getStatistics();
      
      expect(stats.totalEntries).toBeGreaterThan(0);
      expect(stats.totalQuickActions).toBeGreaterThan(0);
      expect(stats.categories).toContain('navigation');
      expect(stats.categories).toContain('shortcuts');
    });

    it('should have built search index', () => {
      const stats = helpSystem.getStatistics();
      expect(stats.searchIndexSize).toBeGreaterThan(0);
    });

    it('should have default quick actions', () => {
      const stats = helpSystem.getStatistics();
      expect(stats.totalQuickActions).toBeGreaterThanOrEqual(4); // search, help, back, home
    });
  });

  describe('Help Entry Management', () => {
    it('should add help entries', () => {
      const entry = {
        id: 'test-entry',
        title: 'Test Entry',
        content: 'This is a test entry for the help system.',
        category: 'testing',
        tags: ['test', 'example'],
        difficulty: 'beginner' as const
      };

      const eventSpy = jest.fn();
      helpSystem.on('help-entry-added', eventSpy);

      helpSystem.addHelpEntry(entry);

      expect(helpSystem.getHelpEntry('test-entry')).toBeDefined();
      expect(helpSystem.getHelpEntry('test-entry')?.title).toBe('Test Entry');
      expect(eventSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          id: 'test-entry',
          title: 'Test Entry'
        })
      );
    });

    it('should remove help entries', () => {
      const entry = {
        id: 'removable-entry',
        title: 'Removable Entry',
        content: 'This entry will be removed.',
        category: 'testing',
        tags: ['removable']
      };

      helpSystem.addHelpEntry(entry);
      expect(helpSystem.getHelpEntry('removable-entry')).toBeDefined();

      const eventSpy = jest.fn();
      helpSystem.on('help-entry-removed', eventSpy);

      const removed = helpSystem.removeHelpEntry('removable-entry');

      expect(removed).toBe(true);
      expect(helpSystem.getHelpEntry('removable-entry')).toBeUndefined();
      expect(eventSpy).toHaveBeenCalledWith('removable-entry');
    });

    it('should return false when removing non-existent entry', () => {
      const removed = helpSystem.removeHelpEntry('non-existent');
      expect(removed).toBe(false);
    });

    it('should set lastUpdated when adding entries', () => {
      const entry = {
        id: 'dated-entry',
        title: 'Dated Entry',
        content: 'Entry with date.',
        category: 'testing',
        tags: []
      };

      helpSystem.addHelpEntry(entry);
      const retrieved = helpSystem.getHelpEntry('dated-entry');

      expect(retrieved?.lastUpdated).toBeInstanceOf(Date);
    });
  });

  describe('Quick Action Management', () => {
    it('should add quick actions', () => {
      const action = {
        id: 'test-action',
        label: 'Test Action',
        description: 'A test quick action',
        command: 'test-command',
        category: 'testing'
      };

      const eventSpy = jest.fn();
      helpSystem.on('quick-action-added', eventSpy);

      helpSystem.addQuickAction(action);

      expect(eventSpy).toHaveBeenCalledWith(action);
    });
  });

  describe('Contextual Help Generation', () => {
    let testContext: HelpContext;

    beforeEach(() => {
      // Add test help entries
      helpSystem.addHelpEntry({
        id: 'algorithm-help',
        title: 'Algorithm Help',
        content: 'Help for algorithms.',
        category: 'algorithms',
        tags: ['algorithm', 'sorting'],
        difficulty: 'intermediate'
      });

      helpSystem.addHelpEntry({
        id: 'search-help',
        title: 'Search Help',
        content: 'How to search effectively.',
        category: 'search',
        tags: ['search', 'find'],
        difficulty: 'beginner'
      });

      testContext = {
        currentNode: {
          id: 'current-node',
          label: 'Current Node',
          category: 'algorithms',
          tags: ['algorithm'],
          description: 'The current navigation node'
        },
        availableCommands: ['search', 'help', 'navigate'],
        shortcuts: [
          { key: '/', ctrl: true, description: 'Search' },
          { key: 'F1', description: 'Help' }
        ],
        suggestions: ['Try using search', 'Check the help section']
      };
    });

    it('should generate contextual help', () => {
      const contextualHelp = helpSystem.getContextualHelp(testContext);

      expect(contextualHelp).toHaveProperty('primary');
      expect(contextualHelp).toHaveProperty('suggestions');
      expect(contextualHelp).toHaveProperty('quickActions');
      expect(contextualHelp).toHaveProperty('shortcuts');
      expect(contextualHelp).toHaveProperty('tips');
    });

    it('should find help for current node category', () => {
      const contextualHelp = helpSystem.getContextualHelp(testContext);

      // Should find algorithm-help because context node is in 'algorithms' category
      expect(contextualHelp.primary.some(entry => entry.id === 'algorithm-help')).toBe(true);
    });

    it('should include relevant shortcuts', () => {
      const contextualHelp = helpSystem.getContextualHelp(testContext);

      expect(contextualHelp.shortcuts.length).toBeGreaterThan(0);
      expect(contextualHelp.shortcuts.some(shortcut => shortcut.key === '/')).toBe(true);
    });

    it('should provide contextual quick actions', () => {
      const contextualHelp = helpSystem.getContextualHelp(testContext);

      expect(contextualHelp.quickActions.length).toBeGreaterThan(0);
      expect(contextualHelp.quickActions.some(action => action.category === 'navigation')).toBe(true);
    });

    it('should maintain context history', () => {
      helpSystem.getContextualHelp(testContext);
      helpSystem.getContextualHelp({
        ...testContext,
        currentNode: { ...testContext.currentNode!, id: 'different-node' }
      });

      const stats = helpSystem.getStatistics();
      expect(stats.contextHistorySize).toBe(2);
    });

    it('should emit contextual-help-generated events', () => {
      const eventSpy = jest.fn();
      helpSystem.on('contextual-help-generated', eventSpy);

      helpSystem.getContextualHelp(testContext);

      expect(eventSpy).toHaveBeenCalled();
    });
  });

  describe('Help Search', () => {
    beforeEach(() => {
      // Add searchable entries
      helpSystem.addHelpEntry({
        id: 'sorting-algorithms',
        title: 'Sorting Algorithms',
        content: 'Learn about bubble sort, quick sort, and merge sort algorithms.',
        category: 'algorithms',
        tags: ['sort', 'algorithm', 'bubble', 'quick', 'merge'],
        difficulty: 'intermediate'
      });

      helpSystem.addHelpEntry({
        id: 'search-techniques',
        title: 'Search Techniques',
        content: 'Binary search and linear search methods.',
        category: 'algorithms',
        tags: ['search', 'binary', 'linear'],
        difficulty: 'beginner'
      });

      helpSystem.addHelpEntry({
        id: 'navigation-basics',
        title: 'Navigation Basics',
        content: 'How to navigate through the interface.',
        category: 'navigation',
        tags: ['nav', 'basics'],
        difficulty: 'beginner'
      });
    });

    it('should find entries by title', () => {
      const results = helpSystem.searchHelp({
        query: 'sorting',
        includeExamples: false,
        fuzzyThreshold: 0.1
      });

      expect(results.length).toBeGreaterThan(0);
      expect(results[0].item.id).toBe('sorting-algorithms');
      expect(results[0].matchType).toBe('prefix');
    });

    it('should find entries by content', () => {
      const results = helpSystem.searchHelp({
        query: 'bubble',
        includeExamples: false,
        fuzzyThreshold: 0.1
      });

      expect(results.length).toBeGreaterThan(0);
      expect(results[0].item.id).toBe('sorting-algorithms');
    });

    it('should find entries by tags', () => {
      const results = helpSystem.searchHelp({
        query: 'binary',
        includeExamples: false,
        fuzzyThreshold: 0.1
      });

      expect(results.length).toBeGreaterThan(0);
      expect(results[0].item.id).toBe('search-techniques');
    });

    it('should filter by category', () => {
      const results = helpSystem.searchHelp({
        query: 'nav',
        category: 'navigation',
        includeExamples: false,
        fuzzyThreshold: 0.1
      });

      expect(results.length).toBe(1);
      expect(results[0].item.id).toBe('navigation-basics');
    });

    it('should filter by difficulty', () => {
      const results = helpSystem.searchHelp({
        query: 'algorithm',
        difficulty: 'beginner',
        includeExamples: false,
        fuzzyThreshold: 0.1
      });

      expect(results.length).toBe(1);
      expect(results[0].item.id).toBe('search-techniques');
    });

    it('should return results sorted by relevance', () => {
      const results = helpSystem.searchHelp({
        query: 'search',
        includeExamples: false,
        fuzzyThreshold: 0.1
      });

      expect(results.length).toBeGreaterThan(1);
      // First result should have higher score
      expect(results[0].score).toBeGreaterThanOrEqual(results[1].score);
    });

    it('should provide highlights for matches', () => {
      const results = helpSystem.searchHelp({
        query: 'sorting',
        includeExamples: false,
        fuzzyThreshold: 0.1
      });

      expect(results[0].highlights).toBeDefined();
      expect(results[0].highlights!.length).toBeGreaterThan(0);
      expect(results[0].highlights![0]).toHaveProperty('field');
      expect(results[0].highlights![0]).toHaveProperty('start');
      expect(results[0].highlights![0]).toHaveProperty('end');
    });

    it('should handle fuzzy matching', () => {
      const results = helpSystem.searchHelp({
        query: 'srch', // fuzzy match for 'search'
        includeExamples: false,
        fuzzyThreshold: 0.1
      });

      expect(results.length).toBeGreaterThan(0);
      expect(results.some(r => r.matchType === 'fuzzy')).toBe(true);
    });

    it('should return empty results for no matches', () => {
      const results = helpSystem.searchHelp({
        query: 'nonexistent-topic',
        includeExamples: false,
        fuzzyThreshold: 0.5
      });

      expect(results).toEqual([]);
    });
  });

  describe('Category-based Help', () => {
    beforeEach(() => {
      helpSystem.addHelpEntry({
        id: 'nav-1',
        title: 'Navigation Entry 1',
        content: 'Navigation content 1',
        category: 'navigation',
        tags: []
      });

      helpSystem.addHelpEntry({
        id: 'nav-2',
        title: 'Navigation Entry 2',
        content: 'Navigation content 2',
        category: 'navigation',
        tags: []
      });

      helpSystem.addHelpEntry({
        id: 'search-1',
        title: 'Search Entry 1',
        content: 'Search content 1',
        category: 'search',
        tags: []
      });
    });

    it('should get help entries by category', () => {
      const navigationHelp = helpSystem.getHelpByCategory('navigation');
      const searchHelp = helpSystem.getHelpByCategory('search');

      expect(navigationHelp.length).toBe(3); // 2 added + 1 default
      expect(searchHelp.length).toBe(2); // 1 added + 1 default
      expect(navigationHelp.every(entry => entry.category === 'navigation')).toBe(true);
      expect(searchHelp.every(entry => entry.category === 'search')).toBe(true);
    });

    it('should return empty array for non-existent category', () => {
      const result = helpSystem.getHelpByCategory('non-existent');
      expect(result).toEqual([]);
    });
  });

  describe('Statistics and Analytics', () => {
    it('should provide accurate statistics', () => {
      const initialStats = helpSystem.getStatistics();

      // Add test entries
      helpSystem.addHelpEntry({
        id: 'test-stat-1',
        title: 'Test Stat 1',
        content: 'Content 1',
        category: 'test-category',
        tags: []
      });

      helpSystem.addQuickAction({
        id: 'test-action-1',
        label: 'Test Action',
        description: 'Test',
        command: 'test',
        category: 'test'
      });

      const newStats = helpSystem.getStatistics();

      expect(newStats.totalEntries).toBe(initialStats.totalEntries + 1);
      expect(newStats.totalQuickActions).toBe(initialStats.totalQuickActions + 1);
      expect(newStats.categories).toContain('test-category');
    });
  });

  describe('Data Export and Import', () => {
    it('should export help content', () => {
      const exported = helpSystem.exportHelp();

      expect(exported).toHaveProperty('entries');
      expect(exported).toHaveProperty('quickActions');
      expect(exported).toHaveProperty('timestamp');
      expect(Array.isArray(exported.entries)).toBe(true);
      expect(Array.isArray(exported.quickActions)).toBe(true);
    });

    it('should import help content', () => {
      const testData = {
        entries: [
          ['imported-entry', {
            id: 'imported-entry',
            title: 'Imported Entry',
            content: 'Imported content',
            category: 'imported',
            tags: ['import'],
            difficulty: 'beginner'
          }]
        ],
        quickActions: [
          ['imported-action', {
            id: 'imported-action',
            label: 'Imported Action',
            description: 'Imported',
            command: 'import',
            category: 'imported'
          }]
        ]
      };

      const eventSpy = jest.fn();
      helpSystem.on('help-imported', eventSpy);

      helpSystem.importHelp(testData);

      expect(helpSystem.getHelpEntry('imported-entry')).toBeDefined();
      expect(eventSpy).toHaveBeenCalledWith(testData);
    });

    it('should rebuild search index after import', () => {
      const testData = {
        entries: [
          ['searchable-import', {
            id: 'searchable-import',
            title: 'Searchable Import',
            content: 'This can be searched',
            category: 'imported',
            tags: ['searchable']
          }]
        ],
        quickActions: []
      };

      helpSystem.importHelp(testData);

      const results = helpSystem.searchHelp({
        query: 'searchable',
        includeExamples: false,
        fuzzyThreshold: 0.1
      });

      expect(results.length).toBeGreaterThan(0);
      expect(results[0].item.id).toBe('searchable-import');
    });
  });

  describe('Skill Level Inference', () => {
    it('should provide appropriate suggestions based on inferred skill level', () => {
      // Create contexts that simulate beginner usage
      const beginnerContexts = Array.from({ length: 5 }, (_, i) => ({
        currentNode: { id: `node${i}`, label: `Node ${i}` },
        availableCommands: ['help', 'back'], // Limited commands suggest beginner
        shortcuts: [],
        suggestions: []
      }));

      // Generate contextual help multiple times to build history
      beginnerContexts.forEach(context => {
        helpSystem.getContextualHelp(context);
      });

      const contextualHelp = helpSystem.getContextualHelp(beginnerContexts[0]);

      // Should include beginner-appropriate suggestions
      expect(contextualHelp.suggestions.some(s => s.difficulty === 'beginner')).toBe(true);
    });
  });

  describe('Memory Management', () => {
    it('should clear all content', () => {
      helpSystem.addHelpEntry({
        id: 'temp-entry',
        title: 'Temporary',
        content: 'Will be cleared',
        category: 'temp',
        tags: []
      });

      const eventSpy = jest.fn();
      helpSystem.on('help-cleared', eventSpy);

      helpSystem.clear();

      expect(helpSystem.getHelpEntry('temp-entry')).toBeUndefined();
      expect(helpSystem.getStatistics().totalEntries).toBe(0);
      expect(eventSpy).toHaveBeenCalled();
    });

    it('should clean up resources on destroy', () => {
      helpSystem.addHelpEntry({
        id: 'destroy-test',
        title: 'Destroy Test',
        content: 'Test destroy',
        category: 'test',
        tags: []
      });

      helpSystem.destroy();

      expect(helpSystem.getStatistics().totalEntries).toBe(0);
      expect(helpSystem.getStatistics().searchIndexSize).toBe(0);
    });

    it('should limit context history size', () => {
      // Generate many contexts
      for (let i = 0; i < 60; i++) {
        helpSystem.getContextualHelp({
          currentNode: { id: `node${i}`, label: `Node ${i}` },
          availableCommands: [],
          shortcuts: [],
          suggestions: []
        });
      }

      const stats = helpSystem.getStatistics();
      expect(stats.contextHistorySize).toBeLessThanOrEqual(50);
    });
  });

  describe('Edge Cases and Error Handling', () => {
    it('should handle entries with missing optional fields', () => {
      const minimalEntry = {
        id: 'minimal',
        title: 'Minimal Entry',
        content: 'Minimal content',
        category: 'test',
        tags: []
      };

      expect(() => {
        helpSystem.addHelpEntry(minimalEntry);
      }).not.toThrow();

      expect(helpSystem.getHelpEntry('minimal')).toBeDefined();
    });

    it('should handle search with empty query', () => {
      const results = helpSystem.searchHelp({
        query: '',
        includeExamples: false,
        fuzzyThreshold: 0.1
      });

      expect(results).toEqual([]);
    });

    it('should handle search with very high fuzzy threshold', () => {
      const results = helpSystem.searchHelp({
        query: 'test',
        includeExamples: false,
        fuzzyThreshold: 1.0 // Very high threshold
      });

      expect(Array.isArray(results)).toBe(true);
      // Should return fewer or no results due to high threshold
    });

    it('should handle contextual help with minimal context', () => {
      const minimalContext: HelpContext = {
        availableCommands: [],
        shortcuts: [],
        suggestions: []
      };

      expect(() => {
        helpSystem.getContextualHelp(minimalContext);
      }).not.toThrow();
    });
  });
});