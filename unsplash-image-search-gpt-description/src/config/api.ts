/**
 * API Configuration for VocabLens PWA
 * Centralizes all API endpoints, keys, and configuration
 */

// Environment variable validation
const requiredEnvVars = [
  'VITE_UNSPLASH_ACCESS_KEY',
  'VITE_OPENAI_API_KEY',
  'VITE_SUPABASE_URL',
  'VITE_SUPABASE_ANON_KEY'
];

// Validate required environment variables
const missingVars = requiredEnvVars.filter(varName => !import.meta.env[varName]);
if (missingVars.length > 0) {
  console.error('Missing required environment variables:', missingVars);
  throw new Error(`Missing required environment variables: ${missingVars.join(', ')}`);
}

/**
 * API Configuration object
 */
export const apiConfig = {
  // Application Configuration
  app: {
    name: import.meta.env.VITE_APP_NAME || 'VocabLens',
    version: import.meta.env.VITE_APP_VERSION || '1.0.0',
    description: import.meta.env.VITE_APP_DESCRIPTION || 'AI-Powered Vocabulary Learning'
  },

  // API Keys
  keys: {
    unsplash: import.meta.env.VITE_UNSPLASH_ACCESS_KEY,
    openai: import.meta.env.VITE_OPENAI_API_KEY
  },

  // Supabase Configuration
  supabase: {
    url: import.meta.env.VITE_SUPABASE_URL,
    anonKey: import.meta.env.VITE_SUPABASE_ANON_KEY
  },

  // API Endpoints
  endpoints: {
    unsplash: {
      base: import.meta.env.VITE_UNSPLASH_API_URL || 'https://api.unsplash.com',
      search: '/search/photos',
      photos: '/photos'
    },
    openai: {
      base: import.meta.env.VITE_OPENAI_API_URL || 'https://api.openai.com/v1',
      completions: '/chat/completions',
      models: '/models'
    }
  },

  // Rate Limiting
  rateLimit: {
    perMinute: parseInt(import.meta.env.VITE_API_RATE_LIMIT_PER_MINUTE || '60'),
    maxConcurrent: parseInt(import.meta.env.VITE_MAX_CONCURRENT_REQUESTS || '5')
  },

  // Feature Flags
  features: {
    pwa: import.meta.env.VITE_ENABLE_PWA === 'true',
    offlineMode: import.meta.env.VITE_ENABLE_OFFLINE_MODE === 'true',
    pushNotifications: import.meta.env.VITE_ENABLE_PUSH_NOTIFICATIONS === 'true',
    analytics: import.meta.env.VITE_ENABLE_ANALYTICS === 'true',
    debug: import.meta.env.VITE_ENABLE_DEBUG === 'true'
  },

  // Image Configuration
  images: {
    defaultSize: import.meta.env.VITE_DEFAULT_IMAGE_SIZE || 'regular',
    maxPerSearch: parseInt(import.meta.env.VITE_MAX_IMAGES_PER_SEARCH || '30'),
    cacheSizeMB: parseInt(import.meta.env.VITE_IMAGE_CACHE_SIZE_MB || '50'),
    supportedSizes: ['thumb', 'small', 'regular', 'full'] as const
  },

  // AI Configuration
  ai: {
    defaultModel: import.meta.env.VITE_DEFAULT_AI_MODEL || 'gpt-3.5-turbo',
    maxDescriptionLength: parseInt(import.meta.env.VITE_MAX_DESCRIPTION_LENGTH || '500'),
    temperature: parseFloat(import.meta.env.VITE_AI_TEMPERATURE || '0.7'),
    maxTokens: 1000,
    supportedModels: ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo-preview'] as const
  },

  // Vocabulary Configuration
  vocabulary: {
    dailyGoal: parseInt(import.meta.env.VITE_DEFAULT_DAILY_GOAL || '10'),
    maxItems: parseInt(import.meta.env.VITE_MAX_VOCABULARY_ITEMS || '10000'),
    srsInitialInterval: parseInt(import.meta.env.VITE_SRS_INITIAL_INTERVAL || '1')
  },

  // Security Configuration
  security: {
    enableCSP: import.meta.env.VITE_ENABLE_CONTENT_SECURITY_POLICY === 'true',
    secureHeaders: import.meta.env.VITE_SECURE_HEADERS === 'true'
  },

  // Development Configuration
  development: {
    devTools: import.meta.env.VITE_DEV_TOOLS === 'true',
    logLevel: import.meta.env.VITE_LOG_LEVEL || 'info'
  }
} as const;

/**
 * API Headers configuration
 */
export const getApiHeaders = (service: 'unsplash' | 'openai') => {
  const baseHeaders = {
    'Content-Type': 'application/json',
    'User-Agent': `${apiConfig.app.name}/${apiConfig.app.version}`
  };

  switch (service) {
    case 'unsplash':
      return {
        ...baseHeaders,
        'Authorization': `Client-ID ${apiConfig.keys.unsplash}`,
        'Accept-Version': 'v1'
      };
    case 'openai':
      return {
        ...baseHeaders,
        'Authorization': `Bearer ${apiConfig.keys.openai}`
      };
    default:
      return baseHeaders;
  }
};

/**
 * Build API URL with proper encoding
 */
export const buildApiUrl = (
  base: string,
  endpoint: string,
  params?: Record<string, string | number | boolean>
): string => {
  const url = new URL(endpoint, base);
  
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      url.searchParams.append(key, String(value));
    });
  }

  return url.toString();
};

/**
 * Validate API key format
 */
export const validateApiKey = (key: string, service: 'unsplash' | 'openai'): boolean => {
  if (!key || typeof key !== 'string') return false;
  
  switch (service) {
    case 'unsplash':
      // Unsplash keys are typically 43 characters long
      return key.length >= 20 && /^[A-Za-z0-9_-]+$/.test(key);
    case 'openai':
      // OpenAI keys start with 'sk-' and have specific format
      return key.startsWith('sk-') && key.length > 20;
    default:
      return false;
  }
};

/**
 * Environment type checking
 */
export const isDevelopment = import.meta.env.DEV;
export const isProduction = import.meta.env.PROD;
export const isTest = import.meta.env.MODE === 'test';

/**
 * API Error types
 */
export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public code?: string,
    public service?: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * Request timeout configuration
 */
export const timeouts = {
  default: 30000, // 30 seconds
  upload: 60000,  // 60 seconds for uploads
  search: 15000,  // 15 seconds for search
  ai: 45000       // 45 seconds for AI requests
} as const;

/**
 * Retry configuration
 */
export const retryConfig = {
  maxAttempts: 3,
  backoffMs: 1000,
  backoffMultiplier: 2
} as const;

// Validate configuration on module load
if (isDevelopment) {
  console.log('API Configuration loaded:', {
    unsplashKeyValid: validateApiKey(apiConfig.keys.unsplash, 'unsplash'),
    openaiKeyValid: validateApiKey(apiConfig.keys.openai, 'openai'),
    supabaseConfigured: !!apiConfig.supabase.url && !!apiConfig.supabase.anon
  });
}

export default apiConfig;