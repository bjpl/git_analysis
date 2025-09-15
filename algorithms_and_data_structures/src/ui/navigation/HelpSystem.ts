/**
 * HelpSystem - Context-aware help and assistance system
 * Provides intelligent help suggestions, documentation, and guidance
 */

import { EventEmitter } from 'events';
import {
  NavigationNode,
  NavigationConfig,
  HelpContext,
  HelpExample,
  KeyBinding,
  SearchResult
} from '../../types/navigation.js';

export interface HelpEntry {
  id: string;
  title: string;
  content: string;
  category: string;
  tags: string[];
  examples?: HelpExample[];
  seeAlso?: string[];
  difficulty?: 'beginner' | 'intermediate' | 'advanced';
  lastUpdated?: Date;
}

export interface ContextualHelp {
  primary: HelpEntry[];
  suggestions: HelpEntry[];
  quickActions: QuickAction[];
  shortcuts: KeyBinding[];
  tips?: string[];
}

export interface QuickAction {
  id: string;
  label: string;
  description: string;
  command: string;
  shortcut?: KeyBinding;
  category: string;
}

export interface HelpSearchOptions {
  query: string;
  category?: string;
  difficulty?: 'beginner' | 'intermediate' | 'advanced';
  includeExamples: boolean;
  fuzzyThreshold: number;
}

export class HelpSystem extends EventEmitter {
  private config: NavigationConfig;
  private helpEntries: Map<string, HelpEntry> = new Map();
  private quickActions: Map<string, QuickAction> = new Map();
  private contextHistory: HelpContext[] = [];
  private currentContext?: HelpContext;
  private searchIndex: Map<string, Set<string>> = new Map(); // word -> entry IDs

  constructor(config: NavigationConfig) {
    super();
    this.config = config;
    this.initializeDefaultHelp();
    this.buildSearchIndex();
  }

