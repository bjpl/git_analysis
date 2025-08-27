import React, { createContext, useContext, useState, useCallback, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { cn } from '@/utils/cn';
import { 
  CheckCircleIcon, 
  ExclamationTriangleIcon, 
  XCircleIcon, 
  InformationCircleIcon,
  XMarkIcon 
} from '@heroicons/react/24/outline';

export type NotificationType = 'success' | 'error' | 'warning' | 'info';
export type NotificationPosition = 
  | 'top-left' | 'top-center' | 'top-right'
  | 'bottom-left' | 'bottom-center' | 'bottom-right';

export interface NotificationData {
  id: string;
  type: NotificationType;
  title: string;
  message?: string;
  duration?: number;
  persistent?: boolean;
  action?: {
    label: string;
    onClick: () => void;
  };
  onClose?: () => void;
}

interface NotificationContextType {
  notifications: NotificationData[];
  addNotification: (notification: Omit<NotificationData, 'id'>) => string;
  removeNotification: (id: string) => void;
  clearAll: () => void;
  updateNotification: (id: string, updates: Partial<NotificationData>) => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

interface NotificationProviderProps {
  children: React.ReactNode;
  position?: NotificationPosition;
  maxNotifications?: number;
  defaultDuration?: number;
}

/**
 * Enhanced Notification System with accessible toasts and rich interactions
 * Supports multiple types, positions, actions, and persistent notifications
 */
export function NotificationProvider({
  children,
  position = 'top-right',
  maxNotifications = 5,
  defaultDuration = 5000,
}: NotificationProviderProps) {
  const [notifications, setNotifications] = useState<NotificationData[]>([]);
  const timeoutsRef = useRef<Map<string, NodeJS.Timeout>>(new Map());

  // Auto-remove notification after duration
  const scheduleRemoval = useCallback((id: string, duration: number) => {
    if (timeoutsRef.current.has(id)) {
      clearTimeout(timeoutsRef.current.get(id)!);
    }

    const timeout = setTimeout(() => {
      removeNotification(id);
    }, duration);

    timeoutsRef.current.set(id, timeout);
  }, []);

  const addNotification = useCallback((notificationData: Omit<NotificationData, 'id'>): string => {
    const id = `notification-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const duration = notificationData.duration ?? defaultDuration;

    const notification: NotificationData = {
      ...notificationData,
      id,
    };

    setNotifications(prev => {
      const updated = [...prev, notification];
      // Limit maximum notifications
      if (updated.length > maxNotifications) {
        const removed = updated.shift();
        if (removed && timeoutsRef.current.has(removed.id)) {
          clearTimeout(timeoutsRef.current.get(removed.id)!);
          timeoutsRef.current.delete(removed.id);
        }
      }
      return updated;
    });

    // Schedule removal if not persistent
    if (!notification.persistent && duration > 0) {
      scheduleRemoval(id, duration);
    }

    return id;
  }, [maxNotifications, defaultDuration, scheduleRemoval]);

  const removeNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
    
    if (timeoutsRef.current.has(id)) {
      clearTimeout(timeoutsRef.current.get(id)!);
      timeoutsRef.current.delete(id);
    }

    // Find and call onClose if it exists
    const notification = notifications.find(n => n.id === id);
    notification?.onClose?.();
  }, [notifications]);

  const clearAll = useCallback(() => {
    // Clear all timeouts
    timeoutsRef.current.forEach(timeout => clearTimeout(timeout));
    timeoutsRef.current.clear();
    
    // Call onClose for all notifications
    notifications.forEach(notification => notification.onClose?.());
    
    setNotifications([]);
  }, [notifications]);

  const updateNotification = useCallback((id: string, updates: Partial<NotificationData>) => {
    setNotifications(prev =>
      prev.map(notification =>
        notification.id === id
          ? { ...notification, ...updates }
          : notification
      )
    );
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      timeoutsRef.current.forEach(timeout => clearTimeout(timeout));
    };
  }, []);

  const contextValue: NotificationContextType = {
    notifications,
    addNotification,
    removeNotification,
    clearAll,
    updateNotification,
  };

  return (
    <NotificationContext.Provider value={contextValue}>
      {children}
      <NotificationContainer position={position} notifications={notifications} />
    </NotificationContext.Provider>
  );
}

/**
 * Hook to use notification system
 */
export function useNotifications() {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
}

/**
 * Convenient hooks for specific notification types
 */
export function useNotificationHelpers() {
  const { addNotification } = useNotifications();

  const success = useCallback((title: string, message?: string, options?: Partial<NotificationData>) => {
    return addNotification({ ...options, type: 'success', title, message });
  }, [addNotification]);

  const error = useCallback((title: string, message?: string, options?: Partial<NotificationData>) => {
    return addNotification({ ...options, type: 'error', title, message, persistent: true });
  }, [addNotification]);

  const warning = useCallback((title: string, message?: string, options?: Partial<NotificationData>) => {
    return addNotification({ ...options, type: 'warning', title, message });
  }, [addNotification]);

  const info = useCallback((title: string, message?: string, options?: Partial<NotificationData>) => {
    return addNotification({ ...options, type: 'info', title, message });
  }, [addNotification]);

  return { success, error, warning, info };
}

/**
 * Container component for rendering notifications
 */
interface NotificationContainerProps {
  position: NotificationPosition;
  notifications: NotificationData[];
}

function NotificationContainer({ position, notifications }: NotificationContainerProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted || notifications.length === 0) {
    return null;
  }

  const positionClasses = {
    'top-left': 'top-4 left-4',
    'top-center': 'top-4 left-1/2 -translate-x-1/2',
    'top-right': 'top-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'bottom-center': 'bottom-4 left-1/2 -translate-x-1/2',
    'bottom-right': 'bottom-4 right-4',
  };

  const containerContent = (
    <div
      className={cn(
        'fixed z-toast pointer-events-none',
        'flex flex-col gap-2',
        positionClasses[position]
      )}
      aria-live="polite"
      aria-label="Notifications"
      role="region"
    >
      {notifications.map((notification, index) => (
        <NotificationItem
          key={notification.id}
          notification={notification}
          index={index}
          position={position}
        />
      ))}
    </div>
  );

  return createPortal(containerContent, document.body);
}

/**
 * Individual notification item component
 */
interface NotificationItemProps {
  notification: NotificationData;
  index: number;
  position: NotificationPosition;
}

function NotificationItem({ notification, index, position }: NotificationItemProps) {
  const { removeNotification } = useNotifications();
  const [isExiting, setIsExiting] = useState(false);

  const handleClose = () => {
    setIsExiting(true);
    setTimeout(() => removeNotification(notification.id), 300);
  };

  const handleAction = () => {
    notification.action?.onClick();
    handleClose();
  };

  const typeConfig = {
    success: {
      icon: CheckCircleIcon,
      className: 'border-success bg-success/10 text-success',
      iconClassName: 'text-success',
    },
    error: {
      icon: XCircleIcon,
      className: 'border-destructive bg-destructive/10 text-destructive',
      iconClassName: 'text-destructive',
    },
    warning: {
      icon: ExclamationTriangleIcon,
      className: 'border-warning bg-warning/10 text-warning',
      iconClassName: 'text-warning',
    },
    info: {
      icon: InformationCircleIcon,
      className: 'border-info bg-info/10 text-info',
      iconClassName: 'text-info',
    },
  };

  const config = typeConfig[notification.type];
  const Icon = config.icon;

  // Animation classes based on position
  const isTop = position.includes('top');
  const isRight = position.includes('right');
  const isLeft = position.includes('left');
  const isCenter = position.includes('center');

  let slideClass = '';
  if (isExiting) {
    if (isRight) slideClass = 'animate-slide-out-right';
    else if (isLeft) slideClass = 'animate-slide-out-left';
    else if (isCenter) slideClass = 'animate-fade-out';
  } else {
    if (isRight) slideClass = 'animate-slide-in-right';
    else if (isLeft) slideClass = 'animate-slide-in-left';
    else if (isCenter) slideClass = 'animate-slide-up';
  }

  return (
    <div
      className={cn(
        'pointer-events-auto relative',
        'w-full max-w-sm sm:max-w-md',
        'bg-background border border-border rounded-lg shadow-lg',
        'p-4 transform transition-all duration-300 ease-out',
        config.className,
        slideClass,
        isTop ? `translate-y-${index * 2}` : `translate-y-${-index * 2}`
      )}
      role="alert"
      aria-live="assertive"
      aria-describedby={notification.message ? `${notification.id}-message` : undefined}
    >
      <div className="flex items-start gap-3">
        {/* Icon */}
        <div className="flex-shrink-0 pt-0.5">
          <Icon className={cn('h-5 w-5', config.iconClassName)} aria-hidden="true" />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-foreground">
            {notification.title}
          </p>
          {notification.message && (
            <p
              id={`${notification.id}-message`}
              className="mt-1 text-sm text-muted-foreground"
            >
              {notification.message}
            </p>
          )}

          {/* Action Button */}
          {notification.action && (
            <div className="mt-3">
              <button
                onClick={handleAction}
                className={cn(
                  'text-sm font-medium underline hover:no-underline',
                  'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-ring',
                  config.iconClassName
                )}
              >
                {notification.action.label}
              </button>
            </div>
          )}
        </div>

        {/* Close Button */}
        <button
          onClick={handleClose}
          className="flex-shrink-0 rounded-md p-1 focus:outline-none focus:ring-2 focus:ring-ring hover:bg-muted"
          aria-label="Close notification"
        >
          <XMarkIcon className="h-4 w-4" aria-hidden="true" />
        </button>
      </div>

      {/* Progress bar for timed notifications */}
      {!notification.persistent && notification.duration && notification.duration > 0 && (
        <div className="absolute bottom-0 left-0 right-0 h-1 bg-border rounded-b-lg overflow-hidden">
          <div
            className={cn('h-full transition-all ease-linear', config.iconClassName, 'bg-current opacity-60')}
            style={{
              animation: `progress-bar ${notification.duration}ms linear`,
              width: '100%',
            }}
          />
        </div>
      )}
    </div>
  );
}

// Add progress bar keyframes to CSS
const progressBarStyles = `
@keyframes progress-bar {
  from { width: 100%; }
  to { width: 0%; }
}

@keyframes slide-in-right {
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}

@keyframes slide-out-right {
  from { transform: translateX(0); opacity: 1; }
  to { transform: translateX(100%); opacity: 0; }
}

@keyframes slide-in-left {
  from { transform: translateX(-100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}

@keyframes slide-out-left {
  from { transform: translateX(0); opacity: 1; }
  to { transform: translateX(-100%); opacity: 0; }
}

@keyframes fade-out {
  from { opacity: 1; }
  to { opacity: 0; }
}
`;

// Inject styles if not already present
if (typeof document !== 'undefined' && !document.getElementById('notification-styles')) {
  const style = document.createElement('style');
  style.id = 'notification-styles';
  style.textContent = progressBarStyles;
  document.head.appendChild(style);
}