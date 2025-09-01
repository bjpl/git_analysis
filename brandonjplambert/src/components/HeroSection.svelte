<script>
  import SocialLinks from './SocialLinks.svelte';
</script>

<section id="home" class="relative pt-20 pb-16 md:pt-32 md:pb-24">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
      
      <!-- Content Column -->
      <div class="order-2 lg:order-1">
        <!-- Main Headline -->
        <h1 class="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 leading-tight mb-6">
          <span class="bg-gradient-to-r from-blue-600 via-blue-700 to-blue-800 bg-clip-text text-transparent">
            Language Learning
          </span>
          <br>
          <span class="text-gray-800">& Teaching</span>
        </h1>

        <!-- Bio Section -->
        <div class="prose prose-lg max-w-none mb-8">
          <p class="text-xl text-gray-600 leading-relaxed mb-6">
            <span class="font-semibold text-gray-800">Fourth-generation educator</span> with MA-TESOL and 10 years in language education and edtech.
          </p>
          
          <div class="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-blue-100">
            <p class="text-gray-700 leading-relaxed mb-4">
              Fluent in <span class="font-semibold text-blue-700">English</span> (native) and 
              <span class="font-semibold text-blue-700">Spanish</span> (B2/ACTFL Advanced Low/Mid), 
              currently exploring new opportunities in language education and AI-powered learning.
            </p>
            
            <!-- Key Skills/Highlights -->
            <div class="flex flex-wrap gap-2 mt-4">
              <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                MA-TESOL
              </span>
              <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                10+ Years Experience
              </span>
              <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                EdTech Innovation
              </span>
              <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                AI-Powered Learning
              </span>
            </div>
          </div>
        </div>

        <!-- Social Links -->
        <SocialLinks />

        <!-- CTA Buttons -->
        <div class="flex flex-col sm:flex-row gap-4 mt-8">
          <a 
            href="#work" 
            class="inline-flex items-center justify-center px-8 py-4 bg-gradient-to-r from-blue-600 to-blue-700 text-white font-semibold rounded-xl hover:from-blue-700 hover:to-blue-800 transform hover:scale-105 transition-all duration-200 shadow-lg hover:shadow-xl"
          >
            View My Work
            <svg class="ml-2 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </a>
          
          <a 
            href="#contact" 
            class="inline-flex items-center justify-center px-8 py-4 bg-white text-blue-700 font-semibold rounded-xl border-2 border-blue-200 hover:border-blue-300 hover:bg-blue-50 transform hover:scale-105 transition-all duration-200 shadow-md hover:shadow-lg"
          >
            Get In Touch
            <svg class="ml-2 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-3.582 8-8 8a8.959 8.959 0 01-4.906-1.447L3 21l2.447-5.094A8.959 8.959 0 013 12c0-4.418 3.582-8 8-8s8 3.582 8 8z" />
            </svg>
          </a>
        </div>
      </div>

      <!-- Image Column -->
      <div class="order-1 lg:order-2 flex justify-center lg:justify-end">
        <div class="relative">
          <!-- Background Decorations -->
          <div class="absolute -inset-4 bg-gradient-to-r from-blue-200 to-blue-300 rounded-full opacity-20 animate-pulse"></div>
          <div class="absolute -inset-2 bg-gradient-to-r from-blue-300 to-blue-400 rounded-full opacity-30"></div>
          
          <!-- Profile Image -->
          <div class="relative z-10 w-80 h-80 md:w-96 md:h-96 rounded-full overflow-hidden shadow-2xl border-4 border-white">
            <img 
              src="/headshot.jpg" 
              alt="Brandon J. Lambert - Professional Headshot"
              class="w-full h-full object-cover"
              loading="eager"
            />
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Background Gradient Elements -->
  <div class="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
    <div class="absolute top-1/4 right-0 w-96 h-96 bg-gradient-to-l from-blue-100 to-transparent rounded-full opacity-50 transform translate-x-1/2"></div>
    <div class="absolute bottom-0 left-0 w-80 h-80 bg-gradient-to-r from-blue-50 to-transparent rounded-full opacity-30 transform -translate-x-1/2"></div>
  </div>
</section>