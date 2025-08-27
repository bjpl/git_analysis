/**
 * Configuration Manager for VocabLens
 * Handles runtime configuration updates, API key management, and service configuration
 */

import { apiConfig, validateConfiguration, ENVIRONMENT } from '../config/api';
import { ServiceName, Environment, ApiResponse, ValidationResult } from '../types/api';
import { envValidator, validateEnvironment } from './envValidator';
import { rateLimiter } from './rateLimiter';

export interface ConfigurationUpdate {
  service: ServiceName;
  apiKey?: string;
  endpoint?: string;
  rateLimit?: {
    windowMs?: number;
    maxRequests?: number;
    minDelay?: number;
  };
  features?: Record<string, boolean>;
  settings?: Record<string, any>;
}

export interface ServiceConfiguration {
  service: ServiceName;
  status: 'active' | 'inactive' | 'error';
  lastChecked: string;
  apiKeyStatus: 'valid' | 'invalid' | 'missing' | 'expired';
  rateLimit: {
    current: number;
    limit: number;
    resetTime: Date;
  };
  features: string[];
  endpoints: Record<string, string>;
  errors?: string[];
}

export interface ConfigurationHealth {
  overall: 'healthy' | 'degraded' | 'critical';
  services: Record<ServiceName, ServiceConfiguration>;
  environment: Environment;
  lastValidated: string;
  issues: Array<{
    severity: 'error' | 'warning' | 'info';
    service?: ServiceName;
    message: string;
    suggestion?: string;
  }>;
}

class ConfigManager {
  private config: typeof apiConfig;
  private validationCache: Map<string, ValidationResult> = new Map();
  private serviceStatus: Map<ServiceName, ServiceConfiguration> = new Map();
  private healthCheckInterval: NodeJS.Timeout | null = null;

  constructor() {
    this.config = { ...apiConfig };
    this.initializeServices();
    this.startHealthMonitoring();
  }

  /**
   * Get current configuration
   */
  getConfiguration(): typeof apiConfig {
    return { ...this.config };
  }

  /**
   * Update configuration for a specific service
   */
  async updateServiceConfiguration(updates: ConfigurationUpdate): Promise<ApiResponse<boolean>> {
    try {
      const { service, apiKey, endpoint, rateLimit: rateLimitConfig, features, settings } = updates;

      // Validate the update
      const validationResult = await this.validateConfigurationUpdate(updates);
      if (!validationResult.valid) {
        return {
          data: false,
          success: false,
          error: {
            code: 'INVALID_CONFIGURATION',
            message: 'Configuration update validation failed',
            details: validationResult.errors,
            service: 'app',
            statusCode: 400
          }
        };
      }

      // Apply API key update
      if (apiKey) {
        await this.updateApiKey(service, apiKey);
      }

      // Apply endpoint update
      if (endpoint) {
        await this.updateEndpoint(service, endpoint);
      }

      // Apply rate limiting update
      if (rateLimitConfig) {
        await this.updateRateLimit(service, rateLimitConfig);
      }

      // Apply feature flags update
      if (features) {
        await this.updateFeatures(service, features);
      }

      // Apply general settings update
      if (settings) {
        await this.updateSettings(service, settings);
      }

      // Refresh service status
      await this.refreshServiceStatus(service);

      return {
        data: true,
        success: true,
        meta: {
          timestamp: new Date().toISOString(),
          requestId: `config_${Date.now()}`,
          service: 'app'
        }
      };
    } catch (error) {
      return {
        data: false,
        success: false,
        error: {
          code: 'CONFIGURATION_UPDATE_FAILED',
          message: error instanceof Error ? error.message : 'Failed to update configuration',
          service: 'app',
          statusCode: 500
        }
      };
    }
  }

  /**
   * Validate API key for a service
   */
  async validateApiKey(service: ServiceName, apiKey: string): Promise<{
    valid: boolean;
    error?: string;
    details?: any;
  }> {
    try {
      switch (service) {
        case 'unsplash':
          return await this.validateUnsplashKey(apiKey);
        case 'openai':
          return await this.validateOpenAIKey(apiKey);
        case 'supabase':
          return await this.validateSupabaseKey(apiKey);
        case 'translate':
          return await this.validateTranslationKey(apiKey);
        default:
          return { valid: false, error: 'Unknown service' };
      }
    } catch (error) {
      return {
        valid: false,
        error: error instanceof Error ? error.message : 'Validation failed',
        details: error
      };
    }
  }

