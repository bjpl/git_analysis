import React from 'react';
import { useAuthContext } from '@/contexts/AuthContext';
import { LoadingSpinner } from '../Shared/LoadingStates/LoadingSkeleton';
import { LoginForm } from './LoginForm';
import { Button } from '../Shared/Button/Button';
import { cn } from '@/utils/cn';

interface ProtectedRouteProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  requireAuth?: boolean;
  className?: string;
}

interface AuthPromptProps {
  onSignIn?: () => void;
}

/**
 * Authentication prompt component shown to unauthenticated users
 */
function AuthPrompt({ onSignIn }: AuthPromptProps) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-primary-100 dark:bg-primary-900">
            <svg 
              className="h-6 w-6 text-primary-600 dark:text-primary-400" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" 
              />
            </svg>
          </div>
          
          <h2 className="mt-6 text-3xl font-bold text-gray-900 dark:text-white">
            Authentication Required
          </h2>
          
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Please sign in to access this content. Your learning progress and vocabulary will be saved securely.
          </p>
        </div>
        
        <div className="mt-8 space-y-6">
          <LoginForm 
            onSuccess={() => {
              onSignIn?.();
              // Page will automatically update when auth state changes
            }}
            className="w-full"
          />
        </div>
      </div>
    </div>
  );
}

/**
 * ProtectedRoute component that wraps content requiring authentication
 * Shows loading spinner during auth check and login form for unauthenticated users
 */
export function ProtectedRoute({ 
  children, 
  fallback, 
  requireAuth = true, 
  className 
}: ProtectedRouteProps) {
  const { user, isAuthenticated, isLoading } = useAuthContext();

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div className={cn('min-h-screen flex items-center justify-center', className)}>
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-gray-600 dark:text-gray-400">
            Checking authentication...
          </p>
        </div>
      </div>
    );
  }

  // If authentication is not required, always show children
  if (!requireAuth) {
    return <div className={className}>{children}</div>;
  }

  // If user is authenticated, show the protected content
  if (isAuthenticated && user) {
    return <div className={className}>{children}</div>;
  }

  // If user is not authenticated, show fallback or default auth prompt
  if (fallback) {
    return <div className={className}>{fallback}</div>;
  }

  return <AuthPrompt />;
}

/**
 * Higher-order component version of ProtectedRoute
 * Usage: const ProtectedComponent = withAuth(MyComponent);
 */
export function withAuth<P extends object>(
  Component: React.ComponentType<P>,
  options: { requireAuth?: boolean; fallback?: React.ReactNode } = {}
) {
  const { requireAuth = true, fallback } = options;
  
  return function ProtectedComponent(props: P) {
    return (
      <ProtectedRoute requireAuth={requireAuth} fallback={fallback}>
        <Component {...props} />
      </ProtectedRoute>
    );
  };
}

/**
 * Hook to check if current route should be protected
 * Useful for conditional rendering based on auth requirements
 */
export function useProtectedRoute(requireAuth: boolean = true) {
  const { isAuthenticated, isLoading, user } = useAuthContext();
  
  return {
    isProtected: requireAuth,
    isAuthenticated,
    isLoading,
    user,
    shouldShowAuth: requireAuth && !isAuthenticated && !isLoading,
    shouldShowContent: !requireAuth || (isAuthenticated && user),
    shouldShowLoading: isLoading,
  };
}