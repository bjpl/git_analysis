import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { User, AppError } from '@/types';
import { useSupabase } from '@/hooks/useSupabase';
import type { AuthError, Session, User as SupabaseUser } from '@supabase/supabase-js';

interface AuthContextType {
  user: User | null;
  session: Session | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: AppError | null;
  signIn: (email: string, password: string) => Promise<{ error: AppError | null }>;
  signUp: (email: string, password: string, username?: string) => Promise<{ error: AppError | null }>;
  signInWithOAuth: (provider: 'google' | 'github' | 'apple') => Promise<{ error: AppError | null }>;
  signOut: () => Promise<{ error: AppError | null }>;
  resetPassword: (email: string) => Promise<{ error: AppError | null }>;
  updateProfile: (updates: Partial<User>) => Promise<{ error: AppError | null }>;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

interface AuthProviderProps {
  children: ReactNode;
}

/**
 * Transforms Supabase user to app user format
 */
function transformUser(supabaseUser: SupabaseUser): User {
  return {
    id: supabaseUser.id,
    email: supabaseUser.email || '',
    username: supabaseUser.user_metadata?.username || supabaseUser.user_metadata?.name,
    avatar_url: supabaseUser.user_metadata?.avatar_url,
    created_at: supabaseUser.created_at || new Date().toISOString(),
    preferences: {
      language: supabaseUser.user_metadata?.language || 'en',
      description_style: supabaseUser.user_metadata?.description_style || 'casual',
      quiz_difficulty: supabaseUser.user_metadata?.quiz_difficulty || 3,
      notification_enabled: supabaseUser.user_metadata?.notification_enabled ?? true,
    },
  };
}

/**
 * Transforms Supabase auth error to app error format
 */
function transformAuthError(authError: AuthError): AppError {
  return {
    code: authError.status?.toString() || 'AUTH_ERROR',
    message: authError.message,
    details: authError,
    timestamp: new Date().toISOString(),
    recoverable: true,
  };
}

/**
 * AuthProvider component that manages authentication state and operations
 * Integrates with Supabase Auth and provides context to child components
 */
export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<AppError | null>(null);
  const supabase = useSupabase();

  const clearError = () => setError(null);

  // Initialize auth state and set up auth listener
  useEffect(() => {
    let mounted = true;

    const initializeAuth = async () => {
      try {
        const { data: { session: initialSession }, error: sessionError } = 
          await supabase.auth.getSession();

        if (sessionError) {
          console.error('Error getting session:', sessionError);
          if (mounted) {
            setError(transformAuthError(sessionError));
          }
          return;
        }

        if (mounted) {
          setSession(initialSession);
          setUser(initialSession?.user ? transformUser(initialSession.user) : null);
        }
      } catch (err) {
        console.error('Error initializing auth:', err);
        if (mounted) {
          setError({
            code: 'INIT_ERROR',
            message: 'Failed to initialize authentication',
            details: err,
            timestamp: new Date().toISOString(),
            recoverable: true,
          });
        }
      } finally {
        if (mounted) {
          setIsLoading(false);
        }
      }
    };

    initializeAuth();

    // Listen for auth state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (event, session) => {
        console.log('Auth state change:', event, session);
        
        if (!mounted) return;

        setSession(session);
        setUser(session?.user ? transformUser(session.user) : null);
        
        // Clear errors on successful auth state changes
        if (event === 'SIGNED_IN' || event === 'SIGNED_OUT') {
          setError(null);
        }
      }
    );

