import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ url }) => {
	const baseUrl = url.origin;
	
	const robots = `# Robots.txt for Brandon Lambert Portfolio
# AI Engineer & Full-Stack Developer

User-agent: *
Allow: /

# Sitemap location
Sitemap: ${baseUrl}/sitemap.xml

# Crawl delay for being respectful
Crawl-delay: 1

# Block access to sensitive files/directories
Disallow: /api/
Disallow: /.env*
Disallow: /node_modules/
Disallow: /build/
Disallow: /.svelte-kit/
Disallow: /static/admin/
Disallow: /*.json$

# Block specific bot types that might be resource-intensive
User-agent: AhrefsBot
Crawl-delay: 10

User-agent: MJ12bot
Crawl-delay: 10

User-agent: DotBot
Crawl-delay: 10

# Allow all major search engines
User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

User-agent: Slurp
Allow: /

User-agent: DuckDuckBot
Allow: /

User-agent: Baiduspider
Allow: /

User-agent: YandexBot
Allow: /

User-agent: facebookexternalhit
Allow: /

User-agent: Twitterbot
Allow: /

User-agent: LinkedInBot
Allow: /

# SEO optimization
Host: ${baseUrl.replace(/https?:\/\//, '')}`;

	return new Response(robots, {
		headers: {
			'Content-Type': 'text/plain; charset=utf-8',
			'Cache-Control': 'public, max-age=86400, s-maxage=86400',
			'X-Robots-Tag': 'noindex'
		}
	});
};

// Enable prerendering for robots.txt
export const prerender = true;