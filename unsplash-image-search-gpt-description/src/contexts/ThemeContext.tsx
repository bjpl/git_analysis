import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';

export type Theme = 'light' | 'dark' | 'system';
export type ResolvedTheme = 'light' | 'dark';

interface ThemeContextType {
  theme: Theme;
  resolvedTheme: ResolvedTheme;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

interface ThemeProviderProps {
  children: React.ReactNode;
  defaultTheme?: Theme;
  storageKey?: string;
}

const STORAGE_KEY = 'vocablens-theme';
const DARK_CLASS = 'dark';

/**
 * Enhanced Theme Provider with system preference detection
 * Supports light, dark, and system themes with smooth transitions
 */
export function ThemeProvider({
  children,
  defaultTheme = 'system',
  storageKey = STORAGE_KEY,
}: ThemeProviderProps) {
  const [theme, setThemeState] = useState<Theme>(defaultTheme);
  const [resolvedTheme, setResolvedTheme] = useState<ResolvedTheme>('light');
  const [mounted, setMounted] = useState(false);

  // Get system preference
  const getSystemTheme = useCallback((): ResolvedTheme => {
    if (typeof window === 'undefined') return 'light';
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }, []);

  // Resolve theme based on current setting and system preference
  const resolveTheme = useCallback((themeValue: Theme): ResolvedTheme => {
    if (themeValue === 'system') {
      return getSystemTheme();
    }
    return themeValue as ResolvedTheme;
  }, [getSystemTheme]);

  // Apply theme to document
  const applyTheme = useCallback((resolvedTheme: ResolvedTheme) => {
    const root = window.document.documentElement;
    const isDark = resolvedTheme === 'dark';
    
    root.classList.remove(DARK_CLASS);
    if (isDark) {
      root.classList.add(DARK_CLASS);
    }
    
    // Update meta theme-color for PWA
    const metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (metaThemeColor) {
      metaThemeColor.setAttribute('content', isDark ? '#020617' : '#ffffff');
    }
    
    // Dispatch custom event for other components to listen to
    window.dispatchEvent(new CustomEvent('theme-changed', { 
      detail: { theme: resolvedTheme } 
    }));
  }, []);

  // Load theme from storage
  const loadTheme = useCallback((): Theme => {
    if (typeof window === 'undefined') return defaultTheme;
    
    try {
      const stored = localStorage.getItem(storageKey);
      if (stored && ['light', 'dark', 'system'].includes(stored)) {
        return stored as Theme;
      }
    } catch (error) {
      console.warn('Failed to load theme from localStorage:', error);
    }
    
    return defaultTheme;
  }, [defaultTheme, storageKey]);

  // Save theme to storage
  const saveTheme = useCallback((theme: Theme) => {
    try {
      localStorage.setItem(storageKey, theme);
    } catch (error) {
      console.warn('Failed to save theme to localStorage:', error);
    }
  }, [storageKey]);

  // Set theme with persistence and application
  const setTheme = useCallback((newTheme: Theme) => {
    setThemeState(newTheme);
    saveTheme(newTheme);
    
    const resolved = resolveTheme(newTheme);
    setResolvedTheme(resolved);
    applyTheme(resolved);
  }, [resolveTheme, applyTheme, saveTheme]);

  // Toggle between light and dark (ignoring system)
  const toggleTheme = useCallback(() => {
    const newTheme = resolvedTheme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
  }, [resolvedTheme, setTheme]);

  // Initialize theme on mount
  useEffect(() => {
    const initialTheme = loadTheme();
    const resolved = resolveTheme(initialTheme);
    
    setThemeState(initialTheme);
    setResolvedTheme(resolved);
    applyTheme(resolved);
    setMounted(true);
  }, [loadTheme, resolveTheme, applyTheme]);

  // Listen for system theme changes
  useEffect(() => {
    if (theme !== 'system') return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (event: MediaQueryListEvent) => {
      const systemTheme = event.matches ? 'dark' : 'light';
      setResolvedTheme(systemTheme);
      applyTheme(systemTheme);
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [theme, applyTheme]);

  // Listen for storage changes (for multi-tab synchronization)
  useEffect(() => {
    const handleStorageChange = (event: StorageEvent) => {
      if (event.key === storageKey && event.newValue) {
        const newTheme = event.newValue as Theme;
        const resolved = resolveTheme(newTheme);
        
        setThemeState(newTheme);
        setResolvedTheme(resolved);
        applyTheme(resolved);
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [storageKey, resolveTheme, applyTheme]);

  // Provide stable context value
  const contextValue = React.useMemo(() => ({
    theme,
    resolvedTheme,
    setTheme,
    toggleTheme,
  }), [theme, resolvedTheme, setTheme, toggleTheme]);

  // Don't render until theme is mounted to prevent hydration mismatch
  if (!mounted) {
    return <div style={{ visibility: 'hidden' }}>{children}</div>;
  }

  return (
    <ThemeContext.Provider value={contextValue}>
      {children}
    </ThemeContext.Provider>
  );
}

/**
 * Hook to use theme context
 * Throws error if used outside ThemeProvider
 */
export function useTheme(): ThemeContextType {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}

/**
 * Higher-order component to add theme support
 */
export function withTheme<P extends object>(Component: React.ComponentType<P>) {
  const WrappedComponent = (props: P) => {
    const themeProps = useTheme();
    return <Component {...props} {...themeProps} />;
  };
  
  WrappedComponent.displayName = `withTheme(${Component.displayName || Component.name})`;
  return WrappedComponent;
}

/**
 * Theme-aware component wrapper for conditional rendering
 */
interface ThemeAwareProps {
  light?: React.ReactNode;
  dark?: React.ReactNode;
  children?: (theme: ResolvedTheme) => React.ReactNode;
}

export function ThemeAware({ light, dark, children }: ThemeAwareProps) {
  const { resolvedTheme } = useTheme();

  if (children) {
    return <>{children(resolvedTheme)}</>;
  }

  if (resolvedTheme === 'dark' && dark) {
    return <>{dark}</>;
  }

  if (resolvedTheme === 'light' && light) {
    return <>{light}</>;
  }

  return null;
}

/**
 * Theme toggle button component
 */
interface ThemeToggleProps {
  className?: string;
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export function ThemeToggle({ 
  className = '', 
  showLabel = false, 
  size = 'md' 
}: ThemeToggleProps) {
  const { theme, resolvedTheme, toggleTheme } = useTheme();

  const sizeClasses = {
    sm: 'h-8 w-8',
    md: 'h-10 w-10',
    lg: 'h-12 w-12',
  };

  const iconSize = {
    sm: 'h-4 w-4',
    md: 'h-5 w-5',
    lg: 'h-6 w-6',
  };

  return (
    <button
      onClick={toggleTheme}
      className={`
        inline-flex items-center justify-center gap-2 
        rounded-lg border border-gray-200 dark:border-gray-700
        bg-white dark:bg-gray-800 
        text-gray-900 dark:text-gray-100
        hover:bg-gray-50 dark:hover:bg-gray-700
        focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
        transition-all duration-200
        ${sizeClasses[size]}
        ${showLabel ? 'px-4' : ''}
        ${className}
      `}
      title={`Switch to ${resolvedTheme === 'dark' ? 'light' : 'dark'} theme`}
      aria-label={`Switch to ${resolvedTheme === 'dark' ? 'light' : 'dark'} theme`}
    >
      {resolvedTheme === 'dark' ? (
        <svg className={iconSize[size]} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
      ) : (
        <svg className={iconSize[size]} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
        </svg>
      )}
      
      {showLabel && (
        <span className="text-sm font-medium">
          {resolvedTheme === 'dark' ? 'Light' : 'Dark'}
        </span>
      )}
      
      {theme === 'system' && (
        <div className="absolute -top-1 -right-1 h-3 w-3 bg-blue-500 rounded-full border-2 border-white dark:border-gray-800" 
             title="Following system theme" />
      )}
    </button>
  );
}