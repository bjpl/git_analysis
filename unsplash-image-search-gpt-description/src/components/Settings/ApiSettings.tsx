/**
 * API Settings Component
 * Allows users to configure their API keys with secure storage
 */

import React, { useState, useEffect } from 'react';
import { Eye, EyeOff, Check, X, ExternalLink, AlertCircle, Loader2 } from 'lucide-react';
import { apiConfigService } from '../../services/apiConfigService';
import { API_PROVIDERS, ApiProviderName, ApiConfiguration, ValidationResult } from '../../types/api';

interface ApiKeyInputProps {
  provider: ApiProviderName;
  value: string;
  onChange: (value: string) => void;
  onValidate: () => void;
  isValidating: boolean;
  validationResult?: ValidationResult;
  showValue: boolean;
  onToggleShow: () => void;
}

const ApiKeyInput: React.FC<ApiKeyInputProps> = ({
  provider,
  value,
  onChange,
  onValidate,
  isValidating,
  validationResult,
  showValue,
  onToggleShow
}) => {
  const providerInfo = API_PROVIDERS[provider];

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
            {providerInfo.displayName}
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {providerInfo.description}
          </p>
        </div>
        <a
          href={providerInfo.getApiKeyUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center px-3 py-1 text-sm bg-blue-50 text-blue-700 rounded-md hover:bg-blue-100 dark:bg-blue-900/20 dark:text-blue-300 dark:hover:bg-blue-900/30 transition-colors"
        >
          Get API Key
          <ExternalLink className="ml-1 h-3 w-3" />
        </a>
      </div>

      <div className="space-y-2">
        <div className="relative">
          <input
            type={showValue ? 'text' : 'password'}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder={providerInfo.placeholder}
            className="w-full px-3 py-2 pr-20 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100 dark:placeholder-gray-400"
          />
          <div className="absolute inset-y-0 right-0 flex items-center">
            <button
              type="button"
              onClick={onToggleShow}
              className="px-2 py-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              title={showValue ? 'Hide API key' : 'Show API key'}
            >
              {showValue ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
            <button
              type="button"
              onClick={onValidate}
              disabled={isValidating || !value.trim()}
              className="ml-1 mr-2 px-2 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-gray-600 dark:text-gray-200 dark:hover:bg-gray-500"
              title="Test API key"
            >
              {isValidating ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                'Test'
              )}
            </button>
          </div>
        </div>

        {/* Validation Status */}
        {validationResult && (
          <div className={`flex items-center space-x-2 text-sm ${
            validationResult.isValid 
              ? 'text-green-600 dark:text-green-400' 
              : 'text-red-600 dark:text-red-400'
          }`}>
            {validationResult.isValid ? (
              <Check className="h-4 w-4" />
            ) : (
              <X className="h-4 w-4" />
            )}
            <span>
              {validationResult.isValid 
                ? 'API key is valid' 
                : `Invalid: ${validationResult.error}`
              }
            </span>
          </div>
        )}

        <p className="text-xs text-gray-500 dark:text-gray-400">
          {providerInfo.helpText}
        </p>
      </div>
    </div>
  );
};

