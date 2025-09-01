<script lang="ts">
	import { onMount } from 'svelte';
	import { fade, fly } from 'svelte/transition';
	import type { PageData } from './$types';
	import PhilosophyCard from '$lib/components/work/PhilosophyCard.svelte';
	import TimelineItem from '$lib/components/work/TimelineItem.svelte';
	import TestimonialCard from '$lib/components/work/TestimonialCard.svelte';

	export let data: PageData;

	let mounted = false;
	let heroSection: HTMLElement;
	let observer: IntersectionObserver;

	onMount(() => {
		mounted = true;
		
		// Intersection observer for scroll animations
		if (typeof IntersectionObserver !== 'undefined') {
			observer = new IntersectionObserver(
				(entries) => {
					entries.forEach((entry) => {
						if (entry.isIntersecting) {
							entry.target.classList.add('animate-in');
						}
					});
				},
				{ threshold: 0.1, rootMargin: '50px' }
			);

			// Observe sections
			const sections = document.querySelectorAll('.observe-scroll');
			sections.forEach((section) => observer.observe(section));
		}

		return () => {
			if (observer) {
				observer.disconnect();
			}
		};
	});

	// Format numbers for stats display
	function formatStat(num: number): string {
		return num.toLocaleString();
	}
</script>

<svelte:head>
	<title>Teaching Philosophy & Experience - Brandon Lambert</title>
	<meta name="description" content="Explore my language teaching philosophy, educational career timeline, and testimonials from colleagues. Discover my 10 core principles for effective language education and cultural learning." />
	<meta property="og:title" content="Teaching Philosophy & Experience - Brandon Lambert" />
	<meta property="og:description" content="Explore my language teaching philosophy, educational career timeline, and testimonials from colleagues. Discover my 10 core principles for effective language education and cultural learning." />
	<meta property="og:type" content="website" />
</svelte:head>

<!-- Hero Section -->
<section 
	bind:this={heroSection}
	class="section bg-gradient-to-br from-primary-50 via-white to-secondary-50"
