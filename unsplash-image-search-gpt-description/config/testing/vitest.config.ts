import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react-swc';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup/vitest.setup.ts'],
    include: ['src/**/*.{test,spec}.{js,ts,jsx,tsx}', 'tests/**/*.{test,spec}.{js,ts,jsx,tsx}'],
    exclude: ['node_modules', 'dist', 'build'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'tests/',
        '*.config.*',
        '*.d.ts',
        'src/main.tsx',
        'src/sw.ts',
      ],
      thresholds: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80,
        },
      },
    },
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, '../../src'),
      '@/components': resolve(__dirname, '../../src/components'),
      '@/hooks': resolve(__dirname, '../../src/hooks'),
      '@/utils': resolve(__dirname, '../../src/utils'),
      '@/types': resolve(__dirname, '../../src/types'),
      '@/stores': resolve(__dirname, '../../src/stores'),
      '@/lib': resolve(__dirname, '../../src/lib'),
    },
  },
});