# VocabLens Deployment Guide

This guide covers deploying VocabLens to Vercel with comprehensive CI/CD pipeline setup.

## Quick Deployment

### Prerequisites

1. **Node.js** >= 18.0.0
2. **npm** >= 8.0.0
3. **Vercel CLI** (optional, for manual deployments)
4. **Git** repository on GitHub

### Environment Variables

Copy `config/.env.example` to `.env.local` and configure:

```bash
# Required API Keys
VITE_UNSPLASH_ACCESS_KEY=your_unsplash_access_key
VITE_OPENAI_API_KEY=your_openai_api_key

# Supabase (required for user features)
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key

# Optional monitoring
VITE_SENTRY_DSN=your_sentry_dsn
VITE_POSTHOG_KEY=your_posthog_key
```

### Vercel Deployment

#### Method 1: GitHub Integration (Recommended)

1. **Connect Repository**
   ```bash
   # Push to GitHub
   git remote add origin https://github.com/username/vocablens.git
   git push -u origin main
   ```

2. **Import to Vercel**
   - Go to [vercel.com/new](https://vercel.com/new)
   - Import your GitHub repository
   - Framework Preset: **Vite**
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`

3. **Configure Environment Variables**
   - In Vercel Dashboard → Settings → Environment Variables
   - Add all variables from `.env.example`
   - Ensure variable names start with `VITE_`

#### Method 2: Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login and deploy
vercel login
vercel --prod
```

## CI/CD Pipeline

The project includes a comprehensive GitHub Actions workflow in `.github/workflows/vercel-deployment.yml`.

### Pipeline Stages

1. **Quality Check**
   - TypeScript compilation
   - ESLint code quality
   - Prettier formatting
   - Unit tests with coverage

2. **Build Test**
   - Production build verification
   - Asset optimization
   - Bundle size analysis

3. **E2E Testing**
   - Playwright browser tests
   - PWA functionality testing
   - Performance validation

4. **Preview Deployment**
   - Automatic PR preview deployments
   - Comment with preview URLs
   - Lighthouse performance audits

5. **Production Deployment**
   - Deploy to production on main branch
   - Create GitHub releases
   - Performance monitoring

### Required GitHub Secrets

Add these secrets to your GitHub repository:

```bash
# Vercel Integration
VERCEL_TOKEN=your_vercel_token
VERCEL_ORG_ID=your_vercel_org_id
VERCEL_PROJECT_ID=your_vercel_project_id

# Environment Variables (matching .env.local)
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_UNSPLASH_ACCESS_KEY=your_unsplash_access_key
VITE_OPENAI_API_KEY=your_openai_api_key

# Optional Monitoring
VITE_SENTRY_DSN=your_sentry_dsn
VITE_POSTHOG_KEY=your_posthog_key
CODECOV_TOKEN=your_codecov_token
LHCI_GITHUB_APP_TOKEN=your_lighthouse_token
```

## Production Configuration

### Performance Optimizations

The production build includes:

- **Code Splitting**: Vendor chunks for optimal caching
- **Tree Shaking**: Unused code elimination
- **Minification**: Terser for JavaScript compression
- **Image Optimization**: WebP format with fallbacks
- **PWA Features**: Service worker with caching strategies

### Security Headers

Vercel configuration includes security headers:

```json
{
  "X-Content-Type-Options": "nosniff",
  "X-Frame-Options": "DENY",
  "X-XSS-Protection": "1; mode=block",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "Content-Security-Policy": "default-src 'self'; img-src 'self' https://images.unsplash.com..."
}
```

### Caching Strategy

- **Static Assets**: 1 year cache with immutable headers
- **Service Worker**: No cache, must revalidate
- **API Responses**: Network-first with 1-hour fallback
- **Images**: Cache-first with 30-day expiration

## Monitoring & Analytics

### Error Tracking (Sentry)

```javascript
// Automatic error capture
import * as Sentry from '@sentry/react';

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  integrations: [new BrowserTracing()],
  tracesSampleRate: 0.1,
});
```

### Performance Monitoring (PostHog)

```javascript
// User analytics and feature flags
import posthog from 'posthog-js';

posthog.init(import.meta.env.VITE_POSTHOG_KEY, {
  api_host: import.meta.env.VITE_POSTHOG_HOST
});
```

### Lighthouse CI

Automated performance testing on every PR:

- **Performance**: > 90 score
- **Accessibility**: > 95 score  
- **Best Practices**: > 90 score
- **SEO**: > 90 score
- **PWA**: Passes all checks

## Troubleshooting

### Common Build Issues

1. **TypeScript Errors**
   ```bash
   npm run typecheck
   # Fix type errors before deployment
   ```

2. **Environment Variables**
   ```bash
   # Ensure all VITE_ prefixed variables are set
   npm run build -- --mode production
   ```

3. **Bundle Size Warnings**
   ```bash
   npm run build:analyze
   # Review chunk sizes and optimize imports
   ```

### Deployment Failures

1. **Build Command Issues**
   - Verify `package.json` scripts
   - Check Node.js version compatibility
   - Ensure all dependencies are installed

2. **Environment Variable Problems**
   - Variables must start with `VITE_`
   - Check Vercel dashboard configuration
   - Verify secret naming in GitHub Actions

3. **Asset Loading Issues**
   - Check public asset paths
   - Verify image optimization settings
   - Review service worker cache patterns

### Performance Issues

1. **Slow Loading**
   - Enable image optimization
   - Check bundle size analysis
   - Review network requests in DevTools

2. **PWA Installation Problems**
   - Verify manifest.json configuration
   - Check service worker registration
   - Test offline functionality

## Advanced Configuration

### Custom Domain Setup

1. **Add Domain in Vercel**
   - Dashboard → Settings → Domains
   - Add custom domain
   - Configure DNS records

2. **SSL Certificate**
   - Automatic Let's Encrypt certificate
   - Force HTTPS redirects
   - HSTS headers enabled

### Multi-Environment Setup

```bash
# Development
vercel --dev

# Staging
vercel --target staging

# Production  
vercel --prod
```

### Database Migrations

If using Supabase:

```bash
# Run migrations before deployment
npx supabase db push --linked
```

## Monitoring Dashboard

Access deployment metrics:

- **Vercel Analytics**: Function performance and usage
- **Vercel Speed Insights**: Core Web Vitals tracking
- **GitHub Actions**: Build and deployment history
- **Sentry Dashboard**: Error rates and performance
- **PostHog Analytics**: User behavior and feature usage

## Support

For deployment issues:

1. Check [Vercel Documentation](https://vercel.com/docs)
2. Review GitHub Actions logs
3. Monitor error tracking dashboards
4. Contact team via repository issues