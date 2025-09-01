import adapter from '@sveltejs/adapter-cloudflare';
import { vitePreprocess } from '@sveltejs/kit/vite';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  // Consult https://kit.svelte.dev/docs/integrations#preprocessors
  preprocess: vitePreprocess(),

  kit: {
    // Cloudflare Pages adapter configuration
    adapter: adapter({
      // Cloudflare Pages configuration
      pages: 'build',
      assets: 'build',
      fallback: null,
      precompress: true,
      
      // Platform-specific settings
      platformProxy: {
        // Configure local development proxy for Cloudflare bindings
        persist: './wrangler-local',
        
        // Environment bindings (KV, D1, R2, etc.)
        bindings: {
          // Example KV namespace
          // CACHE: {
          //   type: 'kv',
          //   id: 'your-kv-namespace-id'
          // },
          
          // Example D1 database
          // DB: {
          //   type: 'd1',
          //   databaseId: 'your-database-id'
          // },
          
          // Example R2 bucket
          // BUCKET: {
          //   type: 'r2',
          //   bucketName: 'your-bucket-name'
          // }
        }
      }
    }),

    // Environment variables configuration
    env: {
      // Public variables (exposed to client)
      publicPrefix: 'PUBLIC_',
      
      // Private variables (server-only)
      privatePrefix: 'PRIVATE_'
    },

    // Path configuration
    paths: {
      base: '',
      assets: ''
    },

    // Prerendering configuration for static generation
    prerender: {
      // Enable prerendering for better performance
      handleHttpError: 'warn',
      handleMissingId: 'warn',
      
      // Entries to prerender
      entries: ['*'],
      
      // Crawler configuration
      crawl: true,
      
      // Origin for absolute URLs in prerendered pages
      origin: 'https://your-domain.pages.dev'
    },

    // Service worker configuration
    serviceWorker: {
      register: false // Disable service worker for now
    },

    // TypeScript configuration
    typescript: {
      config: (config) => {
        // Extend TypeScript config for Cloudflare environment
        config.compilerOptions = {
          ...config.compilerOptions,
          target: 'ES2022',
          module: 'ES2022',
          moduleResolution: 'bundler'
        };
        return config;
      }
    },

    // CSP configuration
    csp: {
      mode: 'auto',
      directives: {
        'default-src': ['self'],
        'script-src': ['self', 'unsafe-inline'],
        'style-src': ['self', 'unsafe-inline'],
        'img-src': ['self', 'data:', 'https:'],
        'font-src': ['self', 'data:'],
        'connect-src': ['self', 'https:'],
        'frame-ancestors': ['none']
      }
    },

    // Alias configuration
    alias: {
      $lib: 'src/lib',
      $components: 'src/components',
      $stores: 'src/stores',
      $utils: 'src/utils',
      $types: 'src/types'
    }
  },

  // Svelte compiler options
  compilerOptions: {
    // Enable runtime checks in development
    dev: process.env.NODE_ENV === 'development',
    
    // CSS generation options
    css: 'injected',
    
    // Enable source maps
    enableSourcemap: true
  },

  // Vite-specific options
  vite: {
    // Define global constants
    define: {
      __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
      __VERSION__: JSON.stringify(process.env.npm_package_version || '1.0.0')
    },
    
    // Optimize dependencies
    optimizeDeps: {
      include: ['@prismic/client', '@prismic/helpers']
    }
  }
};

export default config;