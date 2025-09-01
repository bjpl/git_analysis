import type { RequestHandler } from './$types';

// Define all the routes in your application
const routes = [
	{
		path: '',
		priority: '1.0',
		changefreq: 'weekly'
	},
	{
		path: '/agentic-ai',
		priority: '0.9',
		changefreq: 'weekly'
	},
	{
		path: '/resources', 
		priority: '0.8',
		changefreq: 'weekly'
	},
	{
		path: '/work',
		priority: '0.8',
		changefreq: 'monthly'
	}
];

export const GET: RequestHandler = async ({ url }) => {
	const baseUrl = url.origin;
	const today = new Date().toISOString().split('T')[0];
	
	// Generate sitemap XML
	const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml"
        xmlns:mobile="http://www.google.com/schemas/sitemap-mobile/1.0"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"
        xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">
${routes
	.map(route => `  <url>
    <loc>${baseUrl}${route.path}</loc>
    <lastmod>${today}</lastmod>
    <changefreq>${route.changefreq}</changefreq>
    <priority>${route.priority}</priority>
    <mobile:mobile/>
  </url>`)
	.join('\n')}
</urlset>`;

	return new Response(sitemap, {
		headers: {
			'Content-Type': 'application/xml; charset=utf-8',
			'Cache-Control': 'public, max-age=3600, s-maxage=3600',
			'X-Robots-Tag': 'all'
		}
	});
};

// Enable prerendering for the sitemap
export const prerender = true;