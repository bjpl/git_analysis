/**
 * First Time Setup Modal
 * Welcome screen for new users to configure API keys
 */

import React, { useState, useEffect } from 'react';
import { 
  X, 
  Key, 
  ExternalLink, 
  Check, 
  ChevronRight, 
  ChevronLeft, 
  AlertCircle,
  Loader2,
  Eye,
  EyeOff
} from 'lucide-react';
import { apiConfigService } from '../../services/apiConfigService';
import { API_PROVIDERS, ApiProviderName, SetupStep } from '../../types/api';

interface FirstTimeSetupProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete: () => void;
}

const SetupStep: React.FC<{
  step: SetupStep;
  isActive: boolean;
  isCompleted: boolean;
}> = ({ step, isActive, isCompleted }) => (
  <div className={`flex items-center space-x-3 p-3 rounded-lg transition-colors ${
    isActive ? 'bg-blue-50 dark:bg-blue-900/20' : ''
  }`}>
    <div className={`flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-sm font-medium ${
      isCompleted
        ? 'bg-green-100 text-green-600 dark:bg-green-900/20 dark:text-green-400'
        : isActive
          ? 'bg-blue-100 text-blue-600 dark:bg-blue-900/40 dark:text-blue-400'
          : 'bg-gray-100 text-gray-400 dark:bg-gray-700 dark:text-gray-500'
    }`}>
      {isCompleted ? <Check className="h-4 w-4" /> : step.id}
    </div>
    <div className="flex-1">
      <p className={`font-medium ${
        isActive ? 'text-gray-900 dark:text-gray-100' : 'text-gray-600 dark:text-gray-400'
      }`}>
        {step.title}
      </p>
      <p className="text-sm text-gray-500 dark:text-gray-500">
        {step.description}
      </p>
    </div>
  </div>
);

