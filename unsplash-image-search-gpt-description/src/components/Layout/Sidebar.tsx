import React from 'react';
import { cn } from '@/utils/cn';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '../Shared/Button/Button';
import {
  HomeIcon,
  MagnifyingGlassIcon,
  BookOpenIcon,
  ChartBarIcon,
  CogIcon,
  QuestionMarkCircleIcon,
  UserGroupIcon,
  XMarkIcon,
  SparklesIcon,
  AcademicCapIcon
} from '@heroicons/react/24/outline';

interface SidebarProps {
  open: boolean;
  onClose: () => void;
  isMobile: boolean;
  className?: string;
}

interface NavigationItem {
  id: string;
  name: string;
  href: string;
  icon: React.ComponentType<React.ComponentProps<'svg'>>;
  badge?: string | number;
  requiresAuth?: boolean;
}

const navigationItems: NavigationItem[] = [
  {
    id: 'dashboard',
    name: 'Dashboard',
    href: '/dashboard',
    icon: HomeIcon,
    requiresAuth: true
  },
  {
    id: 'search',
    name: 'Image Search',
    href: '/search',
    icon: MagnifyingGlassIcon
  },
  {
    id: 'vocabulary',
    name: 'Vocabulary',
    href: '/vocabulary',
    icon: BookOpenIcon,
    requiresAuth: true,
    badge: 24
  },
  {
    id: 'quiz',
    name: 'Quiz',
    href: '/quiz',
    icon: AcademicCapIcon,
    requiresAuth: true
  },
  {
    id: 'multiplayer',
    name: 'Multiplayer',
    href: '/multiplayer',
    icon: UserGroupIcon,
    requiresAuth: true,
    badge: 'New'
  },
  {
    id: 'ai-generation',
    name: 'AI Descriptions',
    href: '/ai-generation',
    icon: SparklesIcon
  },
  {
    id: 'analytics',
    name: 'Analytics',
    href: '/analytics',
    icon: ChartBarIcon,
    requiresAuth: true
  }
];

const bottomNavigationItems: NavigationItem[] = [
  {
    id: 'settings',
    name: 'Settings',
    href: '/settings',
    icon: CogIcon
  },
  {
    id: 'help',
    name: 'Help & Support',
    href: '/help',
    icon: QuestionMarkCircleIcon
  }
];

/**
 * Responsive sidebar navigation component with mobile support
 * Includes proper ARIA attributes and keyboard navigation
 */
export function Sidebar({ open, onClose, isMobile, className }: SidebarProps) {
  const { isAuthenticated, user } = useAuth();
  const currentPath = window.location.pathname;

  // Filter items based on authentication status
  const filteredItems = navigationItems.filter(item => 
    !item.requiresAuth || isAuthenticated
  );

  const handleItemClick = (item: NavigationItem) => {
    // In a real app, this would handle navigation
    console.log('Navigate to:', item.href);
    if (isMobile) {
      onClose();
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent, item: NavigationItem) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      handleItemClick(item);
    }
  };

  return (
    <>
      {/* Sidebar */}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-900',
          'border-r border-gray-200 dark:border-gray-800',
          'transform transition-transform duration-300 ease-in-out',
          'flex flex-col',
          isMobile ? (
            open ? 'translate-x-0' : '-translate-x-full'
          ) : (
            isAuthenticated ? 'translate-x-0 lg:relative lg:z-auto' : '-translate-x-full'
          ),
          className
        )}
        id="mobile-sidebar"
        aria-label="Navigation sidebar"
        role="navigation"
      >
        {/* Sidebar Header */}
        <div className="flex h-16 items-center justify-between px-4 border-b border-gray-200 dark:border-gray-800">
          <div className="flex items-center gap-2">
            <SparklesIcon className="h-6 w-6 text-primary-600" />
            <span className="text-lg font-semibold text-gray-900 dark:text-white">
              VocabLens
            </span>
          </div>
          
          {isMobile && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              aria-label="Close sidebar"
            >
              <XMarkIcon className="h-5 w-5" />
            </Button>
          )}
        </div>

        {/* User Info (if authenticated) */}
        {isAuthenticated && user && (
          <div className="p-4 border-b border-gray-200 dark:border-gray-800">
            <div className="flex items-center gap-3">
              <div className="h-8 w-8 rounded-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center">
                <span className="text-sm font-medium text-primary-600 dark:text-primary-400">
                  {user.username?.[0]?.toUpperCase() || user.email[0].toUpperCase()}
                </span>
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                  {user.username || 'User'}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                  {user.email}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Navigation Items */}
        <nav className="flex-1 px-4 py-4 space-y-2 overflow-y-auto">
          <div className="space-y-1">
            {filteredItems.map((item) => {
              const isActive = currentPath === item.href;
              const Icon = item.icon;
              
              return (
                <button
                  key={item.id}
                  onClick={() => handleItemClick(item)}
                  onKeyDown={(e) => handleKeyDown(e, item)}
                  className={cn(
                    'w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium',
                    'transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500',
                    isActive ? (
                      'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-400 border border-primary-200 dark:border-primary-800'
                    ) : (
                      'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800'
                    )
                  )}
                  aria-current={isActive ? 'page' : undefined}
                >
                  <Icon className="h-5 w-5 flex-shrink-0" aria-hidden="true" />
                  <span className="flex-1 text-left">{item.name}</span>
                  {item.badge && (
                    <span className={cn(
                      'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium',
                      typeof item.badge === 'number' ? (
                        'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300'
                      ) : (
                        'bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-400'
                      )
                    )}>
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </nav>

        {/* Bottom Navigation */}
        <div className="border-t border-gray-200 dark:border-gray-800 p-4 space-y-1">
          {bottomNavigationItems.map((item) => {
            const isActive = currentPath === item.href;
            const Icon = item.icon;
            
            return (
              <button
                key={item.id}
                onClick={() => handleItemClick(item)}
                onKeyDown={(e) => handleKeyDown(e, item)}
                className={cn(
                  'w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium',
                  'transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500',
                  isActive ? (
                    'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-400'
                  ) : (
                    'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800'
                  )
                )}
                aria-current={isActive ? 'page' : undefined}
              >
                <Icon className="h-5 w-5 flex-shrink-0" aria-hidden="true" />
                <span className="flex-1 text-left">{item.name}</span>
              </button>
            );
          })}
        </div>

        {/* App Version */}
        <div className="border-t border-gray-200 dark:border-gray-800 p-4">
          <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
            VocabLens v1.0.0
          </p>
        </div>
      </aside>
    </>
  );
}