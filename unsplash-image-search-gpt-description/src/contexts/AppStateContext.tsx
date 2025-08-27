import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { AppState } from '../types';

// Define the app state interface
interface ExtendedAppState extends AppState {
  selectedImage: any | null;
  searchResults: any[];
  currentDescription: string;
  vocabulary: any[];
  isGeneratingDescription: boolean;
  searchQuery: string;
  searchFilters: {
    orientation?: 'landscape' | 'portrait' | 'squarish';
    color?: string;
    category?: string;
  };
  activeRoute: 'home' | 'search' | 'vocabulary' | 'quiz' | 'profile';
  apiKeys: {
    unsplash?: string;
    openai?: string;
  };
  settings: {
    autoGenerate: boolean;
    defaultVocabularyLevel: 1 | 2 | 3 | 4 | 5;
    preferredLanguage: string;
    maxImagesPerSearch: number;
  };
}

// Define action types
type AppStateAction = 
  | { type: 'SET_ONLINE_STATUS'; payload: boolean }
  | { type: 'SET_THEME'; payload: 'light' | 'dark' | 'system' }
  | { type: 'SET_LANGUAGE'; payload: string }
  | { type: 'SELECT_IMAGE'; payload: any }
  | { type: 'SET_SEARCH_RESULTS'; payload: any[] }
  | { type: 'SET_CURRENT_DESCRIPTION'; payload: string }
  | { type: 'SET_GENERATING_DESCRIPTION'; payload: boolean }
  | { type: 'SET_SEARCH_QUERY'; payload: string }
  | { type: 'SET_SEARCH_FILTERS'; payload: ExtendedAppState['searchFilters'] }
  | { type: 'SET_ACTIVE_ROUTE'; payload: ExtendedAppState['activeRoute'] }
  | { type: 'SET_API_KEY'; payload: { service: 'unsplash' | 'openai'; key: string } }
  | { type: 'UPDATE_SETTINGS'; payload: Partial<ExtendedAppState['settings']> }
  | { type: 'CLEAR_SEARCH'; payload?: never }
  | { type: 'RESET_DESCRIPTION'; payload?: never };

// Initial state
const initialState: ExtendedAppState = {
  isOnline: navigator.onLine,
  theme: 'system',
  language: 'en',
  selectedImage: null,
  searchResults: [],
  currentDescription: '',
  vocabulary: [],
  isGeneratingDescription: false,
  searchQuery: '',
  searchFilters: {},
  activeRoute: 'home',
  apiKeys: {},
  settings: {
    autoGenerate: false,
    defaultVocabularyLevel: 3,
    preferredLanguage: 'en',
    maxImagesPerSearch: 20,
  },
};

// Reducer function
function appStateReducer(state: ExtendedAppState, action: AppStateAction): ExtendedAppState {
  switch (action.type) {
    case 'SET_ONLINE_STATUS':
      return { ...state, isOnline: action.payload };
    
    case 'SET_THEME':
      return { ...state, theme: action.payload };
    
    case 'SET_LANGUAGE':
      return { ...state, language: action.payload };
    
    case 'SELECT_IMAGE':
      return { 
        ...state, 
        selectedImage: action.payload,
        currentDescription: '', // Reset description when selecting new image
      };
    
    case 'SET_SEARCH_RESULTS':
      return { ...state, searchResults: action.payload };
    
    case 'SET_CURRENT_DESCRIPTION':
      return { ...state, currentDescription: action.payload };
    
    case 'SET_GENERATING_DESCRIPTION':
      return { ...state, isGeneratingDescription: action.payload };
    
    case 'SET_SEARCH_QUERY':
      return { ...state, searchQuery: action.payload };
    
    case 'SET_SEARCH_FILTERS':
      return { ...state, searchFilters: { ...state.searchFilters, ...action.payload } };
    
    case 'SET_ACTIVE_ROUTE':
      return { ...state, activeRoute: action.payload };
    
    case 'SET_API_KEY':
      return { 
        ...state, 
        apiKeys: { 
          ...state.apiKeys, 
          [action.payload.service]: action.payload.key 
        } 
      };
    
    case 'UPDATE_SETTINGS':
      return { 
        ...state, 
        settings: { ...state.settings, ...action.payload } 
      };
    
    case 'CLEAR_SEARCH':
      return {
        ...state,
        searchResults: [],
        searchQuery: '',
        selectedImage: null,
        currentDescription: '',
        isGeneratingDescription: false,
      };
    
    case 'RESET_DESCRIPTION':
      return {
        ...state,
        currentDescription: '',
        isGeneratingDescription: false,
      };
    
    default:
      return state;
  }
}

// Context creation
const AppStateContext = createContext<{
  state: ExtendedAppState;
  dispatch: React.Dispatch<AppStateAction>;
} | null>(null);

