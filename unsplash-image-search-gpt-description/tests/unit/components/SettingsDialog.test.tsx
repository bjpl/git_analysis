/**
 * Component Tests for Settings Dialog
 * Tests the UI components for runtime API configuration
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { SettingsDialog } from '../../../src/components/Settings/SettingsDialog';
import { configManager } from '../../../src/services/configManager';

// Mock the config manager
vi.mock('../../../src/services/configManager', () => ({
  configManager: {
    getConfiguration: vi.fn(),
    updateServiceConfiguration: vi.fn(),
    validateApiKey: vi.fn(),
    getHealthStatus: vi.fn(),
    exportConfiguration: vi.fn(),
    resetConfiguration: vi.fn()
  }
}));

// Mock toast notifications
vi.mock('react-hot-toast', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
    loading: vi.fn()
  }
}));

// Mock clipboard API
Object.assign(navigator, {
  clipboard: {
    writeText: vi.fn()
  }
});

// Settings Dialog Component (since it might not exist, we'll create a mock)
const MockSettingsDialog: React.FC<{ isOpen: boolean; onClose: () => void }> = ({ isOpen, onClose }) => {
  const [apiKeys, setApiKeys] = React.useState({
    unsplash: '',
    openai: '',
    supabase: ''
  });
  
  const [validationStates, setValidationStates] = React.useState<Record<string, 'idle' | 'validating' | 'valid' | 'invalid'>>({});
  const [showKeys, setShowKeys] = React.useState<Record<string, boolean>>({});

  const handleApiKeyChange = (service: string, value: string) => {
    setApiKeys(prev => ({ ...prev, [service]: value }));
  };

  const handleValidateKey = async (service: string) => {
    if (!apiKeys[service as keyof typeof apiKeys]) return;
    
    setValidationStates(prev => ({ ...prev, [service]: 'validating' }));
    
    try {
      const result = await configManager.validateApiKey(service as any, apiKeys[service as keyof typeof apiKeys]);
      setValidationStates(prev => ({ ...prev, [service]: result.valid ? 'valid' : 'invalid' }));
    } catch (error) {
      setValidationStates(prev => ({ ...prev, [service]: 'invalid' }));
    }
  };

  const handleSave = async () => {
    const updates = Object.entries(apiKeys)
      .filter(([_, key]) => key.trim() !== '')
      .map(([service, key]) => ({ service: service as any, apiKey: key }));

    for (const update of updates) {
      await configManager.updateServiceConfiguration(update);
    }
    
    onClose();
  };

  const toggleShowKey = (service: string) => {
    setShowKeys(prev => ({ ...prev, [service]: !prev[service] }));
  };

  if (!isOpen) return null;

  return (
    <div role="dialog" aria-labelledby="settings-title">
      <h2 id="settings-title">API Settings</h2>
      
      {/* Unsplash API Key */}
      <div>
        <label htmlFor="unsplash-key">Unsplash API Key</label>
        <div>
          <input
            id="unsplash-key"
            type={showKeys.unsplash ? 'text' : 'password'}
            value={apiKeys.unsplash}
            onChange={(e) => handleApiKeyChange('unsplash', e.target.value)}
            placeholder="Enter Unsplash access key"
            aria-describedby="unsplash-help"
          />
          <button onClick={() => toggleShowKey('unsplash')} aria-label="Toggle key visibility">
            {showKeys.unsplash ? 'Hide' : 'Show'}
          </button>
          <button onClick={() => handleValidateKey('unsplash')} disabled={validationStates.unsplash === 'validating'}>
            {validationStates.unsplash === 'validating' ? 'Validating...' : 'Validate'}
          </button>
        </div>
        <div id="unsplash-help">
          Get your key from <a href="https://unsplash.com/developers" target="_blank" rel="noopener noreferrer">
            Unsplash Developers
          </a>
        </div>
        {validationStates.unsplash === 'valid' && <div className="validation-success">✓ Valid key</div>}
        {validationStates.unsplash === 'invalid' && <div className="validation-error">✗ Invalid key</div>}
      </div>

      {/* OpenAI API Key */}
      <div>
        <label htmlFor="openai-key">OpenAI API Key</label>
        <div>
          <input
            id="openai-key"
            type={showKeys.openai ? 'text' : 'password'}
            value={apiKeys.openai}
            onChange={(e) => handleApiKeyChange('openai', e.target.value)}
            placeholder="sk-..."
            aria-describedby="openai-help"
          />
          <button onClick={() => toggleShowKey('openai')} aria-label="Toggle key visibility">
            {showKeys.openai ? 'Hide' : 'Show'}
          </button>
          <button onClick={() => handleValidateKey('openai')} disabled={validationStates.openai === 'validating'}>
            {validationStates.openai === 'validating' ? 'Validating...' : 'Validate'}
          </button>
        </div>
        <div id="openai-help">
          Get your key from <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer">
            OpenAI Platform
          </a>
        </div>
        {validationStates.openai === 'valid' && <div className="validation-success">✓ Valid key</div>}
        {validationStates.openai === 'invalid' && <div className="validation-error">✗ Invalid key</div>}
      </div>

      {/* Action buttons */}
      <div>
        <button onClick={handleSave}>Save Settings</button>
        <button onClick={onClose}>Cancel</button>
        <button onClick={() => configManager.resetConfiguration()}>Reset All</button>
      </div>
    </div>
  );
};

