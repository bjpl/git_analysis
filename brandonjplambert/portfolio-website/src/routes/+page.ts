import { createClient } from '$lib/prismic/client';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch, params }) => {
	// Check if Prismic is properly configured
	const hasPrismicConfig = import.meta.env.VITE_PRISMIC_REPOSITORY && 
		import.meta.env.VITE_PRISMIC_REPOSITORY !== 'portfolio-demo';

	// Return fallback data immediately if Prismic is not configured
	if (!hasPrismicConfig) {
		console.log('Prismic not configured, using fallback data');
		return {
			homepage: null,
			projects: [],
			blogPosts: [],
			hasPrismic: false
		};
	}

	const client = createClient({ fetch });

	try {
		// Fetch homepage data from Prismic
		const homepage = await client.getSingle('homepage');
		
		// Fetch recent projects for the homepage
		const projects = await client.getAllByType('project', {
			limit: 6,
			orderings: [
				{
					field: 'document.first_publication_date',
					direction: 'desc'
				}
			]
		});

		// Fetch recent blog posts
		const blogPosts = await client.getAllByType('blog_post', {
			limit: 3,
			orderings: [
				{
					field: 'blog_post.publication_date',
					direction: 'desc'
				}
			]
		});

		return {
			homepage,
			projects,
			blogPosts,
			hasPrismic: true
		};
	} catch (error) {
		console.error('Error loading homepage data:', error);
		
		// Return fallback data if Prismic fails
		return {
			homepage: null,
			projects: [],
			blogPosts: [],
			hasPrismic: false
		};
	}
};