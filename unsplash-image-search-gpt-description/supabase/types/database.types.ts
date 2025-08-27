export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export interface Database {
  public: {
    Tables: {
      quiz_results: {
        Row: {
          correct_answer: string
          created_at: string
          difficulty: string
          id: string
          is_correct: boolean
          question: string
          quiz_type: string
          response_time_ms: number | null
          user_answer: string | null
          user_id: string
          vocabulary_item_id: string
        }
        Insert: {
          correct_answer: string
          created_at?: string
          difficulty?: string
          id?: string
          is_correct: boolean
          question: string
          quiz_type: string
          response_time_ms?: number | null
          user_answer?: string | null
          user_id: string
          vocabulary_item_id: string
        }
        Update: {
          correct_answer?: string
          created_at?: string
          difficulty?: string
          id?: string
          is_correct?: boolean
          question?: string
          quiz_type?: string
          response_time_ms?: number | null
          user_answer?: string | null
          user_id?: string
          vocabulary_item_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "quiz_results_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "quiz_results_vocabulary_item_id_fkey"
            columns: ["vocabulary_item_id"]
            isOneToOne: false
            referencedRelation: "vocabulary_items"
            referencedColumns: ["id"]
          }
        ]
      }
      search_sessions: {
        Row: {
          created_at: string
          duration_seconds: number | null
          id: string
          query: string
          results_count: number
          selected_image_id: string | null
          style: string
          updated_at: string
          user_id: string
        }
        Insert: {
          created_at?: string
          duration_seconds?: number | null
          id?: string
          query: string
          results_count?: number
          selected_image_id?: string | null
          style?: string
          updated_at?: string
          user_id: string
        }
        Update: {
          created_at?: string
          duration_seconds?: number | null
          id?: string
          query?: string
          results_count?: number
          selected_image_id?: string | null
          style?: string
          updated_at?: string
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "search_sessions_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          }
        ]
      }
      shared_lists: {
        Row: {
          created_at: string
          description: string | null
          download_count: number
          id: string
          is_public: boolean
          owner_id: string
          share_code: string
          tags: string[]
          title: string
          updated_at: string
          vocabulary_items: string[]
        }
        Insert: {
          created_at?: string
          description?: string | null
          download_count?: number
          id?: string
          is_public?: boolean
          owner_id: string
          share_code?: string
          tags?: string[]
          title: string
          updated_at?: string
          vocabulary_items?: string[]
        }
        Update: {
          created_at?: string
          description?: string | null
          download_count?: number
          id?: string
          is_public?: boolean
          owner_id?: string
          share_code?: string
          tags?: string[]
          title?: string
          updated_at?: string
          vocabulary_items?: string[]
        }
        Relationships: [
          {
            foreignKeyName: "shared_lists_owner_id_fkey"
            columns: ["owner_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          }
        ]
      }
      user_preferences: {
        Row: {
          auto_play_pronunciation: boolean
          created_at: string
          daily_goal_notifications: boolean
          dark_mode: boolean
          email_reminders: boolean
          id: string
          language_interface: string
          notifications_enabled: boolean
          quiz_auto_advance: boolean
          show_example_sentences: boolean
          show_pronunciation: boolean
          spaced_repetition_enabled: boolean
          study_reminder_time: string
          updated_at: string
          user_id: string
        }
        Insert: {
          auto_play_pronunciation?: boolean
          created_at?: string
          daily_goal_notifications?: boolean
          dark_mode?: boolean
          email_reminders?: boolean
          id?: string
          language_interface?: string
          notifications_enabled?: boolean
          quiz_auto_advance?: boolean
          show_example_sentences?: boolean
          show_pronunciation?: boolean
          spaced_repetition_enabled?: boolean
          study_reminder_time?: string
          updated_at?: string
          user_id: string
        }
        Update: {
          auto_play_pronunciation?: boolean
          created_at?: string
          daily_goal_notifications?: boolean
          dark_mode?: boolean
          email_reminders?: boolean
          id?: string
          language_interface?: string
          notifications_enabled?: boolean
          quiz_auto_advance?: boolean
          show_example_sentences?: boolean
          show_pronunciation?: boolean
          spaced_repetition_enabled?: boolean
          study_reminder_time?: string
          updated_at?: string
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "user_preferences_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: true
            referencedRelation: "users"
            referencedColumns: ["id"]
          }
        ]
      }
      users: {
        Row: {
          avatar_url: string | null
          created_at: string
          daily_goal: number
          email: string
          full_name: string | null
          id: string
          last_activity_date: string
          preferred_language: string
          quiz_difficulty: string
          streak_count: number
          subscription_expires_at: string | null
          subscription_tier: string
          theme_preference: string
          total_words_learned: number
          updated_at: string
        }
        Insert: {
          avatar_url?: string | null
          created_at?: string
          daily_goal?: number
          email: string
          full_name?: string | null
          id: string
          last_activity_date?: string
          preferred_language?: string
          quiz_difficulty?: string
          streak_count?: number
          subscription_expires_at?: string | null
          subscription_tier?: string
          theme_preference?: string
          total_words_learned?: number
          updated_at?: string
        }
        Update: {
          avatar_url?: string | null
          created_at?: string
          daily_goal?: number
          email?: string
          full_name?: string | null
          id?: string
          last_activity_date?: string
          preferred_language?: string
          quiz_difficulty?: string
          streak_count?: number
          subscription_expires_at?: string | null
          subscription_tier?: string
          theme_preference?: string
          total_words_learned?: number
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "users_id_fkey"
            columns: ["id"]
            isOneToOne: true
            referencedRelation: "users"
            referencedColumns: ["id"]
          }
        ]
      }
      vocabulary_items: {
        Row: {
          created_at: string
          definition: string
          difficulty_level: string
          example_sentence: string | null
          id: string
          image_alt_text: string | null
          image_source: string
          image_url: string | null
          is_archived: boolean
          is_favorite: boolean
          last_practiced_at: string | null
          mastery_level: number
          next_review_at: string
          notes: string | null
          part_of_speech: string | null
          pronunciation: string | null
          source_language: string
          tags: string[]
          target_language: string
          times_correct: number
          times_practiced: number
          translation: string | null
          unsplash_photo_id: string | null
          unsplash_photographer: string | null
          updated_at: string
          user_id: string
          word: string
        }
        Insert: {
          created_at?: string
          definition: string
          difficulty_level?: string
          example_sentence?: string | null
          id?: string
          image_alt_text?: string | null
          image_source?: string
          image_url?: string | null
          is_archived?: boolean
          is_favorite?: boolean
          last_practiced_at?: string | null
          mastery_level?: number
          next_review_at?: string
          notes?: string | null
          part_of_speech?: string | null
          pronunciation?: string | null
          source_language?: string
          tags?: string[]
          target_language?: string
          times_correct?: number
          times_practiced?: number
          translation?: string | null
          unsplash_photo_id?: string | null
          unsplash_photographer?: string | null
          updated_at?: string
          user_id: string
          word: string
        }
        Update: {
          created_at?: string
          definition?: string
          difficulty_level?: string
          example_sentence?: string | null
          id?: string
          image_alt_text?: string | null
          image_source?: string
          image_url?: string | null
          is_archived?: boolean
          is_favorite?: boolean
          last_practiced_at?: string | null
          mastery_level?: number
          next_review_at?: string
          notes?: string | null
          part_of_speech?: string | null
          pronunciation?: string | null
          source_language?: string
          tags?: string[]
          target_language?: string
          times_correct?: number
          times_practiced?: number
          translation?: string | null
          unsplash_photo_id?: string | null
          unsplash_photographer?: string | null
          updated_at?: string
          user_id?: string
          word?: string
        }
        Relationships: [
          {
            foreignKeyName: "vocabulary_items_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          }
        ]
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      cleanup_old_exports: {
        Args: Record<PropertyKey, never>
        Returns: undefined
      }
      get_vocabulary_for_review: {
        Args: {
          user_uuid: string
          limit_count?: number
        }
        Returns: {
          id: string
          word: string
          definition: string
          pronunciation: string | null
          part_of_speech: string | null
          example_sentence: string | null
          difficulty_level: string
          translation: string | null
          image_url: string | null
          image_alt_text: string | null
          mastery_level: number
          times_practiced: number
          times_correct: number
          next_review_at: string
        }[]
      }
      search_vocabulary: {
        Args: {
          user_uuid: string
          search_query?: string
          tag_filter?: string[]
          difficulty_filter?: string
          limit_count?: number
          offset_count?: number
        }
        Returns: {
          id: string
          word: string
          definition: string
          pronunciation: string | null
          part_of_speech: string | null
          example_sentence: string | null
          difficulty_level: string
          translation: string | null
          image_url: string | null
          image_alt_text: string | null
          tags: string[]
          mastery_level: number
          times_practiced: number
          is_favorite: boolean
          created_at: string
        }[]
      }
      update_vocabulary_practice: {
        Args: {
          item_id: string
          is_correct_answer: boolean
          response_time?: number
        }
        Returns: undefined
      }
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}