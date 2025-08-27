import { useState, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { VocabularyWord, UseVocabularyReturn } from '../types';
import { supabase } from './useSupabase';
import toast from 'react-hot-toast';

interface VocabularyFilters {
  learned?: boolean;
  difficulty?: number[];
  language?: string;
  search?: string;
}

class VocabularyAPI {
  async getVocabularyWords(userId: string, filters: VocabularyFilters = {}): Promise<VocabularyWord[]> {
    let query = supabase
      .from('vocabulary_words')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false });

    // Apply filters
    if (filters.learned !== undefined) {
      query = query.eq('learned', filters.learned);
    }

    if (filters.difficulty && filters.difficulty.length > 0) {
      query = query.in('difficulty_level', filters.difficulty);
    }

    if (filters.language) {
      query = query.eq('language', filters.language);
    }

    if (filters.search) {
      query = query.or(`word.ilike.%${filters.search}%,definition.ilike.%${filters.search}%`);
    }

    const { data, error } = await query;

    if (error) {
      throw new Error(`Failed to fetch vocabulary: ${error.message}`);
    }

    return data || [];
  }

  async addVocabularyWord(userId: string, word: Omit<VocabularyWord, 'id' | 'created_at' | 'user_id'>): Promise<VocabularyWord> {
    const { data, error } = await supabase
      .from('vocabulary_words')
      .insert([{ ...word, user_id: userId }])
      .select()
      .single();

    if (error) {
      throw new Error(`Failed to add vocabulary word: ${error.message}`);
    }

    return data;
  }

  async updateVocabularyWord(wordId: string, updates: Partial<VocabularyWord>): Promise<VocabularyWord> {
    const { data, error } = await supabase
      .from('vocabulary_words')
      .update(updates)
      .eq('id', wordId)
      .select()
      .single();

    if (error) {
      throw new Error(`Failed to update vocabulary word: ${error.message}`);
    }

    return data;
  }

  async deleteVocabularyWord(wordId: string): Promise<void> {
    const { error } = await supabase
      .from('vocabulary_words')
      .delete()
      .eq('id', wordId);

    if (error) {
      throw new Error(`Failed to delete vocabulary word: ${error.message}`);
    }
  }

  async exportVocabulary(userId: string, format: 'csv' | 'anki'): Promise<string> {
    const words = await this.getVocabularyWords(userId);

    if (format === 'csv') {
      return this.exportToCSV(words);
    } else {
      return this.exportToAnki(words);
    }
  }

  private exportToCSV(words: VocabularyWord[]): string {
    const headers = ['Word', 'Definition', 'Translation', 'Language', 'Difficulty', 'Context', 'Learned', 'Review Count'];
    const rows = words.map(word => [
      word.word,
      word.definition,
      word.translation || '',
      word.language,
      word.difficulty_level.toString(),
      word.context,
      word.learned ? 'Yes' : 'No',
      word.review_count.toString(),
    ]);

    return [headers, ...rows]
      .map(row => row.map(cell => `"${cell.replace(/"/g, '""')}"`).join(','))
      .join('\n');
  }

  private exportToAnki(words: VocabularyWord[]): string {
    // Anki uses tab-separated values
    return words
      .map(word => [
        word.word,
        word.definition,
        word.translation || '',
        word.context,
        `Difficulty: ${word.difficulty_level}`,
      ].join('\t'))
      .join('\n');
  }
}

const vocabularyAPI = new VocabularyAPI();