>
	<div class="container-wide">
		<div class="text-center max-w-4xl mx-auto">
			{#if mounted}
				<h1 
					class="text-4xl sm:text-5xl lg:text-6xl font-serif font-bold text-secondary-900 mb-6"
					in:fly={{ y: 30, duration: 800, delay: 200 }}
				>
					My Teaching & 
					<span class="text-gradient">Philosophy</span>
				</h1>
				
				<p 
					class="text-xl text-secondary-600 leading-relaxed max-w-3xl mx-auto mb-8"
					in:fly={{ y: 20, duration: 600, delay: 400 }}
				>
					Shaping meaningful language learning experiences. Here's how I approach every 
					educational opportunity with pedagogical expertise, cultural sensitivity, and innovation.
				</p>

				<!-- Stats Grid -->
				<div 
					class="grid grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8 mt-12"
					in:fade={{ duration: 800, delay: 600 }}
				>
					<div class="text-center">
						<div class="text-3xl lg:text-4xl font-bold text-primary-600 mb-2">
							{formatStat(data.stats.yearsExperience)}+
						</div>
						<div class="text-sm lg:text-base text-secondary-600 font-medium">
							Years in Education
						</div>
					</div>
					
					<div class="text-center">
						<div class="text-3xl lg:text-4xl font-bold text-primary-600 mb-2">
							{formatStat(data.stats.projectsCompleted)}+
						</div>
						<div class="text-sm lg:text-base text-secondary-600 font-medium">
							Lessons Taught
						</div>
					</div>
					
					<div class="text-center">
						<div class="text-3xl lg:text-4xl font-bold text-primary-600 mb-2">
							{formatStat(data.stats.clientsSatisfied)}+
						</div>
						<div class="text-sm lg:text-base text-secondary-600 font-medium">
							Students Inspired
						</div>
					</div>
					
					<div class="text-center">
						<div class="text-3xl lg:text-4xl font-bold text-primary-600 mb-2">
							{formatStat(data.stats.technologiesMastered)}+
						</div>
						<div class="text-sm lg:text-base text-secondary-600 font-medium">
							EdTech Tools
						</div>
					</div>
				</div>
			{/if}
		</div>
	</div>
</section>

<!-- Philosophy Section -->
<section class="section observe-scroll">
	<div class="container-wide">
		<div class="text-center mb-16">
			<h2 class="text-3xl lg:text-4xl font-serif font-bold text-secondary-900 mb-4">
				My Teaching <span class="text-gradient">Philosophy</span>
			</h2>
			<p class="text-lg text-secondary-600 max-w-3xl mx-auto">
				These 10 core principles guide every educational decision I make and every learning experience I design.
			</p>
		</div>

		<div class="grid gap-6 lg:gap-8 md:grid-cols-2">
			{#each data.philosophy as principle, index}
				<PhilosophyCard {principle} {index} />
			{/each}
		</div>
	</div>
</section>

<!-- Timeline Section -->
<section class="section bg-secondary-50/50 observe-scroll">
	<div class="container-wide">
		<div class="text-center mb-16">
			<h2 class="text-3xl lg:text-4xl font-serif font-bold text-secondary-900 mb-4">
				Educational <span class="text-gradient">Journey</span>
			</h2>
			<p class="text-lg text-secondary-600 max-w-3xl mx-auto">
				A timeline of my teaching career, educational background, and key achievements in language education.
			</p>
		</div>

		<div class="max-w-4xl mx-auto">
			{#each data.timeline as event, index}
				<TimelineItem 
					{event} 
					{index} 
					isLast={index === data.timeline.length - 1} 
				/>
			{/each}
		</div>
	</div>
</section>

<!-- Testimonials Section -->
<section class="section observe-scroll">
	<div class="container-wide">
		<div class="text-center mb-16">
			<h2 class="text-3xl lg:text-4xl font-serif font-bold text-secondary-900 mb-4">
				Colleague <span class="text-gradient">Testimonials</span>
			</h2>
			<p class="text-lg text-secondary-600 max-w-3xl mx-auto">
				What colleagues and educational partners say about working with me in language education.
			</p>
		</div>

		<div class="grid gap-6 lg:gap-8 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-2">
			{#each data.testimonials as testimonial, index}
				<TestimonialCard {testimonial} {index} />
			{/each}
		</div>
	</div>
</section>

<!-- CTA Section -->
<section class="section bg-gradient-to-br from-primary-600 to-primary-700 text-white observe-scroll">
	<div class="container-wide">
		<div class="text-center max-w-3xl mx-auto">
			<h2 class="text-3xl lg:text-4xl font-serif font-bold mb-6">
				Ready to Work Together?
			</h2>
			<p class="text-xl text-primary-100 leading-relaxed mb-8">
				Let's explore how we can create engaging language learning experiences with the same 
				dedication and pedagogical excellence that my colleagues and students have appreciated.
			</p>
			
			<div class="flex flex-col sm:flex-row gap-4 justify-center">
				<a 
					href="/contact"
					class="btn bg-white text-primary-600 hover:bg-primary-50 focus:ring-white shadow-lg"
				>
					Start a Conversation
				</a>
				<a 
					href="/agentic-ai"
					class="btn bg-transparent text-white hover:bg-white/10 focus:ring-white border border-white/30 hover:border-white/50"
				>
					Explore AI Projects
				</a>
			</div>
		</div>
	</div>
</section>

<style>
	:global(.observe-scroll) {
		opacity: 0;
		transform: translateY(30px);
		transition: all 0.8s ease-out;
	}

	:global(.observe-scroll.animate-in) {
		opacity: 1;
		transform: translateY(0);
	}

	/* Responsive grid adjustments */
	@media (min-width: 1536px) {
		.grid.xl\:grid-cols-2 {
			grid-template-columns: repeat(2, minmax(0, 1fr));
		}
	}
</style>