  /**
   * Get health status of all services
   */
  async getHealthStatus(): Promise<ConfigurationHealth> {
    const services: Record<ServiceName, ServiceConfiguration> = {} as any;
    const issues: ConfigurationHealth['issues'] = [];

    // Check each service
    for (const serviceName of ['unsplash', 'openai', 'supabase', 'translate'] as ServiceName[]) {
      try {
        const status = await this.getServiceStatus(serviceName);
        services[serviceName] = status;

        // Collect issues
        if (status.status === 'error') {
          issues.push({
            severity: 'error',
            service: serviceName,
            message: `${serviceName} service is not working`,
            suggestion: status.errors?.[0]
          });
        } else if (status.apiKeyStatus === 'invalid' || status.apiKeyStatus === 'missing') {
          issues.push({
            severity: status.apiKeyStatus === 'missing' ? 'error' : 'warning',
            service: serviceName,
            message: `${serviceName} API key is ${status.apiKeyStatus}`,
            suggestion: `Update ${serviceName} API key in configuration`
          });
        }

        // Check rate limiting
        if (status.rateLimit.current >= status.rateLimit.limit * 0.9) {
          issues.push({
            severity: 'warning',
            service: serviceName,
            message: `${serviceName} approaching rate limit`,
            suggestion: 'Consider upgrading your API plan or reducing request frequency'
          });
        }
      } catch (error) {
        services[serviceName] = {
          service: serviceName,
          status: 'error',
          lastChecked: new Date().toISOString(),
          apiKeyStatus: 'missing',
          rateLimit: { current: 0, limit: 0, resetTime: new Date() },
          features: [],
          endpoints: {},
          errors: [error instanceof Error ? error.message : 'Unknown error']
        };

        issues.push({
          severity: 'error',
          service: serviceName,
          message: `Failed to check ${serviceName} status`
        });
      }
    }

    // Determine overall health
    const errorCount = issues.filter(i => i.severity === 'error').length;
    const warningCount = issues.filter(i => i.severity === 'warning').length;

    let overall: ConfigurationHealth['overall'];
    if (errorCount > 0) {
      overall = 'critical';
    } else if (warningCount > 0) {
      overall = 'degraded';
    } else {
      overall = 'healthy';
    }

    return {
      overall,
      services,
      environment: ENVIRONMENT,
      lastValidated: new Date().toISOString(),
      issues
    };
  }

  /**
   * Reset configuration to defaults
   */
  async resetConfiguration(): Promise<void> {
    // Clear caches
    this.validationCache.clear();
    this.serviceStatus.clear();

    // Reset rate limiters
    rateLimiter.reset('unsplash');
    rateLimiter.reset('openai');
    rateLimiter.reset('supabase');
    rateLimiter.reset('translate');

    // Reinitialize with default config
    this.config = { ...apiConfig };
    await this.initializeServices();
  }

  /**
   * Export current configuration (for backup/debugging)
   */
  exportConfiguration(): {
    config: Partial<typeof apiConfig>;
    serviceStatus: Record<string, any>;
    metadata: {
      exportedAt: string;
      environment: Environment;
      version: string;
    };
  } {
    // Create safe config export (without sensitive data)
    const safeConfig = {
      app: this.config.app,
      endpoints: this.config.endpoints,
      rateLimit: this.config.rateLimit,
      features: this.config.features,
      images: this.config.images,
      ai: {
        ...this.config.ai,
        // Exclude sensitive data
        organizationId: this.config.ai.organizationId ? '[HIDDEN]' : undefined
      },
      vocabulary: this.config.vocabulary,
      security: this.config.security,
      storage: this.config.storage,
      performance: this.config.performance,
      ui: this.config.ui,
      development: this.config.development,
      environment: this.config.environment
    };

    const serviceStatus: Record<string, any> = {};
    for (const [service, status] of this.serviceStatus.entries()) {
      serviceStatus[service] = {
        ...status,
        // Remove sensitive information
        endpoints: Object.keys(status.endpoints).reduce((acc, key) => {
          acc[key] = '[ENDPOINT]';
          return acc;
        }, {} as Record<string, string>)
      };
    }

    return {
      config: safeConfig,
      serviceStatus,
      metadata: {
        exportedAt: new Date().toISOString(),
        environment: ENVIRONMENT,
        version: this.config.app.version
      }
    };
  }

  // Private methods

  private async initializeServices(): Promise<void> {
    // Initialize service status for all services
    const services: ServiceName[] = ['unsplash', 'openai', 'supabase', 'translate'];
    
    for (const service of services) {
      await this.refreshServiceStatus(service);
    }
  }

