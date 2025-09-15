/**
 * MenuAnimations.ts - Animation system for interactive menus
 * Features: Smooth transitions, entrance/exit effects, typewriter, parallax
 */

import { MenuAnimation, MenuTransition } from './types.js';

export interface AnimationOptions {
  duration?: number;
  easing?: string;
  delay?: number;
  direction?: 'up' | 'down' | 'left' | 'right';
  stagger?: number;
  fillMode?: 'none' | 'forwards' | 'backwards' | 'both';
}

export interface KeyframeDefinition {
  [key: string]: string | number;
}

export interface AnimationSequence {
  element: HTMLElement;
  keyframes: KeyframeDefinition[];
  options: KeyframeAnimationOptions;
}

export class MenuAnimations {
  private activeAnimations: Map<string, Animation> = new Map();
  private animationQueue: Array<() => Promise<void>> = [];
  private isProcessingQueue: boolean = false;
  private globalAnimationsEnabled: boolean = true;
  private performanceMode: 'smooth' | 'performance' | 'reduced-motion' = 'smooth';
  private defaultDuration: number = 300;
  private defaultEasing: string = 'cubic-bezier(0.4, 0, 0.2, 1)';
  
  constructor() {
    this.detectMotionPreferences();
    this.setupPerformanceObserver();
  }
  
  // ================================
  // Core Animation Methods
  // ================================
  
  public async animateElement(
    element: HTMLElement,
    keyframes: KeyframeDefinition[],
    options: AnimationOptions = {}
  ): Promise<void> {
    if (!this.globalAnimationsEnabled || this.performanceMode === 'reduced-motion') {
      return Promise.resolve();
    }
    
    const animationId = this.generateAnimationId(element);
    
    // Cancel any existing animation on this element
    this.cancelAnimation(animationId);
    
    const animationOptions: KeyframeAnimationOptions = {
      duration: options.duration || this.defaultDuration,
      easing: options.easing || this.defaultEasing,
      delay: options.delay || 0,
      fill: options.fillMode || 'forwards'
    };
    
    try {
      const animation = element.animate(keyframes, animationOptions);
      this.activeAnimations.set(animationId, animation);
      
      await animation.finished;
      this.activeAnimations.delete(animationId);
    } catch (error) {
      console.warn('Animation failed:', error);
      this.activeAnimations.delete(animationId);
    }
  }
  
  public async animateSequence(sequences: AnimationSequence[]): Promise<void> {
    const promises = sequences.map(seq => 
      this.animateElement(seq.element, seq.keyframes, seq.options)
    );
    
    await Promise.all(promises);
  }
  
  public async animateStaggered(
    elements: HTMLElement[],
    keyframes: KeyframeDefinition[],
    options: AnimationOptions = {}
  ): Promise<void> {
    const staggerDelay = options.stagger || 50;
    
    const promises = elements.map((element, index) => {
      const elementOptions = {
        ...options,
        delay: (options.delay || 0) + (index * staggerDelay)
      };
      
      return this.animateElement(element, keyframes, elementOptions);
    });
    
    await Promise.all(promises);
  }
  
  // ================================
  // Menu-specific Animations
  // ================================
  
  public async animateItemEntrance(
    element: HTMLElement,
    delay: number = 0,
    direction: 'up' | 'down' | 'left' | 'right' = 'up'
  ): Promise<void> {
    const keyframes = this.getEntranceKeyframes(direction);
    
    await this.animateElement(element, keyframes, {
      duration: 400,
      delay,
      easing: 'cubic-bezier(0.34, 1.56, 0.64, 1)' // Spring-like easing
    });
  }
  
  public async animateItemExit(
    element: HTMLElement,
    direction: 'up' | 'down' | 'left' | 'right' = 'down'
  ): Promise<void> {
    const keyframes = this.getExitKeyframes(direction);
    
    await this.animateElement(element, keyframes, {
      duration: 250,
      easing: 'cubic-bezier(0.55, 0, 0.55, 0.2)'
    });
  }
  
  public async animateMenuTransition(
    exitingMenu: HTMLElement,
    enteringMenu: HTMLElement,
    direction: 'forward' | 'backward' = 'forward'
  ): Promise<void> {
    const exitDirection = direction === 'forward' ? 'left' : 'right';
    const enterDirection = direction === 'forward' ? 'right' : 'left';
    
    // Animate both menus simultaneously
    await Promise.all([
      this.animateItemExit(exitingMenu, exitDirection),
      this.animateItemEntrance(enteringMenu, 100, enterDirection)
    ]);
  }
  
