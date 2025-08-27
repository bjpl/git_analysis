import React from 'react';
import { AuthProvider as AuthContextProvider } from '@/contexts/AuthContext';
import { ErrorBoundary } from '../Shared/ErrorBoundary/ErrorBoundary';
import { LoadingSpinner } from '../Shared/LoadingStates/LoadingSkeleton';

interface AuthProviderProps {
  children: React.ReactNode;
}

/**
 * AuthProvider wrapper component that includes error boundary
 * and loading states for authentication initialization
 */
export function AuthProvider({ children }: AuthProviderProps) {
  return (
    <ErrorBoundary
      fallback={(
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              Authentication Error
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              There was a problem initializing the authentication system.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              Reload Page
            </button>
          </div>
        </div>
      )}
      onError={(error) => {
        console.error('Auth Provider Error:', error);
        // In production, send to error tracking service
      }}
    >
      <AuthContextProvider>
        <React.Suspense
          fallback={(
            <div className="min-h-screen flex items-center justify-center">
              <div className="text-center">
                <LoadingSpinner size="lg" />
                <p className="mt-4 text-gray-600 dark:text-gray-400">
                  Initializing authentication...
                </p>
              </div>
            </div>
          )}
        >
          {children}
        </React.Suspense>
      </AuthContextProvider>
    </ErrorBoundary>
  );
}