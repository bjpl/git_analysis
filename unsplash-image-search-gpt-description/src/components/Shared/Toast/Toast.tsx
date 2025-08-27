import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { cn } from '@/utils/cn';
import { Button } from '../Button/Button';
import {
  CheckCircleIcon,
  ExclamationCircleIcon,
  InformationCircleIcon,
  XCircleIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';

export interface Toast {
  id: string;
  title: string;
  description?: string;
  variant?: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
  dismissible?: boolean;
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface ToastContextType {
  toasts: Toast[];
  toast: (toast: Omit<Toast, 'id'>) => void;
  dismiss: (id: string) => void;
  dismissAll: () => void;
}

const ToastContext = createContext<ToastContextType | null>(null);

/**
 * Hook to access toast functionality
 */
export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}

/**
 * Toast Provider component that manages toast state
 */
interface ToastProviderProps {
  children: React.ReactNode;
  maxToasts?: number;
}

export function ToastProvider({ children, maxToasts = 5 }: ToastProviderProps) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const toast = useCallback((newToast: Omit<Toast, 'id'>) => {
    const id = Math.random().toString(36).substr(2, 9);
    const toastWithId = {
      id,
      duration: 5000,
      dismissible: true,
      variant: 'info' as const,
      ...newToast,
    };

    setToasts(prev => {
      const updated = [toastWithId, ...prev];
      // Limit number of toasts
      return updated.slice(0, maxToasts);
    });

    // Auto dismiss after duration
    if (toastWithId.duration && toastWithId.duration > 0) {
      setTimeout(() => {
        dismiss(id);
      }, toastWithId.duration);
    }
  }, [maxToasts]);

  const dismiss = useCallback((id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  }, []);

  const dismissAll = useCallback(() => {
    setToasts([]);
  }, []);

  return (
    <ToastContext.Provider value={{ toasts, toast, dismiss, dismissAll }}>
      {children}
      <ToastContainer toasts={toasts} onDismiss={dismiss} />
    </ToastContext.Provider>
  );
}

/**
 * Individual Toast component
 */
interface ToastItemProps {
  toast: Toast;
  onDismiss: (id: string) => void;
}

function ToastItem({ toast, onDismiss }: ToastItemProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [isLeaving, setIsLeaving] = useState(false);

  useEffect(() => {
    // Trigger enter animation
    const timer = setTimeout(() => setIsVisible(true), 10);
    return () => clearTimeout(timer);
  }, []);

  const handleDismiss = () => {
    setIsLeaving(true);
    // Wait for exit animation before removing
    setTimeout(() => onDismiss(toast.id), 300);
  };

  const icons = {
    success: CheckCircleIcon,
    error: XCircleIcon,
    warning: ExclamationCircleIcon,
    info: InformationCircleIcon,
  };

  const Icon = icons[toast.variant || 'info'];

  const variantStyles = {
    success: 'border-green-200 bg-green-50 text-green-800 dark:border-green-800 dark:bg-green-900/50 dark:text-green-200',
    error: 'border-red-200 bg-red-50 text-red-800 dark:border-red-800 dark:bg-red-900/50 dark:text-red-200',
    warning: 'border-yellow-200 bg-yellow-50 text-yellow-800 dark:border-yellow-800 dark:bg-yellow-900/50 dark:text-yellow-200',
    info: 'border-blue-200 bg-blue-50 text-blue-800 dark:border-blue-800 dark:bg-blue-900/50 dark:text-blue-200',
  };

  const iconStyles = {
    success: 'text-green-500 dark:text-green-400',
    error: 'text-red-500 dark:text-red-400',
    warning: 'text-yellow-500 dark:text-yellow-400',
    info: 'text-blue-500 dark:text-blue-400',
  };

  return (
    <div
      className={cn(
        'flex w-full max-w-sm items-center gap-3 p-4 border rounded-lg shadow-lg',
        'backdrop-blur-sm transition-all duration-300 ease-out',
        variantStyles[toast.variant || 'info'],
        isVisible && !isLeaving
          ? 'translate-x-0 opacity-100 scale-100'
          : 'translate-x-full opacity-0 scale-95'
      )}
      role="alert"
      aria-live="polite"
    >
      <Icon className={cn('h-5 w-5 flex-shrink-0', iconStyles[toast.variant || 'info'])} />
      
      <div className="flex-1 min-w-0">
        <div className="text-sm font-medium">{toast.title}</div>
        {toast.description && (
          <div className="mt-1 text-sm opacity-90">{toast.description}</div>
        )}
      </div>

      <div className="flex items-center gap-2 ml-3">
        {toast.action && (
          <Button
            variant="ghost"
            size="xs"
            onClick={toast.action.onClick}
            className="h-7 px-2 text-xs hover:bg-black/10 dark:hover:bg-white/10"
          >
            {toast.action.label}
          </Button>
        )}
        
        {toast.dismissible && (
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={handleDismiss}
            className="h-6 w-6 hover:bg-black/10 dark:hover:bg-white/10"
            aria-label="Dismiss notification"
          >
            <XMarkIcon className="h-3 w-3" />
          </Button>
        )}
      </div>
    </div>
  );
}

/**
 * Toast Container component that renders all toasts
 */
interface ToastContainerProps {
  toasts: Toast[];
  onDismiss: (id: string) => void;
}

function ToastContainer({ toasts, onDismiss }: ToastContainerProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  if (toasts.length === 0) return null;

  return createPortal(
    <div
      className="fixed top-4 right-4 z-[100] flex flex-col gap-2 pointer-events-none"
      aria-live="polite"
      aria-label="Notifications"
    >
      {toasts.map((toast) => (
        <div key={toast.id} className="pointer-events-auto">
          <ToastItem toast={toast} onDismiss={onDismiss} />
        </div>
      ))}
    </div>,
    document.body
  );
}

/**
 * Utility functions for common toast patterns
 */
export const toast = {
  success: (title: string, description?: string, options?: Partial<Toast>) => ({
    title,
    description,
    variant: 'success' as const,
    ...options,
  }),
  
  error: (title: string, description?: string, options?: Partial<Toast>) => ({
    title,
    description,
    variant: 'error' as const,
    duration: 0, // Don't auto-dismiss errors
    ...options,
  }),
  
  warning: (title: string, description?: string, options?: Partial<Toast>) => ({
    title,
    description,
    variant: 'warning' as const,
    ...options,
  }),
  
  info: (title: string, description?: string, options?: Partial<Toast>) => ({
    title,
    description,
    variant: 'info' as const,
    ...options,
  }),
  
  promise: <T>(
    promise: Promise<T>,
    {
      loading,
      success,
      error,
    }: {
      loading: string;
      success: string | ((data: T) => string);
      error: string | ((error: any) => string);
    }
  ) => {
    const toastId = Math.random().toString(36).substr(2, 9);
    
    // Show loading toast
    const loadingToast = {
      id: toastId,
      title: loading,
      variant: 'info' as const,
      duration: 0,
      dismissible: false,
    };
    
    promise
      .then((data) => {
        const successTitle = typeof success === 'function' ? success(data) : success;
        return {
          title: successTitle,
          variant: 'success' as const,
        };
      })
      .catch((err) => {
        const errorTitle = typeof error === 'function' ? error(err) : error;
        return {
          title: errorTitle,
          variant: 'error' as const,
          duration: 0,
        };
      });
    
    return loadingToast;
  },
};