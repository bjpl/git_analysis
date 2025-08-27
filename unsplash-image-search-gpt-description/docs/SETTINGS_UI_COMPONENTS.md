# Settings UI Components Architecture

## Overview

This document outlines the comprehensive user interface components for VocabLens's runtime API key configuration system. The UI is designed to be intuitive, secure, and accessible while providing advanced configuration options for power users.

## Component Hierarchy

```
SettingsModal
├── SettingsTabs
│   ├── APIKeysTab
│   │   ├── ServiceStatusDashboard
│   │   ├── APIKeyForm (per service)
│   │   ├── ValidationIndicator
│   │   ├── TestConnectivityButton
│   │   └── SecurityOptions
│   ├── StorageTab
│   │   ├── SecurityLevelSelector
│   │   ├── ExpirationSettings
│   │   ├── MasterPasswordSection
│   │   └── StorageUsageDisplay
│   ├── MigrationTab
│   │   ├── EnvironmentImporter
│   │   ├── ConfigurationExporter
│   │   └── ResetSection
│   └── AdvancedTab
│       ├── ServiceEndpoints
│       ├── RateLimitSettings
│       └── DebugInformation
└── FirstTimeSetup
    ├── WelcomeStep
    ├── SecurityExplanationStep
    ├── APIKeyInputStep
    ├── ValidationStep
    └── CompletionStep
```

## Core Components

### 1. Settings Modal Container

```typescript
// src/components/Settings/SettingsModal.tsx

import React, { useState, useEffect } from 'react';
import { X, Shield, Key, Database, Settings as SettingsIcon } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialTab?: 'api-keys' | 'storage' | 'migration' | 'advanced';
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose,
  initialTab = 'api-keys'
}) => {
  const [activeTab, setActiveTab] = useState(initialTab);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  const tabs = [
    { id: 'api-keys', label: 'API Keys', icon: Key },
    { id: 'storage', label: 'Storage', icon: Shield },
    { id: 'migration', label: 'Migration', icon: Database },
    { id: 'advanced', label: 'Advanced', icon: SettingsIcon }
  ];

  const handleClose = () => {
    if (hasUnsavedChanges) {
      if (window.confirm('You have unsaved changes. Are you sure you want to close?')) {
        onClose();
      }
    } else {
      onClose();
    }
  };

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        handleClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, hasUnsavedChanges]);

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
        onClick={(e) => e.target === e.currentTarget && handleClose()}
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-4xl h-[80vh] flex flex-col"
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b dark:border-gray-700">
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white">
              Settings
            </h2>
            <button
              onClick={handleClose}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              aria-label="Close settings"
            >
              <X className="w-5 h-5 text-gray-500 dark:text-gray-400" />
            </button>
          </div>

          <div className="flex flex-1 overflow-hidden">
            {/* Sidebar */}
            <div className="w-64 bg-gray-50 dark:bg-gray-900 border-r dark:border-gray-700 p-4">
              <nav className="space-y-2">
                {tabs.map(({ id, label, icon: Icon }) => (
                  <button
                    key={id}
                    onClick={() => setActiveTab(id)}
                    className={`
                      w-full flex items-center gap-3 px-3 py-2 text-left rounded-lg transition-colors
                      ${activeTab === id
                        ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                        : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'
                      }
                    `}
                  >
                    <Icon className="w-5 h-5" />
                    {label}
                  </button>
                ))}
              </nav>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6">
              {activeTab === 'api-keys' && (
                <APIKeysTab onChangesSaved={setHasUnsavedChanges} />
              )}
              {activeTab === 'storage' && (
                <StorageTab onChangesSaved={setHasUnsavedChanges} />
              )}
              {activeTab === 'migration' && (
                <MigrationTab onChangesSaved={setHasUnsavedChanges} />
              )}
              {activeTab === 'advanced' && (
                <AdvancedTab onChangesSaved={setHasUnsavedChanges} />
              )}
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};
```

### 2. API Keys Tab

