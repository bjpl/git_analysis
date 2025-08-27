import React, { Component, ErrorInfo, ReactNode, useState, useEffect } from 'react';
import { cn } from '@/utils/cn';
import { Button } from '../Button/Button';
import { 
  ExclamationTriangleIcon,
  ArrowPathIcon,
  HomeIcon,
  BugAntIcon,
  CloudArrowDownIcon,
  WifiIcon,
  ShieldExclamationIcon
} from '@heroicons/react/24/outline';

export type ErrorType = 'network' | 'authentication' | 'permission' | 'validation' | 'server' | 'unknown';

export interface ErrorDetails {
  type: ErrorType;
  message: string;
  code?: string | number;
  details?: string;
  timestamp?: Date;
  userId?: string;
  action?: string;
  recoverable?: boolean;
  retryable?: boolean;
}

/**
 * Enhanced Error Boundary with detailed error reporting and recovery options
 */
interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: (error: Error, errorInfo: ErrorInfo) => ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  isolate?: boolean;
  resetOnPropsChange?: boolean;
  resetKeys?: Array<string | number>;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  errorId: string | null;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  private resetTimeoutId: number | null = null;

  constructor(props: ErrorBoundaryProps) {
    super(props);

    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    const errorId = `error-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    return {
      hasError: true,
      error,
      errorId,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error Boundary caught an error:', error, errorInfo);
    
    this.setState({
      errorInfo,
    });

    // Call custom error handler
    this.props.onError?.(error, errorInfo);

    // Report to error tracking service
    this.reportError(error, errorInfo);
  }

  componentDidUpdate(prevProps: ErrorBoundaryProps) {
    const { hasError } = this.state;
    const { resetKeys, resetOnPropsChange } = this.props;

    if (hasError && !prevProps.hasError) {
      // Error just occurred, don't reset immediately
      return;
    }

    if (hasError) {
      // Check if we should reset based on props change
      if (resetOnPropsChange && prevProps.children !== this.props.children) {
        this.resetErrorBoundary();
        return;
      }

      // Check if reset keys changed
      if (resetKeys && prevProps.resetKeys) {
        const hasResetKeyChanged = resetKeys.some(
          (key, idx) => prevProps.resetKeys![idx] !== key
        );
        
        if (hasResetKeyChanged) {
          this.resetErrorBoundary();
        }
      }
    }
  }

  componentWillUnmount() {
    if (this.resetTimeoutId) {
      clearTimeout(this.resetTimeoutId);
    }
  }

  private reportError = (error: Error, errorInfo: ErrorInfo) => {
    const errorDetails = {
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href,
      userId: this.getUserId(),
    };

    // Report to analytics or error tracking service
    if (process.env.NODE_ENV === 'production') {
      // Example: Sentry, LogRocket, etc.
      console.error('Error reported:', errorDetails);
    }
  };

  private getUserId = (): string | undefined => {
    // Get user ID from your auth system
    return undefined;
  };

  private resetErrorBoundary = () => {
    if (this.resetTimeoutId) {
      clearTimeout(this.resetTimeoutId);
    }

    this.resetTimeoutId = window.setTimeout(() => {
      this.setState({
        hasError: false,
        error: null,
        errorInfo: null,
        errorId: null,
      });
    }, 100);
  };

  render() {
    const { hasError, error, errorInfo, errorId } = this.state;
    const { children, fallback, isolate } = this.props;

    if (hasError && error) {
      if (fallback) {
        return fallback(error, errorInfo!);
      }

      return (
        <ErrorFallback
          error={error}
          errorInfo={errorInfo}
          errorId={errorId}
          onRetry={this.resetErrorBoundary}
          isolate={isolate}
        />
      );
    }

    return children;
  }
}

/**
 * Default error fallback component with recovery options
 */
interface ErrorFallbackProps {
  error: Error;
  errorInfo: ErrorInfo | null;
  errorId: string | null;
  onRetry: () => void;
  isolate?: boolean;
}

function ErrorFallback({ error, errorInfo, errorId, onRetry, isolate }: ErrorFallbackProps) {
  const [showDetails, setShowDetails] = useState(false);
  const [isRetrying, setIsRetrying] = useState(false);

  const handleRetry = async () => {
    setIsRetrying(true);
    
    // Add a small delay to show loading state
    await new Promise(resolve => setTimeout(resolve, 500));
    
    onRetry();
    setIsRetrying(false);
  };

  const errorType = determineErrorType(error);
  const errorConfig = getErrorConfig(errorType);

  return (
    <div 
      className={cn(
        'flex flex-col items-center justify-center p-8',
        'bg-background border border-destructive/20 rounded-lg',
        isolate ? 'min-h-32' : 'min-h-64',
        'text-center space-y-4'
      )}
      role="alert"
      aria-live="assertive"
    >
      {/* Error Icon */}
      <div className="flex-shrink-0">
        <errorConfig.icon className="h-12 w-12 text-destructive mx-auto" aria-hidden="true" />
      </div>

      {/* Error Message */}
      <div className="space-y-2">
        <h2 className="text-xl font-semibold text-foreground">
          {errorConfig.title}
        </h2>
        <p className="text-muted-foreground max-w-md">
          {errorConfig.description}
        </p>
        {error.message && (
          <p className="text-sm text-destructive font-mono bg-destructive/10 px-3 py-1 rounded">
            {error.message}
          </p>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-3 justify-center">
        {errorConfig.retryable && (
          <Button
            onClick={handleRetry}
            loading={isRetrying}
            variant="primary"
            className="min-w-24"
          >
            <ArrowPathIcon className="h-4 w-4 mr-2" />
            Try Again
          </Button>
        )}
        
        <Button
          onClick={() => window.location.href = '/'}
          variant="outline"
        >
          <HomeIcon className="h-4 w-4 mr-2" />
          Go Home
        </Button>

        {process.env.NODE_ENV === 'development' && (
          <Button
            onClick={() => setShowDetails(!showDetails)}
            variant="ghost"
            size="sm"
          >
            <BugAntIcon className="h-4 w-4 mr-2" />
            {showDetails ? 'Hide' : 'Show'} Details
          </Button>
        )}
      </div>

      {/* Error Details (Development) */}
      {showDetails && process.env.NODE_ENV === 'development' && (
        <details className="w-full max-w-2xl">
          <summary className="cursor-pointer text-sm font-medium text-muted-foreground mb-2">
            Technical Details (ID: {errorId})
          </summary>
          <div className="bg-muted p-4 rounded text-left text-xs font-mono space-y-2 overflow-auto max-h-60">
            <div>
              <strong>Error:</strong> {error.name}: {error.message}
            </div>
            {error.stack && (
              <div>
                <strong>Stack:</strong>
                <pre className="whitespace-pre-wrap mt-1">{error.stack}</pre>
              </div>
            )}
            {errorInfo?.componentStack && (
              <div>
                <strong>Component Stack:</strong>
                <pre className="whitespace-pre-wrap mt-1">{errorInfo.componentStack}</pre>
              </div>
            )}
          </div>
        </details>
      )}
    </div>
  );
}

/**
 * Specific error components for different scenarios
 */

// Network Error Component
export function NetworkError({ onRetry, message }: { onRetry?: () => void; message?: string }) {
  return (
    <ErrorDisplay
      type="network"
      title="Connection Problem"
      message={message || "Unable to connect to our servers. Please check your internet connection."}
      icon={WifiIcon}
      actions={onRetry ? [{ label: 'Try Again', onClick: onRetry, variant: 'primary' }] : undefined}
    />
  );
}

// Permission Error Component
export function PermissionError({ message, onLogin }: { message?: string; onLogin?: () => void }) {
  return (
    <ErrorDisplay
      type="permission"
      title="Access Denied"
      message={message || "You don't have permission to view this content."}
      icon={ShieldExclamationIcon}
      actions={onLogin ? [{ label: 'Sign In', onClick: onLogin, variant: 'primary' }] : undefined}
    />
  );
}

// Server Error Component
export function ServerError({ onRetry, message }: { onRetry?: () => void; message?: string }) {
  return (
    <ErrorDisplay
      type="server"
      title="Server Error"
      message={message || "Something went wrong on our end. We're working to fix it."}
      icon={CloudArrowDownIcon}
      actions={onRetry ? [{ label: 'Try Again', onClick: onRetry, variant: 'primary' }] : undefined}
    />
  );
}

// Generic Error Display Component
interface ErrorDisplayProps {
  type: ErrorType;
  title: string;
  message: string;
  icon?: React.ComponentType<{ className?: string }>;
  actions?: Array<{
    label: string;
    onClick: () => void;
    variant?: 'primary' | 'secondary' | 'outline';
    loading?: boolean;
  }>;
  className?: string;
}

export function ErrorDisplay({ 
  type, 
  title, 
  message, 
  icon: Icon = ExclamationTriangleIcon, 
  actions, 
  className 
}: ErrorDisplayProps) {
  return (
    <div 
      className={cn(
        'flex flex-col items-center justify-center p-8',
        'bg-background border border-border rounded-lg',
        'text-center space-y-4 min-h-64',
        className
      )}
      role="alert"
      aria-live="polite"
    >
      <Icon className="h-12 w-12 text-muted-foreground" aria-hidden="true" />
      
      <div className="space-y-2 max-w-md">
        <h3 className="text-lg font-semibold text-foreground">{title}</h3>
        <p className="text-muted-foreground">{message}</p>
      </div>

      {actions && actions.length > 0 && (
        <div className="flex gap-3 flex-wrap justify-center">
          {actions.map((action, index) => (
            <Button
              key={index}
              onClick={action.onClick}
              variant={action.variant || 'primary'}
              loading={action.loading}
            >
              {action.label}
            </Button>
          ))}
        </div>
      )}
    </div>
  );
}

/**
 * Hook for handling async errors
 */
export function useErrorHandler() {
  const [error, setError] = useState<Error | null>(null);

  const handleError = (error: Error | unknown) => {
    if (error instanceof Error) {
      setError(error);
    } else {
      setError(new Error(String(error)));
    }
  };

  const clearError = () => setError(null);

  return {
    error,
    handleError,
    clearError,
    hasError: error !== null,
  };
}

/**
 * Utility functions
 */
function determineErrorType(error: Error): ErrorType {
  const message = error.message.toLowerCase();
  const name = error.name.toLowerCase();

  if (message.includes('network') || message.includes('fetch') || name.includes('networkerror')) {
    return 'network';
  }
  
  if (message.includes('unauthorized') || message.includes('authentication')) {
    return 'authentication';
  }
  
  if (message.includes('forbidden') || message.includes('permission')) {
    return 'permission';
  }
  
  if (message.includes('validation') || name.includes('validationerror')) {
    return 'validation';
  }
  
  if (message.includes('server') || message.includes('5')) {
    return 'server';
  }

  return 'unknown';
}

function getErrorConfig(type: ErrorType) {
  const configs = {
    network: {
      title: 'Connection Problem',
      description: 'Please check your internet connection and try again.',
      icon: WifiIcon,
      retryable: true,
    },
    authentication: {
      title: 'Authentication Required',
      description: 'Please sign in to continue.',
      icon: ShieldExclamationIcon,
      retryable: false,
    },
    permission: {
      title: 'Access Denied',
      description: 'You don\'t have permission to perform this action.',
      icon: ShieldExclamationIcon,
      retryable: false,
    },
    validation: {
      title: 'Invalid Data',
      description: 'Please check your input and try again.',
      icon: ExclamationTriangleIcon,
      retryable: true,
    },
    server: {
      title: 'Server Error',
      description: 'Something went wrong on our end. Please try again later.',
      icon: CloudArrowDownIcon,
      retryable: true,
    },
    unknown: {
      title: 'Something Went Wrong',
      description: 'An unexpected error occurred. Please try again.',
      icon: ExclamationTriangleIcon,
      retryable: true,
    },
  };

  return configs[type];
}