import * as Sentry from '@sentry/react';
import { BrowserTracing } from '@sentry/tracing';

export const initSentry = () => {
  Sentry.init({
    dsn: process.env.VITE_SENTRY_DSN,
    environment: process.env.NODE_ENV || 'development',
    integrations: [
      new BrowserTracing({
        // Set sampling rate for performance monitoring
        tracePropagationTargets: [
          'localhost',
          /^https:\/\/api\.unsplash\.com/,
          /^https:\/\/api\.openai\.com/,
        ],
      }),
      new Sentry.Replay({
        // Capture 10% of sessions for replay
        sessionSampleRate: 0.1,
        // Capture 100% of sessions with errors for replay
        errorSampleRate: 1.0,
      }),
    ],
    // Performance Monitoring
    tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.1 : 1.0,
    // Release tracking
    release: process.env.VITE_APP_VERSION,
    // User context
    beforeSend: (event, hint) => {
      // Filter out development errors
      if (process.env.NODE_ENV === 'development') {
        console.warn('Sentry Event (dev):', event, hint);
        return null;
      }

      // Filter out known non-critical errors
      const error = hint.originalException;
      if (error && error.message) {
        const ignoredMessages = [
          'ResizeObserver loop limit exceeded',
          'Script error',
          'Network request failed',
          'Loading chunk',
        ];

        if (ignoredMessages.some(msg => error.message.includes(msg))) {
          return null;
        }
      }

      return event;
    },
    // Additional configuration
    beforeBreadcrumb: (breadcrumb, hint) => {
      // Filter out noisy breadcrumbs
      if (breadcrumb.category === 'console' && breadcrumb.level === 'debug') {
        return null;
      }
      return breadcrumb;
    },
  });
};

export const captureUserFeedback = (feedback) => {
  Sentry.captureUserFeedback({
    event_id: Sentry.lastEventId(),
    name: feedback.name || 'Anonymous',
    email: feedback.email || 'no-email@example.com',
    comments: feedback.message,
  });
};

export const setUserContext = (user) => {
  Sentry.setUser({
    id: user.id,
    email: user.email,
    username: user.username,
  });
};

export const addBreadcrumb = (message, category = 'custom', level = 'info') => {
  Sentry.addBreadcrumb({
    message,
    category,
    level,
    timestamp: Date.now() / 1000,
  });
};

export const captureException = (error, context = {}) => {
  Sentry.withScope(scope => {
    Object.keys(context).forEach(key => {
      scope.setTag(key, context[key]);
    });
    Sentry.captureException(error);
  });
};

export const startTransaction = (name, op = 'navigation') => {
  return Sentry.startTransaction({ name, op });
};

export default Sentry;