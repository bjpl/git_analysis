<script lang="ts">
	import '../app-minimal.css';
	import { onMount } from 'svelte';
	import { dev } from '$app/environment';
	import Header from '$lib/components/layout/Header.svelte';
	import Footer from '$lib/components/layout/Footer.svelte';

	// Add smooth scrolling behavior and performance optimizations
	onMount(() => {
		// Reduce motion for users who prefer it
		const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
		if (prefersReducedMotion.matches) {
			document.documentElement.style.scrollBehavior = 'auto';
		}
	});
</script>

<svelte:head>
	<title>Professional Portfolio</title>
</svelte:head>

<div class="flex min-h-screen flex-col">
	<Header />
	
	<main class="flex-1">
		<slot />
	</main>
	
	<Footer />
</div>

{#if dev}
	<!-- Development indicator -->
	<div class="fixed bottom-4 right-4 z-50 rounded-full bg-orange-500 px-3 py-1 text-xs font-medium text-white shadow-lg">
		DEV
	</div>
{/if}