  private async validateConfigurationUpdate(updates: ConfigurationUpdate): Promise<ValidationResult> {
    const errors: ValidationResult['errors'] = [];
    const warnings: ValidationResult['warnings'] = [];

    // Validate API key if provided
    if (updates.apiKey) {
      const keyValidation = await this.validateApiKey(updates.service, updates.apiKey);
      if (!keyValidation.valid) {
        errors.push({
          field: 'apiKey',
          message: keyValidation.error || 'Invalid API key'
        });
      }
    }

    // Validate endpoint if provided
    if (updates.endpoint) {
      try {
        new URL(updates.endpoint);
      } catch {
        errors.push({
          field: 'endpoint',
          message: 'Invalid endpoint URL format'
        });
      }
    }

    // Validate rate limiting config
    if (updates.rateLimit) {
      const { windowMs, maxRequests, minDelay } = updates.rateLimit;
      
      if (windowMs && (windowMs < 1000 || windowMs > 3600000)) {
        errors.push({
          field: 'rateLimit.windowMs',
          message: 'Window must be between 1 second and 1 hour'
        });
      }

      if (maxRequests && (maxRequests < 1 || maxRequests > 10000)) {
        errors.push({
          field: 'rateLimit.maxRequests',
          message: 'Max requests must be between 1 and 10000'
        });
      }

      if (minDelay && (minDelay < 0 || minDelay > 60000)) {
        errors.push({
          field: 'rateLimit.minDelay',
          message: 'Min delay must be between 0 and 60 seconds'
        });
      }
    }

    return {
      valid: errors.length === 0,
      errors,
      warnings,
      environment: ENVIRONMENT
    };
  }

  private async updateApiKey(service: ServiceName, apiKey: string): Promise<void> {
    // Update in-memory configuration
    switch (service) {
      case 'unsplash':
        this.config.keys.unsplash = apiKey;
        break;
      case 'openai':
        this.config.keys.openai = apiKey;
        break;
      // Supabase and translate keys would need special handling
    }
  }

  private async updateEndpoint(service: ServiceName, endpoint: string): Promise<void> {
    // Update service endpoint
    switch (service) {
      case 'unsplash':
        this.config.endpoints.unsplash.base = endpoint;
        break;
      case 'openai':
        this.config.endpoints.openai.base = endpoint;
        break;
    }
  }

  private async updateRateLimit(service: ServiceName, config: NonNullable<ConfigurationUpdate['rateLimit']>): Promise<void> {
    // Update rate limiter configuration
    rateLimiter.configure(service, {
      windowMs: config.windowMs || 60000,
      maxRequests: config.maxRequests || 100,
      minDelay: config.minDelay || 1000
    });
  }

  private async updateFeatures(service: ServiceName, features: Record<string, boolean>): Promise<void> {
    // Update feature flags
    Object.assign(this.config.features, features);
  }

  private async updateSettings(service: ServiceName, settings: Record<string, any>): Promise<void> {
    // Update service-specific settings
    switch (service) {
      case 'openai':
        if (settings.model && this.config.ai.supportedModels.includes(settings.model)) {
          this.config.ai.defaultModel = settings.model;
        }
        if (typeof settings.temperature === 'number') {
          this.config.ai.temperature = Math.max(0, Math.min(2, settings.temperature));
        }
        break;
      case 'unsplash':
        if (settings.defaultSize && this.config.images.supportedSizes.includes(settings.defaultSize)) {
          this.config.images.defaultSize = settings.defaultSize;
        }
        break;
    }
  }

  private async getServiceStatus(service: ServiceName): Promise<ServiceConfiguration> {
    const cached = this.serviceStatus.get(service);
    if (cached && Date.now() - new Date(cached.lastChecked).getTime() < 300000) { // 5 minutes cache
      return cached;
    }

    return await this.refreshServiceStatus(service);
  }

