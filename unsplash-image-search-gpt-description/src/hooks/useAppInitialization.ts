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
      setState(prev => ({ ...prev, isLoading: true, error: null }));

      // Initialize the API config service
      await apiConfigService.initialize();

      // Check if setup is needed
      const needsSetup = await apiConfigService.isSetupNeeded();
      
      // Check if user has dismissed setup before (for returning users)
      const hasSeenSetup = localStorage.getItem('vocablens_has_seen_setup') === 'true';
      
      setState(prev => ({
        ...prev,
        isLoading: false,
        needsSetup,
        showFirstTimeSetup: needsSetup && !hasSeenSetup
      }));

    } catch (error) {
      console.error('App initialization failed:', error);
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Initialization failed'
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