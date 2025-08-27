import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '../../../tests/utils/testUtils';
import userEvent from '@testing-library/user-event';
import { SearchBar } from '../../../src/components/ImageSearch/SearchBar';
import { SearchResults } from '../../../src/components/ImageSearch/SearchResults';
import { ImageCard } from '../../../src/components/ImageSearch/ImageCard';
import { server } from '../../mocks/server';
import { http, HttpResponse } from 'msw';
import { createMockPhoto } from '../../../tests/utils/testUtils';

describe('ImageSearch Components', () => {
  describe('SearchBar', () => {
    const mockOnSearch = vi.fn();
    const user = userEvent.setup();

    beforeEach(() => {
      mockOnSearch.mockClear();
    });

    it('renders search input and button', () => {
      render(
        <SearchBar 
          onSearch={mockOnSearch}
          isLoading={false}
          placeholder="Search for images..."
        />
      );

      expect(screen.getByRole('searchbox')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /search/i })).toBeInTheDocument();
    });

    it('calls onSearch when form is submitted', async () => {
      render(
        <SearchBar 
          onSearch={mockOnSearch}
          isLoading={false}
        />
      );

      const searchInput = screen.getByRole('searchbox');
      const searchButton = screen.getByRole('button', { name: /search/i });

      await user.type(searchInput, 'mountains');
      await user.click(searchButton);

      expect(mockOnSearch).toHaveBeenCalledWith('mountains');
    });

    it('calls onSearch with debounced input', async () => {
      const mockDebounced = vi.fn();
      
      render(
        <SearchBar 
          onSearch={mockDebounced}
          isLoading={false}
          enableAutoSearch={true}
          debounceMs={300}
        />
      );

      const searchInput = screen.getByRole('searchbox');
      
      await user.type(searchInput, 'nature');
      
      // Should not call immediately
      expect(mockDebounced).not.toHaveBeenCalled();
      
      // Should call after debounce
      await waitFor(() => {
        expect(mockDebounced).toHaveBeenCalledWith('nature');
      }, { timeout: 500 });
    });

    it('disables search button when loading', () => {
      render(
        <SearchBar 
          onSearch={mockOnSearch}
          isLoading={true}
        />
      );

      const searchButton = screen.getByRole('button', { name: /search/i });
      expect(searchButton).toBeDisabled();
    });

    it('shows loading spinner when searching', () => {
      render(
        <SearchBar 
          onSearch={mockOnSearch}
          isLoading={true}
        />
      );

      expect(screen.getByTestId('search-loading')).toBeInTheDocument();
    });

    it('handles empty search query', async () => {
      render(
        <SearchBar 
          onSearch={mockOnSearch}
          isLoading={false}
        />
      );

      const searchButton = screen.getByRole('button', { name: /search/i });
      await user.click(searchButton);

      expect(mockOnSearch).not.toHaveBeenCalled();
    });

    it('handles keyboard shortcuts', async () => {
      render(
        <SearchBar 
          onSearch={mockOnSearch}
          isLoading={false}
        />
      );

      const searchInput = screen.getByRole('searchbox');
      
      await user.type(searchInput, 'flowers');
      await user.keyboard('{Enter}');

      expect(mockOnSearch).toHaveBeenCalledWith('flowers');
    });

    it('clears search input when clear button is clicked', async () => {
      render(
        <SearchBar 
          onSearch={mockOnSearch}
          isLoading={false}
          showClearButton={true}
        />
      );

      const searchInput = screen.getByRole('searchbox');
      
      await user.type(searchInput, 'test query');
      
      const clearButton = screen.getByRole('button', { name: /clear/i });
      await user.click(clearButton);

      expect(searchInput).toHaveValue('');
    });
  });

  describe('ImageCard', () => {
    const mockImage = createMockPhoto();
    const mockOnSelect = vi.fn();

    beforeEach(() => {
      mockOnSelect.mockClear();
    });

    it('renders image with proper attributes', () => {
      render(
        <ImageCard 
          image={mockImage}
          onSelect={mockOnSelect}
        />
      );

      const img = screen.getByRole('img');
      expect(img).toHaveAttribute('src', mockImage.urls.small);
      expect(img).toHaveAttribute('alt', mockImage.alt_description);
    });

    it('calls onSelect when clicked', async () => {
      const user = userEvent.setup();
      
      render(
        <ImageCard 
          image={mockImage}
          onSelect={mockOnSelect}
        />
      );

      const card = screen.getByTestId('image-card');
      await user.click(card);

      expect(mockOnSelect).toHaveBeenCalledWith(mockImage);
    });

    it('shows loading state while image loads', () => {
      render(
        <ImageCard 
          image={mockImage}
          onSelect={mockOnSelect}
          loading={true}
        />
      );

      expect(screen.getByTestId('image-loading')).toBeInTheDocument();
    });

    it('handles image load error gracefully', async () => {
      const brokenImage = { ...mockImage, urls: { ...mockImage.urls, small: 'invalid-url' }};
      
      render(
        <ImageCard 
          image={brokenImage}
          onSelect={mockOnSelect}
        />
      );

      const img = screen.getByRole('img');
      fireEvent.error(img);

      await waitFor(() => {
        expect(screen.getByTestId('image-error')).toBeInTheDocument();
      });
    });

    it('displays photographer attribution', () => {
      render(
        <ImageCard 
          image={mockImage}
          onSelect={mockOnSelect}
          showAttribution={true}
        />
      );

      expect(screen.getByText(mockImage.user.name)).toBeInTheDocument();
      expect(screen.getByText(`@${mockImage.user.username}`)).toBeInTheDocument();
    });

    it('supports keyboard navigation', async () => {
      const user = userEvent.setup();
      
      render(
        <ImageCard 
          image={mockImage}
          onSelect={mockOnSelect}
        />
      );

      const card = screen.getByTestId('image-card');
      await user.tab();
      expect(card).toHaveFocus();

      await user.keyboard('{Enter}');
      expect(mockOnSelect).toHaveBeenCalledWith(mockImage);
    });

    it('handles lazy loading with IntersectionObserver', async () => {
      const mockObserve = vi.fn();
      const mockUnobserve = vi.fn();
      
      // Mock IntersectionObserver
      global.IntersectionObserver = vi.fn().mockImplementation((callback) => ({
        observe: mockObserve,
        unobserve: mockUnobserve,
        disconnect: vi.fn(),
      }));

      render(
        <ImageCard 
          image={mockImage}
          onSelect={mockOnSelect}
          lazyLoad={true}
        />
      );

      expect(mockObserve).toHaveBeenCalled();
    });
  });

  describe('SearchResults', () => {
    const mockImages = Array.from({ length: 6 }, (_, i) => 
      createMockPhoto({ id: `image-${i}`, alt_description: `Test image ${i}` })
    );
    const mockOnImageSelect = vi.fn();
    const mockOnLoadMore = vi.fn();

    beforeEach(() => {
      mockOnImageSelect.mockClear();
      mockOnLoadMore.mockClear();
    });

    it('renders grid of images', () => {
      render(
        <SearchResults 
          images={mockImages}
          onImageSelect={mockOnImageSelect}
          loading={false}
        />
      );

      expect(screen.getAllByTestId('image-card')).toHaveLength(6);
    });

    it('shows loading state', () => {
      render(
        <SearchResults 
          images={[]}
          onImageSelect={mockOnImageSelect}
          loading={true}
        />
      );

      expect(screen.getByTestId('results-loading')).toBeInTheDocument();
    });

    it('shows empty state when no results', () => {
      render(
        <SearchResults 
          images={[]}
          onImageSelect={mockOnImageSelect}
          loading={false}
          query="nonexistent"
        />
      );

      expect(screen.getByTestId('empty-results')).toBeInTheDocument();
      expect(screen.getByText(/no images found/i)).toBeInTheDocument();
    });

    it('handles infinite scroll loading', async () => {
      render(
        <SearchResults 
          images={mockImages}
          onImageSelect={mockOnImageSelect}
          loading={false}
          hasMore={true}
          onLoadMore={mockOnLoadMore}
        />
      );

      // Simulate scrolling to bottom
      const loadMoreTrigger = screen.getByTestId('load-more-trigger');
      fireEvent.scroll(window, { target: { scrollY: 1000 } });

      await waitFor(() => {
        expect(mockOnLoadMore).toHaveBeenCalled();
      });
    });

    it('handles network errors gracefully', async () => {
      // Mock network error
      server.use(
        http.get('https://api.unsplash.com/search/photos', () => {
          return HttpResponse.error();
        })
      );

      render(
        <SearchResults 
          images={[]}
          onImageSelect={mockOnImageSelect}
          loading={false}
          error="Network error occurred"
        />
      );

      expect(screen.getByTestId('results-error')).toBeInTheDocument();
      expect(screen.getByText(/network error/i)).toBeInTheDocument();
    });

    it('supports grid layout customization', () => {
      render(
        <SearchResults 
          images={mockImages}
          onImageSelect={mockOnImageSelect}
          loading={false}
          columns={4}
          gap={16}
        />
      );

      const grid = screen.getByTestId('results-grid');
      expect(grid).toHaveStyle({
        'grid-template-columns': 'repeat(4, 1fr)',
        'gap': '16px'
      });
    });

    it('handles responsive layout', () => {
      // Mock window resize
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 768,
      });

      render(
        <SearchResults 
          images={mockImages}
          onImageSelect={mockOnImageSelect}
          loading={false}
          responsive={true}
        />
      );

      const grid = screen.getByTestId('results-grid');
      expect(grid).toHaveClass('responsive-grid');
    });

    it('handles performance optimization for large lists', async () => {
      const manyImages = Array.from({ length: 100 }, (_, i) => 
        createMockPhoto({ id: `image-${i}` })
      );

      const renderTime = await measurePerformance(async () => {
        render(
          <SearchResults 
            images={manyImages}
            onImageSelect={mockOnImageSelect}
            loading={false}
            virtualized={true}
          />
        );
      });

      // Should render within reasonable time (< 100ms for virtualized list)
      expect(renderTime).toBeLessThan(100);
    });
  });
});

// Helper function for performance measurement
async function measurePerformance(fn: () => Promise<void> | void): Promise<number> {
  const start = performance.now();
  await fn();
  const end = performance.now();
  return end - start;
}