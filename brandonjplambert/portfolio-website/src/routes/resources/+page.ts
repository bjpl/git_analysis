import type { PageLoad } from './$types';
import { instagramAccounts } from '$lib/data/instagram-accounts';
import { learningTools, journeyStats } from '$lib/data/learning-tools';
import type { InstagramAccount } from '$lib/types';

// Simulate API delay
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export const load: PageLoad = async ({ url }) => {
	// Simulate loading delay for demonstration
	await delay(300);

	// Get unique categories and countries for filtering
	const categories = [...new Set(instagramAccounts.map(account => account.category))].sort();
	const countries = [...new Set(instagramAccounts.map(account => account.country))].sort();
	const toolCategories = [...new Set(learningTools.map(tool => tool.category))].sort();
	
	// Check for any URL parameters for initial filters
	const searchParams = url.searchParams;
	const initialSearch = searchParams.get('search') || '';
	const initialCategory = searchParams.get('category');
	const initialCountry = searchParams.get('country');
	
	return {
		// Learning tools data
		learningTools,
		toolCategories,
		
		// Instagram accounts data
		instagramAccounts,
		categories,
		countries,
		
		// Journey statistics
		journeyStats,
		
		// Initial filter state
		initialFilters: {
			search: initialSearch,
			categories: initialCategory ? [initialCategory] : [],
			countries: initialCountry ? [initialCountry] : []
		},
		
		// Meta information
		meta: {
			title: 'Spanish Learning Resources | Brandon Lambert',
			description: 'Comprehensive Spanish learning resources including 400+ hours of Baselang tutoring, curated Instagram accounts, and proven tools for achieving B2/Advanced fluency.',
			keywords: 'Spanish learning, Baselang, language learning tools, Spanish Instagram accounts, B2 level Spanish, Colombia immersion, Spanish tutoring, language resources'
		},
		
		// Loading state
		loading: false
	};
};
