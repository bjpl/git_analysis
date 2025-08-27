import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { cn } from '@/utils/cn';
import {
  ChevronRightIcon,
  HomeIcon,
  MagnifyingGlassIcon,
  BookOpenIcon,
  AcademicCapIcon,
  InformationCircleIcon,
  ChartBarIcon,
  UserCircleIcon,
  Cog6ToothIcon
} from '@heroicons/react/24/outline';

interface BreadcrumbItem {
  name: string;
  href: string;
  icon?: React.ComponentType<{ className?: string }>;
  current?: boolean;
}

interface BreadcrumbsProps {
  className?: string;
  showIcons?: boolean;
  maxItems?: number;
}

// Route configuration for breadcrumbs
const routeConfig: Record<string, { name: string; icon?: React.ComponentType<{ className?: string }> }> = {
  '/': { name: 'Home', icon: HomeIcon },
  '/search': { name: 'Search', icon: MagnifyingGlassIcon },
  '/vocabulary': { name: 'Vocabulary', icon: BookOpenIcon },
  '/quiz': { name: 'Quiz', icon: AcademicCapIcon },
  '/about': { name: 'About', icon: InformationCircleIcon },
  '/analytics': { name: 'Analytics', icon: ChartBarIcon },
  '/profile': { name: 'Profile', icon: UserCircleIcon },
  '/settings': { name: 'Settings', icon: Cog6ToothIcon },
  
  // Nested routes
  '/vocabulary/add': { name: 'Add Word' },
  '/vocabulary/import': { name: 'Import' },
  '/vocabulary/export': { name: 'Export' },
  '/vocabulary/categories': { name: 'Categories' },
  '/quiz/history': { name: 'History' },
  '/quiz/settings': { name: 'Quiz Settings' },
  '/profile/edit': { name: 'Edit Profile' },
  '/settings/appearance': { name: 'Appearance' },
  '/settings/notifications': { name: 'Notifications' },
  '/settings/data': { name: 'Data & Privacy' }
};

/**
 * Breadcrumbs Navigation Component
 * Features:
 * - Automatic breadcrumb generation from current route
 * - Icon support for route segments
 * - Responsive design with truncation for long paths
 * - Accessibility features with proper ARIA labels
 * - Customizable appearance and behavior
 */
export function Breadcrumbs({ 
  className, 
  showIcons = true, 
  maxItems = 4 
}: BreadcrumbsProps) {
  const location = useLocation();

  // Generate breadcrumb items from current path
  const breadcrumbItems = React.useMemo(() => {
    const pathSegments = location.pathname.split('/').filter(segment => segment !== '');
    const items: BreadcrumbItem[] = [];

    // Always include Home as first item (unless we're on home page)
    if (location.pathname !== '/') {
      items.push({
        name: routeConfig['/'].name,
        href: '/',
        icon: showIcons ? routeConfig['/'].icon : undefined
      });
    }

    // Build breadcrumb items from path segments
    let currentPath = '';
    pathSegments.forEach((segment, index) => {
      currentPath += `/${segment}`;
      const isLast = index === pathSegments.length - 1;
      
      const config = routeConfig[currentPath];
      if (config) {
        items.push({
          name: config.name,
          href: currentPath,
          icon: showIcons ? config.icon : undefined,
          current: isLast
        });
      } else {
        // Generate readable name from segment if no config exists
        const readableName = segment
          .split('-')
          .map(word => word.charAt(0).toUpperCase() + word.slice(1))
          .join(' ');
        
        items.push({
          name: readableName,
          href: currentPath,
          current: isLast
        });
      }
    });

    return items;
  }, [location.pathname, showIcons]);

  // Don't render breadcrumbs for home page or if there's only one item
  if (breadcrumbItems.length <= 1 && location.pathname === '/') {
    return null;
  }

  // Truncate breadcrumbs if they exceed maxItems
  const displayItems = breadcrumbItems.length > maxItems
    ? [
        breadcrumbItems[0], // Always show first (Home)
        { name: '...', href: '', current: false }, // Ellipsis
        ...breadcrumbItems.slice(-maxItems + 2) // Show last few items
      ]
    : breadcrumbItems;

  return (
    <nav 
      aria-label="Breadcrumb" 
      className={cn('flex', className)}
    >
      <ol className="flex items-center space-x-2 text-sm">
        {displayItems.map((item, index) => (
          <li key={item.href || index} className="flex items-center">
            {/* Separator */}
            {index > 0 && (
              <ChevronRightIcon 
                className="h-4 w-4 text-gray-400 dark:text-gray-500 mx-2" 
                aria-hidden="true" 
              />
            )}

            {/* Breadcrumb Item */}
            {item.current ? (
              // Current page (not clickable)
              <span 
                className="flex items-center gap-1.5 font-medium text-gray-900 dark:text-white"
                aria-current="page"
              >
                {item.icon && (
                  <item.icon className="h-4 w-4" aria-hidden="true" />
                )}
                {item.name}
              </span>
            ) : item.name === '...' ? (
              // Ellipsis (not clickable)
              <span className="text-gray-500 dark:text-gray-400 px-1" aria-hidden="true">
                {item.name}
              </span>
            ) : (
              // Clickable breadcrumb
              <Link
                to={item.href}
                className={cn(
                  'flex items-center gap-1.5 transition-colors duration-200',
                  'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white',
                  'focus:outline-none focus:underline focus:text-gray-900 dark:focus:text-white'
                )}
                aria-label={`Go to ${item.name}`}
              >
                {item.icon && (
                  <item.icon className="h-4 w-4" aria-hidden="true" />
                )}
                {item.name}
              </Link>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
}

/**
 * Simplified breadcrumb hook for getting current page info
 */
export function useBreadcrumbs() {
  const location = useLocation();
  
  const currentPage = React.useMemo(() => {
    const config = routeConfig[location.pathname];
    if (config) {
      return {
        name: config.name,
        path: location.pathname,
        icon: config.icon
      };
    }
    
    // Generate from path if no config
    const segments = location.pathname.split('/').filter(Boolean);
    const lastSegment = segments[segments.length - 1] || 'home';
    const name = lastSegment
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
    
    return {
      name,
      path: location.pathname,
      icon: undefined
    };
  }, [location.pathname]);

  return { currentPage };
}

export default Breadcrumbs;