  private async refreshServiceStatus(service: ServiceName): Promise<ServiceConfiguration> {
    const status: ServiceConfiguration = {
      service,
      status: 'inactive',
      lastChecked: new Date().toISOString(),
      apiKeyStatus: 'missing',
      rateLimit: { current: 0, limit: 0, resetTime: new Date() },
      features: [],
      endpoints: {},
      errors: []
    };

    try {
      // Check API key status
      const hasApiKey = this.hasApiKey(service);
      if (!hasApiKey) {
        status.apiKeyStatus = 'missing';
        status.errors?.push('API key is missing');
      } else {
        const keyValidation = await this.validateApiKey(service, this.getApiKey(service)!);
        status.apiKeyStatus = keyValidation.valid ? 'valid' : 'invalid';
        if (!keyValidation.valid) {
          status.errors?.push(keyValidation.error || 'API key validation failed');
        }
      }

      // Check rate limiting status
      const rateLimitStatus = rateLimiter.getRateLimitStatus(service);
      if (rateLimitStatus) {
        status.rateLimit = {
          current: rateLimitStatus.limit - rateLimitStatus.remaining,
          limit: rateLimitStatus.limit,
          resetTime: rateLimitStatus.reset
        };
      }

      // Set overall status
      if (status.apiKeyStatus === 'valid') {
        status.status = 'active';
      } else if (status.errors && status.errors.length > 0) {
        status.status = 'error';
      }

      // Get service features
      status.features = this.getServiceFeatures(service);

      // Get service endpoints
      status.endpoints = this.getServiceEndpoints(service);

    } catch (error) {
      status.status = 'error';
      status.errors?.push(error instanceof Error ? error.message : 'Unknown error');
    }

    this.serviceStatus.set(service, status);
    return status;
  }

  private hasApiKey(service: ServiceName): boolean {
    switch (service) {
      case 'unsplash':
        return !!this.config.keys.unsplash;
      case 'openai':
        return !!this.config.keys.openai;
      case 'supabase':
        return !!this.config.supabase.anonKey;
      case 'translate':
        return !!(this.config.translation.googleTranslate.apiKey || this.config.translation.deepl.apiKey);
      default:
        return false;
    }
  }

  private getApiKey(service: ServiceName): string | null {
    switch (service) {
      case 'unsplash':
        return this.config.keys.unsplash;
      case 'openai':
        return this.config.keys.openai;
      case 'supabase':
        return this.config.supabase.anonKey;
      case 'translate':
        return this.config.translation.googleTranslate.apiKey || this.config.translation.deepl.apiKey || null;
      default:
        return null;
    }
  }

  private getServiceFeatures(service: ServiceName): string[] {
    const features: Record<ServiceName, string[]> = {
      unsplash: ['image-search', 'random-images', 'download-tracking'],
      openai: ['chat-completion', 'text-generation', 'vocabulary-generation'],
      supabase: ['database', 'auth', 'storage', 'realtime'],
      translate: ['text-translation', 'language-detection']
    };

    return features[service] || [];
  }

  private getServiceEndpoints(service: ServiceName): Record<string, string> {
    switch (service) {
      case 'unsplash':
        return this.config.endpoints.unsplash;
      case 'openai':
        return this.config.endpoints.openai;
      default:
        return {};
    }
  }

  // API key validation methods
  private async validateUnsplashKey(apiKey: string): Promise<{ valid: boolean; error?: string; details?: any }> {
    try {
      const response = await fetch(`${this.config.endpoints.unsplash.base}/me`, {
        headers: { 'Authorization': `Client-ID ${apiKey}` }
      });
      return { valid: response.ok };
    } catch (error) {
      return { valid: false, error: 'Network error', details: error };
    }
  }

  private async validateOpenAIKey(apiKey: string): Promise<{ valid: boolean; error?: string; details?: any }> {
    try {
      const response = await fetch(`${this.config.endpoints.openai.base}/models`, {
        headers: { 'Authorization': `Bearer ${apiKey}` }
      });
      return { valid: response.ok };
    } catch (error) {
      return { valid: false, error: 'Network error', details: error };
    }
  }

  private async validateSupabaseKey(apiKey: string): Promise<{ valid: boolean; error?: string; details?: any }> {
    // Basic format validation for Supabase keys
    if (apiKey.length < 100) {
      return { valid: false, error: 'Key too short' };
    }
    return { valid: true };
  }

  private async validateTranslationKey(apiKey: string): Promise<{ valid: boolean; error?: string; details?: any }> {
    // Basic format validation
    if (apiKey.length < 20) {
      return { valid: false, error: 'Key too short' };
    }
    return { valid: true };
  }

  private startHealthMonitoring(): void {
    // Run health check every 15 minutes
    this.healthCheckInterval = setInterval(async () => {
      try {
        await this.getHealthStatus();
      } catch (error) {
        console.error('Health check failed:', error);
      }
    }, 15 * 60 * 1000);
  }

  /**
   * Stop health monitoring
   */
  stopHealthMonitoring(): void {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
      this.healthCheckInterval = null;
    }
  }
}

// Export singleton instance
export const configManager = new ConfigManager();

export default ConfigManager;