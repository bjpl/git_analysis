/**
 * Cloudflare Pages Functions Configuration
 * Configure edge functions for advanced functionality
 */

// Environment configuration for different stages
export const environmentConfig = {
  development: {
    debug: true,
    caching: false,
    minification: false
  },
  staging: {
    debug: true,
    caching: true,
    minification: true
  },
  production: {
    debug: false,
    caching: true,
    minification: true
  }
};

// Cache configuration by content type
export const cacheConfig = {
  // Static assets - long cache
  static: {
    patterns: ['/assets/*', '*.css', '*.js', '*.woff2', '*.ico'],
    ttl: 31536000, // 1 year
    headers: {
      'Cache-Control': 'public, max-age=31536000, immutable',
      'Vary': 'Accept-Encoding'
    }
  },
  
  // Images - medium cache
  images: {
    patterns: ['*.jpg', '*.jpeg', '*.png', '*.webp', '*.svg'],
    ttl: 2592000, // 30 days
    headers: {
      'Cache-Control': 'public, max-age=2592000',
      'Vary': 'Accept-Encoding'
    }
  },
  
  // HTML pages - short cache with revalidation
  pages: {
    patterns: ['/', '*.html'],
    ttl: 300, // 5 minutes
    headers: {
      'Cache-Control': 'public, max-age=300, must-revalidate',
      'Vary': 'Accept-Encoding'
    }
  },
  
  // API routes - minimal cache
  api: {
    patterns: ['/api/*'],
    ttl: 60, // 1 minute
    headers: {
      'Cache-Control': 'public, max-age=60, must-revalidate',
      'Vary': 'Accept-Encoding, Authorization'
    }
  }
};

// Security headers configuration
export const securityHeaders = {
  // Basic security headers
  'X-Frame-Options': 'DENY',
  'X-Content-Type-Options': 'nosniff',
  'X-XSS-Protection': '1; mode=block',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
  
  // HSTS
  'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
  
  // CSP (will be customized per route)
  'Content-Security-Policy': [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://static.cloudflareinsights.com",
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data: https:",
    "font-src 'self' data:",
    "connect-src 'self' https:",
    "frame-ancestors 'none'"
  ].join('; ')
};

// Performance optimization settings
export const performanceConfig = {
  // Compression settings
  compression: {
    enabled: true,
    minSize: 1024, // Minimum size to compress (bytes)
    types: [
      'text/html',
      'text/css',
      'text/javascript',
      'text/plain',
      'application/javascript',
      'application/json',
      'application/xml',
      'image/svg+xml'
    ]
  },
  
  // Image optimization
  imageOptimization: {
    enabled: true,
    formats: ['webp', 'avif'],
    quality: 85,
    progressive: true
  },
  
  // Minification settings
  minification: {
    html: true,
    css: true,
    javascript: true,
    preserveComments: false
  }
};

// Redirect rules
export const redirectConfig = {
  // Permanent redirects (301)
  permanent: [
    // Example: { from: '/old-page', to: '/new-page' }
  ],
  
  // Temporary redirects (302)
  temporary: [
    // Example: { from: '/maintenance', to: '/under-construction' }
  ],
  
  // Conditional redirects
  conditional: [
    // Example: { from: '/mobile/*', to: '/m/*', condition: 'mobile' }
  ]
};

// Analytics and monitoring
export const analyticsConfig = {
  // Web analytics
  webAnalytics: {
    enabled: true,
    provider: 'cloudflare', // or 'google-analytics'
    trackingId: process.env.ANALYTICS_ID
  },
  
  // Performance monitoring
  performanceMonitoring: {
    enabled: true,
    sampleRate: 0.1, // 10% sampling
    metrics: ['LCP', 'FID', 'CLS', 'TTFB']
  },
  
  // Error tracking
  errorTracking: {
    enabled: true,
    provider: 'sentry', // or custom
    dsn: process.env.SENTRY_DSN
  }
};

// Rate limiting configuration
export const rateLimitConfig = {
  // Global rate limits
  global: {
    requests: 100,
    window: '1m' // 1 minute
  },
  
  // API rate limits
  api: {
    requests: 20,
    window: '1m'
  },
  
  // Per-IP rate limits
  perIP: {
    requests: 50,
    window: '1m'
  }
};

// Geolocation and edge routing
export const edgeConfig = {
  // Geographic routing
  geoRouting: {
    enabled: true,
    rules: [
      // Example: Route EU users to EU-specific content
      // { region: 'EU', redirect: '/eu' }
    ]
  },
  
  // Edge computing features
  edgeFeatures: {
    // Enable edge-side includes
    esi: true,
    
    // Enable edge-side JavaScript
    edgeJS: true,
    
    // Enable image resizing
    imageResizing: true
  }
};

// Environment-specific overrides
export function getConfig(environment = 'development') {
  const baseConfig = {
    environment: environmentConfig[environment],
    cache: cacheConfig,
    security: securityHeaders,
    performance: performanceConfig,
    redirects: redirectConfig,
    analytics: analyticsConfig,
    rateLimit: rateLimitConfig,
    edge: edgeConfig
  };

  // Apply environment-specific overrides
  switch (environment) {
    case 'production':
      return {
        ...baseConfig,
        security: {
          ...baseConfig.security,
          // Stricter CSP for production
          'Content-Security-Policy': baseConfig.security['Content-Security-Policy']
            .replace("'unsafe-inline'", '')
            .replace("'unsafe-eval'", '')
        }
      };
    
    case 'staging':
      return {
        ...baseConfig,
        analytics: {
          ...baseConfig.analytics,
          performanceMonitoring: {
            ...baseConfig.analytics.performanceMonitoring,
            sampleRate: 1.0 // 100% sampling in staging
          }
        }
      };
    
    default:
      return baseConfig;
  }
}

export default getConfig;