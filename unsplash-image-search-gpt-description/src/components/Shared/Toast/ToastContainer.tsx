import React from 'react';
import { Toaster } from 'react-hot-toast';
import { useAppStore } from '../../../stores/appStore';

export const ToastContainer: React.FC = () => {
  const { theme } = useAppStore();

  return (
    <Toaster
      position="top-right"
      gutter={8}
      containerClassName=""
      containerStyle={{}}
      toastOptions={{
        // Default options for all toasts
        className: '',
        duration: 4000,
        style: {
          background: theme === 'dark' ? '#374151' : '#ffffff',
          color: theme === 'dark' ? '#f9fafb' : '#111827',
          border: theme === 'dark' ? '1px solid #4b5563' : '1px solid #e5e7eb',
          borderRadius: '0.5rem',
          boxShadow: theme === 'dark' 
            ? '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)'
            : '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
          fontSize: '0.875rem',
          maxWidth: '400px',
        },

        // Specific styles for different types
        success: {
          iconTheme: {
            primary: '#10b981',
            secondary: '#ffffff',
          },
          style: {
            border: '1px solid #10b981',
          },
        },

        error: {
          iconTheme: {
            primary: '#ef4444',
            secondary: '#ffffff',
          },
          style: {
            border: '1px solid #ef4444',
          },
        },

        loading: {
          iconTheme: {
            primary: '#6366f1',
            secondary: '#ffffff',
          },
        },
      }}
    />
  );
};