import { RateLimitInfo } from '../types';

export interface RateLimiterConfig {
  windowMs: number; // Time window in milliseconds
  maxRequests: number; // Max requests per window
  minDelay: number; // Minimum delay between requests in milliseconds
  burstSize?: number; // Allow burst of requests
  skipOnError?: boolean; // Skip rate limiting on errors
}

export interface TokenBucket {
  capacity: number;
  tokens: number;
  refillRate: number; // tokens per second
  lastRefill: number;
}

class RateLimiter {
  private buckets: Map<string, TokenBucket> = new Map();
  private requestTimes: Map<string, number[]> = new Map();
  private configs: Map<string, RateLimiterConfig> = new Map();

  /**
   * Configure rate limiting for a service
   */
  configure(service: string, config: RateLimiterConfig): void {
    this.configs.set(service, config);
    
    // Initialize token bucket if not exists
    if (!this.buckets.has(service)) {
      this.buckets.set(service, {
        capacity: config.maxRequests,
        tokens: config.maxRequests,
        refillRate: config.maxRequests / (config.windowMs / 1000),
        lastRefill: Date.now()
      });
    }
  }

  /**
   * Acquire tokens for rate limiting - compatible with new interface
   */
  async acquire(service: string, tokens: number = 1): Promise<void> {
    const result = await this.checkRateLimit(service);
    if (!result.allowed) {
      const waitTime = result.retryAfter ? result.retryAfter * 1000 : 1000;
      throw new Error(`Rate limit exceeded for ${service}. Retry after ${result.retryAfter} seconds`);
    }
  }

  /**
   * Get current status - compatible with new interface
   */
  getStatus(service: string): { remaining: number; resetTime: number } {
    const status = this.getRateLimitStatus(service);
    return {
      remaining: status?.remaining || 0,
      resetTime: status?.reset?.getTime() || Date.now()
    };
  }

  /**
   * Check if a request can be made and consume a token
   */
  async checkRateLimit(service: string, endpoint?: string): Promise<{
    allowed: boolean;
    resetTime?: Date;
    retryAfter?: number;
  }> {
    const config = this.configs.get(service);
    if (!config) {
      return { allowed: true }; // No rate limiting configured
    }

    const key = endpoint ? `${service}:${endpoint}` : service;
    
    // Check token bucket
    const tokenResult = await this.checkTokenBucket(service);
    if (!tokenResult.allowed) {
      return tokenResult;
    }

    // Check sliding window
    const windowResult = this.checkSlidingWindow(key, config);
    if (!windowResult.allowed) {
      return windowResult;
    }

    // Check minimum delay
    const delayResult = await this.checkMinDelay(key, config);
    if (!delayResult.allowed) {
      return delayResult;
    }

    // Record successful request
    this.recordRequest(key);
    
    return { allowed: true };
  }

  /**
   * Token bucket algorithm implementation
   */
  private async checkTokenBucket(service: string): Promise<{
    allowed: boolean;
    resetTime?: Date;
    retryAfter?: number;
  }> {
    const bucket = this.buckets.get(service);
    if (!bucket) {
      return { allowed: true };
    }

    // Refill tokens based on time passed
    const now = Date.now();
    const timePassed = (now - bucket.lastRefill) / 1000; // seconds
    const tokensToAdd = Math.floor(timePassed * bucket.refillRate);
    
    if (tokensToAdd > 0) {
      bucket.tokens = Math.min(bucket.capacity, bucket.tokens + tokensToAdd);
      bucket.lastRefill = now;
    }

    // Check if we have tokens available
    if (bucket.tokens >= 1) {
      bucket.tokens -= 1;
      return { allowed: true };
    }

    // Calculate when next token will be available
    const timeUntilNextToken = (1 / bucket.refillRate) * 1000;
    const resetTime = new Date(now + timeUntilNextToken);
    
    return {
      allowed: false,
      resetTime,
      retryAfter: Math.ceil(timeUntilNextToken / 1000)
    };
  }

  /**
   * Sliding window rate limiting
   */
  private checkSlidingWindow(key: string, config: RateLimiterConfig): {
    allowed: boolean;
    resetTime?: Date;
    retryAfter?: number;
  } {
    const now = Date.now();
    const windowStart = now - config.windowMs;
    
    // Get or create request times array
    let requests = this.requestTimes.get(key) || [];
    
    // Remove requests outside the window
    requests = requests.filter(time => time > windowStart);
    this.requestTimes.set(key, requests);

    // Check if we can make another request
    if (requests.length < config.maxRequests) {
      return { allowed: true };
    }

    // Calculate when the oldest request will expire
    const oldestRequest = Math.min(...requests);
    const resetTime = new Date(oldestRequest + config.windowMs);
    const retryAfter = Math.ceil((resetTime.getTime() - now) / 1000);

    return {
      allowed: false,
      resetTime,
      retryAfter
    };
  }

  /**
   * Minimum delay between requests
   */
  private async checkMinDelay(key: string, config: RateLimiterConfig): Promise<{
    allowed: boolean;
    resetTime?: Date;
    retryAfter?: number;
  }> {
    const requests = this.requestTimes.get(key) || [];
    if (requests.length === 0) {
      return { allowed: true };
    }

    const lastRequest = Math.max(...requests);
    const timeSinceLastRequest = Date.now() - lastRequest;

    if (timeSinceLastRequest >= config.minDelay) {
      return { allowed: true };
    }

    const waitTime = config.minDelay - timeSinceLastRequest;
    
    // Wait for the minimum delay
    await this.delay(waitTime);
    
    return { allowed: true };
  }

