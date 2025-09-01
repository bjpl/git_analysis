<script lang="ts">
  import type { PageData } from './$types';
  import { onMount } from 'svelte';
  import type { ContentCategory } from '$lib/types';

  export let data: PageData;

  // Search and filter state
  let searchTerm = '';
  let selectedCategory: ContentCategory | 'all' = 'all';
  let selectedCountry = 'all';
  let selectedSubcategory = 'all';
  let expandedAccounts = new Set<string>();

  // Filter functions
  $: filteredAccounts = data.instagramAccounts.filter(account => {
    const matchesSearch = searchTerm === '' || 
      account.handle.toLowerCase().includes(searchTerm.toLowerCase()) ||
      account.description.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesCategory = selectedCategory === 'all' || account.category === selectedCategory;
    const matchesCountry = selectedCountry === 'all' || account.country === selectedCountry;
    const matchesSubcategory = selectedSubcategory === 'all' || account.subcategory === selectedSubcategory;
    
    return matchesSearch && matchesCategory && matchesCountry && matchesSubcategory;
  });

  // Get unique subcategories for selected category
  $: subcategories = selectedCategory === 'all' 
    ? [...new Set(data.instagramAccounts.map(a => a.subcategory).filter(Boolean))]
    : [...new Set(data.instagramAccounts
        .filter(a => a.category === selectedCategory)
        .map(a => a.subcategory)
        .filter(Boolean)
      )];

  // Statistics
  $: categoryStats = data.categories.map(category => ({
    name: category,
    count: data.instagramAccounts.filter(a => a.category === category).length
  }));

  function toggleExpanded(handle: string) {
    if (expandedAccounts.has(handle)) {
      expandedAccounts.delete(handle);
    } else {
      expandedAccounts.add(handle);
    }
    expandedAccounts = expandedAccounts;
  }

  function resetFilters() {
    searchTerm = '';
    selectedCategory = 'all';
    selectedCountry = 'all';
    selectedSubcategory = 'all';
    expandedAccounts.clear();
    expandedAccounts = expandedAccounts;
  }

  // Tool categories for organization
  $: toolsByCategory = data.learningTools.reduce((acc, tool) => {
    if (!acc[tool.category]) {
      acc[tool.category] = [];
    }
    acc[tool.category].push(tool);
    return acc;
  }, {} as Record<string, typeof data.learningTools>);

  onMount(() => {
    // Any initialization if needed
  });
</script>

<svelte:head>
  <title>{data.meta.title}</title>
  <meta name="description" content={data.meta.description} />
  <meta name="keywords" content={data.meta.keywords} />
</svelte:head>

