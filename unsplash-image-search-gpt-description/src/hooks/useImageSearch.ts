import { useState, useCallback, useRef } from 'react';
import { useQuery, useInfiniteQuery } from '@tanstack/react-query';
import { Image, UnsplashSearchResponse, UseImageSearchReturn } from '../types';
import toast from 'react-hot-toast';

const UNSPLASH_ACCESS_KEY = process.env.REACT_APP_UNSPLASH_ACCESS_KEY!;
const UNSPLASH_API_URL = 'https://api.unsplash.com';

if (!UNSPLASH_ACCESS_KEY) {
  throw new Error('Missing Unsplash API key');
}

interface SearchParams {
  query: string;
  page?: number;
  per_page?: number;
  order_by?: 'latest' | 'oldest' | 'popular';
  color?: 'black_and_white' | 'black' | 'white' | 'yellow' | 'orange' | 'red' | 'purple' | 'magenta' | 'green' | 'teal' | 'blue';
  orientation?: 'landscape' | 'portrait' | 'squarish';
}

class UnsplashAPI {
  private baseURL = UNSPLASH_API_URL;
  private headers = {
    'Authorization': `Client-ID ${UNSPLASH_ACCESS_KEY}`,
    'Accept-Version': 'v1',
  };

  async searchPhotos(params: SearchParams): Promise<UnsplashSearchResponse> {
    const searchParams = new URLSearchParams({
      query: params.query,
      page: String(params.page || 1),
      per_page: String(params.per_page || 20),
      ...(params.order_by && { order_by: params.order_by }),
      ...(params.color && { color: params.color }),
      ...(params.orientation && { orientation: params.orientation }),
    });

    const response = await fetch(`${this.baseURL}/search/photos?${searchParams}`, {
      headers: this.headers,
    });

    if (!response.ok) {
      if (response.status === 403) {
        throw new Error('API rate limit exceeded. Please try again later.');
      }
      throw new Error(`Search failed: ${response.statusText}`);
    }

    return response.json();
  }

  async getRandomPhotos(count: number = 20): Promise<Image[]> {
    const response = await fetch(`${this.baseURL}/photos/random?count=${count}`, {
      headers: this.headers,
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch random photos: ${response.statusText}`);
    }

    return response.json();
  }

  async getPhoto(id: string): Promise<Image> {
    const response = await fetch(`${this.baseURL}/photos/${id}`, {
      headers: this.headers,
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch photo: ${response.statusText}`);
    }

    return response.json();
  }

  async downloadPhoto(downloadUrl: string): Promise<void> {
    // Trigger download tracking as per Unsplash guidelines
    await fetch(downloadUrl, {
      headers: this.headers,
    });
  }
}

const unsplashAPI = new UnsplashAPI();

export const useImageSearch = (): UseImageSearchReturn => {
  const [currentQuery, setCurrentQuery] = useState<string>('');
  const [searchFilters, setSearchFilters] = useState<Omit<SearchParams, 'query' | 'page'>>({});
  const abortControllerRef = useRef<AbortController | null>(null);

  // Infinite query for search results with pagination
  const {
    data,
    isLoading,
    error,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    refetch,
  } = useInfiniteQuery({
    queryKey: ['images', 'search', currentQuery, searchFilters],
    queryFn: async ({ pageParam = 1, signal }) => {
      if (!currentQuery.trim()) {
        // Return random photos if no query
        const images = await unsplashAPI.getRandomPhotos(20);
        return {
          results: images,
          total: images.length,
          total_pages: 1,
        } as UnsplashSearchResponse;
      }

      return unsplashAPI.searchPhotos({
        query: currentQuery,
        page: pageParam,
        per_page: 20,
        ...searchFilters,
      });
    },
    getNextPageParam: (lastPage, allPages) => {
      if (lastPage.results.length === 0) return undefined;
      return allPages.length < lastPage.total_pages ? allPages.length + 1 : undefined;
    },
    enabled: true,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    retry: (failureCount, error) => {
      // Don't retry on rate limit or auth errors
      if (error.message.includes('rate limit') || error.message.includes('403')) {
        return false;
      }
      return failureCount < 2;
    },
  });

  // Flatten paginated results
  const images = data?.pages.flatMap(page => page.results) || [];
  const hasMore = hasNextPage;

  const search = useCallback((query: string, filters?: Omit<SearchParams, 'query' | 'page'>) => {
    // Cancel any ongoing request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    setCurrentQuery(query);
    if (filters) {
      setSearchFilters(filters);
    }
  }, []);

  const loadMore = useCallback(() => {
    if (hasNextPage && !isFetchingNextPage) {
      fetchNextPage();
    }
  }, [hasNextPage, isFetchingNextPage, fetchNextPage]);

  const clearResults = useCallback(() => {
    setCurrentQuery('');
    setSearchFilters({});
  }, []);

  // Handle errors
  if (error) {
    toast.error(error.message || 'Failed to search images');
  }

  return {
    images,
    isLoading: isLoading || isFetchingNextPage,
    error: error ? { 
      code: 'SEARCH_ERROR', 
      message: error.message || 'Search failed',
      timestamp: new Date().toISOString(),
      recoverable: true,
      details: error
    } : null,
    hasMore,
    search,
    loadMore,
    clearResults,
  };
};

// Hook for getting a specific image
export const useImage = (imageId: string | null) => {
  return useQuery({
    queryKey: ['images', 'detail', imageId],
    queryFn: () => unsplashAPI.getPhoto(imageId!),
    enabled: !!imageId,
    staleTime: 30 * 60 * 1000, // 30 minutes
    retry: 1,
  });
};

// Hook for random images (used for initial load)
export const useRandomImages = (count: number = 20) => {
  return useQuery({
    queryKey: ['images', 'random', count],
    queryFn: () => unsplashAPI.getRandomPhotos(count),
    staleTime: 10 * 60 * 1000, // 10 minutes
    retry: 1,
  });
};

// Utility hook for tracking downloads (Unsplash requirement)
export const useTrackDownload = () => {
  return useCallback(async (image: Image) => {
    try {
      if (image.links?.download_location) {
        await unsplashAPI.downloadPhoto(image.links.download_location);
      }
    } catch (error) {
      console.error('Failed to track download:', error);
      // Don't show error to user as this is just tracking
    }
  }, []);
};