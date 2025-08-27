import { createClient, type SupabaseClient, type User } from '@supabase/supabase-js';
import { Database } from '../types';

export interface SupabaseConfig {
  url: string;
  anonKey: string;
  serviceRoleKey?: string;
  options?: {
    auth?: {
      autoRefreshToken?: boolean;
      persistSession?: boolean;
      detectSessionInUrl?: boolean;
      flowType?: 'pkce' | 'implicit';
    };
    realtime?: {
      params?: {
        eventsPerSecond?: number;
      };
    };
    global?: {
      headers?: Record<string, string>;
    };
  };
}

export interface AuthError {
  message: string;
  status?: number;
  code?: string;
}

export interface AuthUser {
  id: string;
  email: string;
  emailConfirmed: boolean;
  phone?: string;
  confirmedAt?: string;
  lastSignInAt?: string;
  appMetadata: Record<string, any>;
  userMetadata: Record<string, any>;
  identities?: Array<{
    id: string;
    userId: string;
    identityData: Record<string, any>;
    provider: string;
    createdAt: string;
    updatedAt: string;
  }>;
}

export interface RealtimeChannel {
  subscribe: (callback: (payload: any) => void) => void;
  unsubscribe: () => void;
  on: (event: string, callback: (payload: any) => void) => void;
}

class SupabaseService {
  private client: SupabaseClient<Database>;
  private config: SupabaseConfig;
  private channels: Map<string, RealtimeChannel> = new Map();
  private authListeners: Array<(user: AuthUser | null) => void> = [];

  constructor(config?: Partial<SupabaseConfig>) {
    // Get configuration from environment variables with fallbacks
    const supabaseUrl = config?.url || process.env.NEXT_PUBLIC_SUPABASE_URL || process.env.VITE_SUPABASE_URL;
    const supabaseAnonKey = config?.anonKey || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || process.env.VITE_SUPABASE_ANON_KEY;
    
    if (!supabaseUrl || !supabaseAnonKey) {
      throw new Error('Supabase URL and anon key are required');
    }

    this.config = {
      url: supabaseUrl,
      anonKey: supabaseAnonKey,
      serviceRoleKey: config?.serviceRoleKey || process.env.SUPABASE_SERVICE_ROLE_KEY,
      options: {
        auth: {
          autoRefreshToken: true,
          persistSession: true,
          detectSessionInUrl: true,
          flowType: 'pkce',
          ...config?.options?.auth
        },
        realtime: {
          params: {
            eventsPerSecond: 10
          },
          ...config?.options?.realtime
        },
        ...config?.options
      }
    };

    // Create Supabase client
    this.client = createClient<Database>(
      this.config.url,
      this.config.anonKey,
      this.config.options
    );

    // Set up auth state listener
    this.setupAuthListener();
  }

  /**
   * Get the Supabase client instance
   */
  getClient(): SupabaseClient<Database> {
    return this.client;
  }

  /**
   * Authentication methods
   */
  async signUp(email: string, password: string, metadata?: Record<string, any>): Promise<{
    user: AuthUser | null;
    session: any;
    error: AuthError | null;
  }> {
    try {
      const { data, error } = await this.client.auth.signUp({
        email,
        password,
        options: {
          data: metadata
        }
      });

      return {
        user: data.user ? this.transformUser(data.user) : null,
        session: data.session,
        error: error ? this.transformAuthError(error) : null
      };
    } catch (error) {
      return {
        user: null,
        session: null,
        error: this.transformAuthError(error)
      };
    }
  }

  async signIn(email: string, password: string): Promise<{
    user: AuthUser | null;
    session: any;
    error: AuthError | null;
  }> {
    try {
      const { data, error } = await this.client.auth.signInWithPassword({
        email,
        password
      });

      return {
        user: data.user ? this.transformUser(data.user) : null,
        session: data.session,
        error: error ? this.transformAuthError(error) : null
      };
    } catch (error) {
      return {
        user: null,
        session: null,
        error: this.transformAuthError(error)
      };
    }
  }

  async signInWithProvider(provider: 'google' | 'github' | 'discord' | 'twitter'): Promise<{
    data: any;
    error: AuthError | null;
  }> {
    try {
      const { data, error } = await this.client.auth.signInWithOAuth({
        provider,
        options: {
          redirectTo: `${window.location.origin}/auth/callback`
        }
      });

      return {
        data,
        error: error ? this.transformAuthError(error) : null
      };
    } catch (error) {
      return {
        data: null,
        error: this.transformAuthError(error)
      };
    }
  }

  async signOut(): Promise<{ error: AuthError | null }> {
    try {
      const { error } = await this.client.auth.signOut();
      
      // Clear all channels when signing out
      this.clearAllChannels();
      
      return {
        error: error ? this.transformAuthError(error) : null
      };
    } catch (error) {
      return {
        error: this.transformAuthError(error)
      };
    }
  }

