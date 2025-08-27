import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { User } from '../types';

interface AppState {
  // User and authentication
  user: User | null;
  isAuthenticated: boolean;
  
  // UI preferences
  theme: 'light' | 'dark' | 'system';
  sidebarOpen: boolean;
  
  // Network status
  isOnline: boolean;
  
  // App settings
  settings: {
    language: string;
    autoSave: boolean;
    notifications: boolean;
    analytics: boolean;
  };
}

interface AppActions {
  // User actions
  setUser: (user: User | null) => void;
  setIsAuthenticated: (isAuthenticated: boolean) => void;
  
  // UI actions
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;
  
  // Network actions
  setIsOnline: (isOnline: boolean) => void;
  
  // Settings actions
  updateSettings: (settings: Partial<AppState['settings']>) => void;
  
  // Reset actions
  reset: () => void;
}

type AppStore = AppState & AppActions;

const initialState: AppState = {
  user: null,
  isAuthenticated: false,
  theme: 'system',
  sidebarOpen: true,
  isOnline: true,
  settings: {
    language: 'en',
    autoSave: true,
    notifications: true,
    analytics: false,
  },
};

export const useAppStore = create<AppStore>()(
  persist(
    (set, get) => ({
      ...initialState,
      
      // User actions
      setUser: (user) => set({ user, isAuthenticated: !!user }),
      setIsAuthenticated: (isAuthenticated) => set({ isAuthenticated }),
      
      // UI actions
      setTheme: (theme) => {
        set({ theme });
        
        // Apply theme to document
        const root = document.documentElement;
        if (theme === 'dark') {
          root.classList.add('dark');
        } else if (theme === 'light') {
          root.classList.remove('dark');
        } else {
          // System theme
          const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
          if (prefersDark) {
            root.classList.add('dark');
          } else {
            root.classList.remove('dark');
          }
        }
      },
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      
      // Network actions
      setIsOnline: (isOnline) => set({ isOnline }),
      
      // Settings actions
      updateSettings: (newSettings) =>
        set((state) => ({
          settings: { ...state.settings, ...newSettings },
        })),
      
      // Reset actions
      reset: () => set(initialState),
    }),
    {
      name: 'vocablens-app-store',
      storage: createJSONStorage(() => localStorage),
      // Only persist certain fields
      partialize: (state) => ({
        theme: state.theme,
        sidebarOpen: state.sidebarOpen,
        settings: state.settings,
      }),
    }
  )
);

// Initialize theme on app load
if (typeof window !== 'undefined') {
  const { theme } = useAppStore.getState();
  const root = document.documentElement;
  
  if (theme === 'dark') {
    root.classList.add('dark');
  } else if (theme === 'light') {
    root.classList.remove('dark');
  } else {
    // System theme
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (prefersDark) {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    
    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      const currentTheme = useAppStore.getState().theme;
      if (currentTheme === 'system') {
        if (e.matches) {
          root.classList.add('dark');
        } else {
          root.classList.remove('dark');
        }
      }
    });
  }
}