  /**
   * Initialize default help content
   */
  private initializeDefaultHelp(): void {
    const defaultEntries: HelpEntry[] = [
      {
        id: 'navigation-basics',
        title: 'Basic Navigation',
        content: `Navigate through the CLI using arrow keys or vim-style commands.
        
Use ↑/↓ to move between items, Enter to select, and Esc to go back.
The breadcrumb trail at the top shows your current location.`,
        category: 'navigation',
        tags: ['basics', 'movement', 'arrows'],
        examples: [
          {
            command: '↑/↓',
            description: 'Navigate up and down',
            usage: 'Use arrow keys to move between menu items'
          },
          {
            command: 'Enter',
            description: 'Select current item',
            usage: 'Press Enter to execute the highlighted command'
          },
          {
            command: 'Esc',
            description: 'Go back',
            usage: 'Press Escape to return to the previous menu'
          }
        ],
        difficulty: 'beginner'
      },
      {
        id: 'keyboard-shortcuts',
        title: 'Keyboard Shortcuts',
        content: `Learn essential keyboard shortcuts to navigate efficiently.
        
Most shortcuts use common conventions like Ctrl+/ for search and F1 for help.
You can customize shortcuts in the configuration.`,
        category: 'shortcuts',
        tags: ['keyboard', 'shortcuts', 'hotkeys'],
        examples: [
          {
            command: 'Ctrl+/',
            description: 'Open search',
            usage: 'Press Ctrl+/ to quickly find commands or content'
          },
          {
            command: 'F1',
            description: 'Show help',
            usage: 'Press F1 to open context-sensitive help'
          },
          {
            command: 'Alt+←/→',
            description: 'Navigate history',
            usage: 'Use Alt with arrows to go back/forward in history'
          }
        ],
        difficulty: 'beginner'
      },
      {
        id: 'search-system',
        title: 'Search and Filtering',
        content: `Use the powerful search system to quickly find what you need.
        
Search supports fuzzy matching, tags, and descriptions. Use filters to narrow results.`,
        category: 'search',
        tags: ['search', 'filter', 'fuzzy', 'find'],
        examples: [
          {
            command: 'search algorithm',
            description: 'Search for algorithm-related content',
            usage: 'Type your search query to find matching items'
          },
          {
            command: '/',
            description: 'Quick search mode',
            usage: 'Press / to start typing a search query immediately'
          }
        ],
        difficulty: 'intermediate',
        seeAlso: ['keyboard-shortcuts', 'navigation-basics']
      },
      {
        id: 'command-routing',
        title: 'Command System',
        content: `Execute commands using the routing system with parameters and patterns.
        
Commands can be executed directly or through menu selection. Support for complex routing.`,
        category: 'commands',
        tags: ['commands', 'routing', 'execution'],
        examples: [
          {
            command: 'help <topic>',
            description: 'Get help on specific topic',
            usage: 'help search - shows help about the search system'
          },
          {
            command: 'cd <path>',
            description: 'Navigate to specific path',
            usage: 'cd algorithms/sorting - navigate to sorting algorithms'
          }
        ],
        difficulty: 'intermediate'
      },
      {
        id: 'advanced-features',
        title: 'Advanced Features',
        content: `Explore advanced functionality like key sequences, custom shortcuts, and automation.
        
Set up custom workflows and use power-user features for enhanced productivity.`,
        category: 'advanced',
        tags: ['advanced', 'sequences', 'automation', 'customization'],
        examples: [
          {
            command: 'gg',
            description: 'Vim-style goto line',
            usage: 'Press g twice quickly to jump to specific line/item'
          },
          {
            command: 'Ctrl+P Ctrl+P',
            description: 'Command palette',
            usage: 'Press Ctrl+P twice to open the command palette'
          }
        ],
        difficulty: 'advanced',
        seeAlso: ['keyboard-shortcuts', 'command-routing']
      }
    ];

    defaultEntries.forEach(entry => this.addHelpEntry(entry));

    // Add default quick actions
    const defaultActions: QuickAction[] = [
      {
        id: 'search',
        label: 'Search',
        description: 'Search for commands or content',
        command: 'search',
        shortcut: { key: '/', ctrl: true },
        category: 'navigation'
      },
      {
        id: 'help',
        label: 'Help',
        description: 'Show contextual help',
        command: 'help',
        shortcut: { key: 'F1' },
        category: 'assistance'
      },
      {
        id: 'back',
        label: 'Back',
        description: 'Navigate to previous location',
        command: 'back',
        shortcut: { key: 'Escape' },
        category: 'navigation'
      },
      {
        id: 'home',
        label: 'Home',
        description: 'Go to main menu',
        command: 'home',
        shortcut: { key: 'Home' },
        category: 'navigation'
      }
    ];

    defaultActions.forEach(action => this.addQuickAction(action));
  }

  /**
   * Add help entry to the system
   */
  addHelpEntry(entry: HelpEntry): void {
    entry.lastUpdated = entry.lastUpdated || new Date();
    this.helpEntries.set(entry.id, entry);
    this.indexHelpEntry(entry);
    this.emit('help-entry-added', entry);
  }

  /**
   * Remove help entry
   */
  removeHelpEntry(entryId: string): boolean {
    const entry = this.helpEntries.get(entryId);
    if (!entry) return false;

    this.helpEntries.delete(entryId);
    this.removeFromSearchIndex(entry);
    this.emit('help-entry-removed', entryId);
    return true;
  }

  /**
   * Add quick action
   */
  addQuickAction(action: QuickAction): void {
    this.quickActions.set(action.id, action);
    this.emit('quick-action-added', action);
  }

  /**
   * Get contextual help for current state
   */
  getContextualHelp(context: HelpContext): ContextualHelp {
    this.currentContext = context;
    this.contextHistory.push(context);

    // Limit context history
    if (this.contextHistory.length > 50) {
      this.contextHistory = this.contextHistory.slice(-50);
    }

    const primary = this.getPrimaryHelp(context);
    const suggestions = this.getSuggestions(context);
    const quickActions = this.getContextualQuickActions(context);
    const shortcuts = this.getRelevantShortcuts(context);
    const tips = this.getContextualTips(context);

    const result: ContextualHelp = {
      primary,
      suggestions,
      quickActions,
      shortcuts,
      tips
    };

    this.emit('contextual-help-generated', result);
    return result;
  }