  public async animateHover(element: HTMLElement): Promise<void> {
    const keyframes = [
      { transform: 'scale(1) translateX(0)' },
      { transform: 'scale(1.02) translateX(4px)' }
    ];
    
    await this.animateElement(element, keyframes, {
      duration: 150,
      easing: 'ease-out'
    });
  }
  
  public async animateUnhover(element: HTMLElement): Promise<void> {
    const keyframes = [
      { transform: 'scale(1.02) translateX(4px)' },
      { transform: 'scale(1) translateX(0)' }
    ];
    
    await this.animateElement(element, keyframes, {
      duration: 150,
      easing: 'ease-out'
    });
  }
  
  public async animateSelection(element: HTMLElement): Promise<void> {
    // Pulse effect for selection
    const keyframes = [
      { transform: 'scale(1)', backgroundColor: 'var(--selected-bg, #eff6ff)' },
      { transform: 'scale(1.05)', backgroundColor: 'var(--selected-bg-active, #dbeafe)' },
      { transform: 'scale(1)', backgroundColor: 'var(--selected-bg, #eff6ff)' }
    ];
    
    await this.animateElement(element, keyframes, {
      duration: 300,
      easing: 'ease-out'
    });
  }
  
  // ================================
  // Loading and Feedback Animations
  // ================================
  
  public async animateLoading(element: HTMLElement): Promise<Animation> {
    const keyframes = [
      { opacity: '0.5' },
      { opacity: '1' },
      { opacity: '0.5' }
    ];
    
    const animation = element.animate(keyframes, {
      duration: 1500,
      iterations: Infinity,
      easing: 'ease-in-out'
    });
    
    const animationId = this.generateAnimationId(element) + '-loading';
    this.activeAnimations.set(animationId, animation);
    
    return animation;
  }
  
  public async animateSuccess(element: HTMLElement): Promise<void> {
    // Green flash effect
    const keyframes = [
      { backgroundColor: 'transparent' },
      { backgroundColor: 'var(--success-color, #10b981)' },
      { backgroundColor: 'transparent' }
    ];
    
    await this.animateElement(element, keyframes, {
      duration: 600,
      easing: 'ease-out'
    });
  }
  
  public async animateError(element: HTMLElement): Promise<void> {
    // Shake and red flash effect
    const shakeKeyframes = [
      { transform: 'translateX(0)' },
      { transform: 'translateX(-5px)' },
      { transform: 'translateX(5px)' },
      { transform: 'translateX(-3px)' },
      { transform: 'translateX(3px)' },
      { transform: 'translateX(0)' }
    ];
    
    const colorKeyframes = [
      { backgroundColor: 'transparent' },
      { backgroundColor: 'var(--error-color, #ef4444)' },
      { backgroundColor: 'transparent' }
    ];
    
    await Promise.all([
      this.animateElement(element, shakeKeyframes, {
        duration: 400,
        easing: 'ease-out'
      }),
      this.animateElement(element, colorKeyframes, {
        duration: 600,
        easing: 'ease-out'
      })
    ]);
  }
  
  // ================================
  // Text and Typewriter Effects
  // ================================
  
  public async animateTypewriter(
    element: HTMLElement,
    text: string,
    options: { speed?: number; cursor?: boolean } = {}
  ): Promise<void> {
    const speed = options.speed || 50;
    const showCursor = options.cursor !== false;
    
    element.textContent = '';
    
    // Add cursor
    if (showCursor) {
      const cursor = document.createElement('span');
      cursor.textContent = '|';
      cursor.style.animation = 'blink 1s infinite';
      element.appendChild(cursor);
    }
    
    // Type characters one by one
    for (let i = 0; i < text.length; i++) {
      await new Promise(resolve => setTimeout(resolve, speed));
      
      if (showCursor) {
        element.firstChild!.textContent = text.substring(0, i + 1);
      } else {
        element.textContent = text.substring(0, i + 1);
      }
    }
    
    // Remove cursor after a delay
    if (showCursor) {
      setTimeout(() => {
        const cursor = element.querySelector('span');
        if (cursor) {
          cursor.remove();
        }
      }, 1000);
    }
  }
  
