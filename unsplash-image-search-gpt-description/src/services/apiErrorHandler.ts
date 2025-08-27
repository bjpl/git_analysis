import { AppError, DetailedAppError, ValidationError } from '../types';

export interface ErrorHandlerConfig {
  enableLogging: boolean;
  enableUserFriendlyMessages: boolean;
  enableRetryableErrors: boolean;
  maxRetryAttempts: number;
  enableErrorReporting: boolean;
  sentryDsn?: string;
}

export interface ErrorContext {
  service: 'unsplash' | 'openai' | 'supabase' | 'app';
  operation: string;
  endpoint?: string;
  requestId?: string;
  userId?: string;
  metadata?: Record<string, any>;
}

class APIErrorHandler {
  private config: ErrorHandlerConfig;
  private errorCounts: Map<string, number> = new Map();
  private lastErrors: Map<string, Date> = new Map();

  constructor(config?: Partial<ErrorHandlerConfig>) {
    this.config = {
      enableLogging: true,
      enableUserFriendlyMessages: true,
      enableRetryableErrors: true,
      maxRetryAttempts: 3,
      enableErrorReporting: true,
      ...config
    };
  }

  /**
   * Handle and transform errors from different services
   */
  handleError(
    error: any, 
    context: ErrorContext
  ): DetailedAppError {
    const errorId = this.generateErrorId();
    const transformedError = this.transformError(error, context, errorId);
    
    // Log error if enabled
    if (this.config.enableLogging) {
      this.logError(transformedError, context);
    }

    // Report error for monitoring if enabled
    if (this.config.enableErrorReporting) {
      this.reportError(transformedError, context);
    }

    // Track error frequency
    this.trackErrorFrequency(transformedError.code);

    return transformedError;
  }

  /**
   * Transform raw errors into standardized DetailedAppError
   */
  private transformError(
    error: any, 
    context: ErrorContext, 
    correlationId: string
  ): DetailedAppError {
    let baseError: DetailedAppError;

    // Handle different error types
    if (error instanceof Error) {
      baseError = this.handleJavaScriptError(error, context);
    } else if (this.isHttpError(error)) {
      baseError = this.handleHttpError(error, context);
    } else if (this.isSupabaseError(error)) {
      baseError = this.handleSupabaseError(error, context);
    } else if (typeof error === 'string') {
      baseError = this.handleStringError(error, context);
    } else {
      baseError = this.handleUnknownError(error, context);
    }

    // Add common properties
    baseError.correlationId = correlationId;
    baseError.timestamp = new Date().toISOString();
    baseError.context = {
      ...baseError.context,
      service: context.service,
      operation: context.operation,
      endpoint: context.endpoint,
      requestId: context.requestId,
      userId: context.userId,
      ...context.metadata
    };

    // Add user-friendly messages
    if (this.config.enableUserFriendlyMessages) {
      baseError.userMessage = this.getUserFriendlyMessage(baseError);
      baseError.suggestions = this.getSuggestions(baseError);
      baseError.documentation = this.getDocumentationLink(baseError);
    }

    return baseError;
  }

  /**
   * Handle JavaScript Error instances
   */
  private handleJavaScriptError(error: Error, context: ErrorContext): DetailedAppError {
    const isNetworkError = this.isNetworkError(error);
    const isTimeoutError = this.isTimeoutError(error);
    const isAbortError = this.isAbortError(error);

    return {
      code: isNetworkError ? 'NETWORK_ERROR' : 
            isTimeoutError ? 'TIMEOUT_ERROR' :
            isAbortError ? 'REQUEST_CANCELLED' : 'JAVASCRIPT_ERROR',
      message: error.message,
      details: {
        name: error.name,
        stack: error.stack
      },
      timestamp: new Date().toISOString(),
      recoverable: isNetworkError || isTimeoutError,
      retryable: isNetworkError || isTimeoutError,
      statusCode: isNetworkError ? 0 : undefined,
      service: context.service,
      endpoint: context.endpoint,
      technicalMessage: `${error.name}: ${error.message}`,
      stack: error.stack
    };
  }

