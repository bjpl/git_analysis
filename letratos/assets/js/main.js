// Main JavaScript file for Letratos

// Video control functions
function toggleVideo(video) {
  if (video.paused) {
    video.play();
    video.classList.remove('video-paused');
    video.classList.add('playing');
  } else {
    video.pause();
    video.classList.add('video-paused');
    video.classList.remove('playing');
  }
}

function togglePoemVideo(video) {
  if (video.paused) {
    video.play();
    video.classList.remove('paused');
    video.classList.add('playing');
  } else {
    video.pause();
    video.classList.add('paused');
    video.classList.remove('playing');
  }
}

// Lightbox functions
function openLightbox(src, caption) {
  const lightbox = document.getElementById('lightbox');
  const img = document.getElementById('lightbox-img');
  const captionText = document.getElementById('lightbox-caption');
  
  if (lightbox && img) {
    lightbox.classList.add('active');
    img.src = src;
    if (captionText) {
      captionText.textContent = caption || '';
    }
    document.body.style.overflow = 'hidden';
  }
}

function closeLightbox() {
  const lightbox = document.getElementById('lightbox');
  if (lightbox) {
    lightbox.classList.remove('active');
    document.body.style.overflow = 'auto';
  }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
  // Initialize gallery videos
  const galleryVideos = document.querySelectorAll('.gallery-video');
  galleryVideos.forEach(video => {
    video.play().catch(e => {
      // If autoplay fails, add paused class
      video.classList.add('video-paused');
    });
  });
  
  // Initialize poem videos
  const poemVideos = document.querySelectorAll('.sketch-video');
  poemVideos.forEach(video => {
    video.play().catch(e => {
      // If autoplay fails, add paused class
      video.classList.add('paused');
    });
  });
  
  // Keyboard shortcuts
  document.addEventListener('keydown', function(e) {
    // Escape key closes lightbox
    if (e.key === 'Escape') {
      closeLightbox();
    }
  });
  
  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });
  
  // Add loading state for slow images
  const images = document.querySelectorAll('img[loading="lazy"]');
  images.forEach(img => {
    img.addEventListener('load', function() {
      this.classList.add('loaded');
    });
  });
  
  // Navigation active state based on current path
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-links a').forEach(link => {
    const href = link.getAttribute('href');
    if (href && currentPath.includes(href.replace(/\/$/, ''))) {
      link.classList.add('active');
    }
  });
});

// Export functions for global use
window.toggleVideo = toggleVideo;
window.togglePoemVideo = togglePoemVideo;
window.openLightbox = openLightbox;
window.closeLightbox = closeLightbox;