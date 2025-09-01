# Brandon Lambert - Portfolio Website

A modern, responsive portfolio website showcasing full-stack development skills, projects, and professional experience.

## 🚀 Tech Stack

- **Frontend**: React 18 + TypeScript
- **Styling**: Tailwind CSS + Framer Motion
- **Build Tool**: Vite
- **Deployment**: Cloudflare Pages
- **CI/CD**: GitHub Actions
- **Email Service**: EmailJS
- **Analytics**: Google Analytics / Plausible

## ✨ Features

- **Responsive Design**: Optimized for all devices
- **Dark/Light Mode**: System preference detection with manual toggle
- **Smooth Animations**: Framer Motion powered interactions
- **Performance Optimized**: Lighthouse score 95+
- **SEO Friendly**: Meta tags, structured data, sitemap
- **Contact Form**: EmailJS integration with validation
- **Project Showcase**: GitHub integration for live project data
- **Accessibility**: WCAG 2.1 AA compliant
- **Progressive Web App**: Offline support and installability

## 🛠️ Development Setup

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/brandonjplambert/portfolio-website.git
   cd portfolio-website
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Environment setup**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration values
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

5. **Open browser**
   Navigate to `http://localhost:5173`

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint
- `npm run lint:fix` - Fix ESLint issues
- `npm run type-check` - Run TypeScript type checking
- `npm test` - Run tests
- `npm run test:watch` - Run tests in watch mode
- `npm run test:coverage` - Run tests with coverage report

## 🌐 Deployment

### Cloudflare Pages (Recommended)

1. **Automatic Deployment**
   - Push to `main` branch triggers automatic deployment
   - Pull requests create preview deployments
   - GitHub Actions handles build and deployment

2. **Manual Deployment**
   ```bash
   npm run build
   # Upload dist/ folder to Cloudflare Pages
   ```

### Environment Variables

Set these secrets in your GitHub repository settings:

#### Required Secrets
- `CLOUDFLARE_API_TOKEN` - Cloudflare API token with Pages:Edit permissions
- `CLOUDFLARE_ACCOUNT_ID` - Your Cloudflare account ID
- `CLOUDFLARE_PROJECT_NAME` - Your Cloudflare Pages project name
- `VITE_GITHUB_TOKEN` - GitHub personal access token (public_repo scope)
- `VITE_EMAILJS_SERVICE_ID` - EmailJS service ID
- `VITE_EMAILJS_TEMPLATE_ID` - EmailJS template ID
- `VITE_EMAILJS_PUBLIC_KEY` - EmailJS public key

#### Optional Secrets
- `VITE_ANALYTICS_ID` - Google Analytics measurement ID
- `CODECOV_TOKEN` - Codecov token for coverage reports
- `LHCI_GITHUB_APP_TOKEN` - Lighthouse CI GitHub app token
- `LHCI_SERVER_URL` - Lighthouse CI server URL

### Build Configuration

The build process:
1. Installs dependencies
2. Runs linting and type checking
3. Executes tests with coverage
4. Builds optimized production bundle
5. Deploys to Cloudflare Pages
6. Runs Lighthouse performance audit

## 📁 Project Structure

```
portfolio-website/
├── public/                 # Static assets
│   ├── images/            # Project images and assets
│   ├── icons/             # Favicons and app icons
│   └── manifest.json      # PWA manifest
├── src/
│   ├── components/        # React components
│   │   ├── common/        # Reusable components
│   │   ├── layout/        # Layout components
│   │   └── sections/      # Page sections
│   ├── hooks/             # Custom React hooks
│   ├── services/          # API and external services
│   ├── styles/            # Global styles and themes
│   ├── types/             # TypeScript type definitions
│   ├── utils/             # Utility functions
│   └── data/              # Static data and configuration
├── tests/                 # Test files
├── .github/               # GitHub workflows and templates
└── docs/                  # Documentation files
```

## 🎨 Customization

### Theme Configuration
Edit `src/styles/theme.ts` to customize:
- Color palette
- Typography scales
- Spacing system
- Animation presets

### Content Updates
Update your information in:
- `src/data/personal.ts` - Personal information
- `src/data/projects.ts` - Project showcase
- `src/data/experience.ts` - Work experience
- `src/data/skills.ts` - Technical skills

### Component Styling
- Tailwind classes for utility-first styling
- CSS modules for component-specific styles
- Framer Motion for animations

## 🔧 Performance Optimizations

- **Code Splitting**: Lazy loading of route components
- **Image Optimization**: WebP format with fallbacks
- **Bundle Analysis**: Webpack Bundle Analyzer integration
- **Caching Strategy**: Service worker for offline support
- **Lighthouse CI**: Automated performance monitoring

## 🧪 Testing

- **Unit Tests**: React Testing Library + Jest
- **Integration Tests**: Component interaction testing
- **E2E Tests**: Playwright for critical user flows
- **Visual Regression**: Chromatic for UI testing
- **Coverage**: 85%+ code coverage requirement

## 📈 Monitoring & Analytics

- **Performance**: Lighthouse CI scores
- **Analytics**: User behavior tracking
- **Error Monitoring**: Sentry integration
- **Uptime**: StatusPage monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

Brandon Lambert
- Website: [brandonlambert.dev](https://brandonlambert.dev)
- Email: [contact@brandonlambert.dev](mailto:contact@brandonlambert.dev)
- LinkedIn: [linkedin.com/in/brandonjplambert](https://linkedin.com/in/brandonjplambert)
- GitHub: [github.com/brandonjplambert](https://github.com/brandonjplambert)

---

Built with ❤️ using React, TypeScript, and Tailwind CSS