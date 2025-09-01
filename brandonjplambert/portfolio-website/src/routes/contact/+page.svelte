<script lang="ts">
  import { onMount } from 'svelte';
  import ContactForm from '$lib/components/contact/ContactForm.svelte';
  import type { ContactFormData, FormState } from '$lib/types/contact';
  import { page } from '$app/stores';

  // EmailJS configuration
  let emailJS: any;
  const EMAILJS_SERVICE_ID = 'service_portfolio'; // Replace with your EmailJS service ID
  const EMAILJS_TEMPLATE_ID = 'template_contact'; // Replace with your EmailJS template ID  
  const EMAILJS_PUBLIC_KEY = 'your_public_key_here'; // Replace with your EmailJS public key

  let formState: FormState = {
    isSubmitting: false,
    isSubmitted: false,
    error: null
  };

  onMount(async () => {
    // Load EmailJS dynamically
    try {
      const emailJSModule = await import('@emailjs/browser');
      emailJS = emailJSModule.default;
      emailJS.init(EMAILJS_PUBLIC_KEY);
    } catch (error) {
      console.error('Failed to load EmailJS:', error);
    }
  });

  async function handleFormSubmit(event: CustomEvent<ContactFormData>) {
    const formData = event.detail;
    
    formState = {
      ...formState,
      isSubmitting: true,
      error: null
    };

    try {
      if (!emailJS) {
        throw new Error('EmailJS is not loaded');
      }

      // Send email using EmailJS
      const result = await emailJS.send(
        EMAILJS_SERVICE_ID,
        EMAILJS_TEMPLATE_ID,
        {
          from_name: formData.name,
          from_email: formData.email,
          subject: formData.subject,
          message: formData.message,
          to_email: 'brandon.lambert87@gmail.com'
        }
      );

      console.log('Email sent successfully:', result);
      
      formState = {
        isSubmitting: false,
        isSubmitted: true,
        error: null
      };

      // Reset form after success (optional)
      setTimeout(() => {
        formState = {
          isSubmitting: false,
          isSubmitted: false,
          error: null
        };
      }, 5000);

    } catch (error) {
      console.error('Failed to send email:', error);
      
      formState = {
        isSubmitting: false,
        isSubmitted: false,
        error: error instanceof Error ? error.message : 'Failed to send message. Please try again.'
      };
    }
  }
</script>

<svelte:head>
  <title>Contact - Brandon Lambert | Software Engineer & Data Scientist</title>
  <meta name="description" content="Get in touch with Brandon Lambert for software engineering, data science, and AI projects. Contact form available for collaboration opportunities." />
  <meta name="keywords" content="contact, software engineer, data scientist, collaboration, projects, hire developer" />
  <meta property="og:title" content="Contact Brandon Lambert" />
  <meta property="og:description" content="Get in touch for software engineering, data science, and AI projects." />
  <meta property="og:type" content="website" />
  <meta name="robots" content="index, follow" />
</svelte:head>

<main class="contact-page">
  <div class="container">
    <!-- Header Section -->
    <section class="contact-header">
      <div class="header-content">
        <h1 class="page-title">
          Let's Work <span class="gradient-text">Together</span>
        </h1>
        <p class="page-description">
          Have a project in mind? Looking for collaboration? Or just want to say hello? 
          I'd love to hear from you. Drop me a message and let's create something amazing together.
        </p>
      </div>
    </section>

    <!-- Contact Information -->
    <section class="contact-info">
      <div class="info-grid">
        <div class="info-card">
          <div class="info-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
              <circle cx="12" cy="10" r="3"></circle>
            </svg>
          </div>
          <div class="info-content">
            <h3>Location</h3>
            <p class="location-transition">
              <span class="current-location">Mountain View, CA</span>
              <span class="transition-arrow">→</span>
              <span class="future-location">Medellín, Colombia (2025)</span>
            </p>
          </div>
        </div>

        <div class="info-card">
          <div class="info-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
              <polyline points="22,6 12,13 2,6"></polyline>
            </svg>
          </div>
          <div class="info-content">
            <h3>Email</h3>
            <a href="mailto:brandon.lambert87@gmail.com" class="contact-link">
              brandon.lambert87@gmail.com
            </a>
          </div>
        </div>

        <div class="info-card">
          <div class="info-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 19c-5 1-5-5-7-5m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path>
            </svg>
          </div>
          <div class="info-content">
            <h3>GitHub</h3>
            <a href="https://github.com/bjpl" target="_blank" rel="noopener noreferrer" class="contact-link">
              github.com/bjpl
            </a>
          </div>
        </div>

        <div class="info-card">
          <div class="info-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path>
              <rect x="2" y="9" width="4" height="12"></rect>
              <circle cx="4" cy="4" r="2"></circle>
            </svg>
          </div>
          <div class="info-content">
            <h3>LinkedIn</h3>
            <a href="https://linkedin.com/in/brandonjplambert" target="_blank" rel="noopener noreferrer" class="contact-link">
              linkedin.com/in/brandonjplambert
            </a>
          </div>
        </div>
      </div>
    </section>

    <!-- Contact Form Section -->
    <section class="contact-form-section">
      <div class="form-container">
        <div class="form-header">
          <h2>Send Me a Message</h2>
          <p>Fill out the form below and I'll get back to you as soon as possible.</p>
        </div>
        
        <ContactForm 
          {formState} 
          on:submit={handleFormSubmit}
        />
      </div>
    </section>

    <!-- Alternative Contact Methods -->
    <section class="alternative-contact">
      <div class="alt-contact-content">
        <h3>Other Ways to Connect</h3>
        <p>
          Prefer a more direct approach? Feel free to reach out through any of these channels:
        </p>
        
        <div class="social-links">
          <a 
            href="https://linkedin.com/in/brandonjplambert" 
            target="_blank" 
            rel="noopener noreferrer" 
            class="social-link linkedin"
            aria-label="Connect on LinkedIn"
          >
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path>
              <rect x="2" y="9" width="4" height="12"></rect>
              <circle cx="4" cy="4" r="2"></circle>
            </svg>
            LinkedIn
          </a>
          
          <a 
            href="https://github.com/bjpl" 
            target="_blank" 
            rel="noopener noreferrer" 
            class="social-link github"
            aria-label="View GitHub profile"
          >
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M9 19c-5 1-5-5-7-5m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path>
            </svg>
            GitHub
          </a>
          
          <a 
            href="mailto:brandon.lambert87@gmail.com" 
            class="social-link email"
            aria-label="Send email"
          >
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
              <polyline points="22,6 12,13 2,6"></polyline>
            </svg>
            Email
          </a>
        </div>
      </div>
    </section>
  </div>
