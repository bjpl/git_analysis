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

// Re-export for compatibility
export type Image = UnsplashImage;