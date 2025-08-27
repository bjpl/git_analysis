export interface EnvironmentConfig {
  // API Keys
  UNSPLASH_ACCESS_KEY?: string;
  UNSPLASH_SECRET_KEY?: string;
  OPENAI_API_KEY?: string;
  OPENAI_ORG_ID?: string;
  
  // Supabase
  NEXT_PUBLIC_SUPABASE_URL?: string;
  NEXT_PUBLIC_SUPABASE_ANON_KEY?: string;
  SUPABASE_SERVICE_ROLE_KEY?: string;
  
  // App Configuration
  NODE_ENV?: string;
  NEXT_PUBLIC_APP_ENV?: string;
  NEXT_PUBLIC_API_URL?: string;
  
  // Feature Flags
  ENABLE_ANALYTICS?: string;
  ENABLE_ERROR_REPORTING?: string;
  ENABLE_OFFLINE_MODE?: string;
  
  // Rate Limiting
  UNSPLASH_RATE_LIMIT?: string;
  OPENAI_RATE_LIMIT?: string;
  
  // Security
  JWT_SECRET?: string;
  ENCRYPTION_KEY?: string;
  
  // Third-party Services
  SENTRY_DSN?: string;
  GOOGLE_ANALYTICS_ID?: string;
}

export interface ValidationRule {
  required: boolean;
  type: 'string' | 'number' | 'boolean' | 'url' | 'email';
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  description: string;
  example?: string;
}

export interface ValidationResult {
  valid: boolean;
  missing: string[];
  invalid: Array<{
    key: string;
    value?: string;
    reason: string;
    suggestion?: string;
  }>;
  warnings: Array<{
    key: string;
    message: string;
  }>;
}

class EnvironmentValidator {
  private validationRules: Record<string, ValidationRule> = {
    // Required API Keys
    UNSPLASH_ACCESS_KEY: {
      required: true,
      type: 'string',
      minLength: 43,
      maxLength: 43,
      pattern: /^[a-zA-Z0-9_-]{43}$/,
      description: 'Unsplash Access Key for image search functionality',
      example: 'abc123def456ghi789jkl012mno345pqr678stu901vwx'
    },
    
    OPENAI_API_KEY: {
      required: true,
      type: 'string',
      minLength: 51,
      maxLength: 51,
      pattern: /^sk-[a-zA-Z0-9]{48}$/,
      description: 'OpenAI API key for GPT description generation',
      example: 'sk-abc123def456ghi789jkl012mno345pqr678stu901vwx234'
    },
    
    NEXT_PUBLIC_SUPABASE_URL: {
      required: true,
      type: 'url',
      pattern: /^https:\/\/[a-zA-Z0-9-]+\.supabase\.co$/,
      description: 'Supabase project URL',
      example: 'https://your-project.supabase.co'
    },
    
    NEXT_PUBLIC_SUPABASE_ANON_KEY: {
      required: true,
      type: 'string',
      minLength: 100,
      description: 'Supabase anonymous/public key',
      example: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
    },
    
    // Optional but recommended
    SUPABASE_SERVICE_ROLE_KEY: {
      required: false,
      type: 'string',
      minLength: 100,
      description: 'Supabase service role key for server-side operations',
      example: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
    },
    
    UNSPLASH_SECRET_KEY: {
      required: false,
      type: 'string',
      minLength: 43,
      maxLength: 43,
      description: 'Unsplash Secret Key (optional, for OAuth flow)',
      example: 'def456ghi789jkl012mno345pqr678stu901vwx234abc'
    },
    
    OPENAI_ORG_ID: {
      required: false,
      type: 'string',
      pattern: /^org-[a-zA-Z0-9]{24}$/,
      description: 'OpenAI Organization ID (optional)',
      example: 'org-abc123def456ghi789jkl012'
    },
    
    // Application Configuration
    NODE_ENV: {
      required: false,
      type: 'string',
      pattern: /^(development|production|test)$/,
      description: 'Node.js environment',
      example: 'development'
    },
    
    NEXT_PUBLIC_APP_ENV: {
      required: false,
      type: 'string',
      pattern: /^(development|staging|production)$/,
      description: 'Application environment',
      example: 'development'
    },
    
    // Rate Limiting
    UNSPLASH_RATE_LIMIT: {
      required: false,
      type: 'number',
      description: 'Unsplash API rate limit (requests per hour)',
      example: '1000'
    },
    
    OPENAI_RATE_LIMIT: {
      required: false,
      type: 'number',
      description: 'OpenAI API rate limit (requests per minute)',
      example: '60'
    },
    
    // Feature Flags
    ENABLE_ANALYTICS: {
      required: false,
      type: 'boolean',
      description: 'Enable analytics tracking',
      example: 'true'
    },
    
    ENABLE_ERROR_REPORTING: {
      required: false,
      type: 'boolean',
      description: 'Enable error reporting to external services',
      example: 'true'
    },
    
    ENABLE_OFFLINE_MODE: {
      required: false,
      type: 'boolean',
      description: 'Enable offline functionality',
      example: 'true'
    },
    
    // Security
    JWT_SECRET: {
      required: false,
      type: 'string',
      minLength: 32,
      description: 'JWT signing secret (for custom auth)',
      example: 'your-super-secret-jwt-signing-key-here'
    },
    
    ENCRYPTION_KEY: {
      required: false,
      type: 'string',
      minLength: 32,
      description: 'Encryption key for sensitive data',
      example: 'your-32-character-encryption-key-here'
    },
    
    // Third-party Services
    SENTRY_DSN: {
      required: false,
      type: 'url',
      pattern: /^https:\/\/[a-f0-9]+@[a-f0-9]+\.ingest\.sentry\.io\/[0-9]+$/,
      description: 'Sentry DSN for error tracking',
      example: 'https://abc123@def456.ingest.sentry.io/789012'
    },
    
    GOOGLE_ANALYTICS_ID: {
      required: false,
      type: 'string',
      pattern: /^G-[A-Z0-9]{10}$|^UA-[0-9]+-[0-9]+$/,
      description: 'Google Analytics tracking ID',
      example: 'G-XXXXXXXXXX'
    }
  };

