/**
 * Unsplash API Service for VocabLens PWA
 * Handles image search and retrieval from Unsplash
 */
import { apiConfig, getApiHeaders, buildApiUrl, ApiError, timeouts } from '../config/api';
import { apiConfigService } from './apiConfigService';

export interface UnsplashImage {
  id: string;
  description?: string;
  alt_description?: string;
  urls: {
    thumb: string;
    small: string;
    regular: string;
    full: string;
  };
  user: {
    name: string;
    username: string;
    portfolio_url?: string;
  };
  likes: number;
  downloads: number;
  tags?: Array<{ title: string }>;
  created_at: string;
  width: number;
  height: number;
}

export interface UnsplashSearchResult {
  total: number;
  total_pages: number;
  results: UnsplashImage[];
}

export interface SearchParams {
  query: string;
  page?: number;
  per_page?: number;
  order_by?: 'latest' | 'oldest' | 'popular';
  orientation?: 'landscape' | 'portrait' | 'squarish';
  category?: string;
  color?: 'black_and_white' | 'black' | 'white' | 'yellow' | 'orange' | 'red' | 'purple' | 'magenta' | 'green' | 'teal' | 'blue';
}

class UnsplashService {
  private readonly baseUrl = apiConfig.endpoints.unsplash.base;
  private requestQueue: Promise<any>[] = [];

  /**
   * Get API headers with runtime or fallback API key
   */
  private async getHeaders(): Promise<Record<string, string>> {
    const apiKey = await apiConfigService.getEffectiveApiKey('unsplash');
    
    if (!apiKey) {
      throw new ApiError(
        'Unsplash API key not configured. Please set up your API key in settings.',
        401,
        'NO_API_KEY',
        'unsplash'
      );
    }

    return {
      'Authorization': `Client-ID ${apiKey}`,
      'Accept': 'application/json',
      'Accept-Version': 'v1'
    };
  }

  /**
   * Search for images on Unsplash
   */
  async searchImages(params: SearchParams): Promise<UnsplashSearchResult> {
    this.validateSearchParams(params);
    
    // Rate limiting
    await this.enforceRateLimit();

    const searchParams = {
      query: params.query,
      page: params.page || 1,
      per_page: Math.min(params.per_page || 20, apiConfig.images.maxPerSearch),
      order_by: params.order_by || 'relevant',
      ...(params.orientation && { orientation: params.orientation }),
      ...(params.category && { category: params.category }),
      ...(params.color && { color: params.color })
    };

    const url = buildApiUrl(
      this.baseUrl,
      apiConfig.endpoints.unsplash.search,
      searchParams
    );

    try {
      const headers = await this.getHeaders();
      const response = await this.fetchWithTimeout(url, {
        headers,
        method: 'GET'
      });

      if (!response.ok) {
        throw new ApiError(
          `Unsplash API error: ${response.statusText}`,
          response.status,
          'UNSPLASH_API_ERROR',
          'unsplash'
        );
      }

      const data: UnsplashSearchResult = await response.json();
      
      // Transform and validate the response
      return this.transformSearchResult(data);
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      
      throw new ApiError(
        `Failed to search images: ${error instanceof Error ? error.message : 'Unknown error'}`,
        500,
        'SEARCH_FAILED',
        'unsplash'
      );
    }
  }

  /**
   * Get a specific image by ID
   */
  async getImage(imageId: string): Promise<UnsplashImage> {
    if (!imageId) {
      throw new ApiError('Image ID is required', 400, 'INVALID_IMAGE_ID', 'unsplash');
    }

    await this.enforceRateLimit();

    const url = buildApiUrl(
      this.baseUrl,
      `${apiConfig.endpoints.unsplash.photos}/${imageId}`
    );

    try {
      const headers = await this.getHeaders();
      const response = await this.fetchWithTimeout(url, {
        headers,
        method: 'GET'
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new ApiError('Image not found', 404, 'IMAGE_NOT_FOUND', 'unsplash');
        }
        
        throw new ApiError(
          `Unsplash API error: ${response.statusText}`,
          response.status,
          'UNSPLASH_API_ERROR',
          'unsplash'
        );
      }

      const data: UnsplashImage = await response.json();
      return this.transformImage(data);
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      
      throw new ApiError(
        `Failed to get image: ${error instanceof Error ? error.message : 'Unknown error'}`,
        500,
        'GET_IMAGE_FAILED',
        'unsplash'
      );
    }
  }