  /**
   * Get primary help for context
   */
  private getPrimaryHelp(context: HelpContext): HelpEntry[] {
    const entries: HelpEntry[] = [];

    // Help based on current node
    if (context.currentNode) {
      const nodeHelp = this.findHelpForNode(context.currentNode);
      entries.push(...nodeHelp);
    }

    // Help based on available commands
    const commandHelp = this.findHelpForCommands(context.availableCommands);
    entries.push(...commandHelp);

    return entries.slice(0, 5); // Limit primary help
  }

  /**
   * Find help entries for a navigation node
   */
  private findHelpForNode(node: NavigationNode): HelpEntry[] {
    const entries: HelpEntry[] = [];

    // Look for direct help entries
    const directHelp = this.helpEntries.get(node.id);
    if (directHelp) {
      entries.push(directHelp);
    }

    // Look for category-based help
    if (node.category) {
      const categoryHelp = Array.from(this.helpEntries.values())
        .filter(entry => entry.category === node.category);
      entries.push(...categoryHelp.slice(0, 3));
    }

    // Look for tag-based help
    if (node.tags) {
      const tagHelp = Array.from(this.helpEntries.values())
        .filter(entry => entry.tags.some(tag => node.tags!.includes(tag)));
      entries.push(...tagHelp.slice(0, 2));
    }

    return entries;
  }

  /**
   * Find help entries for commands
   */
  private findHelpForCommands(commands: string[]): HelpEntry[] {
    const entries: HelpEntry[] = [];

    for (const command of commands) {
      const commandHelp = Array.from(this.helpEntries.values())
        .filter(entry => 
          entry.content.toLowerCase().includes(command.toLowerCase()) ||
          entry.examples?.some(ex => ex.command.includes(command))
        );
      entries.push(...commandHelp.slice(0, 2));
    }

    return entries;
  }

  /**
   * Get help suggestions based on context
   */
  private getSuggestions(context: HelpContext): HelpEntry[] {
    const suggestions: HelpEntry[] = [];

    // Suggest based on user's apparent skill level
    const skillLevel = this.inferSkillLevel();
    const levelAppropriate = Array.from(this.helpEntries.values())
      .filter(entry => {
        if (!entry.difficulty) return true;
        
        switch (skillLevel) {
          case 'beginner':
            return entry.difficulty === 'beginner';
          case 'intermediate':
            return ['beginner', 'intermediate'].includes(entry.difficulty);
          case 'advanced':
            return true;
          default:
            return true;
        }
      });

    suggestions.push(...levelAppropriate.slice(0, 3));

    // Suggest related entries
    if (context.currentNode?.tags) {
      const related = this.findRelatedHelp(context.currentNode.tags);
      suggestions.push(...related.slice(0, 2));
    }

    return suggestions;
  }

  /**
   * Infer user's skill level based on usage patterns
   */
  private inferSkillLevel(): 'beginner' | 'intermediate' | 'advanced' {
    const recentContexts = this.contextHistory.slice(-10);
    
    // Simple heuristic based on command diversity and frequency
    const uniqueCommands = new Set(
      recentContexts.flatMap(ctx => ctx.availableCommands)
    ).size;

    if (uniqueCommands < 5) return 'beginner';
    if (uniqueCommands < 15) return 'intermediate';
    return 'advanced';
  }

  /**
   * Find related help entries based on tags
   */
  private findRelatedHelp(tags: string[]): HelpEntry[] {
    const related: HelpEntry[] = [];
    const tagSet = new Set(tags);

    for (const entry of this.helpEntries.values()) {
      const commonTags = entry.tags.filter(tag => tagSet.has(tag));
      if (commonTags.length > 0) {
        related.push(entry);
      }
    }

    // Sort by relevance (number of matching tags)
    return related.sort((a, b) => {
      const aMatches = a.tags.filter(tag => tagSet.has(tag)).length;
      const bMatches = b.tags.filter(tag => tagSet.has(tag)).length;
      return bMatches - aMatches;
    });
  }

  /**
   * Get contextual quick actions
   */
  private getContextualQuickActions(context: HelpContext): QuickAction[] {
    const actions = Array.from(this.quickActions.values());
    
    // Filter and sort by relevance
    return actions
      .filter(action => this.isActionRelevant(action, context))
      .sort((a, b) => this.getActionRelevanceScore(b, context) - 
                      this.getActionRelevanceScore(a, context))
      .slice(0, 6);
  }

