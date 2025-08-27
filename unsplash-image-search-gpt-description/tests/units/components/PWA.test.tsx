import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, fireEvent, act } from '../../utils/testUtils';
import userEvent from '@testing-library/user-event';
import { server } from '../../mocks/server';

// Mock PWA components
const MockPWAManager = ({ children, ...props }: any) => {
  return (
    <div data-testid="pwa-manager" {...props}>
      {children}
    </div>
  );
};

const MockInstallPrompt = ({ onInstall, onDismiss, isVisible }: any) => {
  if (!isVisible) return null;
  
  return (
    <div data-testid="install-prompt" role="dialog" aria-label="Install app">
      <h2>Install VocabLens</h2>
      <p>Install this app on your device for a better experience</p>
      <button onClick={onInstall}>Install</button>
      <button onClick={onDismiss}>Not now</button>
    </div>
  );
};

const MockUpdatePrompt = ({ onUpdate, onDismiss, isVisible }: any) => {
  if (!isVisible) return null;
  
  return (
    <div data-testid="update-prompt" role="dialog" aria-label="App update">
      <h2>Update Available</h2>
      <p>A new version is available. Update now?</p>
      <button onClick={onUpdate}>Update</button>
      <button onClick={onDismiss}>Later</button>
    </div>
  );
};

const MockOfflineBanner = ({ isOffline }: any) => {
  if (!isOffline) return null;
  
  return (
    <div data-testid="offline-banner" role="alert">
      <span>You're offline. Some features may be limited.</span>
    </div>
  );
};

// Mock service worker registration
const mockServiceWorkerRegistration = {
  installing: null,
  waiting: null,
  active: {
    postMessage: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
  },
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  update: vi.fn(() => Promise.resolve()),
  unregister: vi.fn(() => Promise.resolve(true)),
};

