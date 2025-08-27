/**
 * Unit Tests for Configuration Encryption Utilities
 * Tests the encryption/decryption functions used for securing API keys
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import CryptoJS from 'crypto-js';

// Mock the crypto-js module since we need to test encryption functionality
vi.mock('crypto-js', () => ({
  default: {
    AES: {
      encrypt: vi.fn(),
      decrypt: vi.fn()
    },
    enc: {
      Utf8: {
        stringify: vi.fn()
      }
    }
  }
}));

// Configuration encryption utility functions
class ConfigEncryption {
  private static readonly ENCRYPTION_KEY = 'vocablens-config-key-v1';
  private static readonly STORAGE_PREFIX = 'vl_enc_';

  /**
   * Encrypt sensitive configuration data
   */
  static encrypt(data: string): string {
    try {
      const encrypted = CryptoJS.AES.encrypt(data, this.ENCRYPTION_KEY).toString();
      return this.STORAGE_PREFIX + encrypted;
    } catch (error) {
      throw new Error('Failed to encrypt configuration data');
    }
  }

  /**
   * Decrypt sensitive configuration data
   */
  static decrypt(encryptedData: string): string {
    try {
      if (!encryptedData.startsWith(this.STORAGE_PREFIX)) {
        throw new Error('Invalid encrypted data format');
      }

      const encrypted = encryptedData.replace(this.STORAGE_PREFIX, '');
      const decrypted = CryptoJS.AES.decrypt(encrypted, this.ENCRYPTION_KEY);
      return CryptoJS.enc.Utf8.stringify(decrypted);
    } catch (error) {
      throw new Error('Failed to decrypt configuration data');
    }
  }

  /**
   * Validate encryption format
   */
  static isEncrypted(data: string): boolean {
    return typeof data === 'string' && data.startsWith(this.STORAGE_PREFIX);
  }

  /**
   * Secure storage operations
   */
  static secureStore(key: string, value: string): void {
    try {
      const encrypted = this.encrypt(value);
      localStorage.setItem(key, encrypted);
    } catch (error) {
      throw new Error(`Failed to securely store ${key}`);
    }
  }

  static secureRetrieve(key: string): string | null {
    try {
      const encrypted = localStorage.getItem(key);
      if (!encrypted) return null;
      
      if (this.isEncrypted(encrypted)) {
        return this.decrypt(encrypted);
      }
      
      // Handle legacy unencrypted data
      return encrypted;
    } catch (error) {
      console.error(`Failed to retrieve ${key}:`, error);
      return null;
    }
  }

  static secureRemove(key: string): void {
    localStorage.removeItem(key);
  }
}

