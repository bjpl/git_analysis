import adapter from '@sveltejs/adapter-cloudflare';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	// Consult https://kit.svelte.dev/docs/integrations#preprocessors
	// for more information about preprocessors
	preprocess: vitePreprocess(),

	kit: {
		// adapter-auto only supports some environments, see https://kit.svelte.dev/docs/adapter-auto
		// If your environment is not supported or you settled on a specific environment, switch out the adapter.
		// See https://kit.svelte.dev/docs/adapters for more information about adapters.
		adapter: adapter({
			// Cloudflare Pages configuration
			routes: {
				include: ['/*'],
				exclude: ['<all>']
			}
		}),
		
		// Prerendering configuration
		prerender: {
			handleHttpError: ({ path, referrer, message }) => {
				// Log errors but don't fail the build
				console.warn(`Prerender error for ${path}: ${message}`);
			}
		},
		
		// CSP configuration for security and performance
		csp: {
			directives: {
				'default-src': ['self'],
				'script-src': ['self', 'unsafe-inline', 'unsafe-eval', 'https://fonts.googleapis.com'],
				'style-src': ['self', 'unsafe-inline', 'https://fonts.googleapis.com', 'https://fonts.gstatic.com'],
				'font-src': ['self', 'https://fonts.gstatic.com'],
				'img-src': ['self', 'data:', 'https:'],
				'connect-src': ['self', 'https://api.prismic.io'],
				'media-src': ['self'],
				'object-src': ['none'],
				'base-uri': ['self'],
				'form-action': ['self'],
				'frame-ancestors': ['none'],
				'upgrade-insecure-requests': true
			},
			mode: 'hash'
		},
		
		// Additional performance optimizations
		serviceWorker: {
			register: true,
			files: (filepath) => !/\.(DS_Store|Thumbs\.db)$/.test(filepath)
		},
		
		// Environment-specific alias configuration
		alias: {
			'$lib': './src/lib',
			'$lib/*': './src/lib/*',
			'$app/*': '$app/*'
		}
	}
};

export default config;