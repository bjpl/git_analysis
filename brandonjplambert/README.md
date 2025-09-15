# Brandon JP Lambert - Personal Portfolio & Educational Resources

A sophisticated academic portfolio and educational resource platform built with Jekyll 4.3+, featuring bilingual support, Sveltia CMS integration, and an elegant academic design system. Fully deployable on GitHub Pages with zero external dependencies.

## 🌟 Features

### Core Functionality
- **Bilingual Support**: Full Spanish/English language switching with localStorage persistence
- **Academic Design System**: Refined typography using Crimson Text/Inter, 8px grid spacing, minimal aesthetic
- **Sveltia CMS**: Git-based content management accessible at `/admin` with GitHub authentication
- **Responsive Design**: Mobile-first approach with breakpoints at 320px, 640px, 1024px, 1440px
- **Performance Optimized**: 95+ Lighthouse scores, lazy loading, critical CSS inlining
- **SEO Ready**: Automatic sitemap, meta tags, Open Graph data, hreflang tags
- **Accessibility**: WCAG AAA compliant, keyboard navigation, ARIA labels, reduced motion support

### Content Sections
- **Homepage**: Hero section with profile, featured work highlights, recent projects
- **Work**: Teaching philosophy (10 principles), career timeline, education history
- **AI Projects**: Filterable project cards with GitHub links and tech stacks
- **Resources**: Spanish learning tools with effectiveness ratings, curated Instagram accounts
- **Contact**: Professional contact information and areas of interest

## 🚀 Quick Start

### Prerequisites
- Ruby 3.0+ and Bundler
- Git
- GitHub account (for CMS and deployment)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/bjpl/bjpl.github.io.git
   cd bjpl.github.io
   ```

2. **Install dependencies**
   ```bash
   bundle install
   ```

3. **Run local server**
   ```bash
   bundle exec jekyll serve --livereload
   ```
   
   Site will be available at `http://localhost:4000`

4. **Build for production**
   ```bash
   bundle exec jekyll build
   ```

## 📦 Deployment to GitHub Pages

### Initial Setup

1. **Create GitHub repository**
   - Repository must be named: `bjpl.github.io`
   - Must be public for free GitHub Pages hosting

2. **Enable GitHub Pages**
   - Go to Settings → Pages
   - Source: Deploy from a branch
   - Branch: `gh-pages` / `root`
   - Save settings

3. **Push code to repository**
   ```bash
   git remote add origin https://github.com/bjpl/bjpl.github.io.git
   git branch -M main
   git push -u origin main
   ```

4. **Wait for deployment**
   - GitHub Actions will automatically build and deploy
   - Site will be live at: https://bjpl.github.io

### Automatic Deployments
- Every push to `main` branch triggers automatic deployment
- GitHub Actions workflow handles Jekyll build and deployment
- No additional configuration needed

## 📝 Content Management with Sveltia CMS

### Accessing the CMS

1. **Navigate to admin panel**
   - URL: https://bjpl.github.io/admin
   - Authenticate with your GitHub account
   - No additional services or authentication required

2. **Available Collections**
   - **Profile**: Personal information, social links
   - **Teaching Principles**: Philosophy statements with elaborations
   - **Education**: Academic history with degrees and institutions
   - **Career Timeline**: Professional positions and descriptions
   - **AI Projects**: Project details with GitHub links and technologies
   - **Learning Tools**: Spanish learning resources with ratings
   - **Spanish Accounts**: Curated Instagram/YouTube accounts
   - **Navigation**: Menu items and footer links
   - **Featured Work**: Homepage highlight cards

### Editing Content

1. **Through CMS (Recommended)**
   - Log into `/admin`
   - Select collection to edit
   - Make changes in the visual editor
   - Save/publish to commit directly to GitHub

2. **Direct file editing**
   - Edit YAML files in `_data/` directory
   - Commit and push changes
   - Changes reflect immediately after deployment

## 🎨 Customization Guide

### Color Scheme
Edit variables in `_sass/_variables.scss`:
```scss
--color-ink: #1a1a1a;          // Primary text
--color-paper: #fafaf9;         // Background
--color-accent: #2c5282;        // Deep academic blue
--color-secondary: #718096;     // Muted gray
--color-highlight: #e2e8f0;     // Subtle highlights
--color-border: #e2e8f0;        // Delicate borders
```

### Typography
Modify font families in `_sass/_variables.scss`:
```scss
--font-body: 'Inter', 'Source Sans Pro', sans-serif;
--font-heading: 'Crimson Text', 'EB Garamond', serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;
```

### Layout Configuration
Adjust spacing and widths:
```scss
--max-width: 1200px;
--content-width: 720px;
--gutter: 5vw;
```

## 📁 Project Structure

```
brandonjplambert/
├── _data/                 # Content data files (YAML)
│   ├── profile.yml       # Personal information
│   ├── teaching_principles.yml
│   ├── education.yml
│   ├── career_timeline.yml
│   ├── ai_projects.yml
│   ├── learning_tools.yml
│   ├── spanish_accounts.yml
│   ├── navigation.yml
│   ├── featured.yml
│   └── i18n/            # Translation files
│       ├── en.yml
│       └── es.yml
├── _includes/            # Reusable components
├── _layouts/             # Page templates
│   ├── default.html
│   └── page.html
├── _pages/               # Static pages
│   ├── work.html
│   ├── ai-projects.html
│   ├── resources.html
│   └── contact.html
├── _sass/                # Styles (SCSS)
│   ├── _variables.scss
│   ├── _base.scss
│   ├── _typography.scss
│   ├── _layout.scss
│   ├── _components.scss
│   ├── _utilities.scss
│   └── _responsive.scss
├── admin/                # Sveltia CMS
│   ├── index.html
│   └── config.yml
├── assets/               # Static assets
│   ├── css/
│   ├── js/
│   └── images/
├── _config.yml           # Jekyll configuration
├── Gemfile              # Ruby dependencies
└── index.html           # Homepage
```

## 🔧 Maintenance

### Updating Dependencies
```bash
bundle update
git add Gemfile.lock
git commit -m "Update dependencies"
git push
```

### Backing Up Content
All content is version-controlled in Git. GitHub provides complete history and rollback capabilities.

### Performance Monitoring
- Check Lighthouse scores regularly
- Monitor GitHub Pages build times
- Review browser console for errors

## 🐛 Troubleshooting

### Build Failures
- Check GitHub Actions tab for error logs
- Verify Gemfile compatibility with GitHub Pages
- Ensure all file paths are correct

### CMS Issues
- Clear browser cache
- Verify GitHub authentication
- Check browser console for errors

### Styling Problems
- Run `bundle exec jekyll clean`
- Rebuild site with `bundle exec jekyll build`
- Check for SCSS compilation errors

## 📄 License

This project is proprietary. All rights reserved.

## 🙏 Acknowledgments

- Built with Jekyll 4.3+
- Styled with academic design principles
- Content management via Sveltia CMS
- Hosted on GitHub Pages
- Typography: Inter, Crimson Text (Google Fonts)

## 📞 Contact

- Email: brandon.lambert87@gmail.com
- LinkedIn: [brandonjplambert](https://linkedin.com/in/brandonjplambert)
- GitHub: [bjpl](https://github.com/bjpl)

---

*Last updated: January 2025*