/**
 * useImageSearch Hook Tests
 * Comprehensive tests for the image search custom hook
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useImageSearch } from '../../../src/hooks/useImageSearch';
import { server } from '../../mocks/server';
import { http, HttpResponse } from 'msw';
import React from 'react';

// Create wrapper component for React Query
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
      },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('useImageSearch', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('initial state', () => {
    it('should return initial state correctly', () => {
      const { result } = renderHook(() => useImageSearch(), {
        wrapper: createWrapper(),
      });

      expect(result.current.images).toEqual([]);
      expect(result.current.isLoading).toBe(true); // Initially loading random images
      expect(result.current.error).toBeNull();
      expect(result.current.hasMore).toBe(false);
      expect(typeof result.current.search).toBe('function');
      expect(typeof result.current.loadMore).toBe('function');
      expect(typeof result.current.clearResults).toBe('function');
    });
  });

  describe('search functionality', () => {
    it('should search for images successfully', async () => {
      const { result } = renderHook(() => useImageSearch(), {
        wrapper: createWrapper(),
      });

      // Wait for initial load
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Perform search
      result.current.search('nature');

      await waitFor(() => {
        expect(result.current.images.length).toBeGreaterThan(0);
      });

      expect(result.current.images[0]).toHaveProperty('id');
      expect(result.current.images[0]).toHaveProperty('urls');
      expect(result.current.error).toBeNull();
    });

    it('should handle search with filters', async () => {
      const { result } = renderHook(() => useImageSearch(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      result.current.search('landscape', {
        orientation: 'landscape',
        color: 'blue',
        order_by: 'popular'
      });

      await waitFor(() => {
        expect(result.current.images.length).toBeGreaterThan(0);
      });

      expect(result.current.error).toBeNull();
    });

    it('should load random images when no query provided', async () => {
      const { result } = renderHook(() => useImageSearch(), {
        wrapper: createWrapper(),
      });

      // Clear any existing search
      result.current.clearResults();

      await waitFor(() => {
        expect(result.current.images.length).toBeGreaterThan(0);
      });

      // Should have loaded random images
      expect(result.current.images[0]).toHaveProperty('id');
      expect(result.current.error).toBeNull();
    });

    it('should handle empty search results', async () => {
      server.use(
        http.get('https://api.unsplash.com/search/photos', () => {
          return HttpResponse.json({
            total: 0,
            total_pages: 0,
            results: []
          });
        })
      );

      const { result } = renderHook(() => useImageSearch(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      result.current.search('noresults');

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.images).toEqual([]);
      expect(result.current.error).toBeNull();
    });
  });

  describe('pagination', () => {
    it('should support loading more results', async () => {
      const { result } = renderHook(() => useImageSearch(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      result.current.search('nature');

      await waitFor(() => {
        expect(result.current.images.length).toBeGreaterThan(0);
        expect(result.current.hasMore).toBe(true);
      });

      const initialLength = result.current.images.length;

      // Load more results
      result.current.loadMore();

      await waitFor(() => {
        expect(result.current.images.length).toBeGreaterThan(initialLength);
      });
    });

    it('should not load more when no more pages available', async () => {
      server.use(
        http.get('https://api.unsplash.com/search/photos', ({ request }) => {
          const url = new URL(request.url);
          const page = parseInt(url.searchParams.get('page') || '1');
          
          return HttpResponse.json({
            total: 10,
            total_pages: 1,
            results: page > 1 ? [] : [
              {
                id: 'single-result',
                urls: { regular: 'https://example.com/image.jpg' },
                user: { name: 'Test', username: 'test' },
                likes: 0,
                downloads: 0,
                created_at: '2024-01-01T00:00:00Z',
                width: 100,
                height: 100
              }
            ]
          });
        })
      );

      const { result } = renderHook(() => useImageSearch(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      result.current.search('single');

      await waitFor(() => {
        expect(result.current.images.length).toBe(1);
        expect(result.current.hasMore).toBe(false);
      });

      // Try to load more - should not increase results
      const initialLength = result.current.images.length;
      result.current.loadMore();

      await waitFor(() => {
        expect(result.current.images.length).toBe(initialLength);
      });
    });
  });

  describe('error handling', () => {
    it('should handle API errors gracefully', async () => {
      server.use(
        http.get('https://api.unsplash.com/search/photos', () => {
          return HttpResponse.json(
            { errors: ['Rate limit exceeded'] },
            { status: 403 }
          );
        })
      );

      const { result } = renderHook(() => useImageSearch(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      result.current.search('error');

      await waitFor(() => {
        expect(result.current.error).not.toBeNull();
      });

      expect(result.current.error?.code).toBe('SEARCH_ERROR');
      expect(result.current.error?.message).toContain('rate limit');
    });

    it('should handle network errors', async () => {
      server.use(
        http.get('https://api.unsplash.com/search/photos', () => {
          return HttpResponse.error();
        })
      );

      const { result } = renderHook(() => useImageSearch(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      result.current.search('network-error');

      await waitFor(() => {
        expect(result.current.error).not.toBeNull();
      });

      expect(result.current.error?.code).toBe('SEARCH_ERROR');
    });

    it('should retry failed requests appropriately', async () => {
      let callCount = 0;
      server.use(
        http.get('https://api.unsplash.com/search/photos', () => {
          callCount++;
          if (callCount < 2) {
            return HttpResponse.error();
          }
          return HttpResponse.json({
            total: 1,
            total_pages: 1,
            results: [{
              id: 'retry-success',
              urls: { regular: 'https://example.com/retry.jpg' },
              user: { name: 'Test', username: 'test' },
              likes: 0,
              downloads: 0,
              created_at: '2024-01-01T00:00:00Z',
              width: 100,
              height: 100
            }]
          });
        })
      );

      const { result } = renderHook(() => useImageSearch(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      result.current.search('retry-test');

      await waitFor(() => {
        expect(result.current.images.length).toBe(1);
        expect(callCount).toBe(2); // Should have retried once
      });
    });
  });

  describe('state management', () => {
    it('should clear results correctly', async () => {
      const { result } = renderHook(() => useImageSearch(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      result.current.search('nature');

      await waitFor(() => {
        expect(result.current.images.length).toBeGreaterThan(0);
      });

      result.current.clearResults();

      await waitFor(() => {
        expect(result.current.images.length).toBeGreaterThan(0); // Should load random images
      });
    });

    it('should cancel previous requests when new search is made', async () => {
      const { result } = renderHook(() => useImageSearch(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Start first search
      result.current.search('first-search');
      
      // Immediately start second search
      result.current.search('second-search');

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Should have results from the second search
      expect(result.current.images.length).toBeGreaterThan(0);
    });

    it('should maintain loading state correctly', async () => {
      const { result } = renderHook(() => useImageSearch(), {
        wrapper: createWrapper(),
      });

      expect(result.current.isLoading).toBe(true);

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      result.current.search('loading-test');
      
      // Should be loading during search
      expect(result.current.isLoading).toBe(true);

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });
    });
  });

  describe('caching behavior', () => {
    it('should cache search results', async () => {
      let apiCallCount = 0;
      server.use(
        http.get('https://api.unsplash.com/search/photos', () => {
          apiCallCount++;
          return HttpResponse.json({
            total: 1,
            total_pages: 1,
            results: [{
              id: 'cached-result',
              urls: { regular: 'https://example.com/cached.jpg' },
              user: { name: 'Test', username: 'test' },
              likes: 0,
              downloads: 0,
              created_at: '2024-01-01T00:00:00Z',
              width: 100,
              height: 100
            }]
          });
        })
      );

      const { result } = renderHook(() => useImageSearch(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // First search
      result.current.search('cached-query');

      await waitFor(() => {
        expect(result.current.images.length).toBe(1);
      });

      const initialCallCount = apiCallCount;

      // Second search with same query should use cache
      result.current.search('cached-query');

      await waitFor(() => {
        expect(result.current.images.length).toBe(1);
      });

      // Should not have made additional API call due to caching
      expect(apiCallCount).toBe(initialCallCount);
    });
  });
});