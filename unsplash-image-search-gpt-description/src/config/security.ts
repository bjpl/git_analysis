/**
 * Security Configuration for VocabLens PWA
 * Centralizes security policies, headers, and configurations
 */

/**
 * Content Security Policy Configuration
 */
export const CSP_CONFIG = {
  // Development CSP (less restrictive for dev tools)
  development: {
    'default-src': ["'self'"],
    'script-src': [
      "'self'",
      "'unsafe-inline'", // Required for Vite dev mode
      "'unsafe-eval'", // Required for React dev tools
      "https://api.unsplash.com",
      "https://api.openai.com",
      "https://*.supabase.co",
      "http://localhost:*",
      "ws://localhost:*"
    ],
    'style-src': [
      "'self'",
      "'unsafe-inline'", // Required for styled components
      "https://fonts.googleapis.com"
    ],
    'img-src': [
      "'self'",
      "data:",
      "blob:",
      "https:",
      "http://localhost:*",
      "https://images.unsplash.com",
      "https://plus.unsplash.com",
      "https://*.unsplash.com"
    ],
    'font-src': [
      "'self'",
      "https://fonts.gstatic.com"
    ],
    'connect-src': [
      "'self'",
      "https://api.unsplash.com",
      "https://api.openai.com",
      "https://*.supabase.co",
      "wss://*.supabase.co",
      "ws://localhost:*",
      "http://localhost:*",
      "https://vitals.vercel-insights.com"
    ],
    'media-src': ["'self'", "blob:", "data:"],
    'object-src': ["'none'"],
    'base-uri': ["'self'"],
    'form-action': ["'self'"],
    'frame-ancestors': ["'none'"],
    'upgrade-insecure-requests': []
  },

  // Production CSP (strict security)
  production: {
    'default-src': ["'self'"],
    'script-src': [
      "'self'",
      "'sha256-HASH_OF_INLINE_SCRIPTS'", // Replace with actual hashes
      "https://api.unsplash.com",
      "https://api.openai.com",
      "https://*.supabase.co"
    ],
    'style-src': [
      "'self'",
      "'sha256-HASH_OF_INLINE_STYLES'", // Replace with actual hashes
      "https://fonts.googleapis.com"
    ],
    'img-src': [
      "'self'",
      "data:",
      "blob:",
      "https://images.unsplash.com",
      "https://plus.unsplash.com",
      "https://*.unsplash.com"
    ],
    'font-src': [
      "'self'",
      "https://fonts.gstatic.com"
    ],
    'connect-src': [
      "'self'",
      "https://api.unsplash.com",
      "https://api.openai.com",
      "https://*.supabase.co",
      "wss://*.supabase.co",
      "https://vitals.vercel-insights.com"
    ],
    'media-src': ["'self'", "blob:", "data:"],
    'object-src': ["'none'"],
    'base-uri': ["'self'"],
    'form-action': ["'self'"],
    'frame-ancestors': ["'none'"],
    'upgrade-insecure-requests': [],
    'block-all-mixed-content': []
  }
};

/**
 * Security Headers Configuration
 */
export const SECURITY_HEADERS = {
  // Prevents MIME type sniffing
  'X-Content-Type-Options': 'nosniff',
  
  // Prevents clickjacking
  'X-Frame-Options': 'DENY',
  
  // Enables XSS protection in browsers
  'X-XSS-Protection': '1; mode=block',
  
  // Enforces HTTPS
  'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
  
  // Restricts referrer information
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  
  // Controls browser features
  'Permissions-Policy': [
    'geolocation=()',
    'microphone=()',
    'camera=()',
    'payment=()',
    'usb=()',
    'magnetometer=()',
    'gyroscope=()',
    'accelerometer=()'
  ].join(', ')
};

/**
 * CORS Configuration
 */
export const CORS_CONFIG = {
  allowedOrigins: [
    'https://vocablens.app',
    'https://www.vocablens.app',
    'https://vocablens.netlify.app',
    'https://vocablens.vercel.app',
    ...(import.meta.env.DEV ? [
      'http://localhost:5173',
      'http://localhost:3000',
      'http://127.0.0.1:5173',
      'http://127.0.0.1:3000'
    ] : [])
  ],
  allowedMethods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
  allowedHeaders: [
    'Authorization',
    'Content-Type',
    'X-Requested-With',
    'Accept',
    'Origin',
    'X-API-Key',
    'X-Client-Version'
  ],
  exposedHeaders: ['X-Rate-Limit-Remaining', 'X-Rate-Limit-Reset'],
  credentials: true,
  maxAge: 86400 // 24 hours
};

/**
 * API Security Configuration
 */
