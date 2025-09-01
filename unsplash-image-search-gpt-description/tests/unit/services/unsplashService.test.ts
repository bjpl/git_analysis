/**
 * UnsplashService Unit Tests
 * Comprehensive tests for the Unsplash API service layer
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { server } from '../../mocks/server';
import { http, HttpResponse } from 'msw';
import { unsplashService } from '../../../src/services/unsplashService';
import { ApiError } from '../../../src/config/api';

describe('UnsplashService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    server.resetHandlers();
  });

  describe('searchImages', () => {
    it('should search for images successfully', async () => {
      const params = {
        query: 'nature',
        page: 1,
        per_page: 10
      };

      const result = await unsplashService.searchImages(params);

      expect(result).toBeDefined();
      expect(result.results).toBeInstanceOf(Array);
      expect(result.total).toBeGreaterThan(0);
      expect(result.total_pages).toBeGreaterThan(0);
      expect(result.results[0]).toHaveProperty('id');
      expect(result.results[0]).toHaveProperty('urls');
      expect(result.results[0]).toHaveProperty('user');
    });

    it('should handle pagination correctly', async () => {
      const params = {
        query: 'landscape',
        page: 2,
        per_page: 5
      };

      const result = await unsplashService.searchImages(params);

      expect(result).toBeDefined();
      expect(result.results.length).toBeLessThanOrEqual(5);
    });

    it('should include search filters in the request', async () => {
      const params = {
        query: 'ocean',
        page: 1,
        per_page: 10,
        orientation: 'landscape' as const,
        color: 'blue' as const,
        order_by: 'popular' as const
      };

      const result = await unsplashService.searchImages(params);
      expect(result).toBeDefined();
    });

    it('should validate search parameters', async () => {
      // Empty query
      await expect(
        unsplashService.searchImages({ query: '' })
      ).rejects.toThrow(ApiError);

      // Query too long
      await expect(
        unsplashService.searchImages({ 
          query: 'a'.repeat(201) 
        })
      ).rejects.toThrow('Search query too long');

      // Invalid per_page
      await expect(
        unsplashService.searchImages({ 
          query: 'nature',
          per_page: 0 
        })
      ).rejects.toThrow('Invalid per_page value');

      // Invalid page
      await expect(
        unsplashService.searchImages({ 
          query: 'nature',
          page: 0 
        })
      ).rejects.toThrow('Page number must be greater than 0');
    });

    it('should handle API errors', async () => {
      server.use(
        http.get('https://api.unsplash.com/search/photos', () => {
          return HttpResponse.json(
            { errors: ['Internal server error'] },
            { status: 500 }
          );
        })
      );

      await expect(
        unsplashService.searchImages({ query: 'error' })
      ).rejects.toThrow(ApiError);
    });

    it('should handle rate limit errors', async () => {
      server.use(
        http.get('https://api.unsplash.com/search/photos', () => {
          return HttpResponse.json(
            { errors: ['Rate Limit Exceeded'] },
            { status: 403 }
          );
        })
      );

      await expect(
        unsplashService.searchImages({ query: 'rate_limit' })
      ).rejects.toThrow(ApiError);
    });

    it('should handle network timeouts', async () => {
      server.use(
        http.get('https://api.unsplash.com/search/photos', () => {
          return new Promise(() => {}); // Never resolves
        })
      );

      await expect(
        unsplashService.searchImages({ query: 'timeout' })
      ).rejects.toThrow('Request timeout');
    }, 35000);

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

      const result = await unsplashService.searchImages({ query: 'noresults' });
      
      expect(result.total).toBe(0);
      expect(result.results).toHaveLength(0);
    });
  });

  describe('getImage', () => {
    it('should get a specific image by ID', async () => {
      const imageId = 'test-image-123';
      
      const result = await unsplashService.getImage(imageId);

      expect(result).toBeDefined();
      expect(result).toHaveProperty('id');
      expect(result).toHaveProperty('urls');
      expect(result).toHaveProperty('user');
    });

    it('should throw error for empty image ID', async () => {
      await expect(
        unsplashService.getImage('')
      ).rejects.toThrow('Image ID is required');
    });

    it('should handle image not found', async () => {
      server.use(
        http.get('https://api.unsplash.com/photos/:id', () => {
          return HttpResponse.json(
            { errors: ['Photo not found'] },
            { status: 404 }
          );
        })
      );

      await expect(
        unsplashService.getImage('not-found')
      ).rejects.toThrow('Image not found');
    });

    it('should handle API errors', async () => {
      server.use(
        http.get('https://api.unsplash.com/photos/:id', () => {
          return HttpResponse.json(
            { errors: ['Server error'] },
            { status: 500 }
          );
        })
      );

      await expect(
        unsplashService.getImage('error')
      ).rejects.toThrow(ApiError);
    });
  });

  describe('getRandomImages', () => {
    it('should get random images', async () => {
      const result = await unsplashService.getRandomImages(5);

      expect(result).toBeInstanceOf(Array);
      expect(result.length).toBeLessThanOrEqual(5);
      expect(result[0]).toHaveProperty('id');
      expect(result[0]).toHaveProperty('urls');
    });

    it('should respect count limit', async () => {
      const result = await unsplashService.getRandomImages(35); // Over limit
      
      expect(result).toBeInstanceOf(Array);
      expect(result.length).toBeLessThanOrEqual(30); // Should be capped at 30
    });

    it('should include optional parameters', async () => {
      const result = await unsplashService.getRandomImages(
        3, 
        'nature', 
        'landscape'
      );

      expect(result).toBeInstanceOf(Array);
      expect(result.length).toBeLessThanOrEqual(3);
    });

    it('should handle API errors', async () => {
      server.use(
        http.get('https://api.unsplash.com/photos/random', () => {
          return HttpResponse.json(
            { errors: ['Server error'] },
            { status: 500 }
          );
        })
      );

      await expect(
        unsplashService.getRandomImages(5, 'error')
      ).rejects.toThrow(ApiError);
    });
  });

  describe('triggerDownload', () => {
    it('should trigger download tracking', async () => {
      const result = await unsplashService.triggerDownload('test-image');

      expect(result).toHaveProperty('url');
      expect(result.url).toBe('https://images.unsplash.com/download');
    });

    it('should throw error for empty image ID', async () => {
      await expect(
        unsplashService.triggerDownload('')
      ).rejects.toThrow('Image ID is required');
    });

    it('should handle API errors', async () => {
      server.use(
        http.get('https://api.unsplash.com/photos/:id/download', () => {
          return HttpResponse.json(
            { errors: ['Download failed'] },
            { status: 500 }
          );
        })
      );

      await expect(
        unsplashService.triggerDownload('error')
      ).rejects.toThrow(ApiError);
    });
  });

  describe('utility methods', () => {
    const mockImage = {
      id: 'test',
      description: 'Test image',
      alt_description: 'Test alt',
      urls: {
        thumb: 'https://example.com/thumb',
        small: 'https://example.com/small',
        regular: 'https://example.com/regular',
        full: 'https://example.com/full'
      },
      user: {
        name: 'Test User',
        username: 'testuser',
        portfolio_url: 'https://example.com/portfolio'
      },
      likes: 100,
      downloads: 500,
      tags: [{ title: 'test' }],
      created_at: '2024-01-01T00:00:00Z',
      width: 1000,
      height: 800
    };

    describe('getImageUrl', () => {
      it('should return correct URL for specified size', () => {
        expect(unsplashService.getImageUrl(mockImage, 'small'))
          .toBe('https://example.com/small');
        
        expect(unsplashService.getImageUrl(mockImage, 'thumb'))
          .toBe('https://example.com/thumb');
      });

      it('should default to regular size', () => {
        expect(unsplashService.getImageUrl(mockImage))
          .toBe('https://example.com/regular');
      });

      it('should fallback to regular if size not available', () => {
        const imageWithMissingSize = {
          ...mockImage,
          urls: { ...mockImage.urls, small: undefined }
        } as any;

        expect(unsplashService.getImageUrl(imageWithMissingSize, 'small'))
          .toBe('https://example.com/regular');
      });
    });

    describe('getAttribution', () => {
      it('should return correct attribution text', () => {
        const attribution = unsplashService.getAttribution(mockImage);
        expect(attribution).toBe('Photo by Test User on Unsplash');
      });
    });

    describe('getAttributionLink', () => {
      it('should return correct attribution link', () => {
        const link = unsplashService.getAttributionLink(mockImage);
        expect(link).toContain('@testuser');
        expect(link).toContain('utm_source=');
        expect(link).toContain('utm_medium=referral');
      });
    });
  });

  describe('rate limiting', () => {
    it('should enforce concurrent request limits', async () => {
      const promises = Array.from({ length: 10 }, () => 
        unsplashService.searchImages({ query: 'test' })
      );

      const results = await Promise.all(promises);
      
      expect(results).toHaveLength(10);
      results.forEach(result => {
        expect(result).toBeDefined();
      });
    });

    it('should handle request queue properly', async () => {
      const startTime = Date.now();
      
      // Make multiple concurrent requests
      const promises = Array.from({ length: 5 }, (_, i) => 
        unsplashService.searchImages({ query: `test-${i}` })
      );

      await Promise.all(promises);
      
      const endTime = Date.now();
      const duration = endTime - startTime;
      
      // Should complete within reasonable time despite rate limiting
      expect(duration).toBeLessThan(10000);
    });
  });

  describe('error handling', () => {
    it('should preserve error details', async () => {
      server.use(
        http.get('https://api.unsplash.com/search/photos', () => {
          return HttpResponse.json(
            { errors: ['Custom error message'] },
            { status: 422 }
          );
        })
      );

      try {
        await unsplashService.searchImages({ query: 'error' });
        expect.fail('Should have thrown an error');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        expect((error as ApiError).status).toBe(422);
        expect((error as ApiError).service).toBe('unsplash');
      }
    });

    it('should handle network errors', async () => {
      server.use(
        http.get('https://api.unsplash.com/search/photos', () => {
          return HttpResponse.error();
        })
      );

      await expect(
        unsplashService.searchImages({ query: 'network-error' })
      ).rejects.toThrow('Failed to search images');
    });
  });
});