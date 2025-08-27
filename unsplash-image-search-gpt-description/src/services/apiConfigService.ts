/**
 * API Configuration Service
 * Manages secure storage and validation of API keys
 */

import { encryptString, decryptString } from '../utils/encryption';
import { 
  ApiKeys, 
  ApiConfiguration, 
  ApiKeyStatus, 
  ValidationResult, 
  EncryptedApiData, 
  ApiProviderName 
} from '../types/api';

const STORAGE_KEY = 'vocablens_api_config';
const CONFIG_VERSION = '1.0.0';

class ApiConfigService {
  private config: ApiConfiguration | null = null;
  private isInitialized = false;

  /**
   * Initialize the service and load existing configuration
   */
  async initialize(): Promise<void> {
    if (this.isInitialized) return;
    
    try {
      await this.loadConfiguration();
    } catch (error) {
      console.warn('Failed to load API configuration:', error);
      this.config = this.createDefaultConfiguration();
    }
    
    this.isInitialized = true;
  }

  /**
   * Creates a default empty configuration
   */
  private createDefaultConfiguration(): ApiConfiguration {
    return {
      keys: {
        unsplash: null,
        openai: null
      },
      status: {
        unsplash: { isValid: false, isConfigured: false },
        openai: { isValid: false, isConfigured: false }
      }
    };
  }

  /**
   * Load configuration from encrypted storage
   */
  private async loadConfiguration(): Promise<void> {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) {
      this.config = this.createDefaultConfiguration();
      return;
    }

