# Asset Files Guide

## Overview
Asset files include images, fonts, audio, and video resources that enhance user interfaces and user experiences. This guide covers essential asset file types and optimization strategies.

## File Types Reference

| **Asset Type** | **Core Files** | **Supporting Files** | **Purpose** |
|---------------|----------------|---------------------|------------|
| **Images** | `.png`, `.jpg`, `.jpeg` | `.gif`, `.webp`, `.ico` | Graphics, photos, icons |
| **Vector Graphics** | `.svg` | `.ai`, `.eps` | Scalable graphics and icons |
| **Fonts** | `.woff`, `.woff2` | `.ttf`, `.otf`, `.eot` | Typography and icon fonts |
| **Audio/Video** | `.mp3`, `.mp4` | `.wav`, `.webm`, `.ogg` | Media content |

## Use Cases & Examples

### Image Optimization
**Best For:** Web performance, responsive images, lazy loading
```html
<!-- Responsive images with srcset -->
<picture>
  <source 
    type="image/webp"
    srcset="hero-small.webp 400w,
            hero-medium.webp 800w,
            hero-large.webp 1200w"
    sizes="(max-width: 400px) 400px,
           (max-width: 800px) 800px,
           1200px">
  <source 
    type="image/jpeg"
    srcset="hero-small.jpg 400w,
            hero-medium.jpg 800w,
            hero-large.jpg 1200w"
    sizes="(max-width: 400px) 400px,
           (max-width: 800px) 800px,
           1200px">
  <img src="hero-large.jpg" alt="Hero image" loading="lazy">
</picture>
```

**Image Processing Script:**
```javascript
// imageOptimizer.js - Sharp image processing
const sharp = require('sharp');
const fs = require('fs').promises;
const path = require('path');

async function optimizeImages(inputDir, outputDir) {
  const files = await fs.readdir(inputDir);
  
  for (const file of files) {
    if (!/\.(jpg|jpeg|png)$/i.test(file)) continue;
    
    const input = path.join(inputDir, file);
    const name = path.parse(file).name;
    
    // Generate WebP version
    await sharp(input)
      .webp({ quality: 85 })
      .toFile(path.join(outputDir, `${name}.webp`));
    
    // Generate responsive sizes
    const sizes = [400, 800, 1200];
    for (const width of sizes) {
      await sharp(input)
        .resize(width, null, { withoutEnlargement: true })
        .jpeg({ quality: 85, progressive: true })
        .toFile(path.join(outputDir, `${name}-${width}.jpg`));
    }
    
    // Generate thumbnail
    await sharp(input)
      .resize(150, 150, { fit: 'cover' })
      .toFile(path.join(outputDir, `${name}-thumb.jpg`));
  }
}
```
**Example Projects:** E-commerce galleries, portfolio sites, image-heavy apps

### SVG Graphics
**Best For:** Icons, logos, illustrations, animations
```svg
<!-- icon.svg - Optimized SVG icon -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <defs>
    <style>
      .icon-primary { fill: currentColor; }
      .icon-secondary { opacity: 0.4; }
    </style>
  </defs>
  <path class="icon-primary" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10..."/>
  <circle class="icon-secondary" cx="12" cy="12" r="3"/>
</svg>
```

**SVG Sprite System:**
```html
<!-- sprite.svg -->
<svg xmlns="http://www.w3.org/2000/svg">
  <defs>
    <symbol id="icon-home" viewBox="0 0 24 24">
      <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/>
    </symbol>
    <symbol id="icon-user" viewBox="0 0 24 24">
      <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4..."/>
    </symbol>
  </defs>
</svg>

<!-- Usage -->
<svg class="icon">
  <use href="#icon-home"></use>
</svg>
```
**Example Projects:** Icon systems, animated logos, interactive graphics

### Web Fonts
**Best For:** Custom typography, icon fonts, brand consistency
```css
/* Font loading with fallbacks */
@font-face {
  font-family: 'CustomFont';
  src: url('/fonts/custom.woff2') format('woff2'),
       url('/fonts/custom.woff') format('woff');
  font-weight: 400;
  font-style: normal;
  font-display: swap; /* Prevents FOIT */
}

@font-face {
  font-family: 'CustomFont';
  src: url('/fonts/custom-bold.woff2') format('woff2'),
       url('/fonts/custom-bold.woff') format('woff');
  font-weight: 700;
  font-style: normal;
  font-display: swap;
}

/* Variable fonts */
@font-face {
  font-family: 'VariableFont';
  src: url('/fonts/variable.woff2') format('woff2-variations');
  font-weight: 100 900;
  font-stretch: 75% 125%;
  font-display: optional;
}

/* Icon font */
@font-face {
  font-family: 'IconFont';
  src: url('/fonts/icons.woff2') format('woff2');
  font-weight: normal;
  font-style: normal;
}

.icon::before {
  font-family: 'IconFont';
  font-style: normal;
  font-weight: normal;
  speak: never;
  display: inline-block;
  text-decoration: none;
  width: 1em;
  text-align: center;
}

.icon-home::before { content: '\e900'; }
.icon-user::before { content: '\e901'; }
```
**Example Projects:** Brand websites, typography-focused designs, icon systems