export const ApiSettings: React.FC = () => {
  const [config, setConfig] = useState<ApiConfiguration | null>(null);
  const [tempKeys, setTempKeys] = useState<{ [K in ApiProviderName]: string }>({
    unsplash: '',
    openai: ''
  });
  const [showKeys, setShowKeys] = useState<{ [K in ApiProviderName]: boolean }>({
    unsplash: false,
    openai: false
  });
  const [validatingKeys, setValidatingKeys] = useState<{ [K in ApiProviderName]: boolean }>({
    unsplash: false,
    openai: false
  });
  const [validationResults, setValidationResults] = useState<{ [K in ApiProviderName]?: ValidationResult }>({});
  const [isSaving, setIsSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadConfiguration();
  }, []);

  useEffect(() => {
    if (config) {
      const hasAnyChanges = Object.entries(tempKeys).some(([provider, value]) => {
        const storedKey = config.keys[provider as ApiProviderName] || '';
        return value !== storedKey;
      });
      setHasChanges(hasAnyChanges);
    }
  }, [tempKeys, config]);

  const loadConfiguration = async () => {
    try {
      setLoading(true);
      const currentConfig = await apiConfigService.getConfiguration();
      setConfig(currentConfig);
      
      // Load current keys into temp state
      const newTempKeys = { ...tempKeys };
      Object.entries(currentConfig.keys).forEach(([provider, key]) => {
        newTempKeys[provider as ApiProviderName] = key || '';
      });
      setTempKeys(newTempKeys);
    } catch (error) {
      console.error('Failed to load API configuration:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyChange = (provider: ApiProviderName, value: string) => {
    setTempKeys(prev => ({ ...prev, [provider]: value }));
    // Clear validation result when key changes
    setValidationResults(prev => ({ ...prev, [provider]: undefined }));
  };

  const validateKey = async (provider: ApiProviderName) => {
    const key = tempKeys[provider].trim();
    if (!key) return;

    setValidatingKeys(prev => ({ ...prev, [provider]: true }));
    
    try {
      const result = await apiConfigService.validateApiKey(provider, key);
      setValidationResults(prev => ({ ...prev, [provider]: result }));
    } catch (error) {
      setValidationResults(prev => ({
        ...prev,
        [provider]: {
          isValid: false,
          error: error instanceof Error ? error.message : 'Validation failed'
        }
      }));
    } finally {
      setValidatingKeys(prev => ({ ...prev, [provider]: false }));
    }
  };

  const toggleShowKey = (provider: ApiProviderName) => {
    setShowKeys(prev => ({ ...prev, [provider]: !prev[provider] }));
  };

  const saveConfiguration = async () => {
    setIsSaving(true);
    
    try {
      // Save each API key
      for (const [provider, key] of Object.entries(tempKeys)) {
        const cleanKey = key.trim() || null;
        await apiConfigService.setApiKey(provider as ApiProviderName, cleanKey);
      }
      
      // Reload configuration to get updated status
      await loadConfiguration();
      setHasChanges(false);
      
      // Clear validation results
      setValidationResults({});
    } catch (error) {
      console.error('Failed to save configuration:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const resetChanges = () => {
    if (config) {
      const resetKeys = { ...tempKeys };
      Object.entries(config.keys).forEach(([provider, key]) => {
        resetKeys[provider as ApiProviderName] = key || '';
      });
      setTempKeys(resetKeys);
      setValidationResults({});
      setHasChanges(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-6 w-6 animate-spin text-blue-500" />
        <span className="ml-2 text-gray-600 dark:text-gray-400">Loading API settings...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
        <div className="flex items-start space-x-2">
          <AlertCircle className="h-5 w-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-blue-800 dark:text-blue-200">
            <p className="font-medium mb-1">Secure Storage</p>
            <p>
              API keys are encrypted and stored locally in your browser. They are never sent to our servers.
              You can always clear them or reconfigure as needed.
            </p>
          </div>
        </div>
      </div>

      <div className="space-y-8">
        {Object.entries(API_PROVIDERS).map(([providerKey, provider]) => (
          <ApiKeyInput
            key={providerKey}
            provider={providerKey as ApiProviderName}
            value={tempKeys[providerKey as ApiProviderName]}
            onChange={(value) => handleKeyChange(providerKey as ApiProviderName, value)}
            onValidate={() => validateKey(providerKey as ApiProviderName)}
            isValidating={validatingKeys[providerKey as ApiProviderName]}
            validationResult={validationResults[providerKey as ApiProviderName]}
            showValue={showKeys[providerKey as ApiProviderName]}
            onToggleShow={() => toggleShowKey(providerKey as ApiProviderName)}
          />
        ))}
      </div>

      {/* Action Buttons */}
      {hasChanges && (
        <div className="flex items-center justify-between pt-6 border-t border-gray-200 dark:border-gray-700">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            You have unsaved changes
          </p>
          <div className="flex space-x-3">
            <button
              onClick={resetChanges}
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200"
            >
              Cancel
            </button>
            <button
              onClick={saveConfiguration}
              disabled={isSaving}
              className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              {isSaving ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  Saving...
                </>
              ) : (
                'Save Changes'
              )}
            </button>
          </div>
        </div>
      )}

      {/* Current Status */}
      {config && (
        <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
            Current Status
          </h3>
          <div className="grid gap-4 md:grid-cols-2">
            {Object.entries(config.status).map(([providerKey, status]) => (
              <div
                key={providerKey}
                className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-gray-900 dark:text-gray-100">
                    {API_PROVIDERS[providerKey as ApiProviderName].displayName}
                  </span>
                  <div className={`flex items-center space-x-1 text-sm ${
                    status.isValid 
                      ? 'text-green-600 dark:text-green-400' 
                      : status.isConfigured
                        ? 'text-yellow-600 dark:text-yellow-400'
                        : 'text-gray-500 dark:text-gray-400'
                  }`}>
                    {status.isValid ? (
                      <Check className="h-4 w-4" />
                    ) : status.isConfigured ? (
                      <AlertCircle className="h-4 w-4" />
                    ) : (
                      <X className="h-4 w-4" />
                    )}
                    <span>
                      {status.isValid 
                        ? 'Valid' 
                        : status.isConfigured 
                          ? 'Not validated' 
                          : 'Not configured'
                      }
                    </span>
                  </div>
                </div>
                {status.lastValidated && (
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Last validated: {status.lastValidated.toLocaleString()}
                  </p>
                )}
                {status.error && (
                  <p className="text-xs text-red-600 dark:text-red-400 mt-1">
                    Error: {status.error}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};