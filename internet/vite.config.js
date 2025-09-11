import { defineConfig } from 'vite';

export default defineConfig({
  base: './',
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          'three': ['three'],
          'three-globe': ['three-globe'],
          'd3': ['d3'],
          'gsap': ['gsap']
        }
      }
    }
  },
  optimizeDeps: {
    include: ['three', 'globe.gl', 'd3', 'gsap']
  },
  server: {
    port: 5173,
    open: true
  }
});