    try {
      const encryptedData: EncryptedApiData = JSON.parse(stored);
      const decrypted = await decryptString(encryptedData);
      const parsedConfig = JSON.parse(decrypted);
      
      // Validate configuration structure
      if (this.isValidConfiguration(parsedConfig)) {
        this.config = parsedConfig;
      } else {
        throw new Error('Invalid configuration structure');
      }
    } catch (error) {
      console.error('Failed to decrypt API configuration:', error);
      throw error;
    }
  }

  /**
   * Save configuration to encrypted storage
   */
  private async saveConfiguration(): Promise<void> {
    if (!this.config) return;

    try {
      const serialized = JSON.stringify(this.config);
      const encrypted = await encryptString(serialized);
      
      const encryptedData: EncryptedApiData = {
        ...encrypted,
        timestamp: Date.now()
      };
      
      localStorage.setItem(STORAGE_KEY, JSON.stringify(encryptedData));
    } catch (error) {
      console.error('Failed to save API configuration:', error);
      throw error;
    }
  }

  /**
   * Validates configuration structure
   */
  private isValidConfiguration(config: any): config is ApiConfiguration {
    return (
      config &&
      typeof config === 'object' &&
      config.keys &&
      typeof config.keys === 'object' &&
      config.status &&
      typeof config.status === 'object'
    );
  }

  /**
   * Get all API keys (decrypted)
   */
  async getApiKeys(): Promise<ApiKeys> {
    await this.initialize();
    return { ...this.config!.keys };
  }

  /**
   * Get a specific API key
   */
  async getApiKey(provider: ApiProviderName): Promise<string | null> {
    await this.initialize();
    return this.config!.keys[provider];
  }

  /**
   * Set an API key for a provider
   */
  async setApiKey(provider: ApiProviderName, apiKey: string | null): Promise<void> {
    await this.initialize();
    
    this.config!.keys[provider] = apiKey;
    this.config!.status[provider] = {
      isValid: false,
      isConfigured: apiKey !== null && apiKey.trim() !== '',
      error: undefined
    };

    await this.saveConfiguration();
  }

  /**
   * Get API configuration status
   */
  async getConfiguration(): Promise<ApiConfiguration> {
    await this.initialize();
    return JSON.parse(JSON.stringify(this.config!)); // Deep clone
  }

  /**
   * Get status for a specific provider
   */
  async getProviderStatus(provider: ApiProviderName): Promise<ApiKeyStatus> {
    await this.initialize();
    return { ...this.config!.status[provider] };
  }

  /**
   * Validate an API key against its service
   */
  async validateApiKey(provider: ApiProviderName, apiKey?: string): Promise<ValidationResult> {
    const keyToValidate = apiKey || await this.getApiKey(provider);
    
    if (!keyToValidate) {
      return { isValid: false, error: 'No API key provided' };
    }

    try {
      let result: ValidationResult;

      switch (provider) {
        case 'unsplash':
          result = await this.validateUnsplashKey(keyToValidate);
          break;
        case 'openai':
          result = await this.validateOpenAIKey(keyToValidate);
          break;
        default:
          result = { isValid: false, error: 'Unknown provider' };
      }

      // Update status if this was for a stored key
      if (!apiKey) {
        await this.updateProviderStatus(provider, result);
      }

      return result;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      return { isValid: false, error: errorMessage };
    }
  }

  /**
   * Update provider status after validation
   */
  private async updateProviderStatus(provider: ApiProviderName, result: ValidationResult): Promise<void> {
    await this.initialize();
    
    this.config!.status[provider] = {
      isValid: result.isValid,
      isConfigured: this.config!.keys[provider] !== null,
      lastValidated: new Date(),
      error: result.error
    };

    await this.saveConfiguration();
  }

  /**
   * Validate Unsplash API key
   */
  private async validateUnsplashKey(apiKey: string): Promise<ValidationResult> {
    try {
      const response = await fetch('https://api.unsplash.com/me', {
        headers: {
          'Authorization': `Client-ID ${apiKey}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        return {
          isValid: true,
          details: { username: data.username, name: data.name }
        };
      } else if (response.status === 401) {
        return { isValid: false, error: 'Invalid API key' };
      } else {
        return { isValid: false, error: `HTTP ${response.status}: ${response.statusText}` };
      }
    } catch (error) {
      return {
        isValid: false,
        error: error instanceof Error ? error.message : 'Network error'
      };
    }
  }

  /**
   * Validate OpenAI API key
   */
  private async validateOpenAIKey(apiKey: string): Promise<ValidationResult> {
    try {
      const response = await fetch('https://api.openai.com/v1/models', {
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        return { isValid: true };
      } else if (response.status === 401) {
        return { isValid: false, error: 'Invalid API key' };
      } else if (response.status === 429) {
        return { isValid: false, error: 'Rate limit exceeded' };
      } else {
        return { isValid: false, error: `HTTP ${response.status}: ${response.statusText}` };
      }
    } catch (error) {
      return {
        isValid: false,
        error: error instanceof Error ? error.message : 'Network error'
      };
    }
  }

  /**
   * Check if any API keys are configured
   */
  async hasAnyApiKeys(): Promise<boolean> {
    const keys = await this.getApiKeys();
    return Object.values(keys).some(key => key !== null && key.trim() !== '');
  }

  /**
   * Check if all required API keys are configured and valid
   */
  async areAllKeysValid(): Promise<boolean> {
    await this.initialize();
    const config = this.config!;
    
    return Object.values(config.status).every(status => 
      status.isConfigured && status.isValid
    );
  }

  /**
   * Clear all API keys and configuration
   */
  async clearConfiguration(): Promise<void> {
    this.config = this.createDefaultConfiguration();
    localStorage.removeItem(STORAGE_KEY);
    await this.saveConfiguration();
  }

  /**
   * Check if setup is needed (no valid API keys)
   */
  async isSetupNeeded(): Promise<boolean> {
    await this.initialize();
    const hasKeys = await this.hasAnyApiKeys();
    return !hasKeys;
  }

  /**
   * Get fallback API key from environment variables
   */
  getEnvApiKey(provider: ApiProviderName): string | null {
    switch (provider) {
      case 'unsplash':
        return import.meta.env.VITE_UNSPLASH_ACCESS_KEY || null;
      case 'openai':
        return import.meta.env.VITE_OPENAI_API_KEY || null;
      default:
        return null;
    }
  }

  /**
   * Get effective API key (runtime config or fallback to env)
   */
  async getEffectiveApiKey(provider: ApiProviderName): Promise<string | null> {
    const runtimeKey = await this.getApiKey(provider);
    if (runtimeKey) {
      return runtimeKey;
    }
    
    return this.getEnvApiKey(provider);
  }
}

// Export singleton instance
export const apiConfigService = new ApiConfigService();