export const API_SECURITY_CONFIG = {
  // Rate limiting
  rateLimit: {
    windowMs: 15 * 60 * 1000, // 15 minutes
    maxRequests: 100, // per window
    message: 'Too many requests, please try again later',
    standardHeaders: true,
    legacyHeaders: false
  },

  // Request validation
  requestValidation: {
    maxBodySize: '10mb',
    maxUrlLength: 2048,
    maxHeaderSize: '8kb',
    timeoutMs: 30000
  },

  // API key patterns for detection
  apiKeyPatterns: {
    openai: /^sk-[a-zA-Z0-9]{20,}$/,
    unsplash: /^[a-zA-Z0-9_-]{20,50}$/,
    supabase: /^eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+$/
  },

  // Allowed API endpoints
  allowedEndpoints: {
    unsplash: [
      'https://api.unsplash.com/search/photos',
      'https://api.unsplash.com/photos',
      'https://api.unsplash.com/photos/*/download'
    ],
    openai: [
      'https://api.openai.com/v1/chat/completions',
      'https://api.openai.com/v1/models'
    ],
    supabase: [
      // Dynamically configured based on project URL
    ]
  }
};

/**
 * Client-Side Storage Security
 */
export const STORAGE_SECURITY_CONFIG = {
  // Encryption settings
  encryption: {
    algorithm: 'AES-GCM',
    keyLength: 256,
    ivLength: 96,
    tagLength: 128,
    saltLength: 128,
    iterations: 100000, // PBKDF2 iterations
    hashAlgorithm: 'SHA-256'
  },

  // Storage keys (prefixed for isolation)
  storageKeys: {
    encryptedKeys: 'vocablens_encrypted_keys',
    securityMetrics: 'vocablens_security_metrics',
    userPreferences: 'vocablens_user_prefs',
    sessionData: 'vocablens_session'
  },

  // Security thresholds
  security: {
    minPasswordLength: 12,
    maxFailedAttempts: 5,
    lockoutDurationMs: 15 * 60 * 1000, // 15 minutes
    keyRotationReminderDays: 30,
    sessionTimeoutMs: 60 * 60 * 1000, // 1 hour
    masterKeyCacheTimeMs: 15 * 60 * 1000 // 15 minutes
  }
};

/**
 * Content Validation Rules
 */
