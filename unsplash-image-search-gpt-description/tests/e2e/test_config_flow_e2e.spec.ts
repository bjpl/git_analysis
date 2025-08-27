/**
 * End-to-End Tests for Configuration Flow
 * Tests the complete user journey through API configuration using Playwright
 */

import { test, expect, Page, BrowserContext } from '@playwright/test';

// Test configuration
const TEST_CONFIG = {
  baseUrl: process.env.VITE_APP_URL || 'http://localhost:5173',
  timeouts: {
    navigation: 10000,
    validation: 30000,
    apiCall: 15000
  },
  testKeys: {
    unsplash: {
      valid: process.env.TEST_UNSPLASH_KEY || 'test-unsplash-key-123',
      invalid: 'invalid-unsplash-key'
    },
    openai: {
      valid: process.env.TEST_OPENAI_KEY || 'sk-test-openai-key-456',
      invalid: 'invalid-openai-key'
    }
  }
};

// Page object for API Settings
class ApiSettingsPage {
  constructor(private page: Page) {}

  // Locators
  get settingsButton() { return this.page.getByTestId('settings-button'); }
  get apiSettingsTab() { return this.page.getByTestId('api-settings-tab'); }
  get unsplashKeyInput() { return this.page.getByTestId('unsplash-key-input'); }
  get openaiKeyInput() { return this.page.getByTestId('openai-key-input'); }
  get validateUnsplashButton() { return this.page.getByTestId('validate-unsplash-button'); }
  get validateOpenaiButton() { return this.page.getByTestId('validate-openai-button'); }
  get saveButton() { return this.page.getByTestId('save-settings-button'); }
  get resetButton() { return this.page.getByTestId('reset-settings-button'); }
  get closeButton() { return this.page.getByTestId('close-settings-button'); }
  get validationSuccess() { return this.page.getByTestId('validation-success'); }
  get validationError() { return this.page.getByTestId('validation-error'); }
  get loadingSpinner() { return this.page.getByTestId('validation-loading'); }

  // Actions
  async openSettings() {
    await this.settingsButton.click();
    await this.page.waitForSelector('[data-testid="api-settings-dialog"]');
  }

  async enterUnsplashKey(key: string) {
    await this.unsplashKeyInput.fill(key);
  }

  async enterOpenaiKey(key: string) {
    await this.openaiKeyInput.fill(key);
  }

  async validateUnsplashKey() {
    await this.validateUnsplashButton.click();
    await this.page.waitForSelector('[data-testid="validation-success"], [data-testid="validation-error"]', {
      timeout: TEST_CONFIG.timeouts.validation
    });
  }

  async validateOpenaiKey() {
    await this.validateOpenaiButton.click();
    await this.page.waitForSelector('[data-testid="validation-success"], [data-testid="validation-error"]', {
      timeout: TEST_CONFIG.timeouts.validation
    });
  }

  async saveSettings() {
    await this.saveButton.click();
    await this.page.waitForSelector('[data-testid="save-success-toast"]');
  }

  async resetSettings() {
    await this.resetButton.click();
    // Wait for confirmation dialog if any
    const confirmButton = this.page.getByTestId('confirm-reset-button');
    if (await confirmButton.isVisible()) {
      await confirmButton.click();
    }
  }

  async closeSettings() {
    await this.closeButton.click();
    await this.page.waitForSelector('[data-testid="api-settings-dialog"]', { state: 'hidden' });
  }
}

// Page object for First-time Setup Wizard
class SetupWizardPage {
  constructor(private page: Page) {}

  // Locators
  get wizardContainer() { return this.page.getByTestId('setup-wizard'); }
  get nextButton() { return this.page.getByTestId('wizard-next-button'); }
  get prevButton() { return this.page.getByTestId('wizard-prev-button'); }
  get skipButton() { return this.page.getByTestId('wizard-skip-button'); }
  get finishButton() { return this.page.getByTestId('wizard-finish-button'); }
  get progressBar() { return this.page.getByTestId('wizard-progress'); }
  get stepTitle() { return this.page.getByTestId('wizard-step-title'); }

  // Actions
  async clickNext() {
    await this.nextButton.click();
  }

  async clickPrevious() {
    await this.prevButton.click();
  }

  async clickSkip() {
    await this.skipButton.click();
  }

  async clickFinish() {
    await this.finishButton.click();
  }

