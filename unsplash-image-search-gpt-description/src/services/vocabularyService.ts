import { supabase } from '../lib/supabase';
import { apiConfig } from '../config/api';
import {
  VocabularyItem,
  VocabularyFilter,
  VocabularyStats,
  SRSReviewSession,
  MasteryLevel,
  VocabularySortBy,
  OfflineVocabularyChange,
  ConflictResolution,
  SharedVocabularyList
} from '../types';

class VocabularyService {
  private readonly TABLE_NAME = 'vocabulary_items';
  private readonly SESSIONS_TABLE = 'review_sessions';
  private readonly SHARED_LISTS_TABLE = 'shared_vocabulary_lists';
  private readonly MAX_VOCABULARY_ITEMS = apiConfig.vocabulary.maxItems;
  private readonly DAILY_GOAL = apiConfig.vocabulary.dailyGoal;

  // CRUD Operations
  async getVocabulary(filter: VocabularyFilter = { sortBy: VocabularySortBy.CREATED_AT, sortOrder: 'desc' }): Promise<VocabularyItem[]> {
    let query = supabase
      .from(this.TABLE_NAME)
      .select(`
        *,
        examples:vocabulary_examples(*)
      `);

    // Apply filters
    if (filter.search) {
      query = query.or(`word.ilike.%${filter.search}%,translation.ilike.%${filter.search}%,notes.ilike.%${filter.search}%`);
    }

    if (filter.masteryLevel?.length) {
      query = query.in('mastery_level', filter.masteryLevel);
    }

    if (filter.tags?.length) {
      query = query.contains('tags', filter.tags);
    }

    if (filter.category) {
      query = query.eq('category', filter.category);
    }

    if (filter.difficulty) {
      query = query.gte('difficulty', filter.difficulty[0]).lte('difficulty', filter.difficulty[1]);
    }

    if (filter.dateRange) {
      query = query.gte('created_at', filter.dateRange[0].toISOString())
                  .lte('created_at', filter.dateRange[1].toISOString());
    }

    // Apply sorting
    const sortColumn = this.mapSortByToColumn(filter.sortBy);
    query = query.order(sortColumn, { ascending: filter.sortOrder === 'asc' });

    const { data, error } = await query;

    if (error) throw new Error(`Failed to fetch vocabulary: ${error.message}`);

    return this.transformDatabaseToVocabulary(data || []);
  }

  async createVocabularyItem(item: Omit<VocabularyItem, 'id' | 'createdAt' | 'updatedAt'>): Promise<VocabularyItem> {
    const vocabularyData = this.transformVocabularyToDatabase(item);
    const { examples, ...itemData } = vocabularyData;

    const { data, error } = await supabase
      .from(this.TABLE_NAME)
      .insert([itemData])
      .select()
      .single();

    if (error) throw new Error(`Failed to create vocabulary item: ${error.message}`);

    // Create examples if provided
    if (examples?.length) {
      const { error: examplesError } = await supabase
        .from('vocabulary_examples')
        .insert(
          examples.map(example => ({
            ...example,
            vocabulary_id: data.id
          }))
        );

      if (examplesError) {
        console.warn('Failed to create examples:', examplesError.message);
      }
    }

    // Fetch the complete item with examples
    return this.getVocabularyItem(data.id);
  }

  async updateVocabularyItem(id: string, updates: Partial<VocabularyItem>): Promise<VocabularyItem> {
    const updateData = this.transformVocabularyToDatabase(updates);
    const { examples, ...itemData } = updateData;

    const { data, error } = await supabase
      .from(this.TABLE_NAME)
      .update({
        ...itemData,
        updated_at: new Date().toISOString()
      })
      .eq('id', id)
      .select()
      .single();

    if (error) throw new Error(`Failed to update vocabulary item: ${error.message}`);

    // Update examples if provided
    if (examples) {
      // Delete existing examples
      await supabase
        .from('vocabulary_examples')
        .delete()
        .eq('vocabulary_id', id);

      // Insert new examples
      if (examples.length > 0) {
        await supabase
          .from('vocabulary_examples')
          .insert(
            examples.map(example => ({
              ...example,
              vocabulary_id: id
            }))
          );
      }
    }

    return this.getVocabularyItem(id);
  }

