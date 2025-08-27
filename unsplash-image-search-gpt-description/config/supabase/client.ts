import { createClient, type SupabaseClient } from '@supabase/supabase-js'
import { Database } from '../../supabase/types/database.types'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

// Client-side Supabase instance
export const supabase: SupabaseClient<Database> = createClient<Database>(
  supabaseUrl,
  supabaseAnonKey,
  {
    auth: {
      autoRefreshToken: true,
      persistSession: true,
      detectSessionInUrl: true,
    },
  }
)

// Server-side Supabase instance (for API routes)
export function createServerSupabaseClient(accessToken?: string): SupabaseClient<Database> {
  return createClient<Database>(
    supabaseUrl,
    supabaseAnonKey,
    {
      auth: {
        autoRefreshToken: false,
        persistSession: false,
      },
      global: {
        headers: accessToken ? {
          Authorization: `Bearer ${accessToken}`,
        } : {},
      },
    }
  )
}

// Type definitions for better TypeScript support
export type Tables<T extends keyof Database['public']['Tables']> = Database['public']['Tables'][T]['Row']
export type Enums<T extends keyof Database['public']['Enums']> = Database['public']['Enums'][T]

// Utility types for common table operations
export type VocabularyItem = Tables<'vocabulary_items'>
export type User = Tables<'users'>
export type SearchSession = Tables<'search_sessions'>
export type QuizResult = Tables<'quiz_results'>
export type SharedList = Tables<'shared_lists'>
export type UserPreferences = Tables<'user_preferences'>

// Insert types
export type VocabularyItemInsert = Database['public']['Tables']['vocabulary_items']['Insert']
export type SearchSessionInsert = Database['public']['Tables']['search_sessions']['Insert']
export type QuizResultInsert = Database['public']['Tables']['quiz_results']['Insert']
export type SharedListInsert = Database['public']['Tables']['shared_lists']['Insert']
export type UserPreferencesInsert = Database['public']['Tables']['user_preferences']['Insert']

// Update types
export type VocabularyItemUpdate = Database['public']['Tables']['vocabulary_items']['Update']
export type UserUpdate = Database['public']['Tables']['users']['Update']
export type SearchSessionUpdate = Database['public']['Tables']['search_sessions']['Update']
export type SharedListUpdate = Database['public']['Tables']['shared_lists']['Update']
export type UserPreferencesUpdate = Database['public']['Tables']['user_preferences']['Update']