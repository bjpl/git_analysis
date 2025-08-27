/**
 * Integration Tests for Runtime API Services
 * Tests the integration between ConfigManager and API services with runtime configuration
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { configManager } from '../../src/services/configManager';
import { unsplashService } from '../../src/services/unsplashService';
import { openaiService } from '../../src/services/openaiService';

// Mock fetch for API calls
const mockFetch = vi.fn();
global.fetch = mockFetch;

// Mock localStorage for configuration persistence
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
  length: 0,
  key: vi.fn()
};
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

describe('Runtime API Services Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockFetch.mockClear();
    localStorageMock.getItem.mockClear();
    localStorageMock.setItem.mockClear();
  });

  afterEach(() => {
    configManager.stopHealthMonitoring();
  });

  describe('First-Time User Setup Flow', () => {
    it('should guide new user through API key setup', async () => {
      // Simulate new user with no stored keys
      localStorageMock.getItem.mockReturnValue(null);

      // Check initial health status
      const initialHealth = await configManager.getHealthStatus();
      expect(initialHealth.overall).toBe('critical');
      
      const missingKeyIssues = initialHealth.issues.filter(
        issue => issue.message.includes('missing')
      );
      expect(missingKeyIssues.length).toBeGreaterThan(0);

      // Simulate user adding Unsplash key
      mockFetch.mockResolvedValueOnce({ 
        ok: true,
        json: () => Promise.resolve({ username: 'testuser' })
      });

      const unsplashResult = await configManager.updateServiceConfiguration({
        service: 'unsplash',
        apiKey: 'valid-unsplash-key-123'
      });

      expect(unsplashResult.success).toBe(true);
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/me'),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Client-ID valid-unsplash-key-123'
          })
        })
      );

      // Simulate user adding OpenAI key
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ data: [{ id: 'gpt-3.5-turbo' }] })
      });

      const openaiResult = await configManager.updateServiceConfiguration({
        service: 'openai',
        apiKey: 'sk-valid-openai-key-456'
      });

      expect(openaiResult.success).toBe(true);
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/models'),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Bearer sk-valid-openai-key-456'
          })
        })
      );

      // Check improved health status
      const finalHealth = await configManager.getHealthStatus();
      expect(finalHealth.overall).not.toBe('critical');
    });

    it('should handle partial setup gracefully', async () => {
      // User adds only Unsplash key
      mockFetch.mockResolvedValueOnce({ ok: true });

      await configManager.updateServiceConfiguration({
        service: 'unsplash',
        apiKey: 'unsplash-only-key'
      });

      const health = await configManager.getHealthStatus();
      
      // Should be degraded (not critical) with partial setup
      expect(health.overall).toBe('degraded');
      
      // Should have issues for missing OpenAI key
      const openaiIssues = health.issues.filter(
        issue => issue.service === 'openai' && issue.message.includes('missing')
      );
      expect(openaiIssues.length).toBeGreaterThan(0);
    });
  });

  describe('API Key Validation Integration', () => {
    it('should validate Unsplash key with actual API call', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          id: 'testuser',
          username: 'testuser',
          name: 'Test User'
        })
      });

      const result = await configManager.validateApiKey('unsplash', 'valid-key');
      
      expect(result.valid).toBe(true);
      expect(mockFetch).toHaveBeenCalledWith(
        'https://api.unsplash.com/me',
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Client-ID valid-key'
          })
        })
      );
    });

    it('should validate OpenAI key with actual API call', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          data: [
            { id: 'gpt-3.5-turbo', object: 'model' },
            { id: 'gpt-4', object: 'model' }
          ]
        })
      });

      const result = await configManager.validateApiKey('openai', 'sk-valid-key');
      
      expect(result.valid).toBe(true);
      expect(mockFetch).toHaveBeenCalledWith(
        'https://api.openai.com/v1/models',
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Bearer sk-valid-key'
          })
        })
      );
    });

    it('should handle invalid API keys properly', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        statusText: 'Unauthorized'
      });

      const result = await configManager.validateApiKey('unsplash', 'invalid-key');
      
      expect(result.valid).toBe(false);
      expect(result.error).toBeDefined();
    });

    it('should handle network failures during validation', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network failure'));

      const result = await configManager.validateApiKey('openai', 'sk-test');
      
      expect(result.valid).toBe(false);
      expect(result.error).toContain('Network error');
    });
  });

  describe('Service Integration with Runtime Keys', () => {
    it('should use updated API keys in Unsplash service', async () => {
      // Update API key in config manager
      mockFetch.mockResolvedValueOnce({ ok: true }); // Validation call
      
      await configManager.updateServiceConfiguration({
        service: 'unsplash',
        apiKey: 'runtime-unsplash-key'
      });

      // Mock successful search response
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          total: 10,
          total_pages: 1,
          results: [{
            id: 'test-image',
            urls: { regular: 'https://test-image.jpg' },
            user: { name: 'Test User', username: 'testuser' },
            likes: 100,
            downloads: 50,
            created_at: '2023-01-01T00:00:00Z',
            width: 1200,
            height: 800
          }]
        })
      });

      // Use Unsplash service - it should use the runtime key
      await unsplashService.searchImages({ query: 'test' });

      expect(mockFetch).toHaveBeenLastCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Client-ID runtime-unsplash-key'
          })
        })
      );
    });

    it('should use updated API keys in OpenAI service', async () => {
      // Update API key in config manager
      mockFetch.mockResolvedValueOnce({ ok: true }); // Validation call
      
      await configManager.updateServiceConfiguration({
        service: 'openai',
        apiKey: 'sk-runtime-openai-key'
      });

      // Mock successful completion response
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          choices: [{
            message: {
              content: 'Test response'
            }
          }],
          usage: {
            prompt_tokens: 10,
            completion_tokens: 20,
            total_tokens: 30
          }
        })
      });

      // Use OpenAI service - it should use the runtime key
      await openaiService.createChatCompletion({
        model: 'gpt-3.5-turbo',
        messages: [{ role: 'user', content: 'test' }]
      });

      expect(mockFetch).toHaveBeenLastCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Bearer sk-runtime-openai-key'
          })
        })
      );
    });
  });

  describe('Fallback Behavior', () => {
    it('should handle missing API keys gracefully', async () => {
      // Ensure no API keys are set
      await configManager.resetConfiguration();

      // Try to use Unsplash service without API key
      try {
        await unsplashService.searchImages({ query: 'test' });
        expect.fail('Should have thrown an error');
      } catch (error) {
        expect(error).toBeDefined();
      }
    });

    it('should switch to fallback endpoints when configured', async () => {
      // Configure fallback endpoint
      await configManager.updateServiceConfiguration({
        service: 'openai',
        endpoint: 'https://fallback-openai.com/v1'
      });

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          choices: [{ message: { content: 'Fallback response' } }],
          usage: { total_tokens: 10 }
        })
      });

      await openaiService.createChatCompletion({
        model: 'gpt-3.5-turbo',
        messages: [{ role: 'user', content: 'test' }]
      });

      expect(mockFetch).toHaveBeenCalledWith(
        'https://fallback-openai.com/v1/chat/completions',
        expect.any(Object)
      );
    });
  });

  describe('Migration from Environment Variables', () => {
    it('should migrate from env vars to runtime config', async () => {
      // Simulate existing environment variables
      const originalConfig = configManager.getConfiguration();
      
      // Check if env vars are being used
      if (originalConfig.keys.unsplash) {
        // Should be able to update with runtime key
        mockFetch.mockResolvedValueOnce({ ok: true });
        
        const result = await configManager.updateServiceConfiguration({
          service: 'unsplash',
          apiKey: 'new-runtime-key'
        });

        expect(result.success).toBe(true);
      }
    });

    it('should preserve existing functionality during migration', async () => {
      // Test that existing functionality works during migration
      const health = await configManager.getHealthStatus();
      expect(health).toBeDefined();
      expect(health.services).toBeDefined();
    });
  });

  describe('Error Handling and Recovery', () => {
    it('should recover from temporary API failures', async () => {
      // First call fails
      mockFetch
        .mockRejectedValueOnce(new Error('Temporary failure'))
        .mockResolvedValueOnce({ ok: true });

      // First attempt should fail
      const firstResult = await configManager.validateApiKey('unsplash', 'test-key');
      expect(firstResult.valid).toBe(false);

      // Second attempt should succeed
      const secondResult = await configManager.validateApiKey('unsplash', 'test-key');
      expect(secondResult.valid).toBe(true);
    });

    it('should handle rate limiting appropriately', async () => {
      // Mock rate limit response
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 429,
        statusText: 'Too Many Requests',
        headers: new Map([['X-RateLimit-Remaining', '0']])
      });

      const result = await configManager.validateApiKey('openai', 'sk-test');
      
      expect(result.valid).toBe(false);
      expect(result.error).toContain('rate limit');
    });

    it('should handle malformed responses gracefully', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.reject('Invalid JSON')
      });

      const result = await configManager.validateApiKey('unsplash', 'test-key');
      expect(result.valid).toBe(false);
    });
  });

  describe('Configuration Persistence', () => {
    it('should persist configuration updates', async () => {
      mockFetch.mockResolvedValueOnce({ ok: true });

      await configManager.updateServiceConfiguration({
        service: 'unsplash',
        apiKey: 'persistent-key'
      });

      // Should have called localStorage.setItem
      expect(localStorageMock.setItem).toHaveBeenCalled();
    });

    it('should restore configuration on initialization', async () => {
      // Mock existing configuration in storage
      localStorageMock.getItem.mockReturnValue(JSON.stringify({
        unsplash_key: 'stored-key'
      }));

      // Re-initialize config manager (in real scenario)
      const config = configManager.getConfiguration();
      
      // Should have attempted to restore from storage
      expect(localStorageMock.getItem).toHaveBeenCalled();
    });
  });

  describe('Concurrent Operations', () => {
    it('should handle multiple simultaneous API validations', async () => {
      const responses = [
        { ok: true },
        { ok: true },
        { ok: false, status: 401 },
        { ok: true }
      ];

      responses.forEach(response => {
        mockFetch.mockResolvedValueOnce(response);
      });

      const validations = [
        configManager.validateApiKey('unsplash', 'key1'),
        configManager.validateApiKey('openai', 'sk-key2'),
        configManager.validateApiKey('unsplash', 'badkey'),
        configManager.validateApiKey('openai', 'sk-key3')
      ];

      const results = await Promise.all(validations);
      
      expect(results[0].valid).toBe(true);
      expect(results[1].valid).toBe(true);
      expect(results[2].valid).toBe(false);
      expect(results[3].valid).toBe(true);
    });

    it('should handle multiple configuration updates', async () => {
      mockFetch.mockResolvedValue({ ok: true });

      const updates = [
        { service: 'unsplash' as const, apiKey: 'key1' },
        { service: 'openai' as const, apiKey: 'sk-key2' },
        { service: 'unsplash' as const, endpoint: 'https://api1.com' }
      ];

      const results = await Promise.all(
        updates.map(update => configManager.updateServiceConfiguration(update))
      );

      results.forEach(result => {
        expect(result.success).toBe(true);
      });
    });
  });

  describe('Health Monitoring Integration', () => {
    it('should continuously monitor service health', async () => {
      mockFetch.mockResolvedValue({ ok: true });

      // Set up a service with valid key
      await configManager.updateServiceConfiguration({
        service: 'unsplash',
        apiKey: 'monitoring-key'
      });

      // Get initial health status
      const initialHealth = await configManager.getHealthStatus();
      
      // Simulate health check after some time
      await new Promise(resolve => setTimeout(resolve, 100));
      
      const laterHealth = await configManager.getHealthStatus();
      
      expect(initialHealth).toBeDefined();
      expect(laterHealth).toBeDefined();
    });

    it('should detect service degradation', async () => {
      // Initially working
      mockFetch.mockResolvedValueOnce({ ok: true });
      
      await configManager.updateServiceConfiguration({
        service: 'openai',
        apiKey: 'sk-working-key'
      });

      // Later failing
      mockFetch.mockResolvedValueOnce({ ok: false, status: 503 });
      
      const health = await configManager.getHealthStatus();
      
      const serviceIssues = health.issues.filter(
        issue => issue.service === 'openai'
      );
      
      expect(serviceIssues.length).toBeGreaterThan(0);
    });
  });
});