  async deleteVocabularyItem(id: string): Promise<void> {
    const { error } = await supabase
      .from(this.TABLE_NAME)
      .delete()
      .eq('id', id);

    if (error) throw new Error(`Failed to delete vocabulary item: ${error.message}`);
  }

  async getVocabularyItem(id: string): Promise<VocabularyItem> {
    const { data, error } = await supabase
      .from(this.TABLE_NAME)
      .select(`
        *,
        examples:vocabulary_examples(*)
      `)
      .eq('id', id)
      .single();

    if (error) throw new Error(`Failed to fetch vocabulary item: ${error.message}`);

    return this.transformDatabaseToVocabulary([data])[0];
  }

  // Bulk Operations
  async bulkDeleteVocabularyItems(ids: string[]): Promise<void> {
    const { error } = await supabase
      .from(this.TABLE_NAME)
      .delete()
      .in('id', ids);

    if (error) throw new Error(`Failed to bulk delete vocabulary items: ${error.message}`);
  }

  async bulkUpdateVocabularyItems(ids: string[], updates: Partial<VocabularyItem>): Promise<VocabularyItem[]> {
    const updateData = this.transformVocabularyToDatabase(updates);
    const { examples, ...itemData } = updateData;

    const { data, error } = await supabase
      .from(this.TABLE_NAME)
      .update({
        ...itemData,
        updated_at: new Date().toISOString()
      })
      .in('id', ids)
      .select(`
        *,
        examples:vocabulary_examples(*)
      `);

    if (error) throw new Error(`Failed to bulk update vocabulary items: ${error.message}`);

    return this.transformDatabaseToVocabulary(data || []);
  }

  // Statistics
  async getVocabularyStats(): Promise<VocabularyStats> {
    const { data: items } = await supabase
      .from(this.TABLE_NAME)
      .select('mastery_level, difficulty, category, times_reviewed, times_correct, created_at')
      .eq('user_id', (await supabase.auth.getUser()).data.user?.id);

    if (!items) {
      return this.getEmptyStats();
    }

    const totalWords = items.length;
    const masteryBreakdown = items.reduce((acc, item) => {
      acc[item.mastery_level] = (acc[item.mastery_level] || 0) + 1;
      return acc;
    }, {} as Record<MasteryLevel, number>);

    const categoryBreakdown = items.reduce((acc, item) => {
      if (item.category) {
        acc[item.category] = (acc[item.category] || 0) + 1;
      }
      return acc;
    }, {} as Record<string, number>);

    const totalReviews = items.reduce((sum, item) => sum + (item.times_reviewed || 0), 0);
    const totalCorrect = items.reduce((sum, item) => sum + (item.times_correct || 0), 0);
    const accuracy = totalReviews > 0 ? (totalCorrect / totalReviews) * 100 : 0;

    const averageDifficulty = items.length > 0 
      ? items.reduce((sum, item) => sum + (item.difficulty || 5), 0) / items.length
      : 0;

    // Calculate weekly progress (last 7 days)
    const weeklyProgress = await this.getWeeklyProgress();
    const currentStreak = await this.getCurrentStreak();
    const dailyGoal = await this.getDailyGoal();
    const todayProgress = await this.getTodayProgress();

    return {
      totalWords,
      newWords: masteryBreakdown[MasteryLevel.NEW] || 0,
      learningWords: masteryBreakdown[MasteryLevel.LEARNING] || 0,
      reviewWords: masteryBreakdown[MasteryLevel.REVIEW] || 0,
      masteredWords: masteryBreakdown[MasteryLevel.MASTERED] || 0,
      dailyGoal,
      dailyProgress: todayProgress,
      streak: currentStreak,
      accuracy,
      averageDifficulty,
      weeklyProgress,
      categoryBreakdown
    };
  }

  // SRS (Spaced Repetition System)
  async startReviewSession(session: SRSReviewSession): Promise<SRSReviewSession> {
    const { data, error } = await supabase
      .from(this.SESSIONS_TABLE)
      .insert([{
        ...session,
        user_id: (await supabase.auth.getUser()).data.user?.id
      }])
      .select()
      .single();

    if (error) throw new Error(`Failed to start review session: ${error.message}`);

    return data;
  }

