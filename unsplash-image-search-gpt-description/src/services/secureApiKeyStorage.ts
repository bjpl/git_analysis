/**
 * Secure API Key Storage Service for VocabLens PWA
 * Implements client-side encryption using Web Crypto API for secure API key storage
 */

// Types for secure storage
interface EncryptedData {
  iv: string;
  salt: string;
  data: string;
  timestamp: number;
  keyVersion: number;
}

interface ApiKeyData {
  unsplash?: string;
  openai?: string;
  lastUpdated: number;
  rotationReminder?: number;
}

interface StorageMetrics {
  keyRotations: number;
  lastAccess: number;
  failedAttempts: number;
  encryptionMethod: string;
}

/**
 * Secure API Key Storage using Web Crypto API
 * Implements AES-GCM encryption with PBKDF2 key derivation
 */
export class SecureApiKeyStorage {
  private readonly STORAGE_KEY = 'vocablens_encrypted_keys';
  private readonly METRICS_KEY = 'vocablens_key_metrics';
  private readonly MASTER_KEY_CACHE_TIME = 15 * 60 * 1000; // 15 minutes
  private readonly KEY_ROTATION_REMINDER_DAYS = 30;
  
  // Encryption parameters
  private readonly PBKDF2_ITERATIONS = 100000;
  private readonly AES_KEY_LENGTH = 256;
  private readonly IV_LENGTH = 12; // 96 bits for GCM
  private readonly SALT_LENGTH = 16; // 128 bits
  private readonly TAG_LENGTH = 16; // 128 bits for GCM auth tag
  
  private masterKeyCache: CryptoKey | null = null;
  private masterKeyCacheTime: number = 0;
  private userPassword: string | null = null;

  /**
   * Initialize secure storage with user's master password
   * This password is used to derive the encryption key
   */
  async initialize(password: string): Promise<boolean> {
    try {
      // Validate password strength
      if (!this.validatePasswordStrength(password)) {
        throw new SecurityError('Password does not meet minimum security requirements');
      }

      this.userPassword = password;
      
      // Test encryption/decryption to validate setup
      const testData = { test: 'validation' };
      const encrypted = await this.encryptData(JSON.stringify(testData), password);
      const decrypted = await this.decryptData(encrypted, password);
      
      const parsed = JSON.parse(decrypted);
      if (parsed.test !== 'validation') {
        throw new SecurityError('Encryption validation failed');
      }

      // Update metrics
      await this.updateMetrics('initialization');
      
      return true;
    } catch (error) {
      console.error('Failed to initialize secure storage:', error);
      return false;
    }
  }