  async resetPassword(email: string): Promise<{ error: AuthError | null }> {
    try {
      const { error } = await this.client.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/auth/reset-password`
      });

      return {
        error: error ? this.transformAuthError(error) : null
      };
    } catch (error) {
      return {
        error: this.transformAuthError(error)
      };
    }
  }

  async updateUser(updates: {
    email?: string;
    password?: string;
    data?: Record<string, any>;
  }): Promise<{
    user: AuthUser | null;
    error: AuthError | null;
  }> {
    try {
      const { data, error } = await this.client.auth.updateUser(updates);

      return {
        user: data.user ? this.transformUser(data.user) : null,
        error: error ? this.transformAuthError(error) : null
      };
    } catch (error) {
      return {
        user: null,
        error: this.transformAuthError(error)
      };
    }
  }

  async getCurrentUser(): Promise<AuthUser | null> {
    try {
      const { data: { user }, error } = await this.client.auth.getUser();
      
      if (error) {
        console.warn('Failed to get current user:', error);
        return null;
      }
      
      return user ? this.transformUser(user) : null;
    } catch (error) {
      console.warn('Failed to get current user:', error);
      return null;
    }
  }

  async getCurrentSession() {
    try {
      const { data: { session }, error } = await this.client.auth.getSession();
      
      if (error) {
        console.warn('Failed to get current session:', error);
        return null;
      }
      
      return session;
    } catch (error) {
      console.warn('Failed to get current session:', error);
      return null;
    }
  }

  /**
   * Database operations with enhanced error handling
   */
  async query<T = any>(
    table: string,
    options: {
      select?: string;
      filter?: Record<string, any>;
      order?: { column: string; ascending?: boolean };
      range?: { from: number; to: number };
      single?: boolean;
    } = {}
  ): Promise<{ data: T | T[] | null; error: any }> {
    try {
      let query = this.client.from(table).select(options.select || '*');

      // Apply filters
      if (options.filter) {
        Object.entries(options.filter).forEach(([key, value]) => {
          if (Array.isArray(value)) {
            query = query.in(key, value);
          } else if (value !== null && value !== undefined) {
            query = query.eq(key, value);
          }
        });
      }

      // Apply ordering
      if (options.order) {
        query = query.order(options.order.column, { ascending: options.order.ascending ?? true });
      }

      // Apply range
      if (options.range) {
        query = query.range(options.range.from, options.range.to);
      }

      // Execute query
      if (options.single) {
        const { data, error } = await query.single();
        return { data: data as T, error };
      } else {
        const { data, error } = await query;
        return { data: data as T[], error };
      }
    } catch (error) {
      return { data: null, error };
    }
  }

  async insert<T = any>(
    table: string,
    data: any | any[],
    options: {
      returning?: string;
      onConflict?: string;
    } = {}
  ): Promise<{ data: T | T[] | null; error: any }> {
    try {
      let query = this.client.from(table).insert(data);

      if (options.returning) {
        query = query.select(options.returning);
      }

      if (options.onConflict) {
        query = query.onConflict(options.onConflict);
      }

      const { data: result, error } = await query;
      return { data: result as T | T[], error };
    } catch (error) {
      return { data: null, error };
    }
  }

  async update<T = any>(
    table: string,
    updates: any,
    filter: Record<string, any>,
    options: {
      returning?: string;
    } = {}
  ): Promise<{ data: T | T[] | null; error: any }> {
    try {
      let query = this.client.from(table).update(updates);

      // Apply filters
      Object.entries(filter).forEach(([key, value]) => {
        query = query.eq(key, value);
      });

      if (options.returning) {
        query = query.select(options.returning);
      }

      const { data, error } = await query;
      return { data: data as T | T[], error };
    } catch (error) {
      return { data: null, error };
    }
  }

  async delete(
    table: string,
    filter: Record<string, any>
  ): Promise<{ error: any }> {
    try {
      let query = this.client.from(table).delete();

      // Apply filters
      Object.entries(filter).forEach(([key, value]) => {
        query = query.eq(key, value);
      });

      const { error } = await query;
      return { error };
    } catch (error) {
      return { error };
    }
  }

  /**
   * Real-time subscriptions
   */
  subscribeToTable(
    table: string,
    callback: (payload: any) => void,
    options: {
      event?: 'INSERT' | 'UPDATE' | 'DELETE' | '*';
      filter?: string;
    } = {}
  ): string {
    const channelName = `${table}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const channel = this.client
      .channel(channelName)
      .on(
        'postgres_changes',
        {
          event: options.event || '*',
          schema: 'public',
          table,
          ...(options.filter && { filter: options.filter })
        },
        callback
      )
      .subscribe();

    this.channels.set(channelName, channel as any);
    return channelName;
  }

  unsubscribeFromChannel(channelName: string): void {
    const channel = this.channels.get(channelName);
    if (channel) {
      this.client.removeChannel(channel as any);
      this.channels.delete(channelName);
    }
  }

  /**
   * File storage operations
   */
  async uploadFile(
    bucket: string,
    path: string,
    file: File | Buffer,
    options: {
      contentType?: string;
      metadata?: Record<string, any>;
      upsert?: boolean;
    } = {}
  ): Promise<{ data: any; error: any }> {
    try {
      const { data, error } = await this.client.storage
        .from(bucket)
        .upload(path, file, {
          contentType: options.contentType,
          metadata: options.metadata,
          upsert: options.upsert
        });

      return { data, error };
    } catch (error) {
      return { data: null, error };
    }
  }

  async downloadFile(
    bucket: string,
    path: string
  ): Promise<{ data: Blob | null; error: any }> {
    try {
      const { data, error } = await this.client.storage
        .from(bucket)
        .download(path);

      return { data, error };
    } catch (error) {
      return { data: null, error };
    }
  }

  async deleteFile(
    bucket: string,
    paths: string[]
  ): Promise<{ data: any; error: any }> {
    try {
      const { data, error } = await this.client.storage
        .from(bucket)
        .remove(paths);

      return { data, error };
    } catch (error) {
      return { data: null, error };
    }
  }

  getPublicUrl(bucket: string, path: string): string {
    const { data } = this.client.storage
      .from(bucket)
      .getPublicUrl(path);
    
    return data.publicUrl;
  }

  /**
   * Edge Functions
   */
  async invokeFunction<T = any>(
    functionName: string,
    payload?: any,
    options: {
      headers?: Record<string, string>;
      method?: 'POST' | 'GET' | 'PUT' | 'DELETE';
    } = {}
  ): Promise<{ data: T | null; error: any }> {
    try {
      const { data, error } = await this.client.functions.invoke(functionName, {
        body: payload,
        headers: options.headers,
        method: options.method
      });

      return { data: data as T, error };
    } catch (error) {
      return { data: null, error };
    }
  }

  /**
   * Utility methods
   */
  async testConnection(): Promise<{ success: boolean; message: string }> {
    try {
      const { data, error } = await this.client
        .from('profiles')
        .select('id')
        .limit(1);

      if (error && error.code !== 'PGRST116') { // PGRST116 is "table not found" which is fine for testing
        return {
          success: false,
          message: `Connection failed: ${error.message}`
        };
      }

      return {
        success: true,
        message: 'Successfully connected to Supabase'
      };
    } catch (error) {
      return {
        success: false,
        message: `Connection failed: ${(error as Error).message}`
      };
    }
  }

  /**
   * Auth state management
   */
  onAuthStateChange(callback: (user: AuthUser | null) => void): () => void {
    this.authListeners.push(callback);
    
    return () => {
      const index = this.authListeners.indexOf(callback);
      if (index > -1) {
        this.authListeners.splice(index, 1);
      }
    };
  }

  /**
   * Private helper methods
   */
  private setupAuthListener(): void {
    this.client.auth.onAuthStateChange((event, session) => {
      const user = session?.user ? this.transformUser(session.user) : null;
      this.authListeners.forEach(callback => callback(user));
    });
  }

  private transformUser(user: User): AuthUser {
    return {
      id: user.id,
      email: user.email || '',
      emailConfirmed: user.email_confirmed_at !== null,
      phone: user.phone,
      confirmedAt: user.confirmed_at,
      lastSignInAt: user.last_sign_in_at,
      appMetadata: user.app_metadata,
      userMetadata: user.user_metadata,
      identities: user.identities?.map(identity => ({
        id: identity.id,
        userId: identity.user_id,
        identityData: identity.identity_data,
        provider: identity.provider,
        createdAt: identity.created_at,
        updatedAt: identity.updated_at
      }))
    };
  }

  private transformAuthError(error: any): AuthError {
    return {
      message: error?.message || 'An unknown error occurred',
      status: error?.status,
      code: error?.code
    };
  }

  private clearAllChannels(): void {
    this.channels.forEach((channel, name) => {
      this.client.removeChannel(channel as any);
    });
    this.channels.clear();
  }
}

// Export singleton instance
export const supabaseService = new SupabaseService();

// Export the client directly for backward compatibility
export const supabase = supabaseService.getClient();

// Export class for custom configurations
export { SupabaseService };

// Export utility types
export type Tables<T extends keyof Database['public']['Tables']> = Database['public']['Tables'][T]['Row'];
export type Enums<T extends keyof Database['public']['Enums']> = Database['public']['Enums'][T];

// Common table type exports for convenience
export type VocabularyItem = Tables<'vocabulary_items'>;
export type UserProfile = Tables<'profiles'>;
export type SearchSession = Tables<'search_sessions'>;
export type QuizResult = Tables<'quiz_results'>;
export type SharedList = Tables<'shared_lists'>;
export type UserPreferences = Tables<'user_preferences'>;

// Insert and update types
export type VocabularyItemInsert = Database['public']['Tables']['vocabulary_items']['Insert'];
export type VocabularyItemUpdate = Database['public']['Tables']['vocabulary_items']['Update'];
export type UserProfileInsert = Database['public']['Tables']['profiles']['Insert'];
export type UserProfileUpdate = Database['public']['Tables']['profiles']['Update'];}