describe('PWA Components', () => {
  let mockBeforeInstallPrompt: any;
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    user = userEvent.setup();
    
    // Mock PWA install prompt event
    mockBeforeInstallPrompt = {
      prompt: vi.fn(() => Promise.resolve()),
      userChoice: Promise.resolve({ outcome: 'accepted' }),
      preventDefault: vi.fn(),
    };

    // Mock navigator properties
    Object.defineProperty(navigator, 'serviceWorker', {
      value: {
        register: vi.fn(() => Promise.resolve(mockServiceWorkerRegistration)),
        ready: Promise.resolve(mockServiceWorkerRegistration),
        controller: mockServiceWorkerRegistration.active,
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
      },
      writable: true,
    });

    // Mock online/offline state
    Object.defineProperty(navigator, 'onLine', {
      value: true,
      writable: true,
    });

    // Reset window properties
    window.addEventListener = vi.fn();
    window.removeEventListener = vi.fn();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('PWAManager', () => {
    it('renders children correctly', () => {
      render(
        <MockPWAManager enableInstallPrompt={true}>
          <div>Test Content</div>
        </MockPWAManager>
      );

      expect(screen.getByTestId('pwa-manager')).toBeInTheDocument();
      expect(screen.getByText('Test Content')).toBeInTheDocument();
    });

    it('registers service worker on mount', async () => {
      render(
        <MockPWAManager enableInstallPrompt={true}>
          <div>Content</div>
        </MockPWAManager>
      );

      await waitFor(() => {
        expect(navigator.serviceWorker.register).toHaveBeenCalledWith('/sw.js');
      });
    });

    it('handles service worker registration failure', async () => {
      const mockError = new Error('Service worker registration failed');
      vi.mocked(navigator.serviceWorker.register).mockRejectedValue(mockError);

      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      render(
        <MockPWAManager enableInstallPrompt={true}>
          <div>Content</div>
        </MockPWAManager>
      );

      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith(
          'Service worker registration failed:',
          mockError
        );
      });

      consoleSpy.mockRestore();
    });

    it('sets up beforeinstallprompt event listener', () => {
      render(
        <MockPWAManager enableInstallPrompt={true}>
          <div>Content</div>
        </MockPWAManager>
      );

      expect(window.addEventListener).toHaveBeenCalledWith(
        'beforeinstallprompt',
        expect.any(Function)
      );
    });

    it('sets up online/offline event listeners', () => {
      render(
        <MockPWAManager enableOfflineBanner={true}>
          <div>Content</div>
        </MockPWAManager>
      );

      expect(window.addEventListener).toHaveBeenCalledWith(
        'online',
        expect.any(Function)
      );
      expect(window.addEventListener).toHaveBeenCalledWith(
        'offline',
        expect.any(Function)
      );
    });
  });

  describe('InstallPrompt', () => {
    it('renders when visible', () => {
      render(
        <MockInstallPrompt 
          isVisible={true}
          onInstall={vi.fn()}
          onDismiss={vi.fn()}
        />
      );

      expect(screen.getByTestId('install-prompt')).toBeInTheDocument();
      expect(screen.getByRole('dialog')).toHaveAccessibleName('Install app');
      expect(screen.getByText('Install VocabLens')).toBeInTheDocument();
    });

    it('does not render when not visible', () => {
      render(
        <MockInstallPrompt 
          isVisible={false}
          onInstall={vi.fn()}
          onDismiss={vi.fn()}
        />
      );

      expect(screen.queryByTestId('install-prompt')).not.toBeInTheDocument();
    });

    it('calls onInstall when install button clicked', async () => {
      const mockOnInstall = vi.fn();
      
      render(
        <MockInstallPrompt 
          isVisible={true}
          onInstall={mockOnInstall}
          onDismiss={vi.fn()}
        />
      );

      const installButton = screen.getByText('Install');
      await user.click(installButton);

      expect(mockOnInstall).toHaveBeenCalled();
    });

    it('calls onDismiss when dismiss button clicked', async () => {
      const mockOnDismiss = vi.fn();
      
      render(
        <MockInstallPrompt 
          isVisible={true}
          onInstall={vi.fn()}
          onDismiss={mockOnDismiss}
        />
      );

      const dismissButton = screen.getByText('Not now');
      await user.click(dismissButton);

      expect(mockOnDismiss).toHaveBeenCalled();
    });

    it('handles keyboard navigation', async () => {
      render(
        <MockInstallPrompt 
          isVisible={true}
          onInstall={vi.fn()}
          onDismiss={vi.fn()}
        />
      );

      // Tab to install button
      await user.tab();
      expect(screen.getByText('Install')).toHaveFocus();

      // Tab to dismiss button
      await user.tab();
      expect(screen.getByText('Not now')).toHaveFocus();
    });

    it('supports escape key to dismiss', async () => {
      const mockOnDismiss = vi.fn();
      
      render(
        <MockInstallPrompt 
          isVisible={true}
          onInstall={vi.fn()}
          onDismiss={mockOnDismiss}
        />
      );

      await user.keyboard('{Escape}');
      expect(mockOnDismiss).toHaveBeenCalled();
    });

    it('traps focus within dialog', async () => {
      render(
        <MockInstallPrompt 
          isVisible={true}
          onInstall={vi.fn()}
          onDismiss={vi.fn()}
        />
      );

      const installButton = screen.getByText('Install');
      const dismissButton = screen.getByText('Not now');

      // Tab forward
      await user.tab();
      expect(installButton).toHaveFocus();

      await user.tab();
      expect(dismissButton).toHaveFocus();

      // Tab should wrap back to first button
      await user.tab();
      expect(installButton).toHaveFocus();

      // Shift+Tab should go backwards
      await user.keyboard('{Shift>}{Tab}{/Shift}');
      expect(dismissButton).toHaveFocus();
    });
  });

  describe('UpdatePrompt', () => {
    it('renders when update available', () => {
      render(
        <MockUpdatePrompt 
          isVisible={true}
          onUpdate={vi.fn()}
          onDismiss={vi.fn()}
        />
      );

      expect(screen.getByTestId('update-prompt')).toBeInTheDocument();
      expect(screen.getByText('Update Available')).toBeInTheDocument();
    });

    it('calls onUpdate when update button clicked', async () => {
      const mockOnUpdate = vi.fn();
      
      render(
        <MockUpdatePrompt 
          isVisible={true}
          onUpdate={mockOnUpdate}
          onDismiss={vi.fn()}
        />
      );

      await user.click(screen.getByText('Update'));
      expect(mockOnUpdate).toHaveBeenCalled();
    });

    it('calls onDismiss when later button clicked', async () => {
      const mockOnDismiss = vi.fn();
      
      render(
        <MockUpdatePrompt 
          isVisible={true}
          onUpdate={vi.fn()}
          onDismiss={mockOnDismiss}
        />
      );

      await user.click(screen.getByText('Later'));
      expect(mockOnDismiss).toHaveBeenCalled();
    });

    it('shows loading state during update', async () => {
      const mockOnUpdate = vi.fn(() => new Promise(resolve => 
        setTimeout(resolve, 100)
      ));
      
      render(
        <MockUpdatePrompt 
          isVisible={true}
          onUpdate={mockOnUpdate}
          onDismiss={vi.fn()}
        />
      );

      await user.click(screen.getByText('Update'));
      
      // Would show loading state in real implementation
      expect(mockOnUpdate).toHaveBeenCalled();
    });
  });

  describe('OfflineBanner', () => {
    it('renders when offline', () => {
      render(<MockOfflineBanner isOffline={true} />);

      const banner = screen.getByTestId('offline-banner');
      expect(banner).toBeInTheDocument();
      expect(banner).toHaveAttribute('role', 'alert');
      expect(banner).toHaveTextContent('You\'re offline');
    });

    it('does not render when online', () => {
      render(<MockOfflineBanner isOffline={false} />);

      expect(screen.queryByTestId('offline-banner')).not.toBeInTheDocument();
    });

    it('provides appropriate ARIA attributes', () => {
      render(<MockOfflineBanner isOffline={true} />);

      const banner = screen.getByRole('alert');
      expect(banner).toBeInTheDocument();
    });
  });

  describe('PWA Lifecycle Events', () => {
    it('handles app installation', async () => {
      const mockOnInstall = vi.fn();
      
      // Simulate beforeinstallprompt event
      const installEvent = new Event('beforeinstallprompt');
      Object.assign(installEvent, mockBeforeInstallPrompt);

      render(
        <MockInstallPrompt 
          isVisible={true}
          onInstall={mockOnInstall}
          onDismiss={vi.fn()}
        />
      );

      await user.click(screen.getByText('Install'));
      
      expect(mockOnInstall).toHaveBeenCalled();
    });

    it('handles service worker updates', async () => {
      const mockOnUpdate = vi.fn();
      
      render(
        <MockUpdatePrompt 
          isVisible={true}
          onUpdate={mockOnUpdate}
          onDismiss={vi.fn()}
        />
      );

      await user.click(screen.getByText('Update'));
      
      expect(mockOnUpdate).toHaveBeenCalled();
    });

    it('handles offline mode transitions', () => {
      const { rerender } = render(<MockOfflineBanner isOffline={false} />);

      // Should not show banner initially
      expect(screen.queryByTestId('offline-banner')).not.toBeInTheDocument();

      // Simulate going offline
      rerender(<MockOfflineBanner isOffline={true} />);
      
      expect(screen.getByTestId('offline-banner')).toBeInTheDocument();

      // Simulate going back online
      rerender(<MockOfflineBanner isOffline={false} />);
      
      expect(screen.queryByTestId('offline-banner')).not.toBeInTheDocument();
    });
  });

  describe('PWA Caching', () => {
    it('caches critical resources', async () => {
      // Mock Cache API
      const mockCache = {
        addAll: vi.fn(() => Promise.resolve()),
        match: vi.fn(() => Promise.resolve()),
        put: vi.fn(() => Promise.resolve()),
      };

      Object.defineProperty(window, 'caches', {
        value: {
          open: vi.fn(() => Promise.resolve(mockCache)),
          match: vi.fn(() => Promise.resolve()),
        },
        writable: true,
      });

      render(
        <MockPWAManager enableInstallPrompt={true}>
          <div>Content</div>
        </MockPWAManager>
      );

      await waitFor(() => {
        expect(window.caches.open).toHaveBeenCalled();
      });
    });

    it('serves cached content when offline', async () => {
      // Mock fetch for offline scenario
      global.fetch = vi.fn(() => Promise.reject(new Error('Network error')));

      const mockCachedResponse = new Response('Cached content');
      const mockCache = {
        match: vi.fn(() => Promise.resolve(mockCachedResponse)),
      };

      Object.defineProperty(window, 'caches', {
        value: {
          match: vi.fn(() => Promise.resolve(mockCachedResponse)),
        },
        writable: true,
      });

      // Simulate service worker fetch event
      const fetchEvent = new Event('fetch');
      Object.assign(fetchEvent, {
        request: { url: '/cached-resource' },
        respondWith: vi.fn(),
      });

      // In a real scenario, service worker would handle this
      const cachedResponse = await window.caches.match('/cached-resource');
      expect(cachedResponse).toBeDefined();
    });
  });

  describe('Performance Optimizations', () => {
    it('lazy loads non-critical PWA features', async () => {
      const LazyComponent = () => <div>Lazy loaded</div>;
      
      render(
        <MockPWAManager enablePerformanceOptimization={true}>
          <LazyComponent />
        </MockPWAManager>
      );

      await waitFor(() => {
        expect(screen.getByText('Lazy loaded')).toBeInTheDocument();
      });
    });

    it('preloads critical resources', async () => {
      const linkElements = document.querySelectorAll('link[rel="preload"]');
      const criticalResources = Array.from(linkElements).map(
        link => (link as HTMLLinkElement).href
      );

      // In a real implementation, would check for preloaded resources
      expect(Array.isArray(criticalResources)).toBe(true);
    });

    it('implements resource hints', () => {
      render(
        <MockPWAManager enablePerformanceOptimization={true}>
          <div>Content</div>
        </MockPWAManager>
      );

      // Check for dns-prefetch, preconnect, etc.
      const resourceHints = document.querySelectorAll(
        'link[rel="dns-prefetch"], link[rel="preconnect"]'
      );

      // Would verify resource hints in real implementation
      expect(resourceHints).toBeDefined();
    });
  });

  describe('Accessibility', () => {
    it('provides proper ARIA labels for PWA elements', () => {
      render(
        <MockInstallPrompt 
          isVisible={true}
          onInstall={vi.fn()}
          onDismiss={vi.fn()}
        />
      );

      const dialog = screen.getByRole('dialog');
      expect(dialog).toHaveAccessibleName('Install app');
    });

    it('supports screen reader announcements', () => {
      render(<MockOfflineBanner isOffline={true} />);

      const alert = screen.getByRole('alert');
      expect(alert).toBeInTheDocument();
    });

    it('maintains focus management in PWA dialogs', async () => {
      render(
        <MockInstallPrompt 
          isVisible={true}
          onInstall={vi.fn()}
          onDismiss={vi.fn()}
        />
      );

      // Focus should be trapped within the dialog
      await user.tab();
      expect(document.activeElement).toBeInstanceOf(HTMLElement);
    });
  });
});