```typescript
// src/components/Settings/APIKeysTab.tsx

import React, { useState, useEffect } from 'react';
import { CheckCircle, XCircle, AlertTriangle, Eye, EyeOff, TestTube } from 'lucide-react';
import { useAPIKeyManager } from '../../hooks/useAPIKeyManager';
import { ServiceStatusDashboard } from './ServiceStatusDashboard';
import { ValidationIndicator } from './ValidationIndicator';

interface APIKeysTabProps {
  onChangesSaved: (hasChanges: boolean) => void;
}

interface ServiceConfig {
  name: string;
  key: 'unsplash' | 'openai' | 'supabase';
  label: string;
  placeholder: string;
  helpText: string;
  validation: RegExp;
  required: boolean;
}

const services: ServiceConfig[] = [
  {
    name: 'Unsplash',
    key: 'unsplash',
    label: 'Unsplash Access Key',
    placeholder: 'Enter your Unsplash Access Key',
    helpText: 'Get your free API key from https://unsplash.com/developers',
    validation: /^[A-Za-z0-9_-]{20,50}$/,
    required: false
  },
  {
    name: 'OpenAI',
    key: 'openai',
    label: 'OpenAI API Key',
    placeholder: 'sk-...',
    helpText: 'Get your API key from https://platform.openai.com/api-keys',
    validation: /^sk-[A-Za-z0-9]{20,}$/,
    required: true
  },
  {
    name: 'Supabase',
    key: 'supabase',
    label: 'Supabase Anonymous Key',
    placeholder: 'eyJ...',
    helpText: 'Find your project keys in Supabase dashboard settings',
    validation: /^eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*$/,
    required: false
  }
];

export const APIKeysTab: React.FC<APIKeysTabProps> = ({ onChangesSaved }) => {
  const {
    apiKeys,
    setAPIKey,
    validateKey,
    testConnectivity,
    getServiceStatus
  } = useAPIKeyManager();

  const [formData, setFormData] = useState<Record<string, string>>({});
  const [showKeys, setShowKeys] = useState<Record<string, boolean>>({});
  const [validation, setValidation] = useState<Record<string, {
    isValid: boolean;
    error?: string;
    isValidating?: boolean;
  }>>({});
  const [hasChanges, setHasChanges] = useState(false);

  // Initialize form data
  useEffect(() => {
    const initialData: Record<string, string> = {};
    services.forEach(service => {
      initialData[service.key] = apiKeys[service.key] || '';
    });
    setFormData(initialData);
  }, [apiKeys]);

  // Track changes
  useEffect(() => {
    const hasUnsavedChanges = Object.keys(formData).some(key => 
      formData[key] !== (apiKeys[key as keyof typeof apiKeys] || '')
    );
    setHasChanges(hasUnsavedChanges);
    onChangesSaved(hasUnsavedChanges);
  }, [formData, apiKeys, onChangesSaved]);

  const handleInputChange = (key: string, value: string) => {
    setFormData(prev => ({ ...prev, [key]: value }));
    
    // Clear previous validation
    setValidation(prev => ({ ...prev, [key]: { isValid: false } }));
    
    // Validate format immediately
    const service = services.find(s => s.key === key);
    if (service && value) {
      const formatValid = service.validation.test(value);
      setValidation(prev => ({
        ...prev,
        [key]: {
          isValid: formatValid,
          error: formatValid ? undefined : 'Invalid format'
        }
      }));
    }
  };

  const handleValidateKey = async (serviceKey: string) => {
    const value = formData[serviceKey];
    if (!value) return;

    setValidation(prev => ({
      ...prev,
      [serviceKey]: { ...prev[serviceKey], isValidating: true }
    }));

    try {
      const result = await validateKey(serviceKey as any, value);
      setValidation(prev => ({
        ...prev,
        [serviceKey]: {
          isValid: result.valid,
          error: result.error,
          isValidating: false
        }
      }));
    } catch (error) {
      setValidation(prev => ({
        ...prev,
        [serviceKey]: {
          isValid: false,
          error: 'Validation failed',
          isValidating: false
        }
      }));
    }
  };

  const handleTestConnectivity = async (serviceKey: string) => {
    const value = formData[serviceKey];
    if (!value) return;

    try {
      const result = await testConnectivity(serviceKey as any, value);
      setValidation(prev => ({
        ...prev,
        [serviceKey]: {
          ...prev[serviceKey],
          isValid: result,
          error: result ? undefined : 'Connection test failed'
        }
      }));
    } catch (error) {
      setValidation(prev => ({
        ...prev,
        [serviceKey]: {
          ...prev[serviceKey],
          isValid: false,
          error: 'Connection test failed'
        }
      }));
    }
  };

  const handleSave = async () => {
    const validationPromises = Object.entries(formData).map(([key, value]) => {
      if (value && value !== apiKeys[key as keyof typeof apiKeys]) {
        return handleValidateKey(key);
      }
      return Promise.resolve();
    });

    await Promise.all(validationPromises);

    // Save valid keys
    for (const [key, value] of Object.entries(formData)) {
      if (value && validation[key]?.isValid) {
        await setAPIKey(key as any, value);
      }
    }

    setHasChanges(false);
    onChangesSaved(false);
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          API Configuration
        </h3>
        <p className="text-gray-600 dark:text-gray-400 text-sm">
          Configure your API keys for external services. Keys are encrypted and stored securely.
        </p>
      </div>

      {/* Service Status Dashboard */}
      <ServiceStatusDashboard />

      {/* API Key Forms */}
      <div className="space-y-6">
        {services.map(service => (
          <div key={service.key} className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <h4 className="font-medium text-gray-900 dark:text-white">
                {service.name}
              </h4>
              {service.required && (
                <span className="text-xs bg-red-100 text-red-600 px-2 py-1 rounded">
                  Required
                </span>
              )}
              <ValidationIndicator
                status={validation[service.key]?.isValid ? 'valid' : 
                       validation[service.key]?.error ? 'invalid' : 'unknown'}
                isValidating={validation[service.key]?.isValidating}
              />
            </div>

            <div className="space-y-3">
              <div className="relative">
                <input
                  type={showKeys[service.key] ? 'text' : 'password'}
                  value={formData[service.key] || ''}
                  onChange={(e) => handleInputChange(service.key, e.target.value)}
                  placeholder={service.placeholder}
                  className={`
                    w-full px-3 py-2 pr-20 border rounded-lg
                    ${validation[service.key]?.isValid ? 'border-green-300' : 
                      validation[service.key]?.error ? 'border-red-300' : 'border-gray-300'}
                    dark:border-gray-600 dark:bg-gray-800 dark:text-white
                    focus:outline-none focus:ring-2 focus:ring-blue-500
                  `}
                />
                <div className="absolute right-2 top-2 flex gap-1">
                  <button
                    type="button"
                    onClick={() => setShowKeys(prev => ({ 
                      ...prev, 
                      [service.key]: !prev[service.key] 
                    }))}
                    className="p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded"
                    aria-label={showKeys[service.key] ? 'Hide key' : 'Show key'}
                  >
                    {showKeys[service.key] ? 
                      <EyeOff className="w-4 h-4" /> : 
                      <Eye className="w-4 h-4" />
                    }
                  </button>
                  {formData[service.key] && (
                    <button
                      type="button"
                      onClick={() => handleTestConnectivity(service.key)}
                      className="p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded"
                      aria-label="Test connectivity"
                      disabled={validation[service.key]?.isValidating}
                    >
                      <TestTube className={`w-4 h-4 ${
                        validation[service.key]?.isValidating ? 'animate-spin' : ''
                      }`} />
                    </button>
                  )}
                </div>
              </div>

              {validation[service.key]?.error && (
                <p className="text-red-600 text-sm flex items-center gap-1">
                  <XCircle className="w-4 h-4" />
                  {validation[service.key].error}
                </p>
              )}

              <p className="text-gray-500 dark:text-gray-400 text-xs">
                {service.helpText}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Action Buttons */}
      {hasChanges && (
        <div className="flex gap-3 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <button
            onClick={handleSave}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Save Changes
          </button>
          <button
            onClick={() => {
              setFormData(apiKeys);
              setHasChanges(false);
              onChangesSaved(false);
            }}
            className="px-4 py-2 border border-gray-300 text-gray-700 dark:text-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
          >
            Cancel
          </button>
        </div>
      )}
    </div>
  );
};
```

