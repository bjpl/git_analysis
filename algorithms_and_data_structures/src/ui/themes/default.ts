/**
 * Default Theme Configuration
 */

import { Theme } from '../types';

export const defaultTheme: Theme = {
  primary: '#3b82f6',     // Blue
  secondary: '#64748b',   // Slate
  success: '#10b981',     // Emerald
  warning: '#f59e0b',     // Amber
  error: '#ef4444',       // Red
  info: '#06b6d4',        // Cyan
  background: '#ffffff',  // White
  foreground: '#1f2937',  // Gray-800
  border: '#d1d5db',      // Gray-300
  accent: '#8b5cf6',      // Violet
  muted: '#9ca3af'        // Gray-400
};

export const darkTheme: Theme = {
  primary: '#60a5fa',     // Blue-400
  secondary: '#94a3b8',   // Slate-400
  success: '#34d399',     // Emerald-400
  warning: '#fbbf24',     // Amber-400
  error: '#f87171',       // Red-400
  info: '#22d3ee',        // Cyan-400
  background: '#111827',  // Gray-900
  foreground: '#f9fafb',  // Gray-50
  border: '#374151',      // Gray-700
  accent: '#a78bfa',      // Violet-400
  muted: '#6b7280'        // Gray-500
};

export const terminalTheme: Theme = {
  primary: 'brightBlue',
  secondary: 'gray',
  success: 'brightGreen',
  warning: 'brightYellow',
  error: 'brightRed',
  info: 'brightCyan',
  background: 'black',
  foreground: 'white',
  border: 'white',
  accent: 'brightMagenta',
  muted: 'gray'
};