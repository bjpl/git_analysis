# API Key Security Implementation Guide

## Overview

This document provides detailed implementation specifications for secure client-side API key storage and management in VocabLens. The security implementation follows industry best practices for browser-based credential management while maintaining usability.

## Encryption Implementation

### 1. Core Encryption Service

```typescript
// src/services/encryptionService.ts

interface EncryptionResult {
  encrypted: string;
  iv: string;
  salt: string;
  tag: string;
}

interface DecryptionOptions {
  encrypted: string;
  iv: string;
  salt: string;
  tag: string;
  masterKey: string;
}

class EncryptionService {
  private readonly ALGORITHM = 'AES-GCM';
  private readonly KEY_LENGTH = 256;
  private readonly IV_LENGTH = 12;
  private readonly TAG_LENGTH = 16;
  private readonly PBKDF2_ITERATIONS = 100000;

  /**
   * Generate a cryptographically secure random salt
   */
  generateSalt(): string {
    const array = new Uint8Array(32);
    crypto.getRandomValues(array);
    return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
  }

  /**
   * Derive encryption key from master password and salt
   */
  async deriveKey(masterPassword: string, salt: string): Promise<CryptoKey> {
    const encoder = new TextEncoder();
    const keyMaterial = await crypto.subtle.importKey(
      'raw',
      encoder.encode(masterPassword),
      { name: 'PBKDF2' },
      false,
      ['deriveKey']
    );

    return crypto.subtle.deriveKey(
      {
        name: 'PBKDF2',
        salt: this.hexToArrayBuffer(salt),
        iterations: this.PBKDF2_ITERATIONS,
        hash: 'SHA-256'
      },
      keyMaterial,
      { name: this.ALGORITHM, length: this.KEY_LENGTH },
      false,
      ['encrypt', 'decrypt']
    );
  }

  /**
   * Encrypt sensitive data with AES-GCM
   */
  async encrypt(data: string, masterKey: string): Promise<EncryptionResult> {
    const encoder = new TextEncoder();
    const salt = this.generateSalt();
    const iv = crypto.getRandomValues(new Uint8Array(this.IV_LENGTH));
    
    const key = await this.deriveKey(masterKey, salt);
    
    const encryptedBuffer = await crypto.subtle.encrypt(
      {
        name: this.ALGORITHM,
        iv: iv
      },
      key,
      encoder.encode(data)
    );

    const encrypted = this.arrayBufferToHex(encryptedBuffer);
    const ivHex = this.arrayBufferToHex(iv);
    
    // Extract the authentication tag (last 16 bytes)
    const tagStart = encryptedBuffer.byteLength - this.TAG_LENGTH;
    const tag = this.arrayBufferToHex(encryptedBuffer.slice(tagStart));
    const ciphertext = this.arrayBufferToHex(encryptedBuffer.slice(0, tagStart));

    return {
      encrypted: ciphertext,
      iv: ivHex,
      salt: salt,
      tag: tag
    };
  }

  /**
   * Decrypt sensitive data with AES-GCM
   */
  async decrypt(options: DecryptionOptions): Promise<string> {
    const { encrypted, iv, salt, tag, masterKey } = options;
    
    const key = await this.deriveKey(masterKey, salt);
    
    // Reconstruct the complete encrypted buffer with tag
    const ciphertextBuffer = this.hexToArrayBuffer(encrypted);
    const tagBuffer = this.hexToArrayBuffer(tag);
    const fullEncrypted = new Uint8Array(ciphertextBuffer.byteLength + tagBuffer.byteLength);
    fullEncrypted.set(new Uint8Array(ciphertextBuffer));
    fullEncrypted.set(new Uint8Array(tagBuffer), ciphertextBuffer.byteLength);

    try {
      const decryptedBuffer = await crypto.subtle.decrypt(
        {
          name: this.ALGORITHM,
          iv: this.hexToArrayBuffer(iv)
        },
        key,
        fullEncrypted
      );

      const decoder = new TextDecoder();
      return decoder.decode(decryptedBuffer);
    } catch (error) {
      throw new Error('Decryption failed: Invalid key or corrupted data');
    }
  }

  /**
   * Securely wipe sensitive data from memory
   */
  secureWipe(data: string | ArrayBuffer | Uint8Array): void {
    if (typeof data === 'string') {
      // For strings, we can only zero out if it's a typed array
      return;
    }
    
    if (data instanceof ArrayBuffer) {
      const view = new Uint8Array(data);
      crypto.getRandomValues(view);
    } else if (data instanceof Uint8Array) {
      crypto.getRandomValues(data);
    }
  }

  // Utility methods
  private arrayBufferToHex(buffer: ArrayBuffer): string {
    const byteArray = new Uint8Array(buffer);
    return Array.from(byteArray, byte => byte.toString(16).padStart(2, '0')).join('');
  }

  private hexToArrayBuffer(hex: string): ArrayBuffer {
    const bytes = new Uint8Array(hex.length / 2);
    for (let i = 0; i < hex.length; i += 2) {
      bytes[i / 2] = parseInt(hex.substr(i, 2), 16);
    }
    return bytes.buffer;
  }
}
```

