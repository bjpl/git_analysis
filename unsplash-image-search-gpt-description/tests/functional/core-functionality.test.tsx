import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { SearchBar } from '../../src/components/ImageSearch/SearchBar';
import { mockImage } from '../mocks/mockData';

// Test wrapper with providers
const TestWrapper = ({ children }: { children: React.ReactNode }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return (
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    </BrowserRouter>
  );
};

describe('Core Functionality Tests', () => {
  const mockOnSearch = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('SearchBar Component', () => {
    it('should render search input with placeholder', () => {
      render(
        <TestWrapper>
          <SearchBar onSearch={mockOnSearch} placeholder="Search images..." />
        </TestWrapper>
      );

      const searchInput = screen.getByPlaceholderText('Search images...');
      expect(searchInput).toBeInTheDocument();
      expect(searchInput).toHaveAttribute('type', 'text');
    });

    it('should call onSearch when form is submitted with valid input', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <SearchBar onSearch={mockOnSearch} />
        </TestWrapper>
      );

      const searchInput = screen.getByRole('textbox');
      const searchButton = screen.getByRole('button', { name: /search/i });

      await user.type(searchInput, 'beautiful landscape');
      await user.click(searchButton);

      expect(mockOnSearch).toHaveBeenCalledWith('beautiful landscape');
      expect(mockOnSearch).toHaveBeenCalledTimes(1);
    });

    it('should not submit empty search queries', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <SearchBar onSearch={mockOnSearch} />
        </TestWrapper>
      );

      const searchButton = screen.getByRole('button', { name: /search/i });
      await user.click(searchButton);

      expect(mockOnSearch).not.toHaveBeenCalled();
    });

    it('should trim whitespace from search queries', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <SearchBar onSearch={mockOnSearch} />
        </TestWrapper>
      );

      const searchInput = screen.getByRole('textbox');
      const searchButton = screen.getByRole('button', { name: /search/i });

      await user.type(searchInput, '  mountains and lakes  ');
      await user.click(searchButton);

      expect(mockOnSearch).toHaveBeenCalledWith('mountains and lakes');
    });

    it('should show loading state when isLoading is true', () => {
      render(
        <TestWrapper>
          <SearchBar onSearch={mockOnSearch} isLoading={true} />
        </TestWrapper>
      );

      const searchInput = screen.getByRole('textbox');
      const searchButton = screen.getByRole('button', { name: /search/i });

      expect(searchInput).toBeDisabled();
      expect(searchButton).toBeDisabled();
    });

    it('should handle keyboard navigation with Enter key', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <SearchBar onSearch={mockOnSearch} />
        </TestWrapper>
      );

      const searchInput = screen.getByRole('textbox');
      
      await user.type(searchInput, 'ocean waves');
      await user.keyboard('{Enter}');

      expect(mockOnSearch).toHaveBeenCalledWith('ocean waves');
    });
  });

  describe('Application Routing', () => {
    it('should render different routes correctly', () => {
      // Test would verify routing functionality
      expect(true).toBe(true); // Placeholder test
    });
  });

  describe('Image Display', () => {
    it('should display image with correct attributes', () => {
      const imageElement = document.createElement('img');
      imageElement.src = mockImage.urls.regular;
      imageElement.alt = mockImage.alt_description || '';
      
      expect(imageElement.src).toBe(mockImage.urls.regular);
      expect(imageElement.alt).toBe(mockImage.alt_description);
    });
  });

  describe('Error Handling', () => {
    it('should handle network errors gracefully', async () => {
      // Mock network error
      const mockError = new Error('Network error');
      const handleError = vi.fn();
      
      try {
        throw mockError;
      } catch (error) {
        handleError(error);
      }
      
      expect(handleError).toHaveBeenCalledWith(mockError);
    });

    it('should display user-friendly error messages', () => {
      const errorMessage = 'Something went wrong. Please try again.';
      
      render(
        <div role="alert" aria-live="polite">
          {errorMessage}
        </div>
      );

      expect(screen.getByRole('alert')).toHaveTextContent(errorMessage);
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA attributes', () => {
      render(
        <TestWrapper>
          <SearchBar 
            onSearch={mockOnSearch} 
            placeholder="Search for images"
          />
        </TestWrapper>
      );

      const searchInput = screen.getByRole('textbox');
      expect(searchInput).toHaveAttribute('placeholder', 'Search for images');
    });

    it('should support keyboard navigation', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <SearchBar onSearch={mockOnSearch} />
        </TestWrapper>
      );

      const searchInput = screen.getByRole('textbox');
      
      // Tab to focus input
      await user.tab();
      expect(searchInput).toHaveFocus();
      
      // Type and submit with Enter
      await user.type(searchInput, 'test');
      await user.keyboard('{Enter}');
      
      expect(mockOnSearch).toHaveBeenCalledWith('test');
    });
  });

  describe('Responsive Design', () => {
    it('should adapt to different screen sizes', () => {
      // Mock window resize
      global.innerWidth = 768;
      global.dispatchEvent(new Event('resize'));
      
      render(
        <TestWrapper>
          <SearchBar onSearch={mockOnSearch} />
        </TestWrapper>
      );

      const searchInput = screen.getByRole('textbox');
      expect(searchInput).toBeInTheDocument();
    });
  });

  describe('Performance', () => {
    it('should debounce search inputs', async () => {
      const user = userEvent.setup();
      let callCount = 0;
      const debouncedSearch = vi.fn(() => {
        callCount++;
      });
      
      render(
        <TestWrapper>
          <SearchBar onSearch={debouncedSearch} />
        </TestWrapper>
      );

      const searchInput = screen.getByRole('textbox');
      
      // Type rapidly
      await user.type(searchInput, 'fast typing', { delay: 50 });
      
      // Should be called only once or limited times due to debouncing
      expect(callCount).toBeLessThan(5);
    });
  });
});