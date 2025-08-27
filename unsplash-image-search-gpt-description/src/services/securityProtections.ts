/**
 * Security Protection Service for VocabLens PWA
 * Implements comprehensive security measures for client-side API key protection
 */

/**
 * Content Security Policy Configuration
 */
export const CSP_POLICIES = {
  'default-src': ["'self'"],
  'script-src': [
    "'self'",
    "'unsafe-inline'", // Required for Vite dev mode
    "'unsafe-eval'", // Required for some React dev tools
    "https://api.unsplash.com",
    "https://api.openai.com",
    "https://*.supabase.co"
  ],
  'style-src': [
    "'self'",
    "'unsafe-inline'", // Required for styled components and CSS-in-JS
    "https://fonts.googleapis.com"
  ],
  'img-src': [
    "'self'",
    "data:",
    "blob:",
    "https:",
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
  'upgrade-insecure-requests': []
};

/**
 * XSS Protection Service
 */
export class XSSProtection {
  private static readonly DANGEROUS_PATTERNS = [
    /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
    /javascript:/gi,
    /on\w+\s*=/gi,
    /<iframe\b[^>]*>/gi,
    /<object\b[^>]*>/gi,
    /<embed\b[^>]*>/gi,
    /<link\b[^>]*>/gi,
    /<meta\b[^>]*>/gi,
    /expression\s*\(/gi,
    /vbscript:/gi
  ];

  /**
   * Sanitize user input to prevent XSS attacks
   */
  static sanitizeInput(input: string): string {
    if (typeof input !== 'string') {
      return '';
    }

    let sanitized = input;

    // Remove dangerous patterns
    this.DANGEROUS_PATTERNS.forEach(pattern => {
      sanitized = sanitized.replace(pattern, '');
    });

    // Encode HTML entities
    sanitized = sanitized
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#x27;')
      .replace(/\//g, '&#x2F;');

    return sanitized.trim();
  }

  /**
   * Validate URL to prevent malicious redirects
   */
  static validateUrl(url: string): boolean {
    try {
      const parsed = new URL(url);
      const allowedProtocols = ['https:', 'http:'];
      const allowedHosts = [
        'api.unsplash.com',
        'images.unsplash.com',
        'plus.unsplash.com',
        'api.openai.com',
        'supabase.co',
        'localhost'
      ];

      // Check protocol
      if (!allowedProtocols.includes(parsed.protocol)) {
        return false;
      }

      // Check host against whitelist
      const isAllowedHost = allowedHosts.some(host => 
        parsed.hostname === host || parsed.hostname.endsWith('.' + host)
      );

      return isAllowedHost;
    } catch {
      return false;
    }
  }

  /**
   * Create safe HTML attributes
   */
  static createSafeAttributes(attributes: Record<string, string>): Record<string, string> {
    const safe: Record<string, string> = {};
    const dangerousAttributes = ['onclick', 'onload', 'onerror', 'onmouseover', 'onfocus', 'onblur'];

    Object.entries(attributes).forEach(([key, value]) => {
      if (!dangerousAttributes.includes(key.toLowerCase())) {
        safe[key] = this.sanitizeInput(value);
      }
    });

    return safe;
  }
}

/**
 * API Key Exposure Prevention
 */
export class ApiKeyProtection {
  private static readonly API_KEY_PATTERNS = [
    /sk-[a-zA-Z0-9]{48}/g, // OpenAI API keys
    /[a-zA-Z0-9]{43}/g, // Unsplash access keys (typical length)
    /eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+/g // JWT tokens
  ];

  /**
   * Scan text for potential API key exposure
   */
  static scanForApiKeys(text: string): string[] {
    const potentialKeys: string[] = [];

    this.API_KEY_PATTERNS.forEach(pattern => {
      const matches = text.match(pattern);
      if (matches) {
        potentialKeys.push(...matches);
      }
    });

    return potentialKeys;
  }

  /**
   * Redact API keys from text for logging
   */
  static redactApiKeys(text: string): string {
    let redacted = text;

    this.API_KEY_PATTERNS.forEach(pattern => {
      redacted = redacted.replace(pattern, (match) => {
        // Show first 4 and last 4 characters, redact the middle
        if (match.length > 8) {
          return match.substring(0, 4) + '*'.repeat(match.length - 8) + match.substring(match.length - 4);
        }
        return '*'.repeat(match.length);
      });
    });

    return redacted;
  }

  /**
   * Validate API key format without exposing the key
   */
  static validateApiKeyFormat(key: string, service: 'unsplash' | 'openai'): {
    valid: boolean;
    reason?: string;
  } {
    if (!key || typeof key !== 'string') {
      return { valid: false, reason: 'Key is empty or not a string' };
    }

    switch (service) {
      case 'unsplash':
        if (key.length < 20 || key.length > 50) {
          return { valid: false, reason: 'Invalid key length for Unsplash' };
        }
        if (!/^[A-Za-z0-9_-]+$/.test(key)) {
          return { valid: false, reason: 'Invalid characters in Unsplash key' };
        }
        return { valid: true };

      case 'openai':
        if (!key.startsWith('sk-')) {
          return { valid: false, reason: 'OpenAI keys must start with sk-' };
        }
        if (key.length < 20) {
          return { valid: false, reason: 'OpenAI key too short' };
        }
        if (!/^sk-[A-Za-z0-9]{20,}$/.test(key)) {
          return { valid: false, reason: 'Invalid OpenAI key format' };
        }
        return { valid: true };

      default:
        return { valid: false, reason: 'Unknown service' };
    }
  }
}

/**
 * Network Request Protection
 */
export class NetworkProtection {
  private static readonly MAX_RETRY_ATTEMPTS = 3;
  private static readonly RETRY_DELAY_BASE = 1000;
  private static readonly REQUEST_TIMEOUT = 30000;

  /**
   * Create secure fetch wrapper with protection against common attacks
   */
  static async secureRequest(
    url: string,
    options: RequestInit = {},
    retryCount = 0
  ): Promise<Response> {
    // Validate URL
    if (!XSSProtection.validateUrl(url)) {
      throw new SecurityError('Invalid or potentially malicious URL');
    }

    // Add security headers
    const secureOptions: RequestInit = {
      ...options,
      headers: {
        ...options.headers,
        'X-Requested-With': 'XMLHttpRequest',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY'
      }
    };

    // Add timeout protection
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.REQUEST_TIMEOUT);
    secureOptions.signal = controller.signal;

    try {
      const response = await fetch(url, secureOptions);
      clearTimeout(timeoutId);

      // Check for suspicious response headers
      this.validateResponseHeaders(response);

      return response;
    } catch (error) {
      clearTimeout(timeoutId);

      // Handle network errors with retry logic
      if (error instanceof Error && error.name === 'AbortError') {
        throw new SecurityError('Request timeout - potential DoS protection activated');
      }

      // Retry on network errors (but not on security errors)
      if (retryCount < this.MAX_RETRY_ATTEMPTS && this.isRetryableError(error)) {
        const delay = this.RETRY_DELAY_BASE * Math.pow(2, retryCount);
        await this.sleep(delay);
        return this.secureRequest(url, options, retryCount + 1);
      }

      throw error;
    }
  }

  /**
   * Validate response headers for security issues
   */
  private static validateResponseHeaders(response: Response): void {
    const contentType = response.headers.get('content-type');
    
    // Ensure JSON responses have correct content type
    if (contentType && !contentType.includes('application/json') && 
        !contentType.includes('text/plain') && !contentType.includes('image/')) {
      console.warn('Unexpected content type:', contentType);
    }

    // Check for potentially malicious headers
    const suspiciousHeaders = ['x-powered-by', 'server'];
    suspiciousHeaders.forEach(header => {
      const value = response.headers.get(header);
      if (value) {
        console.warn(`Potentially leaky header detected: ${header}: ${value}`);
      }
    });
  }

  /**
   * Check if error is retryable
   */
  private static isRetryableError(error: unknown): boolean {
    if (error instanceof SecurityError) {
      return false; // Never retry security errors
    }

    if (error instanceof Error) {
      const retryableErrors = ['NetworkError', 'TypeError'];
      return retryableErrors.some(type => error.name.includes(type));
    }

    return false;
  }

  /**
   * Sleep utility for retry delays
   */
  private static sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

/**
 * Browser Security Monitor
 */
export class BrowserSecurityMonitor {
  private static instance: BrowserSecurityMonitor | null = null;
  private eventListeners: (() => void)[] = [];
  private securityEvents: Array<{
    type: string;
    timestamp: number;
    details: any;
  }> = [];

  static getInstance(): BrowserSecurityMonitor {
    if (!this.instance) {
      this.instance = new BrowserSecurityMonitor();
    }
    return this.instance;
  }

  /**
   * Initialize security monitoring
   */
  initialize(): void {
    this.setupConsoleProtection();
    this.setupExtensionDetection();
    this.setupDevToolsDetection();
    this.setupNetworkMonitoring();
  }

  /**
   * Set up console protection to prevent API key exposure
   */
  private setupConsoleProtection(): void {
    // Override console methods to redact sensitive information
    const originalLog = console.log;
    const originalError = console.error;
    const originalWarn = console.warn;

    console.log = (...args) => {
      const redactedArgs = args.map(arg => 
        typeof arg === 'string' ? ApiKeyProtection.redactApiKeys(arg) : arg
      );
      originalLog.apply(console, redactedArgs);
    };

    console.error = (...args) => {
      const redactedArgs = args.map(arg => 
        typeof arg === 'string' ? ApiKeyProtection.redactApiKeys(arg) : arg
      );
      originalError.apply(console, redactedArgs);
    };

    console.warn = (...args) => {
      const redactedArgs = args.map(arg => 
        typeof arg === 'string' ? ApiKeyProtection.redactApiKeys(arg) : arg
      );
      originalWarn.apply(console, redactedArgs);
    };
  }

  /**
   * Detect potentially malicious browser extensions
   */
  private setupExtensionDetection(): void {
    // Check for known problematic extension patterns
    const checkExtensions = () => {
      const suspiciousPatterns = [
        'chrome-extension://',
        'moz-extension://',
        'extension://'
      ];

      const scripts = Array.from(document.scripts);
      const links = Array.from(document.links);
      
      suspiciousPatterns.forEach(pattern => {
        const suspiciousScripts = scripts.filter(script => 
          script.src && script.src.includes(pattern)
        );
        
        if (suspiciousScripts.length > 0) {
          this.recordSecurityEvent('suspicious_extension_detected', {
            pattern,
            count: suspiciousScripts.length
          });
        }
      });
    };

    // Check periodically
    setInterval(checkExtensions, 30000); // Every 30 seconds
    checkExtensions(); // Initial check
  }

  /**
   * Detect developer tools usage
   */
  private setupDevToolsDetection(): void {
    let devToolsOpen = false;
    
    const detectDevTools = () => {
      const threshold = 160;
      const widthThreshold = window.outerWidth - window.innerWidth > threshold;
      const heightThreshold = window.outerHeight - window.innerHeight > threshold;
      
      if (widthThreshold || heightThreshold) {
        if (!devToolsOpen) {
          devToolsOpen = true;
          this.recordSecurityEvent('devtools_opened', {
            timestamp: Date.now(),
            userAgent: navigator.userAgent
          });
        }
      } else {
        devToolsOpen = false;
      }
    };

    setInterval(detectDevTools, 1000);
  }

  /**
   * Monitor network requests for potential data leakage
   */
  private setupNetworkMonitoring(): void {
    // Override fetch to monitor outgoing requests
    const originalFetch = window.fetch;
    
    window.fetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
      const url = typeof input === 'string' ? input : input.toString();
      
      // Check for potential data leakage in URLs
      const potentialKeys = ApiKeyProtection.scanForApiKeys(url);
      if (potentialKeys.length > 0) {
        this.recordSecurityEvent('potential_key_leak_in_url', {
          url: ApiKeyProtection.redactApiKeys(url),
          keyCount: potentialKeys.length
        });
      }

      // Monitor request headers
      if (init?.headers) {
        const headerString = JSON.stringify(init.headers);
        const potentialHeaderKeys = ApiKeyProtection.scanForApiKeys(headerString);
        if (potentialHeaderKeys.length > 0) {
          this.recordSecurityEvent('potential_key_leak_in_headers', {
            keyCount: potentialHeaderKeys.length
          });
        }
      }

      return originalFetch(input, init);
    };
  }

  /**
   * Record security events
   */
  private recordSecurityEvent(type: string, details: any): void {
    this.securityEvents.push({
      type,
      timestamp: Date.now(),
      details
    });

    // Keep only last 100 events
    if (this.securityEvents.length > 100) {
      this.securityEvents = this.securityEvents.slice(-100);
    }

    // Log high-priority events
    const highPriorityEvents = [
      'potential_key_leak_in_url',
      'potential_key_leak_in_headers',
      'suspicious_extension_detected'
    ];

    if (highPriorityEvents.includes(type)) {
      console.warn(`Security Alert: ${type}`, details);
    }
  }

  /**
   * Get security events for review
   */
  getSecurityEvents(): Array<{ type: string; timestamp: number; details: any }> {
    return [...this.securityEvents];
  }

  /**
   * Clear security events
   */
  clearSecurityEvents(): void {
    this.securityEvents = [];
  }

  /**
   * Cleanup resources
   */
  cleanup(): void {
    this.eventListeners.forEach(cleanup => cleanup());
    this.eventListeners = [];
  }
}

/**
 * Security Error class
 */
export class SecurityError extends Error {
  constructor(message: string, public code?: string) {
    super(message);
    this.name = 'SecurityError';
  }
}

/**
 * Security utility functions
 */
export const SecurityUtils = {
  /**
   * Generate Content Security Policy header value
   */
  generateCSPHeader(): string {
    return Object.entries(CSP_POLICIES)
      .map(([directive, sources]) => {
        if (sources.length === 0) {
          return directive;
        }
        return `${directive} ${sources.join(' ')}`;
      })
      .join('; ');
  },

  /**
   * Check if running in secure context
   */
  isSecureContext(): boolean {
    return window.isSecureContext || location.protocol === 'https:' || location.hostname === 'localhost';
  },

  /**
   * Validate environment security
   */
  validateEnvironmentSecurity(): Array<{ issue: string; severity: 'high' | 'medium' | 'low' }> {
    const issues: Array<{ issue: string; severity: 'high' | 'medium' | 'low' }> = [];

    // Check secure context
    if (!this.isSecureContext()) {
      issues.push({
        issue: 'Application not running in secure context (HTTPS)',
        severity: 'high'
      });
    }

    // Check for development mode in production
    if (import.meta.env.PROD && import.meta.env.DEV) {
      issues.push({
        issue: 'Development mode detected in production build',
        severity: 'high'
      });
    }

    // Check localStorage availability
    try {
      localStorage.setItem('test', 'test');
      localStorage.removeItem('test');
    } catch {
      issues.push({
        issue: 'LocalStorage not available - private browsing mode?',
        severity: 'medium'
      });
    }

    // Check Web Crypto API availability
    if (!window.crypto || !window.crypto.subtle) {
      issues.push({
        issue: 'Web Crypto API not available',
        severity: 'high'
      });
    }

    return issues;
  }
};

// Initialize security monitoring on module load
if (typeof window !== 'undefined') {
  const monitor = BrowserSecurityMonitor.getInstance();
  monitor.initialize();
}

export default {
  XSSProtection,
  ApiKeyProtection,
  NetworkProtection,
  BrowserSecurityMonitor,
  SecurityError,
  SecurityUtils
};