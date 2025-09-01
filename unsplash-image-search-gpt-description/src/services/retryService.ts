/**
 * Advanced retry service with circuit breaker pattern
 * Provides resilient API call handling with exponential backoff
 */

export interface RetryPolicy {
  maxRetries: number;
  baseDelay: number;
  maxDelay: number;
  backoffMultiplier: number;
  jitter: boolean;
  retryableStatusCodes: number[];
}

export interface CircuitBreakerConfig {
  failureThreshold: number;
  recoveryTimeout: number;
  monitoringPeriod: number;
}

export type CircuitBreakerState = 'CLOSED' | 'OPEN' | 'HALF_OPEN';

export class CircuitBreaker {
  private state: CircuitBreakerState = 'CLOSED';
  private failureCount = 0;
  private lastFailureTime = 0;
  private successCount = 0;

  constructor(private config: CircuitBreakerConfig) {}

  async execute<T>(operation: () => Promise<T>): Promise<T> {
    if (this.state === 'OPEN') {
      if (Date.now() - this.lastFailureTime > this.config.recoveryTimeout) {
        this.state = 'HALF_OPEN';
        this.successCount = 0;
      } else {
        throw new Error('Circuit breaker is OPEN - operation rejected');
      }
    }

    try {
      const result = await operation();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  getState(): CircuitBreakerState {
    return this.state;
  }

  getMetrics() {
    return {
      state: this.state,
      failureCount: this.failureCount,
      lastFailureTime: this.lastFailureTime,
      successCount: this.successCount
    };
  }

  reset(): void {
    this.state = 'CLOSED';
    this.failureCount = 0;
    this.lastFailureTime = 0;
    this.successCount = 0;
  }

  private onSuccess(): void {
    if (this.state === 'HALF_OPEN') {
      this.successCount++;
      if (this.successCount >= 3) {
        this.state = 'CLOSED';
        this.failureCount = 0;
      }
    } else {
      this.failureCount = Math.max(0, this.failureCount - 1);
    }
  }

  private onFailure(): void {
    this.failureCount++;
    this.lastFailureTime = Date.now();

    if (this.failureCount >= this.config.failureThreshold) {
      this.state = 'OPEN';
    }
  }
}

export async function retryWithBackoff<T>(
  operation: () => Promise<T>,
  policy: RetryPolicy
): Promise<T> {
  let lastError: Error | null = null;

  for (let attempt = 0; attempt <= policy.maxRetries; attempt++) {
    try {
      return await operation();
    } catch (error) {
      lastError = error as Error;

      // Don't retry if it's the last attempt
      if (attempt === policy.maxRetries) {
        break;
      }

      // Check if error is retryable
      if (error instanceof Error && 'status' in error) {
        const status = (error as any).status;
        if (!policy.retryableStatusCodes.includes(status)) {
          throw error; // Don't retry non-retryable errors
        }
      }

      // Calculate delay with exponential backoff
      let delay = policy.baseDelay * Math.pow(policy.backoffMultiplier, attempt);
      delay = Math.min(delay, policy.maxDelay);

      // Add jitter to prevent thundering herd
      if (policy.jitter) {
        delay *= 0.5 + Math.random() * 0.5;
      }

      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }

  throw lastError || new Error('Operation failed after all retry attempts');
}

export class ExponentialBackoff {
  private attempts = 0;
  private baseDelay: number;
  private maxDelay: number;
  private multiplier: number;
  private jitter: boolean;

  constructor(
    baseDelay = 1000,
    maxDelay = 30000,
    multiplier = 2,
    jitter = true
  ) {
    this.baseDelay = baseDelay;
    this.maxDelay = maxDelay;
    this.multiplier = multiplier;
    this.jitter = jitter;
  }

  async wait(): Promise<void> {
    let delay = this.baseDelay * Math.pow(this.multiplier, this.attempts);
    delay = Math.min(delay, this.maxDelay);

    if (this.jitter) {
      delay *= 0.5 + Math.random() * 0.5;
    }

    this.attempts++;
    await new Promise(resolve => setTimeout(resolve, delay));
  }

  reset(): void {
    this.attempts = 0;
  }

  getAttempts(): number {
    return this.attempts;
  }
}

/**
 * Retry decorator for methods
 */
export function withRetry(policy: RetryPolicy) {
  return function (target: any, propertyName: string, descriptor: PropertyDescriptor) {
    const method = descriptor.value;

    descriptor.value = async function (...args: any[]) {
      return retryWithBackoff(() => method.apply(this, args), policy);
    };

    return descriptor;
  };
}

/**
 * Circuit breaker decorator for methods
 */
export function withCircuitBreaker(config: CircuitBreakerConfig) {
  const circuitBreaker = new CircuitBreaker(config);

  return function (target: any, propertyName: string, descriptor: PropertyDescriptor) {
    const method = descriptor.value;

    descriptor.value = async function (...args: any[]) {
      return circuitBreaker.execute(() => method.apply(this, args));
    };

    return descriptor;
  };
}

// Default retry policies for different service types
export const DEFAULT_RETRY_POLICIES: Record<string, RetryPolicy> = {
  api: {
    maxRetries: 3,
    baseDelay: 1000,
    maxDelay: 10000,
    backoffMultiplier: 2,
    jitter: true,
    retryableStatusCodes: [408, 429, 500, 502, 503, 504]
  },
  
  critical: {
    maxRetries: 5,
    baseDelay: 500,
    maxDelay: 15000,
    backoffMultiplier: 1.5,
    jitter: true,
    retryableStatusCodes: [408, 429, 500, 502, 503, 504]
  },
  
  background: {
    maxRetries: 10,
    baseDelay: 2000,
    maxDelay: 60000,
    backoffMultiplier: 2,
    jitter: true,
    retryableStatusCodes: [408, 429, 500, 502, 503, 504]
  }
};

// Default circuit breaker configurations
export const DEFAULT_CIRCUIT_BREAKER_CONFIGS: Record<string, CircuitBreakerConfig> = {
  api: {
    failureThreshold: 5,
    recoveryTimeout: 30000,
    monitoringPeriod: 60000
  },
  
  critical: {
    failureThreshold: 3,
    recoveryTimeout: 60000,
    monitoringPeriod: 120000
  },
  
  background: {
    failureThreshold: 10,
    recoveryTimeout: 15000,
    monitoringPeriod: 30000
  }
};