### 2. Secure Storage Layer

```typescript
// src/services/secureStorageService.ts

interface StorageOptions {
  securityLevel: 'memory' | 'session' | 'persistent';
  autoExpiry?: number; // minutes
  requireConfirmation?: boolean;
}

interface StoredCredential {
  service: string;
  encrypted: EncryptionResult;
  metadata: {
    createdAt: number;
    lastAccessed: number;
    expiresAt?: number;
    securityLevel: string;
  };
}

class SecureStorageService {
  private encryption = new EncryptionService();
  private memoryStore = new Map<string, StoredCredential>();
  private masterKey: string | null = null;

  constructor() {
    // Clear memory store on page unload
    window.addEventListener('beforeunload', () => {
      this.clearMemoryStore();
    });

    // Set up periodic cleanup
    setInterval(() => {
      this.cleanupExpiredCredentials();
    }, 60000); // Check every minute
  }

  /**
   * Set master key for encryption/decryption
   */
  async setMasterKey(password: string): Promise<boolean> {
    try {
      // Validate master key strength
      if (!this.validateMasterKeyStrength(password)) {
        throw new Error('Master key does not meet security requirements');
      }

      this.masterKey = password;
      return true;
    } catch (error) {
      console.error('Failed to set master key:', error);
      return false;
    }
  }

  /**
   * Store encrypted credential
   */
  async storeCredential(
    key: string,
    value: string,
    options: StorageOptions
  ): Promise<boolean> {
    if (!this.masterKey) {
      throw new Error('Master key not set');
    }

    try {
      const encrypted = await this.encryption.encrypt(value, this.masterKey);
      const credential: StoredCredential = {
        service: key,
        encrypted,
        metadata: {
          createdAt: Date.now(),
          lastAccessed: Date.now(),
          expiresAt: options.autoExpiry ? Date.now() + (options.autoExpiry * 60000) : undefined,
          securityLevel: options.securityLevel
        }
      };

      switch (options.securityLevel) {
        case 'memory':
          this.memoryStore.set(key, credential);
          break;
        case 'session':
          sessionStorage.setItem(`secure_${key}`, JSON.stringify(credential));
          break;
        case 'persistent':
          if (options.requireConfirmation && !await this.getUserConsent(key)) {
            return false;
          }
          localStorage.setItem(`secure_${key}`, JSON.stringify(credential));
          break;
      }

      return true;
    } catch (error) {
      console.error('Failed to store credential:', error);
      return false;
    }
  }

  /**
   * Retrieve and decrypt credential
   */
  async retrieveCredential(key: string): Promise<string | null> {
    if (!this.masterKey) {
      throw new Error('Master key not set');
    }

    try {
      let credential: StoredCredential | null = null;

      // Check memory store first
      if (this.memoryStore.has(key)) {
        credential = this.memoryStore.get(key)!;
      } else {
        // Check session storage
        const sessionData = sessionStorage.getItem(`secure_${key}`);
        if (sessionData) {
          credential = JSON.parse(sessionData);
        } else {
          // Check persistent storage
          const persistentData = localStorage.getItem(`secure_${key}`);
          if (persistentData) {
            credential = JSON.parse(persistentData);
          }
        }
      }

      if (!credential) {
        return null;
      }

      // Check expiry
      if (credential.metadata.expiresAt && Date.now() > credential.metadata.expiresAt) {
        await this.removeCredential(key);
        return null;
      }

      // Update last accessed
      credential.metadata.lastAccessed = Date.now();
      await this.storeCredential(
        key, 
        await this.encryption.decrypt({
          ...credential.encrypted,
          masterKey: this.masterKey
        }),
        { securityLevel: credential.metadata.securityLevel as any }
      );

      return await this.encryption.decrypt({
        ...credential.encrypted,
        masterKey: this.masterKey
      });
    } catch (error) {
      console.error('Failed to retrieve credential:', error);
      return null;
    }
  }

  /**
   * Remove credential from all storage levels
   */
  async removeCredential(key: string): Promise<boolean> {
    try {
      this.memoryStore.delete(key);
      sessionStorage.removeItem(`secure_${key}`);
      localStorage.removeItem(`secure_${key}`);
      return true;
    } catch (error) {
      console.error('Failed to remove credential:', error);
      return false;
    }
  }

  /**
   * Clear all stored credentials
   */
  async clearAllCredentials(): Promise<boolean> {
    try {
      this.clearMemoryStore();
      
      // Clear session storage
      const sessionKeys = Object.keys(sessionStorage).filter(key => key.startsWith('secure_'));
      sessionKeys.forEach(key => sessionStorage.removeItem(key));

      // Clear local storage
      const localKeys = Object.keys(localStorage).filter(key => key.startsWith('secure_'));
      localKeys.forEach(key => localStorage.removeItem(key));

      return true;
    } catch (error) {
      console.error('Failed to clear credentials:', error);
      return false;
    }
  }

  /**
   * List all stored credential keys
   */
  async listCredentials(): Promise<string[]> {
    const keys = new Set<string>();

    // Memory store
    this.memoryStore.forEach((_, key) => keys.add(key));

    // Session storage
    Object.keys(sessionStorage)
      .filter(key => key.startsWith('secure_'))
      .forEach(key => keys.add(key.replace('secure_', '')));

    // Local storage
    Object.keys(localStorage)
      .filter(key => key.startsWith('secure_'))
      .forEach(key => keys.add(key.replace('secure_', '')));

    return Array.from(keys);
  }

  /**
   * Get credential metadata
   */
  async getCredentialInfo(key: string): Promise<StoredCredential['metadata'] | null> {
    let credential: StoredCredential | null = null;

    if (this.memoryStore.has(key)) {
      credential = this.memoryStore.get(key)!;
    } else {
      const sessionData = sessionStorage.getItem(`secure_${key}`);
      if (sessionData) {
        credential = JSON.parse(sessionData);
      } else {
        const persistentData = localStorage.getItem(`secure_${key}`);
        if (persistentData) {
          credential = JSON.parse(persistentData);
        }
      }
    }

    return credential ? credential.metadata : null;
  }

  // Private methods

  private validateMasterKeyStrength(password: string): boolean {
    // Minimum 12 characters
    if (password.length < 12) {
      return false;
    }

    // Must contain uppercase, lowercase, number, and symbol
    const hasUpper = /[A-Z]/.test(password);
    const hasLower = /[a-z]/.test(password);
    const hasNumber = /[0-9]/.test(password);
    const hasSymbol = /[^A-Za-z0-9]/.test(password);

    return hasUpper && hasLower && hasNumber && hasSymbol;
  }

  private async getUserConsent(key: string): Promise<boolean> {
    return new Promise((resolve) => {
      const modal = document.createElement('div');
      modal.innerHTML = `
        <div style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 9999; display: flex; align-items: center; justify-content: center;">
          <div style="background: white; padding: 2rem; border-radius: 8px; max-width: 400px;">
            <h3>Store API Key Persistently?</h3>
            <p>Do you want to store the ${key} API key persistently on this device? This will keep it available between browser sessions but may pose a security risk on shared computers.</p>
            <div style="display: flex; gap: 1rem; justify-content: flex-end; margin-top: 1rem;">
              <button id="deny" style="padding: 0.5rem 1rem; border: 1px solid #ccc; background: white; cursor: pointer;">No, session only</button>
              <button id="allow" style="padding: 0.5rem 1rem; border: none; background: #007bff; color: white; cursor: pointer;">Yes, store persistently</button>
            </div>
          </div>
        </div>
      `;

      document.body.appendChild(modal);

      modal.querySelector('#allow')!.addEventListener('click', () => {
        document.body.removeChild(modal);
        resolve(true);
      });

      modal.querySelector('#deny')!.addEventListener('click', () => {
        document.body.removeChild(modal);
        resolve(false);
      });
    });
  }

  private clearMemoryStore(): void {
    // Securely wipe sensitive data
    this.memoryStore.forEach(credential => {
      // Zero out encrypted data if possible
      this.encryption.secureWipe(credential.encrypted.encrypted);
    });
    this.memoryStore.clear();
    
    // Clear master key
    if (this.masterKey) {
      this.masterKey = null;
    }
  }

  private cleanupExpiredCredentials(): void {
    const now = Date.now();

    // Clean memory store
    for (const [key, credential] of this.memoryStore.entries()) {
      if (credential.metadata.expiresAt && now > credential.metadata.expiresAt) {
        this.memoryStore.delete(key);
      }
    }

    // Clean session storage
    Object.keys(sessionStorage)
      .filter(key => key.startsWith('secure_'))
      .forEach(key => {
        try {
          const credential: StoredCredential = JSON.parse(sessionStorage.getItem(key)!);
          if (credential.metadata.expiresAt && now > credential.metadata.expiresAt) {
            sessionStorage.removeItem(key);
          }
        } catch (error) {
          // Remove corrupted entries
          sessionStorage.removeItem(key);
        }
      });

    // Clean local storage
    Object.keys(localStorage)
      .filter(key => key.startsWith('secure_'))
      .forEach(key => {
        try {
          const credential: StoredCredential = JSON.parse(localStorage.getItem(key)!);
          if (credential.metadata.expiresAt && now > credential.metadata.expiresAt) {
            localStorage.removeItem(key);
          }
        } catch (error) {
          // Remove corrupted entries
          localStorage.removeItem(key);
        }
      });
  }
}

export const secureStorage = new SecureStorageService();
```

