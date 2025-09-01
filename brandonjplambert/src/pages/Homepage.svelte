<script>
  import Navigation from '../components/Navigation.svelte';
  import HeroSection from '../components/HeroSection.svelte';
  import { onMount } from 'svelte';

  // Add smooth scroll behavior and mobile menu functionality
  onMount(() => {
    // Smooth scroll for navigation links
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const target = document.querySelector(link.getAttribute('href'));
        if (target) {
          target.scrollIntoView({ behavior: 'smooth' });
        }
      });
    });
  });
</script>

<main class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
  <Navigation />
  <HeroSection />
</main>

<style>
  :global(body) {
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
  }
</style>