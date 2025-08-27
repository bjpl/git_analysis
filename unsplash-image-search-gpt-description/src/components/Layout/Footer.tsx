import React from 'react';
import { cn } from '@/utils/cn';
import { useAuth } from '@/hooks/useAuth';
import { useVocabulary } from '@/hooks/useVocabulary';
import {
  HeartIcon,
  GlobeAltIcon,
  ShieldCheckIcon,
  BugAntIcon
} from '@heroicons/react/24/outline';

interface FooterProps {
  className?: string;
}

interface FooterLink {
  id: string;
  label: string;
  href: string;
  external?: boolean;
}

const footerLinks: FooterLink[] = [
  { id: 'privacy', label: 'Privacy Policy', href: '/privacy' },
  { id: 'terms', label: 'Terms of Service', href: '/terms' },
  { id: 'support', label: 'Support', href: '/support' },
  { id: 'github', label: 'GitHub', href: 'https://github.com/vocablens', external: true },
  { id: 'feedback', label: 'Feedback', href: '/feedback' }
];

/**
 * Footer component with user stats, links, and app information
 * Displays contextual information based on authentication status
 */
export function Footer({ className }: FooterProps) {
  const { isAuthenticated, user } = useAuth();
  const { words } = useVocabulary();
  
  // Calculate user stats
  const totalWords = words?.length || 0;
  const learnedWords = words?.filter(word => word.learned).length || 0;
  const currentStreak = 7; // This would come from user data in real app

  return (
    <footer 
      className={cn(
        'bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800',
        'mt-auto',
        className
      )}
      role="contentinfo"
      aria-label="Site footer"
    >
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        {/* User Stats Section (for authenticated users) */}
        {isAuthenticated && (
          <div className="mb-8 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
              Your Learning Progress
            </h3>
            
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-primary-600 dark:text-primary-400">
                  {totalWords}
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400">
                  Words Collected
                </div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {learnedWords}
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400">
                  Words Learned
                </div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
                  {currentStreak}
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400">
                  Day Streak
                </div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                  {totalWords > 0 ? Math.round((learnedWords / totalWords) * 100) : 0}%
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400">
                  Completion
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* App Info */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <GlobeAltIcon className="h-6 w-6 text-primary-600" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                VocabLens
              </h3>
            </div>
            
            <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
              Learn vocabulary through visual context. Discover new words with AI-powered 
              image descriptions and interactive learning experiences.
            </p>
            
            <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
              <div className="flex items-center gap-1">
                <ShieldCheckIcon className="h-4 w-4" />
                <span>Privacy First</span>
              </div>
              <div className="flex items-center gap-1">
                <HeartIcon className="h-4 w-4" />
                <span>Open Source</span>
              </div>
            </div>
          </div>

          {/* Quick Links */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Quick Links
            </h3>
            
            <nav className="space-y-2" aria-label="Footer navigation">
              {footerLinks.map((link) => (
                <a
                  key={link.id}
                  href={link.href}
                  target={link.external ? '_blank' : undefined}
                  rel={link.external ? 'noopener noreferrer' : undefined}
                  className={cn(
                    'block text-sm text-gray-600 dark:text-gray-400',
                    'hover:text-primary-600 dark:hover:text-primary-400',
                    'transition-colors duration-200'
                  )}
                >
                  {link.label}
                  {link.external && (
                    <span className="ml-1" aria-label="Opens in new tab">
                      ↗
                    </span>
                  )}
                </a>
              ))}
            </nav>
          </div>

          {/* Help & Feedback */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Help & Feedback
            </h3>
            
            <div className="space-y-3">
              <a
                href="/help"
                className={cn(
                  'flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400',
                  'hover:text-primary-600 dark:hover:text-primary-400',
                  'transition-colors duration-200'
                )}
              >
                <span>Get Help</span>
              </a>
              
              <button
                onClick={() => {
                  // In real app, this would open feedback modal
                  console.log('Open feedback modal');
                }}
                className={cn(
                  'flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400',
                  'hover:text-primary-600 dark:hover:text-primary-400',
                  'transition-colors duration-200'
                )}
              >
                <BugAntIcon className="h-4 w-4" />
                <span>Report Bug</span>
              </button>
              
              <div className="pt-2">
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Found an issue? We'd love to hear from you.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className={cn(
          'mt-8 pt-8 border-t border-gray-200 dark:border-gray-800',
          'flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4'
        )}>
          <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
            <span>
              © 2024 VocabLens. All rights reserved.
            </span>
            
            <div className="hidden sm:block w-px h-4 bg-gray-300 dark:bg-gray-600" />
            
            <span>
              Version 1.0.0
            </span>
          </div>
          
          {/* Online Status */}
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
              <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse" />
              <span>Online</span>
            </div>
            
            {isAuthenticated && (
              <>
                <div className="w-px h-4 bg-gray-300 dark:bg-gray-600" />
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  Welcome back, {user?.username || 'User'}!
                </span>
              </>
            )}
          </div>
        </div>
      </div>
    </footer>
  );
}