    return () => {
      mounted = false;
      subscription.unsubscribe();
    };
  }, [supabase]);

  const signIn = async (email: string, password: string) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const { error: authError } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (authError) {
        const appError = transformAuthError(authError);
        setError(appError);
        return { error: appError };
      }

      return { error: null };
    } catch (err) {
      const appError: AppError = {
        code: 'SIGNIN_ERROR',
        message: 'Failed to sign in',
        details: err,
        timestamp: new Date().toISOString(),
        recoverable: true,
      };
      setError(appError);
      return { error: appError };
    } finally {
      setIsLoading(false);
    }
  };

  const signUp = async (email: string, password: string, username?: string) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const { error: authError } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            username,
            language: 'en',
            description_style: 'casual',
            quiz_difficulty: 3,
            notification_enabled: true,
          },
        },
      });

      if (authError) {
        const appError = transformAuthError(authError);
        setError(appError);
        return { error: appError };
      }

      return { error: null };
    } catch (err) {
      const appError: AppError = {
        code: 'SIGNUP_ERROR',
        message: 'Failed to sign up',
        details: err,
        timestamp: new Date().toISOString(),
        recoverable: true,
      };
      setError(appError);
      return { error: appError };
    } finally {
      setIsLoading(false);
    }
  };

  const signInWithOAuth = async (provider: 'google' | 'github' | 'apple') => {
    try {
      setIsLoading(true);
      setError(null);
      
      const { error: authError } = await supabase.auth.signInWithOAuth({
        provider,
        options: {
          redirectTo: `${window.location.origin}/auth/callback`,
        },
      });

      if (authError) {
        const appError = transformAuthError(authError);
        setError(appError);
        return { error: appError };
      }

      return { error: null };
    } catch (err) {
      const appError: AppError = {
        code: 'OAUTH_ERROR',
        message: `Failed to sign in with ${provider}`,
        details: err,
        timestamp: new Date().toISOString(),
        recoverable: true,
      };
      setError(appError);
      return { error: appError };
    } finally {
      setIsLoading(false);
    }
  };

  const signOut = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const { error: authError } = await supabase.auth.signOut();

      if (authError) {
        const appError = transformAuthError(authError);
        setError(appError);
        return { error: appError };
      }

      return { error: null };
    } catch (err) {
      const appError: AppError = {
        code: 'SIGNOUT_ERROR',
        message: 'Failed to sign out',
        details: err,
        timestamp: new Date().toISOString(),
        recoverable: true,
      };
      setError(appError);
      return { error: appError };
    } finally {
      setIsLoading(false);
    }
  };

  const resetPassword = async (email: string) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const { error: authError } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/auth/reset-password`,
      });

      if (authError) {
        const appError = transformAuthError(authError);
        setError(appError);
        return { error: appError };
      }

      return { error: null };
    } catch (err) {
      const appError: AppError = {
        code: 'RESET_ERROR',
        message: 'Failed to send reset email',
        details: err,
        timestamp: new Date().toISOString(),
        recoverable: true,
      };
      setError(appError);
      return { error: appError };
    } finally {
      setIsLoading(false);
    }
  };

  const updateProfile = async (updates: Partial<User>) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const { error: authError } = await supabase.auth.updateUser({
        data: {
          username: updates.username,
          avatar_url: updates.avatar_url,
          language: updates.preferences?.language,
          description_style: updates.preferences?.description_style,
          quiz_difficulty: updates.preferences?.quiz_difficulty,
          notification_enabled: updates.preferences?.notification_enabled,
        },
      });

      if (authError) {
        const appError = transformAuthError(authError);
        setError(appError);
        return { error: appError };
      }

      return { error: null };
    } catch (err) {
      const appError: AppError = {
        code: 'UPDATE_ERROR',
        message: 'Failed to update profile',
        details: err,
        timestamp: new Date().toISOString(),
        recoverable: true,
      };
      setError(appError);
      return { error: appError };
    } finally {
      setIsLoading(false);
    }
  };

  const contextValue: AuthContextType = {
    user,
    session,
    isAuthenticated: !!user,
    isLoading,
    error,
    signIn,
    signUp,
    signInWithOAuth,
    signOut,
    resetPassword,
    updateProfile,
    clearError,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

/**
 * Hook to access auth context
 * Throws error if used outside AuthProvider
 */
export function useAuthContext(): AuthContextType {
  const context = useContext(AuthContext);
  
  if (!context) {
    throw new Error('useAuthContext must be used within an AuthProvider');
  }
  
  return context;
}