/**
 * Unit Tests for Configuration Manager
 * Tests the ConfigManager class and its methods for runtime API configuration
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { configManager } from '../../src/services/configManager';
import type { ConfigurationUpdate, ServiceConfiguration, ConfigurationHealth } from '../../src/services/configManager';

// Mock the API config
vi.mock('../../src/config/api', () => ({
  apiConfig: {
    app: { name: 'VocabLens', version: '1.0.0' },
    keys: { unsplash: '', openai: '' },
    endpoints: {
      unsplash: { base: 'https://api.unsplash.com', search: '/search/photos' },
      openai: { base: 'https://api.openai.com/v1', completions: '/chat/completions' }
    },
    rateLimit: { windowMs: 60000, maxRequests: 100, minDelay: 1000 },
    features: {},
    images: { supportedSizes: ['thumb', 'small', 'regular', 'full'] },
    ai: { 
      supportedModels: ['gpt-3.5-turbo', 'gpt-4'],
      defaultModel: 'gpt-3.5-turbo',
      temperature: 0.7
    },
    vocabulary: {},
    security: {},
    storage: {},
    performance: {},
    ui: {},
    development: {},
    environment: 'development',
    supabase: { anonKey: '' },
    translation: { googleTranslate: { apiKey: '' }, deepl: { apiKey: '' } }
  },
  validateConfiguration: vi.fn(),
  ENVIRONMENT: 'development'
}));

// Mock the rate limiter
vi.mock('../../src/services/rateLimiter', () => ({
  rateLimiter: {
    configure: vi.fn(),
    reset: vi.fn(),
    getRateLimitStatus: vi.fn(() => ({
      limit: 100,
      remaining: 90,
      reset: new Date()
    }))
  }
}));

// Mock fetch for API validation tests
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe('ConfigManager', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockFetch.mockClear();
  });

  afterEach(() => {
    configManager.stopHealthMonitoring();
  });

  describe('getConfiguration', () => {
    it('should return current configuration', () => {
      const config = configManager.getConfiguration();
      expect(config).toBeDefined();
      expect(config.app.name).toBe('VocabLens');
    });

    it('should return a copy of configuration (immutable)', () => {
      const config1 = configManager.getConfiguration();
      const config2 = configManager.getConfiguration();
      
      expect(config1).not.toBe(config2); // Different object references
      expect(config1).toEqual(config2); // Same content
    });
  });

  describe('updateServiceConfiguration', () => {
    it('should update API key successfully', async () => {
      mockFetch.mockResolvedValueOnce({ ok: true });
      
      const update: ConfigurationUpdate = {
        service: 'unsplash',
        apiKey: 'new_unsplash_key_123'
      };

      const result = await configManager.updateServiceConfiguration(update);
      
      expect(result.success).toBe(true);
      expect(result.data).toBe(true);
    });

    it('should update endpoint successfully', async () => {
      const update: ConfigurationUpdate = {
        service: 'openai',
        endpoint: 'https://custom-openai-endpoint.com/v1'
      };

      const result = await configManager.updateServiceConfiguration(update);
      
      expect(result.success).toBe(true);
    });

    it('should update rate limit configuration', async () => {
      const update: ConfigurationUpdate = {
        service: 'unsplash',
        rateLimit: {
          windowMs: 120000,
          maxRequests: 200,
          minDelay: 500
        }
      };

      const result = await configManager.updateServiceConfiguration(update);
      
      expect(result.success).toBe(true);
    });

    it('should update feature flags', async () => {
      const update: ConfigurationUpdate = {
        service: 'unsplash',
        features: {
          enableAdvancedSearch: true,
          enableImageFilters: false
        }
      };

      const result = await configManager.updateServiceConfiguration(update);
      
      expect(result.success).toBe(true);
    });

    it('should reject invalid API key', async () => {
      mockFetch.mockResolvedValueOnce({ ok: false, status: 401 });
      
      const update: ConfigurationUpdate = {
        service: 'unsplash',
        apiKey: 'invalid_key'
      };

      const result = await configManager.updateServiceConfiguration(update);
      
      expect(result.success).toBe(false);
      expect(result.error?.code).toBe('INVALID_CONFIGURATION');
    });

    it('should reject invalid endpoint URL', async () => {
      const update: ConfigurationUpdate = {
        service: 'openai',
        endpoint: 'not-a-valid-url'
      };

      const result = await configManager.updateServiceConfiguration(update);
      
      expect(result.success).toBe(false);
      expect(result.error?.message).toContain('validation failed');
    });

    it('should reject invalid rate limit values', async () => {
      const update: ConfigurationUpdate = {
        service: 'unsplash',
        rateLimit: {
          windowMs: 500, // Too low
          maxRequests: 20000, // Too high
          minDelay: -1 // Negative
        }
      };

      const result = await configManager.updateServiceConfiguration(update);
      
      expect(result.success).toBe(false);
      expect(result.error?.details).toBeDefined();
    });
  });

  describe('validateApiKey', () => {
    it('should validate Unsplash API key', async () => {
      mockFetch.mockResolvedValueOnce({ ok: true });
      
      const result = await configManager.validateApiKey('unsplash', 'valid_unsplash_key');
      
      expect(result.valid).toBe(true);
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/me'),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': expect.stringContaining('Client-ID')
          })
        })
      );
    });

    it('should validate OpenAI API key', async () => {
      mockFetch.mockResolvedValueOnce({ ok: true });
      
      const result = await configManager.validateApiKey('openai', 'sk-valid-openai-key');
      
      expect(result.valid).toBe(true);
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/models'),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': expect.stringContaining('Bearer')
          })
        })
      );
    });

    it('should handle network errors gracefully', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));
      
      const result = await configManager.validateApiKey('unsplash', 'test_key');
      
      expect(result.valid).toBe(false);
      expect(result.error).toContain('Network error');
    });

    it('should reject invalid service', async () => {
      const result = await configManager.validateApiKey('invalid_service' as any, 'test_key');
      
      expect(result.valid).toBe(false);
      expect(result.error).toBe('Unknown service');
    });
  });

  describe('getHealthStatus', () => {
    it('should return comprehensive health status', async () => {
      mockFetch
        .mockResolvedValueOnce({ ok: true }) // Unsplash validation
        .mockResolvedValueOnce({ ok: true }) // OpenAI validation
        .mockResolvedValueOnce({ ok: true }) // Supabase validation
        .mockResolvedValueOnce({ ok: true }); // Translation validation

      const health = await configManager.getHealthStatus();
      
      expect(health.overall).toBeDefined();
      expect(health.services).toBeDefined();
      expect(health.environment).toBe('development');
      expect(health.lastValidated).toBeDefined();
      expect(health.issues).toBeInstanceOf(Array);
    });

    it('should identify missing API keys', async () => {
      const health = await configManager.getHealthStatus();
      
      const missingKeyIssues = health.issues.filter(
        issue => issue.message.includes('missing')
      );
      
      expect(missingKeyIssues.length).toBeGreaterThan(0);
    });

    it('should identify invalid API keys', async () => {
      mockFetch.mockResolvedValue({ ok: false, status: 401 });
      
      const health = await configManager.getHealthStatus();
      
      const invalidKeyIssues = health.issues.filter(
        issue => issue.message.includes('invalid')
      );
      
      expect(invalidKeyIssues.length).toBeGreaterThan(0);
    });

    it('should warn about approaching rate limits', async () => {
      // Mock rate limiter to return high usage
      const { rateLimiter } = await import('../../src/services/rateLimiter');
      (rateLimiter.getRateLimitStatus as any).mockReturnValue({
        limit: 100,
        remaining: 5, // Only 5 remaining out of 100
        reset: new Date()
      });

      const health = await configManager.getHealthStatus();
      
      const rateLimitIssues = health.issues.filter(
        issue => issue.message.includes('rate limit')
      );
      
      expect(rateLimitIssues.length).toBeGreaterThan(0);
    });

    it('should categorize overall health correctly', async () => {
      // Test healthy state
      mockFetch.mockResolvedValue({ ok: true });
      let health = await configManager.getHealthStatus();
      
      // Should be degraded or critical due to missing keys, not healthy
      expect(['degraded', 'critical']).toContain(health.overall);
    });
  });

  describe('resetConfiguration', () => {
    it('should reset configuration to defaults', async () => {
      // First update something
      await configManager.updateServiceConfiguration({
        service: 'unsplash',
        apiKey: 'test_key'
      });

      // Then reset
      await configManager.resetConfiguration();

      const config = configManager.getConfiguration();
      expect(config.keys.unsplash).toBe('');
    });
  });

  describe('exportConfiguration', () => {
    it('should export safe configuration without sensitive data', () => {
      const exported = configManager.exportConfiguration();
      
      expect(exported.config).toBeDefined();
      expect(exported.serviceStatus).toBeDefined();
      expect(exported.metadata).toBeDefined();
      
      expect(exported.metadata.exportedAt).toBeDefined();
      expect(exported.metadata.environment).toBe('development');
      expect(exported.metadata.version).toBe('1.0.0');
    });

    it('should hide sensitive information in export', () => {
      const exported = configManager.exportConfiguration();
      
      // Check that sensitive data is hidden
      expect(JSON.stringify(exported)).not.toContain('sk-');
      expect(JSON.stringify(exported)).not.toContain('Client-ID');
    });
  });
});

describe('Configuration Validation', () => {
  it('should validate configuration update structure', async () => {
    const invalidUpdate = {
      service: 'invalid_service',
      apiKey: null
    } as any;

    const result = await configManager.updateServiceConfiguration(invalidUpdate);
    expect(result.success).toBe(false);
  });

  it('should validate rate limit boundaries', async () => {
    const updates = [
      { windowMs: 500 }, // Too low
      { windowMs: 4000000 }, // Too high
      { maxRequests: 0 }, // Too low
      { maxRequests: 20000 }, // Too high
      { minDelay: -1 }, // Negative
      { minDelay: 80000 } // Too high
    ];

    for (const rateLimit of updates) {
      const result = await configManager.updateServiceConfiguration({
        service: 'unsplash',
        rateLimit
      });
      
      expect(result.success).toBe(false);
    }
  });

  it('should validate endpoint URLs', async () => {
    const invalidEndpoints = [
      'not-a-url',
      'http://invalid',
      'ftp://wrong-protocol.com',
      ''
    ];

    for (const endpoint of invalidEndpoints) {
      const result = await configManager.updateServiceConfiguration({
        service: 'openai',
        endpoint
      });
      
      expect(result.success).toBe(false);
    }
  });
});

describe('Error Handling', () => {
  it('should handle API validation network failures', async () => {
    mockFetch.mockRejectedValue(new Error('Network failure'));
    
    const result = await configManager.validateApiKey('unsplash', 'test_key');
    
    expect(result.valid).toBe(false);
    expect(result.error).toBeDefined();
  });

  it('should handle malformed API responses', async () => {
    mockFetch.mockResolvedValue({
      ok: false,
      status: 500,
      json: () => Promise.reject('Invalid JSON')
    });
    
    const result = await configManager.validateApiKey('openai', 'sk-test');
    
    expect(result.valid).toBe(false);
  });

  it('should handle timeout scenarios', async () => {
    // Mock a long-running request
    mockFetch.mockImplementation(() => new Promise(resolve => {
      setTimeout(() => resolve({ ok: true }), 10000);
    }));
    
    const startTime = Date.now();
    const result = await configManager.validateApiKey('unsplash', 'test_key');
    const endTime = Date.now();
    
    // Should timeout quickly, not wait for the full 10 seconds
    expect(endTime - startTime).toBeLessThan(5000);
    expect(result.valid).toBe(false);
  });
});

describe('Concurrent Operations', () => {
  it('should handle multiple simultaneous configuration updates', async () => {
    mockFetch.mockResolvedValue({ ok: true });
    
    const updates = [
      { service: 'unsplash' as const, apiKey: 'key1' },
      { service: 'openai' as const, apiKey: 'sk-key2' },
      { service: 'unsplash' as const, endpoint: 'https://api1.com' },
      { service: 'openai' as const, endpoint: 'https://api2.com' }
    ];

    const promises = updates.map(update => 
      configManager.updateServiceConfiguration(update)
    );

    const results = await Promise.all(promises);
    
    results.forEach(result => {
      expect(result).toBeDefined();
    });
  });

  it('should handle concurrent API key validations', async () => {
    mockFetch.mockResolvedValue({ ok: true });
    
    const validations = [
      configManager.validateApiKey('unsplash', 'key1'),
      configManager.validateApiKey('openai', 'sk-key2'),
      configManager.validateApiKey('unsplash', 'key3'),
      configManager.validateApiKey('openai', 'sk-key4')
    ];

    const results = await Promise.all(validations);
    
    expect(results).toHaveLength(4);
    results.forEach(result => {
      expect(result.valid).toBe(true);
    });
  });
});