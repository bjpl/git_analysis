import React, { useEffect, useRef, useState, useCallback, ReactNode } from 'react';
import { cn } from '@/utils/cn';

/**
 * Screen Reader Only Content
 * Content that is only visible to screen readers
 */
export function ScreenReaderOnly({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <span 
      className={cn(
        'sr-only',
        'absolute w-px h-px p-0 -m-px overflow-hidden whitespace-nowrap border-0',
        className
      )}
    >
      {children}
    </span>
  );
}

/**
 * Skip Link for keyboard navigation
 */
interface SkipLinkProps {
  href: string;
  children: ReactNode;
  className?: string;
}

export function SkipLink({ href, children, className }: SkipLinkProps) {
  return (
    <a
      href={href}
      className={cn(
        'skip-link',
        'absolute -top-10 left-4 z-tooltip',
        'px-4 py-2 bg-primary text-primary-foreground',
        'rounded-md text-sm font-medium',
        'focus:top-4 transition-all duration-200',
        'focus:outline-none focus:ring-2 focus:ring-ring',
        className
      )}
    >
      {children}
    </a>
  );
}

/**
 * Focus Manager Hook
 * Manages focus for accessibility
 */
export function useFocusManagement() {
  const previousFocus = useRef<HTMLElement | null>(null);

  const captureFocus = useCallback(() => {
    previousFocus.current = document.activeElement as HTMLElement;
  }, []);

  const restoreFocus = useCallback(() => {
    if (previousFocus.current) {
      previousFocus.current.focus();
      previousFocus.current = null;
    }
  }, []);

  const trapFocus = useCallback((container: HTMLElement) => {
    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    const firstFocusable = focusableElements[0] as HTMLElement;
    const lastFocusable = focusableElements[focusableElements.length - 1] as HTMLElement;

    const handleTabKey = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        if (document.activeElement === firstFocusable) {
          lastFocusable?.focus();
          e.preventDefault();
        }
      } else {
        if (document.activeElement === lastFocusable) {
          firstFocusable?.focus();
          e.preventDefault();
        }
      }
    };

    container.addEventListener('keydown', handleTabKey);
    firstFocusable?.focus();

    return () => {
      container.removeEventListener('keydown', handleTabKey);
    };
  }, []);

  return {
    captureFocus,
    restoreFocus,
    trapFocus,
  };
}

/**
 * Accessible Button with enhanced keyboard support
 */
interface AccessibleButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  loadingText?: string;
  children: ReactNode;
}

export function AccessibleButton({
  variant = 'primary',
  size = 'md',
  loading = false,
  loadingText,
  children,
  className,
  disabled,
  ...props
}: AccessibleButtonProps) {
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  const variantClasses = {
    primary: 'bg-primary text-primary-foreground hover:bg-primary/90',
    secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
    ghost: 'hover:bg-accent hover:text-accent-foreground',
    danger: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
  };

  return (
    <button
      className={cn(
        'inline-flex items-center justify-center gap-2',
        'rounded-md font-medium transition-colors',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
        'disabled:pointer-events-none disabled:opacity-50',
        'touch-target', // Minimum 44px touch target
        sizeClasses[size],
        variantClasses[variant],
        className
      )}
      disabled={disabled || loading}
      aria-disabled={disabled || loading}
      {...(loading && loadingText ? { 'aria-label': loadingText } : {})}
      {...props}
    >
      {loading && (
        <>
          <div 
            className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"
            aria-hidden="true"
          />
          <ScreenReaderOnly>Loading...</ScreenReaderOnly>
        </>
      )}
      {children}
    </button>
  );
}

/**
 * Accessible Form Field with proper labeling
 */
interface AccessibleFieldProps {
  id: string;
  label: string;
  description?: string;
  error?: string;
  required?: boolean;
  children: ReactNode;
  className?: string;
}