  public async animateTextHighlight(
    element: HTMLElement,
    searchTerm: string
  ): Promise<void> {
    const text = element.textContent || '';
    const regex = new RegExp(`(${searchTerm})`, 'gi');
    
    const highlightedHTML = text.replace(regex, '<mark class="search-highlight">$1</mark>');
    element.innerHTML = highlightedHTML;
    
    // Animate the highlights
    const highlights = element.querySelectorAll('.search-highlight');
    
    const keyframes = [
      { backgroundColor: 'transparent' },
      { backgroundColor: 'var(--highlight-color, #fef3c7)' },
      { backgroundColor: 'var(--highlight-color-active, #fde047)' }
    ];
    
    const promises = Array.from(highlights).map((highlight, index) => 
      this.animateElement(highlight as HTMLElement, keyframes, {
        duration: 400,
        delay: index * 50,
        easing: 'ease-out'
      })
    );
    
    await Promise.all(promises);
  }
  
  // ================================
  // Parallax and Scroll Effects
  // ================================
  
  public setupParallaxScrolling(
    container: HTMLElement,
    intensity: number = 0.5
  ): () => void {
    let ticking = false;
    
    const updateParallax = () => {
      const scrollTop = container.scrollTop;
      const items = container.querySelectorAll('.menu-item');
      
      items.forEach((item, index) => {
        const element = item as HTMLElement;
        const offset = scrollTop * intensity * (index % 3 + 1) * 0.1;
        element.style.transform = `translateY(${offset}px)`;
      });
      
      ticking = false;
    };
    
    const onScroll = () => {
      if (!ticking) {
        requestAnimationFrame(updateParallax);
        ticking = true;
      }
    };
    
    container.addEventListener('scroll', onScroll, { passive: true });
    
    // Return cleanup function
    return () => {
      container.removeEventListener('scroll', onScroll);
    };
  }
  
