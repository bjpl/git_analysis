import { defineConfig } from 'vite';

export default defineConfig({
  base: '/Internet-Infrastructure-Map/',
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          'three': ['three'],
          'globe': ['globe.gl'],
          'd3': ['d3']
        }
      }
    }
  },
  optimizeDeps: {
    include: ['three', 'globe.gl', 'd3']
  },
  server: {
    port: 5173,
    open: true
  }
});