  /**
   * Check if quick action is relevant to context
   */
  private isActionRelevant(action: QuickAction, context: HelpContext): boolean {
    // Basic relevance check
    if (action.category === 'navigation') return true;
    
    // Context-specific relevance
    if (context.currentNode?.category === action.category) return true;
    
    return false;
  }

  /**
   * Get relevance score for quick action
   */
  private getActionRelevanceScore(action: QuickAction, context: HelpContext): number {
    let score = 0;
    
    if (action.category === 'navigation') score += 10;
    if (context.currentNode?.category === action.category) score += 20;
    if (context.availableCommands.includes(action.command)) score += 15;
    
    return score;
  }

  /**
   * Get relevant keyboard shortcuts
   */
  private getRelevantShortcuts(context: HelpContext): KeyBinding[] {
    const shortcuts = Object.values(this.config.keyBindings);
    
    return shortcuts
      .filter(shortcut => shortcut.description)
      .slice(0, 8); // Show most common shortcuts
  }

  /**
   * Get contextual tips
   */
  private getContextualTips(context: HelpContext): string[] {
    const tips: string[] = [];

    // Navigation tips
    if (context.availableCommands.length > 10) {
      tips.push('Use search (Ctrl+/) to quickly find commands in large lists');
    }

    // Shortcut tips
    if (this.contextHistory.length > 5) {
      tips.push('Try keyboard shortcuts for faster navigation');
    }

    // Context-specific tips
    if (context.currentNode?.category === 'algorithms') {
      tips.push('Use breadcrumbs to navigate between algorithm categories');
    }

    return tips.slice(0, 3);
  }

  /**
   * Search help entries
   */
  searchHelp(options: HelpSearchOptions): SearchResult[] {
    const results: SearchResult[] = [];
    const queryWords = options.query.toLowerCase().split(/\\s+/);

    for (const entry of this.helpEntries.values()) {
      // Skip if category filter doesn't match
      if (options.category && entry.category !== options.category) {
        continue;
      }

      // Skip if difficulty filter doesn't match
      if (options.difficulty && entry.difficulty !== options.difficulty) {
        continue;
      }

      const score = this.calculateHelpSearchScore(entry, queryWords);
      
      if (score >= options.fuzzyThreshold) {
        results.push({
          item: this.helpEntryToNode(entry),
          score,
          matchType: this.getMatchType(entry, options.query),
          highlights: this.findHighlights(entry, options.query)
        });
      }
    }

    return results.sort((a, b) => b.score - a.score);
  }

  /**
   * Calculate search score for help entry
   */
  private calculateHelpSearchScore(entry: HelpEntry, queryWords: string[]): number {
    let score = 0;
    const title = entry.title.toLowerCase();
    const content = entry.content.toLowerCase();
    const tags = entry.tags.join(' ').toLowerCase();

    for (const word of queryWords) {
      // Exact matches in title
      if (title.includes(word)) score += 10;
      
      // Exact matches in tags
      if (tags.includes(word)) score += 8;
      
      // Exact matches in content
      if (content.includes(word)) score += 5;
      
      // Fuzzy matches
      if (this.fuzzyMatch(title, word)) score += 3;
      if (this.fuzzyMatch(content, word)) score += 2;
    }

    return score;
  }

  /**
   * Simple fuzzy matching
   */
  private fuzzyMatch(text: string, pattern: string): boolean {
    const regex = new RegExp(pattern.split('').join('.*'), 'i');
    return regex.test(text);
  }

  /**
   * Get match type for search result
   */
  private getMatchType(entry: HelpEntry, query: string): SearchResult['matchType'] {
    const queryLower = query.toLowerCase();
    
    if (entry.title.toLowerCase() === queryLower) return 'exact';
    if (entry.title.toLowerCase().startsWith(queryLower)) return 'prefix';
    if (entry.tags.some(tag => tag.toLowerCase() === queryLower)) return 'tag';
    if (entry.content.toLowerCase().includes(queryLower)) return 'description';
    
    return 'fuzzy';
  }