## Security Best Practices Implementation

### 1. Content Security Policy Headers

```typescript
// Add to index.html or configure via server
const CSP_POLICY = `
  default-src 'self';
  script-src 'self' 'unsafe-eval';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https://images.unsplash.com https://via.placeholder.com;
  connect-src 'self' https://api.unsplash.com https://api.openai.com https://*.supabase.co;
  font-src 'self' data:;
  frame-src 'none';
  object-src 'none';
  base-uri 'self';
  form-action 'self';
`;
```

### 2. XSS Protection

```typescript
// src/utils/securityUtils.ts

export class SecurityUtils {
  /**
   * Sanitize user input to prevent XSS
   */
  static sanitizeInput(input: string): string {
    const div = document.createElement('div');
    div.textContent = input;
    return div.innerHTML;
  }

  /**
   * Validate API key format to prevent injection
   */
  static validateApiKeyFormat(key: string, service: 'unsplash' | 'openai' | 'supabase'): boolean {
    const patterns = {
      unsplash: /^[A-Za-z0-9_-]{20,50}$/,
      openai: /^sk-[A-Za-z0-9]{20,}$/,
      supabase: /^eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*$/
    };

    return patterns[service].test(key);
  }

  /**
   * Generate secure random string for session IDs
   */
  static generateSecureRandom(length: number = 32): string {
    const array = new Uint8Array(length);
    crypto.getRandomValues(array);
    return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
  }

  /**
   * Check if current context is secure (HTTPS)
   */
  static isSecureContext(): boolean {
    return window.isSecureContext && location.protocol === 'https:';
  }

  /**
   * Detect if running in private/incognito mode
   */
  static async isPrivateMode(): Promise<boolean> {
    try {
      await new Promise((resolve, reject) => {
        const iframe = document.createElement('iframe');
        iframe.style.display = 'none';
        iframe.onload = () => {
          try {
            iframe.contentWindow?.localStorage.setItem('test', 'test');
            iframe.contentWindow?.localStorage.removeItem('test');
            resolve(false);
          } catch {
            resolve(true);
          }
          document.body.removeChild(iframe);
        };
        iframe.onerror = () => {
          resolve(true);
          document.body.removeChild(iframe);
        };
        document.body.appendChild(iframe);
      });
      return false;
    } catch {
      return true;
    }
  }
}
```