### Audio/Video Management
**Best For:** Background music, video tutorials, podcasts
```html
<!-- Adaptive video streaming -->
<video 
  controls 
  preload="metadata"
  poster="thumbnail.jpg">
  <source src="video.webm" type="video/webm">
  <source src="video.mp4" type="video/mp4">
  <track src="captions.vtt" kind="captions" srclang="en" label="English">
  Your browser doesn't support HTML5 video.
</video>

<!-- Audio with fallback -->
<audio controls preload="none">
  <source src="audio.mp3" type="audio/mpeg">
  <source src="audio.ogg" type="audio/ogg">
  Your browser doesn't support HTML5 audio.
</audio>
```

**Media Processing:**
```javascript
// videoProcessor.js - FFmpeg wrapper
const ffmpeg = require('fluent-ffmpeg');

function processVideo(input, output) {
  return new Promise((resolve, reject) => {
    ffmpeg(input)
      .outputOptions([
        '-c:v libx264',      // Video codec
        '-crf 23',           // Quality (lower = better)
        '-preset medium',    // Encoding speed
        '-c:a aac',         // Audio codec
        '-b:a 128k',        // Audio bitrate
        '-movflags +faststart' // Web optimization
      ])
      .size('1280x720')      // Resolution
      .on('end', resolve)
      .on('error', reject)
      .save(output);
  });
}

// Generate thumbnail
function generateThumbnail(video, output) {
  return new Promise((resolve, reject) => {
    ffmpeg(video)
      .screenshots({
        timestamps: ['50%'],
        filename: output,
        size: '320x240'
      })
      .on('end', resolve)
      .on('error', reject);
  });
}
```
**Example Projects:** Video platforms, podcast apps, e-learning sites

## Best Practices

1. **Optimization:** Compress assets without quality loss
2. **Formats:** Use modern formats (WebP, AVIF, WOFF2)
3. **Lazy Loading:** Load assets only when needed
4. **CDN:** Serve assets from CDN for better performance
5. **Caching:** Set appropriate cache headers
6. **Accessibility:** Provide alt text and captions

## File Organization Pattern
```
assets/
├── images/
│   ├── originals/
│   ├── optimized/
│   └── thumbnails/
├── icons/
│   ├── svg/
│   └── sprite.svg
├── fonts/
│   ├── woff2/
│   └── variable/
├── audio/
│   ├── music/
│   └── effects/
└── video/
    ├── source/
    └── compressed/
```

## Optimization Techniques

### Image Optimization
```bash
# ImageMagick batch optimization
mogrify -resize 1920x1080\> -quality 85 -format jpg *.png

# WebP conversion
cwebp input.jpg -q 85 -o output.webp

# AVIF conversion
avifenc input.png output.avif --min 20 --max 30
```

### Font Subsetting
```javascript
// Subset font to used characters
const Fontmin = require('fontmin');

const fontmin = new Fontmin()
  .src('fonts/*.ttf')
  .use(Fontmin.glyph({
    text: 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
  }))
  .use(Fontmin.ttf2woff2())
  .dest('fonts/subset');

fontmin.run((err, files) => {
  if (err) throw err;
  console.log('Fonts subsetted successfully');
});
```

## Performance Metrics
- **LCP (Largest Contentful Paint):** Optimize hero images
- **CLS (Cumulative Layout Shift):** Define image dimensions
- **File Size:** Target < 100KB for images, < 50KB for fonts
- **Format Support:** Provide fallbacks for older browsers

## Tools & Libraries
- **Image Processing:** Sharp, ImageMagick, Squoosh
- **SVG Optimization:** SVGO, SVG Sprite
- **Font Tools:** Fontmin, Font Squirrel
- **Video Processing:** FFmpeg, HandBrake
- **Asset Management:** Webpack, Vite, Parcel