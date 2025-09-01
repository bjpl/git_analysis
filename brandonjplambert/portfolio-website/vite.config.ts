import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	
	// Development server configuration
	server: {
		port: 5173,
		host: true,
		strictPort: false
	},
	
	// Preview server configuration
	preview: {
		port: 4173,
		host: true
	},
	
	// Build configuration
	build: {
		minify: process.env.NODE_ENV === 'production' ? 'terser' : 'esbuild',
		terserOptions: process.env.NODE_ENV === 'production' ? {
			compress: {
				drop_console: true,
				drop_debugger: true,
				pure_funcs: ['console.log']
			},
			mangle: true
		} : undefined,
		reportCompressedSize: false,
		chunkSizeWarningLimit: 1000,
		rollupOptions: {
			output: {
				manualChunks: {
					vendor: ['svelte']
				}
			}
		},
		// Ensure client-side dependencies are handled properly
		ssr: {
			noExternal: ['@emailjs/browser']
		}
	},
	
	// Optimization configuration
	optimizeDeps: {
		include: ['@prismicio/client', '@prismicio/svelte']
	},
	
	// Define global constants
	define: {
		__APP_VERSION__: JSON.stringify(process.env.npm_package_version),
		__BUILD_DATE__: JSON.stringify(new Date().toISOString()),
		__PROD__: JSON.stringify(process.env.NODE_ENV === 'production')
	},
	
	// CSS configuration
	css: {
		postcss: './postcss.config.js'
	},
	
	// Environment variables prefix
	envPrefix: 'VITE_'
});