import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

// Context Providers
import { ThemeProvider } from '@/contexts/ThemeContext';
import { NotificationProvider } from '@/components/Shared/Notification/NotificationSystem';

// Layout Components
import { AppShell } from '@/components/Layout/AppShell';
import { ErrorBoundary } from '@/components/Shared/ErrorHandling/ErrorComponents';
import { SkipLink } from '@/components/Shared/Accessibility/AccessibilityComponents';

// UI Components
import { Button } from '@/components/Shared/Button/Button';
import { Card } from '@/components/Shared/Card/Card';
import { ThemeToggle } from '@/contexts/ThemeContext';
import { useNotificationHelpers } from '@/components/Shared/Notification/NotificationSystem';

// Icons
import { 
  MagnifyingGlassIcon,
  SparklesIcon,
  BookOpenIcon,
  RocketLaunchIcon
} from '@heroicons/react/24/outline';

// Create a stable query client instance
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      refetchOnWindowFocus: false,
    },
  },
});

/**
 * Welcome Page Component with enhanced UI/UX
 */
function WelcomePage() {
  const { success, info } = useNotificationHelpers();
  const [isGettingStarted, setIsGettingStarted] = useState(false);

  const handleGetStarted = async () => {
    setIsGettingStarted(true);
    
    // Simulate getting started process
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    success("Welcome!", "Let's start learning vocabulary together!", {
      duration: 4000,
      action: {
        label: 'Start Tutorial',
        onClick: () => info('Tutorial', 'Tutorial feature coming soon!')
      }
    });
    
    setIsGettingStarted(false);
  };

  const features = [
    {
      icon: MagnifyingGlassIcon,
      title: 'Search Images',
      description: 'Find beautiful, high-quality images from Unsplash to enhance your learning experience.',
      color: 'text-blue-500',
      bgColor: 'bg-blue-50 dark:bg-blue-950'
    },
    {
      icon: SparklesIcon,
      title: 'AI Descriptions',
      description: 'Generate detailed, educational descriptions with highlighted vocabulary using advanced AI.',
      color: 'text-purple-500',
      bgColor: 'bg-purple-50 dark:bg-purple-950'
    },
    {
      icon: BookOpenIcon,
      title: 'Learn Vocabulary',
      description: 'Build and retain vocabulary with our intelligent spaced repetition system.',
      color: 'text-green-500',
      bgColor: 'bg-green-50 dark:bg-green-950'
    }
  ];

  return (
    <div className="min-h-screen bg-background">
      <main 
        id="main-content"
        className="container mx-auto px-4 py-8 sm:py-12 lg:py-16"
        role="main"
        aria-label="VocabLens welcome page"
      >
        {/* Hero Section */}
        <section className="text-center mb-16 animate-fade-in">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-center justify-center gap-3 mb-6">
              <div className="h-12 w-12 bg-primary rounded-lg flex items-center justify-center">
                <RocketLaunchIcon className="h-7 w-7 text-primary-foreground" aria-hidden="true" />
              </div>
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-foreground">
                VocabLens
              </h1>
            </div>
            
            <p className="text-xl sm:text-2xl text-muted-foreground mb-8 max-w-2xl mx-auto leading-relaxed">
              Transform your vocabulary learning through 
              <span className="vocabulary-highlight mx-2">beautiful images</span> 
              and AI-powered descriptions
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Button 
                size="lg"
                onClick={handleGetStarted}
                loading={isGettingStarted}
                className="min-w-40 text-base"
                aria-describedby="get-started-description"
              >
                Get Started
              </Button>
              
              <Button 
                variant="outline" 
                size="lg"
                className="text-base"
                onClick={() => info('Demo', 'Interactive demo coming soon!')}
              >
                Try Demo
              </Button>
            </div>
            
            <p 
              id="get-started-description" 
              className="text-sm text-muted-foreground mt-4"
            >
              Start learning vocabulary in under 30 seconds
            </p>
          </div>
        </section>

        {/* Features Section */}
        <section 
          className="mb-16"
          aria-labelledby="features-heading"
        >
          <h2 
            id="features-heading"
            className="text-3xl font-bold text-center text-foreground mb-12"
          >
            Why Choose VocabLens?
          </h2>
          
          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {features.map((feature, index) => (
              <Card 
                key={feature.title}
                className={`p-6 text-center border-0 shadow-md hover:shadow-lg transition-all duration-300 animate-slide-up`}
                style={{ animationDelay: `${index * 150}ms` }}
              >
                <div className={`w-16 h-16 ${feature.bgColor} rounded-2xl flex items-center justify-center mx-auto mb-4`}>
                  <feature.icon 
                    className={`w-8 h-8 ${feature.color}`} 
                    aria-hidden="true"
                  />
                </div>
                
                <h3 className="text-xl font-semibold text-foreground mb-3">
                  {feature.title}
                </h3>
                
                <p className="text-muted-foreground leading-relaxed">
                  {feature.description}
                </p>
              </Card>
            ))}
          </div>
        </section>

        {/* Benefits Section */}
        <section 
          className="bg-muted/30 rounded-2xl p-8 sm:p-12 text-center"
          aria-labelledby="benefits-heading"
        >
          <h2 
            id="benefits-heading"
            className="text-3xl font-bold text-foreground mb-6"
          >
            Learn Smarter, Not Harder
          </h2>
          
          <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
            Our research-backed approach combines visual learning with spaced repetition 
            to help you retain vocabulary 3x faster than traditional methods.
          </p>
          
          <div className="grid sm:grid-cols-3 gap-6 max-w-3xl mx-auto">
            <div className="bg-background rounded-lg p-6 shadow-sm">
              <div className="text-2xl font-bold text-primary mb-2">85%</div>
              <div className="text-sm text-muted-foreground">Retention Rate</div>
            </div>
            <div className="bg-background rounded-lg p-6 shadow-sm">
              <div className="text-2xl font-bold text-success mb-2">3x</div>
              <div className="text-sm text-muted-foreground">Faster Learning</div>
            </div>
            <div className="bg-background rounded-lg p-6 shadow-sm">
              <div className="text-2xl font-bold text-info mb-2">1M+</div>
              <div className="text-sm text-muted-foreground">Images Available</div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

/**
 * Enhanced App Component with comprehensive UI/UX architecture
 */
function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider defaultTheme="system">
        <NotificationProvider 
          position="top-right"
          maxNotifications={5}
        >
          <ErrorBoundary
            onError={(error, errorInfo) => {
              console.error('App Error:', error, errorInfo);
              // Report to error tracking service in production
            }}
          >
            <Router>
              {/* Accessibility Skip Links */}
              <SkipLink href="#main-content">
                Skip to main content
              </SkipLink>
              
              <AppShell className="min-h-screen">
                <Routes>
                  <Route path="/" element={<WelcomePage />} />
                  {/* Add more routes as needed */}
                </Routes>
                
                {/* Theme Toggle - Fixed Position */}
                <div className="fixed bottom-6 right-6 z-40 no-print">
                  <ThemeToggle size="md" className="shadow-lg" />
                </div>
              </AppShell>
            </Router>
          </ErrorBoundary>
          
          {/* React Query DevTools (development only) */}
          {process.env.NODE_ENV === 'development' && (
            <ReactQueryDevtools initialIsOpen={false} />
          )}
        </NotificationProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;