</main>

<style>
  .contact-page {
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding-top: 2rem;
  }

  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 2rem;
  }

  /* Header Section */
  .contact-header {
    text-align: center;
    margin-bottom: 4rem;
  }

  .header-content {
    max-width: 800px;
    margin: 0 auto;
  }

  .page-title {
    font-size: clamp(2.5rem, 5vw, 4rem);
    font-weight: 800;
    margin-bottom: 1.5rem;
    line-height: 1.1;
  }

  .gradient-text {
    background: linear-gradient(135deg, #60a5fa, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .page-description {
    font-size: 1.25rem;
    line-height: 1.7;
    opacity: 0.9;
    max-width: 600px;
    margin: 0 auto;
  }

  /* Contact Information */
  .contact-info {
    margin-bottom: 4rem;
  }

  .info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 2rem;
  }

  .info-card {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 1rem;
    padding: 2rem;
    text-align: center;
    transition: all 0.3s ease;
  }

  .info-card:hover {
    transform: translateY(-5px);
    background: rgba(255, 255, 255, 0.15);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  }

  .info-icon {
    width: 3rem;
    height: 3rem;
    margin: 0 auto 1rem;
    color: #60a5fa;
  }

  .info-icon svg {
    width: 100%;
    height: 100%;
  }

  .info-content h3 {
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
  }

  .location-transition {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.75rem;
    flex-wrap: wrap;
  }

  .current-location {
    opacity: 0.8;
  }

  .transition-arrow {
    color: #60a5fa;
    font-weight: bold;
  }

  .future-location {
    color: #a78bfa;
    font-weight: 600;
  }

  .contact-link {
    color: #60a5fa;
    text-decoration: none;
    transition: color 0.2s ease;
  }

  .contact-link:hover {
    color: #a78bfa;
    text-decoration: underline;
  }

  /* Contact Form Section */
  .contact-form-section {
    margin-bottom: 4rem;
  }

  .form-container {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    border-radius: 2rem;
    padding: 3rem;
    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.1);
    color: #1f2937;
  }

  .form-header {
    text-align: center;
    margin-bottom: 2rem;
  }

  .form-header h2 {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    color: #1f2937;
  }

  .form-header p {
    color: #6b7280;
    font-size: 1.1rem;
  }

  /* Alternative Contact */
  .alternative-contact {
    text-align: center;
    margin-bottom: 4rem;
  }

  .alt-contact-content {
    max-width: 600px;
    margin: 0 auto;
  }

  .alt-contact-content h3 {
    font-size: 1.75rem;
    font-weight: 700;
    margin-bottom: 1rem;
  }

  .alt-contact-content p {
    font-size: 1.1rem;
    opacity: 0.9;
    margin-bottom: 2rem;
  }

  .social-links {
    display: flex;
    justify-content: center;
    gap: 1.5rem;
    flex-wrap: wrap;
  }

  .social-link {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem 1.5rem;
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 0.75rem;
    color: white;
    text-decoration: none;
    font-weight: 500;
    transition: all 0.3s ease;
  }

  .social-link svg {
    width: 1.25rem;
    height: 1.25rem;
  }

  .social-link:hover {
    transform: translateY(-2px);
    background: rgba(255, 255, 255, 0.2);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  }

  .social-link.linkedin:hover {
    background: #0077b5;
    border-color: #0077b5;
  }

  .social-link.github:hover {
    background: #333;
    border-color: #333;
  }

  .social-link.email:hover {
    background: #ea4335;
    border-color: #ea4335;
  }

  /* Mobile Responsiveness */
  @media (max-width: 768px) {
    .container {
      padding: 0 1rem;
    }

    .contact-header {
      margin-bottom: 3rem;
    }

    .page-title {
      font-size: 2.5rem;
    }

    .page-description {
      font-size: 1.1rem;
    }

    .info-grid {
      grid-template-columns: 1fr;
      gap: 1.5rem;
    }

    .info-card {
      padding: 1.5rem;
    }

    .form-container {
      padding: 2rem 1.5rem;
      border-radius: 1.5rem;
    }

    .form-header h2 {
      font-size: 1.75rem;
    }

    .location-transition {
      flex-direction: column;
      gap: 0.5rem;
    }

    .social-links {
      flex-direction: column;
      align-items: center;
      gap: 1rem;
    }

    .social-link {
      width: 100%;
      max-width: 200px;
      justify-content: center;
    }
  }

  @media (max-width: 480px) {
    .contact-page {
      padding-top: 1rem;
    }

    .page-title {
      font-size: 2rem;
    }

    .form-container {
      padding: 1.5rem 1rem;
    }

    .info-card {
      padding: 1rem;
    }
  }
</style>