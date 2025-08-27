// Core types for VocabLens application

export interface UnsplashImage {
  id: string;
  urls: {
    regular: string;
    small: string;
    thumb: string;
  };
  alt_description?: string;
  width: number;
  height: number;
  user?: {
    name: string;
    username: string;
  };
}

export interface VocabularyWord {
  id?: string;
  word: string;
  definition: string;
  language: string;
  difficulty_level: 1 | 2 | 3 | 4 | 5;
  context?: string;
  image_id?: string;
  learned: boolean;
  review_count: number;
  created_at?: string;
  updated_at?: string;
}

export interface DescriptionStyle {
  id: string;
  name: string;
  description: string;
  vocabularyComplexity: 1 | 2 | 3 | 4 | 5;
}

export interface AIGeneratedDescription {
  id: string;
  imageId: string;
  description: string;
  style: DescriptionStyle;
  vocabulary: VocabularyWord[];
  tokenCount: number;
  processingTime: number;
  created_at: string;
}

export interface User {
  id: string;
  email: string;
  username?: string;
  created_at: string;
  updated_at: string;
}

export interface AppState {
  isOnline: boolean;
  theme: 'light' | 'dark' | 'system';
  language: string;
}

// Vocabulary Management Types
export enum MasteryLevel {
  NEW = 'new',
  LEARNING = 'learning', 
  REVIEW = 'review',
  MASTERED = 'mastered'
}

export interface VocabularyItem {
  id: string;
  word: string;
  definition: string;
  translation?: string;
  pronunciation?: string;
  partOfSpeech?: string;
  language: string;
  difficulty: number; // 1-10
  context?: string;
  imageId?: string;
  imageUrl?: string;
  category?: string;
  tags: string[];
  examples: string[];
  masteryLevel: MasteryLevel;
  timesReviewed: number;
  timesCorrect: number;
  streak: number;
  easeFactor: number;
  intervalDays: number;
  lastReviewedAt?: Date;
  nextReviewAt?: Date;
  createdAt: Date;
  updatedAt: Date;
  userId?: string;
  sharedFromUserId?: string;
}

export interface VocabularyStats {
  totalWords: number;
  newWords: number;
  learningWords: number;
  reviewWords: number;
  masteredWords: number;
  accuracy: number;
  averageDifficulty: number;
  streak: number;
  dailyGoal: number;
  dailyProgress: number;
  weeklyProgress: number[];
  categoryBreakdown: Record<string, number>;
}

export interface VocabularyAnalytics {
  learningVelocity: number;
  retentionRate: number;
  difficultyDistribution: Record<number, number>;
  categoryProgress: Record<string, { total: number; mastered: number; accuracy: number }>;
  weeklyActivity: Array<{
    date: string;
    wordsLearned: number;
    reviewsCompleted: number;
    accuracy: number;
  }>;
  streakHistory: Array<{
    date: string;
    streak: number;
  }>;
}

export interface SharedVocabularyList {
  id: string;
  name: string;
  description?: string;
  category?: string;
  tags: string[];
  items: VocabularyItem[];
  ownerId: string;
  ownerName: string;
  rating: number;
  downloadCount: number;
  isPublic: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface VocabularyMarketplace {
  lists: SharedVocabularyList[];
  categories: string[];
  popularTags: string[];
  featuredLists: SharedVocabularyList[];
}

export interface SpacedRepetitionSession {
  id: string;
  items: VocabularyItem[];
  currentIndex: number;
  startedAt: Date;
  completedAt?: Date;
  results: Array<{
    itemId: string;
    correct: boolean;
    responseTime: number;
    difficulty: number;
  }>;
}

export interface SRSReviewSession {
  id: string;
  items: VocabularyItem[];
  currentIndex: number;
  startedAt: Date;
  completedAt?: Date;
  totalCorrect: number;
  totalIncorrect: number;
}

export enum VocabularySortBy {
  DATE_CREATED = 'date_created',
  DATE_UPDATED = 'date_updated',
  ALPHABETICAL = 'alphabetical',
  DIFFICULTY = 'difficulty',
  MASTERY_LEVEL = 'mastery_level',
  REVIEW_DUE = 'review_due'
}

export interface OfflineVocabularyChange {
  id: string;
  action: 'create' | 'update' | 'delete';
  data: VocabularyItem;
  timestamp: Date;
  synced: boolean;
}

export enum ConflictResolution {
  LOCAL_WINS = 'local_wins',
  REMOTE_WINS = 'remote_wins', 
  MERGE = 'merge',
  ASK_USER = 'ask_user'
}

export enum ExportFormat {
  JSON = 'json',
  CSV = 'csv',
  ANKI = 'anki',
  PDF = 'pdf',
  TXT = 'txt'
}

// Re-export for compatibility
export type Image = UnsplashImage;