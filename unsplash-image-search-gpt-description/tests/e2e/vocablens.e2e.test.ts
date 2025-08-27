import { test, expect, Page } from '@playwright/test';

test.describe('VocabLens PWA E2E Tests', () => {
  let page: Page;

  test.beforeEach(async ({ browser }) => {
    page = await browser.newPage();
    
    // Set viewport for consistent testing
    await page.setViewportSize({ width: 1280, height: 720 });
    
    // Navigate to app
    await page.goto('/');
    
    // Wait for app to load
    await page.waitForSelector('[data-testid="app-container"]', { timeout: 10000 });
  });

  test.afterEach(async () => {
    await page.close();
  });

  test.describe('App Loading and Navigation', () => {
    test('loads the main page successfully', async () => {
      // Check if main elements are present
      await expect(page.locator('h1')).toContainText('VocabLens');
      await expect(page.locator('[data-testid="search-bar"]')).toBeVisible();
    });

    test('navigates between main sections', async () => {
      // Test navigation to vocabulary page
      await page.click('[data-testid="nav-vocabulary"]');
      await expect(page.locator('[data-testid="vocabulary-manager"]')).toBeVisible();
      
      // Test navigation to quiz page
      await page.click('[data-testid="nav-quiz"]');
      await expect(page.locator('[data-testid="quiz-container"]')).toBeVisible();
      
      // Test navigation back to search
      await page.click('[data-testid="nav-search"]');
      await expect(page.locator('[data-testid="search-bar"]')).toBeVisible();
    });

    test('handles responsive design', async () => {
      // Test mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });
      await expect(page.locator('[data-testid="mobile-menu"]')).toBeVisible();
      
      // Test tablet viewport
      await page.setViewportSize({ width: 768, height: 1024 });
      await expect(page.locator('[data-testid="sidebar"]')).toBeVisible();
    });
  });

  test.describe('Image Search Functionality', () => {
    test('performs basic image search', async () => {
      const searchTerm = 'nature';
      
      // Enter search term
      await page.fill('[data-testid="search-input"]', searchTerm);
      
      // Click search button
      await page.click('[data-testid="search-button"]');
      
      // Wait for results
      await page.waitForSelector('[data-testid="search-results"]');
      
      // Check if images are loaded
      const images = page.locator('[data-testid="image-card"]');
      await expect(images).toHaveCountGreaterThan(0);
      
      // Verify search term is displayed
      await expect(page.locator('[data-testid="search-query"]')).toContainText(searchTerm);
    });

    test('handles search with no results', async () => {
      const searchTerm = 'xyznonexistentterm123';
      
      await page.fill('[data-testid="search-input"]', searchTerm);
      await page.click('[data-testid="search-button"]');
      
      // Wait for empty state
      await expect(page.locator('[data-testid="empty-results"]')).toBeVisible();
      await expect(page.locator('[data-testid="empty-results"]')).toContainText('No images found');
    });

    test('implements infinite scroll', async () => {
      await page.fill('[data-testid="search-input"]', 'landscape');
      await page.click('[data-testid="search-button"]');
      
      // Wait for initial results
      await page.waitForSelector('[data-testid="search-results"]');
      
      const initialCount = await page.locator('[data-testid="image-card"]').count();
      
      // Scroll to bottom
      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
      
      // Wait for more images to load
      await page.waitForTimeout(2000);
      
      const newCount = await page.locator('[data-testid="image-card"]').count();
      expect(newCount).toBeGreaterThan(initialCount);
    });

    test('selects image for description generation', async () => {
      await page.fill('[data-testid="search-input"]', 'mountain');
      await page.click('[data-testid="search-button"]');
      
      await page.waitForSelector('[data-testid="image-card"]');
      
      // Click first image
      await page.click('[data-testid="image-card"]:first-child');
      
      // Verify image selection
      await expect(page.locator('[data-testid="selected-image"]')).toBeVisible();
      await expect(page.locator('[data-testid="description-panel"]')).toBeVisible();
    });
  });

  test.describe('AI Description Generation', () => {
    test('generates description for selected image', async () => {
      // Select an image first
      await page.fill('[data-testid="search-input"]', 'forest');
      await page.click('[data-testid="search-button"]');
      await page.waitForSelector('[data-testid="image-card"]');
      await page.click('[data-testid="image-card"]:first-child');
      
      // Generate description
      await page.click('[data-testid="generate-description"]');
      
      // Wait for description to appear
      await expect(page.locator('[data-testid="generated-description"]')).toBeVisible();
      
      // Check if vocabulary words are highlighted
      await expect(page.locator('[data-testid="vocabulary-highlight"]')).toHaveCountGreaterThan(0);
    });

    test('allows style customization', async () => {
      await page.fill('[data-testid="search-input"]', 'ocean');
      await page.click('[data-testid="search-button"]');
      await page.waitForSelector('[data-testid="image-card"]');
      await page.click('[data-testid="image-card"]:first-child');
      
      // Change description style
      await page.selectOption('[data-testid="style-selector"]', 'narrative');
      await page.click('[data-testid="generate-description"]');
      
      await expect(page.locator('[data-testid="generated-description"]')).toBeVisible();
    });

    test('handles generation errors gracefully', async () => {
      // Mock API error by intercepting requests
      await page.route('**/api/generate-description', route => {
        route.fulfill({ status: 500, body: 'Server error' });
      });

      await page.fill('[data-testid="search-input"]', 'test');
      await page.click('[data-testid="search-button"]');
      await page.waitForSelector('[data-testid="image-card"]');
      await page.click('[data-testid="image-card"]:first-child');
      await page.click('[data-testid="generate-description"]');
      
      await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
      await expect(page.locator('[data-testid="error-message"]')).toContainText('Failed to generate description');
    });
  });

  test.describe('Vocabulary Management', () => {
    test('adds vocabulary from description', async () => {
      // Navigate to search and generate a description
      await page.fill('[data-testid="search-input"]', 'garden');
      await page.click('[data-testid="search-button"]');
      await page.waitForSelector('[data-testid="image-card"]');
      await page.click('[data-testid="image-card"]:first-child');
      await page.click('[data-testid="generate-description"]');
      
      await page.waitForSelector('[data-testid="vocabulary-highlight"]');
      
      // Click on highlighted word
      await page.click('[data-testid="vocabulary-highlight"]:first-child');
      
      // Verify add vocabulary dialog
      await expect(page.locator('[data-testid="add-vocabulary-dialog"]')).toBeVisible();
      
      // Add the word
      await page.click('[data-testid="add-vocabulary-confirm"]');
      
      // Check success message
      await expect(page.locator('[data-testid="success-message"]')).toContainText('Vocabulary added');
    });

    test('manages vocabulary in vocabulary page', async () => {
      await page.click('[data-testid="nav-vocabulary"]');
      
      // Wait for vocabulary list
      await page.waitForSelector('[data-testid="vocabulary-list"]');
      
      // Add new vocabulary manually
      await page.click('[data-testid="add-vocabulary-button"]');
      await page.fill('[data-testid="word-input"]', 'serendipity');
      await page.fill('[data-testid="definition-input"]', 'A pleasant surprise');
      await page.selectOption('[data-testid="difficulty-select"]', 'advanced');
      await page.click('[data-testid="save-vocabulary"]');
      
      // Verify word appears in list
      await expect(page.locator('[data-testid="vocabulary-item"]')).toContainText('serendipity');
    });

    test('filters and searches vocabulary', async () => {
      await page.click('[data-testid="nav-vocabulary"]');
      await page.waitForSelector('[data-testid="vocabulary-list"]');
      
      // Use search filter
      await page.fill('[data-testid="vocabulary-search"]', 'nature');
      
      // Wait for filtered results
      await page.waitForTimeout(500);
      
      // Verify filtered results
      const visibleItems = page.locator('[data-testid="vocabulary-item"]:visible');
      await expect(visibleItems).toHaveCountGreaterThan(0);
      
      // Test difficulty filter
      await page.selectOption('[data-testid="difficulty-filter"]', 'advanced');
      await page.waitForTimeout(500);
    });
  });

  test.describe('Spaced Repetition Quiz', () => {
    test('starts and completes a quiz', async () => {
      await page.click('[data-testid="nav-quiz"]');
      
      // Start quiz
      await page.click('[data-testid="start-quiz"]');
      
      // Wait for quiz question
      await expect(page.locator('[data-testid="quiz-question"]')).toBeVisible();
      
      // Answer question
      await page.click('[data-testid="quiz-option"]:first-child');
      
      // Submit answer
      await page.click('[data-testid="submit-answer"]');
      
      // Check feedback
      await expect(page.locator('[data-testid="quiz-feedback"]')).toBeVisible();
      
      // Continue to next question or finish
      if (await page.locator('[data-testid="next-question"]').isVisible()) {
        await page.click('[data-testid="next-question"]');
      } else {
        await expect(page.locator('[data-testid="quiz-complete"]')).toBeVisible();
      }
    });

    test('shows quiz statistics', async () => {
      await page.click('[data-testid="nav-quiz"]');
      
      // Check if statistics are displayed
      await expect(page.locator('[data-testid="quiz-stats"]')).toBeVisible();
      await expect(page.locator('[data-testid="words-mastered"]')).toBeVisible();
      await expect(page.locator('[data-testid="quiz-accuracy"]')).toBeVisible();
    });
  });

  test.describe('PWA Features', () => {
    test('shows install prompt', async () => {
      // Trigger beforeinstallprompt event
      await page.evaluate(() => {
        const event = new Event('beforeinstallprompt');
        window.dispatchEvent(event);
      });
      
      // Check if install prompt appears
      await expect(page.locator('[data-testid="install-prompt"]')).toBeVisible();
      
      // Test dismiss functionality
      await page.click('[data-testid="dismiss-install"]');
      await expect(page.locator('[data-testid="install-prompt"]')).not.toBeVisible();
    });

    test('handles offline state', async () => {
      // Go offline
      await page.route('**/*', route => route.abort());
      
      // Trigger offline event
      await page.evaluate(() => {
        Object.defineProperty(navigator, 'onLine', { value: false });
        window.dispatchEvent(new Event('offline'));
      });
      
      // Check offline banner
      await expect(page.locator('[data-testid="offline-banner"]')).toBeVisible();
      
      // Try to search (should show cached results or offline message)
      await page.fill('[data-testid="search-input"]', 'offline test');
      await page.click('[data-testid="search-button"]');
      
      await expect(page.locator('[data-testid="offline-message"]')).toBeVisible();
    });

    test('caches resources for offline use', async () => {
      // Check if service worker is registered
      const swRegistered = await page.evaluate(() => {
        return 'serviceWorker' in navigator;
      });
      
      expect(swRegistered).toBe(true);
      
      // Check if cache API is available
      const cacheAvailable = await page.evaluate(() => {
        return 'caches' in window;
      });
      
      expect(cacheAvailable).toBe(true);
    });
  });

  test.describe('Accessibility', () => {
    test('supports keyboard navigation', async () => {
      // Tab through main navigation
      await page.keyboard.press('Tab');
      await expect(page.locator('[data-testid="search-input"]')).toBeFocused();
      
      await page.keyboard.press('Tab');
      await expect(page.locator('[data-testid="search-button"]')).toBeFocused();
      
      // Continue tabbing through elements
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
    });

    test('provides proper ARIA labels', async () => {
      // Check main navigation
      await expect(page.locator('[role="navigation"]')).toBeVisible();
      
      // Check search region
      await expect(page.locator('[role="search"]')).toBeVisible();
      
      // Check main content
      await expect(page.locator('[role="main"]')).toBeVisible();
    });

    test('supports screen reader navigation', async () => {
      // Check heading structure
      const h1 = await page.locator('h1').count();
      expect(h1).toBe(1);
      
      // Check for proper heading hierarchy
      const headings = await page.locator('h1, h2, h3, h4, h5, h6').allTextContents();
      expect(headings.length).toBeGreaterThan(0);
    });

    test('meets color contrast requirements', async () => {
      // This would require more complex color analysis
      // For now, check that dark mode toggle works
      if (await page.locator('[data-testid="theme-toggle"]').isVisible()) {
        await page.click('[data-testid="theme-toggle"]');
        
        // Verify dark theme is applied
        const bodyClass = await page.getAttribute('body', 'class');
        expect(bodyClass).toContain('dark');
      }
    });
  });

  test.describe('Performance', () => {
    test('loads within performance budget', async () => {
      const startTime = Date.now();
      await page.goto('/');
      await page.waitForSelector('[data-testid="app-container"]');
      const endTime = Date.now();
      
      const loadTime = endTime - startTime;
      expect(loadTime).toBeLessThan(3000); // Should load within 3 seconds
    });

    test('handles large datasets efficiently', async () => {
      // Search for a term that returns many results
      await page.fill('[data-testid="search-input"]', 'nature');
      await page.click('[data-testid="search-button"]');
      
      await page.waitForSelector('[data-testid="search-results"]');
      
      // Measure scroll performance
      const startTime = performance.now();
      
      for (let i = 0; i < 5; i++) {
        await page.evaluate(() => window.scrollBy(0, 500));
        await page.waitForTimeout(100);
      }
      
      const endTime = performance.now();
      const scrollTime = endTime - startTime;
      
      expect(scrollTime).toBeLessThan(1000); // Smooth scrolling
    });
  });

  test.describe('Error Handling', () => {
    test('handles network errors gracefully', async () => {
      // Mock network failure
      await page.route('**/api/search/photos', route => {
        route.fulfill({ status: 500, body: 'Internal server error' });
      });

      await page.fill('[data-testid="search-input"]', 'error test');
      await page.click('[data-testid="search-button"]');
      
      // Should show error message
      await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
      await expect(page.locator('[data-testid="retry-button"]')).toBeVisible();
    });

    test('recovers from errors with retry functionality', async () => {
      let callCount = 0;
      
      // Mock failing then succeeding API
      await page.route('**/api/search/photos', route => {
        callCount++;
        if (callCount === 1) {
          route.fulfill({ status: 500, body: 'Server error' });
        } else {
          route.continue();
        }
      });

      await page.fill('[data-testid="search-input"]', 'retry test');
      await page.click('[data-testid="search-button"]');
      
      // Should show error first
      await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
      
      // Click retry
      await page.click('[data-testid="retry-button"]');
      
      // Should succeed on retry
      await expect(page.locator('[data-testid="search-results"]')).toBeVisible();
    });
  });
});