<script lang="ts">
	import { onMount } from 'svelte';
	
	// Animation trigger for scroll-based animations
	let mounted = false;
	
	// Project data
	const featuredProject = {
		title: "Describe It - Spanish Learning through Visual Intelligence",
		subtitle: "Next.js 14 AI-Powered Language Education Platform",
		description: "Revolutionary language learning app that combines visual intelligence with AI to teach Spanish through multi-style descriptions, interactive Q&A, and smart phrase extraction. Features real-time collaboration and adaptive learning paths powered by GPT-4.",
		features: [
			"Multi-style descriptions (5 unique learning styles)",
			"Interactive AI-powered Q&A system",
			"Smart phrase extraction and analysis",
			"Session management and progress tracking",
			"Real-time collaborative learning",
			"Adaptive difficulty adjustment",
			"Voice pronunciation feedback",
			"Cultural context integration"
		],
		techStack: [
			{ name: "Next.js 14", color: "bg-gray-900 text-white" },
			{ name: "TypeScript", color: "bg-blue-600 text-white" },
			{ name: "Supabase", color: "bg-green-600 text-white" },
			{ name: "Vercel KV", color: "bg-black text-white" },
			{ name: "OpenAI GPT-4", color: "bg-emerald-600 text-white" },
			{ name: "Tailwind CSS", color: "bg-cyan-500 text-white" },
			{ name: "React Query", color: "bg-red-500 text-white" },
			{ name: "Framer Motion", color: "bg-purple-600 text-white" }
		],
		metrics: [
			{ label: "Learning Retention", value: "94%" },
			{ label: "User Engagement", value: "87%" },
			{ label: "AI Accuracy", value: "96%" },
			{ label: "Response Time", value: "<200ms" }
		],
		links: {
			github: "#",
			demo: "#",
			case_study: "#"
		}
	};
	
	const otherProjects = [
		{
			title: "brandonjplambert.com",
			description: "Personal portfolio showcasing full-stack development expertise and AI integration capabilities.",
			status: "Live",
			tech: ["SvelteKit", "TypeScript", "Prismic CMS"],
			category: "Portfolio"
		},
		{
			title: "letratos.com",
			description: "Comprehensive Spanish learning platform with gamified experiences and adaptive AI tutoring.",
			status: "Coming Soon",
			tech: ["React", "Node.js", "PostgreSQL", "OpenAI"],
			category: "EdTech"
		},
		{
			title: "hablas.co",
			description: "Real-time language practice application with AI conversation partners and pronunciation analysis.",
			status: "Coming Soon",
			tech: ["Next.js", "WebRTC", "Speech API", "TensorFlow"],
			category: "Language Learning"
		},
		{
			title: "Conjugation Practice App",
			description: "Interactive Spanish verb conjugation tool with personalized difficulty and gamified learning paths.",
			status: "Coming Soon",
			tech: ["Vue.js", "Python", "FastAPI", "Redis"],
			category: "Educational Tool"
		}
	];
	
	const aiExpertise = [
		"Large Language Models (GPT-4, Claude, Gemini)",
		"Computer Vision & Image Analysis",
		"Natural Language Processing",
		"Conversational AI & Chatbots",
		"Machine Learning Integration",
		"AI-Powered User Experiences",
		"Prompt Engineering & Optimization",
		"Multimodal AI Applications"
	];
	
	onMount(() => {
		mounted = true;
	});
</script>

<svelte:head>
	<title>Agentic AI Projects - Brandon Lambert</title>
	<meta name="description" content="Explore cutting-edge AI projects combining language learning, computer vision, and intelligent user experiences built with modern web technologies." />
</svelte:head>