  /**
   * Record a successful request
   */
  private recordRequest(key: string): void {
    const requests = this.requestTimes.get(key) || [];
    requests.push(Date.now());
    this.requestTimes.set(key, requests);
  }

  /**
   * Get current rate limit status
   */
  getRateLimitStatus(service: string, endpoint?: string): RateLimitInfo | null {
    const config = this.configs.get(service);
    if (!config) return null;

    const key = endpoint ? `${service}:${endpoint}` : service;
    const requests = this.requestTimes.get(key) || [];
    const now = Date.now();
    const windowStart = now - config.windowMs;
    
    // Count requests in current window
    const recentRequests = requests.filter(time => time > windowStart);
    const remaining = Math.max(0, config.maxRequests - recentRequests.length);
    
    // Calculate reset time
    const oldestRequest = recentRequests.length > 0 ? Math.min(...recentRequests) : now;
    const resetTime = new Date(oldestRequest + config.windowMs);

    return {
      limit: config.maxRequests,
      remaining,
      reset: resetTime,
      resetMs: resetTime.getTime() - now
    };
  }

  /**
   * Reset rate limiting for a service
   */
  reset(service: string, endpoint?: string): void {
    const key = endpoint ? `${service}:${endpoint}` : service;
    this.requestTimes.delete(key);
    
    if (!endpoint) {
      // Reset token bucket
      const config = this.configs.get(service);
      if (config) {
        this.buckets.set(service, {
          capacity: config.maxRequests,
          tokens: config.maxRequests,
          refillRate: config.maxRequests / (config.windowMs / 1000),
          lastRefill: Date.now()
        });
      }
    }
  }

  /**
   * Update rate limit from response headers
   */
  updateFromHeaders(service: string, headers: Headers): void {
    const limit = headers.get('X-RateLimit-Limit') || headers.get('RateLimit-Limit');
    const remaining = headers.get('X-RateLimit-Remaining') || headers.get('RateLimit-Remaining');
    const reset = headers.get('X-RateLimit-Reset') || headers.get('RateLimit-Reset');

    if (limit && remaining && reset) {
      const config = this.configs.get(service);
      if (config) {
        const bucket = this.buckets.get(service);
        if (bucket) {
          bucket.capacity = parseInt(limit, 10);
          bucket.tokens = parseInt(remaining, 10);
          
          // Parse reset time (could be Unix timestamp or seconds from now)
          const resetTime = parseInt(reset, 10);
          const resetDate = resetTime > 1000000000 ? 
            new Date(resetTime * 1000) : 
            new Date(Date.now() + resetTime * 1000);
          
          bucket.lastRefill = resetDate.getTime();
        }
      }
    }
  }

  /**
   * Check if service is currently rate limited
   */
  isRateLimited(service: string, endpoint?: string): boolean {
    const status = this.getRateLimitStatus(service, endpoint);
    return status ? status.remaining === 0 : false;
  }

  /**
   * Get time until rate limit resets
   */
  getTimeUntilReset(service: string, endpoint?: string): number {
    const status = this.getRateLimitStatus(service, endpoint);
    return status ? Math.max(0, status.resetMs) : 0;
  }

  /**
   * Clean up old request records
   */
  cleanup(): void {
    const now = Date.now();
    const maxAge = 24 * 60 * 60 * 1000; // 24 hours

    for (const [key, requests] of this.requestTimes.entries()) {
      const recentRequests = requests.filter(time => now - time < maxAge);
      if (recentRequests.length === 0) {
        this.requestTimes.delete(key);
      } else {
        this.requestTimes.set(key, recentRequests);
      }
    }
  }

  /**
   * Get statistics for monitoring
   */
  getStatistics(): {
    services: Record<string, {
      configured: boolean;
      currentRequests: number;
      tokensRemaining: number;
      nextReset: Date | null;
    }>;
    totalServices: number;
    totalRequests: number;
  } {
    const services: Record<string, any> = {};
    let totalRequests = 0;

    // Process configured services
    for (const [service] of this.configs.entries()) {
      const status = this.getRateLimitStatus(service);
      const bucket = this.buckets.get(service);
      
      services[service] = {
        configured: true,
        currentRequests: status ? status.limit - status.remaining : 0,
        tokensRemaining: bucket ? bucket.tokens : 0,
        nextReset: status ? status.reset : null
      };
      
      totalRequests += services[service].currentRequests;
    }

    return {
      services,
      totalServices: Object.keys(services).length,
      totalRequests
    };
  }

  /**
   * Utility delay function
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Export singleton instance
export const rateLimiter = new RateLimiter();

// Pre-configure common services
rateLimiter.configure('unsplash', {
  windowMs: 60 * 60 * 1000, // 1 hour
  maxRequests: 1000, // Unsplash demo limit
  minDelay: 1000, // 1 second between requests
  burstSize: 10
});

rateLimiter.configure('openai', {
  windowMs: 60 * 1000, // 1 minute
  maxRequests: 60, // Adjust based on your OpenAI plan
  minDelay: 1000, // 1 second between requests
  burstSize: 5
});

rateLimiter.configure('supabase', {
  windowMs: 60 * 1000, // 1 minute
  maxRequests: 100, // Conservative limit
  minDelay: 100, // 100ms between requests
  burstSize: 20
});

export { RateLimiter };