import type { Handle, HandleServerError } from '@sveltejs/kit';
import { sequence } from '@sveltejs/kit/hooks';

// Security headers
const securityHeaders: Handle = async ({ event, resolve }) => {
	const response = await resolve(event);
	
	// Add security headers
	response.headers.set('X-Frame-Options', 'DENY');
	response.headers.set('X-Content-Type-Options', 'nosniff');
	response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
	response.headers.set('Permissions-Policy', 'camera=(), microphone=(), geolocation=()');
	
	// HSTS for HTTPS
	if (event.url.protocol === 'https:') {
		response.headers.set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains; preload');
	}
	
	return response;
};

// Performance headers
const performanceHeaders: Handle = async ({ event, resolve }) => {
	const response = await resolve(event);
	
	const pathname = event.url.pathname;
	
	// Cache control for static assets
	if (pathname.includes('/static/') || pathname.includes('/favicon') || pathname.match(/\.(js|css|png|jpg|jpeg|gif|webp|svg|woff|woff2)$/)) {
		response.headers.set('Cache-Control', 'public, max-age=31536000, immutable');
	}
	// Cache control for HTML pages
	else if (pathname.endsWith('.html') || pathname === '/' || !pathname.includes('.')) {
		response.headers.set('Cache-Control', 'public, max-age=300, s-maxage=3600');
	}
	// Cache control for API routes
	else if (pathname.startsWith('/api/')) {
		response.headers.set('Cache-Control', 'public, max-age=60');
	}
	
	// Compression hint
	response.headers.set('Vary', 'Accept-Encoding');
	
	return response;
};

// SEO and preload headers
const seoHeaders: Handle = async ({ event, resolve }) => {
	const response = await resolve(event);
	
	const pathname = event.url.pathname;
	
	// Add preload hints for critical resources on main pages
	if (pathname === '/' || pathname === '/agentic-ai' || pathname === '/resources' || pathname === '/work') {
		response.headers.set('Link', [
			'</favicon-32x32.png>; rel=preload; as=image',
			'<https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap>; rel=preload; as=style',
			'</headshot.jpg>; rel=preload; as=image'
		].join(', '));
	}
	
	return response;
};

// Analytics and monitoring
const analyticsHeaders: Handle = async ({ event, resolve }) => {
	const start = Date.now();
	const response = await resolve(event);
	const end = Date.now();
	
	// Add server timing header for performance monitoring
	response.headers.set('Server-Timing', `total;dur=${end - start}`);
	
	// Log for monitoring (in production, send to analytics service)
	if (process.env.NODE_ENV === 'production') {
		console.log({
			method: event.request.method,
			url: event.url.pathname,
			status: response.status,
			duration: end - start,
			userAgent: event.request.headers.get('user-agent'),
			timestamp: new Date().toISOString()
		});
	}
	
	return response;
};

// Combine all hooks in sequence
export const handle = sequence(
	securityHeaders,
	performanceHeaders,
	seoHeaders,
	analyticsHeaders
);

// Global error handling
export const handleError: HandleServerError = async ({ error, event }) => {
	const errorId = crypto.randomUUID();
	
	// Log error for monitoring
	console.error({
		errorId,
		error: error?.toString(),
		stack: error?.stack,
		url: event.url.pathname,
		method: event.request.method,
		userAgent: event.request.headers.get('user-agent'),
		timestamp: new Date().toISOString()
	});
	
	return {
		message: 'Something went wrong. Please try again later.',
		errorId
	};
};