  /**
   * Handle HTTP errors (fetch responses)
   */
  private handleHttpError(error: any, context: ErrorContext): DetailedAppError {
    const status = error.status || error.statusCode || 500;
    const message = error.message || error.statusText || 'Unknown HTTP error';

    return {
      code: this.getHttpErrorCode(status),
      message,
      details: error.data || error.body || {},
      timestamp: new Date().toISOString(),
      recoverable: this.isRecoverableHttpError(status),
      retryable: this.isRetryableHttpError(status),
      statusCode: status,
      service: context.service,
      endpoint: context.endpoint,
      technicalMessage: `HTTP ${status}: ${message}`,
      retryAfter: error.retryAfter || this.getRetryDelay(status)
    };
  }

  /**
   * Handle Supabase-specific errors
   */
  private handleSupabaseError(error: any, context: ErrorContext): DetailedAppError {
    const code = error.code || 'SUPABASE_ERROR';
    const message = error.message || 'Supabase operation failed';

    return {
      code: this.mapSupabaseErrorCode(code),
      message,
      details: {
        hint: error.hint,
        details: error.details,
        code: error.code
      },
      timestamp: new Date().toISOString(),
      recoverable: this.isRecoverableSupabaseError(code),
      retryable: this.isRetryableSupabaseError(code),
      service: context.service,
      endpoint: context.endpoint,
      technicalMessage: `Supabase Error ${code}: ${message}`,
      validationErrors: this.extractValidationErrors(error)
    };
  }

  /**
   * Handle string errors
   */
  private handleStringError(error: string, context: ErrorContext): DetailedAppError {
    return {
      code: 'STRING_ERROR',
      message: error,
      details: {},
      timestamp: new Date().toISOString(),
      recoverable: false,
      service: context.service,
      endpoint: context.endpoint,
      technicalMessage: error
    };
  }

  /**
   * Handle unknown error types
   */
  private handleUnknownError(error: any, context: ErrorContext): DetailedAppError {
    return {
      code: 'UNKNOWN_ERROR',
      message: 'An unknown error occurred',
      details: { originalError: error },
      timestamp: new Date().toISOString(),
      recoverable: false,
      service: context.service,
      endpoint: context.endpoint,
      technicalMessage: `Unknown error: ${JSON.stringify(error)}`
    };
  }

  /**
   * Generate user-friendly error messages
   */
  private getUserFriendlyMessage(error: DetailedAppError): string {
    const messageMap: Record<string, string> = {
      'NETWORK_ERROR': 'Unable to connect to the service. Please check your internet connection and try again.',
      'TIMEOUT_ERROR': 'The request took too long to complete. Please try again.',
      'RATE_LIMIT_EXCEEDED': 'Too many requests. Please wait a moment and try again.',
      'UNAUTHORIZED': 'Please check your API keys in the settings.',
      'FORBIDDEN': 'You don\'t have permission to perform this action.',
      'NOT_FOUND': 'The requested resource was not found.',
      'BAD_REQUEST': 'There was a problem with your request. Please check the input and try again.',
      'SERVER_ERROR': 'There was a problem with the server. Please try again later.',
      'SERVICE_UNAVAILABLE': 'The service is temporarily unavailable. Please try again later.'
    };

    return messageMap[error.code] || 'An unexpected error occurred. Please try again.';
  }

  /**
   * Generate actionable suggestions for users
   */
  private getSuggestions(error: DetailedAppError): string[] {
    const suggestions: Record<string, string[]> = {
      'NETWORK_ERROR': [
        'Check your internet connection',
        'Try refreshing the page',
        'Disable any VPN or proxy'
      ],
      'UNAUTHORIZED': [
        'Verify your API keys in settings',
        'Check if your API keys have expired',
        'Ensure you have the correct permissions'
      ],
      'RATE_LIMIT_EXCEEDED': [
        'Wait a few minutes before trying again',
        'Consider upgrading your API plan',
        'Reduce the frequency of requests'
      ],
      'TIMEOUT_ERROR': [
        'Try again with a smaller request',
        'Check your internet connection speed',
        'Wait a moment and retry'
      ]
    };

    return suggestions[error.code] || ['Try refreshing the page or contact support'];
  }

  /**
   * Get documentation links for errors
   */
  private getDocumentationLink(error: DetailedAppError): string | undefined {
    const docLinks: Record<string, string> = {
      'UNAUTHORIZED': '/docs/api-setup',
      'RATE_LIMIT_EXCEEDED': '/docs/rate-limits',
      'BAD_REQUEST': '/docs/api-usage'
    };

    return docLinks[error.code];
  }