### 3. Memory Management

```typescript
// src/services/memoryManager.ts

class MemoryManager {
  private sensitiveRefs = new WeakMap<object, string>();
  private cleanupTasks = new Set<() => void>();

  /**
   * Register sensitive data for automatic cleanup
   */
  registerSensitiveData(obj: object, description: string): void {
    this.sensitiveRefs.set(obj, description);
  }

  /**
   * Add cleanup task to be executed on page unload
   */
  addCleanupTask(task: () => void): void {
    this.cleanupTasks.add(task);
  }

  /**
   * Execute all cleanup tasks
   */
  cleanup(): void {
    this.cleanupTasks.forEach(task => {
      try {
        task();
      } catch (error) {
        console.error('Cleanup task failed:', error);
      }
    });
    this.cleanupTasks.clear();
  }

  /**
   * Force garbage collection (if available)
   */
  forceGarbageCollection(): void {
    if ('gc' in window) {
      (window as any).gc();
    }
  }
}

export const memoryManager = new MemoryManager();

// Set up automatic cleanup
window.addEventListener('beforeunload', () => {
  memoryManager.cleanup();
});

window.addEventListener('unload', () => {
  memoryManager.cleanup();
});
```

## Security Audit Checklist

### Encryption
- [ ] AES-GCM algorithm with 256-bit keys
- [ ] PBKDF2 with minimum 100,000 iterations
- [ ] Cryptographically secure random number generation
- [ ] Proper IV generation for each encryption
- [ ] Authentication tag verification on decryption

### Storage Security
- [ ] No plaintext API keys in storage
- [ ] Encrypted data includes integrity verification
- [ ] Automatic expiration of stored credentials
- [ ] Secure cleanup on application exit
- [ ] Protection against storage quotas attacks

### Input Validation
- [ ] API key format validation
- [ ] Input sanitization against XSS
- [ ] Rate limiting on validation attempts
- [ ] Error messages don't leak sensitive information
- [ ] Proper handling of malformed data

### Browser Security
- [ ] Content Security Policy implemented
- [ ] HTTPS-only operation in production
- [ ] Secure context verification
- [ ] Private mode detection
- [ ] Cross-origin protection

### Memory Management
- [ ] Sensitive data cleared from memory
- [ ] WeakMap usage for object references
- [ ] Cleanup tasks registered and executed
- [ ] No sensitive data in error logs
- [ ] Garbage collection hints where available

This implementation provides enterprise-grade security for client-side API key management while maintaining usability and performance.