  async completeReview(vocabularyId: string, correct: boolean, timeSpent: number): Promise<void> {
    // Get current vocabulary item
    const item = await this.getVocabularyItem(vocabularyId);
    
    // Calculate new SRS values
    const srsUpdate = this.calculateSRSUpdate(item, correct);
    
    // Update vocabulary item with new SRS data
    await this.updateVocabularyItem(vocabularyId, {
      ...srsUpdate,
      timesReviewed: item.timesReviewed + 1,
      timesCorrect: item.timesCorrect + (correct ? 1 : 0),
      lastReviewedAt: new Date(),
      streak: correct ? item.streak + 1 : 0
    });

    // Log the review
    await supabase
      .from('review_logs')
      .insert([{
        vocabulary_id: vocabularyId,
        user_id: (await supabase.auth.getUser()).data.user?.id,
        correct,
        time_spent: timeSpent,
        created_at: new Date().toISOString()
      }]);
  }

  // Collaborative Features
  async getSharedVocabularyLists(): Promise<SharedVocabularyList[]> {
    const { data, error } = await supabase
      .from(this.SHARED_LISTS_TABLE)
      .select(`
        *,
        owner:profiles!shared_vocabulary_lists_owner_id_fkey(display_name),
        items:vocabulary_items(*)
      `)
      .eq('is_public', true)
      .order('download_count', { ascending: false });

    if (error) throw new Error(`Failed to fetch shared vocabulary lists: ${error.message}`);

    return data.map(list => ({
      id: list.id,
      name: list.name,
      description: list.description,
      ownerId: list.owner_id,
      ownerName: list.owner?.display_name || 'Anonymous',
      items: this.transformDatabaseToVocabulary(list.items || []),
      isPublic: list.is_public,
      tags: list.tags || [],
      category: list.category || '',
      difficulty: list.difficulty || 1,
      downloadCount: list.download_count || 0,
      rating: list.rating || 0,
      createdAt: new Date(list.created_at),
      updatedAt: new Date(list.updated_at)
    }));
  }

  async shareVocabularyList(
    name: string, 
    description: string, 
    vocabularyIds: string[], 
    isPublic: boolean = false
  ): Promise<SharedVocabularyList> {
    const userId = (await supabase.auth.getUser()).data.user?.id;
    if (!userId) throw new Error('User not authenticated');

    const { data, error } = await supabase
      .from(this.SHARED_LISTS_TABLE)
      .insert([{
        name,
        description,
        owner_id: userId,
        vocabulary_item_ids: vocabularyIds,
        is_public: isPublic,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }])
      .select()
      .single();

    if (error) throw new Error(`Failed to share vocabulary list: ${error.message}`);

    return data;
  }

  // Import/Export
  async exportVocabulary(format: 'csv' | 'json' | 'anki'): Promise<Blob> {
    const items = await this.getVocabulary();
    
    switch (format) {
      case 'csv':
        return this.exportToCSV(items);
      case 'json':
        return this.exportToJSON(items);
      case 'anki':
        return this.exportToAnki(items);
      default:
        throw new Error('Unsupported export format');
    }
  }

  async importVocabulary(file: File, format: 'csv' | 'json'): Promise<number> {
    const text = await file.text();
    let items: Partial<VocabularyItem>[];

    switch (format) {
      case 'csv':
        items = this.parseCSV(text);
        break;
      case 'json':
        items = JSON.parse(text);
        break;
      default:
        throw new Error('Unsupported import format');
    }

    // Import items in batches
    const batchSize = 50;
    let importedCount = 0;

    for (let i = 0; i < items.length; i += batchSize) {
      const batch = items.slice(i, i + batchSize);
      const promises = batch.map(item => this.createVocabularyItem(item as any));
      
      try {
        await Promise.all(promises);
        importedCount += batch.length;
      } catch (error) {
        console.error(`Failed to import batch ${i / batchSize + 1}:`, error);
      }
    }

    return importedCount;
  }