  /**
   * Check if an error is retryable
   */
  isRetryable(error: DetailedAppError): boolean {
    if (!this.config.enableRetryableErrors) {
      return false;
    }

    const retryableCodes = [
      'NETWORK_ERROR',
      'TIMEOUT_ERROR',
      'RATE_LIMIT_EXCEEDED',
      'SERVER_ERROR',
      'SERVICE_UNAVAILABLE'
    ];

    return error.retryable || retryableCodes.includes(error.code);
  }

  /**
   * Get retry delay based on error type and attempt count
   */
  getRetryDelay(error: DetailedAppError, attemptCount: number): number {
    if (error.retryAfter) {
      return error.retryAfter * 1000; // Convert to milliseconds
    }

    // Exponential backoff with jitter
    const baseDelay = 1000; // 1 second
    const maxDelay = 30000; // 30 seconds
    const exponentialDelay = Math.min(baseDelay * Math.pow(2, attemptCount), maxDelay);
    const jitter = Math.random() * 1000; // Add up to 1 second of jitter

    return exponentialDelay + jitter;
  }

  /**
   * Check if we should retry based on attempt count
   */
  shouldRetry(error: DetailedAppError, attemptCount: number): boolean {
    return this.isRetryable(error) && attemptCount < this.config.maxRetryAttempts;
  }

  /**
   * Create a circuit breaker pattern for error handling
   */
  checkCircuitBreaker(service: string, endpoint: string): boolean {
    const key = `${service}:${endpoint}`;
    const errorCount = this.errorCounts.get(key) || 0;
    const lastError = this.lastErrors.get(key);

    // If we have too many errors in a short time, open the circuit
    if (errorCount >= 5 && lastError && (Date.now() - lastError.getTime()) < 60000) {
      return false; // Circuit is open
    }

    return true; // Circuit is closed
  }

  /**
   * Reset circuit breaker for a service/endpoint
   */
  resetCircuitBreaker(service: string, endpoint: string): void {
    const key = `${service}:${endpoint}`;
    this.errorCounts.delete(key);
    this.lastErrors.delete(key);
  }