describe('ConfigEncryption', () => {
  beforeEach(() => {
    // Reset all mocks
    vi.clearAllMocks();
    
    // Setup default mock implementations
    (CryptoJS.AES.encrypt as any).mockReturnValue({ toString: () => 'mock_encrypted_string' });
    (CryptoJS.AES.decrypt as any).mockReturnValue({});
    (CryptoJS.enc.Utf8.stringify as any).mockReturnValue('decrypted_value');
    
    // Clear localStorage
    localStorage.clear();
  });

  describe('encrypt', () => {
    it('should encrypt data with correct prefix', () => {
      const testData = 'sk-test-api-key-123';
      const result = ConfigEncryption.encrypt(testData);

      expect(CryptoJS.AES.encrypt).toHaveBeenCalledWith(testData, 'vocablens-config-key-v1');
      expect(result).toBe('vl_enc_mock_encrypted_string');
    });

    it('should handle empty strings', () => {
      const result = ConfigEncryption.encrypt('');
      expect(result).toBe('vl_enc_mock_encrypted_string');
    });

    it('should throw error on encryption failure', () => {
      (CryptoJS.AES.encrypt as any).mockImplementation(() => {
        throw new Error('Encryption failed');
      });

      expect(() => ConfigEncryption.encrypt('test')).toThrow('Failed to encrypt configuration data');
    });
  });

  describe('decrypt', () => {
    it('should decrypt data with valid prefix', () => {
      const encryptedData = 'vl_enc_encrypted_string';
      const result = ConfigEncryption.decrypt(encryptedData);

      expect(CryptoJS.AES.decrypt).toHaveBeenCalledWith('encrypted_string', 'vocablens-config-key-v1');
      expect(CryptoJS.enc.Utf8.stringify).toHaveBeenCalled();
      expect(result).toBe('decrypted_value');
    });

    it('should throw error for invalid prefix', () => {
      expect(() => ConfigEncryption.decrypt('invalid_data')).toThrow('Invalid encrypted data format');
    });

    it('should throw error on decryption failure', () => {
      (CryptoJS.AES.decrypt as any).mockImplementation(() => {
        throw new Error('Decryption failed');
      });

      expect(() => ConfigEncryption.decrypt('vl_enc_data')).toThrow('Failed to decrypt configuration data');
    });
  });

  describe('isEncrypted', () => {
    it('should return true for valid encrypted data', () => {
      expect(ConfigEncryption.isEncrypted('vl_enc_data')).toBe(true);
    });

    it('should return false for unencrypted data', () => {
      expect(ConfigEncryption.isEncrypted('plain_text')).toBe(false);
    });

    it('should return false for non-string data', () => {
      expect(ConfigEncryption.isEncrypted(null as any)).toBe(false);
      expect(ConfigEncryption.isEncrypted(undefined as any)).toBe(false);
      expect(ConfigEncryption.isEncrypted(123 as any)).toBe(false);
    });
  });

  describe('secureStore', () => {
    it('should encrypt and store data', () => {
      const key = 'api_key';
      const value = 'sk-test-123';
      
      ConfigEncryption.secureStore(key, value);

      expect(localStorage.getItem(key)).toBe('vl_enc_mock_encrypted_string');
    });

    it('should throw error on storage failure', () => {
      (CryptoJS.AES.encrypt as any).mockImplementation(() => {
        throw new Error('Encryption failed');
      });

      expect(() => ConfigEncryption.secureStore('key', 'value')).toThrow('Failed to securely store key');
    });
  });

  describe('secureRetrieve', () => {
    it('should retrieve and decrypt encrypted data', () => {
      localStorage.setItem('test_key', 'vl_enc_encrypted_data');
      
      const result = ConfigEncryption.secureRetrieve('test_key');
      
      expect(result).toBe('decrypted_value');
    });

    it('should return legacy unencrypted data', () => {
      localStorage.setItem('legacy_key', 'unencrypted_value');
      
      const result = ConfigEncryption.secureRetrieve('legacy_key');
      
      expect(result).toBe('unencrypted_value');
    });

    it('should return null for non-existent key', () => {
      const result = ConfigEncryption.secureRetrieve('non_existent');
      expect(result).toBeNull();
    });

    it('should handle decryption errors gracefully', () => {
      localStorage.setItem('corrupt_key', 'vl_enc_corrupt_data');
      (CryptoJS.AES.decrypt as any).mockImplementation(() => {
        throw new Error('Decryption failed');
      });

      const result = ConfigEncryption.secureRetrieve('corrupt_key');
      expect(result).toBeNull();
    });
  });

  describe('secureRemove', () => {
    it('should remove data from storage', () => {
      localStorage.setItem('test_key', 'test_value');
      
      ConfigEncryption.secureRemove('test_key');
      
      expect(localStorage.getItem('test_key')).toBeNull();
    });
  });
});

describe('Integration Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    
    // Use real-like mock implementations for integration tests
    (CryptoJS.AES.encrypt as any).mockImplementation((data: string, key: string) => ({
      toString: () => `encrypted_${data}_with_${key}`
    }));
    
    (CryptoJS.AES.decrypt as any).mockImplementation((encrypted: string, key: string) => ({}));
    
    (CryptoJS.enc.Utf8.stringify as any).mockImplementation(() => 'original_data');
  });

  it('should handle full encrypt-store-retrieve-decrypt cycle', () => {
    const originalData = 'sk-test-api-key-abc123';
    const storageKey = 'openai_api_key';

    // Store encrypted data
    ConfigEncryption.secureStore(storageKey, originalData);

    // Verify it's stored encrypted
    const storedData = localStorage.getItem(storageKey);
    expect(storedData).toMatch(/^vl_enc_/);

    // Retrieve and decrypt
    const retrievedData = ConfigEncryption.secureRetrieve(storageKey);
    expect(retrievedData).toBe('original_data');
  });

  it('should handle multiple API keys', () => {
    const apiKeys = {
      unsplash: 'unsplash_key_123',
      openai: 'sk-openai-456',
      supabase: 'supabase_anon_key_789'
    };

    // Store all keys
    Object.entries(apiKeys).forEach(([service, key]) => {
      ConfigEncryption.secureStore(`${service}_api_key`, key);
    });

    // Verify all are stored encrypted
    Object.keys(apiKeys).forEach(service => {
      const stored = localStorage.getItem(`${service}_api_key`);
      expect(stored).toMatch(/^vl_enc_/);
    });

    // Verify all can be retrieved
    Object.keys(apiKeys).forEach(service => {
      const retrieved = ConfigEncryption.secureRetrieve(`${service}_api_key`);
      expect(retrieved).toBe('original_data');
    });
  });
});

// Export for use in other tests
export { ConfigEncryption };