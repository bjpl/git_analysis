/**
 * Accessibility utilities for VocabLens PWA
 * Provides helper functions for ARIA attributes, keyboard navigation, and screen reader support
 */

/**
 * Generates unique IDs for ARIA relationships
 */
export function generateId(prefix: string = 'vocablens'): string {
  return `${prefix}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Manages focus within a container (focus trapping)
 */
export class FocusManager {
  private container: HTMLElement;
  private focusableElements: HTMLElement[];
  private firstFocusable: HTMLElement | null = null;
  private lastFocusable: HTMLElement | null = null;
  private previousFocus: HTMLElement | null = null;

  constructor(container: HTMLElement) {
    this.container = container;
    this.updateFocusableElements();
  }

  private updateFocusableElements() {
    const focusableSelectors = [
      'button:not([disabled])',
      'input:not([disabled])',
      'select:not([disabled])',
      'textarea:not([disabled])',
      'a[href]',
      '[tabindex]:not([tabindex="-1"])',
      '[contenteditable="true"]'
    ].join(',');

    this.focusableElements = Array.from(
      this.container.querySelectorAll<HTMLElement>(focusableSelectors)
    ).filter(element => this.isVisible(element));

    this.firstFocusable = this.focusableElements[0] || null;
    this.lastFocusable = this.focusableElements[this.focusableElements.length - 1] || null;
  }

  private isVisible(element: HTMLElement): boolean {
    const style = window.getComputedStyle(element);
    return (
      style.display !== 'none' &&
      style.visibility !== 'hidden' &&
      element.offsetWidth > 0 &&
      element.offsetHeight > 0
    );
  }

  /**
   * Traps focus within the container
   */
  trapFocus() {
    this.previousFocus = document.activeElement as HTMLElement;
    this.container.addEventListener('keydown', this.handleKeyDown);
    
    // Focus the first focusable element
    if (this.firstFocusable) {
      this.firstFocusable.focus();
    }
  }

  /**
   * Releases focus trap and restores previous focus
   */
  releaseFocus() {
    this.container.removeEventListener('keydown', this.handleKeyDown);
    
    if (this.previousFocus) {
      this.previousFocus.focus();
    }
  }

  private handleKeyDown = (event: KeyboardEvent) => {
    if (event.key !== 'Tab') return;

    this.updateFocusableElements();

    if (event.shiftKey) {
      // Shift + Tab (moving backwards)
      if (document.activeElement === this.firstFocusable && this.lastFocusable) {
        event.preventDefault();
        this.lastFocusable.focus();
      }
    } else {
      // Tab (moving forwards)
      if (document.activeElement === this.lastFocusable && this.firstFocusable) {
        event.preventDefault();
        this.firstFocusable.focus();
      }
    }
  };
}

/**
 * Announces messages to screen readers
 */
export class ScreenReaderAnnouncer {
  private static instance: ScreenReaderAnnouncer;
  private liveRegion: HTMLElement;

  private constructor() {
    this.liveRegion = this.createLiveRegion();
  }

  static getInstance(): ScreenReaderAnnouncer {
    if (!ScreenReaderAnnouncer.instance) {
      ScreenReaderAnnouncer.instance = new ScreenReaderAnnouncer();
    }
    return ScreenReaderAnnouncer.instance;
  }

  private createLiveRegion(): HTMLElement {
    const existing = document.getElementById('vocablens-live-region');
    if (existing) {
      return existing;
    }

    const liveRegion = document.createElement('div');
    liveRegion.id = 'vocablens-live-region';
    liveRegion.setAttribute('aria-live', 'polite');
    liveRegion.setAttribute('aria-atomic', 'true');
    liveRegion.style.position = 'absolute';
    liveRegion.style.left = '-10000px';
    liveRegion.style.width = '1px';
    liveRegion.style.height = '1px';
    liveRegion.style.overflow = 'hidden';
    
    document.body.appendChild(liveRegion);
    return liveRegion;
  }

  /**
   * Announces a message to screen readers
   */
  announce(message: string, priority: 'polite' | 'assertive' = 'polite') {
    this.liveRegion.setAttribute('aria-live', priority);
    
    // Clear and set the message
    this.liveRegion.textContent = '';
    setTimeout(() => {
      this.liveRegion.textContent = message;
    }, 10);
  }

  /**
   * Announces status updates (loading, success, error)
   */
  announceStatus(status: string, type: 'loading' | 'success' | 'error' | 'info' = 'info') {
    const prefixes = {
      loading: 'Loading:',
      success: 'Success:',
      error: 'Error:',
      info: 'Information:'
    };
    
    const priority = type === 'error' ? 'assertive' : 'polite';
    this.announce(`${prefixes[type]} ${status}`, priority);
  }
}

/**
 * Keyboard navigation utilities
 */
export class KeyboardNavigation {
  /**
   * Creates arrow key navigation for a list of elements
   */
  static createArrowNavigation(
    container: HTMLElement,
    itemSelector: string,
    options: {
      wrap?: boolean;
      orientation?: 'vertical' | 'horizontal' | 'both';
      onActivate?: (element: HTMLElement) => void;
    } = {}
  ) {
    const { wrap = true, orientation = 'vertical', onActivate } = options;
    
    const handleKeyDown = (event: KeyboardEvent) => {
      const items = Array.from(container.querySelectorAll<HTMLElement>(itemSelector));
      const currentIndex = items.findIndex(item => item === document.activeElement);
      
      if (currentIndex === -1) return;
      
      let nextIndex = currentIndex;
      
      switch (event.key) {
        case 'ArrowUp':
          if (orientation === 'vertical' || orientation === 'both') {
            event.preventDefault();
            nextIndex = wrap && currentIndex === 0 ? items.length - 1 : Math.max(0, currentIndex - 1);
          }
          break;
          
        case 'ArrowDown':
          if (orientation === 'vertical' || orientation === 'both') {
            event.preventDefault();
            nextIndex = wrap && currentIndex === items.length - 1 ? 0 : Math.min(items.length - 1, currentIndex + 1);
          }
          break;
          
        case 'ArrowLeft':
          if (orientation === 'horizontal' || orientation === 'both') {
            event.preventDefault();
            nextIndex = wrap && currentIndex === 0 ? items.length - 1 : Math.max(0, currentIndex - 1);
          }
          break;
          
        case 'ArrowRight':
          if (orientation === 'horizontal' || orientation === 'both') {
            event.preventDefault();
            nextIndex = wrap && currentIndex === items.length - 1 ? 0 : Math.min(items.length - 1, currentIndex + 1);
          }
          break;
          
        case 'Home':
          event.preventDefault();
          nextIndex = 0;
          break;
          
        case 'End':
          event.preventDefault();
          nextIndex = items.length - 1;
          break;
          
        case 'Enter':
        case ' ':
          event.preventDefault();
          if (onActivate) {
            onActivate(items[currentIndex]);
          }
          return;
      }
      
      if (nextIndex !== currentIndex && items[nextIndex]) {
        items[nextIndex].focus();
      }
    };
    
    container.addEventListener('keydown', handleKeyDown);
    
    return () => {
      container.removeEventListener('keydown', handleKeyDown);
    };
  }
}

/**
 * ARIA label and description utilities
 */
export const aria = {
  /**
   * Creates ARIA attributes for form controls
   */
  formControl: (
    id: string,
    options: {
      label?: string;
      description?: string;
      error?: string;
      required?: boolean;
    } = {}
  ) => {
    const { label, description, error, required } = options;
    const attrs: Record<string, string> = {
      id,
    };
    
    if (required) {
      attrs['aria-required'] = 'true';
    }
    
    if (error) {
      attrs['aria-invalid'] = 'true';
      attrs['aria-describedby'] = `${id}-error`;
    } else if (description) {
      attrs['aria-describedby'] = `${id}-description`;
    }
    
    if (label) {
      attrs['aria-label'] = label;
    }
    
    return attrs;
  },

  /**
   * Creates ARIA attributes for buttons
   */
  button: (
    options: {
      label?: string;
      pressed?: boolean;
      expanded?: boolean;
      controls?: string;
      describedBy?: string;
    } = {}
  ) => {
    const { label, pressed, expanded, controls, describedBy } = options;
    const attrs: Record<string, string> = {};
    
    if (label) {
      attrs['aria-label'] = label;
    }
    
    if (typeof pressed === 'boolean') {
      attrs['aria-pressed'] = pressed.toString();
    }
    
    if (typeof expanded === 'boolean') {
      attrs['aria-expanded'] = expanded.toString();
    }
    
    if (controls) {
      attrs['aria-controls'] = controls;
    }
    
    if (describedBy) {
      attrs['aria-describedby'] = describedBy;
    }
    
    return attrs;
  },

  /**
   * Creates ARIA attributes for dialogs
   */
  dialog: (
    options: {
      labelledBy?: string;
      describedBy?: string;
      modal?: boolean;
    } = {}
  ) => {
    const { labelledBy, describedBy, modal = true } = options;
    const attrs: Record<string, string> = {
      role: 'dialog',
      'aria-modal': modal.toString(),
    };
    
    if (labelledBy) {
      attrs['aria-labelledby'] = labelledBy;
    }
    
    if (describedBy) {
      attrs['aria-describedby'] = describedBy;
    }
    
    return attrs;
  },

  /**
   * Creates ARIA attributes for lists and list items
   */
  list: (
    options: {
      label?: string;
      multiselectable?: boolean;
      orientation?: 'vertical' | 'horizontal';
    } = {}
  ) => {
    const { label, multiselectable, orientation = 'vertical' } = options;
    const attrs: Record<string, string> = {
      role: 'list',
    };
    
    if (label) {
      attrs['aria-label'] = label;
    }
    
    if (typeof multiselectable === 'boolean') {
      attrs['aria-multiselectable'] = multiselectable.toString();
    }
    
    if (orientation) {
      attrs['aria-orientation'] = orientation;
    }
    
    return attrs;
  },
};

/**
 * Color contrast utilities
 */
export const colorContrast = {
  /**
   * Calculates relative luminance of a color
   */
  getLuminance(color: string): number {
    // Convert hex to RGB
    const hex = color.replace('#', '');
    const r = parseInt(hex.substr(0, 2), 16) / 255;
    const g = parseInt(hex.substr(2, 2), 16) / 255;
    const b = parseInt(hex.substr(4, 2), 16) / 255;
    
    // Apply gamma correction
    const rs = r <= 0.03928 ? r / 12.92 : Math.pow((r + 0.055) / 1.055, 2.4);
    const gs = g <= 0.03928 ? g / 12.92 : Math.pow((g + 0.055) / 1.055, 2.4);
    const bs = b <= 0.03928 ? b / 12.92 : Math.pow((b + 0.055) / 1.055, 2.4);
    
    return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
  },

  /**
   * Calculates contrast ratio between two colors
   */
  getContrastRatio(color1: string, color2: string): number {
    const lum1 = this.getLuminance(color1);
    const lum2 = this.getLuminance(color2);
    const brightest = Math.max(lum1, lum2);
    const darkest = Math.min(lum1, lum2);
    
    return (brightest + 0.05) / (darkest + 0.05);
  },

  /**
   * Checks if colors meet WCAG contrast requirements
   */
  meetsWCAG(color1: string, color2: string, level: 'AA' | 'AAA' = 'AA'): boolean {
    const ratio = this.getContrastRatio(color1, color2);
    return level === 'AA' ? ratio >= 4.5 : ratio >= 7;
  },
};

/**
 * Reduced motion utilities
 */
export const reducedMotion = {
  /**
   * Checks if user prefers reduced motion
   */
  prefersReduced(): boolean {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  },

  /**
   * Returns appropriate animation duration based on user preference
   */
  duration(normal: number, reduced: number = 0): number {
    return this.prefersReduced() ? reduced : normal;
  },

  /**
   * Returns CSS class for animations based on user preference
   */
  cssClass(normalClass: string, reducedClass: string = ''): string {
    return this.prefersReduced() ? reducedClass : normalClass;
  },
};

// Export singleton instances
export const announcer = ScreenReaderAnnouncer.getInstance();
export const navigation = KeyboardNavigation;