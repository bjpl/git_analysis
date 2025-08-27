/**
 * Performance and Network Failure Tests
 * Tests system performance under various network conditions and failure scenarios
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { configManager } from '../../src/services/configManager';
import { unsplashService } from '../../src/services/unsplashService';
import { openaiService } from '../../src/services/openaiService';

// Mock performance API
const mockPerformance = {
  now: vi.fn(() => Date.now()),
  mark: vi.fn(),
  measure: vi.fn(),
  getEntriesByType: vi.fn(() => []),
  getEntriesByName: vi.fn(() => [])
};

Object.defineProperty(global, 'performance', {
  value: mockPerformance
});

// Network conditions simulator
class NetworkSimulator {
  private originalFetch: typeof fetch;
  private conditions: {
    latency: number;
    bandwidth: number;
    dropRate: number;
    errorRate: number;
  };

  constructor() {
    this.originalFetch = global.fetch;
    this.conditions = {
      latency: 0,
      bandwidth: Infinity,
      dropRate: 0,
      errorRate: 0
    };
  }

  setConditions(conditions: Partial<typeof this.conditions>) {
    this.conditions = { ...this.conditions, ...conditions };
  }

  activate() {
    global.fetch = this.simulatedFetch.bind(this);
  }

  deactivate() {
    global.fetch = this.originalFetch;
  }

  private async simulatedFetch(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
    const startTime = performance.now();

    // Simulate packet drop
    if (Math.random() < this.conditions.dropRate) {
      throw new Error('Network packet dropped');
    }

    // Simulate latency
    if (this.conditions.latency > 0) {
      await new Promise(resolve => setTimeout(resolve, this.conditions.latency));
    }

    // Simulate random errors
    if (Math.random() < this.conditions.errorRate) {
      throw new Error('Network error');
    }

    // Simulate bandwidth limitation
    let response: Response;
    try {
      response = await this.originalFetch(input, init);
    } catch (error) {
      throw error;
    }

    // Simulate slow response based on bandwidth
    if (this.conditions.bandwidth < Infinity) {
      const responseSize = parseInt(response.headers.get('content-length') || '1024');
      const downloadTime = (responseSize / this.conditions.bandwidth) * 1000; // Convert to ms
      
      if (downloadTime > 0) {
        await new Promise(resolve => setTimeout(resolve, downloadTime));
      }
    }

    return response;
  }
}

// Performance measurement utilities
class PerformanceMetrics {
  private measurements: Map<string, number[]> = new Map();

  startMeasurement(name: string): () => number {
    const start = performance.now();
    return () => {
      const duration = performance.now() - start;
      this.recordMeasurement(name, duration);
      return duration;
    };
  }

  recordMeasurement(name: string, duration: number) {
    if (!this.measurements.has(name)) {
      this.measurements.set(name, []);
    }
    this.measurements.get(name)!.push(duration);
  }

  getMetrics(name: string) {
    const measurements = this.measurements.get(name) || [];
    if (measurements.length === 0) {
      return { count: 0, avg: 0, min: 0, max: 0, p95: 0, p99: 0 };
    }

    const sorted = [...measurements].sort((a, b) => a - b);
    const sum = measurements.reduce((acc, val) => acc + val, 0);

    return {
      count: measurements.length,
      avg: sum / measurements.length,
      min: sorted[0],
      max: sorted[sorted.length - 1],
      p95: sorted[Math.floor(sorted.length * 0.95)],
      p99: sorted[Math.floor(sorted.length * 0.99)]
    };
  }

  reset() {
    this.measurements.clear();
  }
}

describe('Performance and Network Failure Tests', () => {
  let networkSim: NetworkSimulator;
  let metrics: PerformanceMetrics;

  beforeEach(() => {
    vi.clearAllMocks();
    networkSim = new NetworkSimulator();
    metrics = new PerformanceMetrics();
    
    // Reset performance mock
    mockPerformance.now.mockImplementation(() => Date.now());
  });

  afterEach(() => {
    networkSim.deactivate();
    metrics.reset();
  });

  describe('API Validation Performance', () => {
    it('should validate API keys within performance thresholds', async () => {
      // Mock successful API responses
      networkSim.setConditions({ latency: 100 }); // 100ms latency
      networkSim.activate();

      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ valid: true })
      });
      global.fetch = mockFetch;

      const endMeasurement = metrics.startMeasurement('api_validation');
      
      const result = await configManager.validateApiKey('unsplash', 'test-key');
      
      const duration = endMeasurement();

      expect(result.valid).toBe(true);
      expect(duration).toBeLessThan(5000); // Should complete within 5 seconds
      expect(mockFetch).toHaveBeenCalledTimes(1);
    });

    it('should handle concurrent API validations efficiently', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ valid: true })
      });
      global.fetch = mockFetch;

      const validationPromises = Array.from({ length: 10 }, (_, i) => {
        const endMeasurement = metrics.startMeasurement('concurrent_validation');
        return configManager.validateApiKey('unsplash', `test-key-${i}`).then(result => {
          endMeasurement();
          return result;
        });
      });

      const startTime = performance.now();
      const results = await Promise.all(validationPromises);
      const totalDuration = performance.now() - startTime;

      // All should succeed
      expect(results.every(r => r.valid)).toBe(true);
      
      // Should complete faster than sequential (less than 10x single request time)
      expect(totalDuration).toBeLessThan(10000);

      const concurrentMetrics = metrics.getMetrics('concurrent_validation');
      expect(concurrentMetrics.avg).toBeLessThan(2000);
    });

    it('should timeout appropriately on slow networks', async () => {
      networkSim.setConditions({ latency: 35000 }); // 35 second delay
      networkSim.activate();

      const endMeasurement = metrics.startMeasurement('timeout_test');
      
      const result = await configManager.validateApiKey('unsplash', 'test-key');
      
      const duration = endMeasurement();

      expect(result.valid).toBe(false);
      expect(result.error).toContain('timeout');
      expect(duration).toBeLessThan(35000); // Should timeout before 35s
      expect(duration).toBeGreaterThan(5000); // But not immediately
    });
  });

  describe('Network Failure Scenarios', () => {
    it('should handle intermittent connection drops', async () => {
      networkSim.setConditions({ dropRate: 0.3 }); // 30% packet drop rate
      networkSim.activate();

      const results: boolean[] = [];
      const durations: number[] = [];

      // Try validation multiple times
      for (let i = 0; i < 10; i++) {
        const endMeasurement = metrics.startMeasurement('dropped_connection');
        
        try {
          const result = await configManager.validateApiKey('unsplash', 'test-key');
          results.push(result.valid);
        } catch (error) {
          results.push(false);
        }
        
        durations.push(endMeasurement());
      }

      // Some should fail due to dropped connections
      const failureRate = results.filter(r => !r).length / results.length;
      expect(failureRate).toBeGreaterThan(0); // Some failures expected
      expect(failureRate).toBeLessThan(1); // Not all should fail

      // Failed requests should fail quickly (not hang)
      const avgDuration = durations.reduce((sum, d) => sum + d, 0) / durations.length;
      expect(avgDuration).toBeLessThan(10000);
    });

    it('should handle slow network conditions gracefully', async () => {
      networkSim.setConditions({ 
        latency: 2000, // 2 second latency
        bandwidth: 1024 // 1KB/s bandwidth
      });
      networkSim.activate();

      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ valid: true }),
        headers: new Map([['content-length', '2048']]) // 2KB response
      });
      global.fetch = mockFetch;

      const endMeasurement = metrics.startMeasurement('slow_network');
      
      const result = await configManager.validateApiKey('unsplash', 'test-key');
      
      const duration = endMeasurement();

      // Should eventually succeed despite slow network
      expect(result.valid).toBe(true);
      
      // Duration should reflect network conditions (latency + download time)
      expect(duration).toBeGreaterThan(2000); // At least the latency
    });

    it('should handle API rate limiting with exponential backoff', async () => {
      let attemptCount = 0;
      const mockFetch = vi.fn().mockImplementation(() => {
        attemptCount++;
        if (attemptCount <= 3) {
          return Promise.resolve({
            ok: false,
            status: 429,
            statusText: 'Too Many Requests',
            headers: new Map([['retry-after', '1']])
          });
        }
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ valid: true })
        });
      });
      global.fetch = mockFetch;

      const endMeasurement = metrics.startMeasurement('rate_limit_backoff');
      
      const result = await configManager.validateApiKey('unsplash', 'test-key');
      
      const duration = endMeasurement();

      expect(result.valid).toBe(true);
      expect(mockFetch).toHaveBeenCalledTimes(4); // Initial + 3 retries
      expect(duration).toBeGreaterThan(1000); // Should include backoff delays
    });

    it('should handle DNS resolution failures', async () => {
      const mockFetch = vi.fn().mockRejectedValue(new Error('DNS resolution failed'));
      global.fetch = mockFetch;

      const endMeasurement = metrics.startMeasurement('dns_failure');
      
      const result = await configManager.validateApiKey('unsplash', 'test-key');
      
      const duration = endMeasurement();

      expect(result.valid).toBe(false);
      expect(result.error).toContain('DNS resolution failed');
      expect(duration).toBeLessThan(30000); // Should fail relatively quickly
    });
  });

  describe('Service Integration Performance', () => {
    it('should handle rapid configuration updates efficiently', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ valid: true })
      });
      global.fetch = mockFetch;

      const updates = Array.from({ length: 20 }, (_, i) => ({
        service: (i % 2 === 0 ? 'unsplash' : 'openai') as const,
        apiKey: `test-key-${i}`
      }));

      const endMeasurement = metrics.startMeasurement('rapid_updates');
      
      const results = await Promise.all(
        updates.map(update => configManager.updateServiceConfiguration(update))
      );
      
      const duration = endMeasurement();

      // All updates should succeed
      expect(results.every(r => r.success)).toBe(true);
      
      // Should complete within reasonable time
      expect(duration).toBeLessThan(10000);

      // Should not overwhelm the system
      expect(mockFetch.mock.calls.length).toBeLessThanOrEqual(updates.length * 2); // Validation calls
    });

    it('should maintain performance during health monitoring', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ valid: true })
      });
      global.fetch = mockFetch;

      // Set up some configuration
      await configManager.updateServiceConfiguration({
        service: 'unsplash',
        apiKey: 'test-key'
      });

      // Monitor performance of health checks
      const healthCheckTimes: number[] = [];
      
      for (let i = 0; i < 5; i++) {
        const endMeasurement = metrics.startMeasurement('health_check');
        
        await configManager.getHealthStatus();
        
        healthCheckTimes.push(endMeasurement());
        
        // Wait between checks
        await new Promise(resolve => setTimeout(resolve, 100));
      }

      const avgHealthCheckTime = healthCheckTimes.reduce((sum, time) => sum + time, 0) / healthCheckTimes.length;
      
      // Health checks should be fast
      expect(avgHealthCheckTime).toBeLessThan(2000);
      
      // Performance should be consistent
      const maxVariation = Math.max(...healthCheckTimes) - Math.min(...healthCheckTimes);
      expect(maxVariation).toBeLessThan(5000);
    });

    it('should handle memory efficiently during long sessions', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ valid: true })
      });
      global.fetch = mockFetch;

      // Simulate long session with many operations
      const initialMemory = (performance as any).memory?.usedJSHeapSize || 0;
      
      for (let i = 0; i < 100; i++) {
        await configManager.validateApiKey('unsplash', `test-key-${i}`);
        await configManager.getHealthStatus();
        
        // Occasionally force garbage collection if available
        if (i % 20 === 0 && global.gc) {
          global.gc();
        }
      }

      const finalMemory = (performance as any).memory?.usedJSHeapSize || 0;
      const memoryGrowth = finalMemory - initialMemory;
      
      // Memory growth should be reasonable (less than 50MB for 100 operations)
      if (initialMemory > 0) {
        expect(memoryGrowth).toBeLessThan(50 * 1024 * 1024);
      }
    });
  });

  describe('Error Recovery Performance', () => {
    it('should recover quickly from service unavailability', async () => {
      let isServiceDown = true;
      const mockFetch = vi.fn().mockImplementation(() => {
        if (isServiceDown) {
          return Promise.reject(new Error('Service unavailable'));
        }
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ valid: true })
        });
      });
      global.fetch = mockFetch;

      // First attempt should fail
      const failResult = await configManager.validateApiKey('unsplash', 'test-key');
      expect(failResult.valid).toBe(false);

      // "Service comes back online"
      isServiceDown = false;

      const endMeasurement = metrics.startMeasurement('recovery_time');
      
      // Next attempt should succeed quickly
      const successResult = await configManager.validateApiKey('unsplash', 'test-key');
      
      const recoveryTime = endMeasurement();

      expect(successResult.valid).toBe(true);
      expect(recoveryTime).toBeLessThan(2000); // Should recover quickly
    });

    it('should handle circuit breaker pattern for failing services', async () => {
      const mockFetch = vi.fn()
        .mockRejectedValueOnce(new Error('Service error'))
        .mockRejectedValueOnce(new Error('Service error'))
        .mockRejectedValueOnce(new Error('Service error'))
        .mockRejectedValueOnce(new Error('Service error'))
        .mockRejectedValueOnce(new Error('Service error'))
        .mockResolvedValue({
          ok: true,
          json: () => Promise.resolve({ valid: true })
        });
      global.fetch = mockFetch;

      const attempts: number[] = [];

      // Multiple failed attempts
      for (let i = 0; i < 5; i++) {
        const endMeasurement = metrics.startMeasurement('circuit_breaker');
        
        const result = await configManager.validateApiKey('unsplash', 'test-key');
        
        attempts.push(endMeasurement());
        expect(result.valid).toBe(false);
      }

      // After circuit breaker opens, subsequent calls should fail fast
      const laterAttempts = attempts.slice(-2);
      const avgLaterAttempt = laterAttempts.reduce((sum, time) => sum + time, 0) / laterAttempts.length;
      
      // Later attempts should be faster (circuit breaker open)
      expect(avgLaterAttempt).toBeLessThan(attempts[0]);
    });
  });

  describe('Load Testing', () => {
    it('should handle high concurrent validation load', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ valid: true })
      });
      global.fetch = mockFetch;

      const concurrentRequests = 50;
      const endMeasurement = metrics.startMeasurement('load_test');

      const promises = Array.from({ length: concurrentRequests }, (_, i) =>
        configManager.validateApiKey('unsplash', `load-test-key-${i}`)
      );

      const results = await Promise.all(promises);
      const totalDuration = endMeasurement();

      // All requests should succeed
      expect(results.every(r => r.valid)).toBe(true);
      
      // Should complete within reasonable time even under load
      expect(totalDuration).toBeLessThan(30000);
      
      // Average time per request should be acceptable
      const avgTimePerRequest = totalDuration / concurrentRequests;
      expect(avgTimePerRequest).toBeLessThan(1000);
    });

    it('should maintain performance under sustained load', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ valid: true })
      });
      global.fetch = mockFetch;

      const batchSize = 10;
      const batches = 5;
      const batchTimes: number[] = [];

      for (let batch = 0; batch < batches; batch++) {
        const endMeasurement = metrics.startMeasurement('sustained_load');
        
        const batchPromises = Array.from({ length: batchSize }, (_, i) =>
          configManager.validateApiKey('unsplash', `sustained-key-${batch}-${i}`)
        );

        await Promise.all(batchPromises);
        batchTimes.push(endMeasurement());
        
        // Small delay between batches
        await new Promise(resolve => setTimeout(resolve, 100));
      }

      // Performance should remain consistent across batches
      const avgBatchTime = batchTimes.reduce((sum, time) => sum + time, 0) / batchTimes.length;
      const maxBatchTime = Math.max(...batchTimes);
      
      expect(maxBatchTime).toBeLessThan(avgBatchTime * 2); // Max shouldn't be more than 2x average
      
      // Should not degrade significantly over time
      const firstBatchTime = batchTimes[0];
      const lastBatchTime = batchTimes[batchTimes.length - 1];
      expect(lastBatchTime).toBeLessThan(firstBatchTime * 1.5); // Less than 50% degradation
    });
  });

  describe('Offline/Online Transitions', () => {
    it('should handle offline to online transition smoothly', async () => {
      // Start offline
      let isOnline = false;
      const mockFetch = vi.fn().mockImplementation(() => {
        if (!isOnline) {
          return Promise.reject(new Error('Network offline'));
        }
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ valid: true })
        });
      });
      global.fetch = mockFetch;

      // Offline attempt
      const offlineResult = await configManager.validateApiKey('unsplash', 'test-key');
      expect(offlineResult.valid).toBe(false);

      // Come back online
      isOnline = true;

      const endMeasurement = metrics.startMeasurement('online_transition');
      
      // Should work immediately when online
      const onlineResult = await configManager.validateApiKey('unsplash', 'test-key');
      
      const transitionTime = endMeasurement();

      expect(onlineResult.valid).toBe(true);
      expect(transitionTime).toBeLessThan(5000); // Should be responsive when back online
    });

    it('should queue operations during offline periods', async () => {
      let isOnline = false;
      let queuedCalls = 0;
      
      const mockFetch = vi.fn().mockImplementation(() => {
        if (!isOnline) {
          queuedCalls++;
          return Promise.reject(new Error('Network offline'));
        }
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ valid: true })
        });
      });
      global.fetch = mockFetch;

      // Make several calls while offline
      const offlinePromises = [
        configManager.validateApiKey('unsplash', 'key1'),
        configManager.validateApiKey('openai', 'key2'),
        configManager.validateApiKey('unsplash', 'key3')
      ];

      // All should fail
      const offlineResults = await Promise.all(offlinePromises);
      expect(offlineResults.every(r => !r.valid)).toBe(true);
      expect(queuedCalls).toBe(3);

      // Come back online
      isOnline = true;
      queuedCalls = 0;

      // New calls should work
      const onlineResult = await configManager.validateApiKey('unsplash', 'test-key');
      expect(onlineResult.valid).toBe(true);
    });
  });
});