// Provider component
interface AppStateProviderProps {
  children: ReactNode;
}

export const AppStateProvider: React.FC<AppStateProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(appStateReducer, initialState);

  // Handle online/offline status
  useEffect(() => {
    const handleOnline = () => dispatch({ type: 'SET_ONLINE_STATUS', payload: true });
    const handleOffline = () => dispatch({ type: 'SET_ONLINE_STATUS', payload: false });

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Handle theme changes
  useEffect(() => {
    const root = document.documentElement;
    
    if (state.theme === 'system') {
      const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      root.classList.toggle('dark', isDark);
    } else {
      root.classList.toggle('dark', state.theme === 'dark');
    }

    // Update CSS custom properties for toast styling
    const isDarkMode = root.classList.contains('dark');
    root.style.setProperty('--toast-bg', isDarkMode ? '#374151' : '#ffffff');
    root.style.setProperty('--toast-color', isDarkMode ? '#f9fafb' : '#111827');
  }, [state.theme]);

  // Load settings from localStorage on mount
  useEffect(() => {
    try {
      const savedSettings = localStorage.getItem('vocablens-settings');
      if (savedSettings) {
        const parsed = JSON.parse(savedSettings);
        dispatch({ type: 'UPDATE_SETTINGS', payload: parsed });
      }

      const savedTheme = localStorage.getItem('vocablens-theme') as ExtendedAppState['theme'];
      if (savedTheme) {
        dispatch({ type: 'SET_THEME', payload: savedTheme });
      }

      const savedLanguage = localStorage.getItem('vocablens-language');
      if (savedLanguage) {
        dispatch({ type: 'SET_LANGUAGE', payload: savedLanguage });
      }
    } catch (error) {
      console.warn('Failed to load settings from localStorage:', error);
    }
  }, []);

  // Save settings to localStorage when they change
  useEffect(() => {
    try {
      localStorage.setItem('vocablens-settings', JSON.stringify(state.settings));
      localStorage.setItem('vocablens-theme', state.theme);
      localStorage.setItem('vocablens-language', state.language);
    } catch (error) {
      console.warn('Failed to save settings to localStorage:', error);
    }
  }, [state.settings, state.theme, state.language]);

  return (
    <AppStateContext.Provider value={{ state, dispatch }}>
      {children}
    </AppStateContext.Provider>
  );
};

// Custom hook to use the app state
export const useAppState = () => {
  const context = useContext(AppStateContext);
  if (!context) {
    throw new Error('useAppState must be used within an AppStateProvider');
  }
  return context;
};

// Convenience hooks for specific state slices
export const useSelectedImage = () => {
  const { state, dispatch } = useAppState();
  return {
    selectedImage: state.selectedImage,
    selectImage: (image: any) => dispatch({ type: 'SELECT_IMAGE', payload: image }),
    clearSelection: () => dispatch({ type: 'SELECT_IMAGE', payload: null }),
  };
};

export const useSearchState = () => {
  const { state, dispatch } = useAppState();
  return {
    searchResults: state.searchResults,
    searchQuery: state.searchQuery,
    searchFilters: state.searchFilters,
    setSearchResults: (results: any[]) => dispatch({ type: 'SET_SEARCH_RESULTS', payload: results }),
    setSearchQuery: (query: string) => dispatch({ type: 'SET_SEARCH_QUERY', payload: query }),
    setSearchFilters: (filters: ExtendedAppState['searchFilters']) => 
      dispatch({ type: 'SET_SEARCH_FILTERS', payload: filters }),
    clearSearch: () => dispatch({ type: 'CLEAR_SEARCH' }),
  };
};

export const useDescriptionState = () => {
  const { state, dispatch } = useAppState();
  return {
    currentDescription: state.currentDescription,
    isGeneratingDescription: state.isGeneratingDescription,
    setCurrentDescription: (description: string) => 
      dispatch({ type: 'SET_CURRENT_DESCRIPTION', payload: description }),
    setGeneratingDescription: (generating: boolean) => 
      dispatch({ type: 'SET_GENERATING_DESCRIPTION', payload: generating }),
    resetDescription: () => dispatch({ type: 'RESET_DESCRIPTION' }),
  };
};

export const useAppSettings = () => {
  const { state, dispatch } = useAppState();
  return {
    settings: state.settings,
    theme: state.theme,
    language: state.language,
    isOnline: state.isOnline,
    updateSettings: (settings: Partial<ExtendedAppState['settings']>) => 
      dispatch({ type: 'UPDATE_SETTINGS', payload: settings }),
    setTheme: (theme: ExtendedAppState['theme']) => 
      dispatch({ type: 'SET_THEME', payload: theme }),
    setLanguage: (language: string) => 
      dispatch({ type: 'SET_LANGUAGE', payload: language }),
  };
};

export default AppStateContext;