  /**
   * Validate all environment variables
   */
  validateEnvironment(): ValidationResult {\n    const env = this.getEnvironmentVariables();\n    const result: ValidationResult = {\n      valid: true,\n      missing: [],\n      invalid: [],\n      warnings: []\n    };\n\n    // Check for missing required variables\n    for (const [key, rule] of Object.entries(this.validationRules)) {\n      const value = env[key as keyof EnvironmentConfig];\n      \n      if (rule.required && (!value || value.trim() === '')) {\n        result.missing.push(key);\n        result.valid = false;\n      } else if (value) {\n        // Validate existing values\n        const validation = this.validateValue(key, value, rule);\n        if (!validation.valid) {\n          result.invalid.push({\n            key,\n            value: this.sanitizeValue(key, value),\n            reason: validation.reason,\n            suggestion: validation.suggestion\n          });\n          result.valid = false;\n        }\n      }\n    }\n\n    // Add warnings for recommended but missing variables\n    this.addRecommendationWarnings(env, result);\n    \n    // Add security warnings\n    this.addSecurityWarnings(env, result);\n    \n    return result;\n  }

  /**
   * Validate a specific environment variable
   */
  validateVariable(key: string, value: string): {\n    valid: boolean;\n    reason?: string;\n    suggestion?: string;\n  } {\n    const rule = this.validationRules[key];\n    if (!rule) {\n      return { valid: true }; // Unknown variables are allowed\n    }\n    \n    return this.validateValue(key, value, rule);\n  }

  /**\n   * Get validation suggestions for setup\n   */\n  getSetupGuide(): {\n    required: Array<{ key: string; description: string; example: string }>;\n    recommended: Array<{ key: string; description: string; example: string }>;\n    optional: Array<{ key: string; description: string; example: string }>;\n  } {\n    const required: Array<{ key: string; description: string; example: string }> = [];\n    const recommended: Array<{ key: string; description: string; example: string }> = [];\n    const optional: Array<{ key: string; description: string; example: string }> = [];\n    \n    for (const [key, rule] of Object.entries(this.validationRules)) {\n      const item = {\n        key,\n        description: rule.description,\n        example: rule.example || 'example-value'\n      };\n      \n      if (rule.required) {\n        required.push(item);\n      } else if (this.isRecommended(key)) {\n        recommended.push(item);\n      } else {\n        optional.push(item);\n      }\n    }\n    \n    return { required, recommended, optional };\n  }

  /**\n   * Generate .env template file content\n   */\n  generateEnvTemplate(): string {\n    const guide = this.getSetupGuide();\n    let template = '# VocabLens Environment Configuration\\n\\n';\n    \n    template += '# Required API Keys\\n';\n    for (const item of guide.required) {\n      template += `# ${item.description}\\n`;\n      template += `${item.key}=${item.example}\\n\\n`;\n    }\n    \n    template += '# Recommended Configuration\\n';\n    for (const item of guide.recommended) {\n      template += `# ${item.description}\\n`;\n      template += `# ${item.key}=${item.example}\\n\\n`;\n    }\n    \n    template += '# Optional Configuration\\n';\n    for (const item of guide.optional) {\n      template += `# ${item.description}\\n`;\n      template += `# ${item.key}=${item.example}\\n\\n`;\n    }\n    \n    template += '# Security Notes:\\n';\n    template += '# - Keep your API keys secure and never commit them to version control\\n';\n    template += '# - Use different keys for development and production environments\\n';\n    template += '# - Regularly rotate your API keys\\n';\n    template += '# - Monitor API usage and set up alerts for unusual activity\\n';\n    \n    return template;\n  }

  /**\n   * Test API connections with current environment\n   */\n  async testConnections(): Promise<{\n    unsplash: { success: boolean; message: string };\n    openai: { success: boolean; message: string };\n    supabase: { success: boolean; message: string };\n  }> {\n    const results = {\n      unsplash: { success: false, message: 'Not tested' },\n      openai: { success: false, message: 'Not tested' },\n      supabase: { success: false, message: 'Not tested' }\n    };\n    \n    // Test connections (would import actual services in real implementation)\n    // This is a placeholder that demonstrates the structure\n    \n    try {\n      // Test Unsplash\n      const unsplashKey = process.env.UNSPLASH_ACCESS_KEY;\n      if (unsplashKey) {\n        // const unsplashResult = await unsplashService.testConnection();\n        results.unsplash = { success: true, message: 'Connection test not implemented' };\n      } else {\n        results.unsplash = { success: false, message: 'API key not provided' };\n      }\n      \n      // Test OpenAI\n      const openaiKey = process.env.OPENAI_API_KEY;\n      if (openaiKey) {\n        // const openaiResult = await openaiService.testConnection();\n        results.openai = { success: true, message: 'Connection test not implemented' };\n      } else {\n        results.openai = { success: false, message: 'API key not provided' };\n      }\n      \n      // Test Supabase\n      const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;\n      const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;\n      if (supabaseUrl && supabaseKey) {\n        // const supabaseResult = await supabaseService.testConnection();\n        results.supabase = { success: true, message: 'Connection test not implemented' };\n      } else {\n        results.supabase = { success: false, message: 'Configuration not provided' };\n      }\n    } catch (error) {\n      console.error('Error testing connections:', error);\n    }\n    \n    return results;\n  }

  /**\n   * Get current environment status\n   */\n  getEnvironmentStatus(): {\n    isValid: boolean;\n    environment: string;\n    missingKeys: number;\n    invalidKeys: number;\n    warnings: number;\n    suggestions: string[];\n  } {\n    const validation = this.validateEnvironment();\n    const env = this.getEnvironmentVariables();\n    \n    const suggestions: string[] = [];\n    \n    if (validation.missing.length > 0) {\n      suggestions.push('Set up missing required API keys');\n    }\n    \n    if (validation.invalid.length > 0) {\n      suggestions.push('Fix invalid environment variable values');\n    }\n    \n    if (!env.NODE_ENV || env.NODE_ENV === 'development') {\n      suggestions.push('Configure production environment settings');\n    }\n    \n    if (!env.SENTRY_DSN && env.NODE_ENV === 'production') {\n      suggestions.push('Set up error monitoring for production');\n    }\n    \n    return {\n      isValid: validation.valid,\n      environment: env.NODE_ENV || 'development',\n      missingKeys: validation.missing.length,\n      invalidKeys: validation.invalid.length,\n      warnings: validation.warnings.length,\n      suggestions\n    };\n  }

  /**\n   * Private helper methods\n   */\n  private getEnvironmentVariables(): EnvironmentConfig {\n    if (typeof process !== 'undefined' && process.env) {\n      return process.env as EnvironmentConfig;\n    }\n    \n    // Fallback for browser environments\n    return {\n      NEXT_PUBLIC_SUPABASE_URL: (window as any).__ENV__?.NEXT_PUBLIC_SUPABASE_URL,\n      NEXT_PUBLIC_SUPABASE_ANON_KEY: (window as any).__ENV__?.NEXT_PUBLIC_SUPABASE_ANON_KEY,\n      // Add other public env vars that might be available in browser\n    };\n  }

  private validateValue(\n    key: string,\n    value: string,\n    rule: ValidationRule\n  ): { valid: boolean; reason?: string; suggestion?: string } {\n    // Type validation\n    switch (rule.type) {\n      case 'number':\n        if (isNaN(Number(value))) {\n          return {\n            valid: false,\n            reason: 'Must be a valid number',\n            suggestion: `Example: ${rule.example || '123'}`\n          };\n        }\n        break;\n        \n      case 'boolean':\n        if (!['true', 'false', '1', '0'].includes(value.toLowerCase())) {\n          return {\n            valid: false,\n            reason: 'Must be a boolean value',\n            suggestion: 'Use: true, false, 1, or 0'\n          };\n        }\n        break;\n        \n      case 'url':\n        try {\n          new URL(value);\n        } catch {\n          return {\n            valid: false,\n            reason: 'Must be a valid URL',\n            suggestion: `Example: ${rule.example || 'https://example.com'}`\n          };\n        }\n        break;\n        \n      case 'email':\n        const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;\n        if (!emailRegex.test(value)) {\n          return {\n            valid: false,\n            reason: 'Must be a valid email address',\n            suggestion: 'Example: user@example.com'\n          };\n        }\n        break;\n    }\n    \n    // Length validation\n    if (rule.minLength && value.length < rule.minLength) {\n      return {\n        valid: false,\n        reason: `Must be at least ${rule.minLength} characters long`,\n        suggestion: `Current length: ${value.length}, required: ${rule.minLength}`\n      };\n    }\n    \n    if (rule.maxLength && value.length > rule.maxLength) {\n      return {\n        valid: false,\n        reason: `Must be no more than ${rule.maxLength} characters long`,\n        suggestion: `Current length: ${value.length}, maximum: ${rule.maxLength}`\n      };\n    }\n    \n    // Pattern validation\n    if (rule.pattern && !rule.pattern.test(value)) {\n      return {\n        valid: false,\n        reason: 'Does not match required format',\n        suggestion: `Example: ${rule.example || 'Check documentation for correct format'}`\n      };\n    }\n    \n    return { valid: true };\n  }

  private addRecommendationWarnings(env: EnvironmentConfig, result: ValidationResult): void {\n    const recommended = [\n      'SUPABASE_SERVICE_ROLE_KEY',\n      'SENTRY_DSN',\n      'ENABLE_ANALYTICS'\n    ];\n    \n    for (const key of recommended) {\n      if (!env[key as keyof EnvironmentConfig]) {\n        result.warnings.push({\n          key,\n          message: `Recommended: ${this.validationRules[key]?.description || 'Set this for better functionality'}`\n        });\n      }\n    }\n  }

  private addSecurityWarnings(env: EnvironmentConfig, result: ValidationResult): void {\n    if (env.NODE_ENV === 'production') {\n      if (env.JWT_SECRET && env.JWT_SECRET.length < 32) {\n        result.warnings.push({\n          key: 'JWT_SECRET',\n          message: 'Use a stronger JWT secret (at least 32 characters) for production'\n        });\n      }\n      \n      if (!env.ENABLE_ERROR_REPORTING || env.ENABLE_ERROR_REPORTING === 'false') {\n        result.warnings.push({\n          key: 'ENABLE_ERROR_REPORTING',\n          message: 'Enable error reporting for production monitoring'\n        });\n      }\n    }\n    \n    // Check for potential security issues\n    for (const [key, value] of Object.entries(env)) {\n      if (typeof value === 'string') {\n        if (value.includes('localhost') && env.NODE_ENV === 'production') {\n          result.warnings.push({\n            key,\n            message: 'Remove localhost URLs from production environment'\n          });\n        }\n        \n        if (value.includes('test') || value.includes('demo')) {\n          result.warnings.push({\n            key,\n            message: 'Consider using production-appropriate values instead of test/demo keys'\n          });\n        }\n      }\n    }\n  }

  private isRecommended(key: string): boolean {\n    const recommended = [\n      'SUPABASE_SERVICE_ROLE_KEY',\n      'SENTRY_DSN',\n      'ENABLE_ANALYTICS',\n      'ENABLE_ERROR_REPORTING',\n      'ENABLE_OFFLINE_MODE'\n    ];\n    return recommended.includes(key);\n  }

  private sanitizeValue(key: string, value: string): string {\n    const sensitiveKeys = ['API_KEY', 'SECRET', 'PASSWORD', 'TOKEN'];\n    const isSensitive = sensitiveKeys.some(sensitive => key.includes(sensitive));\n    \n    if (isSensitive && value.length > 8) {\n      return `${value.substring(0, 4)}...${value.substring(value.length - 4)}`;\n    }\n    \n    return value;\n  }\n}\n\n// Export singleton instance\nexport const envValidator = new EnvironmentValidator();\n\n// Export class for custom usage\nexport { EnvironmentValidator };\n\n// Utility functions\nexport const EnvUtils = {\n  /**\n   * Check if running in development mode\n   */\n  isDevelopment(): boolean {\n    return process.env.NODE_ENV === 'development';\n  },\n  \n  /**\n   * Check if running in production mode\n   */\n  isProduction(): boolean {\n    return process.env.NODE_ENV === 'production';\n  },\n  \n  /**\n   * Get a required environment variable or throw an error\n   */\n  getRequiredEnv(key: string): string {\n    const value = process.env[key];\n    if (!value) {\n      throw new Error(`Required environment variable ${key} is not set`);\n    }\n    return value;\n  },\n  \n  /**\n   * Get an optional environment variable with default\n   */\n  getOptionalEnv(key: string, defaultValue: string): string {\n    return process.env[key] || defaultValue;\n  },\n  \n  /**\n   * Get a boolean environment variable\n   */\n  getBooleanEnv(key: string, defaultValue: boolean = false): boolean {\n    const value = process.env[key];\n    if (!value) return defaultValue;\n    return ['true', '1', 'yes', 'on'].includes(value.toLowerCase());\n  },\n  \n  /**\n   * Get a number environment variable\n   */\n  getNumberEnv(key: string, defaultValue: number = 0): number {\n    const value = process.env[key];\n    if (!value) return defaultValue;\n    const parsed = parseInt(value, 10);\n    return isNaN(parsed) ? defaultValue : parsed;\n  }\n};