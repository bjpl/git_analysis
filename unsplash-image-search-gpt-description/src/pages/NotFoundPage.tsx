import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { cn } from '@/utils/cn';
import { Button } from '@/components/Shared/Button/Button';
import {
  ExclamationTriangleIcon,
  HomeIcon,
  ArrowLeftIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline';

/**
 * 404 Not Found Page - Friendly error page with navigation options
 * Features:
 * - Helpful error message with suggestions
 * - Navigation options to return to main sections
 * - Search suggestions for common pages
 * - Breadcrumb navigation
 * - Accessible design with proper focus management
 */
export function NotFoundPage() {
  const navigate = useNavigate();

  const handleGoBack = () => {
    // Check if there's history to go back to
    if (window.history.length > 1) {
      navigate(-1);
    } else {
      navigate('/');
    }
  };

  const popularPages = [
    {
      name: 'Search Images',
      href: '/search',
      description: 'Find beautiful images for vocabulary learning',
      icon: MagnifyingGlassIcon
    },
    {
      name: 'My Vocabulary',
      href: '/vocabulary',
      description: 'Manage your Spanish vocabulary collection',
      icon: MagnifyingGlassIcon // Replace with appropriate icon
    },
    {
      name: 'Take a Quiz',
      href: '/quiz',
      description: 'Practice with spaced repetition quizzes',
      icon: MagnifyingGlassIcon // Replace with appropriate icon
    },
    {
      name: 'About VocabLens',
      href: '/about',
      description: 'Learn more about our learning platform',
      icon: MagnifyingGlassIcon // Replace with appropriate icon
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col">
      {/* Main Content */}
      <div className="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8 py-16">
        <div className="max-w-2xl w-full text-center">
          {/* Error Icon and Code */}
          <div className="mb-8">
            <div className="w-24 h-24 bg-red-100 dark:bg-red-900/20 rounded-full flex items-center justify-center mx-auto mb-6">
              <ExclamationTriangleIcon className="w-12 h-12 text-red-600 dark:text-red-400" />
            </div>
            
            <h1 className="text-6xl font-bold text-gray-900 dark:text-white mb-4">
              404
            </h1>
            
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
              Page Not Found
            </h2>
            
            <p className="text-lg text-gray-600 dark:text-gray-300 mb-8 leading-relaxed">
              Sorry, we couldn't find the page you're looking for. It might have been moved, 
              deleted, or you might have typed the URL incorrectly.
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
            <Button
              variant="primary"
              size="lg"
              onClick={handleGoBack}
              className="group flex items-center gap-2"
            >
              <ArrowLeftIcon className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
              Go Back
            </Button>
            
            <Button
              as={Link}
              to="/"
              variant="outline"
              size="lg"
              className="flex items-center gap-2"
            >
              <HomeIcon className="w-5 h-5" />
              Home Page
            </Button>
          </div>

          {/* Helpful Links */}
          <div className="text-left">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-6 text-center">
              Or try one of these popular pages:
            </h3>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {popularPages.map((page, index) => (
                <Link
                  key={index}
                  to={page.href}
                  className={cn(
                    'group bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700',
                    'p-4 hover:shadow-md hover:scale-[1.02] transition-all duration-200',
                    'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900'
                  )}
                >
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 mt-1">
                      <page.icon className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium text-gray-900 dark:text-white group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                        {page.name}
                      </h4>
                      <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                        {page.description}
                      </p>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </div>

          {/* Additional Help */}
          <div className="mt-12 pt-8 border-t border-gray-200 dark:border-gray-700">
            <p className="text-sm text-gray-600 dark:text-gray-300 mb-4">
              Still having trouble finding what you're looking for?
            </p>
            
            <div className="flex flex-col sm:flex-row gap-3 justify-center items-center">
              <Button
                as={Link}
                to="/search"
                variant="ghost"
                size="sm"
                className="flex items-center gap-2"
              >
                <MagnifyingGlassIcon className="w-4 h-4" />
                Search Images
              </Button>
              
              <Button
                as={Link}
                to="/about"
                variant="ghost"
                size="sm"
              >
                Learn About VocabLens
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Footer Note */}
      <div className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <p className="text-sm text-gray-600 dark:text-gray-300">
              Error code: 404 | Page not found
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default NotFoundPage;