import type { PageLoad } from './$types';

export const load: PageLoad = async () => {
	return {
		meta: {
			title: 'Agentic AI Projects - Brandon Lambert',
			description: 'Explore cutting-edge AI projects combining language learning, computer vision, and intelligent user experiences built with modern web technologies.',
			keywords: 'AI, Artificial Intelligence, Machine Learning, Language Learning, Computer Vision, Next.js, TypeScript, OpenAI, GPT-4'
		}
	};
};