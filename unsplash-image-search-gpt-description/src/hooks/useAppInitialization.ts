/**
 * App Initialization Hook
 * Handles first-time setup and API key configuration checking
 */

import { useState, useEffect } from 'react';
import { apiConfigService } from '../services/apiConfigService';

interface AppInitializationState {
  isLoading: boolean;
  needsSetup: boolean;
  showFirstTimeSetup: boolean;
  error: string | null;
}

export const useAppInitialization = () => {
  const [state, setState] = useState<AppInitializationState>({
    isLoading: true,
    needsSetup: false,
    showFirstTimeSetup: false,
    error: null
  });

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      console.log('[VocabLens] Starting app initialization...');
      setState(prev => ({ ...prev, isLoading: true, error: null }));

      // Add timeout for initialization to prevent infinite loading
      const initPromise = Promise.race([
        (async () => {
          console.log('[VocabLens] Initializing API config service...');
          await apiConfigService.initialize();
          console.log('[VocabLens] API config service initialized');

          console.log('[VocabLens] Checking setup status...');
          const needsSetup = await apiConfigService.isSetupNeeded();
          console.log('[VocabLens] Setup needed:', needsSetup);
          
          // Safe localStorage access with fallback
          let hasSeenSetup = false;
          try {
            hasSeenSetup = localStorage.getItem('vocablens_has_seen_setup') === 'true';
          } catch (localStorageError) {
            console.warn('[VocabLens] localStorage access failed:', localStorageError);
          }
          
          return { needsSetup, hasSeenSetup };
        })(),
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Initialization timeout')), 10000)
        )
      ]);

      const { needsSetup, hasSeenSetup } = await initPromise as { needsSetup: boolean, hasSeenSetup: boolean };
      
      console.log('[VocabLens] Initialization completed successfully');
      setState(prev => ({
        ...prev,
        isLoading: false,
        needsSetup,
        showFirstTimeSetup: needsSetup && !hasSeenSetup
      }));

    } catch (error) {
      console.error('[VocabLens] App initialization failed:', error);
      
      // Graceful degradation - allow app to continue with limited functionality
      console.log('[VocabLens] Falling back to safe mode...');
      
      let hasSeenSetup = false;
      try {
        hasSeenSetup = localStorage.getItem('vocablens_has_seen_setup') === 'true';
      } catch {
        // Ignore localStorage errors in safe mode
      }
      
      setState(prev => ({
        ...prev,
        isLoading: false,
        needsSetup: true,
        showFirstTimeSetup: !hasSeenSetup,
        error: null // Don't block the UI, just show setup
      }));
    }
  };

  const completeFirstTimeSetup = () => {
    localStorage.setItem('vocablens_has_seen_setup', 'true');
    setState(prev => ({
      ...prev,
      showFirstTimeSetup: false,
      needsSetup: false
    }));
  };

  const dismissFirstTimeSetup = () => {
    localStorage.setItem('vocablens_has_seen_setup', 'true');
    setState(prev => ({
      ...prev,
      showFirstTimeSetup: false
    }));
  };

  const checkSetupStatus = async () => {
    try {
      const needsSetup = await apiConfigService.isSetupNeeded();
      setState(prev => ({ ...prev, needsSetup }));
      return needsSetup;
    } catch (error) {
      console.error('Failed to check setup status:', error);
      return true; // Assume setup is needed on error
    }
  };

  const retryInitialization = () => {
    initializeApp();
  };

  return {
    ...state,
    completeFirstTimeSetup,
    dismissFirstTimeSetup,
    checkSetupStatus,
    retryInitialization
  };
};