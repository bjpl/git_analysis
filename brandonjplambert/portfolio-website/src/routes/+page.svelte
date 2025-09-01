<script lang="ts">
	import Hero from '$lib/components/sections/Hero.svelte';
	import About from '$lib/components/sections/About.svelte';
	import Projects from '$lib/components/sections/Projects.svelte';
	import Contact from '$lib/components/sections/Contact.svelte';

	export let data: any; // Will be properly typed once Prismic types are generated
</script>

<svelte:head>
	<title>Brandon Lambert - Language Learning & Teaching Specialist</title>
	<meta name="description" content="Fourth-generation educator with MA-TESOL and 10 years in language education and edtech. Fluent in English and Spanish, exploring AI-powered learning opportunities." />
</svelte:head>

<!-- Hero Section -->
<Hero {data} />

<!-- About Section -->
<About />

<!-- Projects Section -->
<Projects />

<!-- Contact Section -->
<Contact />