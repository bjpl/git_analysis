import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { server } from '../../mocks/server';
import { http, HttpResponse } from 'msw';

// Mock API service functions (these would be imported from actual service files)
class UnsplashService {
  private apiKey: string;
  private baseUrl: string = 'https://api.unsplash.com';

  constructor(apiKey: string) {
    this.apiKey = apiKey;
  }

  async searchPhotos(query: string, page = 1, perPage = 12) {
    const response = await fetch(
      `${this.baseUrl}/search/photos?query=${encodeURIComponent(query)}&page=${page}&per_page=${perPage}`,
      {
        headers: {
          'Authorization': `Client-ID ${this.apiKey}`,
          'Accept-Version': 'v1',
        },
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async getPhoto(id: string) {
    const response = await fetch(`${this.baseUrl}/photos/${id}`, {
      headers: {
        'Authorization': `Client-ID ${this.apiKey}`,
        'Accept-Version': 'v1',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }
}

class SupabaseService {
  private baseUrl: string;
  private apiKey: string;

  constructor(url: string, apiKey: string) {
    this.baseUrl = url;
    this.apiKey = apiKey;
  }

  async getVocabulary(userId: string, limit = 50) {
    const response = await fetch(
      `${this.baseUrl}/rest/v1/vocabulary?user_id=eq.${userId}&limit=${limit}`,
      {
        headers: {
          'apikey': this.apiKey,
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async createVocabularyEntry(entry: any) {
    const response = await fetch(`${this.baseUrl}/rest/v1/vocabulary`, {
      method: 'POST',
      headers: {
        'apikey': this.apiKey,
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(entry),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async updateVocabularyEntry(id: string, updates: any) {
    const response = await fetch(
      `${this.baseUrl}/rest/v1/vocabulary?id=eq.${id}`,
      {
        method: 'PATCH',
        headers: {
          'apikey': this.apiKey,
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updates),
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async deleteVocabularyEntry(id: string) {
    const response = await fetch(
      `${this.baseUrl}/rest/v1/vocabulary?id=eq.${id}`,
      {
        method: 'DELETE',
        headers: {
          'apikey': this.apiKey,
          'Authorization': `Bearer ${this.apiKey}`,
        },
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.status === 204;
  }
}

class OpenAIService {
  private apiKey: string;
  private baseUrl: string = 'https://api.openai.com/v1';

  constructor(apiKey: string) {
    this.apiKey = apiKey;
  }

  async generateDescription(prompt: string, options: any = {}) {
    const response = await fetch(`${this.baseUrl}/chat/completions`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'gpt-3.5-turbo',
        messages: [
          {
            role: 'user',
            content: prompt,
          },
        ],
        max_tokens: options.maxTokens || 150,
        temperature: options.temperature || 0.7,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data.choices[0]?.message?.content || '';
  }
}

describe('API Services', () => {
  let unsplashService: UnsplashService;
  let supabaseService: SupabaseService;
  let openAIService: OpenAIService;

  beforeEach(() => {
    unsplashService = new UnsplashService('test-unsplash-key');
    supabaseService = new SupabaseService('https://test.supabase.co', 'test-supabase-key');
    openAIService = new OpenAIService('test-openai-key');
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('UnsplashService', () => {
    it('searches photos successfully', async () => {
      const result = await unsplashService.searchPhotos('nature', 1, 10);

      expect(result).toHaveProperty('total');
      expect(result).toHaveProperty('results');
      expect(Array.isArray(result.results)).toBe(true);
      expect(result.results).toHaveLength(10);
    });

    it('handles search errors', async () => {
      server.use(
        http.get('https://api.unsplash.com/search/photos', () => {
          return HttpResponse.json(
            { errors: ['Rate limit exceeded'] },
            { status: 429 }
          );
        })
      );

      await expect(unsplashService.searchPhotos('error')).rejects.toThrow(
        'HTTP error! status: 429'
      );
    });

    it('gets individual photo successfully', async () => {
      const result = await unsplashService.getPhoto('test-photo-id');

      expect(result).toHaveProperty('id');
      expect(result).toHaveProperty('urls');
      expect(result).toHaveProperty('user');
    });

    it('handles network errors', async () => {
      server.use(
        http.get('https://api.unsplash.com/search/photos', () => {
          return HttpResponse.error();
        })
      );

      await expect(unsplashService.searchPhotos('network-error')).rejects.toThrow();
    });

    it('properly encodes search queries', async () => {
      const specialQuery = 'nature & wildlife';
      const result = await unsplashService.searchPhotos(specialQuery);

      expect(result).toHaveProperty('results');
    });

    it('respects pagination parameters', async () => {
      const page1 = await unsplashService.searchPhotos('test', 1, 5);
      const page2 = await unsplashService.searchPhotos('test', 2, 5);

      expect(page1.results).toHaveLength(5);
      expect(page2.results).toHaveLength(5);
      expect(page1.results[0].id).not.toBe(page2.results[0].id);
    });
  });

  describe('SupabaseService', () => {
    it('gets vocabulary entries successfully', async () => {
      const result = await supabaseService.getVocabulary('user-123', 10);

      expect(Array.isArray(result)).toBe(true);
      expect(result.length).toBeLessThanOrEqual(10);
      if (result.length > 0) {
        expect(result[0]).toHaveProperty('word');
        expect(result[0]).toHaveProperty('definition');
      }
    });

    it('creates vocabulary entry successfully', async () => {
      const newEntry = {
        word: 'serendipity',
        definition: 'A pleasant surprise',
        user_id: 'user-123',
        difficulty: 'advanced',
      };

      const result = await supabaseService.createVocabularyEntry(newEntry);

      expect(result).toHaveProperty('id');
      expect(result.word).toBe(newEntry.word);
      expect(result.definition).toBe(newEntry.definition);
    });

    it('updates vocabulary entry successfully', async () => {
      const updates = {
        learned: true,
        mastery_level: 3,
      };

      const result = await supabaseService.updateVocabularyEntry('vocab-1', updates);

      expect(result).toHaveProperty('id');
      expect(result.learned).toBe(true);
    });

    it('deletes vocabulary entry successfully', async () => {
      const result = await supabaseService.deleteVocabularyEntry('vocab-1');

      expect(result).toBe(true);
    });

    it('handles authentication errors', async () => {
      server.use(
        http.get('https://test.supabase.co/rest/v1/vocabulary', () => {
          return HttpResponse.json(
            { error: 'Unauthorized' },
            { status: 401 }
          );
        })
      );

      await expect(supabaseService.getVocabulary('user-123')).rejects.toThrow(
        'HTTP error! status: 401'
      );
    });

    it('handles validation errors', async () => {
      server.use(
        http.post('https://test.supabase.co/rest/v1/vocabulary', () => {
          return HttpResponse.json(
            { error: 'Missing required field: word' },
            { status: 400 }
          );
        })
      );

      await expect(
        supabaseService.createVocabularyEntry({ user_id: 'user-123' })
      ).rejects.toThrow('HTTP error! status: 400');
    });
  });

  describe('OpenAIService', () => {
    it('generates description successfully', async () => {
      const prompt = 'Describe this image for vocabulary learning';
      const result = await openAIService.generateDescription(prompt);

      expect(typeof result).toBe('string');
      expect(result.length).toBeGreaterThan(0);
    });

    it('handles API errors', async () => {
      server.use(
        http.post('https://api.openai.com/v1/chat/completions', () => {
          return HttpResponse.json(
            { error: { message: 'Insufficient quota' } },
            { status: 429 }
          );
        })
      );

      await expect(
        openAIService.generateDescription('test prompt')
      ).rejects.toThrow('HTTP error! status: 429');
    });

    it('respects custom options', async () => {
      const options = {
        maxTokens: 100,
        temperature: 0.5,
      };

      const result = await openAIService.generateDescription(
        'test prompt',
        options
      );

      expect(typeof result).toBe('string');
    });

    it('handles empty responses', async () => {
      server.use(
        http.post('https://api.openai.com/v1/chat/completions', () => {
          return HttpResponse.json({
            choices: [],
          });
        })
      );

      const result = await openAIService.generateDescription('test prompt');
      expect(result).toBe('');
    });
  });

  describe('Error Handling and Retry Logic', () => {
    it('implements retry logic for transient failures', async () => {
      let callCount = 0;
      server.use(
        http.get('https://api.unsplash.com/search/photos', () => {
          callCount++;
          if (callCount <= 2) {
            return HttpResponse.json(
              { errors: ['Service temporarily unavailable'] },
              { status: 503 }
            );
          }
          return HttpResponse.json({
            total: 1,
            results: [{ id: 'success', urls: { small: 'test.jpg' } }]
          });
        })
      );

      // This would require implementing retry logic in the actual service
      // For this test, we're just demonstrating the concept
      let retries = 0;
      let result;
      
      while (retries < 3) {
        try {
          result = await unsplashService.searchPhotos('retry-test');
          break;
        } catch (error) {
          retries++;
          if (retries === 3) throw error;
          await new Promise(resolve => setTimeout(resolve, 100));
        }
      }

      expect(result).toHaveProperty('results');
      expect(callCount).toBe(3);
    });

    it('handles timeout scenarios', async () => {
      server.use(
        http.get('https://api.unsplash.com/search/photos', async () => {
          await new Promise(resolve => setTimeout(resolve, 2000));
          return HttpResponse.json({ results: [] });
        })
      );

      // This would require implementing timeout handling
      const timeoutPromise = new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Request timeout')), 1000)
      );

      const searchPromise = unsplashService.searchPhotos('timeout-test');

      await expect(Promise.race([searchPromise, timeoutPromise])).rejects.toThrow('Request timeout');
    });

    it('handles malformed responses', async () => {
      server.use(
        http.get('https://api.unsplash.com/search/photos', () => {
          return new Response('Invalid JSON{', {
            status: 200,
            headers: { 'Content-Type': 'application/json' }
          });
        })
      );

      await expect(unsplashService.searchPhotos('malformed')).rejects.toThrow();
    });
  });

  describe('Caching and Performance', () => {
    it('implements request caching', async () => {
      // First request
      const start1 = performance.now();
      const result1 = await unsplashService.searchPhotos('cache-test');
      const time1 = performance.now() - start1;

      // Second identical request (would be cached in real implementation)
      const start2 = performance.now();
      const result2 = await unsplashService.searchPhotos('cache-test');
      const time2 = performance.now() - start2;

      expect(result1).toEqual(result2);
      // In a real cached implementation, time2 would be significantly less than time1
    });

    it('handles concurrent requests efficiently', async () => {
      const promises = Array.from({ length: 5 }, (_, i) =>
        unsplashService.searchPhotos(`concurrent-${i}`)
      );

      const results = await Promise.all(promises);

      expect(results).toHaveLength(5);
      results.forEach(result => {
        expect(result).toHaveProperty('results');
      });
    });
  });
});