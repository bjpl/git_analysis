import { useAuthContext } from '@/contexts/AuthContext';

/**
 * Hook to access authentication state and operations
 * This is a convenience wrapper around useAuthContext
 */
export function useAuth() {
  return useAuthContext();
}