export function AccessibleField({
  id,
  label,
  description,
  error,
  required = false,
  children,
  className,
}: AccessibleFieldProps) {
  const descriptionId = description ? `${id}-description` : undefined;
  const errorId = error ? `${id}-error` : undefined;

  return (
    <div className={cn('space-y-2', className)}>
      <label 
        htmlFor={id}
        className="text-sm font-medium text-foreground block"
      >
        {label}
        {required && (
          <span className="text-destructive ml-1" aria-label="required">
            *
          </span>
        )}
      </label>
      
      {description && (
        <p 
          id={descriptionId}
          className="text-sm text-muted-foreground"
        >
          {description}
        </p>
      )}
      
      {React.cloneElement(children as React.ReactElement, {
        id,
        required,
        'aria-describedby': [descriptionId, errorId].filter(Boolean).join(' ') || undefined,
        'aria-invalid': error ? 'true' : undefined,
      })}
      
      {error && (
        <p 
          id={errorId}
          className="text-sm text-destructive"
          role="alert"
          aria-live="polite"
        >
          {error}
        </p>
      )}
    </div>
  );
}

/**
 * Accessible Input with enhanced validation
 */
interface AccessibleInputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'id'> {
  error?: string;
}

export const AccessibleInput = React.forwardRef<HTMLInputElement, AccessibleInputProps>(
  ({ error, className, ...props }, ref) => {
    return (
      <input
        ref={ref}
        className={cn(
          'flex h-10 w-full rounded-md border border-input bg-background',
          'px-3 py-2 text-sm ring-offset-background',
          'file:border-0 file:bg-transparent file:text-sm file:font-medium',
          'placeholder:text-muted-foreground',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
          'disabled:cursor-not-allowed disabled:opacity-50',
          error && 'border-destructive focus-visible:ring-destructive',
          className
        )}
        {...props}
      />
    );
  }
);

AccessibleInput.displayName = 'AccessibleInput';

/**
 * Live Region for dynamic content announcements
 */
interface LiveRegionProps {
  children: ReactNode;
  politeness?: 'polite' | 'assertive' | 'off';
  atomic?: boolean;
  relevant?: 'additions' | 'removals' | 'text' | 'all';
  className?: string;
}

export function LiveRegion({
  children,
  politeness = 'polite',
  atomic = false,
  relevant = 'additions text',
  className,
}: LiveRegionProps) {
  return (
    <div
      aria-live={politeness}
      aria-atomic={atomic}
      aria-relevant={relevant}
      className={cn('sr-only', className)}
    >
      {children}
    </div>
  );
}

/**
 * Accessible Disclosure/Collapsible content
 */
interface DisclosureProps {
  trigger: ReactNode;
  children: ReactNode;
  defaultOpen?: boolean;
  onToggle?: (open: boolean) => void;
  className?: string;
  triggerClassName?: string;
  contentClassName?: string;
}

export function Disclosure({
  trigger,
  children,
  defaultOpen = false,
  onToggle,
  className,
  triggerClassName,
  contentClassName,
}: DisclosureProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  const contentId = useRef(`disclosure-${Math.random().toString(36).substr(2, 9)}`).current;

  const handleToggle = () => {
    const newOpen = !isOpen;
    setIsOpen(newOpen);
    onToggle?.(newOpen);
  };

  return (
    <div className={className}>
      <button
        onClick={handleToggle}
        aria-expanded={isOpen}
        aria-controls={contentId}
        className={cn(
          'flex w-full items-center justify-between text-left',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
          triggerClassName
        )}
      >
        {trigger}
      </button>
      
      <div
        id={contentId}
        className={cn(
          'overflow-hidden transition-all duration-200',
          isOpen ? 'max-h-screen opacity-100' : 'max-h-0 opacity-0',
          contentClassName
        )}
        aria-hidden={!isOpen}
      >
        {children}
      </div>
    </div>
  );
}

/**
 * Progress Indicator with accessibility support
 */
interface ProgressProps {
  value: number;
  max?: number;
  label?: string;
  description?: string;
  showValue?: boolean;
  className?: string;
}