<main class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
  <!-- Hero Section -->
  <section class="relative py-20 px-4">
    <div class="max-w-6xl mx-auto text-center">
      <h1 class="text-5xl font-bold text-gray-900 mb-6 bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
        Spanish Learning Resources
      </h1>
      <p class="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
        A comprehensive collection of tools, methods, and curated content for mastering Spanish. 
        From AI-powered learning to authentic cultural immersion.
      </p>
    </div>
  </section>

  <!-- SECTION 1: Learning Tools & Methods -->
  <section class="py-16 px-4 bg-white/80 backdrop-blur-sm">
    <div class="max-w-6xl mx-auto">
      <!-- Journey Stats Hero -->
      <div class="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl p-8 mb-12 text-white">
        <div class="grid md:grid-cols-4 gap-6 items-center">
          <div class="text-center">
            <div class="text-3xl font-bold">{data.journeyStats.currentLevel}</div>
            <div class="text-blue-100">Current Level</div>
          </div>
          <div class="text-center">
            <div class="text-3xl font-bold">{data.journeyStats.totalHours}+</div>
            <div class="text-blue-100">Study Hours</div>
          </div>
          <div class="text-center">
            <div class="text-3xl font-bold">{data.journeyStats.immersionPlanned.location}</div>
            <div class="text-blue-100">Immersion {data.journeyStats.immersionPlanned.year}</div>
          </div>
          <div class="text-center">
            <div class="text-3xl font-bold">🇨🇴🇻🇪</div>
            <div class="text-blue-100">Tutor Origins</div>
          </div>
        </div>
        
        <div class="mt-6 pt-6 border-t border-blue-400">
          <h3 class="text-lg font-semibold mb-3">Key Milestones</h3>
          <div class="grid sm:grid-cols-2 gap-3">
            {#each data.journeyStats.milestones as milestone}
              <div class="flex items-center space-x-2">
                <span class="text-green-300">✓</span>
                <span class="text-sm">{milestone}</span>
              </div>
            {/each}
          </div>
        </div>
      </div>

      <!-- Learning Tools Grid -->
      <h2 class="text-3xl font-bold text-gray-900 mb-8 text-center">Learning Tools & Methods</h2>
      
      {#each Object.entries(toolsByCategory) as [category, tools]}
        <div class="mb-12">
          <h3 class="text-2xl font-semibold text-gray-800 mb-6 flex items-center">
            <span class="inline-block w-1 h-8 bg-blue-600 mr-3 rounded"></span>
            {category}
          </h3>
          
          <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each tools as tool}
              <div class="bg-white rounded-xl shadow-lg border border-gray-100 p-6 hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
                <div class="flex items-center mb-4">
                  <span class="text-3xl mr-3">{tool.icon}</span>
                  <div>
                    <h4 class="text-lg font-semibold text-gray-900">{tool.name}</h4>
                    {#if tool.link}
                      <a href={tool.link} target="_blank" rel="noopener noreferrer" class="text-blue-600 text-sm hover:underline">
                        Visit Site →
                      </a>
                    {/if}
                  </div>
                </div>
                
                <p class="text-gray-600 text-sm mb-4">{tool.description}</p>
                
                <div class="space-y-3">
                  <div>
                    <h5 class="font-medium text-gray-800 text-sm mb-1">Use Case</h5>
                    <p class="text-gray-600 text-sm">{tool.useCase}</p>
                  </div>
                  
                  <div>
                    <h5 class="font-medium text-gray-800 text-sm mb-1">How I Use It</h5>
                    <p class="text-gray-600 text-sm">{tool.howIUseIt}</p>
                  </div>
                  
                  {#if tool.stats}
                    <div class="pt-3 border-t border-gray-100">
                      {#if tool.stats.hours}
                        <div class="flex items-center justify-between text-sm">
                          <span class="text-gray-500">Hours Logged:</span>
                          <span class="font-medium text-blue-600">{tool.stats.hours}+</span>
                        </div>
                      {/if}
                      {#if tool.stats.achievements}
                        <div class="mt-2">
                          {#each tool.stats.achievements as achievement}
                            <span class="inline-block bg-green-100 text-green-700 text-xs px-2 py-1 rounded-full mr-1 mb-1">
                              ✓ {achievement}
                            </span>
                          {/each}
                        </div>
                      {/if}
                    </div>
                  {/if}
                </div>
              </div>
            {/each}
          </div>
        </div>
      {/each}
    </div>
  </section>

  <!-- SECTION 2: Curated Spanish Content -->
  <section class="py-16 px-4 bg-slate-50">
    <div class="max-w-7xl mx-auto">
      <h2 class="text-3xl font-bold text-gray-900 mb-8 text-center">Curated Spanish Content Directory</h2>
      
      <!-- Quick Stats Dashboard -->
      <div class="bg-white rounded-xl shadow-lg p-6 mb-8">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">Content Distribution</h3>
        <div class="grid sm:grid-cols-3 lg:grid-cols-5 gap-4">
          {#each categoryStats as stat}
            <div class="text-center p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg">
              <div class="text-2xl font-bold text-blue-600">{stat.count}</div>
              <div class="text-sm text-gray-600 mt-1">{stat.name}</div>
            </div>
          {/each}
        </div>
        <div class="mt-4 p-4 bg-gray-50 rounded-lg">
          <div class="text-center">
            <span class="text-2xl font-bold text-gray-900">{data.instagramAccounts.length}</span>
            <span class="text-gray-600 ml-2">Total Accounts</span>
          </div>
        </div>
      </div>

      <!-- Search and Filters -->
      <div class="bg-white rounded-xl shadow-lg p-6 mb-8">
        <div class="grid md:grid-cols-2 lg:grid-cols-5 gap-4 items-end">
          <div>
            <label for="search-input" class="block text-sm font-medium text-gray-700 mb-2">Search</label>
            <input
              id="search-input"
              type="text"
              bind:value={searchTerm}
              placeholder="Search handles or descriptions..."
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          
          <div>
            <label for="category-select" class="block text-sm font-medium text-gray-700 mb-2">Category</label>
            <select id="category-select" bind:value={selectedCategory} class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
              <option value="all">All Categories</option>
              {#each data.categories as category}
                <option value={category}>{category}</option>
              {/each}
            </select>
          </div>
          
          <div>
            <label for="country-select" class="block text-sm font-medium text-gray-700 mb-2">Country</label>
            <select id="country-select" bind:value={selectedCountry} class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
              <option value="all">All Countries</option>
              {#each data.countries as country}
                <option value={country}>{country}</option>
              {/each}
            </select>
          </div>
          
          <div>
            <label for="subcategory-select" class="block text-sm font-medium text-gray-700 mb-2">Subcategory</label>
            <select id="subcategory-select" bind:value={selectedSubcategory} class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
              <option value="all">All Subcategories</option>
              {#each subcategories as subcategory}
                <option value={subcategory}>{subcategory}</option>
              {/each}
            </select>
          </div>
          
          <button
            on:click={resetFilters}
            class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            Clear Filters
          </button>
        </div>
        
        <div class="mt-4 text-sm text-gray-600">
          Showing {filteredAccounts.length} of {data.instagramAccounts.length} accounts
        </div>
      </div>

      <!-- Instagram Accounts Directory -->
      <div class="bg-white rounded-xl shadow-lg overflow-hidden">
        <div class="overflow-x-auto">
          <div class="max-h-96 overflow-y-auto">
            {#each filteredAccounts as account}
              <div class="border-b border-gray-100 last:border-b-0">
                <div class="p-4 hover:bg-gray-50 transition-colors">
                  <div class="flex items-center justify-between">
                    <div class="flex-1 min-w-0">
                      <div class="flex items-center space-x-3">
                        <div class="flex-shrink-0">
                          <a
                            href={account.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            class="text-blue-600 hover:text-blue-800 font-medium"
                          >
                            {account.handle}
                          </a>
                          {#if account.verified}
                            <span class="text-blue-500 ml-1">✓</span>
                          {/if}
                        </div>
                        
                        <div class="flex-1 min-w-0">
                          <p class="text-gray-900 text-sm truncate">{account.description}</p>
                        </div>
                      </div>
                      
                      <div class="mt-2 flex flex-wrap items-center space-x-4 text-xs text-gray-500">
                        <span class="inline-flex items-center px-2 py-1 rounded-full bg-blue-100 text-blue-700">
                          {account.category}
                        </span>
                        {#if account.subcategory}
                          <span class="inline-flex items-center px-2 py-1 rounded-full bg-gray-100 text-gray-700">
                            {account.subcategory}
                          </span>
                        {/if}
                        <span class="inline-flex items-center">
                          🌍 {account.country}
                        </span>
                        {#if account.followers}
                          <span class="inline-flex items-center">
                            👥 {account.followers}
                          </span>
                        {/if}
                      </div>
                    </div>
                    
                    <button
                      on:click={() => toggleExpanded(account.handle)}
                      class="ml-4 p-2 text-gray-400 hover:text-gray-600 transition-colors"
                      aria-label="Toggle details"
                    >
                      <svg
                        class="w-5 h-5 transform transition-transform {expandedAccounts.has(account.handle) ? 'rotate-180' : ''}"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                  </div>
                  
                  {#if expandedAccounts.has(account.handle)}
                    <div class="mt-4 p-4 bg-gray-50 rounded-lg">
                      <div class="grid sm:grid-cols-2 gap-4 text-sm">
                        <div>
                          <span class="font-medium text-gray-700">Full Description:</span>
                          <p class="text-gray-600 mt-1">{account.description}</p>
                        </div>
                        <div class="space-y-2">
                          <div class="flex justify-between">
                            <span class="font-medium text-gray-700">Category:</span>
                            <span class="text-gray-600">{account.category}</span>
                          </div>
                          {#if account.subcategory}
                            <div class="flex justify-between">
                              <span class="font-medium text-gray-700">Subcategory:</span>
                              <span class="text-gray-600">{account.subcategory}</span>
                            </div>
                          {/if}
                          <div class="flex justify-between">
                            <span class="font-medium text-gray-700">Country:</span>
                            <span class="text-gray-600">{account.country}</span>
                          </div>
                          {#if account.followers}
                            <div class="flex justify-between">
                              <span class="font-medium text-gray-700">Followers:</span>
                              <span class="text-gray-600">{account.followers}</span>
                            </div>
                          {/if}
                          <div class="flex justify-between">
                            <span class="font-medium text-gray-700">Verified:</span>
                            <span class="text-gray-600">{account.verified ? 'Yes' : 'No'}</span>
                          </div>
                        </div>
                      </div>
                      <div class="mt-4">
                        <a
                          href={account.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                        >
                          Visit Instagram
                          <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                          </svg>
                        </a>
                      </div>
                    </div>
                  {/if}
                </div>
              </div>
            {/each}
          </div>
        </div>
        
        {#if filteredAccounts.length === 0}
          <div class="p-8 text-center text-gray-500">
            <svg class="w-12 h-12 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <p class="text-lg font-medium">No accounts found</p>
            <p class="text-sm mt-1">Try adjusting your search criteria or clearing filters</p>
          </div>
        {/if}
      </div>
    </div>
  </section>
</main>

<style>
  /* Custom scrollbar for the accounts directory */
  .overflow-y-auto::-webkit-scrollbar {
    width: 6px;
  }
  
  .overflow-y-auto::-webkit-scrollbar-track {
    background: #f1f5f9;
  }
  
  .overflow-y-auto::-webkit-scrollbar-thumb {
    background: #cbd5e1;
    border-radius: 3px;
  }
  
  .overflow-y-auto::-webkit-scrollbar-thumb:hover {
    background: #94a3b8;
  }
</style>