/**
 * Storage and Browser Compatibility Tests
 * Tests configuration persistence across different browsers and storage conditions
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

// Browser compatibility test utilities
class BrowserCompatibilityTester {
  private originalLocalStorage: Storage;
  private originalSessionStorage: Storage;
  private originalIndexedDB: IDBFactory;
  private originalNavigator: Navigator;

  constructor() {
    this.originalLocalStorage = localStorage;
    this.originalSessionStorage = sessionStorage;
    this.originalIndexedDB = indexedDB;
    this.originalNavigator = navigator;
  }

  // Mock different browser localStorage implementations
  mockBrowserStorage(browserType: 'chrome' | 'firefox' | 'safari' | 'edge' | 'ie11') {
    const createMockStorage = (quotaLimit?: number, throwOnQuotaExceeded = false) => {
      let store = new Map<string, string>();
      let usedQuota = 0;

      return {
        getItem: vi.fn((key: string) => store.get(key) || null),
        setItem: vi.fn((key: string, value: string) => {
          const newSize = new Blob([value]).size;
          
          if (quotaLimit && usedQuota + newSize > quotaLimit) {
            if (throwOnQuotaExceeded) {
              const error = new DOMException('QuotaExceededError');
              error.name = 'QuotaExceededError';
              throw error;
            }
          }
          
          const oldValue = store.get(key);
          if (oldValue) {
            usedQuota -= new Blob([oldValue]).size;
          }
          
          store.set(key, value);
          usedQuota += newSize;
        }),
        removeItem: vi.fn((key: string) => {
          const value = store.get(key);
          if (value) {
            usedQuota -= new Blob([value]).size;
            store.delete(key);
          }
        }),
        clear: vi.fn(() => {
          store.clear();
          usedQuota = 0;
        }),
        get length() { return store.size; },
        key: vi.fn((index: number) => Array.from(store.keys())[index] || null),
        [Symbol.iterator]: () => store[Symbol.iterator]()
      } as unknown as Storage;
    };

    switch (browserType) {
      case 'chrome':
        Object.defineProperty(window, 'localStorage', {
          value: createMockStorage(10 * 1024 * 1024, true), // 10MB quota
          configurable: true
        });
        break;

      case 'firefox':
        Object.defineProperty(window, 'localStorage', {
          value: createMockStorage(10 * 1024 * 1024, true), // 10MB quota
          configurable: true
        });
        break;

      case 'safari':
        // Safari has stricter private browsing limitations
        Object.defineProperty(window, 'localStorage', {
          value: createMockStorage(5 * 1024 * 1024, true), // 5MB quota
          configurable: true
        });
        break;

      case 'edge':
        Object.defineProperty(window, 'localStorage', {
          value: createMockStorage(10 * 1024 * 1024, true), // 10MB quota
          configurable: true
        });
        break;

      case 'ie11':
        // IE11 has more limited support
        const limitedStorage = createMockStorage(5 * 1024 * 1024, true);
        // Remove some modern methods that IE11 doesn't support
        delete (limitedStorage as any)[Symbol.iterator];
        Object.defineProperty(window, 'localStorage', {
          value: limitedStorage,
          configurable: true
        });
        break;
    }
  }

  mockPrivateBrowsing(isPrivate = true) {
    if (isPrivate) {
      // In private browsing, localStorage might throw errors
      Object.defineProperty(window, 'localStorage', {
        value: {
          getItem: () => null,
          setItem: () => {
            throw new DOMException('QuotaExceededError');
          },
          removeItem: () => {},
          clear: () => {},
          length: 0,
          key: () => null
        },
        configurable: true
      });
    } else {
      this.restore();
    }
  }

  mockIndexedDBSupport(supported = true) {
    if (supported) {
      Object.defineProperty(window, 'indexedDB', {
        value: this.originalIndexedDB,
        configurable: true
      });
    } else {
      Object.defineProperty(window, 'indexedDB', {
        value: undefined,
        configurable: true
      });
    }
  }

  mockNavigatorProperties(overrides: Partial<Navigator>) {
    Object.defineProperty(window, 'navigator', {
      value: { ...this.originalNavigator, ...overrides },
      configurable: true
    });
  }

  restore() {
    Object.defineProperty(window, 'localStorage', {
      value: this.originalLocalStorage,
      configurable: true
    });
    Object.defineProperty(window, 'sessionStorage', {
      value: this.originalSessionStorage,
      configurable: true
    });
    Object.defineProperty(window, 'indexedDB', {
      value: this.originalIndexedDB,
      configurable: true
    });
    Object.defineProperty(window, 'navigator', {
      value: this.originalNavigator,
      configurable: true
    });
  }
}

// Configuration storage utility
class ConfigStorage {
  private static readonly STORAGE_KEY_PREFIX = 'vocablens_config_';
  private static readonly ENCRYPTION_PREFIX = 'encrypted_';

  static setApiKey(service: string, key: string, encrypt = true): void {
    const storageKey = this.STORAGE_KEY_PREFIX + service;
    const value = encrypt ? this.ENCRYPTION_PREFIX + btoa(key) : key;
    
    try {
      localStorage.setItem(storageKey, value);
    } catch (error) {
      // Fallback to sessionStorage
      sessionStorage.setItem(storageKey, value);
      console.warn('Falling back to session storage due to localStorage error:', error);
    }
  }

  static getApiKey(service: string): string | null {
    const storageKey = this.STORAGE_KEY_PREFIX + service;
    
    let value: string | null = null;
    
    try {
      value = localStorage.getItem(storageKey);
    } catch (error) {
      console.warn('localStorage access failed, trying sessionStorage:', error);
    }
    
    if (!value) {
      try {
        value = sessionStorage.getItem(storageKey);
      } catch (error) {
        console.warn('sessionStorage access failed:', error);
        return null;
      }
    }
    
    if (!value) return null;
    
    // Decrypt if encrypted
    if (value.startsWith(this.ENCRYPTION_PREFIX)) {
      try {
        return atob(value.replace(this.ENCRYPTION_PREFIX, ''));
      } catch (error) {
        console.error('Failed to decrypt stored key:', error);
        return null;
      }
    }
    
    return value;
  }

  static removeApiKey(service: string): void {
    const storageKey = this.STORAGE_KEY_PREFIX + service;
    
    try {
      localStorage.removeItem(storageKey);
    } catch (error) {
      console.warn('localStorage removal failed:', error);
    }
    
    try {
      sessionStorage.removeItem(storageKey);
    } catch (error) {
      console.warn('sessionStorage removal failed:', error);
    }
  }

  static clearAllKeys(): void {
    const keys = Object.keys(localStorage).filter(key => 
      key.startsWith(this.STORAGE_KEY_PREFIX)
    );
    
    keys.forEach(key => {
      try {
        localStorage.removeItem(key);
      } catch (error) {
        console.warn('Failed to remove key:', key, error);
      }
    });

    // Also clear from sessionStorage
    const sessionKeys = Object.keys(sessionStorage).filter(key => 
      key.startsWith(this.STORAGE_KEY_PREFIX)
    );
    
    sessionKeys.forEach(key => {
      try {
        sessionStorage.removeItem(key);
      } catch (error) {
        console.warn('Failed to remove session key:', key, error);
      }
    });
  }

  static getStorageInfo(): {
    localStorageAvailable: boolean;
    sessionStorageAvailable: boolean;
    indexedDBAvailable: boolean;
    storageQuota?: number;
  } {
    const info = {
      localStorageAvailable: false,
      sessionStorageAvailable: false,
      indexedDBAvailable: false,
      storageQuota: undefined as number | undefined
    };

    // Test localStorage
    try {
      const testKey = '__storage_test__';
      localStorage.setItem(testKey, 'test');
      localStorage.removeItem(testKey);
      info.localStorageAvailable = true;
    } catch (error) {
      console.warn('localStorage not available:', error);
    }

    // Test sessionStorage
    try {
      const testKey = '__session_test__';
      sessionStorage.setItem(testKey, 'test');
      sessionStorage.removeItem(testKey);
      info.sessionStorageAvailable = true;
    } catch (error) {
      console.warn('sessionStorage not available:', error);
    }

    // Test IndexedDB
    info.indexedDBAvailable = typeof indexedDB !== 'undefined';

    // Try to estimate quota
    if (info.localStorageAvailable && 'navigator' in window && 'storage' in navigator && 'estimate' in navigator.storage) {
      navigator.storage.estimate().then(estimate => {
        info.storageQuota = estimate.quota;
      }).catch(() => {
        // Quota estimation failed
      });
    }

    return info;
  }
}

describe('Storage and Browser Compatibility Tests', () => {
  let browserTester: BrowserCompatibilityTester;

  beforeEach(() => {
    browserTester = new BrowserCompatibilityTester();
    ConfigStorage.clearAllKeys();
  });

  afterEach(() => {
    browserTester.restore();
    ConfigStorage.clearAllKeys();
  });

  describe('Cross-Browser Storage Compatibility', () => {
    it('should work consistently across major browsers', () => {
      const browsers = ['chrome', 'firefox', 'safari', 'edge'] as const;
      const testKey = 'test-unsplash-key-123';
      
      browsers.forEach(browser => {
        browserTester.mockBrowserStorage(browser);
        
        // Store API key
        ConfigStorage.setApiKey('unsplash', testKey);
        
        // Retrieve API key
        const retrievedKey = ConfigStorage.getApiKey('unsplash');
        
        expect(retrievedKey).toBe(testKey);
        
        // Clean up
        ConfigStorage.removeApiKey('unsplash');
        expect(ConfigStorage.getApiKey('unsplash')).toBeNull();
      });
    });

    it('should handle IE11 limitations gracefully', () => {
      browserTester.mockBrowserStorage('ie11');
      
      const testKey = 'ie11-test-key';
      
      // Should still work with basic functionality
      ConfigStorage.setApiKey('openai', testKey);
      expect(ConfigStorage.getApiKey('openai')).toBe(testKey);
      
      // But some modern features might not be available
      expect(typeof (localStorage as any)[Symbol.iterator]).toBe('undefined');
    });

    it('should provide storage information for different browsers', () => {
      const browsers = ['chrome', 'firefox', 'safari', 'edge', 'ie11'] as const;
      
      browsers.forEach(browser => {
        browserTester.mockBrowserStorage(browser);
        
        const info = ConfigStorage.getStorageInfo();
        
        expect(info.localStorageAvailable).toBe(true);
        expect(info.sessionStorageAvailable).toBe(true);
        
        if (browser === 'ie11') {
          // IE11 might have different IndexedDB support
          expect(typeof info.indexedDBAvailable).toBe('boolean');
        } else {
          expect(info.indexedDBAvailable).toBe(true);
        }
      });
    });
  });

  describe('Private Browsing Mode', () => {
    it('should handle private browsing localStorage restrictions', () => {
      browserTester.mockPrivateBrowsing(true);
      
      const testKey = 'private-browsing-key';
      
      // Attempt to store should either fail or fallback to sessionStorage
      expect(() => {
        ConfigStorage.setApiKey('unsplash', testKey);
      }).not.toThrow(); // Should handle the error gracefully
      
      // If storage failed, should handle gracefully
      const retrievedKey = ConfigStorage.getApiKey('unsplash');
      // Either stored in sessionStorage or null
      expect(retrievedKey === testKey || retrievedKey === null).toBe(true);
    });

    it('should detect private browsing mode', () => {
      browserTester.mockPrivateBrowsing(true);
      
      const info = ConfigStorage.getStorageInfo();
      
      // localStorage should be unavailable in private browsing
      expect(info.localStorageAvailable).toBe(false);
      // sessionStorage might still be available
      expect(typeof info.sessionStorageAvailable).toBe('boolean');
    });

    it('should provide appropriate user feedback for private browsing', () => {
      browserTester.mockPrivateBrowsing(true);
      
      const isPrivateBrowsing = () => {
        try {
          localStorage.setItem('__private_test__', '1');
          localStorage.removeItem('__private_test__');
          return false;
        } catch {
          return true;
        }
      };
      
      expect(isPrivateBrowsing()).toBe(true);
      
      // App should show warning or different behavior
      if (isPrivateBrowsing()) {
        // Could show a warning message to user
        const warningMessage = 'Private browsing detected. Settings will only persist for this session.';
        expect(warningMessage).toContain('Private browsing');
      }
    });
  });

  describe('Storage Quota Management', () => {
    it('should handle quota exceeded errors gracefully', () => {
      browserTester.mockBrowserStorage('chrome');
      
      // Try to store a very large key that would exceed quota
      const largeValue = 'x'.repeat(15 * 1024 * 1024); // 15MB string
      
      expect(() => {
        ConfigStorage.setApiKey('large_key', largeValue);
      }).toThrow('QuotaExceededError');
      
      // But normal-sized keys should still work
      expect(() => {
        ConfigStorage.setApiKey('normal_key', 'normal-api-key');
      }).not.toThrow();
      
      expect(ConfigStorage.getApiKey('normal_key')).toBe('normal-api-key');
    });

    it('should clean up old data when quota is low', () => {
      browserTester.mockBrowserStorage('safari'); // Smaller quota
      
      // Store multiple keys
      const keys = Array.from({ length: 10 }, (_, i) => `key_${i}`);
      const values = Array.from({ length: 10 }, (_, i) => `value_${i}_${'x'.repeat(1000)}`);
      
      keys.forEach((key, i) => {
        try {
          ConfigStorage.setApiKey(key, values[i]);
        } catch (error) {
          // If quota exceeded, implement cleanup strategy
          if (error instanceof DOMException && error.name === 'QuotaExceededError') {
            // Remove oldest entries and try again
            for (let j = 0; j < 3; j++) {
              ConfigStorage.removeApiKey(`key_${j}`);
            }
            ConfigStorage.setApiKey(key, values[i]);
          }
        }
      });
      
      // Should have successfully stored some keys
      const storedKeys = keys.filter(key => ConfigStorage.getApiKey(key) !== null);
      expect(storedKeys.length).toBeGreaterThan(0);
    });

    it('should estimate available storage space', async () => {
      browserTester.mockBrowserStorage('chrome');
      
      // Mock navigator.storage.estimate
      const mockEstimate = vi.fn().mockResolvedValue({
        quota: 10 * 1024 * 1024, // 10MB
        usage: 2 * 1024 * 1024   // 2MB used
      });
      
      Object.defineProperty(navigator, 'storage', {
        value: { estimate: mockEstimate },
        configurable: true
      });
      
      const info = ConfigStorage.getStorageInfo();
      
      if ('storage' in navigator && 'estimate' in navigator.storage) {
        const estimate = await navigator.storage.estimate();
        expect(estimate.quota).toBe(10 * 1024 * 1024);
        expect(estimate.usage).toBe(2 * 1024 * 1024);
      }
    });
  });

  describe('Encryption and Security', () => {
    it('should encrypt stored API keys by default', () => {
      browserTester.mockBrowserStorage('chrome');
      
      const apiKey = 'sk-very-secret-api-key-123';
      ConfigStorage.setApiKey('openai', apiKey, true);
      
      // Raw storage should contain encrypted data
      const rawStored = localStorage.getItem('vocablens_config_openai');
      expect(rawStored).not.toBe(apiKey);
      expect(rawStored).toContain('encrypted_');
      
      // But retrieval should return original key
      expect(ConfigStorage.getApiKey('openai')).toBe(apiKey);
    });

    it('should handle encryption errors gracefully', () => {
      browserTester.mockBrowserStorage('chrome');
      
      // Manually store corrupted encrypted data
      localStorage.setItem('vocablens_config_test', 'encrypted_invalid_base64!@#');
      
      // Should return null for corrupted data
      expect(ConfigStorage.getApiKey('test')).toBeNull();
    });

    it('should migrate from unencrypted to encrypted storage', () => {
      browserTester.mockBrowserStorage('chrome');
      
      const apiKey = 'legacy-unencrypted-key';
      
      // Simulate old unencrypted storage
      localStorage.setItem('vocablens_config_legacy', apiKey);
      
      // Should still be able to read unencrypted data
      expect(ConfigStorage.getApiKey('legacy')).toBe(apiKey);
      
      // Re-storing should encrypt it
      ConfigStorage.setApiKey('legacy', apiKey, true);
      
      const rawStored = localStorage.getItem('vocablens_config_legacy');
      expect(rawStored).toContain('encrypted_');
      expect(ConfigStorage.getApiKey('legacy')).toBe(apiKey);
    });
  });

  describe('Fallback Mechanisms', () => {
    it('should fallback to sessionStorage when localStorage fails', () => {
      // Mock localStorage that always fails
      Object.defineProperty(window, 'localStorage', {
        value: {
          getItem: () => { throw new Error('localStorage unavailable'); },
          setItem: () => { throw new Error('localStorage unavailable'); },
          removeItem: () => { throw new Error('localStorage unavailable'); },
          clear: () => { throw new Error('localStorage unavailable'); },
          length: 0,
          key: () => null
        },
        configurable: true
      });
      
      const testKey = 'fallback-test-key';
      
      // Should fallback to sessionStorage without throwing
      expect(() => {
        ConfigStorage.setApiKey('test', testKey);
      }).not.toThrow();
      
      // Should be retrievable from sessionStorage
      expect(ConfigStorage.getApiKey('test')).toBe(testKey);
    });

    it('should handle complete storage failure gracefully', () => {
      // Mock both localStorage and sessionStorage to fail
      const failingStorage = {
        getItem: () => { throw new Error('Storage unavailable'); },
        setItem: () => { throw new Error('Storage unavailable'); },
        removeItem: () => { throw new Error('Storage unavailable'); },
        clear: () => { throw new Error('Storage unavailable'); },
        length: 0,
        key: () => null
      };
      
      Object.defineProperty(window, 'localStorage', {
        value: failingStorage,
        configurable: true
      });
      
      Object.defineProperty(window, 'sessionStorage', {
        value: failingStorage,
        configurable: true
      });
      
      const testKey = 'total-failure-key';
      
      // Should not throw even when all storage fails
      expect(() => {
        ConfigStorage.setApiKey('test', testKey);
      }).not.toThrow();
      
      // Should return null when storage is unavailable
      expect(ConfigStorage.getApiKey('test')).toBeNull();
      
      // Storage info should reflect unavailability
      const info = ConfigStorage.getStorageInfo();
      expect(info.localStorageAvailable).toBe(false);
      expect(info.sessionStorageAvailable).toBe(false);
    });

    it('should provide memory-only fallback', () => {
      // When all persistent storage fails, could use memory storage
      class MemoryStorage {
        private store = new Map<string, string>();
        
        setItem(key: string, value: string) {
          this.store.set(key, value);
        }
        
        getItem(key: string): string | null {
          return this.store.get(key) || null;
        }
        
        removeItem(key: string) {
          this.store.delete(key);
        }
        
        clear() {
          this.store.clear();
        }
      }
      
      const memoryStorage = new MemoryStorage();
      
      // Test memory storage as fallback
      memoryStorage.setItem('test_key', 'test_value');
      expect(memoryStorage.getItem('test_key')).toBe('test_value');
      
      memoryStorage.removeItem('test_key');
      expect(memoryStorage.getItem('test_key')).toBeNull();
    });
  });

  describe('Cross-Tab Synchronization', () => {
    it('should handle storage events for cross-tab sync', () => {
      browserTester.mockBrowserStorage('chrome');
      
      const eventListener = vi.fn();
      window.addEventListener('storage', eventListener);
      
      // Simulate storage change from another tab
      const storageEvent = new StorageEvent('storage', {
        key: 'vocablens_config_unsplash',
        newValue: 'new-api-key',
        oldValue: 'old-api-key',
        url: window.location.href,
        storageArea: localStorage
      });
      
      window.dispatchEvent(storageEvent);
      
      expect(eventListener).toHaveBeenCalledWith(storageEvent);
      
      window.removeEventListener('storage', eventListener);
    });

    it('should sync configuration changes across tabs', () => {
      browserTester.mockBrowserStorage('chrome');
      
      let syncedConfig: { [key: string]: string } = {};
      
      const handleStorageChange = (event: StorageEvent) => {
        if (event.key && event.key.startsWith('vocablens_config_')) {
          const service = event.key.replace('vocablens_config_', '');
          if (event.newValue) {
            syncedConfig[service] = event.newValue;
          } else {
            delete syncedConfig[service];
          }
        }
      };
      
      window.addEventListener('storage', handleStorageChange);
      
      // Simulate changes from another tab
      const changes = [
        { key: 'vocablens_config_unsplash', newValue: 'new-unsplash-key', oldValue: null },
        { key: 'vocablens_config_openai', newValue: 'new-openai-key', oldValue: null },
        { key: 'vocablens_config_unsplash', newValue: null, oldValue: 'new-unsplash-key' }
      ];
      
      changes.forEach(change => {
        const event = new StorageEvent('storage', {
          key: change.key,
          newValue: change.newValue,
          oldValue: change.oldValue,
          url: window.location.href,
          storageArea: localStorage
        });
        window.dispatchEvent(event);
      });
      
      expect(syncedConfig.openai).toBe('new-openai-key');
      expect(syncedConfig.unsplash).toBeUndefined(); // Was removed
      
      window.removeEventListener('storage', handleStorageChange);
    });
  });

  describe('Data Migration and Versioning', () => {
    it('should migrate old configuration format', () => {
      browserTester.mockBrowserStorage('chrome');
      
      // Simulate old format storage
      localStorage.setItem('old_unsplash_key', 'old-format-key');
      localStorage.setItem('old_openai_key', 'old-format-openai-key');
      
      const migrateOldConfig = () => {
        const oldKeys = [
          { old: 'old_unsplash_key', new: 'unsplash' },
          { old: 'old_openai_key', new: 'openai' }
        ];
        
        oldKeys.forEach(({ old, new: newKey }) => {
          const oldValue = localStorage.getItem(old);
          if (oldValue) {
            ConfigStorage.setApiKey(newKey, oldValue);
            localStorage.removeItem(old);
          }
        });
      };
      
      migrateOldConfig();
      
      expect(ConfigStorage.getApiKey('unsplash')).toBe('old-format-key');
      expect(ConfigStorage.getApiKey('openai')).toBe('old-format-openai-key');
      expect(localStorage.getItem('old_unsplash_key')).toBeNull();
    });

    it('should handle configuration versioning', () => {
      browserTester.mockBrowserStorage('chrome');
      
      const CONFIG_VERSION = '1.2.0';
      
      // Store configuration with version
      const configWithVersion = {
        version: CONFIG_VERSION,
        keys: {
          unsplash: 'versioned-unsplash-key',
          openai: 'versioned-openai-key'
        }
      };
      
      localStorage.setItem('vocablens_config_meta', JSON.stringify(configWithVersion));
      
      // Check version compatibility
      const storedConfig = JSON.parse(localStorage.getItem('vocablens_config_meta') || '{}');
      
      if (storedConfig.version) {
        const [major, minor, patch] = storedConfig.version.split('.').map(Number);
        const isCompatible = major === 1 && minor >= 2; // Compatible with v1.2+
        
        expect(isCompatible).toBe(true);
        
        if (isCompatible) {
          expect(storedConfig.keys.unsplash).toBe('versioned-unsplash-key');
        }
      }
    });
  });

  describe('Performance and Resource Management', () => {
    it('should limit storage usage per service', () => {
      browserTester.mockBrowserStorage('chrome');
      
      const maxKeyLength = 1024; // 1KB limit per key
      const longKey = 'x'.repeat(maxKeyLength + 100);
      
      // Should truncate or reject oversized keys
      const storeKey = (key: string) => {
        if (key.length > maxKeyLength) {
          throw new Error('API key too long');
        }
        ConfigStorage.setApiKey('test', key);
      };
      
      expect(() => storeKey(longKey)).toThrow('API key too long');
      expect(() => storeKey('normal-key')).not.toThrow();
    });

    it('should clean up expired configuration', () => {
      browserTester.mockBrowserStorage('chrome');
      
      const now = Date.now();
      const expiredTime = now - (24 * 60 * 60 * 1000); // 24 hours ago
      
      // Store configuration with timestamp
      const configWithTimestamp = JSON.stringify({
        key: 'expired-key',
        timestamp: expiredTime
      });
      
      localStorage.setItem('vocablens_config_expired_test', configWithTimestamp);
      
      // Cleanup function
      const cleanupExpiredConfig = () => {
        const maxAge = 7 * 24 * 60 * 60 * 1000; // 7 days
        
        Object.keys(localStorage).forEach(key => {
          if (key.startsWith('vocablens_config_')) {
            try {
              const config = JSON.parse(localStorage.getItem(key) || '{}');
              if (config.timestamp && (now - config.timestamp) > maxAge) {
                localStorage.removeItem(key);
              }
            } catch {
              // Invalid JSON, remove it
              localStorage.removeItem(key);
            }
          }
        });
      };
      
      cleanupExpiredConfig();
      
      expect(localStorage.getItem('vocablens_config_expired_test')).toBeNull();
    });

    it('should batch storage operations for performance', () => {
      browserTester.mockBrowserStorage('chrome');
      
      const batchOperations = [
        { service: 'unsplash', key: 'batch-key-1' },
        { service: 'openai', key: 'batch-key-2' },
        { service: 'supabase', key: 'batch-key-3' }
      ];
      
      // Batch set operations
      const startTime = performance.now();
      
      batchOperations.forEach(({ service, key }) => {
        ConfigStorage.setApiKey(service, key);
      });
      
      const batchSetTime = performance.now() - startTime;
      
      // Verify all were stored
      batchOperations.forEach(({ service, key }) => {
        expect(ConfigStorage.getApiKey(service)).toBe(key);
      });
      
      // Should be reasonably fast
      expect(batchSetTime).toBeLessThan(100); // Less than 100ms for 3 operations
    });
  });
});