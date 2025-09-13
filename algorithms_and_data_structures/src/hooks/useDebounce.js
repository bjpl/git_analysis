/**
 * useDebounce Hook
 * Debounces values to prevent excessive API calls or updates
 */

import { useState, useEffect } from 'react';

/**
 * Debounce a value - delays updating the debounced value until after 
 * the specified delay has passed since the last time the value changed
 */
export function useDebounce(value, delay) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

/**
 * Advanced debounce hook with additional options
 */
export function useAdvancedDebounce(value, delay, options = {}) {
  const {
    leading = false,    // Execute on leading edge
    trailing = true,    // Execute on trailing edge
    maxWait = null      // Maximum time to wait
  } = options;

  const [debouncedValue, setDebouncedValue] = useState(value);
  const [isDebouncing, setIsDebouncing] = useState(false);

  useEffect(() => {
    let timeoutId;
    let maxTimeoutId;
    
    const updateValue = () => {
      setDebouncedValue(value);
      setIsDebouncing(false);
    };

    // Leading edge execution
    if (leading && !isDebouncing) {
      updateValue();
    } else {
      setIsDebouncing(true);
    }

    // Trailing edge execution
    if (trailing) {
      timeoutId = setTimeout(updateValue, delay);
    }

    // Max wait execution
    if (maxWait && !maxTimeoutId) {
      maxTimeoutId = setTimeout(updateValue, maxWait);
    }

    return () => {
      if (timeoutId) clearTimeout(timeoutId);
      if (maxTimeoutId) clearTimeout(maxTimeoutId);
    };
  }, [value, delay, leading, trailing, maxWait, isDebouncing]);

  return { debouncedValue, isDebouncing };
}

export default useDebounce;