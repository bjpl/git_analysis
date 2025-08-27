import React, { useState, useEffect } from 'react';
import { cn } from '@/utils/cn';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { Footer } from './Footer';
import { useAuth } from '@/hooks/useAuth';
import { useOffline } from '@/hooks/useOffline';
import { OfflineBanner } from '../PWA/OfflineBanner';
import { InstallPrompt } from '../PWA/InstallPrompt';
import { UpdatePrompt } from '../PWA/UpdatePrompt';

interface AppShellProps {
  children: React.ReactNode;
  className?: string;
}

/**
 * AppShell provides the main layout structure for the VocabLens PWA
 * Features responsive design, navigation management, and PWA prompts
 */
export function AppShell({ children, className }: AppShellProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const { user, isAuthenticated } = useAuth();
  const { isOnline, isInstallable } = useOffline();

  // Handle responsive design
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 1024);
      if (window.innerWidth >= 1024) {
        setSidebarOpen(false);
      }
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Close sidebar when clicking outside on mobile
  useEffect(() => {
    if (!isMobile || !sidebarOpen) return;

    const handleClickOutside = (event: MouseEvent) => {
      const sidebar = document.getElementById('mobile-sidebar');
      const trigger = document.getElementById('sidebar-trigger');
      
      if (
        sidebar &&
        !sidebar.contains(event.target as Node) &&
        !trigger?.contains(event.target as Node)
      ) {
        setSidebarOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isMobile, sidebarOpen]);

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Escape to close sidebar
      if (event.key === 'Escape' && sidebarOpen) {
        setSidebarOpen(false);
      }
      
      // Alt + M to toggle sidebar
      if (event.altKey && event.key === 'm') {
        event.preventDefault();
        setSidebarOpen(prev => !prev);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [sidebarOpen]);

  return (
    <div className={cn('min-h-screen bg-gray-50 dark:bg-gray-950', className)}>
      {/* Offline Banner */}
      <OfflineBanner />
      
      {/* Install Prompt */}
      {isInstallable && <InstallPrompt />}
      
      {/* Update Prompt */}
      <UpdatePrompt />
      
      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && isMobile && (
        <div 
          className="fixed inset-0 z-40 bg-black/50 transition-opacity lg:hidden"
          aria-hidden="true"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <Sidebar 
        open={sidebarOpen} 
        onClose={() => setSidebarOpen(false)}
        isMobile={isMobile}
      />

      {/* Main Content Area */}
      <div className={cn(
        'flex flex-col transition-all duration-300 ease-in-out',
        !isMobile && isAuthenticated ? 'lg:pl-64' : '',
        'min-h-screen'
      )}>
        {/* Header */}
        <Header 
          onMenuClick={() => setSidebarOpen(!sidebarOpen)}
          showMenuButton={isMobile || !isAuthenticated}
        />

        {/* Main Content */}
        <main 
          className={cn(
            'flex-1 px-4 sm:px-6 lg:px-8 py-6',
            'focus:outline-none transition-all duration-300'
          )}
          role="main"
          aria-label="Main content"
        >
          <div className="mx-auto max-w-7xl">
            {children}
          </div>
        </main>

        {/* Footer */}
        <Footer />
      </div>

      {/* Skip to main content link for accessibility */}
      <a
        href="#main-content"
        className={cn(
          'sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4',
          'z-100 px-4 py-2 bg-primary-600 text-white rounded-md',
          'font-medium text-sm transition-all duration-200'
        )}
      >
        Skip to main content
      </a>
    </div>
  );
}