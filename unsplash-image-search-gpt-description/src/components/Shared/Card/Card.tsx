import React, { forwardRef, HTMLAttributes } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/utils/cn';

const cardVariants = cva(
  'rounded-lg border bg-card text-card-foreground transition-all duration-200',
  {
    variants: {
      variant: {
        default: 'bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-800 shadow-sm',
        elevated: 'bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-800 shadow-lg hover:shadow-xl',
        outlined: 'bg-transparent border-2 border-gray-300 dark:border-gray-600',
        ghost: 'bg-transparent border-0 shadow-none',
        filled: 'bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700',
      },
      size: {
        sm: 'p-3',
        md: 'p-4',
        lg: 'p-6',
        xl: 'p-8',
      },
      interactive: {
        true: 'cursor-pointer hover:shadow-md active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2',
        false: '',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'md',
      interactive: false,
    },
  }
);

export interface CardProps
  extends HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof cardVariants> {
  as?: React.ElementType;
  loading?: boolean;
  disabled?: boolean;
}

/**
 * Card component for content containers with various styles and sizes
 * Supports interactive states, loading states, and accessibility features
 */
export const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ 
    className, 
    variant, 
    size, 
    interactive, 
    as: Component = 'div',
    loading = false,
    disabled = false,
    children, 
    ...props 
  }, ref) => {
    return (
      <Component
        className={cn(
          cardVariants({ variant, size, interactive, className }),
          loading && 'pointer-events-none opacity-60',
          disabled && 'pointer-events-none opacity-50',
        )}
        ref={ref}
        tabIndex={interactive ? 0 : undefined}
        role={interactive ? 'button' : undefined}
        aria-disabled={disabled}
        {...props}
      >
        {loading ? (
          <div className="space-y-3">
            <div className="animate-pulse bg-gray-200 dark:bg-gray-700 h-4 rounded w-3/4" />
            <div className="animate-pulse bg-gray-200 dark:bg-gray-700 h-4 rounded w-1/2" />
            <div className="animate-pulse bg-gray-200 dark:bg-gray-700 h-4 rounded w-5/6" />
          </div>
        ) : (
          children
        )}
      </Component>
    );
  }
);

Card.displayName = 'Card';

// Card compound components for better composition
export const CardHeader = forwardRef<
  HTMLDivElement,
  HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex flex-col space-y-1.5 pb-4', className)}
    {...props}
  />
));
CardHeader.displayName = 'CardHeader';

export const CardTitle = forwardRef<
  HTMLParagraphElement,
  HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      'text-lg font-semibold leading-none tracking-tight text-gray-900 dark:text-white',
      className
    )}
    {...props}
  />
));
CardTitle.displayName = 'CardTitle';

export const CardDescription = forwardRef<
  HTMLParagraphElement,
  HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn('text-sm text-gray-600 dark:text-gray-400', className)}
    {...props}
  />
));
CardDescription.displayName = 'CardDescription';

export const CardContent = forwardRef<
  HTMLDivElement,
  HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex-1', className)}
    {...props}
  />
));
CardContent.displayName = 'CardContent';

export const CardFooter = forwardRef<
  HTMLDivElement,
  HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex items-center pt-4', className)}
    {...props}
  />
));
CardFooter.displayName = 'CardFooter';