  // Offline Sync
  async syncOfflineChanges(changes: OfflineVocabularyChange[]): Promise<ConflictResolution[]> {
    const conflicts: ConflictResolution[] = [];

    for (const change of changes) {
      try {
        switch (change.type) {
          case 'create':
            if (change.data) {
              await this.createVocabularyItem(change.data as any);
            }
            break;
          case 'update':
            if (change.data) {
              // Check for conflicts
              try {
                const remoteItem = await this.getVocabularyItem(change.vocabularyId);
                if (remoteItem.updatedAt > change.timestamp) {
                  // Conflict detected
                  conflicts.push({
                    localItem: { ...remoteItem, ...change.data } as VocabularyItem,
                    remoteItem,
                    resolution: 'remote' // Default to remote, let user decide
                  });
                  continue;
                }
              } catch {
                // Item doesn't exist remotely, safe to update
              }
              
              await this.updateVocabularyItem(change.vocabularyId, change.data);
            }
            break;
          case 'delete':
            await this.deleteVocabularyItem(change.vocabularyId);
            break;
        }
      } catch (error) {
        console.error(`Failed to sync change ${change.id}:`, error);
      }
    }

    return conflicts;
  }

  // Private helper methods
  private calculateSRSUpdate(item: VocabularyItem, correct: boolean) {
    let ease = item.ease;
    let interval = item.interval;
    let masteryLevel = item.masteryLevel;

    if (correct) {
      ease = Math.max(1.3, ease + 0.1);
      interval = Math.ceil(interval * ease);
      
      // Advance mastery level
      if (masteryLevel === MasteryLevel.NEW) {
        masteryLevel = MasteryLevel.LEARNING;
        interval = 1;
      } else if (masteryLevel === MasteryLevel.LEARNING && item.streak >= 2) {
        masteryLevel = MasteryLevel.REVIEW;
        interval = 4;
      } else if (masteryLevel === MasteryLevel.REVIEW && item.streak >= 5) {
        masteryLevel = MasteryLevel.MASTERED;
      }
    } else {
      ease = Math.max(1.3, ease - 0.2);
      interval = Math.max(1, Math.floor(interval * 0.5));
      
      // Reset mastery level if struggling
      if (masteryLevel === MasteryLevel.MASTERED || masteryLevel === MasteryLevel.REVIEW) {
        masteryLevel = MasteryLevel.LEARNING;
      }
    }

    const nextReviewAt = new Date();
    nextReviewAt.setDate(nextReviewAt.getDate() + interval);

    return {
      ease,
      interval,
      masteryLevel,
      nextReviewAt
    };
  }

  private mapSortByToColumn(sortBy: VocabularySortBy): string {
    const mapping = {
      [VocabularySortBy.CREATED_AT]: 'created_at',
      [VocabularySortBy.UPDATED_AT]: 'updated_at',
      [VocabularySortBy.WORD]: 'word',
      [VocabularySortBy.DIFFICULTY]: 'difficulty',
      [VocabularySortBy.TIMES_REVIEWED]: 'times_reviewed',
      [VocabularySortBy.ACCURACY]: 'times_correct',
      [VocabularySortBy.NEXT_REVIEW]: 'next_review_at'
    };
    return mapping[sortBy] || 'created_at';
  }

  private transformDatabaseToVocabulary(data: any[]): VocabularyItem[] {
    return data.map(item => ({
      id: item.id,
      word: item.word,
      translation: item.translation,
      context: item.context,
      imageUrl: item.image_url,
      searchQuery: item.search_query,
      examples: item.examples || [],
      notes: item.notes,
      tags: item.tags || [],
      category: item.category,
      masteryLevel: item.mastery_level as MasteryLevel,
      difficulty: item.difficulty,
      timesReviewed: item.times_reviewed,
      timesCorrect: item.times_correct,
      streak: item.streak,
      lastReviewedAt: item.last_reviewed_at ? new Date(item.last_reviewed_at) : undefined,
      nextReviewAt: item.next_review_at ? new Date(item.next_review_at) : undefined,
      ease: item.ease,
      interval: item.interval,
      createdAt: new Date(item.created_at),
      updatedAt: new Date(item.updated_at),
      userId: item.user_id,
      isPublic: item.is_public,
      sharedFromUserId: item.shared_from_user_id
    }));
  }