export const CONTENT_VALIDATION = {
  // Input sanitization patterns
  dangerousPatterns: [
    /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
    /javascript:/gi,
    /on\w+\s*=/gi,
    /<iframe\b[^>]*>/gi,
    /<object\b[^>]*>/gi,
    /<embed\b[^>]*>/gi,
    /<link\b[^>]*>/gi,
    /<meta\b[^>]*>/gi,
    /expression\s*\(/gi,
    /vbscript:/gi,
    /data:text\/html/gi
  ],

  // Allowed HTML tags for rich content
  allowedHtmlTags: [
    'p', 'br', 'strong', 'em', 'u', 'i', 'b',
    'ul', 'ol', 'li', 'blockquote', 'code', 'pre'
  ],

  // URL validation
  urlWhitelist: [
    'api.unsplash.com',
    'images.unsplash.com',
    'plus.unsplash.com',
    'api.openai.com',
    '*.supabase.co',
    'fonts.googleapis.com',
    'fonts.gstatic.com'
  ],

  // File upload restrictions
  fileUpload: {
    maxSizeBytes: 5 * 1024 * 1024, // 5MB
    allowedTypes: ['image/jpeg', 'image/png', 'image/webp', 'image/gif'],
    allowedExtensions: ['.jpg', '.jpeg', '.png', '.webp', '.gif']
  }
};

/**
 * Monitoring and Logging Configuration
 */
export const MONITORING_CONFIG = {
  // Security events to track
  securityEvents: [
    'api_key_access',
    'api_key_storage',
    'api_key_rotation',
    'failed_authentication',
    'suspicious_request',
    'xss_attempt',
    'injection_attempt',
    'rate_limit_exceeded',
    'encryption_error',
    'storage_error'
  ],

  // Log levels
  logLevels: {
    ERROR: 0,
    WARN: 1,
    INFO: 2,
    DEBUG: 3
  },

  // Current log level based on environment
  currentLogLevel: import.meta.env.DEV ? 3 : 1, // DEBUG in dev, WARN in prod

  // Event retention
  maxEvents: 1000,
  eventRetentionHours: 24
};

/**
 * Feature Flags for Security Features
 */
export const SECURITY_FEATURE_FLAGS = {
  // Enable/disable security features
  enableCSP: import.meta.env.VITE_ENABLE_CONTENT_SECURITY_POLICY !== 'false',
  enableSecurityHeaders: import.meta.env.VITE_ENABLE_SECURE_HEADERS !== 'false',
  enableApiKeyRotation: import.meta.env.VITE_ENABLE_API_KEY_ROTATION !== 'false',
  enableRequestSigning: import.meta.env.VITE_ENABLE_REQUEST_SIGNING === 'true',
  enableBrowserSecurityMonitoring: true,
  enableConsoleProtection: !import.meta.env.DEV,
  enableDevToolsDetection: !import.meta.env.DEV,
  enableNetworkMonitoring: true,
  enableStorageEncryption: true,
  
  // Development-specific features
  enableVerboseLogging: import.meta.env.DEV,
  enableSecurityTesting: import.meta.env.DEV
};

/**
 * Environment-specific Security Configuration
 */
export const getEnvironmentSecurityConfig = () => {
  const isDev = import.meta.env.DEV;
  const isProd = import.meta.env.PROD;
  const isTest = import.meta.env.MODE === 'test';

  return {
    // CSP based on environment
    csp: isDev ? CSP_CONFIG.development : CSP_CONFIG.production,
    
    // Headers (more permissive in development)
    headers: {
      ...SECURITY_HEADERS,
      ...(isDev && {
        'Strict-Transport-Security': '', // Disable HSTS in dev
        'X-Frame-Options': 'SAMEORIGIN' // Allow framing in dev tools
      })
    },

    // CORS (more permissive in development)
    cors: {
      ...CORS_CONFIG,
      allowedOrigins: isDev ? 
        [...CORS_CONFIG.allowedOrigins, 'http://localhost:*'] : 
        CORS_CONFIG.allowedOrigins.filter(origin => !origin.includes('localhost'))
    },

    // API security (less strict in development)
    apiSecurity: {
      ...API_SECURITY_CONFIG,
      rateLimit: {
        ...API_SECURITY_CONFIG.rateLimit,
        maxRequests: isDev ? 1000 : API_SECURITY_CONFIG.rateLimit.maxRequests
      }
    },

    // Storage security (consistent across environments)
    storageSecurity: STORAGE_SECURITY_CONFIG,

    // Monitoring (more verbose in development)
    monitoring: {
      ...MONITORING_CONFIG,
      currentLogLevel: isDev ? 3 : (isProd ? 1 : 2)
    }
  };
};

/**
 * Generate CSP header string
 */
export const generateCSPHeader = (environment: 'development' | 'production' = 'production'): string => {
  const csp = CSP_CONFIG[environment];
  
  return Object.entries(csp)
    .map(([directive, sources]) => {
      if (sources.length === 0) {
        return directive;
      }
      return `${directive} ${sources.join(' ')}`;
    })
    .join('; ');
};

/**
 * Validate security configuration
 */
export const validateSecurityConfig = (): Array<{
  category: string;
  issue: string;
  severity: 'high' | 'medium' | 'low';
  recommendation: string;
}> => {
  const issues: Array<{
    category: string;
    issue: string;
    severity: 'high' | 'medium' | 'low';
    recommendation: string;
  }> = [];

  // Check HTTPS requirement
  if (import.meta.env.PROD && location.protocol !== 'https:') {
    issues.push({
      category: 'Transport Security',
      issue: 'Application not served over HTTPS in production',
      severity: 'high',
      recommendation: 'Ensure all production traffic uses HTTPS'
    });
  }

  // Check Web Crypto API availability
  if (!window.crypto || !window.crypto.subtle) {
    issues.push({
      category: 'Cryptography',
      issue: 'Web Crypto API not available',
      severity: 'high',
      recommendation: 'Web Crypto API is required for secure key storage'
    });
  }

  // Check localStorage availability
  try {
    localStorage.setItem('test', 'test');
    localStorage.removeItem('test');
  } catch {
    issues.push({
      category: 'Storage',
      issue: 'localStorage not available',
      severity: 'medium',
      recommendation: 'LocalStorage is required for encrypted key storage'
    });
  }

  // Check development mode in production
  if (import.meta.env.PROD && import.meta.env.DEV) {
    issues.push({
      category: 'Build Configuration',
      issue: 'Development mode enabled in production build',
      severity: 'high',
      recommendation: 'Ensure production builds disable development features'
    });
  }

  // Check CSP configuration
  if (!SECURITY_FEATURE_FLAGS.enableCSP) {
    issues.push({
      category: 'Content Security',
      issue: 'Content Security Policy disabled',
      severity: 'medium',
      recommendation: 'Enable CSP to prevent XSS attacks'
    });
  }

  return issues;
};

export default {
  CSP_CONFIG,
  SECURITY_HEADERS,
  CORS_CONFIG,
  API_SECURITY_CONFIG,
  STORAGE_SECURITY_CONFIG,
  CONTENT_VALIDATION,
  MONITORING_CONFIG,
  SECURITY_FEATURE_FLAGS,
  getEnvironmentSecurityConfig,
  generateCSPHeader,
  validateSecurityConfig
};