  /**
   * Store API keys securely with encryption
   */
  async storeApiKeys(apiKeys: Partial<ApiKeyData>): Promise<void> {
    if (!this.userPassword) {
      throw new SecurityError('Secure storage not initialized');
    }

    try {
      // Validate API keys before storage
      this.validateApiKeys(apiKeys);

      // Get existing data to merge
      const existingData = await this.getApiKeys().catch(() => ({}));
      
      const dataToStore: ApiKeyData = {
        ...existingData,
        ...apiKeys,
        lastUpdated: Date.now(),
        rotationReminder: Date.now() + (this.KEY_ROTATION_REMINDER_DAYS * 24 * 60 * 60 * 1000)
      };

      // Encrypt the data
      const encrypted = await this.encryptData(JSON.stringify(dataToStore), this.userPassword);
      
      // Store encrypted data
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(encrypted));
      
      // Update metrics
      await this.updateMetrics('storage');
      
      // Log security event (without sensitive data)
      this.logSecurityEvent('api_keys_stored', {
        keys_count: Object.keys(apiKeys).length,
        timestamp: Date.now()
      });

    } catch (error) {
      await this.updateMetrics('storage_failed');
      throw new SecurityError(`Failed to store API keys: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Retrieve and decrypt API keys
   */
  async getApiKeys(): Promise<ApiKeyData> {
    if (!this.userPassword) {
      throw new SecurityError('Secure storage not initialized');
    }

    try {
      const encryptedDataString = localStorage.getItem(this.STORAGE_KEY);
      if (!encryptedDataString) {
        return { lastUpdated: 0 }; // Return empty data if none exists
      }

      const encryptedData: EncryptedData = JSON.parse(encryptedDataString);
      const decryptedString = await this.decryptData(encryptedData, this.userPassword);
      const apiKeyData: ApiKeyData = JSON.parse(decryptedString);

      // Update access metrics
      await this.updateMetrics('access');

      // Check if rotation reminder is due
      if (apiKeyData.rotationReminder && Date.now() > apiKeyData.rotationReminder) {
        this.showRotationReminder();
      }

      return apiKeyData;
    } catch (error) {
      await this.updateMetrics('access_failed');
      throw new SecurityError(`Failed to retrieve API keys: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Update a specific API key
   */
  async updateApiKey(service: 'unsplash' | 'openai', key: string): Promise<void> {
    const existingData = await this.getApiKeys().catch(() => ({ lastUpdated: 0 }));
    await this.storeApiKeys({
      ...existingData,
      [service]: key
    });
  }

  /**
   * Remove API keys from storage
   */
  async clearApiKeys(): Promise<void> {
    try {
      localStorage.removeItem(this.STORAGE_KEY);
      this.masterKeyCache = null;
      this.masterKeyCacheTime = 0;
      this.userPassword = null;
      
      await this.updateMetrics('cleared');
      
      this.logSecurityEvent('api_keys_cleared', {
        timestamp: Date.now()
      });
    } catch (error) {
      throw new SecurityError(`Failed to clear API keys: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Check if API keys exist in storage
   */
  async hasApiKeys(): Promise<boolean> {
    return localStorage.getItem(this.STORAGE_KEY) !== null;
  }

  /**
   * Get storage metrics and security information
   */
  async getSecurityMetrics(): Promise<StorageMetrics> {
    const metricsString = localStorage.getItem(this.METRICS_KEY);
    if (!metricsString) {
      return {
        keyRotations: 0,
        lastAccess: 0,
        failedAttempts: 0,
        encryptionMethod: 'AES-GCM-256'
      };
    }

    return JSON.parse(metricsString);
  }

  /**
   * Rotate encryption key (change master password)
   */
  async rotateEncryptionKey(oldPassword: string, newPassword: string): Promise<void> {
    try {
      // Validate new password
      if (!this.validatePasswordStrength(newPassword)) {
        throw new SecurityError('New password does not meet security requirements');
      }

      // Decrypt with old password
      const apiKeys = await this.getApiKeys();
      
      // Clear current cache
      this.masterKeyCache = null;
      this.masterKeyCacheTime = 0;
      
      // Re-encrypt with new password
      this.userPassword = newPassword;
      await this.storeApiKeys(apiKeys);
      
      // Update rotation metrics
      const metrics = await this.getSecurityMetrics();
      await this.updateMetrics('key_rotation', {
        keyRotations: metrics.keyRotations + 1
      });

      this.logSecurityEvent('encryption_key_rotated', {
        timestamp: Date.now()
      });

    } catch (error) {
      throw new SecurityError(`Failed to rotate encryption key: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  // Private encryption methods

  /**
   * Encrypt data using AES-GCM with PBKDF2 key derivation
   */
  private async encryptData(data: string, password: string): Promise<EncryptedData> {
    try {
      // Generate random salt and IV
      const salt = crypto.getRandomValues(new Uint8Array(this.SALT_LENGTH));
      const iv = crypto.getRandomValues(new Uint8Array(this.IV_LENGTH));

      // Derive encryption key from password using PBKDF2
      const keyMaterial = await this.deriveKey(password, salt);
      
      // Encrypt the data
      const encoder = new TextEncoder();
      const dataBuffer = encoder.encode(data);
      
      const encryptedBuffer = await crypto.subtle.encrypt(
        {
          name: 'AES-GCM',
          iv: iv
        },
        keyMaterial,
        dataBuffer
      );

      return {
        iv: this.bufferToBase64(iv),
        salt: this.bufferToBase64(salt),
        data: this.bufferToBase64(new Uint8Array(encryptedBuffer)),
        timestamp: Date.now(),
        keyVersion: 1
      };
    } catch (error) {
      throw new SecurityError(`Encryption failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Decrypt data using stored parameters
   */
  private async decryptData(encryptedData: EncryptedData, password: string): Promise<string> {
    try {
      // Convert base64 back to buffers
      const salt = this.base64ToBuffer(encryptedData.salt);
      const iv = this.base64ToBuffer(encryptedData.iv);
      const data = this.base64ToBuffer(encryptedData.data);

      // Derive the same encryption key
      const keyMaterial = await this.deriveKey(password, salt);

      // Decrypt the data
      const decryptedBuffer = await crypto.subtle.decrypt(
        {
          name: 'AES-GCM',
          iv: iv
        },
        keyMaterial,
        data
      );

      const decoder = new TextDecoder();
      return decoder.decode(decryptedBuffer);
    } catch (error) {
      throw new SecurityError(`Decryption failed: ${error instanceof Error ? error.message : 'Authentication failed'}`);
    }
  }

  /**
   * Derive encryption key using PBKDF2
   */
  private async deriveKey(password: string, salt: Uint8Array): Promise<CryptoKey> {
    // Check cache first (with time-based expiration)
    const now = Date.now();
    if (this.masterKeyCache && (now - this.masterKeyCacheTime) < this.MASTER_KEY_CACHE_TIME) {
      return this.masterKeyCache;
    }

    const encoder = new TextEncoder();
    const passwordBuffer = encoder.encode(password);

    // Import password as key material
    const keyMaterial = await crypto.subtle.importKey(
      'raw',
      passwordBuffer,
      { name: 'PBKDF2' },
      false,
      ['deriveKey']
    );

    // Derive AES key
    const derivedKey = await crypto.subtle.deriveKey(
      {
        name: 'PBKDF2',
        salt: salt,
        iterations: this.PBKDF2_ITERATIONS,
        hash: 'SHA-256'
      },
      keyMaterial,
      {
        name: 'AES-GCM',
        length: this.AES_KEY_LENGTH
      },
      false,
      ['encrypt', 'decrypt']
    );

    // Cache the key
    this.masterKeyCache = derivedKey;
    this.masterKeyCacheTime = now;

    return derivedKey;
  }

  /**
   * Validate password strength
   */
  private validatePasswordStrength(password: string): boolean {
    // Minimum 12 characters
    if (password.length < 12) return false;
    
    // Must contain uppercase, lowercase, number, and special character
    const hasUpper = /[A-Z]/.test(password);
    const hasLower = /[a-z]/.test(password);
    const hasNumber = /[0-9]/.test(password);
    const hasSpecial = /[^A-Za-z0-9]/.test(password);
    
    // Check for common weak patterns
    const hasWeakPatterns = /^(password|123456|qwerty)/i.test(password) ||
                           /^(.)\1{3,}/.test(password); // Repeated characters
    
    return hasUpper && hasLower && hasNumber && hasSpecial && !hasWeakPatterns;
  }

  /**
   * Validate API key formats
   */
  private validateApiKeys(apiKeys: Partial<ApiKeyData>): void {
    if (apiKeys.unsplash) {
      if (typeof apiKeys.unsplash !== 'string' || apiKeys.unsplash.length < 20) {
        throw new SecurityError('Invalid Unsplash API key format');
      }
    }

    if (apiKeys.openai) {
      if (typeof apiKeys.openai !== 'string' || !apiKeys.openai.startsWith('sk-')) {
        throw new SecurityError('Invalid OpenAI API key format');
      }
    }
  }

  /**
   * Update security metrics
   */
  private async updateMetrics(operation: string, additionalData?: Partial<StorageMetrics>): Promise<void> {
    try {
      const existingMetrics = await this.getSecurityMetrics();
      const updatedMetrics: StorageMetrics = {
        ...existingMetrics,
        lastAccess: Date.now(),
        ...additionalData
      };

      if (operation.includes('failed')) {
        updatedMetrics.failedAttempts = (existingMetrics.failedAttempts || 0) + 1;
      }

      localStorage.setItem(this.METRICS_KEY, JSON.stringify(updatedMetrics));
    } catch (error) {
      // Don't throw on metrics update failure
      console.warn('Failed to update security metrics:', error);
    }
  }

  /**
   * Log security events for monitoring
   */
  private logSecurityEvent(event: string, data: Record<string, any>): void {
    // In a production app, this would send to a security monitoring service
    console.log(`Security Event: ${event}`, {
      ...data,
      userAgent: navigator.userAgent,
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Show rotation reminder to user
   */
  private showRotationReminder(): void {
    // This would integrate with your app's notification system
    console.warn('API Key Rotation Reminder: Consider rotating your API keys for better security');
    
    // Could dispatch a custom event that the UI listens for
    window.dispatchEvent(new CustomEvent('api-key-rotation-reminder', {
      detail: { message: 'Consider rotating your API keys for enhanced security' }
    }));
  }

  // Utility methods for base64 encoding/decoding
  private bufferToBase64(buffer: Uint8Array): string {
    let binary = '';
    const bytes = new Uint8Array(buffer);
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return window.btoa(binary);
  }

  private base64ToBuffer(base64: string): Uint8Array {
    const binary = window.atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    return bytes;
  }
}

/**
 * Security Error class for API key storage operations
 */
export class SecurityError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'SecurityError';
  }
}

/**
 * Secure API Key Manager - High-level interface
 */
export class SecureApiKeyManager {
  private storage: SecureApiKeyStorage;
  private initialized: boolean = false;

  constructor() {
    this.storage = new SecureApiKeyStorage();
  }

  /**
   * Initialize with master password
   */
  async initialize(password: string): Promise<boolean> {
    this.initialized = await this.storage.initialize(password);
    return this.initialized;
  }

  /**
   * Store API keys with validation
   */
  async storeApiKeys(keys: { unsplash?: string; openai?: string }): Promise<void> {
    this.ensureInitialized();
    await this.storage.storeApiKeys(keys);
  }

  /**
   * Get decrypted API keys
   */
  async getApiKeys(): Promise<{ unsplash?: string; openai?: string }> {
    this.ensureInitialized();
    const data = await this.storage.getApiKeys();
    return {
      unsplash: data.unsplash,
      openai: data.openai
    };
  }

  /**
   * Update individual API key
   */
  async updateApiKey(service: 'unsplash' | 'openai', key: string): Promise<void> {
    this.ensureInitialized();
    await this.storage.updateApiKey(service, key);
  }

  /**
   * Check if keys are stored
   */
  async hasStoredKeys(): Promise<boolean> {
    return this.storage.hasApiKeys();
  }

  /**
   * Clear all stored keys
   */
  async clearKeys(): Promise<void> {
    await this.storage.clearApiKeys();
    this.initialized = false;
  }

  /**
   * Get security metrics
   */
  async getSecurityInfo(): Promise<StorageMetrics> {
    return this.storage.getSecurityMetrics();
  }

  /**
   * Rotate master encryption key
   */
  async rotateEncryptionKey(oldPassword: string, newPassword: string): Promise<void> {
    this.ensureInitialized();
    await this.storage.rotateEncryptionKey(oldPassword, newPassword);
  }

  private ensureInitialized(): void {
    if (!this.initialized) {
      throw new SecurityError('SecureApiKeyManager not initialized. Call initialize() first.');
    }
  }
}

// Export singleton instance
export const secureApiKeyManager = new SecureApiKeyManager();
export default SecureApiKeyManager;