  public async animateSmoothScroll(
    container: HTMLElement,
    targetY: number,
    duration: number = 500
  ): Promise<void> {
    const startY = container.scrollTop;
    const distance = targetY - startY;
    
    const keyframes = [
      { scrollTop: `${startY}px` },
      { scrollTop: `${targetY}px` }
    ];
    
    await this.animateElement(container, keyframes, {
      duration,
      easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)'
    });
  }
  
  // ================================
  // Advanced Effects
  // ================================
  
  public async animateRippleEffect(
    element: HTMLElement,
    x: number,
    y: number
  ): Promise<void> {
    const ripple = document.createElement('div');
    ripple.className = 'ripple-effect';
    
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    
    ripple.style.width = ripple.style.height = `${size}px`;
    ripple.style.left = `${x - size / 2}px`;
    ripple.style.top = `${y - size / 2}px`;
    ripple.style.position = 'absolute';
    ripple.style.borderRadius = '50%';
    ripple.style.backgroundColor = 'rgba(255, 255, 255, 0.3)';
    ripple.style.pointerEvents = 'none';
    ripple.style.transform = 'scale(0)';
    
    element.style.position = 'relative';
    element.style.overflow = 'hidden';
    element.appendChild(ripple);
    
    const keyframes = [
      { transform: 'scale(0)', opacity: '1' },
      { transform: 'scale(1)', opacity: '0' }
    ];
    
    await this.animateElement(ripple, keyframes, {
      duration: 600,
      easing: 'ease-out'
    });
    
    ripple.remove();
  }
  
  public async animateGlow(element: HTMLElement): Promise<void> {
    const keyframes = [
      { boxShadow: '0 0 5px rgba(59, 130, 246, 0)' },
      { boxShadow: '0 0 20px rgba(59, 130, 246, 0.8)' },
      { boxShadow: '0 0 5px rgba(59, 130, 246, 0)' }
    ];
    
    await this.animateElement(element, keyframes, {
      duration: 1000,
      easing: 'ease-in-out'
    });
  }
  
  // ================================
  // Animation Utilities
  // ================================
  
  private getEntranceKeyframes(direction: 'up' | 'down' | 'left' | 'right'): KeyframeDefinition[] {
    const transforms = {
      up: 'translateY(20px)',
      down: 'translateY(-20px)',
      left: 'translateX(20px)',
      right: 'translateX(-20px)'
    };
    
    return [
      { 
        opacity: '0', 
        transform: `${transforms[direction]} scale(0.9)` 
      },
      { 
        opacity: '1', 
        transform: 'translateY(0) translateX(0) scale(1)' 
      }
    ];
  }
  
  private getExitKeyframes(direction: 'up' | 'down' | 'left' | 'right'): KeyframeDefinition[] {
    const transforms = {
      up: 'translateY(-20px)',
      down: 'translateY(20px)',
      left: 'translateX(-20px)',
      right: 'translateX(20px)'
    };
    
    return [
      { 
        opacity: '1', 
        transform: 'translateY(0) translateX(0) scale(1)' 
      },
      { 
        opacity: '0', 
        transform: `${transforms[direction]} scale(0.9)` 
      }
    ];
  }
  
  private generateAnimationId(element: HTMLElement): string {
    return `anim-${element.getAttribute('data-item-id') || Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
  
  // ================================
  // Animation Control
  // ================================
  
  public cancelAnimation(animationId: string): void {
    const animation = this.activeAnimations.get(animationId);
    if (animation) {
      animation.cancel();
      this.activeAnimations.delete(animationId);
    }
  }
  
  public cancelAllAnimations(): void {
    for (const [id, animation] of this.activeAnimations) {
      animation.cancel();
    }
    this.activeAnimations.clear();
  }
  
  public pauseAllAnimations(): void {
    for (const animation of this.activeAnimations.values()) {
      animation.pause();
    }
  }
  
  public resumeAllAnimations(): void {
    for (const animation of this.activeAnimations.values()) {
      animation.play();
    }
  }
  
  // ================================
  // Performance and Accessibility
  // ================================
  
  private detectMotionPreferences(): void {
    if (typeof window !== 'undefined' && window.matchMedia) {
      const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
      
      if (mediaQuery.matches) {
        this.performanceMode = 'reduced-motion';
        this.globalAnimationsEnabled = false;
      }
      
      mediaQuery.addEventListener('change', (e) => {
        if (e.matches) {
          this.performanceMode = 'reduced-motion';
          this.setAnimationsEnabled(false);
        } else {
          this.performanceMode = 'smooth';
          this.setAnimationsEnabled(true);
        }
      });
    }
  }
  
  private setupPerformanceObserver(): void {
    if (typeof PerformanceObserver !== 'undefined') {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        
        for (const entry of entries) {
          // If frame rate drops below 45fps, switch to performance mode
          if (entry.name === 'frame' && (entry as any).duration > 22) {
            this.performanceMode = 'performance';
            this.defaultDuration = Math.max(this.defaultDuration * 0.7, 150);
          }
        }
      });
      
      observer.observe({ entryTypes: ['measure'] });
    }
  }
  
  public setAnimationsEnabled(enabled: boolean): void {
    this.globalAnimationsEnabled = enabled;
    
    if (!enabled) {
      this.cancelAllAnimations();
    }
  }
  
  public setPerformanceMode(mode: 'smooth' | 'performance' | 'reduced-motion'): void {
    this.performanceMode = mode;
    
    switch (mode) {
      case 'smooth':
        this.defaultDuration = 300;
        this.setAnimationsEnabled(true);
        break;
      case 'performance':
        this.defaultDuration = 150;
        this.setAnimationsEnabled(true);
        break;
      case 'reduced-motion':
        this.setAnimationsEnabled(false);
        break;
    }
  }
  
  // ================================
  // CSS Keyframes Registration
  // ================================
  
  public registerCSSAnimations(): void {
    const style = document.createElement('style');
    style.textContent = `
      @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0; }
      }
      
      @keyframes menuFadeIn {
        from {
          opacity: 0;
          transform: translateY(10px) scale(0.95);
        }
        to {
          opacity: 1;
          transform: translateY(0) scale(1);
        }
      }
      
      @keyframes menuFadeOut {
        from {
          opacity: 1;
          transform: translateY(0) scale(1);
        }
        to {
          opacity: 0;
          transform: translateY(-10px) scale(0.95);
        }
      }
      
      @keyframes menuSlideIn {
        from {
          transform: translateX(100%);
        }
        to {
          transform: translateX(0);
        }
      }
      
      @keyframes menuSlideOut {
        from {
          transform: translateX(0);
        }
        to {
          transform: translateX(-100%);
        }
      }
      
      .search-highlight {
        padding: 0 2px;
        border-radius: 2px;
        transition: all 0.2s ease;
      }
      
      .menu-item {
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
      }
      
      @media (prefers-reduced-motion: reduce) {
        .menu-item,
        .search-highlight {
          transition: none !important;
          animation: none !important;
        }
      }
    `;
    
    document.head.appendChild(style);
  }
  
  // ================================
  // Cleanup
  // ================================
  
  public destroy(): void {
    this.cancelAllAnimations();
    this.animationQueue = [];
    this.isProcessingQueue = false;
  }
  
  // ================================
  // Debug and Metrics
  // ================================
  
  public getMetrics(): any {
    return {
      activeAnimations: this.activeAnimations.size,
      queueLength: this.animationQueue.length,
      isProcessingQueue: this.isProcessingQueue,
      globalAnimationsEnabled: this.globalAnimationsEnabled,
      performanceMode: this.performanceMode,
      defaultDuration: this.defaultDuration
    };
  }
}

export default MenuAnimations;
