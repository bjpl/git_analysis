import React, { useState, useRef, useEffect } from 'react';
import { cn } from '@/utils/cn';
import { useAuthContext } from '@/contexts/AuthContext';
import { User } from '@/types';
import { Button } from '../Shared/Button/Button';
import {
  UserCircleIcon,
  CogIcon,
  ArrowRightOnRectangleIcon,
  ChartBarIcon,
  BookOpenIcon,
  BellIcon,
  QuestionMarkCircleIcon,
  ChevronDownIcon
} from '@heroicons/react/24/outline';

interface UserMenuProps {
  user: User | null;
  className?: string;
}

interface MenuOption {
  id: string;
  label: string;
  icon: React.ComponentType<React.ComponentProps<'svg'>>;
  href?: string;
  onClick?: () => void;
  divider?: boolean;
}

/**
 * UserMenu dropdown component with user profile and navigation options
 * Includes proper ARIA attributes and keyboard navigation
 */
export function UserMenu({ user, className }: UserMenuProps) {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const { signOut } = useAuthContext();

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        menuRef.current &&
        !menuRef.current.contains(event.target as Node) &&
        !triggerRef.current?.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Handle keyboard navigation
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setIsOpen(false);
        triggerRef.current?.focus();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen]);

  const handleSignOut = async () => {
    setIsOpen(false);
    const { error } = await signOut();
    if (error) {
      console.error('Sign out error:', error);
      // In a real app, show error toast
    }
  };

  const handleMenuItemClick = (item: MenuOption) => {
    setIsOpen(false);
    if (item.onClick) {
      item.onClick();
    } else if (item.href) {
      // In a real app, this would use router navigation
      console.log('Navigate to:', item.href);
    }
  };

  const menuOptions: MenuOption[] = [
    {
      id: 'profile',
      label: 'Your Profile',
      icon: UserCircleIcon,
      href: '/profile',
    },
    {
      id: 'vocabulary',
      label: 'My Vocabulary',
      icon: BookOpenIcon,
      href: '/vocabulary',
    },
    {
      id: 'analytics',
      label: 'Learning Analytics',
      icon: ChartBarIcon,
      href: '/analytics',
    },
    {
      id: 'notifications',
      label: 'Notifications',
      icon: BellIcon,
      href: '/notifications',
    },
    {
      id: 'settings',
      label: 'Settings',
      icon: CogIcon,
      href: '/settings',
      divider: true,
    },
    {
      id: 'help',
      label: 'Help & Support',
      icon: QuestionMarkCircleIcon,
      href: '/help',
    },
    {
      id: 'signout',
      label: 'Sign Out',
      icon: ArrowRightOnRectangleIcon,
      onClick: handleSignOut,
      divider: true,
    },
  ];

  if (!user) return null;

  const userInitials = user.username?.[0]?.toUpperCase() || user.email[0].toUpperCase();

  return (
    <div className={cn('relative', className)}>
      {/* Menu Trigger */}
      <Button
        ref={triggerRef}
        variant="ghost"
        size="sm"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-2"
        aria-expanded={isOpen}
        aria-haspopup="menu"
        aria-label="User menu"
      >
        {/* User Avatar */}
        <div className="h-8 w-8 rounded-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center overflow-hidden">
          {user.avatar_url ? (
            <img
              src={user.avatar_url}
              alt={user.username || 'User avatar'}
              className="h-full w-full object-cover"
              onError={(e) => {
                // Fallback to initials if image fails to load
                const target = e.target as HTMLImageElement;
                target.style.display = 'none';
                target.nextElementSibling?.classList.remove('hidden');
              }}
            />
          ) : null}
          <span 
            className={cn(
              'text-sm font-medium text-primary-600 dark:text-primary-400',
              user.avatar_url && 'hidden'
            )}
          >
            {userInitials}
          </span>
        </div>
        
        {/* User Name (hidden on mobile) */}
        <span className="hidden sm:block text-sm font-medium text-gray-700 dark:text-gray-300 truncate max-w-24">
          {user.username || 'User'}
        </span>
        
        {/* Chevron Icon */}
        <ChevronDownIcon 
          className={cn(
            'h-4 w-4 text-gray-500 transition-transform duration-200',
            isOpen && 'rotate-180'
          )} 
        />
      </Button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div
          ref={menuRef}
          className={cn(
            'absolute right-0 top-full mt-2 w-56 bg-white dark:bg-gray-800',
            'border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg',
            'z-50 animate-fade-in'
          )}
          role="menu"
          aria-orientation="vertical"
          aria-labelledby="user-menu-button"
        >
          {/* User Info Header */}
          <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center overflow-hidden">
                {user.avatar_url ? (
                  <img
                    src={user.avatar_url}
                    alt={user.username || 'User avatar'}
                    className="h-full w-full object-cover"
                  />
                ) : (
                  <span className="text-lg font-medium text-primary-600 dark:text-primary-400">
                    {userInitials}
                  </span>
                )}
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

          {/* Menu Items */}
          <div className="py-1">
            {menuOptions.map((option, index) => {
              const Icon = option.icon;
              const isLast = index === menuOptions.length - 1;
              
              return (
                <React.Fragment key={option.id}>
                  {option.divider && index > 0 && (
                    <div className="border-t border-gray-200 dark:border-gray-700 my-1" />
                  )}
                  
                  <button
                    onClick={() => handleMenuItemClick(option)}
                    className={cn(
                      'w-full flex items-center gap-3 px-4 py-2 text-sm text-left',
                      'hover:bg-gray-50 dark:hover:bg-gray-700',
                      'focus:outline-none focus:bg-gray-50 dark:focus:bg-gray-700',
                      'transition-colors duration-200',
                      option.id === 'signout' && 'text-red-700 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20',
                      isLast && 'rounded-b-lg'
                    )}
                    role="menuitem"
                    tabIndex={0}
                  >
                    <Icon className="h-4 w-4 flex-shrink-0" aria-hidden="true" />
                    <span>{option.label}</span>
                  </button>
                </React.Fragment>
              );
            })}
          </div>

          {/* User Stats Footer */}
          <div className="border-t border-gray-200 dark:border-gray-700 px-4 py-3">
            <div className="grid grid-cols-2 gap-4 text-center">
              <div>
                <div className="text-lg font-semibold text-gray-900 dark:text-white">
                  24
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  Words Learned
                </div>
              </div>
              <div>
                <div className="text-lg font-semibold text-gray-900 dark:text-white">
                  7
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  Day Streak
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}