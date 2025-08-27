import { useState, useEffect, useCallback } from 'react';

/**
 * Type-safe localStorage hook with serialization support
 * Handles JSON serialization/deserialization automatically
 */
export function useLocalStorage<T>(
  key: string,
  initialValue: T,
  options: {
    serialize?: (value: T) => string;
    deserialize?: (value: string) => T;
  } = {}
): [T, (value: T | ((prev: T) => T)) => void, () => void] {
  const {
    serialize = JSON.stringify,
    deserialize = JSON.parse,
  } = options;

  // Get value from localStorage or return initial value
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? deserialize(item) : initialValue;
    } catch (error) {
      console.warn(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  // Set value in localStorage and state
  const setValue = useCallback(
    (value: T | ((prev: T) => T)) => {
      try {
        const valueToStore = value instanceof Function ? value(storedValue) : value;
        setStoredValue(valueToStore);
        window.localStorage.setItem(key, serialize(valueToStore));
        
        // Dispatch custom event to sync across components
        window.dispatchEvent(
          new CustomEvent('local-storage-change', {
            detail: { key, value: valueToStore },
          })
        );
      } catch (error) {
        console.error(`Error setting localStorage key "${key}":`, error);
      }
    },
    [key, serialize, storedValue]
  );

  // Remove value from localStorage
  const removeValue = useCallback(() => {
    try {
      window.localStorage.removeItem(key);
      setStoredValue(initialValue);
      
      // Dispatch custom event
      window.dispatchEvent(
        new CustomEvent('local-storage-change', {
          detail: { key, value: null },
        })
      );
    } catch (error) {
      console.error(`Error removing localStorage key "${key}":`, error);
    }
  }, [key, initialValue]);

  // Listen for localStorage changes from other components/tabs
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === key && e.newValue !== null) {
        try {
          setStoredValue(deserialize(e.newValue));
        } catch (error) {
          console.warn(`Error deserializing localStorage value for key "${key}":`, error);
        }
      }
    };

    const handleCustomStorageChange = (e: CustomEvent) => {
      if (e.detail.key === key) {
        setStoredValue(e.detail.value ?? initialValue);
      }
    };

    window.addEventListener('storage', handleStorageChange);
    window.addEventListener('local-storage-change', handleCustomStorageChange as EventListener);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('local-storage-change', handleCustomStorageChange as EventListener);
    };
  }, [key, deserialize, initialValue]);

  return [storedValue, setValue, removeValue];
}

/**
 * Hook for storing objects in localStorage with type safety
 */
export function useLocalStorageObject<T extends Record<string, any>>(
  key: string,
  initialValue: T
) {
  return useLocalStorage(key, initialValue, {
    serialize: (value) => JSON.stringify(value),
    deserialize: (value) => {
      try {
        const parsed = JSON.parse(value);
        // Ensure we return an object that matches the initial value structure
        return { ...initialValue, ...parsed };
      } catch {
        return initialValue;
      }
    },
  });
}

/**
 * Hook for storing arrays in localStorage
 */
export function useLocalStorageArray<T>(
  key: string,
  initialValue: T[] = []
) {
  return useLocalStorage(key, initialValue, {
    serialize: (value) => JSON.stringify(value),
    deserialize: (value) => {
      try {
        const parsed = JSON.parse(value);
        return Array.isArray(parsed) ? parsed : initialValue;
      } catch {
        return initialValue;
      }
    },
  });
}

/**
 * Hook for boolean values in localStorage
 */
export function useLocalStorageBoolean(
  key: string,
  initialValue: boolean = false
) {
  return useLocalStorage(key, initialValue, {
    serialize: (value) => value.toString(),
    deserialize: (value) => value === 'true',
  });
}

/**
 * Hook for string values in localStorage (no serialization needed)
 */
export function useLocalStorageString(
  key: string,
  initialValue: string = ''
) {
  return useLocalStorage(key, initialValue, {
    serialize: (value) => value,
    deserialize: (value) => value,
  });
}

/**
 * Utility function to get localStorage size in bytes
 */
export function getLocalStorageSize(): number {
  let total = 0;
  for (const key in localStorage) {
    if (localStorage.hasOwnProperty(key)) {
      total += localStorage[key].length + key.length;
    }
  }
  return total;
}

/**
 * Utility function to clear all localStorage items with a specific prefix
 */
export function clearLocalStorageByPrefix(prefix: string): void {
  const keys = Object.keys(localStorage);
  keys
    .filter(key => key.startsWith(prefix))
    .forEach(key => localStorage.removeItem(key));
}

/**
 * Hook for managing localStorage quota and providing usage info
 */
export function useLocalStorageQuota() {
  const [usage, setUsage] = useState<{
    used: number;
    available: number;
    percentage: number;
  }>({ used: 0, available: 0, percentage: 0 });

  const calculateUsage = useCallback(() => {
    try {
      const used = getLocalStorageSize();
      // Approximate localStorage limit (varies by browser)
      const limit = 5 * 1024 * 1024; // 5MB
      const available = limit - used;
      const percentage = (used / limit) * 100;
      
      setUsage({ used, available, percentage });
    } catch (error) {
      console.error('Error calculating localStorage usage:', error);
    }
  }, []);

  useEffect(() => {
    calculateUsage();
    
    // Update usage when localStorage changes
    const handleStorageChange = () => calculateUsage();
    window.addEventListener('local-storage-change', handleStorageChange);
    window.addEventListener('storage', handleStorageChange);
    
    return () => {
      window.removeEventListener('local-storage-change', handleStorageChange);
      window.removeEventListener('storage', handleStorageChange);
    };
  }, [calculateUsage]);

  return {
    usage,
    refreshUsage: calculateUsage,
    isNearQuota: usage.percentage > 80,
    isQuotaExceeded: usage.percentage >= 100,
  };
}