export function Progress({
  value,
  max = 100,
  label,
  description,
  showValue = false,
  className,
}: ProgressProps) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);
  const progressId = useRef(`progress-${Math.random().toString(36).substr(2, 9)}`).current;

  return (
    <div className={cn('space-y-2', className)}>
      {(label || showValue) && (
        <div className="flex justify-between items-center">
          {label && (
            <span className="text-sm font-medium text-foreground">
              {label}
            </span>
          )}
          {showValue && (
            <span className="text-sm text-muted-foreground">
              {Math.round(percentage)}%
            </span>
          )}
        </div>
      )}
      
      <div
        className="w-full bg-secondary rounded-full h-2 overflow-hidden"
        role="progressbar"
        aria-valuenow={value}
        aria-valuemin={0}
        aria-valuemax={max}
        aria-labelledby={label ? progressId : undefined}
        aria-describedby={description ? `${progressId}-desc` : undefined}
      >
        <div
          className="h-full bg-primary transition-all duration-300 ease-out"
          style={{ width: `${percentage}%` }}
        />
      </div>
      
      {description && (
        <p 
          id={`${progressId}-desc`}
          className="text-sm text-muted-foreground"
        >
          {description}
        </p>
      )}
    </div>
  );
}

/**
 * Custom Hook for managing keyboard navigation
 */
export function useKeyboardNavigation(
  items: HTMLElement[],
  options: {
    loop?: boolean;
    orientation?: 'horizontal' | 'vertical';
    onEscape?: () => void;
  } = {}
) {
  const { loop = true, orientation = 'horizontal', onEscape } = options;
  const [activeIndex, setActiveIndex] = useState(0);

  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    const { key } = event;
    const isHorizontal = orientation === 'horizontal';
    const nextKey = isHorizontal ? 'ArrowRight' : 'ArrowDown';
    const prevKey = isHorizontal ? 'ArrowLeft' : 'ArrowUp';

    switch (key) {
      case nextKey:
        event.preventDefault();
        setActiveIndex(prev => {
          const next = prev + 1;
          if (next >= items.length) {
            return loop ? 0 : prev;
          }
          return next;
        });
        break;

      case prevKey:
        event.preventDefault();
        setActiveIndex(prev => {
          const next = prev - 1;
          if (next < 0) {
            return loop ? items.length - 1 : prev;
          }
          return next;
        });
        break;

      case 'Home':
        event.preventDefault();
        setActiveIndex(0);
        break;

      case 'End':
        event.preventDefault();
        setActiveIndex(items.length - 1);
        break;

      case 'Escape':
        if (onEscape) {
          event.preventDefault();
          onEscape();
        }
        break;
    }
  }, [items, loop, orientation, onEscape]);

  useEffect(() => {
    if (items[activeIndex]) {
      items[activeIndex].focus();
    }
  }, [activeIndex, items]);

  return {
    activeIndex,
    setActiveIndex,
    handleKeyDown,
  };
}

/**
 * Accessible Tooltip
 */
interface TooltipProps {
  content: string;
  children: ReactNode;
  placement?: 'top' | 'bottom' | 'left' | 'right';
  delay?: number;
  className?: string;
}

export function Tooltip({
  content,
  children,
  placement = 'top',
  delay = 200,
  className,
}: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [shouldShow, setShouldShow] = useState(false);
  const timeoutRef = useRef<NodeJS.Timeout>();
  const tooltipId = useRef(`tooltip-${Math.random().toString(36).substr(2, 9)}`).current;

  const showTooltip = () => {
    setShouldShow(true);
    timeoutRef.current = setTimeout(() => {
      setIsVisible(true);
    }, delay);
  };

  const hideTooltip = () => {
    setShouldShow(false);
    setIsVisible(false);
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
  };

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  const placementClasses = {
    top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 -translate-y-1/2 ml-2',
  };

  return (
    <div 
      className="relative inline-block"
      onMouseEnter={showTooltip}
      onMouseLeave={hideTooltip}
      onFocus={showTooltip}
      onBlur={hideTooltip}
    >
      {React.cloneElement(children as React.ReactElement, {
        'aria-describedby': tooltipId,
      })}
      
      {shouldShow && (
        <div
          id={tooltipId}
          role="tooltip"
          className={cn(
            'absolute z-tooltip px-2 py-1',
            'bg-popover text-popover-foreground text-sm rounded-md',
            'border border-border shadow-lg',
            'transition-opacity duration-200',
            isVisible ? 'opacity-100' : 'opacity-0',
            placementClasses[placement],
            className
          )}
        >
          {content}
        </div>
      )}
    </div>
  );
}