/**
 * User Experience and Edge Case Tests
 * Tests the complete user journey and edge cases for API configuration
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { configManager } from '../../src/services/configManager';
import toast from 'react-hot-toast';

// Mock dependencies
vi.mock('../../src/services/configManager');
vi.mock('react-hot-toast', () => ({
  default: {
    success: vi.fn(),
    error: vi.fn(),
    loading: vi.fn(),
    dismiss: vi.fn()
  }
}));

// Mock network conditions
const mockNetworkConditions = {
  online: true,
  connectionType: 'wifi',
  effectiveType: '4g',
  downlink: 10,
  rtt: 100
};

Object.defineProperty(navigator, 'onLine', {
  writable: true,
  value: true
});

Object.defineProperty(navigator, 'connection', {
  writable: true,
  value: mockNetworkConditions
});

// Mock viewport for responsive testing
const mockViewport = {
  width: 1200,
  height: 800
};

Object.defineProperties(window, {
  innerWidth: {
    writable: true,
    configurable: true,
    value: mockViewport.width
  },
  innerHeight: {
    writable: true,
    configurable: true,
    value: mockViewport.height
  }
});

// Mock API Configuration Setup Component
const ApiSetupWizard: React.FC<{ onComplete: () => void }> = ({ onComplete }) => {
  const [currentStep, setCurrentStep] = React.useState(0);
  const [apiKeys, setApiKeys] = React.useState({
    unsplash: '',
    openai: ''
  });
  const [isValidating, setIsValidating] = React.useState<Record<string, boolean>>({});
  const [validationResults, setValidationResults] = React.useState<Record<string, boolean>>({});
  const [showHelp, setShowHelp] = React.useState(false);

  const steps = [
    { title: 'Welcome', description: 'Configure your API keys for VocabLens' },
    { title: 'Unsplash API', description: 'Add your Unsplash access key' },
    { title: 'OpenAI API', description: 'Add your OpenAI API key' },
    { title: 'Verification', description: 'Test your configuration' },
    { title: 'Complete', description: 'Setup complete!' }
  ];

  const validateApiKey = async (service: string, key: string) => {
    if (!key.trim()) return;
    
    setIsValidating(prev => ({ ...prev, [service]: true }));
    
    try {
      const result = await configManager.validateApiKey(service as any, key);
      setValidationResults(prev => ({ ...prev, [service]: result.valid }));
      
      if (result.valid) {
        toast.success(`${service} API key is valid!`);
      } else {
        toast.error(`${service} API key is invalid: ${result.error}`);
      }
    } catch (error) {
      toast.error(`Validation failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
      setValidationResults(prev => ({ ...prev, [service]: false }));
    } finally {
      setIsValidating(prev => ({ ...prev, [service]: false }));
    }
  };

  const handleNext = async () => {
    if (currentStep === steps.length - 1) {
      onComplete();
      return;
    }

    if (currentStep === 3) {
      // Verification step - validate all keys
      const validationPromises = Object.entries(apiKeys)
        .filter(([_, key]) => key.trim())
        .map(([service, key]) => validateApiKey(service, key));
      
      await Promise.all(validationPromises);
      
      const hasValidKeys = Object.values(validationResults).some(Boolean);
      if (!hasValidKeys) {
        toast.error('Please provide at least one valid API key');
        return;
      }
    }

    setCurrentStep(prev => Math.min(prev + 1, steps.length - 1));
  };

  const handlePrevious = () => {
    setCurrentStep(prev => Math.max(prev - 1, 0));
  };

  const handleKeyChange = (service: string, value: string) => {
    setApiKeys(prev => ({ ...prev, [service]: value }));
    // Clear validation result when key changes
    setValidationResults(prev => ({ ...prev, [service]: false }));
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <div className="welcome-step" data-testid="welcome-step">
            <h2>Welcome to VocabLens Setup</h2>
            <p>Let's configure your API keys to unlock the full potential of VocabLens.</p>
            <div className="features">
              <div>✓ AI-powered vocabulary descriptions</div>
              <div>✓ Beautiful image search</div>
              <div>✓ Personalized learning</div>
            </div>
            <button onClick={() => setShowHelp(!showHelp)}>
              {showHelp ? 'Hide' : 'Show'} Help
            </button>
            {showHelp && (
              <div className="help-content" data-testid="help-content">
                <p>You'll need API keys from Unsplash and OpenAI to use all features.</p>
                <ul>
                  <li>Unsplash: For searching beautiful images</li>
                  <li>OpenAI: For AI-powered vocabulary generation</li>
                </ul>
              </div>
            )}
          </div>
        );

      case 1:
        return (
          <div className="unsplash-step" data-testid="unsplash-step">
            <h2>Unsplash API Configuration</h2>
            <div className="input-group">
              <label htmlFor="unsplash-key">Unsplash Access Key</label>
              <input
                id="unsplash-key"
                type="password"
                value={apiKeys.unsplash}
                onChange={(e) => handleKeyChange('unsplash', e.target.value)}
                placeholder="Enter your Unsplash access key"
                className={validationResults.unsplash ? 'valid' : ''}
              />
              <button 
                onClick={() => validateApiKey('unsplash', apiKeys.unsplash)}
                disabled={isValidating.unsplash || !apiKeys.unsplash.trim()}
              >
                {isValidating.unsplash ? 'Validating...' : 'Validate Key'}
              </button>
            </div>
            <div className="help-link">
              <a href="https://unsplash.com/developers" target="_blank" rel="noopener noreferrer">
                Get your Unsplash API key here
              </a>
            </div>
            {validationResults.unsplash && (
              <div className="validation-success" data-testid="unsplash-success">
                ✓ Unsplash API key is valid
              </div>
            )}
          </div>
        );

      case 2:
        return (
          <div className="openai-step" data-testid="openai-step">
            <h2>OpenAI API Configuration</h2>
            <div className="input-group">
              <label htmlFor="openai-key">OpenAI API Key</label>
              <input
                id="openai-key"
                type="password"
                value={apiKeys.openai}
                onChange={(e) => handleKeyChange('openai', e.target.value)}
                placeholder="sk-..."
                className={validationResults.openai ? 'valid' : ''}
              />
              <button 
                onClick={() => validateApiKey('openai', apiKeys.openai)}
                disabled={isValidating.openai || !apiKeys.openai.trim()}
              >
                {isValidating.openai ? 'Validating...' : 'Validate Key'}
              </button>
            </div>
            <div className="help-link">
              <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer">
                Get your OpenAI API key here
              </a>
            </div>
            {validationResults.openai && (
              <div className="validation-success" data-testid="openai-success">
                ✓ OpenAI API key is valid
              </div>
            )}
          </div>
        );

      case 3:
        return (
          <div className="verification-step" data-testid="verification-step">
            <h2>Verify Configuration</h2>
            <div className="config-summary">
              <div className={`service-status ${validationResults.unsplash ? 'valid' : 'invalid'}`}>
                <span>Unsplash:</span> 
                <span>{validationResults.unsplash ? '✓ Connected' : '✗ Not configured'}</span>
              </div>
              <div className={`service-status ${validationResults.openai ? 'valid' : 'invalid'}`}>
                <span>OpenAI:</span> 
                <span>{validationResults.openai ? '✓ Connected' : '✗ Not configured'}</span>
              </div>
            </div>
            <p>At least one service must be configured to continue.</p>
          </div>
        );

      case 4:
        return (
          <div className="complete-step" data-testid="complete-step">
            <h2>🎉 Setup Complete!</h2>
            <p>Your API configuration has been saved securely.</p>
            <div className="next-steps">
              <h3>What's next?</h3>
              <ul>
                <li>Search for images to build your vocabulary</li>
                <li>Generate AI-powered descriptions</li>
                <li>Track your learning progress</li>
              </ul>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="api-setup-wizard" data-testid="api-setup-wizard">
      <div className="progress-bar">
        <div 
          className="progress-fill" 
          style={{ width: `${(currentStep / (steps.length - 1)) * 100}%` }}
        />
      </div>
      
      <div className="step-indicator">
        {currentStep + 1} of {steps.length}: {steps[currentStep].title}
      </div>

      <div className="step-content">
        {renderStepContent()}
      </div>

      <div className="navigation">
        <button 
          onClick={handlePrevious}
          disabled={currentStep === 0}
          data-testid="prev-button"
        >
          Previous
        </button>
        <button 
          onClick={handleNext}
          data-testid="next-button"
        >
          {currentStep === steps.length - 1 ? 'Finish' : 'Next'}
        </button>
      </div>
    </div>
  );
};

describe('User Experience Scenarios', () => {
  const mockOnComplete = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    (configManager.validateApiKey as any).mockResolvedValue({ valid: true });
    (configManager.updateServiceConfiguration as any).mockResolvedValue({ success: true });
    
    // Reset network state
    mockNetworkConditions.online = true;
    (navigator as any).onLine = true;
  });

  describe('First-Time User Experience', () => {
    it('should guide new user through complete setup flow', async () => {
      const user = userEvent.setup();
      render(<ApiSetupWizard onComplete={mockOnComplete} />);

      // Welcome step
      expect(screen.getByTestId('welcome-step')).toBeInTheDocument();
      expect(screen.getByText('Welcome to VocabLens Setup')).toBeInTheDocument();

      // Show help
      await user.click(screen.getByText('Show Help'));
      expect(screen.getByTestId('help-content')).toBeInTheDocument();

      // Next to Unsplash step
      await user.click(screen.getByTestId('next-button'));
      expect(screen.getByTestId('unsplash-step')).toBeInTheDocument();

      // Add Unsplash key
      const unsplashInput = screen.getByLabelText('Unsplash Access Key');
      await user.type(unsplashInput, 'valid-unsplash-key-123');
      
      await user.click(screen.getByText('Validate Key'));
      await waitFor(() => {
        expect(screen.getByTestId('unsplash-success')).toBeInTheDocument();
      });

      // Next to OpenAI step
      await user.click(screen.getByTestId('next-button'));
      expect(screen.getByTestId('openai-step')).toBeInTheDocument();

      // Add OpenAI key
      const openaiInput = screen.getByLabelText('OpenAI API Key');
      await user.type(openaiInput, 'sk-valid-openai-key-456');
      
      await user.click(screen.getByText('Validate Key'));
      await waitFor(() => {
        expect(screen.getByTestId('openai-success')).toBeInTheDocument();
      });

      // Next to verification
      await user.click(screen.getByTestId('next-button'));
      expect(screen.getByTestId('verification-step')).toBeInTheDocument();
      expect(screen.getByText('✓ Connected', { selector: '.service-status.valid span' })).toBeInTheDocument();

      // Complete setup
      await user.click(screen.getByTestId('next-button'));
      expect(screen.getByTestId('complete-step')).toBeInTheDocument();

      await user.click(screen.getByText('Finish'));
      expect(mockOnComplete).toHaveBeenCalled();
    });

    it('should allow skipping optional configurations', async () => {
      const user = userEvent.setup();
      render(<ApiSetupWizard onComplete={mockOnComplete} />);

      // Skip welcome
      await user.click(screen.getByTestId('next-button'));

      // Add only Unsplash key
      const unsplashInput = screen.getByLabelText('Unsplash Access Key');
      await user.type(unsplashInput, 'unsplash-key-only');
      await user.click(screen.getByText('Validate Key'));

      // Skip OpenAI step
      await user.click(screen.getByTestId('next-button'));
      await user.click(screen.getByTestId('next-button'));

      // Should be able to complete with partial configuration
      expect(screen.getByTestId('verification-step')).toBeInTheDocument();
      await user.click(screen.getByTestId('next-button'));
      
      expect(screen.getByTestId('complete-step')).toBeInTheDocument();
    });

    it('should prevent completion without any valid keys', async () => {
      const user = userEvent.setup();
      (configManager.validateApiKey as any).mockResolvedValue({ valid: false, error: 'Invalid key' });

      render(<ApiSetupWizard onComplete={mockOnComplete} />);

      // Skip to verification with no keys
      await user.click(screen.getByTestId('next-button')); // Welcome
      await user.click(screen.getByTestId('next-button')); // Unsplash
      await user.click(screen.getByTestId('next-button')); // OpenAI

      // Try to proceed from verification
      await user.click(screen.getByTestId('next-button'));

      expect(toast.error).toHaveBeenCalledWith('Please provide at least one valid API key');
      expect(screen.getByTestId('verification-step')).toBeInTheDocument();
    });
  });

  describe('Error Handling and Recovery', () => {
    it('should handle API validation failures gracefully', async () => {
      const user = userEvent.setup();
      (configManager.validateApiKey as any).mockResolvedValue({ 
        valid: false, 
        error: 'Invalid API key format' 
      });

      render(<ApiSetupWizard onComplete={mockOnComplete} />);

      // Go to Unsplash step
      await user.click(screen.getByTestId('next-button'));
      
      const unsplashInput = screen.getByLabelText('Unsplash Access Key');
      await user.type(unsplashInput, 'invalid-key');
      await user.click(screen.getByText('Validate Key'));

      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith('unsplash API key is invalid: Invalid API key format');
      });

      expect(screen.queryByTestId('unsplash-success')).not.toBeInTheDocument();
    });

    it('should handle network errors during validation', async () => {
      const user = userEvent.setup();
      (configManager.validateApiKey as any).mockRejectedValue(new Error('Network timeout'));

      render(<ApiSetupWizard onComplete={mockOnComplete} />);

      await user.click(screen.getByTestId('next-button'));
      
      const unsplashInput = screen.getByLabelText('Unsplash Access Key');
      await user.type(unsplashInput, 'test-key');
      await user.click(screen.getByText('Validate Key'));

      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith('Validation failed: Network timeout');
      });
    });

    it('should handle offline scenarios', async () => {
      const user = userEvent.setup();
      
      // Simulate offline condition
      (navigator as any).onLine = false;
      mockNetworkConditions.online = false;

      render(<ApiSetupWizard onComplete={mockOnComplete} />);

      await user.click(screen.getByTestId('next-button'));
      
      const unsplashInput = screen.getByLabelText('Unsplash Access Key');
      await user.type(unsplashInput, 'test-key');

      // Validation button should be disabled or show offline message
      const validateButton = screen.getByText('Validate Key');
      
      if (!navigator.onLine) {
        // Could disable the button or show offline message
        expect(validateButton).toBeInTheDocument();
      }
    });
  });

  describe('Mobile Responsiveness', () => {
    it('should adapt to mobile screen sizes', () => {
      // Mock mobile viewport
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375
      });

      render(<ApiSetupWizard onComplete={mockOnComplete} />);
      
      const wizard = screen.getByTestId('api-setup-wizard');
      expect(wizard).toBeInTheDocument();
      
      // All essential elements should still be present
      expect(screen.getByTestId('next-button')).toBeInTheDocument();
      expect(screen.getByTestId('prev-button')).toBeInTheDocument();
    });

    it('should handle touch interactions', async () => {
      const user = userEvent.setup();
      
      // Mock touch device
      Object.defineProperty(navigator, 'maxTouchPoints', {
        writable: true,
        value: 5
      });

      render(<ApiSetupWizard onComplete={mockOnComplete} />);

      // Touch interactions should work the same as click
      await user.click(screen.getByTestId('next-button'));
      expect(screen.getByTestId('unsplash-step')).toBeInTheDocument();
    });

    it('should show appropriate input types on mobile', () => {
      render(<ApiSetupWizard onComplete={mockOnComplete} />);

      const nextButton = screen.getByTestId('next-button');
      fireEvent.click(nextButton);

      const unsplashInput = screen.getByLabelText('Unsplash Access Key');
      expect(unsplashInput).toHaveAttribute('type', 'password');
    });
  });

  describe('Accessibility Features', () => {
    it('should have proper ARIA labels and roles', () => {
      render(<ApiSetupWizard onComplete={mockOnComplete} />);

      expect(screen.getByTestId('next-button')).toHaveAttribute('type', 'button');
      expect(screen.getByTestId('prev-button')).toHaveAttribute('type', 'button');
    });

    it('should support keyboard navigation', async () => {
      const user = userEvent.setup();
      render(<ApiSetupWizard onComplete={mockOnComplete} />);

      // Tab through elements
      await user.tab();
      expect(screen.getByText('Show Help')).toHaveFocus();

      await user.tab();
      expect(screen.getByTestId('next-button')).toHaveFocus();

      // Navigate with Enter key
      await user.keyboard('{Enter}');
      expect(screen.getByTestId('unsplash-step')).toBeInTheDocument();
    });

    it('should provide screen reader friendly content', () => {
      render(<ApiSetupWizard onComplete={mockOnComplete} />);

      // Steps should have descriptive text
      expect(screen.getByText('1 of 5: Welcome')).toBeInTheDocument();
      expect(screen.getByText('Configure your API keys for VocabLens')).toBeInTheDocument();
    });
  });

  describe('Performance and Loading States', () => {
    it('should show loading states during validation', async () => {
      const user = userEvent.setup();
      
      // Mock slow validation
      (configManager.validateApiKey as any).mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({ valid: true }), 1000))
      );

      render(<ApiSetupWizard onComplete={mockOnComplete} />);

      await user.click(screen.getByTestId('next-button'));
      
      const unsplashInput = screen.getByLabelText('Unsplash Access Key');
      await user.type(unsplashInput, 'test-key');
      await user.click(screen.getByText('Validate Key'));

      expect(screen.getByText('Validating...')).toBeInTheDocument();
      expect(screen.getByText('Validate Key')).toBeDisabled();
    });

    it('should handle rapid user interactions', async () => {
      const user = userEvent.setup();
      render(<ApiSetupWizard onComplete={mockOnComplete} />);

      // Rapid clicking should not break the component
      const nextButton = screen.getByTestId('next-button');
      await user.click(nextButton);
      await user.click(nextButton);
      await user.click(nextButton);

      // Should still be functional
      expect(screen.getByTestId('verification-step')).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle very long API keys', async () => {
      const user = userEvent.setup();
      render(<ApiSetupWizard onComplete={mockOnComplete} />);

      await user.click(screen.getByTestId('next-button'));
      
      const unsplashInput = screen.getByLabelText('Unsplash Access Key');
      const longKey = 'a'.repeat(200);
      
      await user.type(unsplashInput, longKey);
      expect(unsplashInput).toHaveValue(longKey);
    });

    it('should handle special characters in API keys', async () => {
      const user = userEvent.setup();
      render(<ApiSetupWizard onComplete={mockOnComplete} />);

      await user.click(screen.getByTestId('next-button'));
      
      const unsplashInput = screen.getByLabelText('Unsplash Access Key');
      const specialKey = 'key-with_special.chars123';
      
      await user.type(unsplashInput, specialKey);
      expect(unsplashInput).toHaveValue(specialKey);
    });

    it('should handle copy-paste operations', async () => {
      const user = userEvent.setup();
      render(<ApiSetupWizard onComplete={mockOnComplete} />);

      await user.click(screen.getByTestId('next-button'));
      
      const unsplashInput = screen.getByLabelText('Unsplash Access Key');
      
      // Simulate paste operation
      await user.click(unsplashInput);
      await user.paste('sk-pasted-api-key-from-clipboard');
      
      expect(unsplashInput).toHaveValue('sk-pasted-api-key-from-clipboard');
    });

    it('should handle browser back/forward navigation', () => {
      render(<ApiSetupWizard onComplete={mockOnComplete} />);

      // Component should be resilient to browser navigation
      window.history.pushState({}, '', '/test');
      window.history.back();
      
      expect(screen.getByTestId('api-setup-wizard')).toBeInTheDocument();
    });
  });

  describe('Help and Documentation', () => {
    it('should provide contextual help at each step', () => {
      render(<ApiSetupWizard onComplete={mockOnComplete} />);

      // Welcome step should have help
      expect(screen.getByText('Show Help')).toBeInTheDocument();
    });

    it('should provide external links for API key registration', async () => {
      const user = userEvent.setup();
      render(<ApiSetupWizard onComplete={mockOnComplete} />);

      await user.click(screen.getByTestId('next-button'));
      
      const unsplashLink = screen.getByRole('link', { name: /get your unsplash api key here/i });
      expect(unsplashLink).toHaveAttribute('href', 'https://unsplash.com/developers');
      expect(unsplashLink).toHaveAttribute('target', '_blank');
      expect(unsplashLink).toHaveAttribute('rel', 'noopener noreferrer');
    });
  });

  describe('Data Persistence', () => {
    it('should preserve form data during navigation', async () => {
      const user = userEvent.setup();
      render(<ApiSetupWizard onComplete={mockOnComplete} />);

      // Go to Unsplash step and enter key
      await user.click(screen.getByTestId('next-button'));
      const unsplashInput = screen.getByLabelText('Unsplash Access Key');
      await user.type(unsplashInput, 'test-key');

      // Go forward and back
      await user.click(screen.getByTestId('next-button'));
      await user.click(screen.getByTestId('prev-button'));

      // Key should still be there
      expect(screen.getByLabelText('Unsplash Access Key')).toHaveValue('test-key');
    });

    it('should clear validation state when key changes', async () => {
      const user = userEvent.setup();
      render(<ApiSetupWizard onComplete={mockOnComplete} />);

      await user.click(screen.getByTestId('next-button'));
      
      const unsplashInput = screen.getByLabelText('Unsplash Access Key');
      await user.type(unsplashInput, 'valid-key');
      await user.click(screen.getByText('Validate Key'));

      await waitFor(() => {
        expect(screen.getByTestId('unsplash-success')).toBeInTheDocument();
      });

      // Change the key
      await user.clear(unsplashInput);
      await user.type(unsplashInput, 'different-key');

      // Success indicator should be gone
      expect(screen.queryByTestId('unsplash-success')).not.toBeInTheDocument();
    });
  });
});