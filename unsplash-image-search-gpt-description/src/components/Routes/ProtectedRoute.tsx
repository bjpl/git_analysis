import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { LoadingSkeleton } from '@/components/Shared/LoadingStates/LoadingSkeleton';
import { EmptyState } from '@/components/Shared/EmptyState/EmptyState';
import { Button } from '@/components/Shared/Button/Button';
import {
  LockClosedIcon,
  UserIcon,
  ArrowRightIcon
} from '@heroicons/react/24/outline';
import { Link } from 'react-router-dom';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireAuth?: boolean;
  requireRole?: string[];
  fallbackPath?: string;
  showLoginPrompt?: boolean;
}

/**
 * Protected Route Component - Handles authentication and authorization
 * Features:
 * - Authentication requirement checking
 * - Role-based access control
 * - Redirect preservation for post-login navigation
 * - Loading states during auth check
 * - Friendly login prompts
 * - Guest access modes
 */
export function ProtectedRoute({
  children,
  requireAuth = true,
  requireRole = [],
  fallbackPath = '/login',
  showLoginPrompt = true
}: ProtectedRouteProps) {
  const { user, isAuthenticated, isLoading, hasRole } = useAuth();
  const location = useLocation();

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="max-w-md w-full space-y-4">
          <div className="text-center">
            <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <LoadingSkeleton className="w-6 h-6 rounded-full" />
            </div>
            <LoadingSkeleton className="h-6 w-48 mx-auto mb-2" />
            <LoadingSkeleton className="h-4 w-32 mx-auto" />
          </div>
        </div>
      </div>
    );
  }

  // Check authentication requirement
  if (requireAuth && !isAuthenticated) {
    // If we should show a login prompt instead of redirecting
    if (showLoginPrompt) {
      return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
          <div className="max-w-md w-full">
            <EmptyState
              icon={LockClosedIcon}
              title="Authentication Required"
              description="You need to sign in to access this page. Your progress will be saved and synced across devices."
              className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-8"
            >
              <div className="flex flex-col sm:flex-row gap-3 justify-center items-center mt-6">
                <Button
                  as={Link}
                  to="/login"
                  state={{ from: location }}
                  variant="primary"
                  className="group"
                >
                  Sign In
                  <ArrowRightIcon className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </Button>
                
                <Button
                  as={Link}
                  to="/signup"
                  state={{ from: location }}
                  variant="outline"
                >
                  Create Account
                </Button>
              </div>
              
              <div className="mt-6 text-center">
                <p className="text-sm text-gray-600 dark:text-gray-300 mb-2">
                  Don't want to create an account?
                </p>
                <Button
                  as={Link}
                  to="/"
                  variant="ghost"
                  size="sm"
                >
                  Continue as Guest
                </Button>
              </div>
            </EmptyState>
          </div>
        </div>
      );
    }
    
    // Redirect to login with return path
    return (
      <Navigate 
        to={fallbackPath} 
        state={{ from: location }} 
        replace 
      />
    );
  }

  // Check role requirements
  if (requireAuth && isAuthenticated && requireRole.length > 0) {
    const hasRequiredRole = requireRole.some(role => hasRole?.(role));
    
    if (!hasRequiredRole) {
      return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
          <div className="max-w-md w-full">
            <EmptyState
              icon={UserIcon}
              title="Access Restricted"
              description="You don't have the required permissions to access this page."
              className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-8"
            >
              <div className="flex flex-col gap-3 justify-center items-center mt-6">
                <Button
                  as={Link}
                  to="/"
                  variant="primary"
                >
                  Go to Home
                </Button>
                
                <Button
                  as={Link}
                  to="/profile"
                  variant="outline"
                  size="sm"
                >
                  View Your Profile
                </Button>
              </div>
            </EmptyState>
          </div>
        </div>
      );
    }
  }

  // User passes all checks, render the protected content
  return <>{children}</>;
}

/**
 * Higher-order component for protecting routes
 * Usage: const ProtectedComponent = withAuthProtection(YourComponent, options)
 */
export function withAuthProtection<T extends Record<string, any>>(
  Component: React.ComponentType<T>,
  options?: Omit<ProtectedRouteProps, 'children'>
) {
  return function ProtectedComponent(props: T) {
    return (
      <ProtectedRoute {...options}>
        <Component {...props} />
      </ProtectedRoute>
    );
  };
}

/**
 * Hook for checking authentication status within components
 * Useful for conditional rendering based on auth state
 */
export function useProtectedRoute(requireAuth = true) {
  const { isAuthenticated, isLoading, user } = useAuth();
  
  const canAccess = !requireAuth || isAuthenticated;
  const shouldShowLogin = requireAuth && !isAuthenticated && !isLoading;
  
  return {
    canAccess,
    shouldShowLogin,
    isLoading,
    isAuthenticated,
    user
  };
}

export default ProtectedRoute;