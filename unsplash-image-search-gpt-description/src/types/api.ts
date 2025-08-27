/**
 * Type definitions for API configuration and management
 */

export interface ApiKeys {
  unsplash: string | null;
  openai: string | null;
}

export interface ApiKeyStatus {
  isValid: boolean;
  isConfigured: boolean;
  lastValidated?: Date;
  error?: string;
}

export interface ApiConfiguration {
  keys: ApiKeys;
  status: {
    unsplash: ApiKeyStatus;
    openai: ApiKeyStatus;
  };
}

export interface ApiProvider {
  name: string;
  displayName: string;
  description: string;
  getApiKeyUrl: string;
  helpText: string;
  placeholder: string;
}

export interface ValidationResult {
  isValid: boolean;
  error?: string;
  details?: any;
}

export interface EncryptedApiData {
  encrypted: string;
  iv: string;
  salt: string;
  timestamp: number;
}

export type ApiProviderName = 'unsplash' | 'openai';

export const API_PROVIDERS: Record<ApiProviderName, ApiProvider> = {
  unsplash: {
    name: 'unsplash',
    displayName: 'Unsplash',
    description: 'Access to millions of high-quality stock photos',
    getApiKeyUrl: 'https://unsplash.com/developers',
    helpText: 'Create a free developer account on Unsplash to get your API key',
    placeholder: 'Enter your Unsplash Access Key'
  },
  openai: {
    name: 'openai',
    displayName: 'OpenAI',
    description: 'AI-powered image descriptions and text generation',
    getApiKeyUrl: 'https://platform.openai.com/api-keys',
    helpText: 'Get your API key from the OpenAI platform dashboard',
    placeholder: 'Enter your OpenAI API Key (sk-...)'
  }
};

export interface SetupStep {
  id: string;
  title: string;
  description: string;
  isCompleted: boolean;
  isOptional: boolean;
}