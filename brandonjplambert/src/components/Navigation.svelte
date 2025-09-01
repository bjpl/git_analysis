<script>
  import { onMount } from 'svelte';
  
  let mobileMenuOpen = false;
  let scrolled = false;

  const toggleMobileMenu = () => {
    mobileMenuOpen = !mobileMenuOpen;
  };

  onMount(() => {
    const handleScroll = () => {
      scrolled = window.scrollY > 20;
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  });

  const navItems = [
    { name: 'Home', href: '#home' },
    { name: 'Work', href: '#work' },
    { name: 'Agentic AI', href: '#ai' },
    { name: 'Resources', href: '#resources' },
    { name: 'Contact', href: '#contact' }
  ];
</script>

<nav class="fixed top-0 left-0 right-0 z-50 transition-all duration-300 {scrolled ? 'bg-white/95 backdrop-blur-md shadow-lg' : 'bg-transparent'}">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex justify-between items-center py-4">
      <!-- Logo/Brand -->
      <div class="flex-shrink-0">
        <a href="#home" class="text-2xl font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">
          BJ Lambert
        </a>
      </div>

      <!-- Desktop Navigation -->
      <div class="hidden md:block">
        <div class="ml-10 flex items-baseline space-x-8">
          {#each navItems as item}
            <a 
              href={item.href}
              class="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium transition-colors duration-200 hover:bg-blue-50 rounded-lg"
            >
              {item.name}
            </a>
          {/each}
        </div>
      </div>

      <!-- Mobile menu button -->
      <div class="md:hidden">
        <button 
          on:click={toggleMobileMenu}
          class="inline-flex items-center justify-center p-2 rounded-md text-gray-700 hover:text-blue-600 hover:bg-blue-50 transition-colors duration-200"
          aria-label="Toggle mobile menu"
        >
          <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            {#if !mobileMenuOpen}
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            {:else}
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            {/if}
          </svg>
        </button>
      </div>
    </div>

    <!-- Mobile Navigation -->
    {#if mobileMenuOpen}
      <div class="md:hidden bg-white rounded-lg shadow-lg mt-2 mb-4 border border-gray-100">
        <div class="px-2 pt-2 pb-3 space-y-1">
          {#each navItems as item}
            <a 
              href={item.href}
              on:click={() => mobileMenuOpen = false}
              class="text-gray-700 hover:text-blue-600 hover:bg-blue-50 block px-3 py-2 text-base font-medium rounded-lg transition-colors duration-200"
            >
              {item.name}
            </a>
          {/each}
        </div>
      </div>
    {/if}
  </div>
</nav>