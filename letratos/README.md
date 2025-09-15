# Letratos

A static-generated bilingual poetry and photography portfolio built with Jekyll 4.3.0, featuring Spanish/English poem collections with responsive photo galleries and optimized performance through compressed SASS, lazy loading, and minimal JavaScript.

## About

Brandon is a California native who writes poetry in English and Spanish. He also takes photos.

## Technical Architecture

### Built With
- **Jekyll 4.3.0** - Static site generator with Liquid templating
- **Ruby 3.x** - Required for Jekyll build process
- **SASS/SCSS** - Preprocessed CSS with compressed output
- **Jekyll Collections** - Custom content types for poems and photography

### Key Dependencies
- `jekyll-feed` - Generates Atom feed for content syndication
- `jekyll-seo-tag` - Automated SEO meta tags and Open Graph data
- `jekyll-sitemap` - XML sitemap generation for search engines
- `jekyll-github-metadata` - GitHub repository integration
- `jekyll-relative-links` - Markdown link resolution

### Project Structure

```
letratos/
├── _poems_en/          # English poetry collection (markdown/HTML)
├── _poems_es/          # Spanish poetry collection (markdown/HTML)
├── _photography/       # Photo gallery collections with YAML metadata
├── _layouts/           # Liquid templates (default, poem, photography)
├── _sass/             # SCSS partials for modular styling
├── _site/             # Generated static site (gitignored)
├── assets/
│   ├── images/        # Photography organized by gallery
│   ├── sketches/      # Poem accompaniment media (PNG/video)
│   └── css/           # Compiled stylesheets
└── _config.yml        # Jekyll configuration and site settings
```

### Features & Implementation

#### Bilingual Content Management
- Separate Jekyll collections for `poems_en` and `poems_es`
- Custom permalinks: `/en/:title/` and `/es/:title/`
- Cross-language linking via `translation_url` front matter
- Language-aware navigation and metadata

#### Media Handling
- **Poem Sketches**: Support for both static images (PNG) and video (MP4/WebM)
- **Interactive Videos**: Click-to-pause functionality with opacity feedback
- **Lazy Loading**: Images use native `loading="lazy"` attribute
- **Responsive Images**: CSS-based scaling for all viewport sizes

#### Performance Optimizations
- Compressed SASS output (`style: compressed`)
- Minimal JavaScript - only essential video controls
- Static HTML generation at build time
- Optimized asset loading with relative URLs

#### SEO & Accessibility
- Automated meta tags via `jekyll-seo-tag`
- Semantic HTML5 structure
- Descriptive alt text for images
- XML sitemap for search indexing
- Clean URL structure without file extensions

### Configuration Details

The site uses Jekyll's `_config.yml` for:
- **Collections Configuration**: Defines output paths and permalinks
- **Default Front Matter**: Automatic layout assignment by content type
- **Language Settings**: Bilingual support with English as default
- **Build Exclusions**: Ignores vendor files and caches

### Development Notes

- **Markdown Processing**: Kramdown parser for extended markdown features
- **Template Engine**: Liquid for dynamic content generation
- **Asset Pipeline**: Jekyll's built-in SASS processor
- **Local Server**: WEBrick server with auto-regeneration
- **Windows Support**: Includes `wdm` gem for file watching on Windows