  private transformVocabularyToDatabase(item: any) {
    return {
      word: item.word,
      translation: item.translation,
      context: item.context,
      image_url: item.imageUrl,
      search_query: item.searchQuery,
      examples: item.examples,
      notes: item.notes,
      tags: item.tags,
      category: item.category,
      mastery_level: item.masteryLevel,
      difficulty: item.difficulty,
      times_reviewed: item.timesReviewed,
      times_correct: item.timesCorrect,
      streak: item.streak,
      last_reviewed_at: item.lastReviewedAt?.toISOString(),
      next_review_at: item.nextReviewAt?.toISOString(),
      ease: item.ease,
      interval: item.interval,
      user_id: item.userId,
      is_public: item.isPublic,
      shared_from_user_id: item.sharedFromUserId
    };
  }

  private async getWeeklyProgress(): Promise<number[]> {
    // Implementation for weekly progress
    return new Array(7).fill(0);
  }

  private async getCurrentStreak(): Promise<number> {
    // Implementation for current streak
    return 0;
  }

  private async getDailyGoal(): Promise<number> {
    // Implementation for daily goal
    return 10;
  }

  private async getTodayProgress(): Promise<number> {
    // Implementation for today's progress
    return 0;
  }

  private getEmptyStats(): VocabularyStats {
    return {
      totalWords: 0,
      newWords: 0,
      learningWords: 0,
      reviewWords: 0,
      masteredWords: 0,
      dailyGoal: 10,
      dailyProgress: 0,
      streak: 0,
      accuracy: 0,
      averageDifficulty: 0,
      weeklyProgress: new Array(7).fill(0),
      categoryBreakdown: {}
    };
  }

  private exportToCSV(items: VocabularyItem[]): Blob {
    const headers = [
      'Word', 'Translation', 'Context', 'Notes', 'Tags', 'Category',
      'Mastery Level', 'Difficulty', 'Times Reviewed', 'Times Correct',
      'Streak', 'Created At', 'Updated At'
    ];

    const rows = items.map(item => [
      item.word,
      item.translation,
      item.context || '',
      item.notes || '',
      item.tags.join(';'),
      item.category || '',
      item.masteryLevel,
      item.difficulty,
      item.timesReviewed,
      item.timesCorrect,
      item.streak,
      item.createdAt.toISOString(),
      item.updatedAt.toISOString()
    ]);

    const csv = [headers, ...rows]
      .map(row => row.map(cell => `"${cell}"`).join(','))
      .join('\n');

    return new Blob([csv], { type: 'text/csv' });
  }

  private exportToJSON(items: VocabularyItem[]): Blob {
    const exportData = {
      version: '1.0',
      exportedAt: new Date().toISOString(),
      totalItems: items.length,
      items
    };

    return new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
  }

  private exportToAnki(items: VocabularyItem[]): Blob {
    // Anki deck format (simplified)
    const ankiData = items.map(item => ({
      front: item.word,
      back: item.translation,
      context: item.context,
      notes: item.notes,
      tags: item.tags
    }));

    return new Blob([JSON.stringify(ankiData, null, 2)], { type: 'application/json' });
  }

  private parseCSV(text: string): Partial<VocabularyItem>[] {
    const lines = text.split('\n');
    const headers = lines[0].split(',').map(h => h.replace(/"/g, ''));
    
    return lines.slice(1).map(line => {
      const values = line.split(',').map(v => v.replace(/"/g, ''));
      const item: Partial<VocabularyItem> = {};
      
      headers.forEach((header, index) => {
        const value = values[index];
        switch (header.toLowerCase()) {
          case 'word':
            item.word = value;
            break;
          case 'translation':
            item.translation = value;
            break;
          case 'context':
            item.context = value;
            break;
          case 'notes':
            item.notes = value;
            break;
          case 'tags':
            item.tags = value ? value.split(';') : [];
            break;
          case 'category':
            item.category = value;
            break;
        }
      });
      
      return item;
    }).filter(item => item.word && item.translation);
  }
}

export const vocabularyService = new VocabularyService();