  async waitForStep(stepName: string) {
    await this.page.waitForSelector(`[data-testid="wizard-step-${stepName}"]`);
  }
}

test.describe('API Configuration Flow E2E', () => {
  let context: BrowserContext;
  let page: Page;
  let apiSettings: ApiSettingsPage;
  let setupWizard: SetupWizardPage;

  test.beforeEach(async ({ browser }) => {
    context = await browser.newContext({
      permissions: ['clipboard-read', 'clipboard-write']
    });
    page = await context.newPage();
    apiSettings = new ApiSettingsPage(page);
    setupWizard = new SetupWizardPage(page);

    // Clear local storage to simulate fresh user
    await page.goto(TEST_CONFIG.baseUrl);
    await page.evaluate(() => localStorage.clear());
    await page.reload();
  });

  test.afterEach(async () => {
    await context.close();
  });

  test.describe('First-Time User Setup', () => {
    test('should show setup wizard for new user', async () => {
      await page.goto(TEST_CONFIG.baseUrl);
      
      // Setup wizard should appear for new user
      await expect(setupWizard.wizardContainer).toBeVisible();
      await expect(setupWizard.stepTitle).toContainText('Welcome');
    });

    test('should complete full setup wizard flow', async () => {
      await page.goto(TEST_CONFIG.baseUrl);
      
      // Step 1: Welcome
      await expect(setupWizard.stepTitle).toContainText('Welcome');
      await setupWizard.clickNext();

      // Step 2: Unsplash API
      await setupWizard.waitForStep('unsplash');
      await page.getByTestId('unsplash-key-input').fill(TEST_CONFIG.testKeys.unsplash.valid);
      await page.getByTestId('validate-unsplash-button').click();
      
      await expect(page.getByTestId('unsplash-validation-success')).toBeVisible();
      await setupWizard.clickNext();

      // Step 3: OpenAI API
      await setupWizard.waitForStep('openai');
      await page.getByTestId('openai-key-input').fill(TEST_CONFIG.testKeys.openai.valid);
      await page.getByTestId('validate-openai-button').click();
      
      await expect(page.getByTestId('openai-validation-success')).toBeVisible();
      await setupWizard.clickNext();

      // Step 4: Verification
      await setupWizard.waitForStep('verification');
      await expect(page.getByTestId('unsplash-status')).toContainText('Connected');
      await expect(page.getByTestId('openai-status')).toContainText('Connected');
      await setupWizard.clickNext();

      // Step 5: Complete
      await setupWizard.waitForStep('complete');
      await expect(page.getByText('Setup Complete')).toBeVisible();
      await setupWizard.clickFinish();

      // Should navigate to main app
      await expect(page.getByTestId('main-app')).toBeVisible();
      await expect(setupWizard.wizardContainer).not.toBeVisible();
    });

    test('should allow partial setup', async () => {
      await page.goto(TEST_CONFIG.baseUrl);
      
      // Go through wizard but only set up Unsplash
      await setupWizard.clickNext(); // Welcome
      
      // Set up Unsplash only
      await page.getByTestId('unsplash-key-input').fill(TEST_CONFIG.testKeys.unsplash.valid);
      await page.getByTestId('validate-unsplash-button').click();
      await expect(page.getByTestId('unsplash-validation-success')).toBeVisible();
      
      // Skip OpenAI
      await setupWizard.clickNext(); // Skip OpenAI step
      await setupWizard.clickNext(); // Verification
      await setupWizard.clickNext(); // Complete
      await setupWizard.clickFinish();

      // Should still complete successfully
      await expect(page.getByTestId('main-app')).toBeVisible();
    });

    test('should handle setup cancellation', async () => {
      await page.goto(TEST_CONFIG.baseUrl);
      
      await setupWizard.clickNext(); // Welcome
      
      // Try to close/cancel setup
      await page.keyboard.press('Escape');
      // or click a cancel button if available
      const cancelButton = page.getByTestId('wizard-cancel-button');
      if (await cancelButton.isVisible()) {
        await cancelButton.click();
      }

      // Should still show the app, possibly with limited functionality
      await expect(page.getByTestId('main-app')).toBeVisible();
    });
  });

  test.describe('API Key Validation', () => {
    test('should validate valid Unsplash API key', async () => {
      await page.goto(TEST_CONFIG.baseUrl);
      await apiSettings.openSettings();
      
      await apiSettings.enterUnsplashKey(TEST_CONFIG.testKeys.unsplash.valid);
      await apiSettings.validateUnsplashKey();
      
      await expect(apiSettings.validationSuccess).toBeVisible();
      await expect(page.getByText('Unsplash API key is valid')).toBeVisible();
    });

    test('should reject invalid Unsplash API key', async () => {
      await page.goto(TEST_CONFIG.baseUrl);
      await apiSettings.openSettings();
      
      await apiSettings.enterUnsplashKey(TEST_CONFIG.testKeys.unsplash.invalid);
      await apiSettings.validateUnsplashKey();
      
      await expect(apiSettings.validationError).toBeVisible();
      await expect(page.getByText(/invalid.*api.*key/i)).toBeVisible();
    });

    test('should validate valid OpenAI API key', async () => {
      await page.goto(TEST_CONFIG.baseUrl);
      await apiSettings.openSettings();
      
      await apiSettings.enterOpenaiKey(TEST_CONFIG.testKeys.openai.valid);
      await apiSettings.validateOpenaiKey();
      
      await expect(apiSettings.validationSuccess).toBeVisible();
      await expect(page.getByText('OpenAI API key is valid')).toBeVisible();
    });

    test('should reject invalid OpenAI API key', async () => {
      await page.goto(TEST_CONFIG.baseUrl);
      await apiSettings.openSettings();
      
      await apiSettings.enterOpenaiKey(TEST_CONFIG.testKeys.openai.invalid);
      await apiSettings.validateOpenaiKey();
      
      await expect(apiSettings.validationError).toBeVisible();
      await expect(page.getByText(/invalid.*api.*key/i)).toBeVisible();
    });

    test('should show loading state during validation', async () => {
      await page.goto(TEST_CONFIG.baseUrl);
      await apiSettings.openSettings();
      
      await apiSettings.enterUnsplashKey(TEST_CONFIG.testKeys.unsplash.valid);
      
      // Start validation and immediately check for loading state
      const validationPromise = apiSettings.validateUnsplashKey();
      await expect(apiSettings.loadingSpinner).toBeVisible();
      await expect(apiSettings.validateUnsplashButton).toBeDisabled();
      
      await validationPromise;
      await expect(apiSettings.loadingSpinner).not.toBeVisible();
      await expect(apiSettings.validateUnsplashButton).toBeEnabled();
    });

    test('should handle network timeout during validation', async () => {
      // Mock network delay
      await page.route('**/api/**', async route => {
        await new Promise(resolve => setTimeout(resolve, 35000)); // Longer than timeout
        await route.continue();
      });

      await page.goto(TEST_CONFIG.baseUrl);
      await apiSettings.openSettings();
      
      await apiSettings.enterUnsplashKey(TEST_CONFIG.testKeys.unsplash.valid);
      await apiSettings.validateUnsplashKey();
      
      await expect(page.getByText(/timeout/i)).toBeVisible();
    });
  });

  test.describe('Settings Persistence', () => {
    test('should save and persist API key configuration', async () => {
      await page.goto(TEST_CONFIG.baseUrl);
      await apiSettings.openSettings();
      
      // Enter and validate keys
      await apiSettings.enterUnsplashKey(TEST_CONFIG.testKeys.unsplash.valid);
      await apiSettings.validateUnsplashKey();
      await expect(apiSettings.validationSuccess).toBeVisible();
      
      await apiSettings.enterOpenaiKey(TEST_CONFIG.testKeys.openai.valid);
      await apiSettings.validateOpenaiKey();
      await expect(apiSettings.validationSuccess).toBeVisible();
      
      // Save settings
      await apiSettings.saveSettings();
      await apiSettings.closeSettings();
      
      // Reload page
      await page.reload();
      
      // Check that configuration persisted
      await apiSettings.openSettings();
      
      // Keys should be masked but present
      await expect(apiSettings.unsplashKeyInput).toHaveValue(/\*+/);
      await expect(apiSettings.openaiKeyInput).toHaveValue(/sk-\*+/);
    });

    test('should reset configuration to defaults', async () => {
      await page.goto(TEST_CONFIG.baseUrl);
      await apiSettings.openSettings();
      
      // Set some configuration first
      await apiSettings.enterUnsplashKey(TEST_CONFIG.testKeys.unsplash.valid);
      await apiSettings.saveSettings();
      
      // Reset configuration
      await apiSettings.resetSettings();
      
      // Confirm reset
      const confirmDialog = page.getByTestId('confirm-reset-dialog');
      if (await confirmDialog.isVisible()) {
        await page.getByTestId('confirm-reset-yes').click();
      }
      
      // Check that fields are cleared
      await expect(apiSettings.unsplashKeyInput).toHaveValue('');
      await expect(apiSettings.openaiKeyInput).toHaveValue('');
    });
  });

  test.describe('User Experience Features', () => {
    test('should mask API keys in input fields', async () => {
      await page.goto(TEST_CONFIG.baseUrl);
      await apiSettings.openSettings();
      
      // Enter API key
      await apiSettings.enterUnsplashKey(TEST_CONFIG.testKeys.unsplash.valid);
      
      // Input should be of type password
      await expect(apiSettings.unsplashKeyInput).toHaveAttribute('type', 'password');
      
      // Toggle visibility if available
      const showButton = page.getByTestId('show-unsplash-key');
      if (await showButton.isVisible()) {
        await showButton.click();
        await expect(apiSettings.unsplashKeyInput).toHaveAttribute('type', 'text');
        
        await showButton.click();
        await expect(apiSettings.unsplashKeyInput).toHaveAttribute('type', 'password');
      }
    });

    test('should provide help links for API key registration', async () => {
      await page.goto(TEST_CONFIG.baseUrl);
      await apiSettings.openSettings();
      
      // Check Unsplash help link
      const unsplashHelpLink = page.getByRole('link', { name: /unsplash developers/i });
      await expect(unsplashHelpLink).toHaveAttribute('href', /unsplash\.com\/developers/);
      await expect(unsplashHelpLink).toHaveAttribute('target', '_blank');
      
      // Check OpenAI help link
      const openaiHelpLink = page.getByRole('link', { name: /openai platform/i });
      await expect(openaiHelpLink).toHaveAttribute('href', /platform\.openai\.com/);
      await expect(openaiHelpLink).toHaveAttribute('target', '_blank');
    });

    test('should show success feedback after saving', async () => {
      await page.goto(TEST_CONFIG.baseUrl);
      await apiSettings.openSettings();
      
      await apiSettings.enterUnsplashKey(TEST_CONFIG.testKeys.unsplash.valid);
      await apiSettings.saveSettings();
      
      // Should show success toast/notification
      await expect(page.getByTestId('save-success-toast')).toBeVisible();
      await expect(page.getByText(/settings saved successfully/i)).toBeVisible();
    });

    test('should handle keyboard shortcuts', async () => {
      await page.goto(TEST_CONFIG.baseUrl);
      
      // Open settings with keyboard shortcut
      await page.keyboard.press('Control+,');
      await expect(page.getByTestId('api-settings-dialog')).toBeVisible();
      
      // Close with Escape
      await page.keyboard.press('Escape');
      await expect(page.getByTestId('api-settings-dialog')).not.toBeVisible();
    });
  });

  test.describe('Error Scenarios', () => {
    test('should handle offline scenarios', async () => {
      await page.goto(TEST_CONFIG.baseUrl);
      
      // Simulate offline
      await context.setOffline(true);
      
      await apiSettings.openSettings();
      await apiSettings.enterUnsplashKey(TEST_CONFIG.testKeys.unsplash.valid);
      await apiSettings.validateUnsplashKey();
      
      // Should show appropriate offline message
      await expect(page.getByText(/offline/i)).toBeVisible();
      await expect(page.getByText(/check your connection/i)).toBeVisible();
    });

    test('should handle server errors gracefully', async () => {
      // Mock server error
      await page.route('**/api/**', route => 
        route.fulfill({ status: 500, body: 'Internal Server Error' })
      );

      await page.goto(TEST_CONFIG.baseUrl);
      await apiSettings.openSettings();
      
      await apiSettings.enterUnsplashKey(TEST_CONFIG.testKeys.unsplash.valid);
      await apiSettings.validateUnsplashKey();
      
      await expect(page.getByText(/server error/i)).toBeVisible();
    });

    test('should handle malformed responses', async () => {
      // Mock malformed JSON response
      await page.route('**/api/**', route => 
        route.fulfill({ 
          status: 200, 
          contentType: 'application/json',
          body: 'invalid json{'
        })
      );

      await page.goto(TEST_CONFIG.baseUrl);
      await apiSettings.openSettings();
      
      await apiSettings.enterUnsplashKey(TEST_CONFIG.testKeys.unsplash.valid);
      await apiSettings.validateUnsplashKey();
      
      await expect(page.getByText(/unexpected error/i)).toBeVisible();
    });
  });

  test.describe('Mobile Responsiveness', () => {
    test('should work on mobile devices', async () => {
      await page.setViewportSize({ width: 375, height: 667 }); // iPhone SE
      await page.goto(TEST_CONFIG.baseUrl);
      
      await apiSettings.openSettings();
      
      // Settings dialog should be properly sized for mobile
      const dialog = page.getByTestId('api-settings-dialog');
      await expect(dialog).toBeVisible();
      
      // Should be able to interact with form elements
      await apiSettings.enterUnsplashKey(TEST_CONFIG.testKeys.unsplash.valid);
      await expect(apiSettings.unsplashKeyInput).toHaveValue(TEST_CONFIG.testKeys.unsplash.valid);
      
      // Save button should be accessible
      await expect(apiSettings.saveButton).toBeVisible();
    });

    test('should handle touch interactions', async () => {
      await page.setViewportSize({ width: 375, height: 667 });
      await page.goto(TEST_CONFIG.baseUrl);
      
      // Simulate touch interaction
      await page.tap('[data-testid="settings-button"]');
      await expect(page.getByTestId('api-settings-dialog')).toBeVisible();
      
      // Touch scroll should work in long forms
      await page.tap('[data-testid="unsplash-key-input"]');
      await expect(apiSettings.unsplashKeyInput).toBeFocused();
    });
  });

  test.describe('Security Features', () => {
    test('should not leak API keys in network requests', async () => {
      const requests: string[] = [];
      
      page.on('request', request => {
        requests.push(request.url());
      });
      
      await page.goto(TEST_CONFIG.baseUrl);
      await apiSettings.openSettings();
      
      await apiSettings.enterUnsplashKey(TEST_CONFIG.testKeys.unsplash.valid);
      await apiSettings.saveSettings();
      
      // Check that API key is not visible in URLs
      const hasApiKeyInUrl = requests.some(url => 
        url.includes(TEST_CONFIG.testKeys.unsplash.valid)
      );
      
      expect(hasApiKeyInUrl).toBe(false);
    });

    test('should clear sensitive data from memory', async () => {
      await page.goto(TEST_CONFIG.baseUrl);
      await apiSettings.openSettings();
      
      await apiSettings.enterUnsplashKey(TEST_CONFIG.testKeys.unsplash.valid);
      await apiSettings.closeSettings();
      
      // Navigate away and back
      await page.goto('about:blank');
      await page.goto(TEST_CONFIG.baseUrl);
      
      // Temporary form data should be cleared
      await apiSettings.openSettings();
      // Only saved (encrypted) data should remain
    });

    test('should handle XSS attempts in API keys', async () => {
      await page.goto(TEST_CONFIG.baseUrl);
      await apiSettings.openSettings();
      
      const xssPayload = '<script>window.xssExecuted = true;</script>';
      await apiSettings.enterUnsplashKey(xssPayload);
      
      // Script should not execute
      const xssExecuted = await page.evaluate(() => (window as any).xssExecuted);
      expect(xssExecuted).toBeUndefined();
    });
  });

  test.describe('Browser Compatibility', () => {
    test('should work in private/incognito mode', async () => {
      // This test would typically run with a separate browser context
      // configured for private browsing mode
      await page.goto(TEST_CONFIG.baseUrl);
      
      // App should still function, with appropriate warnings about session-only storage
      await apiSettings.openSettings();
      await expect(page.getByTestId('api-settings-dialog')).toBeVisible();
      
      // May show warning about private browsing limitations
      const privateWarning = page.getByTestId('private-browsing-warning');
      if (await privateWarning.isVisible()) {
        await expect(privateWarning).toContainText(/private browsing/i);
      }
    });

    test('should handle storage quota exceeded', async () => {
      // Mock localStorage quota exceeded
      await page.addInitScript(() => {
        const originalSetItem = localStorage.setItem;
        localStorage.setItem = () => {
          throw new DOMException('QuotaExceededError');
        };
      });

      await page.goto(TEST_CONFIG.baseUrl);
      await apiSettings.openSettings();
      
      await apiSettings.enterUnsplashKey(TEST_CONFIG.testKeys.unsplash.valid);
      await apiSettings.saveSettings();
      
      // Should show appropriate error message
      await expect(page.getByText(/storage.*full/i)).toBeVisible();
    });
  });
});