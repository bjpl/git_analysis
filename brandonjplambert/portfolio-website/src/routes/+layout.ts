import type { LayoutLoad } from './$types';

export const load: LayoutLoad = async ({ url, fetch }) => {
	// Preload critical data for performance
	const baseUrl = url.origin;
	
	// SEO metadata that can be customized per route
	const seo = {
		title: 'Brandon Lambert - AI Engineer & Full-Stack Developer',
		description: 'AI Engineer & Full-Stack Developer specializing in agentic AI systems, machine learning, and modern web development. Explore innovative projects and professional work.',
		keywords: 'AI engineer, full-stack developer, agentic AI, machine learning, web development, portfolio, Brandon Lambert, artificial intelligence, software engineer',
		image: `${baseUrl}/og-image.jpg`,
		url: url.href,
		type: 'website'
	};

	// Performance optimization: Preload critical resources
	const preloadPromises = [];

	// Preload font resources
	if (typeof window !== 'undefined') {
		preloadPromises.push(
			// Preload critical fonts
			new Promise((resolve) => {
				const link = document.createElement('link');
				link.rel = 'preload';
				link.href = 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap';
				link.as = 'style';
				link.onload = () => resolve(true);
				link.onerror = () => resolve(false);
				document.head.appendChild(link);
			})
		);
	}

	// Route-specific metadata
	const routeMeta = {
		'/': {
			title: 'Brandon Lambert - AI Engineer & Full-Stack Developer',
			description: 'AI Engineer & Full-Stack Developer specializing in agentic AI systems, machine learning, and modern web development.',
		},
		'/agentic-ai': {
			title: 'Agentic AI Projects - Brandon Lambert',
			description: 'Explore cutting-edge agentic AI projects and systems built by Brandon Lambert, showcasing autonomous agents and intelligent automation.',
		},
		'/resources': {
			title: 'Developer Resources - Brandon Lambert',
			description: 'Curated collection of developer tools, learning resources, and technical insights for AI and web development.',
		},
		'/work': {
			title: 'Professional Experience - Brandon Lambert',
			description: 'Professional work experience, career highlights, and technical expertise in AI engineering and full-stack development.',
		}
	};

	// Update SEO based on current route
	const currentRoute = url.pathname;
	if (routeMeta[currentRoute as keyof typeof routeMeta]) {
		const route = routeMeta[currentRoute as keyof typeof routeMeta];
		seo.title = route.title;
		seo.description = route.description;
	}

	// Wait for preload promises (with timeout)
	try {
		await Promise.allSettled(preloadPromises.map(p => 
			Promise.race([p, new Promise(resolve => setTimeout(resolve, 1000))])
		));
	} catch (error) {
		console.warn('Some resources failed to preload:', error);
	}

	return {
		seo,
		url: url.href,
		pathname: url.pathname,
		// Performance metrics
		loadTime: Date.now()
	};
};

// Enable prerendering for static content
export const prerender = true;

// Enable server-side rendering
export const ssr = true;

// Trailing slash handling
export const trailingSlash = 'never';