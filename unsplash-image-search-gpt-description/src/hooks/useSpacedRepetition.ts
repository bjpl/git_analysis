import { useState, useCallback, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { VocabularyWord } from '../types';
import { supabase } from './useSupabase';
import toast from 'react-hot-toast';

interface SpacedRepetitionReview {
  id: string;
  vocabulary_word_id: string;
  user_id: string;
  ease_factor: number; // 1.3 to 2.5 (Anki algorithm)
  repetition_number: number;
  interval_days: number;
  next_review_date: string;
  quality: 0 | 1 | 2 | 3 | 4 | 5; // Last review quality (0=worst, 5=best)
  created_at: string;
  updated_at: string;
}

interface ReviewSession {
  id: string;
  user_id: string;
  started_at: string;
  completed_at?: string;
  total_cards: number;
  cards_completed: number;
  accuracy: number;
}

interface ReviewCard {
  vocabulary_word: VocabularyWord;
  review: SpacedRepetitionReview | null;
  is_new: boolean;
}

interface UseSpacedRepetitionReturn {
  // Current session
  currentSession: ReviewSession | null;
  currentCard: ReviewCard | null;
  cardsRemaining: number;
  sessionProgress: number;
  
  // Statistics
  dueCount: number;
  newCount: number;
  reviewedToday: number;
  accuracy: number;
  streak: number;
  
  // Actions
  startReviewSession: (cardLimit?: number) => Promise<void>;
  submitReview: (quality: 0 | 1 | 2 | 3 | 4 | 5) => Promise<void>;
  endSession: () => Promise<void>;
  
  // Card management
  getDueCards: () => Promise<ReviewCard[]>;
  getNewCards: () => Promise<ReviewCard[]>;
  
  // Loading states
  isLoading: boolean;
  error: Error | null;
}

// Spaced repetition algorithm (simplified SM-2)
const calculateNextReview = (
  currentInterval: number,
  repetitionNumber: number,
  easeFactor: number,
  quality: 0 | 1 | 2 | 3 | 4 | 5
): { newInterval: number; newEaseFactor: number; newRepetitionNumber: number } => {
  let newEaseFactor = easeFactor;
  let newRepetitionNumber = repetitionNumber;
  let newInterval: number;

  // Update ease factor based on quality
  newEaseFactor = Math.max(
    1.3,
    easeFactor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
  );

  if (quality < 3) {
    // Failed review - start over
    newRepetitionNumber = 0;
    newInterval = 1;
  } else {
    // Successful review
    newRepetitionNumber = repetitionNumber + 1;
    
    if (newRepetitionNumber === 1) {
      newInterval = 1;
    } else if (newRepetitionNumber === 2) {
      newInterval = 6;
    } else {
      newInterval = Math.round(currentInterval * newEaseFactor);
    }
  }

  return { newInterval, newEaseFactor, newRepetitionNumber };
};

class SpacedRepetitionAPI {
  async getDueReviews(userId: string): Promise<SpacedRepetitionReview[]> {
    const today = new Date().toISOString().split('T')[0];
    
    const { data, error } = await supabase
      .from('spaced_repetition_reviews')
      .select(`
        *,
        vocabulary_words!vocabulary_word_id (*)
      `)
      .eq('user_id', userId)
      .lte('next_review_date', today)
      .order('next_review_date', { ascending: true });

    if (error) throw error;
    return data || [];
  }

  async getNewVocabularyWords(userId: string, limit = 20): Promise<VocabularyWord[]> {
    // Get words that don't have any reviews yet
    const { data, error } = await supabase
      .from('vocabulary_words')
      .select(`
        *,
        spaced_repetition_reviews!vocabulary_word_id (id)
      `)
      .eq('user_id', userId)
      .is('spaced_repetition_reviews.id', null)
      .limit(limit)
      .order('created_at', { ascending: true });

    if (error) throw error;
    return data?.filter(word => !word.spaced_repetition_reviews?.length) || [];
  }

  async createReviewSession(userId: string, cardCount: number): Promise<ReviewSession> {
    const { data, error } = await supabase
      .from('review_sessions')
      .insert({
        user_id: userId,
        started_at: new Date().toISOString(),
        total_cards: cardCount,
        cards_completed: 0,
        accuracy: 0,
      })
      .select()
      .single();

    if (error) throw error;
    return data;
  }

  async submitReview(
    userId: string,
    vocabularyWordId: string,
    quality: 0 | 1 | 2 | 3 | 4 | 5,
    sessionId: string
  ): Promise<void> {
    // Get existing review or create new one
    let { data: existingReview, error: fetchError } = await supabase
      .from('spaced_repetition_reviews')
      .select('*')
      .eq('user_id', userId)
      .eq('vocabulary_word_id', vocabularyWordId)
      .single();

    if (fetchError && fetchError.code !== 'PGRST116') {
      throw fetchError;
    }

    let newReview: Partial<SpacedRepetitionReview>;

    if (existingReview) {
      // Update existing review
      const { newInterval, newEaseFactor, newRepetitionNumber } = calculateNextReview(
        existingReview.interval_days,
        existingReview.repetition_number,
        existingReview.ease_factor,
        quality
      );

      const nextReviewDate = new Date();
      nextReviewDate.setDate(nextReviewDate.getDate() + newInterval);

      newReview = {
        ease_factor: newEaseFactor,
        repetition_number: newRepetitionNumber,
        interval_days: newInterval,
        next_review_date: nextReviewDate.toISOString().split('T')[0],
        quality,
        updated_at: new Date().toISOString(),
      };

      const { error: updateError } = await supabase
        .from('spaced_repetition_reviews')
        .update(newReview)
        .eq('id', existingReview.id);

      if (updateError) throw updateError;
    } else {
      // Create new review
      const { newInterval, newEaseFactor, newRepetitionNumber } = calculateNextReview(
        0, 0, 2.5, quality
      );

      const nextReviewDate = new Date();
      nextReviewDate.setDate(nextReviewDate.getDate() + newInterval);

      newReview = {
        user_id: userId,
        vocabulary_word_id: vocabularyWordId,
        ease_factor: newEaseFactor,
        repetition_number: newRepetitionNumber,
        interval_days: newInterval,
        next_review_date: nextReviewDate.toISOString().split('T')[0],
        quality,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      const { error: insertError } = await supabase
        .from('spaced_repetition_reviews')
        .insert(newReview);

      if (insertError) throw insertError;
    }

    // Update session progress
    const { error: sessionError } = await supabase
      .from('review_sessions')
      .update({
        cards_completed: supabase.raw('cards_completed + 1'),
        updated_at: new Date().toISOString(),
      })
      .eq('id', sessionId);

    if (sessionError) throw sessionError;
  }

  async getReviewStats(userId: string): Promise<{
    reviewedToday: number;
    accuracy: number;
    streak: number;
  }> {
    const today = new Date().toISOString().split('T')[0];
    
    // Get reviews from today
    const { data: todayReviews, error: todayError } = await supabase
      .from('spaced_repetition_reviews')
      .select('quality')
      .eq('user_id', userId)
      .gte('updated_at', today);

    if (todayError) throw todayError;

    const reviewedToday = todayReviews?.length || 0;
    const successfulReviews = todayReviews?.filter(r => r.quality >= 3).length || 0;
    const accuracy = reviewedToday > 0 ? (successfulReviews / reviewedToday) * 100 : 0;

    // Calculate streak (simplified - days with at least one review)
    const { data: recentSessions, error: streakError } = await supabase
      .from('review_sessions')
      .select('started_at')
      .eq('user_id', userId)
      .gt('cards_completed', 0)
      .order('started_at', { ascending: false })
      .limit(30);

    if (streakError) throw streakError;

    let streak = 0;
    const sessionDates = new Set(
      recentSessions?.map(s => s.started_at.split('T')[0]) || []
    );

    const currentDate = new Date();
    while (true) {
      const dateStr = currentDate.toISOString().split('T')[0];
      if (sessionDates.has(dateStr)) {
        streak++;
        currentDate.setDate(currentDate.getDate() - 1);
      } else {
        break;
      }
    }

    return { reviewedToday, accuracy, streak };
  }
}

const spacedRepetitionAPI = new SpacedRepetitionAPI();

export const useSpacedRepetition = (): UseSpacedRepetitionReturn => {
  const queryClient = useQueryClient();
  const [currentSession, setCurrentSession] = useState<ReviewSession | null>(null);
  const [reviewCards, setReviewCards] = useState<ReviewCard[]>([]);
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [currentUserId, setCurrentUserId] = useState<string | null>(null);

  // Get current user
  React.useEffect(() => {
    const getCurrentUser = async () => {
      const { data: { user } } = await supabase.auth.getUser();
      setCurrentUserId(user?.id || null);
    };
    getCurrentUser();
  }, []);

  // Get due reviews
  const {
    data: dueReviews = [],
    isLoading: isDueLoading,
    error: dueError,
  } = useQuery({
    queryKey: ['due-reviews', currentUserId],
    queryFn: () => {
      if (!currentUserId) throw new Error('User not authenticated');
      return spacedRepetitionAPI.getDueReviews(currentUserId);
    },
    enabled: !!currentUserId,
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
  });

  // Get new vocabulary words
  const {
    data: newWords = [],
    isLoading: isNewLoading,
    error: newError,
  } = useQuery({
    queryKey: ['new-vocabulary', currentUserId],
    queryFn: () => {
      if (!currentUserId) throw new Error('User not authenticated');
      return spacedRepetitionAPI.getNewVocabularyWords(currentUserId);
    },
    enabled: !!currentUserId,
  });

  // Get review statistics
  const {
    data: stats = { reviewedToday: 0, accuracy: 0, streak: 0 },
    isLoading: isStatsLoading,
  } = useQuery({
    queryKey: ['review-stats', currentUserId],
    queryFn: () => {
      if (!currentUserId) throw new Error('User not authenticated');
      return spacedRepetitionAPI.getReviewStats(currentUserId);
    },
    enabled: !!currentUserId,
  });

  // Computed values
  const dueCount = dueReviews.length;
  const newCount = newWords.length;
  const currentCard = reviewCards[currentCardIndex] || null;
  const cardsRemaining = Math.max(0, reviewCards.length - currentCardIndex);
  const sessionProgress = currentSession 
    ? (currentSession.cards_completed / currentSession.total_cards) * 100 
    : 0;

  const startReviewSession = useCallback(async (cardLimit = 20) => {
    if (!currentUserId) throw new Error('User not authenticated');

    // Combine due reviews and new words
    const dueCards: ReviewCard[] = dueReviews.map(review => ({
      vocabulary_word: review.vocabulary_words as VocabularyWord,
      review,
      is_new: false,
    }));

    const newCards: ReviewCard[] = newWords.slice(0, Math.max(0, cardLimit - dueCards.length)).map(word => ({
      vocabulary_word: word,
      review: null,
      is_new: true,
    }));

    const allCards = [...dueCards, ...newCards].slice(0, cardLimit);
    
    if (allCards.length === 0) {
      toast.info('No cards available for review');
      return;
    }

    // Shuffle cards for better learning
    const shuffledCards = allCards.sort(() => Math.random() - 0.5);
    
    setReviewCards(shuffledCards);
    setCurrentCardIndex(0);

    // Create review session
    const session = await spacedRepetitionAPI.createReviewSession(currentUserId, shuffledCards.length);
    setCurrentSession(session);

    toast.success(`Started review session with ${shuffledCards.length} cards`);
  }, [currentUserId, dueReviews, newWords]);

  const submitReview = useCallback(async (quality: 0 | 1 | 2 | 3 | 4 | 5) => {
    if (!currentUserId || !currentSession || !currentCard) {
      throw new Error('Invalid review state');
    }

    await spacedRepetitionAPI.submitReview(
      currentUserId,
      currentCard.vocabulary_word.id,
      quality,
      currentSession.id
    );

    // Move to next card
    if (currentCardIndex < reviewCards.length - 1) {
      setCurrentCardIndex(prev => prev + 1);
    } else {
      // Session complete
      await endSession();
    }

    // Update session progress
    setCurrentSession(prev => prev ? {
      ...prev,
      cards_completed: prev.cards_completed + 1,
    } : null);

    // Invalidate queries to refresh data
    queryClient.invalidateQueries({ queryKey: ['due-reviews'] });
    queryClient.invalidateQueries({ queryKey: ['new-vocabulary'] });
    queryClient.invalidateQueries({ queryKey: ['review-stats'] });

  }, [currentUserId, currentSession, currentCard, currentCardIndex, reviewCards.length, queryClient]);

  const endSession = useCallback(async () => {
    if (!currentSession) return;

    // Update session completion
    const { error } = await supabase
      .from('review_sessions')
      .update({
        completed_at: new Date().toISOString(),
      })
      .eq('id', currentSession.id);

    if (error) {
      console.error('Failed to complete session:', error);
    }

    // Reset session state
    setCurrentSession(null);
    setReviewCards([]);
    setCurrentCardIndex(0);

    toast.success('Review session completed!');
  }, [currentSession]);

  const getDueCards = useCallback(async (): Promise<ReviewCard[]> => {
    if (!currentUserId) return [];
    
    const reviews = await spacedRepetitionAPI.getDueReviews(currentUserId);
    return reviews.map(review => ({
      vocabulary_word: review.vocabulary_words as VocabularyWord,
      review,
      is_new: false,
    }));
  }, [currentUserId]);

  const getNewCards = useCallback(async (): Promise<ReviewCard[]> => {
    if (!currentUserId) return [];
    
    const words = await spacedRepetitionAPI.getNewVocabularyWords(currentUserId);
    return words.map(word => ({
      vocabulary_word: word,
      review: null,
      is_new: true,
    }));
  }, [currentUserId]);

  const isLoading = isDueLoading || isNewLoading || isStatsLoading || !currentUserId;
  const error = dueError || newError;

  return {
    currentSession,
    currentCard,
    cardsRemaining,
    sessionProgress,
    dueCount,
    newCount,
    reviewedToday: stats.reviewedToday,
    accuracy: stats.accuracy,
    streak: stats.streak,
    startReviewSession,
    submitReview,
    endSession,
    getDueCards,
    getNewCards,
    isLoading,
    error,
  };
};