  /**
   * Find highlights in help entry
   */
  private findHighlights(entry: HelpEntry, query: string): SearchResult['highlights'] {
    const highlights: SearchResult['highlights'] = [];
    const queryLower = query.toLowerCase();

    // Find highlights in title
    const titleIndex = entry.title.toLowerCase().indexOf(queryLower);
    if (titleIndex !== -1) {
      highlights.push({
        field: 'label',
        start: titleIndex,
        end: titleIndex + query.length
      });
    }

    // Find highlights in description (content preview)
    const contentIndex = entry.content.toLowerCase().indexOf(queryLower);
    if (contentIndex !== -1) {
      highlights.push({
        field: 'description',
        start: contentIndex,
        end: contentIndex + query.length
      });
    }

    return highlights;
  }

  /**
   * Convert help entry to navigation node for search results
   */
  private helpEntryToNode(entry: HelpEntry): NavigationNode {
    return {
      id: entry.id,
      label: entry.title,
      description: entry.content.substring(0, 100) + '...',
      category: entry.category,
      tags: entry.tags,
      command: `help ${entry.id}`,
      weight: 5
    };
  }

  /**
   * Get specific help entry
   */
  getHelpEntry(id: string): HelpEntry | undefined {
    return this.helpEntries.get(id);
  }

  /**
   * Get all help entries in category
   */
  getHelpByCategory(category: string): HelpEntry[] {
    return Array.from(this.helpEntries.values())
      .filter(entry => entry.category === category);
  }

  /**
   * Build search index for faster searches
   */
  private buildSearchIndex(): void {
    this.searchIndex.clear();

    for (const [id, entry] of this.helpEntries) {
      this.indexHelpEntry(entry);
    }
  }

  /**
   * Index a help entry for searching
   */
  private indexHelpEntry(entry: HelpEntry): void {
    const words = new Set([
      ...entry.title.toLowerCase().split(/\\W+/),
      ...entry.content.toLowerCase().split(/\\W+/),
      ...entry.tags.map(tag => tag.toLowerCase()),
      ...entry.category.toLowerCase().split(/\\W+/)
    ]);

    for (const word of words) {
      if (word.length > 2) { // Skip very short words
        if (!this.searchIndex.has(word)) {
          this.searchIndex.set(word, new Set());
        }
        this.searchIndex.get(word)!.add(entry.id);
      }
    }
  }

  /**
   * Remove help entry from search index
   */
  private removeFromSearchIndex(entry: HelpEntry): void {
    for (const [word, entryIds] of this.searchIndex) {
      entryIds.delete(entry.id);
      if (entryIds.size === 0) {
        this.searchIndex.delete(word);
      }
    }
  }

  /**
   * Get help statistics
   */
  getStatistics(): any {
    return {
      totalEntries: this.helpEntries.size,
      totalQuickActions: this.quickActions.size,
      categories: [...new Set(Array.from(this.helpEntries.values()).map(e => e.category))],
      contextHistorySize: this.contextHistory.length,
      searchIndexSize: this.searchIndex.size
    };
  }

  /**
   * Export help content
   */
  exportHelp(): any {
    return {
      entries: Array.from(this.helpEntries.entries()),
      quickActions: Array.from(this.quickActions.entries()),
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Import help content
   */
  importHelp(data: any): void {
    // Clear existing content
    this.helpEntries.clear();
    this.quickActions.clear();

    // Import entries
    if (data.entries) {
      for (const [id, entry] of data.entries) {
        this.addHelpEntry(entry);
      }
    }

    // Import quick actions
    if (data.quickActions) {
      for (const [id, action] of data.quickActions) {
        this.addQuickAction(action);
      }
    }

    this.buildSearchIndex();
    this.emit('help-imported', data);
  }

  /**
   * Clear all help content
   */
  clear(): void {
    this.helpEntries.clear();
    this.quickActions.clear();
    this.searchIndex.clear();
    this.contextHistory = [];
    this.currentContext = undefined;
    this.emit('help-cleared');
  }

  /**
   * Destroy help system
   */
  destroy(): void {
    this.clear();
    this.removeAllListeners();
  }
}