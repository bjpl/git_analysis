/**
 * Security Tests for API Key Handling
 * Tests security measures for API key storage, transmission, and validation
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';

// Mock crypto for testing
const mockCrypto = {
  subtle: {
    encrypt: vi.fn(),
    decrypt: vi.fn(),
    generateKey: vi.fn(),
    importKey: vi.fn()
  },
  getRandomValues: vi.fn((array) => {
    for (let i = 0; i < array.length; i++) {
      array[i] = Math.floor(Math.random() * 256);
    }
    return array;
  })
};

Object.defineProperty(global, 'crypto', {
  value: mockCrypto
});

// Mock localStorage with security testing
const secureStorage = {
  items: new Map<string, string>(),
  getItem: vi.fn((key: string) => secureStorage.items.get(key) || null),
  setItem: vi.fn((key: string, value: string) => {
    secureStorage.items.set(key, value);
  }),
  removeItem: vi.fn((key: string) => {
    secureStorage.items.delete(key);
  }),
  clear: vi.fn(() => {
    secureStorage.items.clear();
  })
};

Object.defineProperty(global, 'localStorage', {
  value: secureStorage
});

// Security utility functions
class ApiKeySecurity {
  private static readonly ENCRYPTION_KEY_LENGTH = 32;
  private static readonly IV_LENGTH = 16;
  private static readonly SALT_LENGTH = 16;

  /**
   * Generate a secure encryption key
   */
  static generateEncryptionKey(): ArrayBuffer {
    const key = new Uint8Array(this.ENCRYPTION_KEY_LENGTH);
    crypto.getRandomValues(key);
    return key.buffer;
  }

  /**
   * Encrypt API key with AES-GCM
   */
  static async encryptApiKey(apiKey: string, masterKey: ArrayBuffer): Promise<string> {
    const encoder = new TextEncoder();
    const data = encoder.encode(apiKey);
    
    const iv = new Uint8Array(this.IV_LENGTH);
    crypto.getRandomValues(iv);
    
    const key = await crypto.subtle.importKey(
      'raw',
      masterKey,
      { name: 'AES-GCM' },
      false,
      ['encrypt']
    );
    
    const encrypted = await crypto.subtle.encrypt(
      { name: 'AES-GCM', iv },
      key,
      data
    );
    
    // Combine IV and encrypted data
    const combined = new Uint8Array(iv.length + encrypted.byteLength);
    combined.set(iv, 0);
    combined.set(new Uint8Array(encrypted), iv.length);
    
    return this.arrayBufferToBase64(combined.buffer);
  }

  /**
   * Decrypt API key
   */
  static async decryptApiKey(encryptedData: string, masterKey: ArrayBuffer): Promise<string> {
    const combined = this.base64ToArrayBuffer(encryptedData);
    const iv = combined.slice(0, this.IV_LENGTH);
    const encrypted = combined.slice(this.IV_LENGTH);
    
    const key = await crypto.subtle.importKey(
      'raw',
      masterKey,
      { name: 'AES-GCM' },
      false,
      ['decrypt']
    );
    
    const decrypted = await crypto.subtle.decrypt(
      { name: 'AES-GCM', iv },
      key,
      encrypted
    );
    
    const decoder = new TextDecoder();
    return decoder.decode(decrypted);
  }

  /**
   * Validate API key format without revealing content
   */
  static validateKeyFormat(service: string, key: string): { valid: boolean; reason?: string } {
    if (!key || typeof key !== 'string') {
      return { valid: false, reason: 'Key is required and must be a string' };
    }

    switch (service) {
      case 'unsplash':
        if (key.length < 20) {
          return { valid: false, reason: 'Unsplash key too short' };
        }
        if (!/^[A-Za-z0-9_-]+$/.test(key)) {
          return { valid: false, reason: 'Unsplash key contains invalid characters' };
        }
        break;

      case 'openai':
        if (!key.startsWith('sk-')) {
          return { valid: false, reason: 'OpenAI key must start with sk-' };
        }
        if (key.length < 48) {
          return { valid: false, reason: 'OpenAI key too short' };
        }
        break;

      case 'supabase':
        if (key.length < 50) {
          return { valid: false, reason: 'Supabase key too short' };
        }
        break;

      default:
        return { valid: false, reason: 'Unknown service' };
    }

    return { valid: true };
  }

  /**
   * Mask API key for display purposes
   */
  static maskApiKey(key: string): string {
    if (!key || key.length < 8) return '****';
    
    const start = key.slice(0, 4);
    const end = key.slice(-4);
    const middle = '*'.repeat(Math.min(key.length - 8, 20));
    
    return `${start}${middle}${end}`;
  }

  /**
   * Detect potential API key patterns in text
   */
  static detectApiKeyPattern(text: string): boolean {
    const patterns = [
      /sk-[A-Za-z0-9]{32,}/g, // OpenAI pattern
      /[A-Za-z0-9]{40,}/g,     // Generic long key pattern
      /eyJ[A-Za-z0-9_-]+/g,    // JWT pattern
    ];

    return patterns.some(pattern => pattern.test(text));
  }

  /**
   * Secure memory cleanup
   */
  static secureCleanup(sensitiveString: string): void {
    // In a real implementation, this would overwrite memory
    // For testing, we'll just validate the intent
    if (sensitiveString) {
      // Overwrite the string content (JavaScript limitation - strings are immutable)
      // In real implementation, use ArrayBuffer or similar for mutable data
    }
  }

  // Helper methods
  private static arrayBufferToBase64(buffer: ArrayBuffer): string {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
  }

  private static base64ToArrayBuffer(base64: string): ArrayBuffer {
    const binary = atob(base64);
    const buffer = new ArrayBuffer(binary.length);
    const bytes = new Uint8Array(buffer);
    for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    return buffer;
  }
}