<div class="bg-gradient-to-br from-primary-50 via-white to-secondary-50 min-h-screen">
	<!-- Hero Section -->
	<section class="section">
		<div class="container-wide">
			<div class="text-center max-w-4xl mx-auto">
				<div class="inline-flex items-center px-4 py-2 rounded-full bg-primary-100 text-primary-700 text-sm font-medium mb-6">
					<svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
						<path fill-rule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clip-rule="evenodd" />
					</svg>
					Agentic AI Development
				</div>
				
				<h1 class="text-5xl lg:text-7xl font-serif text-secondary-900 mb-6 {mounted ? 'animate-slide-up' : 'opacity-0'}">
					Intelligent
					<span class="text-gradient block">AI Experiences</span>
				</h1>
				
				<p class="text-xl lg:text-2xl text-secondary-600 mb-8 max-w-3xl mx-auto leading-relaxed {mounted ? 'animate-slide-up' : 'opacity-0'}" style="animation-delay: 0.1s">
					Building the future of human-AI interaction through innovative applications that seamlessly blend artificial intelligence with intuitive user experiences.
				</p>
				
				<div class="flex flex-wrap justify-center gap-3 mb-12 {mounted ? 'animate-slide-up' : 'opacity-0'}" style="animation-delay: 0.2s">
					{#each aiExpertise as skill}
						<span class="px-4 py-2 bg-white/80 backdrop-blur-sm border border-primary-200 rounded-full text-sm font-medium text-primary-700 shadow-soft hover:shadow-medium transition-all duration-200 hover:scale-105">
							{skill}
						</span>
					{/each}
				</div>
			</div>
		</div>
	</section>

	<!-- Featured Project Section -->
	<section class="section bg-white/50 backdrop-blur-sm">
		<div class="container-wide">
			<div class="text-center mb-16">
				<h2 class="text-3xl lg:text-4xl font-serif text-secondary-900 mb-4">
					Featured Project
				</h2>
				<div class="w-24 h-1 bg-gradient-primary mx-auto rounded-full"></div>
			</div>
			
			<div class="grid lg:grid-cols-2 gap-12 items-center">
				<!-- Project Info -->
				<div class="space-y-8">
					<div>
						<div class="inline-flex items-center px-3 py-1 rounded-full bg-success-100 text-success-700 text-sm font-medium mb-4">
							<div class="w-2 h-2 bg-success-500 rounded-full mr-2"></div>
							Featured Project
						</div>
						<h3 class="text-3xl lg:text-4xl font-serif text-secondary-900 mb-4">
							{featuredProject.title}
						</h3>
						<p class="text-lg text-primary-600 font-medium mb-4">
							{featuredProject.subtitle}
						</p>
						<p class="text-secondary-600 leading-relaxed text-lg">
							{featuredProject.description}
						</p>
					</div>
					
					<!-- Key Features -->
					<div>
						<h4 class="text-xl font-semibold text-secondary-900 mb-4">Key Features</h4>
						<div class="grid sm:grid-cols-2 gap-3">
							{#each featuredProject.features as feature}
								<div class="flex items-start space-x-3">
									<svg class="w-5 h-5 text-success-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
										<path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
									</svg>
									<span class="text-secondary-700 text-sm">{feature}</span>
								</div>
							{/each}
						</div>
					</div>
					
					<!-- Performance Metrics -->
					<div>
						<h4 class="text-xl font-semibold text-secondary-900 mb-4">Performance Metrics</h4>
						<div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
							{#each featuredProject.metrics as metric}
								<div class="text-center p-4 bg-white rounded-xl shadow-soft border border-secondary-100">
									<div class="text-2xl font-bold text-primary-600">{metric.value}</div>
									<div class="text-sm text-secondary-600 mt-1">{metric.label}</div>
								</div>
							{/each}
						</div>
					</div>
					
					<!-- Tech Stack -->
					<div>
						<h4 class="text-xl font-semibold text-secondary-900 mb-4">Technology Stack</h4>
						<div class="flex flex-wrap gap-2">
							{#each featuredProject.techStack as tech}
								<span class="px-3 py-1 {tech.color} rounded-full text-sm font-medium shadow-soft">
									{tech.name}
								</span>
							{/each}
						</div>
					</div>
					
					<!-- Action Buttons -->
					<div class="flex flex-wrap gap-4 pt-4">
						<a href={featuredProject.links.demo} class="btn-primary">
							<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
							</svg>
							View Demo
						</a>
						<a href={featuredProject.links.github} class="btn-outline">
							<svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
								<path fill-rule="evenodd" d="M10 0C4.477 0 0 4.484 0 10.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0110 4.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.203 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.942.359.31.678.921.678 1.856 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0020 10.017C20 4.484 15.522 0 10 0z" clip-rule="evenodd" />
							</svg>
							Source Code
						</a>
						<a href={featuredProject.links.case_study} class="btn-secondary">
							<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
							</svg>
							Case Study
						</a>
					</div>
				</div>
				
				<!-- Project Visual -->
				<div class="relative">
					<div class="aspect-[4/3] bg-gradient-to-br from-primary-500 to-primary-700 rounded-2xl shadow-large overflow-hidden">
						<!-- Placeholder for project screenshot -->
						<div class="w-full h-full flex items-center justify-center">
							<div class="text-center text-white p-8">
								<div class="w-24 h-24 bg-white/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
									<svg class="w-12 h-12" fill="currentColor" viewBox="0 0 20 20">
										<path fill-rule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clip-rule="evenodd" />
									</svg>
								</div>
								<h4 class="text-xl font-semibold mb-2">Interactive Demo</h4>
								<p class="text-white/80">Experience AI-powered language learning</p>
							</div>
						</div>
					</div>
					
					<!-- Floating Elements -->
					<div class="absolute -top-4 -right-4 w-24 h-24 bg-white rounded-2xl shadow-large flex items-center justify-center">
						<div class="text-center">
							<div class="text-2xl font-bold text-primary-600">4.9</div>
							<div class="text-xs text-secondary-600">Rating</div>
						</div>
					</div>
					
					<div class="absolute -bottom-4 -left-4 w-32 h-16 bg-success-500 rounded-xl shadow-large flex items-center justify-center text-white">
						<div class="text-center">
							<div class="text-lg font-bold">10K+</div>
							<div class="text-xs">Users</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- Other Projects Section -->
	<section class="section">
		<div class="container-wide">
			<div class="text-center mb-16">
				<h2 class="text-3xl lg:text-4xl font-serif text-secondary-900 mb-4">
					Other AI Projects
				</h2>
				<p class="text-xl text-secondary-600 max-w-2xl mx-auto">
					Exploring diverse applications of artificial intelligence across different domains and use cases.
				</p>
			</div>
			
			<div class="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
				{#each otherProjects as project}
					<div class="card-hover group">
						<div class="p-6">
							<!-- Status Badge -->
							<div class="flex items-center justify-between mb-4">
								<span class="px-3 py-1 rounded-full text-xs font-medium {project.status === 'Live' ? 'bg-success-100 text-success-700' : 'bg-warning-100 text-warning-700'}">
									{project.status}
								</span>
								<span class="px-2 py-1 bg-secondary-100 text-secondary-600 rounded text-xs">
									{project.category}
								</span>
							</div>
							
							<!-- Project Info -->
							<h3 class="text-xl font-semibold text-secondary-900 mb-3 group-hover:text-primary-600 transition-colors">
								{project.title}
							</h3>
							<p class="text-secondary-600 text-sm mb-4 leading-relaxed">
								{project.description}
							</p>
							
							<!-- Tech Stack -->
							<div class="flex flex-wrap gap-1 mb-4">
								{#each project.tech as tech}
									<span class="px-2 py-1 bg-primary-50 text-primary-700 rounded text-xs font-medium">
										{tech}
									</span>
								{/each}
							</div>
							
							<!-- Action -->
							<button class="w-full text-center py-2 text-sm font-medium text-primary-600 hover:text-primary-700 transition-colors {project.status === 'Coming Soon' ? 'opacity-50 cursor-not-allowed' : 'hover:bg-primary-50 rounded-lg'}">
								{project.status === 'Live' ? 'View Project' : 'Coming Soon'}
							</button>
						</div>
					</div>
				{/each}
			</div>
		</div>
	</section>

	<!-- Call to Action -->
	<section class="section bg-gradient-primary">
		<div class="container-narrow text-center">
			<h2 class="text-3xl lg:text-4xl font-serif text-white mb-6">
				Ready to Build Something Amazing?
			</h2>
			<p class="text-xl text-white/90 mb-8 leading-relaxed">
				Let's collaborate on your next AI-powered project. From concept to deployment, I'll help you create intelligent solutions that delight your users.
			</p>
			<div class="flex flex-wrap justify-center gap-4">
				<a href="/contact" class="btn bg-white text-primary-600 hover:bg-gray-50">
					<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
					</svg>
					Start a Conversation
				</a>
				<a href="/work" class="btn bg-transparent text-white border-white hover:bg-white/10">
					<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2-2v2m8 0V6a2 2 0 012 2v6a2 2 0 01-2 2H6a2 2 0 01-2-2V8a2 2 0 012-2V6" />
					</svg>
					View All Work
				</a>
			</div>
		</div>
	</section>
</div>

<style>
	@keyframes slideUp {
		0% {
			transform: translateY(20px);
			opacity: 0;
		}
		100% {
			transform: translateY(0);
			opacity: 1;
		}
	}
	
	.animate-slide-up {
		animation: slideUp 0.6s ease-out forwards;
	}
</style>