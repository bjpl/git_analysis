import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';
import { VitePWA } from 'vite-plugin-pwa';
import path from 'path';

// Bulletproof Vite configuration for guaranteed deployment success
export default defineConfig({
  // Universal base path - works on all static hosts
  base: '/',
  
  plugins: [
    react({
      // Optimize React for production
      jsxImportSource: '@emotion/react',
      plugins: [
        ['@swc/plugin-emotion', {}]
      ]
    }),
    
    // Minimal PWA configuration for reliability
    VitePWA({
      registerType: 'autoUpdate',
      devOptions: {
        enabled: false // Disable in development for faster builds
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff,woff2}'],
        cleanupOutdatedCaches: true,
        skipWaiting: true,
        clientsClaim: true,
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/api\.unsplash\.com\//,
            handler: 'CacheFirst',
            options: {
              cacheName: 'unsplash-api-cache',
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 24 * 60 * 60 * 7 // 1 week
              },
              cacheKeyWillBeUsed: async ({ request }) => {
                // Remove API keys from cache keys for security
                const url = new URL(request.url);
                url.searchParams.delete('client_id');
                return url.href;
              }
            }
          },
          {
            urlPattern: /^https:\/\/images\.unsplash\.com\//,
            handler: 'CacheFirst',
            options: {
              cacheName: 'unsplash-images-cache',
              expiration: {
                maxEntries: 200,
                maxAgeSeconds: 24 * 60 * 60 * 30 // 30 days
              }
            }
          }
        ]
      },
      includeAssets: ['icon-*.png', 'favicon.ico'],
      manifest: {
        name: 'VocabLens - Spanish Vocabulary Learning',
        short_name: 'VocabLens',
        description: 'Learn Spanish vocabulary through AI-powered image descriptions',
        theme_color: '#4f46e5',
        background_color: '#ffffff',
        display: 'standalone',
        scope: '/',
        start_url: '/',
        orientation: 'portrait-primary',
        categories: ['education', 'productivity'],
        lang: 'en',
        icons: [
          {
            src: '/icon-192.png',
            sizes: '192x192',
            type: 'image/png',
            purpose: 'any maskable'
          },
          {
            src: '/icon-512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any maskable'
          }
        ]
      }
    })
  ],

  // Path resolution for cleaner imports
  resolve: {
    alias: {
      '@': path.resolve(__dirname, '../src'),
      '@components': path.resolve(__dirname, '../src/components'),
      '@pages': path.resolve(__dirname, '../src/pages'),
      '@services': path.resolve(__dirname, '../src/services'),
      '@hooks': path.resolve(__dirname, '../src/hooks'),
      '@utils': path.resolve(__dirname, '../src/utils'),
      '@types': path.resolve(__dirname, '../src/types')
    },
  },

  // Optimized build configuration
  build: {
    // Wide browser support for maximum compatibility
    target: 'es2015',
    
    // Build output configuration
    outDir: 'dist',
    assetsDir: 'assets',
    
    // Disable source maps in production for smaller builds
    sourcemap: false,
    
    // Use esbuild for faster builds
    minify: 'esbuild',
    
    // Clean output directory before build
    emptyOutDir: true,
    
    // Report compressed size for monitoring
    reportCompressedSize: true,
    
    // Chunk size warning threshold
    chunkSizeWarningLimit: 1000,
    
    // Advanced rollup configuration
    rollupOptions: {
      output: {
        // Manual chunk splitting for optimal loading
        manualChunks: {
          // Core React libraries
          'react-core': ['react', 'react-dom'],
          
          // Routing
          'react-router': ['react-router-dom'],
          
          // Icons (if using lucide-react)
          'icons': ['lucide-react'],
          
          // Utilities
          'utils': [
            'clsx', 
            'tailwind-merge'
          ]
        },
        
        // Consistent naming for better caching
        chunkFileNames: 'assets/[name]-[hash].js',
        entryFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]'
      },
      
      // External dependencies (if any)
      external: [],
      
      // Input configuration
      input: {
        main: path.resolve(__dirname, '../index.html')
      }
    },
    
    // CSS configuration
    cssCodeSplit: true,
    cssMinify: true,
    
    // Asset handling
    assetsInlineLimit: 4096, // Inline small assets as base64
    
    // Terser options for additional minification
    terserOptions: {
      compress: {
        drop_console: true, // Remove console.log in production
        drop_debugger: true,
        pure_funcs: ['console.log', 'console.info', 'console.debug']
      },
      mangle: {
        safari10: true // Fix Safari 10 issues
      },
      format: {
        comments: false // Remove comments
      }
    }
  },

  // Development server configuration
  server: {
    port: 3000,
    host: true, // Listen on all addresses
    open: true, // Auto-open browser
    cors: true, // Enable CORS
    
    // Proxy configuration for development API calls
    proxy: {
      // Proxy API calls to avoid CORS issues in development
      '/api': {
        target: 'http://localhost:3001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  },

  // Preview server configuration (for production build testing)
  preview: {
    port: 4173,
    host: true,
    cors: true
  },

  // Environment variables
  define: {
    __DEV__: JSON.stringify(process.env.NODE_ENV === 'development'),
    __PROD__: JSON.stringify(process.env.NODE_ENV === 'production'),
    __VERSION__: JSON.stringify(process.env.npm_package_version || '1.0.0')
  },

  // Environment variable prefix
  envPrefix: ['VITE_'],

  // Dependency optimization
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom'
    ],
    exclude: [
      '@vite/client',
      '@vite/env'
    ],
    // Force optimization of specific dependencies
    force: false
  },

  // CSS configuration
  css: {
    devSourcemap: true, // Enable CSS source maps in development
    modules: {
      localsConvention: 'camelCase'
    },
    preprocessorOptions: {
      scss: {
        additionalData: `@import "@/styles/variables.scss";`
      }
    }
  },

  // JSON configuration
  json: {
    namedExports: true,
    stringify: false
  },

  // Worker configuration
  worker: {
    format: 'es'
  }
});