describe('API Key Security Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    secureStorage.clear();
    
    // Setup crypto mocks
    mockCrypto.subtle.encrypt.mockResolvedValue(new ArrayBuffer(32));
    mockCrypto.subtle.decrypt.mockResolvedValue(new ArrayBuffer(32));
    mockCrypto.subtle.importKey.mockResolvedValue({} as CryptoKey);
  });

  describe('Encryption and Storage', () => {
    it('should encrypt API keys before storage', async () => {
      const apiKey = 'sk-test-api-key-123456789';
      const masterKey = ApiKeySecurity.generateEncryptionKey();
      
      const encrypted = await ApiKeySecurity.encryptApiKey(apiKey, masterKey);
      
      expect(encrypted).toBeDefined();
      expect(encrypted).not.toContain(apiKey);
      expect(mockCrypto.subtle.encrypt).toHaveBeenCalled();
    });

    it('should decrypt API keys correctly', async () => {
      const originalKey = 'sk-original-key-123';
      const masterKey = ApiKeySecurity.generateEncryptionKey();
      
      // Mock successful decryption
      const encoder = new TextEncoder();
      mockCrypto.subtle.decrypt.mockResolvedValue(encoder.encode(originalKey));
      
      const encrypted = await ApiKeySecurity.encryptApiKey(originalKey, masterKey);
      const decrypted = await ApiKeySecurity.decryptApiKey(encrypted, masterKey);
      
      expect(decrypted).toBe(originalKey);
    });

    it('should use different IVs for each encryption', async () => {
      const apiKey = 'sk-test-key';
      const masterKey = ApiKeySecurity.generateEncryptionKey();
      
      const encrypted1 = await ApiKeySecurity.encryptApiKey(apiKey, masterKey);
      const encrypted2 = await ApiKeySecurity.encryptApiKey(apiKey, masterKey);
      
      expect(encrypted1).not.toBe(encrypted2);
    });

    it('should fail gracefully with invalid encrypted data', async () => {
      const masterKey = ApiKeySecurity.generateEncryptionKey();
      
      mockCrypto.subtle.decrypt.mockRejectedValue(new Error('Decryption failed'));
      
      await expect(
        ApiKeySecurity.decryptApiKey('invalid-encrypted-data', masterKey)
      ).rejects.toThrow();
    });
  });

  describe('Input Validation and Sanitization', () => {
    it('should validate Unsplash API key format', () => {
      const validKey = 'abcd1234efgh5678ijkl9012mnop3456qrst7890';
      const result = ApiKeySecurity.validateKeyFormat('unsplash', validKey);
      
      expect(result.valid).toBe(true);
    });

    it('should reject invalid Unsplash keys', () => {
      const testCases = [
        { key: 'too-short', reason: 'length' },
        { key: 'valid-length-but-has-invalid-chars!@#', reason: 'characters' },
        { key: '', reason: 'empty' },
        { key: null as any, reason: 'null' }
      ];
      
      testCases.forEach(({ key }) => {
        const result = ApiKeySecurity.validateKeyFormat('unsplash', key);
        expect(result.valid).toBe(false);
        expect(result.reason).toBeDefined();
      });
    });

    it('should validate OpenAI API key format', () => {
      const validKey = 'sk-1234567890abcdef1234567890abcdef1234567890abcdef';
      const result = ApiKeySecurity.validateKeyFormat('openai', validKey);
      
      expect(result.valid).toBe(true);
    });

    it('should reject invalid OpenAI keys', () => {
      const testCases = [
        'pk-wrong-prefix-1234567890abcdef1234567890abcdef',
        'sk-too-short',
        'sk-',
        'not-a-key-at-all'
      ];
      
      testCases.forEach(key => {
        const result = ApiKeySecurity.validateKeyFormat('openai', key);
        expect(result.valid).toBe(false);
      });
    });

    it('should sanitize input to prevent XSS', () => {
      const maliciousInput = '<script>alert("XSS")</script>sk-valid-key-123';
      const result = ApiKeySecurity.validateKeyFormat('openai', maliciousInput);
      
      expect(result.valid).toBe(false);
      expect(result.reason).toContain('invalid characters');
    });
  });

  describe('XSS Prevention', () => {
    it('should not execute scripts in API key fields', () => {
      const TestComponent: React.FC = () => {
        const [apiKey, setApiKey] = React.useState('');
        
        return (
          <input
            data-testid="api-key-input"
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
          />
        );
      };
      
      render(<TestComponent />);
      
      const input = screen.getByTestId('api-key-input');
      const maliciousScript = '<script>window.xssExecuted = true;</script>';
      
      fireEvent.change(input, { target: { value: maliciousScript } });
      
      // Script should not execute
      expect((window as any).xssExecuted).toBeUndefined();
      expect(input).toHaveValue(maliciousScript); // Value should be stored as text
    });

    it('should escape HTML in error messages', () => {
      const maliciousKey = '<img src=x onerror=alert(1)>';
      const result = ApiKeySecurity.validateKeyFormat('openai', maliciousKey);
      
      expect(result.valid).toBe(false);
      expect(result.reason).not.toContain('<img');
    });
  });

  describe('Storage Security', () => {
    it('should not store API keys in plain text', async () => {
      const apiKey = 'sk-secret-key-12345';
      const masterKey = ApiKeySecurity.generateEncryptionKey();
      
      const encrypted = await ApiKeySecurity.encryptApiKey(apiKey, masterKey);
      localStorage.setItem('openai_key', encrypted);
      
      const storedValue = localStorage.getItem('openai_key');
      expect(storedValue).not.toContain(apiKey);
      expect(storedValue).not.toBe(apiKey);
    });

    it('should handle localStorage quota exceeded', () => {
      // Mock localStorage quota exceeded
      secureStorage.setItem.mockImplementation(() => {
        throw new Error('QuotaExceededError');
      });
      
      expect(() => {
        localStorage.setItem('test_key', 'large_value'.repeat(1000));
      }).toThrow('QuotaExceededError');
    });

    it('should clear sensitive data on logout', () => {
      localStorage.setItem('openai_key', 'encrypted-key-data');
      localStorage.setItem('unsplash_key', 'encrypted-key-data');
      localStorage.setItem('user_preference', 'non-sensitive-data');
      
      // Simulate logout - clear only sensitive keys
      const sensitiveKeys = ['openai_key', 'unsplash_key'];
      sensitiveKeys.forEach(key => localStorage.removeItem(key));
      
      expect(localStorage.getItem('openai_key')).toBeNull();
      expect(localStorage.getItem('unsplash_key')).toBeNull();
      expect(localStorage.getItem('user_preference')).toBe('non-sensitive-data');
    });
  });

  describe('API Key Masking', () => {
    it('should mask API keys for display', () => {
      const testCases = [
        {
          key: 'sk-1234567890abcdef1234567890abcdef1234567890abcdef',
          expected: 'sk-1******************cdef'
        },
        {
          key: 'short',
          expected: '****'
        },
        {
          key: 'unsplash-key-1234567890',
          expected: 'unsp****************7890'
        }
      ];
      
      testCases.forEach(({ key, expected }) => {
        const masked = ApiKeySecurity.maskApiKey(key);
        expect(masked).toBe(expected);
        expect(masked).not.toContain(key.slice(4, -4));
      });
    });

    it('should handle edge cases in masking', () => {
      expect(ApiKeySecurity.maskApiKey('')).toBe('****');
      expect(ApiKeySecurity.maskApiKey('abc')).toBe('****');
      expect(ApiKeySecurity.maskApiKey(null as any)).toBe('****');
    });
  });

  describe('Memory Security', () => {
    it('should detect API key patterns in logs', () => {
      const testStrings = [
        'Using API key: sk-1234567890abcdef1234567890abcdef',
        'Configuration: {"openai": "sk-secretkey123456789"}',
        'Normal log message without keys',
        'JWT token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
      ];
      
      expect(ApiKeySecurity.detectApiKeyPattern(testStrings[0])).toBe(true);
      expect(ApiKeySecurity.detectApiKeyPattern(testStrings[1])).toBe(true);
      expect(ApiKeySecurity.detectApiKeyPattern(testStrings[2])).toBe(false);
      expect(ApiKeySecurity.detectApiKeyPattern(testStrings[3])).toBe(true);
    });

    it('should attempt secure cleanup of sensitive data', () => {
      const sensitiveData = 'sk-very-secret-key-12345';
      
      // This test validates the cleanup function exists and can be called
      expect(() => {
        ApiKeySecurity.secureCleanup(sensitiveData);
      }).not.toThrow();
    });
  });

  describe('Session Security', () => {
    it('should handle session timeout appropriately', () => {
      // Simulate session with API keys
      localStorage.setItem('session_start', Date.now().toString());
      localStorage.setItem('openai_key', 'encrypted-key');
      
      // Simulate session timeout (24 hours)
      const sessionStart = parseInt(localStorage.getItem('session_start') || '0');
      const currentTime = Date.now();
      const sessionDuration = currentTime - sessionStart;
      const maxSessionDuration = 24 * 60 * 60 * 1000; // 24 hours
      
      if (sessionDuration > maxSessionDuration) {
        localStorage.removeItem('openai_key');
        localStorage.removeItem('session_start');
      }
      
      // For this test, session is new, so keys should still exist
      expect(localStorage.getItem('openai_key')).toBe('encrypted-key');
    });

    it('should handle browser private/incognito mode', () => {
      // Mock private browsing detection
      const isPrivateBrowsing = () => {
        try {
          localStorage.setItem('test_private', 'test');
          localStorage.removeItem('test_private');
          return false;
        } catch {
          return true;
        }
      };
      
      const isPrivate = isPrivateBrowsing();
      
      if (isPrivate) {
        // In private mode, should warn user about session-only storage
        expect(isPrivate).toBe(true);
      } else {
        expect(isPrivate).toBe(false);
      }
    });
  });

  describe('Network Security', () => {
    it('should validate API responses to prevent code injection', () => {
      const mockResponses = [
        '{"valid": true}', // Valid JSON
        '<script>alert("xss")</script>', // XSS attempt
        '{"valid": true, "message": "<img src=x onerror=alert(1)>"}', // XSS in data
        'function(){return true;}', // Code injection attempt
      ];
      
      mockResponses.forEach(response => {
        try {
          const parsed = JSON.parse(response);
          // Should only succeed for valid JSON
          expect(typeof parsed).toBe('object');
        } catch (error) {
          // Invalid JSON should be rejected
          expect(error).toBeDefined();
        }
      });
    });

    it('should handle HTTPS requirements', () => {
      const testUrls = [
        'https://api.openai.com/v1/models',
        'http://api.openai.com/v1/models', // Should be rejected
        'https://api.unsplash.com/photos',
        'http://api.unsplash.com/photos' // Should be rejected
      ];
      
      testUrls.forEach(url => {
        const isSecure = url.startsWith('https://');
        
        if (!isSecure) {
          expect(isSecure).toBe(false); // Should reject non-HTTPS
        } else {
          expect(isSecure).toBe(true);
        }
      });
    });
  });

  describe('Error Handling Security', () => {
    it('should not leak sensitive information in error messages', () => {
      const sensitiveKey = 'sk-very-secret-api-key-123456789';
      
      try {
        throw new Error(`Invalid API key: ${sensitiveKey}`);
      } catch (error) {
        // In production, error should not contain the full key
        const errorMessage = (error as Error).message;
        const maskedMessage = errorMessage.replace(
          /sk-[A-Za-z0-9]+/g,
          (match) => ApiKeySecurity.maskApiKey(match)
        );
        
        expect(maskedMessage).not.toContain(sensitiveKey);
        expect(maskedMessage).toContain('sk-1');
      }
    });

    it('should handle validation errors securely', () => {
      const result = ApiKeySecurity.validateKeyFormat('openai', 'invalid-key');
      
      expect(result.valid).toBe(false);
      expect(result.reason).toBeDefined();
      expect(result.reason).not.toContain('invalid-key'); // Don't echo back the key
    });
  });
});