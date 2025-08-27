import React, { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { cn } from '@/utils/cn';
import {
  HomeIcon,
  MagnifyingGlassIcon,
  BookOpenIcon,
  AcademicCapIcon,
  InformationCircleIcon,
  ChartBarIcon,
  UserCircleIcon,
  Cog6ToothIcon,
  XMarkIcon,
  Bars3Icon
} from '@heroicons/react/24/outline';
import {
  HomeIcon as HomeIconSolid,
  MagnifyingGlassIcon as MagnifyingGlassIconSolid,
  BookOpenIcon as BookOpenIconSolid,
  AcademicCapIcon as AcademicCapIconSolid,
  InformationCircleIcon as InformationCircleIconSolid
} from '@heroicons/react/24/solid';

interface NavigationItem {
  name: string;
  path: string;
  icon: React.ComponentType<{ className?: string }>;
  iconSolid: React.ComponentType<{ className?: string }>;
  description: string;
  badge?: string;
}

interface NavigationProps {
  isOpen: boolean;
  onClose: () => void;
  className?: string;
}

const primaryNavigation: NavigationItem[] = [
  {
    name: 'Home',
    path: '/',
    icon: HomeIcon,
    iconSolid: HomeIconSolid,
    description: 'Dashboard and overview'
  },
  {
    name: 'Search',
    path: '/search',
    icon: MagnifyingGlassIcon,
    iconSolid: MagnifyingGlassIconSolid,
    description: 'Search for images'
  },
  {
    name: 'Vocabulary',
    path: '/vocabulary',
    icon: BookOpenIcon,
    iconSolid: BookOpenIconSolid,
    description: 'Manage your vocabulary'
  },
  {
    name: 'Quiz',
    path: '/quiz',
    icon: AcademicCapIcon,
    iconSolid: AcademicCapIconSolid,
    description: 'Practice and learn',
    badge: 'New'
  },
  {
    name: 'About',
    path: '/about',
    icon: InformationCircleIcon,
    iconSolid: InformationCircleIconSolid,
    description: 'Learn about VocabLens'
  }
];

const secondaryNavigation: NavigationItem[] = [
  {
    name: 'Analytics',
    path: '/analytics',
    icon: ChartBarIcon,
    iconSolid: ChartBarIcon,
    description: 'View your progress'
  },
  {
    name: 'Profile',
    path: '/profile',
    icon: UserCircleIcon,
    iconSolid: UserCircleIcon,
    description: 'Your account settings'
  },
  {
    name: 'Settings',
    path: '/settings',
    icon: Cog6ToothIcon,
    iconSolid: Cog6ToothIcon,
    description: 'App preferences'
  }
];

/**
 * Navigation component with responsive mobile/desktop layout
 * Features:
 * - Active state indication with icons and styling
 * - Mobile-responsive slide-out menu
 * - Keyboard navigation support
 * - Badge support for new features
 * - Grouped navigation items
 */
export function Navigation({ isOpen, onClose, className }: NavigationProps) {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const isActivePath = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  const handleItemClick = () => {
    onClose();
    setMobileMenuOpen(false);
  };

  const handleKeyDown = (event: React.KeyboardEvent, callback: () => void) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      callback();
    }
  };

  const renderNavigationItem = (item: NavigationItem) => {
    const isActive = isActivePath(item.path);
    const IconComponent = isActive ? item.iconSolid : item.icon;

    return (
      <NavLink
        key={item.path}
        to={item.path}
        onClick={handleItemClick}
        className={({ isActive }) =>
          cn(
            'group flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200',
            'hover:bg-gray-50 dark:hover:bg-gray-800',
            'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900',
            isActive
              ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/20 dark:text-primary-300'
              : 'text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
          )
        }
        aria-current={isActive ? 'page' : undefined}
      >
        <IconComponent
          className={cn(
            'h-5 w-5 transition-colors',
            isActive
              ? 'text-primary-600 dark:text-primary-400'
              : 'text-gray-400 group-hover:text-gray-500 dark:text-gray-500 dark:group-hover:text-gray-400'
          )}
          aria-hidden="true"
        />
        <span className="flex-1">{item.name}</span>
        {item.badge && (
          <span className="inline-flex items-center rounded-full bg-primary-100 px-2 py-0.5 text-xs font-medium text-primary-700 dark:bg-primary-900 dark:text-primary-300">
            {item.badge}
          </span>
        )}
      </NavLink>
    );
  };

  return (
    <>
      {/* Desktop Navigation */}
      <nav
        className={cn(
          'hidden lg:flex lg:flex-col lg:w-64 lg:fixed lg:inset-y-0 lg:z-40',
          'bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800',
          className
        )}
        aria-label="Main navigation"
      >
        <div className="flex flex-col flex-1 min-h-0 pt-5 pb-4 overflow-y-auto">
          <div className="flex items-center flex-shrink-0 px-4 mb-6">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
                <BookOpenIcon className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                VocabLens
              </h1>
            </div>
          </div>

          <div className="flex-1 px-3 space-y-1">
            <div className="space-y-1">
              {primaryNavigation.map(renderNavigationItem)}
            </div>

            {/* Divider */}
            <div className="border-t border-gray-200 dark:border-gray-700 my-4" />

            <div className="space-y-1">
              <h3 className="px-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Account
              </h3>
              {secondaryNavigation.map(renderNavigationItem)}
            </div>
          </div>
        </div>
      </nav>

      {/* Mobile Navigation Overlay */}
      {isOpen && (
        <div className="lg:hidden">
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 transition-opacity"
            onClick={onClose}
            aria-hidden="true"
          />

          {/* Navigation Panel */}
          <div className="fixed inset-0 z-40 flex">
            <div
              className={cn(
                'relative flex w-full max-w-xs flex-1 flex-col bg-white dark:bg-gray-900',
                'transform transition-transform duration-300 ease-in-out',
                isOpen ? 'translate-x-0' : '-translate-x-full'
              )}
              role="dialog"
              aria-modal="true"
              aria-labelledby="mobile-nav-title"
            >
              {/* Close button */}
              <div className="absolute top-0 right-0 -mr-12 pt-2">
                <button
                  type="button"
                  className="ml-1 flex h-10 w-10 items-center justify-center rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
                  onClick={onClose}
                  aria-label="Close navigation menu"
                >
                  <XMarkIcon className="h-6 w-6 text-white" aria-hidden="true" />
                </button>
              </div>

              {/* Navigation content */}
              <div className="flex flex-col flex-1 min-h-0 pt-5 pb-4 overflow-y-auto">
                <div className="flex items-center flex-shrink-0 px-4 mb-6">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
                      <BookOpenIcon className="w-5 h-5 text-white" />
                    </div>
                    <h1
                      id="mobile-nav-title"
                      className="text-xl font-bold text-gray-900 dark:text-white"
                    >
                      VocabLens
                    </h1>
                  </div>
                </div>

                <nav className="flex-1 px-3 space-y-1" aria-label="Mobile navigation">
                  <div className="space-y-1">
                    {primaryNavigation.map(renderNavigationItem)}
                  </div>

                  {/* Divider */}
                  <div className="border-t border-gray-200 dark:border-gray-700 my-4" />

                  <div className="space-y-1">
                    <h3 className="px-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Account
                    </h3>
                    {secondaryNavigation.map(renderNavigationItem)}
                  </div>
                </nav>
              </div>
            </div>

            {/* Spacer element to force the sidebar to shrink to fit close icon */}
            <div className="w-14 flex-shrink-0" aria-hidden="true">
              {/* Empty div to force sidebar to shrink to fit close icon */}
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default Navigation;