  /**
   * Get random images
   */
  async getRandomImages(
    count: number = 10,
    query?: string,
    orientation?: 'landscape' | 'portrait' | 'squarish'
  ): Promise<UnsplashImage[]> {
    count = Math.min(count, 30); // Unsplash limit
    await this.enforceRateLimit();

    const params: Record<string, string | number> = {
      count
    };

    if (query) params.query = query;
    if (orientation) params.orientation = orientation;

    const url = buildApiUrl(
      this.baseUrl,
      `${apiConfig.endpoints.unsplash.photos}/random`,
      params
    );

    try {
      const headers = await this.getHeaders();
      const response = await this.fetchWithTimeout(url, {
        headers,
        method: 'GET'
      });

      if (!response.ok) {
        throw new ApiError(
          `Unsplash API error: ${response.statusText}`,
          response.status,
          'UNSPLASH_API_ERROR',
          'unsplash'
        );
      }

      const data = await response.json();
      const images = Array.isArray(data) ? data : [data];
      
      return images.map(image => this.transformImage(image));
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      
      throw new ApiError(
        `Failed to get random images: ${error instanceof Error ? error.message : 'Unknown error'}`,
        500,
        'RANDOM_IMAGES_FAILED',
        'unsplash'
      );
    }
  }

  /**
   * Download an image (triggers download tracking on Unsplash)
   */
  async triggerDownload(imageId: string): Promise<{ url: string }> {
    if (!imageId) {
      throw new ApiError('Image ID is required', 400, 'INVALID_IMAGE_ID', 'unsplash');
    }

    await this.enforceRateLimit();

    const url = buildApiUrl(
      this.baseUrl,
      `${apiConfig.endpoints.unsplash.photos}/${imageId}/download`
    );

    try {
      const headers = await this.getHeaders();
      const response = await this.fetchWithTimeout(url, {
        headers,
        method: 'GET'
      });

      if (!response.ok) {
        throw new ApiError(
          `Unsplash API error: ${response.statusText}`,
          response.status,
          'UNSPLASH_API_ERROR',
          'unsplash'
        );
      }

      return await response.json();
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      
      throw new ApiError(
        `Failed to trigger download: ${error instanceof Error ? error.message : 'Unknown error'}`,
        500,
        'DOWNLOAD_FAILED',
        'unsplash'
      );
    }
  }

  /**
   * Get image URL for specific size
   */
  getImageUrl(image: UnsplashImage, size: keyof UnsplashImage['urls'] = 'regular'): string {
    return image.urls[size] || image.urls.regular;
  }

  /**
   * Get attribution text for an image
   */
  getAttribution(image: UnsplashImage): string {
    return `Photo by ${image.user.name} on Unsplash`;
  }

  /**
   * Get attribution link for an image
   */
  getAttributionLink(image: UnsplashImage): string {
    return `https://unsplash.com/@${image.user.username}?utm_source=${apiConfig.app.name}&utm_medium=referral`;
  }

  // Private helper methods

  private validateSearchParams(params: SearchParams): void {
    if (!params.query || params.query.trim().length === 0) {
      throw new ApiError('Search query is required', 400, 'INVALID_QUERY', 'unsplash');
    }

    if (params.query.length > 200) {
      throw new ApiError('Search query too long (max 200 characters)', 400, 'QUERY_TOO_LONG', 'unsplash');
    }

    if (params.per_page && (params.per_page < 1 || params.per_page > apiConfig.images.maxPerSearch)) {
      throw new ApiError(
        `Invalid per_page value (1-${apiConfig.images.maxPerSearch})`,
        400,
        'INVALID_PER_PAGE',
        'unsplash'
      );
    }

    if (params.page && params.page < 1) {
      throw new ApiError('Page number must be greater than 0', 400, 'INVALID_PAGE', 'unsplash');
    }
  }

  private async enforceRateLimit(): Promise<void> {
    // Remove completed requests
    this.requestQueue = this.requestQueue.filter(request => 
      request instanceof Promise && 
      (request as any).status !== 'resolved' && 
      (request as any).status !== 'rejected'
    );

    // Wait if we've hit the concurrent request limit
    if (this.requestQueue.length >= apiConfig.rateLimit.maxConcurrent) {
      await Promise.race(this.requestQueue);
    }
  }

  private async fetchWithTimeout(url: string, options: RequestInit): Promise<Response> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeouts.search);

    const request = fetch(url, {
      ...options,
      signal: controller.signal
    });

    this.requestQueue.push(request);

    try {
      const response = await request;
      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error && error.name === 'AbortError') {
        throw new ApiError('Request timeout', 408, 'TIMEOUT', 'unsplash');
      }
      throw error;
    }
  }

  private transformSearchResult(data: UnsplashSearchResult): UnsplashSearchResult {
    return {
      total: data.total,
      total_pages: data.total_pages,
      results: data.results.map(image => this.transformImage(image))
    };
  }

  private transformImage(image: UnsplashImage): UnsplashImage {
    return {
      id: image.id,
      description: image.description,
      alt_description: image.alt_description,
      urls: {
        thumb: image.urls.thumb,
        small: image.urls.small,
        regular: image.urls.regular,
        full: image.urls.full
      },
      user: {
        name: image.user.name,
        username: image.user.username,
        portfolio_url: image.user.portfolio_url
      },
      likes: image.likes,
      downloads: image.downloads || 0,
      tags: image.tags || [],
      created_at: image.created_at,
      width: image.width,
      height: image.height
    };
  }
}

// Export singleton instance
export const unsplashService = new UnsplashService();
export default UnsplashService;