export const FirstTimeSetup: React.FC<FirstTimeSetupProps> = ({
  isOpen,
  onClose,
  onComplete
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [apiKeys, setApiKeys] = useState<{ [K in ApiProviderName]: string }>({
    unsplash: '',
    openai: ''
  });
  const [showKeys, setShowKeys] = useState<{ [K in ApiProviderName]: boolean }>({
    unsplash: false,
    openai: false
  });
  const [isValidating, setIsValidating] = useState(false);
  const [validationResults, setValidationResults] = useState<{ [K in ApiProviderName]?: boolean }>({});
  const [isSaving, setIsSaving] = useState(false);
  
  const steps: SetupStep[] = [
    {
      id: '1',
      title: 'Welcome to VocabLens',
      description: 'Let\'s set up your API keys to get started',
      isCompleted: false,
      isOptional: false
    },
    {
      id: '2',
      title: 'Configure Unsplash API',
      description: 'Get access to millions of high-quality images',
      isCompleted: false,
      isOptional: false
    },
    {
      id: '3',
      title: 'Configure OpenAI API',
      description: 'Enable AI-powered image descriptions',
      isCompleted: false,
      isOptional: true
    },
    {
      id: '4',
      title: 'Complete Setup',
      description: 'Review and save your configuration',
      isCompleted: false,
      isOptional: false
    }
  ];

  const [setupSteps, setSetupSteps] = useState(steps);

  useEffect(() => {
    // Update step completion status based on API key configuration
    const updatedSteps = setupSteps.map((step, index) => {
      if (index === 1) { // Unsplash step
        return { ...step, isCompleted: Boolean(validationResults.unsplash) };
      }
      if (index === 2) { // OpenAI step
        return { ...step, isCompleted: Boolean(validationResults.openai) };
      }
      return step;
    });
    setSetupSteps(updatedSteps);
  }, [validationResults]);

  const handleApiKeyChange = (provider: ApiProviderName, value: string) => {
    setApiKeys(prev => ({ ...prev, [provider]: value }));
    // Clear validation when key changes
    setValidationResults(prev => ({ ...prev, [provider]: undefined }));
  };

  const validateApiKey = async (provider: ApiProviderName) => {
    const key = apiKeys[provider].trim();
    if (!key) return;

    setIsValidating(true);
    try {
      const result = await apiConfigService.validateApiKey(provider, key);
      setValidationResults(prev => ({ ...prev, [provider]: result.isValid }));
    } catch (error) {
      setValidationResults(prev => ({ ...prev, [provider]: false }));
    } finally {
      setIsValidating(false);
    }
  };

  const handleNext = () => {
    if (currentStep < setupSteps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const canProceed = () => {
    switch (currentStep) {
      case 0: // Welcome
        return true;
      case 1: // Unsplash
        return validationResults.unsplash === true;
      case 2: // OpenAI
        return true; // Optional step
      case 3: // Complete
        return validationResults.unsplash === true;
      default:
        return false;
    }
  };

  const completeSetup = async () => {
    setIsSaving(true);
    try {
      // Save configured API keys
      for (const [provider, key] of Object.entries(apiKeys)) {
        if (key.trim()) {
          await apiConfigService.setApiKey(provider as ApiProviderName, key.trim());
        }
      }
      
      onComplete();
      onClose();
    } catch (error) {
      console.error('Failed to save API configuration:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const skipSetup = () => {
    // User can skip, but they'll be prompted again later
    onClose();
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 0: // Welcome
        return (
          <div className="text-center py-8">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Key className="h-8 w-8 text-blue-600" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">
              Welcome to VocabLens
            </h3>
            <p className="text-gray-600 dark:text-gray-400 max-w-md mx-auto mb-6">
              To get started, you'll need to configure API keys for the services that power VocabLens. 
              This takes just a few minutes and enables all the amazing features.
            </p>
            <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4 max-w-md mx-auto">
              <div className="flex items-start space-x-2">
                <AlertCircle className="h-5 w-5 text-yellow-600 dark:text-yellow-400 flex-shrink-0" />
                <div className="text-sm text-yellow-800 dark:text-yellow-200">
                  <p className="font-medium">Your keys are secure</p>
                  <p>API keys are encrypted and stored only in your browser.</p>
                </div>
              </div>
            </div>
          </div>
        );

      case 1: // Unsplash
        return (
          <div className="py-6">
            <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">
              Configure Unsplash API
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Unsplash provides access to millions of high-quality, free-to-use images. 
              This API is required for VocabLens to function.
            </p>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Unsplash Access Key
                </label>
                <div className="relative">
                  <input
                    type={showKeys.unsplash ? 'text' : 'password'}
                    value={apiKeys.unsplash}
                    onChange={(e) => handleApiKeyChange('unsplash', e.target.value)}
                    placeholder="Enter your Unsplash Access Key"
                    className="w-full px-3 py-2 pr-12 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
                  />
                  <button
                    type="button"
                    onClick={() => setShowKeys(prev => ({ ...prev, unsplash: !prev.unsplash }))}
                    className="absolute right-3 top-2.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                  >
                    {showKeys.unsplash ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <button
                  onClick={() => validateApiKey('unsplash')}
                  disabled={!apiKeys.unsplash.trim() || isValidating}
                  className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                >
                  {isValidating ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin mr-2" />
                      Testing...
                    </>
                  ) : (
                    'Test Connection'
                  )}
                </button>
                
                {validationResults.unsplash !== undefined && (
                  <div className={`flex items-center space-x-1 text-sm ${
                    validationResults.unsplash ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {validationResults.unsplash ? <Check className="h-4 w-4" /> : <X className="h-4 w-4" />}
                    <span>{validationResults.unsplash ? 'Valid API key' : 'Invalid API key'}</span>
                  </div>
                )}
              </div>

              <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">
                  How to get your Unsplash API key:
                </h4>
                <ol className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                  <li>1. Visit the Unsplash Developer portal</li>
                  <li>2. Create a free account or sign in</li>
                  <li>3. Create a new application</li>
                  <li>4. Copy your Access Key</li>
                </ol>
                <a
                  href={API_PROVIDERS.unsplash.getApiKeyUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center mt-3 text-blue-600 hover:text-blue-700 text-sm font-medium"
                >
                  Open Unsplash Developers
                  <ExternalLink className="ml-1 h-3 w-3" />
                </a>
              </div>
            </div>
          </div>
        );

      case 2: // OpenAI
        return (
          <div className="py-6">
            <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">
              Configure OpenAI API (Optional)
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              OpenAI enables AI-powered image descriptions and enhanced search capabilities. 
              This is optional but highly recommended for the best experience.
            </p>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  OpenAI API Key
                </label>
                <div className="relative">
                  <input
                    type={showKeys.openai ? 'text' : 'password'}
                    value={apiKeys.openai}
                    onChange={(e) => handleApiKeyChange('openai', e.target.value)}
                    placeholder="Enter your OpenAI API Key (sk-...)"
                    className="w-full px-3 py-2 pr-12 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
                  />
                  <button
                    type="button"
                    onClick={() => setShowKeys(prev => ({ ...prev, openai: !prev.openai }))}
                    className="absolute right-3 top-2.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                  >
                    {showKeys.openai ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <button
                  onClick={() => validateApiKey('openai')}
                  disabled={!apiKeys.openai.trim() || isValidating}
                  className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                >
                  {isValidating ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin mr-2" />
                      Testing...
                    </>
                  ) : (
                    'Test Connection'
                  )}
                </button>
                
                {validationResults.openai !== undefined && (
                  <div className={`flex items-center space-x-1 text-sm ${
                    validationResults.openai ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {validationResults.openai ? <Check className="h-4 w-4" /> : <X className="h-4 w-4" />}
                    <span>{validationResults.openai ? 'Valid API key' : 'Invalid API key'}</span>
                  </div>
                )}
                
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  or skip this step
                </span>
              </div>

              <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">
                  How to get your OpenAI API key:
                </h4>
                <ol className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                  <li>1. Visit OpenAI Platform</li>
                  <li>2. Create an account or sign in</li>
                  <li>3. Go to API Keys section</li>
                  <li>4. Create a new secret key</li>
                  <li>5. Add billing information (required for API usage)</li>
                </ol>
                <a
                  href={API_PROVIDERS.openai.getApiKeyUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center mt-3 text-blue-600 hover:text-blue-700 text-sm font-medium"
                >
                  Open OpenAI Platform
                  <ExternalLink className="ml-1 h-3 w-3" />
                </a>
              </div>
            </div>
          </div>
        );

      case 3: // Complete
        return (
          <div className="text-center py-8">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Check className="h-8 w-8 text-green-600" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">
              Setup Complete!
            </h3>
            <p className="text-gray-600 dark:text-gray-400 max-w-md mx-auto mb-6">
              Your API keys have been configured and validated. You're ready to start using VocabLens!
            </p>
            
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 max-w-md mx-auto">
              <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-2">
                What's configured:
              </h4>
              <ul className="text-sm text-blue-800 dark:text-blue-200 space-y-1">
                <li className="flex items-center space-x-2">
                  <Check className="h-4 w-4" />
                  <span>Unsplash API - Image search</span>
                </li>
                {validationResults.openai && (
                  <li className="flex items-center space-x-2">
                    <Check className="h-4 w-4" />
                    <span>OpenAI API - AI descriptions</span>
                  </li>
                )}
              </ul>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center">
        <div className="fixed inset-0 transition-opacity" onClick={skipSetup}>
          <div className="absolute inset-0 bg-gray-500 dark:bg-gray-900 opacity-75" />
        </div>

        <div className="relative bg-white dark:bg-gray-800 rounded-lg max-w-4xl w-full shadow-xl">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
              VocabLens Setup
            </h2>
            <button
              onClick={skipSetup}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          <div className="flex">
            {/* Sidebar with steps */}
            <div className="w-1/3 p-6 bg-gray-50 dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
                Setup Progress
              </h3>
              <div className="space-y-3">
                {setupSteps.map((step, index) => (
                  <SetupStep
                    key={step.id}
                    step={step}
                    isActive={currentStep === index}
                    isCompleted={step.isCompleted}
                  />
                ))}
              </div>
            </div>

            {/* Main content */}
            <div className="flex-1 p-6">
              <div className="min-h-96">
                {renderStepContent()}
              </div>

              {/* Navigation */}
              <div className="flex items-center justify-between pt-6 border-t border-gray-200 dark:border-gray-700">
                <div>
                  {currentStep > 0 && (
                    <button
                      onClick={handlePrevious}
                      className="inline-flex items-center px-4 py-2 text-sm text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200"
                    >
                      <ChevronLeft className="h-4 w-4 mr-1" />
                      Previous
                    </button>
                  )}
                </div>
                
                <div className="flex space-x-3">
                  <button
                    onClick={skipSetup}
                    className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200"
                  >
                    Skip Setup
                  </button>
                  
                  {currentStep < setupSteps.length - 1 ? (
                    <button
                      onClick={handleNext}
                      disabled={!canProceed()}
                      className="inline-flex items-center px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Continue
                      <ChevronRight className="h-4 w-4 ml-1" />
                    </button>
                  ) : (
                    <button
                      onClick={completeSetup}
                      disabled={!canProceed() || isSaving}
                      className="inline-flex items-center px-4 py-2 text-sm bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isSaving ? (
                        <>
                          <Loader2 className="h-4 w-4 animate-spin mr-2" />
                          Completing...
                        </>
                      ) : (
                        'Complete Setup'
                      )}
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};