  /**
   * Private helper methods
   */
  private generateErrorId(): string {
    return `err_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private isNetworkError(error: Error): boolean {
    return error.name === 'TypeError' && error.message.includes('fetch');
  }

  private isTimeoutError(error: Error): boolean {
    return error.name === 'TimeoutError' || error.message.includes('timeout');
  }

  private isAbortError(error: Error): boolean {
    return error.name === 'AbortError';
  }

  private isHttpError(error: any): boolean {
    return error && typeof error.status === 'number';
  }

  private isSupabaseError(error: any): boolean {
    return error && (error.code || error.hint);
  }

  private getHttpErrorCode(status: number): string {
    const statusMap: Record<number, string> = {
      400: 'BAD_REQUEST',
      401: 'UNAUTHORIZED',
      403: 'FORBIDDEN',
      404: 'NOT_FOUND',
      429: 'RATE_LIMIT_EXCEEDED',
      500: 'SERVER_ERROR',
      502: 'BAD_GATEWAY',
      503: 'SERVICE_UNAVAILABLE',
      504: 'GATEWAY_TIMEOUT'
    };

    return statusMap[status] || 'HTTP_ERROR';
  }

  private isRecoverableHttpError(status: number): boolean {
    return [429, 500, 502, 503, 504].includes(status);
  }

  private isRetryableHttpError(status: number): boolean {
    return [429, 500, 502, 503, 504].includes(status);
  }

  private getRetryDelay(status: number): number {
    const delayMap: Record<number, number> = {
      429: 60, // 1 minute for rate limit
      500: 5,  // 5 seconds for server error
      502: 10, // 10 seconds for bad gateway
      503: 30, // 30 seconds for service unavailable
      504: 15  // 15 seconds for gateway timeout
    };

    return delayMap[status] || 5;
  }

  private mapSupabaseErrorCode(code: string): string {
    const codeMap: Record<string, string> = {
      'PGRST301': 'UNAUTHORIZED',
      'PGRST302': 'FORBIDDEN',
      'PGRST116': 'NOT_FOUND',
      'PGRST204': 'BAD_REQUEST',
      '23505': 'DUPLICATE_ENTRY',
      '23503': 'FOREIGN_KEY_VIOLATION',
      '23502': 'NOT_NULL_VIOLATION'
    };

    return codeMap[code] || 'SUPABASE_ERROR';
  }

  private isRecoverableSupabaseError(code: string): boolean {
    const recoverableCodes = ['PGRST301', 'PGRST302', 'PGRST204'];
    return recoverableCodes.includes(code);
  }

  private isRetryableSupabaseError(code: string): boolean {
    return false; // Most Supabase errors are not retryable
  }

  private extractValidationErrors(error: any): ValidationError[] | undefined {
    if (!error.details) return undefined;

    // Try to parse validation errors from different formats
    const errors: ValidationError[] = [];
    
    if (Array.isArray(error.details)) {
      error.details.forEach((detail: any) => {
        errors.push({
          field: detail.field || 'unknown',
          message: detail.message || 'Validation failed',
          code: detail.code || 'VALIDATION_ERROR',
          value: detail.value
        });
      });
    }

    return errors.length > 0 ? errors : undefined;
  }

  private trackErrorFrequency(code: string): void {
    const currentCount = this.errorCounts.get(code) || 0;
    this.errorCounts.set(code, currentCount + 1);
    this.lastErrors.set(code, new Date());
  }

  private logError(error: DetailedAppError, context: ErrorContext): void {
    const logData = {
      error: {
        code: error.code,
        message: error.message,
        correlationId: error.correlationId,
        statusCode: error.statusCode,
        service: error.service,
        endpoint: error.endpoint
      },
      context,
      timestamp: error.timestamp
    };

    if (error.statusCode && error.statusCode >= 500) {
      console.error('API Error:', logData);
    } else {
      console.warn('API Warning:', logData);
    }
  }

  private reportError(error: DetailedAppError, context: ErrorContext): void {
    // This would typically send to an error monitoring service like Sentry
    // For now, we'll just log it
    if (this.config.sentryDsn) {
      // Sentry.captureException(error, { contexts: { context } });
    }
  }

  /**
   * Get error statistics
   */
  getErrorStatistics(): {
    errorCounts: Record<string, number>;
    totalErrors: number;
    recentErrors: Array<{ code: string; timestamp: Date }>;
  } {
    const totalErrors = Array.from(this.errorCounts.values()).reduce((sum, count) => sum + count, 0);
    const recentErrors = Array.from(this.lastErrors.entries()).map(([code, timestamp]) => ({
      code,
      timestamp
    }));

    return {
      errorCounts: Object.fromEntries(this.errorCounts),
      totalErrors,
      recentErrors
    };
  }

  /**
   * Clear error tracking data
   */
  clearErrorTracking(): void {
    this.errorCounts.clear();
    this.lastErrors.clear();
  }
}

// Export singleton instance
export const apiErrorHandler = new APIErrorHandler();

// Export class for custom configurations
export { APIErrorHandler };

// Utility functions
export const ErrorUtils = {
  /**
   * Create a standardized error response
   */
  createErrorResponse(error: DetailedAppError) {
    return {
      success: false,
      error: {
        code: error.code,
        message: error.userMessage || error.message,
        details: error.details,
        correlationId: error.correlationId,
        suggestions: error.suggestions,
        documentation: error.documentation
      },
      meta: {
        timestamp: error.timestamp,
        retryable: error.retryable,
        service: error.service
      }
    };
  },

  /**
   * Check if an error is user-facing
   */
  isUserFacingError(error: DetailedAppError): boolean {
    const userFacingCodes = [
      'BAD_REQUEST',
      'UNAUTHORIZED',
      'FORBIDDEN',
      'NOT_FOUND',
      'RATE_LIMIT_EXCEEDED'
    ];
    
    return userFacingCodes.includes(error.code);
  },

  /**
   * Format error for display
   */
  formatErrorForDisplay(error: DetailedAppError): string {
    if (error.userMessage) {
      return error.userMessage;
    }

    // Fallback to technical message with some user-friendly formatting
    return error.message.charAt(0).toUpperCase() + error.message.slice(1);
  }
};