### 3. Service Status Dashboard

```typescript
// src/components/Settings/ServiceStatusDashboard.tsx

import React, { useEffect, useState } from 'react';
import { CheckCircle, XCircle, AlertTriangle, RefreshCw } from 'lucide-react';
import { useAPIKeyManager } from '../../hooks/useAPIKeyManager';

interface ServiceStatus {
  service: string;
  status: 'active' | 'inactive' | 'error' | 'warning';
  message: string;
  lastChecked?: Date;
  capabilities?: string[];
  rateLimit?: {
    used: number;
    limit: number;
    resetTime?: Date;
  };
}

export const ServiceStatusDashboard: React.FC = () => {
  const { getServiceStatus, refreshServiceStatus } = useAPIKeyManager();
  const [services, setServices] = useState<ServiceStatus[]>([]);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const loadServiceStatus = async () => {
    const statusPromises = ['unsplash', 'openai', 'supabase'].map(async (service) => {
      try {
        const status = await getServiceStatus(service as any);
        return {
          service,
          status: status.active ? 'active' : status.error ? 'error' : 'inactive',
          message: status.message || `${service} service status`,
          lastChecked: status.lastChecked ? new Date(status.lastChecked) : undefined,
          capabilities: status.capabilities,
          rateLimit: status.rateLimit
        } as ServiceStatus;
      } catch (error) {
        return {
          service,
          status: 'error',
          message: 'Failed to check service status'
        } as ServiceStatus;
      }
    });

    const results = await Promise.all(statusPromises);
    setServices(results);
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await Promise.all(['unsplash', 'openai', 'supabase'].map(service => 
        refreshServiceStatus(service as any)
      ));
      await loadServiceStatus();
    } catch (error) {
      console.error('Failed to refresh service status:', error);
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    loadServiceStatus();
    
    // Refresh every 5 minutes
    const interval = setInterval(loadServiceStatus, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status: ServiceStatus['status']) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'error':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      default:
        return <XCircle className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: ServiceStatus['status']) => {
    switch (status) {
      case 'active':
        return 'bg-green-50 border-green-200 dark:bg-green-900/20 dark:border-green-800';
      case 'error':
        return 'bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200 dark:bg-yellow-900/20 dark:border-yellow-800';
      default:
        return 'bg-gray-50 border-gray-200 dark:bg-gray-900/20 dark:border-gray-700';
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-medium text-gray-900 dark:text-white">Service Status</h3>
        <button
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          aria-label="Refresh service status"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
        </button>
      </div>

      <div className="p-4 space-y-3">
        {services.map(service => (
          <div
            key={service.service}
            className={`border rounded-lg p-3 ${getStatusColor(service.status)}`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {getStatusIcon(service.status)}
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white capitalize">
                    {service.service}
                  </h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {service.message}
                  </p>
                </div>
              </div>
              
              {service.lastChecked && (
                <div className="text-right">
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Last checked
                  </p>
                  <p className="text-xs text-gray-600 dark:text-gray-300">
                    {service.lastChecked.toLocaleTimeString()}
                  </p>
                </div>
              )}
            </div>

            {/* Rate Limit Information */}
            {service.rateLimit && (
              <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-600">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-500 dark:text-gray-400">Rate Limit</span>
                  <span className="text-gray-600 dark:text-gray-300">
                    {service.rateLimit.used}/{service.rateLimit.limit}
                  </span>
                </div>
                <div className="mt-1 bg-gray-200 dark:bg-gray-600 rounded-full h-1">
                  <div
                    className="bg-blue-500 h-1 rounded-full transition-all"
                    style={{
                      width: `${(service.rateLimit.used / service.rateLimit.limit) * 100}%`
                    }}
                  />
                </div>
              </div>
            )}

            {/* Capabilities */}
            {service.capabilities && service.capabilities.length > 0 && (
              <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-600">
                <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Capabilities</p>
                <div className="flex flex-wrap gap-1">
                  {service.capabilities.map(capability => (
                    <span
                      key={capability}
                      className="px-2 py-1 text-xs bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 rounded"
                    >
                      {capability}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
```