export const useVocabulary = (filters: VocabularyFilters = {}): UseVocabularyReturn => {
  const queryClient = useQueryClient();
  const [currentUserId, setCurrentUserId] = useState<string | null>(null);

  // Get current user
  React.useEffect(() => {
    const getCurrentUser = async () => {
      const { data: { user } } = await supabase.auth.getUser();
      setCurrentUserId(user?.id || null);
    };

    getCurrentUser();

    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      setCurrentUserId(session?.user?.id || null);
    });

    return () => subscription.unsubscribe();
  }, []);

  // Fetch vocabulary words
  const {
    data: words = [],
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['vocabulary', currentUserId, filters],
    queryFn: () => {
      if (!currentUserId) throw new Error('User not authenticated');
      return vocabularyAPI.getVocabularyWords(currentUserId, filters);
    },
    enabled: !!currentUserId,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
  });

  // Add word mutation
  const addWordMutation = useMutation({
    mutationFn: (word: Omit<VocabularyWord, 'id' | 'created_at' | 'user_id'>) => {
      if (!currentUserId) throw new Error('User not authenticated');
      return vocabularyAPI.addVocabularyWord(currentUserId, word);
    },
    onSuccess: (newWord) => {
      // Optimistically update the cache
      queryClient.setQueryData(
        ['vocabulary', currentUserId, filters],
        (oldData: VocabularyWord[] | undefined) => [newWord, ...(oldData || [])]
      );
      toast.success(`Added "${newWord.word}" to vocabulary`);
    },
    onError: (error: Error) => {
      toast.error(error.message);
    },
  });

  // Update word mutation
  const updateWordMutation = useMutation({
    mutationFn: ({ id, updates }: { id: string; updates: Partial<VocabularyWord> }) =>
      vocabularyAPI.updateVocabularyWord(id, updates),
    onSuccess: (updatedWord) => {
      // Update the cache
      queryClient.setQueryData(
        ['vocabulary', currentUserId, filters],
        (oldData: VocabularyWord[] | undefined) =>
          oldData?.map(word => word.id === updatedWord.id ? updatedWord : word) || []
      );
      toast.success('Vocabulary word updated');
    },
    onError: (error: Error) => {
      toast.error(error.message);
    },
  });

  // Delete word mutation
  const deleteWordMutation = useMutation({
    mutationFn: vocabularyAPI.deleteVocabularyWord,
    onSuccess: (_, deletedId) => {
      // Remove from cache
      queryClient.setQueryData(
        ['vocabulary', currentUserId, filters],
        (oldData: VocabularyWord[] | undefined) =>
          oldData?.filter(word => word.id !== deletedId) || []
      );
      toast.success('Vocabulary word deleted');
    },
    onError: (error: Error) => {
      toast.error(error.message);
    },
  });

  // Export mutation
  const exportMutation = useMutation({
    mutationFn: (format: 'csv' | 'anki') => {
      if (!currentUserId) throw new Error('User not authenticated');
      return vocabularyAPI.exportVocabulary(currentUserId, format);
    },
    onSuccess: (data, format) => {
      // Create download
      const blob = new Blob([data], { type: format === 'csv' ? 'text/csv' : 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `vocabulary.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      toast.success(`Vocabulary exported as ${format.toUpperCase()}`);
    },
    onError: (error: Error) => {
      toast.error(error.message);
    },
  });

  const addWord = useCallback(
    async (word: Omit<VocabularyWord, 'id' | 'created_at' | 'user_id'>) => {
      return addWordMutation.mutateAsync(word);
    },
    [addWordMutation]
  );

  const updateWord = useCallback(
    async (id: string, updates: Partial<VocabularyWord>) => {
      return updateWordMutation.mutateAsync({ id, updates });
    },
    [updateWordMutation]
  );

  const deleteWord = useCallback(
    async (id: string) => {
      return deleteWordMutation.mutateAsync(id);
    },
    [deleteWordMutation]
  );

  const exportWords = useCallback(
    async (format: 'csv' | 'anki') => {
      return exportMutation.mutateAsync(format);
    },
    [exportMutation]
  );

  return {
    words,
    isLoading: isLoading || !currentUserId,
    error: error ? {
      code: 'VOCABULARY_ERROR',
      message: error.message,
      timestamp: new Date().toISOString(),
      recoverable: true,
      details: error,
    } : null,
    addWord,
    updateWord,
    deleteWord,
    exportWords,
  };
};

// Hook for vocabulary statistics
export const useVocabularyStats = () => {
  const [currentUserId, setCurrentUserId] = useState<string | null>(null);

  React.useEffect(() => {
    const getCurrentUser = async () => {
      const { data: { user } } = await supabase.auth.getUser();
      setCurrentUserId(user?.id || null);
    };
    getCurrentUser();
  }, []);

  return useQuery({
    queryKey: ['vocabulary-stats', currentUserId],
    queryFn: async () => {
      if (!currentUserId) throw new Error('User not authenticated');
      
      const words = await vocabularyAPI.getVocabularyWords(currentUserId);
      
      return {
        total: words.length,
        learned: words.filter(w => w.learned).length,
        byDifficulty: {
          1: words.filter(w => w.difficulty_level === 1).length,
          2: words.filter(w => w.difficulty_level === 2).length,
          3: words.filter(w => w.difficulty_level === 3).length,
          4: words.filter(w => w.difficulty_level === 4).length,
          5: words.filter(w => w.difficulty_level === 5).length,
        },
        averageReviews: words.length > 0 
          ? words.reduce((sum, w) => sum + w.review_count, 0) / words.length 
          : 0,
      };
    },
    enabled: !!currentUserId,
    staleTime: 5 * 60 * 1000,
  });
};