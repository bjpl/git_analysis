/**
 * API Key Management Interface for VocabLens PWA
 * Provides secure user interface for managing API keys
 */
import React, { useState, useEffect, useCallback } from 'react';
import { EyeIcon, EyeSlashIcon, KeyIcon, ShieldCheckIcon, ExclamationTriangleIcon, CheckCircleIcon, ClockIcon } from '@heroicons/react/24/outline';
import { secureApiKeyManager, SecurityError } from '../../services/secureApiKeyStorage';
import { ApiKeyProtection } from '../../services/securityProtections';
import { Button } from '../Shared/Button/Button';
import { Card } from '../Shared/Card/Card';
import { Modal } from '../Shared/Modal/Modal';
import toast from 'react-hot-toast';

interface ApiKeyStatus {
  unsplash: 'valid' | 'invalid' | 'missing' | 'testing';
  openai: 'valid' | 'invalid' | 'missing' | 'testing';
}

interface SecurityMetrics {
  keyRotations: number;
  lastAccess: number;
  failedAttempts: number;
  encryptionMethod: string;
}

export const ApiKeyManager: React.FC = () => {
  const [isInitialized, setIsInitialized] = useState(false);
  const [masterPassword, setMasterPassword] = useState('');
  const [showMasterPassword, setShowMasterPassword] = useState(false);
  const [apiKeys, setApiKeys] = useState({ unsplash: '', openai: '' });
  const [showApiKeys, setShowApiKeys] = useState({ unsplash: false, openai: false });
  const [keyStatus, setKeyStatus] = useState<ApiKeyStatus>({
    unsplash: 'missing',
    openai: 'missing'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSetupModal, setShowSetupModal] = useState(false);
  const [showRotationModal, setShowRotationModal] = useState(false);
  const [securityMetrics, setSecurityMetrics] = useState<SecurityMetrics | null>(null);
  const [passwordStrength, setPasswordStrength] = useState(0);
  const [rotationData, setRotationData] = useState({ oldPassword: '', newPassword: '' });

  // Check if storage is already initialized
  useEffect(() => {
    checkInitialization();
    loadSecurityMetrics();
    
    // Listen for rotation reminders
    const handleRotationReminder = () => {
      toast(
        'Consider rotating your API keys for enhanced security',
        {
          icon: '🔄',
          duration: 8000,
          style: {
            background: '#FEF3C7',
            color: '#92400E',
            border: '1px solid #FBBF24'
          }
        }
      );
    };

    window.addEventListener('api-key-rotation-reminder', handleRotationReminder);
    return () => window.removeEventListener('api-key-rotation-reminder', handleRotationReminder);
  }, []);

  // Check initialization status
  const checkInitialization = async () => {
    try {
      const hasKeys = await secureApiKeyManager.hasStoredKeys();
      if (hasKeys && !isInitialized) {
        setShowSetupModal(true);
      }
    } catch (error) {
      console.error('Failed to check initialization:', error);
    }
  };

  // Load security metrics
  const loadSecurityMetrics = async () => {
    try {
      const metrics = await secureApiKeyManager.getSecurityInfo();
      setSecurityMetrics(metrics);
    } catch (error) {
      console.warn('Failed to load security metrics:', error);
    }
  };

  // Calculate password strength
  const calculatePasswordStrength = useCallback((password: string): number => {
    let score = 0;
    
    if (password.length >= 8) score += 20;
    if (password.length >= 12) score += 20;
    if (/[a-z]/.test(password)) score += 15;
    if (/[A-Z]/.test(password)) score += 15;
    if (/[0-9]/.test(password)) score += 15;
    if (/[^A-Za-z0-9]/.test(password)) score += 15;
    
    // Deduct for weak patterns
    if (/^(password|123456|qwerty)/i.test(password)) score -= 30;
    if (/^(.)\1{3,}/.test(password)) score -= 20; // Repeated characters
    
    return Math.max(0, Math.min(100, score));
  }, []);

  // Update password strength when master password changes
  useEffect(() => {
    setPasswordStrength(calculatePasswordStrength(masterPassword));
  }, [masterPassword, calculatePasswordStrength]);

  // Initialize secure storage
  const initializeStorage = async () => {
    setLoading(true);
    setError(null);

    try {
      if (passwordStrength < 60) {
        throw new SecurityError('Password is too weak. Please use at least 12 characters with mixed case, numbers, and symbols.');
      }

      const success = await secureApiKeyManager.initialize(masterPassword);
      if (!success) {
        throw new SecurityError('Failed to initialize secure storage');
      }

      setIsInitialized(true);
      setShowSetupModal(false);
      setMasterPassword(''); // Clear password from memory
      toast.success('Secure storage initialized successfully');
      
      // Load existing keys if any
      await loadExistingKeys();
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to initialize storage');
      toast.error('Failed to initialize secure storage');
    } finally {
      setLoading(false);
    }
  };

  // Load existing keys
  const loadExistingKeys = async () => {
    try {
      const existingKeys = await secureApiKeyManager.getApiKeys();
      setApiKeys(prevKeys => ({
        unsplash: existingKeys.unsplash || prevKeys.unsplash,
        openai: existingKeys.openai || prevKeys.openai
      }));
      
      // Update status
      setKeyStatus({
        unsplash: existingKeys.unsplash ? 'valid' : 'missing',
        openai: existingKeys.openai ? 'valid' : 'missing'
      });
    } catch (error) {
      console.error('Failed to load existing keys:', error);
    }
  };

  // Unlock storage with password
  const unlockStorage = async () => {
    setLoading(true);
    setError(null);

    try {
      const success = await secureApiKeyManager.initialize(masterPassword);
      if (!success) {
        throw new SecurityError('Invalid password or failed to unlock storage');
      }

      setIsInitialized(true);
      setShowSetupModal(false);
      setMasterPassword(''); // Clear password from memory
      toast.success('Storage unlocked successfully');
      
      await loadExistingKeys();
      await loadSecurityMetrics();
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to unlock storage');
      toast.error('Failed to unlock storage');
    } finally {
      setLoading(false);
    }
  };

  // Save API keys
  const saveApiKeys = async () => {
    if (!isInitialized) {
      toast.error('Please initialize secure storage first');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Validate keys before saving
      const keysToSave: { unsplash?: string; openai?: string } = {};
      
      if (apiKeys.unsplash) {
        const validation = ApiKeyProtection.validateApiKeyFormat(apiKeys.unsplash, 'unsplash');
        if (!validation.valid) {
          throw new SecurityError(`Invalid Unsplash API key: ${validation.reason}`);
        }
        keysToSave.unsplash = apiKeys.unsplash;
      }

      if (apiKeys.openai) {
        const validation = ApiKeyProtection.validateApiKeyFormat(apiKeys.openai, 'openai');
        if (!validation.valid) {
          throw new SecurityError(`Invalid OpenAI API key: ${validation.reason}`);
        }
        keysToSave.openai = apiKeys.openai;
      }

      await secureApiKeyManager.storeApiKeys(keysToSave);
      
      // Test the keys
      await testApiKeys();
      
      toast.success('API keys saved and encrypted successfully');
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to save API keys');
      toast.error('Failed to save API keys');
    } finally {
      setLoading(false);
    }
  };

  // Test API keys
  const testApiKeys = async () => {
    if (!apiKeys.unsplash && !apiKeys.openai) return;

    const newStatus = { ...keyStatus };

    if (apiKeys.unsplash) {
      newStatus.unsplash = 'testing';
      setKeyStatus({ ...newStatus });

      try {
        // Simple validation test for Unsplash
        const response = await fetch('https://api.unsplash.com/me', {
          headers: { Authorization: `Client-ID ${apiKeys.unsplash}` }
        });
        newStatus.unsplash = response.ok ? 'valid' : 'invalid';
      } catch {
        newStatus.unsplash = 'invalid';
      }
    }

    if (apiKeys.openai) {
      newStatus.openai = 'testing';
      setKeyStatus({ ...newStatus });

      try {
        // Simple validation test for OpenAI
        const response = await fetch('https://api.openai.com/v1/models', {
          headers: { Authorization: `Bearer ${apiKeys.openai}` }
        });
        newStatus.openai = response.ok ? 'valid' : 'invalid';
      } catch {
        newStatus.openai = 'invalid';
      }
    }

    setKeyStatus(newStatus);
  };

  // Rotate encryption key
  const rotateEncryptionKey = async () => {
    setLoading(true);
    setError(null);

    try {
      if (calculatePasswordStrength(rotationData.newPassword) < 60) {
        throw new SecurityError('New password is too weak');
      }

      await secureApiKeyManager.rotateEncryptionKey(
        rotationData.oldPassword,
        rotationData.newPassword
      );

      setShowRotationModal(false);
      setRotationData({ oldPassword: '', newPassword: '' });
      toast.success('Encryption key rotated successfully');
      
      await loadSecurityMetrics();
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to rotate encryption key');
      toast.error('Failed to rotate encryption key');
    } finally {
      setLoading(false);
    }
  };

  // Clear all keys
  const clearAllKeys = async () => {
    if (!confirm('Are you sure you want to clear all API keys? This action cannot be undone.')) {
      return;
    }

    try {
      await secureApiKeyManager.clearKeys();
      setIsInitialized(false);
      setApiKeys({ unsplash: '', openai: '' });
      setKeyStatus({ unsplash: 'missing', openai: 'missing' });
      toast.success('All API keys cleared successfully');
    } catch (error) {
      toast.error('Failed to clear API keys');
    }
  };

  // Get status icon and color
  const getStatusIcon = (status: ApiKeyStatus[keyof ApiKeyStatus]) => {
    switch (status) {
      case 'valid':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'invalid':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
      case 'testing':
        return <ClockIcon className="h-5 w-5 text-yellow-500 animate-spin" />;
      default:
        return <KeyIcon className="h-5 w-5 text-gray-400" />;
    }
  };

  // Render password strength indicator
  const renderPasswordStrength = (strength: number) => {
    const getColor = () => {
      if (strength < 40) return 'bg-red-500';
      if (strength < 70) return 'bg-yellow-500';
      return 'bg-green-500';
    };

    const getLabel = () => {
      if (strength < 40) return 'Weak';
      if (strength < 70) return 'Medium';
      return 'Strong';
    };

    return (
      <div className="mt-2">
        <div className="flex justify-between text-sm">
          <span>Password Strength:</span>
          <span className={`font-medium ${
            strength < 40 ? 'text-red-600' : 
            strength < 70 ? 'text-yellow-600' : 'text-green-600'
          }`}>
            {getLabel()}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
          <div 
            className={`h-2 rounded-full transition-all duration-300 ${getColor()}`}
            style={{ width: `${strength}%` }}
          />
        </div>
      </div>
    );
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center mb-8">
        <ShieldCheckIcon className="h-12 w-12 text-blue-600 mx-auto mb-4" />
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          API Key Security Manager
        </h1>
        <p className="text-gray-600 dark:text-gray-300">
          Securely store and manage your API keys with client-side encryption
        </p>
      </div>

      {/* Security Metrics */}
      {securityMetrics && (
        <Card className="bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                {securityMetrics.keyRotations}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Key Rotations</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                {securityMetrics.encryptionMethod}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Encryption</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                {securityMetrics.lastAccess ? 
                  new Date(securityMetrics.lastAccess).toLocaleDateString() : 'Never'
                }
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Last Access</div>
            </div>
          </div>
        </Card>
      )}

      {/* Main Content */}
      {!isInitialized ? (
        <Card>
          <div className="text-center py-8">
            <KeyIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h2 className="text-xl font-semibold mb-2">Secure Storage Not Initialized</h2>
            <p className="text-gray-600 mb-6">
              Initialize secure storage to encrypt and protect your API keys
            </p>
            <Button 
              onClick={() => setShowSetupModal(true)}
              className="bg-blue-600 hover:bg-blue-700"
            >
              Initialize Secure Storage
            </Button>
          </div>
        </Card>
      ) : (
        <div className="space-y-6">
          {/* API Keys Form */}
          <Card>
            <h2 className="text-xl font-semibold mb-6 flex items-center">
              <KeyIcon className="h-6 w-6 mr-2" />
              API Keys
            </h2>

            <div className="space-y-4">
              {/* Unsplash API Key */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Unsplash Access Key
                  {getStatusIcon(keyStatus.unsplash)}
                </label>
                <div className="relative">
                  <input
                    type={showApiKeys.unsplash ? 'text' : 'password'}
                    value={apiKeys.unsplash}
                    onChange={(e) => setApiKeys(prev => ({ ...prev, unsplash: e.target.value }))}
                    className="w-full px-4 py-2 pr-12 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                    placeholder="Enter your Unsplash access key..."
                  />
                  <button
                    type="button"
                    onClick={() => setShowApiKeys(prev => ({ ...prev, unsplash: !prev.unsplash }))}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2"
                  >
                    {showApiKeys.unsplash ? 
                      <EyeSlashIcon className="h-5 w-5 text-gray-400" /> :
                      <EyeIcon className="h-5 w-5 text-gray-400" />
                    }
                  </button>
                </div>
                <p className="mt-1 text-xs text-gray-500">
                  Get your access key from{' '}
                  <a 
                    href="https://unsplash.com/developers" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-500 hover:underline"
                  >
                    Unsplash Developers
                  </a>
                </p>
              </div>

              {/* OpenAI API Key */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  OpenAI API Key
                  {getStatusIcon(keyStatus.openai)}
                </label>
                <div className="relative">
                  <input
                    type={showApiKeys.openai ? 'text' : 'password'}
                    value={apiKeys.openai}
                    onChange={(e) => setApiKeys(prev => ({ ...prev, openai: e.target.value }))}
                    className="w-full px-4 py-2 pr-12 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                    placeholder="Enter your OpenAI API key..."
                  />
                  <button
                    type="button"
                    onClick={() => setShowApiKeys(prev => ({ ...prev, openai: !prev.openai }))}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2"
                  >
                    {showApiKeys.openai ? 
                      <EyeSlashIcon className="h-5 w-5 text-gray-400" /> :
                      <EyeIcon className="h-5 w-5 text-gray-400" />
                    }
                  </button>
                </div>
                <p className="mt-1 text-xs text-gray-500">
                  Get your API key from{' '}
                  <a 
                    href="https://platform.openai.com/api-keys" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-500 hover:underline"
                  >
                    OpenAI Platform
                  </a>
                </p>
              </div>
            </div>

            {error && (
              <div className="mt-4 p-3 bg-red-100 dark:bg-red-900/20 border border-red-300 dark:border-red-800 rounded-lg text-red-700 dark:text-red-400 text-sm">
                {error}
              </div>
            )}

            <div className="mt-6 flex flex-wrap gap-3">
              <Button
                onClick={saveApiKeys}
                disabled={loading}
                className="bg-green-600 hover:bg-green-700"
              >
                {loading ? 'Saving...' : 'Save & Encrypt Keys'}
              </Button>
              
              <Button
                onClick={testApiKeys}
                disabled={loading || (!apiKeys.unsplash && !apiKeys.openai)}
                variant="outline"
              >
                Test Keys
              </Button>

              <Button
                onClick={() => setShowRotationModal(true)}
                variant="outline"
                className="text-blue-600 border-blue-600 hover:bg-blue-50"
              >
                Rotate Encryption Key
              </Button>

              <Button
                onClick={clearAllKeys}
                variant="outline"
                className="text-red-600 border-red-600 hover:bg-red-50"
              >
                Clear All Keys
              </Button>
            </div>
          </Card>

          {/* Security Tips */}
          <Card className="bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800">
            <h3 className="text-lg font-semibold text-yellow-800 dark:text-yellow-200 mb-3">
              Security Best Practices
            </h3>
            <ul className="space-y-2 text-sm text-yellow-700 dark:text-yellow-300">
              <li>• Never share your API keys with anyone</li>
              <li>• Rotate your keys regularly (every 30-90 days)</li>
              <li>• Monitor your API usage for unusual activity</li>
              <li>• Use different keys for development and production</li>
              <li>• Keep your master password secure and unique</li>
            </ul>
          </Card>
        </div>
      )}

      {/* Setup Modal */}
      <Modal 
        isOpen={showSetupModal} 
        onClose={() => setShowSetupModal(false)}
        title={securityMetrics ? "Unlock Secure Storage" : "Initialize Secure Storage"}
      >
        <div className="space-y-4">
          <p className="text-gray-600 dark:text-gray-300">
            {securityMetrics ? 
              "Enter your master password to unlock your encrypted API keys." :
              "Create a strong master password to encrypt your API keys locally."
            }
          </p>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Master Password
            </label>
            <div className="relative">
              <input
                type={showMasterPassword ? 'text' : 'password'}
                value={masterPassword}
                onChange={(e) => setMasterPassword(e.target.value)}
                className="w-full px-4 py-2 pr-12 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
                placeholder={securityMetrics ? "Enter your master password..." : "Create a strong master password..."}
              />
              <button
                type="button"
                onClick={() => setShowMasterPassword(!showMasterPassword)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2"
              >
                {showMasterPassword ? 
                  <EyeSlashIcon className="h-5 w-5 text-gray-400" /> :
                  <EyeIcon className="h-5 w-5 text-gray-400" />
                }
              </button>
            </div>
            
            {!securityMetrics && renderPasswordStrength(passwordStrength)}
          </div>

          {error && (
            <div className="p-3 bg-red-100 dark:bg-red-900/20 border border-red-300 dark:border-red-800 rounded-lg text-red-700 dark:text-red-400 text-sm">
              {error}
            </div>
          )}

          <div className="flex gap-3 pt-4">
            <Button
              onClick={securityMetrics ? unlockStorage : initializeStorage}
              disabled={loading || !masterPassword || (!securityMetrics && passwordStrength < 60)}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {loading ? 'Processing...' : (securityMetrics ? 'Unlock' : 'Initialize')}
            </Button>
            
            <Button
              onClick={() => {
                setShowSetupModal(false);
                setMasterPassword('');
                setError(null);
              }}
              variant="outline"
            >
              Cancel
            </Button>
          </div>
        </div>
      </Modal>

      {/* Rotation Modal */}
      <Modal 
        isOpen={showRotationModal} 
        onClose={() => setShowRotationModal(false)}
        title="Rotate Encryption Key"
      >
        <div className="space-y-4">
          <p className="text-gray-600 dark:text-gray-300">
            Rotating your encryption key enhances security. Enter your current password and create a new one.
          </p>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Current Password
            </label>
            <input
              type="password"
              value={rotationData.oldPassword}
              onChange={(e) => setRotationData(prev => ({ ...prev, oldPassword: e.target.value }))}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
              placeholder="Enter current password..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              New Password
            </label>
            <input
              type="password"
              value={rotationData.newPassword}
              onChange={(e) => setRotationData(prev => ({ ...prev, newPassword: e.target.value }))}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
              placeholder="Create new password..."
            />
            {renderPasswordStrength(calculatePasswordStrength(rotationData.newPassword))}
          </div>

          {error && (
            <div className="p-3 bg-red-100 dark:bg-red-900/20 border border-red-300 dark:border-red-800 rounded-lg text-red-700 dark:text-red-400 text-sm">
              {error}
            </div>
          )}

          <div className="flex gap-3 pt-4">
            <Button
              onClick={rotateEncryptionKey}
              disabled={loading || !rotationData.oldPassword || !rotationData.newPassword || 
                        calculatePasswordStrength(rotationData.newPassword) < 60}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {loading ? 'Rotating...' : 'Rotate Key'}
            </Button>
            
            <Button
              onClick={() => {
                setShowRotationModal(false);
                setRotationData({ oldPassword: '', newPassword: '' });
                setError(null);
              }}
              variant="outline"
            >
              Cancel
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};