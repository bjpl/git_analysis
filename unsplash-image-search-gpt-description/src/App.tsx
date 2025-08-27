import React, { Suspense, lazy, useState } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { clsx } from 'clsx';

// Simple Navigation Component
import Navigation from './components/Navigation/Navigation';

// App initialization and setup
import { useAppInitialization } from './hooks/useAppInitialization';
import { FirstTimeSetup } from './components/Settings/FirstTimeSetup';
import { ErrorBoundary } from './components/Shared/ErrorBoundary/ErrorBoundary';

// Lazy load page components for better performance
const HomePage = lazy(() => import('./pages/HomePage'));
const SearchPage = lazy(() => import('./pages/SearchPage'));
const VocabularyPage = lazy(() => import('./pages/VocabularyPage'));
const QuizPage = lazy(() => import('./pages/QuizPage'));
const AboutPage = lazy(() => import('./pages/AboutPage'));
const NotFoundPage = lazy(() => import('./pages/NotFoundPage'));

const SettingsPage = lazy(() => import('./pages/SettingsPage'));

// Future page components (commented out until created)
// const AnalyticsPage = lazy(() => import('./pages/AnalyticsPage'));
// const ProfilePage = lazy(() => import('./pages/ProfilePage'));
// const LoginPage = lazy(() => import('./pages/auth/LoginPage'));
// const SignupPage = lazy(() => import('./pages/auth/SignupPage'));

// Loading fallback component
const PageLoader: React.FC = () => (
  <div className="min-h-screen flex items-center justify-center">
    <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
  </div>
);

/**
 * App Layout Component - Handles main application layout structure
 */
function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Navigation */}
      <Navigation />
      
      {/* Main Content */}
      <main className="flex-1">
        {children}
      </main>
    </div>
  );
}

/**
 * Main App Component with Complete Routing Structure
 * Features:
 * - Complete routing for all VocabLens pages
 * - Protected routes with optional authentication
 * - Nested routing support for vocabulary management
 * - 404 error handling with helpful navigation
 * - Layout management with responsive design
 * - Lazy loading for optimal performance
 * - First-time setup modal for API configuration
 * - Runtime API key management
 */
function App() {
  const {
    isLoading,
    showFirstTimeSetup,
    completeFirstTimeSetup,
    dismissFirstTimeSetup,
    error,
    retryInitialization
  } = useAppInitialization();

  // Show loading screen during initialization
  if (isLoading) {
    return <PageLoader />;
  }

  // Show error screen if initialization failed
  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            Initialization Failed
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            {error}
          </p>
          <button
            onClick={retryInitialization}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <AppLayout>
        <Suspense fallback={<PageLoader />}>
          <Routes>
            {/* Main Routes */}
            <Route path="/" element={<HomePage />} />
            <Route path="/home" element={<Navigate to="/" replace />} />
            <Route path="/search" element={<SearchPage />} />
            <Route path="/about" element={<AboutPage />} />
            
            {/* Vocabulary Routes with Nested Support */}
            <Route path="/vocabulary/*" element={<VocabularyPage />} />
            
            {/* Quiz Routes */}
            <Route path="/quiz" element={<QuizPage />} />
            
            {/* Settings Route */}
            <Route path="/settings" element={<SettingsPage />} />
            
            {/* Future Protected Routes (uncomment when components are ready) */}
            {/* 
            <Route 
              path="/analytics" 
              element={
                <ProtectedRoute>
                  <AnalyticsPage />
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/profile" 
              element={
                <ProtectedRoute>
                  <ProfilePage />
                </ProtectedRoute>
              } 
            />
            */}
            
            {/* Authentication Routes (uncomment when components are ready) */}
            {/* 
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignupPage />} />
            */}
            
            {/* 404 Catch-all Route */}
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </Suspense>
        
        {/* First Time Setup Modal */}
        <FirstTimeSetup
          isOpen={showFirstTimeSetup}
          onClose={dismissFirstTimeSetup}
          onComplete={completeFirstTimeSetup}
        />
      </AppLayout>
    </ErrorBoundary>
  );
}

export default App;