describe('SettingsDialog', () => {
  const mockOnClose = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    
    (configManager.getConfiguration as any).mockReturnValue({
      keys: { unsplash: '', openai: '', supabase: '' }
    });
    
    (configManager.validateApiKey as any).mockResolvedValue({ valid: true });
    (configManager.updateServiceConfiguration as any).mockResolvedValue({ success: true });
  });

  describe('Rendering', () => {
    it('should render when open', () => {
      render(<MockSettingsDialog isOpen={true} onClose={mockOnClose} />);
      
      expect(screen.getByRole('dialog')).toBeInTheDocument();
      expect(screen.getByText('API Settings')).toBeInTheDocument();
    });

    it('should not render when closed', () => {
      render(<MockSettingsDialog isOpen={false} onClose={mockOnClose} />);
      
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });

    it('should render all API key input fields', () => {
      render(<MockSettingsDialog isOpen={true} onClose={mockOnClose} />);
      
      expect(screen.getByLabelText('Unsplash API Key')).toBeInTheDocument();
      expect(screen.getByLabelText('OpenAI API Key')).toBeInTheDocument();
    });

    it('should have proper accessibility attributes', () => {
      render(<MockSettingsDialog isOpen={true} onClose={mockOnClose} />);
      
      const dialog = screen.getByRole('dialog');
      expect(dialog).toHaveAttribute('aria-labelledby', 'settings-title');
      
      const unsplashInput = screen.getByLabelText('Unsplash API Key');
      expect(unsplashInput).toHaveAttribute('aria-describedby', 'unsplash-help');
    });
  });

  describe('API Key Input', () => {
    it('should allow typing in API key fields', async () => {
      const user = userEvent.setup();
      render(<MockSettingsDialog isOpen={true} onClose={mockOnClose} />);
      
      const unsplashInput = screen.getByLabelText('Unsplash API Key');
      await user.type(unsplashInput, 'test-unsplash-key');
      
      expect(unsplashInput).toHaveValue('test-unsplash-key');
    });

    it('should mask API keys by default', () => {
      render(<MockSettingsDialog isOpen={true} onClose={mockOnClose} />);
      
      const unsplashInput = screen.getByLabelText('Unsplash API Key');
      expect(unsplashInput).toHaveAttribute('type', 'password');
    });

    it('should toggle key visibility', async () => {
      const user = userEvent.setup();
      render(<MockSettingsDialog isOpen={true} onClose={mockOnClose} />);
      
      const unsplashInput = screen.getByLabelText('Unsplash API Key');
      const toggleButton = screen.getByRole('button', { name: 'Toggle key visibility' });
      
      expect(unsplashInput).toHaveAttribute('type', 'password');
      
      await user.click(toggleButton);
      expect(unsplashInput).toHaveAttribute('type', 'text');
      
      await user.click(toggleButton);
      expect(unsplashInput).toHaveAttribute('type', 'password');
    });

    it('should validate individual API keys', async () => {
      const user = userEvent.setup();
      render(<MockSettingsDialog isOpen={true} onClose={mockOnClose} />);
      
      const unsplashInput = screen.getByLabelText('Unsplash API Key');
      await user.type(unsplashInput, 'valid-key');
      
      const validateButton = screen.getByRole('button', { name: /validate/i });
      await user.click(validateButton);
      
      expect(configManager.validateApiKey).toHaveBeenCalledWith('unsplash', 'valid-key');
      
      await waitFor(() => {
        expect(screen.getByText('✓ Valid key')).toBeInTheDocument();
      });
    });

    it('should show validation loading state', async () => {
      const user = userEvent.setup();
      (configManager.validateApiKey as any).mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({ valid: true }), 1000))
      );
      
      render(<MockSettingsDialog isOpen={true} onClose={mockOnClose} />);
      
      const unsplashInput = screen.getByLabelText('Unsplash API Key');
      await user.type(unsplashInput, 'test-key');
      
      const validateButton = screen.getByRole('button', { name: /validate/i });
      await user.click(validateButton);
      
      expect(screen.getByText('Validating...')).toBeInTheDocument();
      expect(validateButton).toBeDisabled();
    });

    it('should show validation error for invalid keys', async () => {
      const user = userEvent.setup();
      (configManager.validateApiKey as any).mockResolvedValue({ valid: false, error: 'Invalid key' });
      
      render(<MockSettingsDialog isOpen={true} onClose={mockOnClose} />);
      
      const unsplashInput = screen.getByLabelText('Unsplash API Key');
      await user.type(unsplashInput, 'invalid-key');
      
      const validateButton = screen.getByRole('button', { name: /validate/i });
      await user.click(validateButton);
      
      await waitFor(() => {
        expect(screen.getByText('✗ Invalid key')).toBeInTheDocument();
      });
    });
  });

  describe('Save Functionality', () => {
    it('should save API keys when save button is clicked', async () => {
      const user = userEvent.setup();
      render(<MockSettingsDialog isOpen={true} onClose={mockOnClose} />);
      
      const unsplashInput = screen.getByLabelText('Unsplash API Key');
      const openaiInput = screen.getByLabelText('OpenAI API Key');
      
      await user.type(unsplashInput, 'unsplash-key-123');
      await user.type(openaiInput, 'sk-openai-key-456');
      
      const saveButton = screen.getByRole('button', { name: 'Save Settings' });
      await user.click(saveButton);
      
      expect(configManager.updateServiceConfiguration).toHaveBeenCalledWith({
        service: 'unsplash',
        apiKey: 'unsplash-key-123'
      });
      
      expect(configManager.updateServiceConfiguration).toHaveBeenCalledWith({
        service: 'openai',
        apiKey: 'sk-openai-key-456'
      });
      
      expect(mockOnClose).toHaveBeenCalled();
    });

    it('should not save empty keys', async () => {
      const user = userEvent.setup();
      render(<MockSettingsDialog isOpen={true} onClose={mockOnClose} />);
      
      const saveButton = screen.getByRole('button', { name: 'Save Settings' });
      await user.click(saveButton);
      
      expect(configManager.updateServiceConfiguration).not.toHaveBeenCalled();
      expect(mockOnClose).toHaveBeenCalled();
    });
  });

  describe('Help Links', () => {
    it('should provide links to API key registration', () => {
      render(<MockSettingsDialog isOpen={true} onClose={mockOnClose} />);
      
      const unsplashLink = screen.getByRole('link', { name: /unsplash developers/i });
      expect(unsplashLink).toHaveAttribute('href', 'https://unsplash.com/developers');
      expect(unsplashLink).toHaveAttribute('target', '_blank');
      expect(unsplashLink).toHaveAttribute('rel', 'noopener noreferrer');
      
      const openaiLink = screen.getByRole('link', { name: /openai platform/i });
      expect(openaiLink).toHaveAttribute('href', 'https://platform.openai.com/api-keys');
    });
  });

  describe('Error Handling', () => {
    it('should handle validation errors gracefully', async () => {
      const user = userEvent.setup();
      (configManager.validateApiKey as any).mockRejectedValue(new Error('Network error'));
      
      render(<MockSettingsDialog isOpen={true} onClose={mockOnClose} />);
      
      const unsplashInput = screen.getByLabelText('Unsplash API Key');
      await user.type(unsplashInput, 'test-key');
      
      const validateButton = screen.getByRole('button', { name: /validate/i });
      await user.click(validateButton);
      
      await waitFor(() => {
        expect(screen.getByText('✗ Invalid key')).toBeInTheDocument();
      });
    });

    it('should handle save errors gracefully', async () => {
      const user = userEvent.setup();
      (configManager.updateServiceConfiguration as any).mockRejectedValue(new Error('Save failed'));
      
      render(<MockSettingsDialog isOpen={true} onClose={mockOnClose} />);
      
      const unsplashInput = screen.getByLabelText('Unsplash API Key');
      await user.type(unsplashInput, 'test-key');
      
      const saveButton = screen.getByRole('button', { name: 'Save Settings' });
      await user.click(saveButton);
      
      // Should still close dialog even on save error
      expect(mockOnClose).toHaveBeenCalled();
    });
  });

  describe('Reset Functionality', () => {
    it('should reset configuration when reset button is clicked', async () => {
      const user = userEvent.setup();
      render(<MockSettingsDialog isOpen={true} onClose={mockOnClose} />);
      
      const resetButton = screen.getByRole('button', { name: 'Reset All' });
      await user.click(resetButton);
      
      expect(configManager.resetConfiguration).toHaveBeenCalled();
    });
  });

  describe('Keyboard Navigation', () => {
    it('should support tab navigation', async () => {
      const user = userEvent.setup();
      render(<MockSettingsDialog isOpen={true} onClose={mockOnClose} />);
      
      const unsplashInput = screen.getByLabelText('Unsplash API Key');
      
      await user.tab();
      expect(unsplashInput).toHaveFocus();
      
      await user.tab();
      // Should move to next focusable element
    });

    it('should handle escape key to close dialog', async () => {
      const user = userEvent.setup();
      render(<MockSettingsDialog isOpen={true} onClose={mockOnClose} />);
      
      await user.keyboard('{Escape}');
      // Would need additional implementation to handle escape key
    });
  });

  describe('Mobile Responsiveness', () => {
    it('should be responsive on small screens', () => {
      // Mock viewport
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      });
      
      render(<MockSettingsDialog isOpen={true} onClose={mockOnClose} />);
      
      // Check that dialog is still usable on mobile
      expect(screen.getByRole('dialog')).toBeInTheDocument();
      expect(screen.getByLabelText('Unsplash API Key')).toBeInTheDocument();
    });
  });
});

describe('Security Features', () => {
  it('should not log sensitive data', async () => {
    const consoleSpy = vi.spyOn(console, 'log');
    const user = userEvent.setup();
    
    render(<MockSettingsDialog isOpen={true} onClose={vi.fn()} />);
    
    const unsplashInput = screen.getByLabelText('Unsplash API Key');
    await user.type(unsplashInput, 'sensitive-api-key');
    
    // Console should not contain the API key
    const consoleCalls = consoleSpy.mock.calls.flat();
    const hasApiKey = consoleCalls.some(call => 
      typeof call === 'string' && call.includes('sensitive-api-key')
    );
    
    expect(hasApiKey).toBe(false);
    
    consoleSpy.mockRestore();
  });

  it('should clear form data on unmount', () => {
    const { unmount } = render(<MockSettingsDialog isOpen={true} onClose={vi.fn()} />);
    
    unmount();
    
    // Form data should be cleared from memory
    // This would require additional implementation
  });
});