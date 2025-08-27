import posthog from 'posthog-js';

export const initAnalytics = () => {
  if (typeof window !== 'undefined' && process.env.VITE_POSTHOG_KEY) {
    posthog.init(process.env.VITE_POSTHOG_KEY, {
      api_host: process.env.VITE_POSTHOG_HOST || 'https://app.posthog.com',
      
      // Configuration options
      loaded: (posthog) => {
        if (process.env.NODE_ENV === 'development') {
          console.log('PostHog loaded successfully');
        }
      },
      
      // Privacy settings
      respect_dnt: true,
      opt_out_capturing_by_default: false,
      
      // Session recording
      session_recording: {
        maskAllInputs: true,
        maskInputOptions: {
          password: true,
          email: false,
        },
        recordCrossOriginIframes: false,
      },
      
      // Feature flags
      bootstrap: {
        featureFlags: {},
      },
      
      // Performance
      disable_session_recording: process.env.NODE_ENV === 'development',
      
      // Custom properties
      property_blacklist: ['password', 'api_key', 'secret'],
      
      // Capture settings
      capture_pageview: true,
      capture_pageleave: true,
    });
  }
};

export const analytics = {
  // Page tracking
  page: (name, properties = {}) => {
    if (typeof window !== 'undefined') {
      posthog.capture('$pageview', {
        page: name,
        ...properties,
      });
    }
  },

  // Event tracking
  track: (eventName, properties = {}) => {
    if (typeof window !== 'undefined') {
      posthog.capture(eventName, {
        timestamp: new Date().toISOString(),
        ...properties,
      });
    }
  },

  // User identification
  identify: (userId, traits = {}) => {
    if (typeof window !== 'undefined') {
      posthog.identify(userId, traits);
    }
  },

  // User properties
  setUserProperties: (properties) => {
    if (typeof window !== 'undefined') {
      posthog.people.set(properties);
    }
  },

  // Feature flags
  isFeatureEnabled: (flagName) => {
    if (typeof window !== 'undefined') {
      return posthog.isFeatureEnabled(flagName);
    }
    return false;
  },

  // A/B testing
  getFeatureFlag: (flagName) => {
    if (typeof window !== 'undefined') {
      return posthog.getFeatureFlag(flagName);
    }
    return null;
  },

  // Custom events for the app
  searchImage: (query, source = 'search_bar') => {
    analytics.track('Image Searched', {
      query,
      source,
      query_length: query.length,
    });
  },

  generateDescription: (imageUrl, style, language) => {
    analytics.track('Description Generated', {
      image_url: imageUrl,
      description_style: style,
      language,
      generation_timestamp: Date.now(),
    });
  },

  addVocabulary: (word, translation, context) => {
    analytics.track('Vocabulary Added', {
      word,
      translation,
      context,
      word_length: word.length,
    });
  },

  startQuiz: (vocabularyCount) => {
    analytics.track('Quiz Started', {
      vocabulary_count: vocabularyCount,
      quiz_type: 'vocabulary',
    });
  },

  completeQuiz: (score, total, duration) => {
    analytics.track('Quiz Completed', {
      score,
      total_questions: total,
      accuracy: (score / total) * 100,
      duration_seconds: duration,
      completion_rate: (score / total),
    });
  },

  exportData: (format, itemCount) => {
    analytics.track('Data Exported', {
      export_format: format,
      item_count: itemCount,
      export_timestamp: Date.now(),
    });
  },

  error: (errorType, errorMessage, context = {}) => {
    analytics.track('Error Occurred', {
      error_type: errorType,
      error_message: errorMessage,
      error_timestamp: Date.now(),
      ...context,
    });
  },

  performance: (metric, value, context = {}) => {
    analytics.track('Performance Metric', {
      metric_name: metric,
      metric_value: value,
      measurement_timestamp: Date.now(),
      ...context,
    });
  },
};

export default analytics;