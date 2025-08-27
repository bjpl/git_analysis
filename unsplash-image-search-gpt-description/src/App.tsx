import React, { Suspense, lazy, useState } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { clsx } from 'clsx';

// Simple Navigation Component
import Navigation from './components/Navigation/Navigation';

// Lazy load page components for better performance
const HomePage = lazy(() => import('./pages/HomePage'));
const SearchPage = lazy(() => import('./pages/SearchPage'));
const VocabularyPage = lazy(() => import('./pages/VocabularyPage'));
const QuizPage = lazy(() => import('./pages/QuizPage'));
const AboutPage = lazy(() => import('./pages/AboutPage'));
const NotFoundPage = lazy(() => import('./pages/NotFoundPage'));

// Future page components (commented out until created)
// const AnalyticsPage = lazy(() => import('./pages/AnalyticsPage'));
// const ProfilePage = lazy(() => import('./pages/ProfilePage'));
// const SettingsPage = lazy(() => import('./pages/SettingsPage'));
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
 */
function App() {
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
            
            <Route 
              path="/settings" 
              element={
                <ProtectedRoute>
                  <SettingsPage />
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
      </AppLayout>
    </ErrorBoundary>
  );
}

export default App;