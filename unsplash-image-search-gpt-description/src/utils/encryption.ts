/**
 * Encryption utilities for secure storage of API keys using Web Crypto API
 * Provides AES-GCM encryption with PBKDF2 key derivation
 */

const ALGORITHM = 'AES-GCM';
const KEY_LENGTH = 256;
const IV_LENGTH = 12; // 96 bits for AES-GCM
const SALT_LENGTH = 16; // 128 bits
const ITERATIONS = 100000; // PBKDF2 iterations

interface EncryptedData {
  encrypted: string;
  iv: string;
  salt: string;
}

/**
 * Generates a random salt for key derivation
 */
function generateSalt(): Uint8Array {
  return crypto.getRandomValues(new Uint8Array(SALT_LENGTH));
}

/**
 * Generates a random initialization vector
 */
function generateIV(): Uint8Array {
  return crypto.getRandomValues(new Uint8Array(IV_LENGTH));
}

/**
 * Derives an encryption key from a password using PBKDF2
 */
async function deriveKey(password: string, salt: Uint8Array): Promise<CryptoKey> {
  const encoder = new TextEncoder();
  const keyMaterial = await crypto.subtle.importKey(
    'raw',
    encoder.encode(password),
    { name: 'PBKDF2' },
    false,
    ['deriveKey']
  );

  return crypto.subtle.deriveKey(
    {
      name: 'PBKDF2',
      salt: salt,
      iterations: ITERATIONS,
      hash: 'SHA-256'
    },
    keyMaterial,
    { name: ALGORITHM, length: KEY_LENGTH },
    false,
    ['encrypt', 'decrypt']
  );
}

/**
 * Gets or creates a device-specific master password
 */
function getMasterPassword(): string {
  const storageKey = '_vocablens_device_key';
  let deviceKey = localStorage.getItem(storageKey);
  
  if (!deviceKey) {
    // Generate a new device-specific key
    const array = new Uint8Array(32);
    crypto.getRandomValues(array);
    deviceKey = Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
    localStorage.setItem(storageKey, deviceKey);
  }
  
  return deviceKey;
}

/**
 * Encrypts a string using AES-GCM
 */
export async function encryptString(plaintext: string): Promise<EncryptedData> {
  const encoder = new TextEncoder();
  const data = encoder.encode(plaintext);
  
  const salt = generateSalt();
  const iv = generateIV();
  const masterPassword = getMasterPassword();
  
  const key = await deriveKey(masterPassword, salt);
  
  const encrypted = await crypto.subtle.encrypt(
    {
      name: ALGORITHM,
      iv: iv
    },
    key,
    data
  );

  return {
    encrypted: arrayBufferToBase64(encrypted),
    iv: arrayBufferToBase64(iv),
    salt: arrayBufferToBase64(salt)
  };
}

/**
 * Decrypts a string using AES-GCM
 */
export async function decryptString(encryptedData: EncryptedData): Promise<string> {
  const masterPassword = getMasterPassword();
  
  const salt = base64ToArrayBuffer(encryptedData.salt);
  const iv = base64ToArrayBuffer(encryptedData.iv);
  const encrypted = base64ToArrayBuffer(encryptedData.encrypted);
  
  const key = await deriveKey(masterPassword, new Uint8Array(salt));
  
  try {
    const decrypted = await crypto.subtle.decrypt(
      {
        name: ALGORITHM,
        iv: new Uint8Array(iv)
      },
      key,
      encrypted
    );

    const decoder = new TextDecoder();
    return decoder.decode(decrypted);
  } catch (error) {
    throw new Error('Failed to decrypt data. The stored data may be corrupted.');
  }
}

/**
 * Converts ArrayBuffer to Base64 string
 */
function arrayBufferToBase64(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer);
  let binary = '';
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

/**
 * Converts Base64 string to ArrayBuffer
 */
function base64ToArrayBuffer(base64: string): ArrayBuffer {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes.buffer;
}

/**
 * Securely clears sensitive data from memory (best effort)
 */
export function secureClear(str: string): void {
  // Note: JavaScript doesn't provide true memory clearing,
  // but this helps prevent accidental retention
  if (str) {
    str.replace(/./g, '0');
  }
}