### 4. First-Time Setup Flow

```typescript
// src/components/Settings/FirstTimeSetup.tsx

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowRight, ArrowLeft, Shield, Key, CheckCircle, AlertTriangle } from 'lucide-react';
import { useAPIKeyManager } from '../../hooks/useAPIKeyManager';

interface FirstTimeSetupProps {
  isOpen: boolean;
  onComplete: () => void;
  onSkip: () => void;
}

type Step = 'welcome' | 'security' | 'input' | 'validation' | 'complete';

export const FirstTimeSetup: React.FC<FirstTimeSetupProps> = ({
  isOpen,
  onComplete,
  onSkip
}) => {
  const [currentStep, setCurrentStep] = useState<Step>('welcome');
  const [apiKeys, setApiKeys] = useState<Record<string, string>>({});
  const [securityLevel, setSecurityLevel] = useState<'session' | 'persistent'>('session');
  const [validationResults, setValidationResults] = useState<Record<string, boolean>>({});
  const { setAPIKey, validateKey } = useAPIKeyManager();

  const steps: Step[] = ['welcome', 'security', 'input', 'validation', 'complete'];
  const currentStepIndex = steps.indexOf(currentStep);

  const handleNext = () => {
    const nextIndex = currentStepIndex + 1;
    if (nextIndex < steps.length) {
      setCurrentStep(steps[nextIndex]);
    }
  };

  const handlePrevious = () => {
    const prevIndex = currentStepIndex - 1;
    if (prevIndex >= 0) {
      setCurrentStep(steps[prevIndex]);
    }
  };

  const handleValidate = async () => {
    const results: Record<string, boolean> = {};
    
    for (const [service, key] of Object.entries(apiKeys)) {
      if (key.trim()) {
        try {
          const result = await validateKey(service as any, key);
          results[service] = result.valid;
        } catch (error) {
          results[service] = false;
        }
      }
    }
    
    setValidationResults(results);
    handleNext();
  };

  const handleComplete = async () => {
    // Save all valid API keys
    for (const [service, key] of Object.entries(apiKeys)) {
      if (key.trim() && validationResults[service]) {
        await setAPIKey(service as any, key, {
          securityLevel,
          autoExpiry: securityLevel === 'session' ? 480 : undefined // 8 hours for session
        });
      }
    }
    
    onComplete();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-2xl"
      >
        {/* Progress Bar */}
        <div className="p-6 border-b dark:border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              Setup VocabLens
            </h2>
            <span className="text-sm text-gray-500 dark:text-gray-400">
              {currentStepIndex + 1} of {steps.length}
            </span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${((currentStepIndex + 1) / steps.length) * 100}%` }}
            />
          </div>
        </div>

        {/* Step Content */}
        <div className="p-6">
          <AnimatePresence mode="wait">
            {currentStep === 'welcome' && (
              <WelcomeStep key="welcome" onNext={handleNext} onSkip={onSkip} />
            )}
            {currentStep === 'security' && (
              <SecurityStep
                key="security"
                securityLevel={securityLevel}
                onSecurityLevelChange={setSecurityLevel}
                onNext={handleNext}
                onPrevious={handlePrevious}
              />
            )}
            {currentStep === 'input' && (
              <InputStep
                key="input"
                apiKeys={apiKeys}
                onApiKeysChange={setApiKeys}
                onNext={handleValidate}
                onPrevious={handlePrevious}
              />
            )}
            {currentStep === 'validation' && (
              <ValidationStep
                key="validation"
                apiKeys={apiKeys}
                validationResults={validationResults}
                onNext={handleNext}
                onPrevious={handlePrevious}
              />
            )}
            {currentStep === 'complete' && (
              <CompleteStep
                key="complete"
                validationResults={validationResults}
                onComplete={handleComplete}
                onPrevious={handlePrevious}
              />
            )}
          </AnimatePresence>
        </div>
      </motion.div>
    </div>
  );
};

// Individual step components would be defined here...
// WelcomeStep, SecurityStep, InputStep, ValidationStep, CompleteStep
```

## Accessibility Features

### 1. Keyboard Navigation
- Tab order follows logical flow
- Escape key closes modals
- Arrow keys navigate between tabs
- Enter/Space activates buttons

### 2. Screen Reader Support
- Proper ARIA labels and descriptions
- Live regions for dynamic content
- Semantic HTML structure
- Form field associations

### 3. Visual Accessibility
- High contrast color schemes
- Focus indicators
- Error state colors meet WCAG guidelines
- Scalable text support

### 4. Responsive Design
- Mobile-first approach
- Touch-friendly interactive elements
- Collapsible sections on small screens
- Horizontal scroll for tables

## Error Handling

### 1. Validation Errors
- Real-time format validation
- Clear error messages
- Contextual help text
- Recovery suggestions

### 2. Network Errors
- Retry mechanisms
- Offline state handling
- Timeout management
- Fallback options

### 3. Security Errors
- Encryption failures
- Storage quota exceeded
- Invalid master passwords
- Permission denied

This comprehensive UI architecture ensures a secure, accessible, and user-friendly experience for managing API keys in VocabLens.