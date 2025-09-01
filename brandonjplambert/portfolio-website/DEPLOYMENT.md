# Deployment Guide - Portfolio Website

## 🚀 Quick Deploy to Cloudflare Pages

### Prerequisites
- Cloudflare account
- GitHub repository with this code
- Domain (optional but recommended)

### Step 1: Environment Secrets Setup

Add these secrets to your GitHub repository (`Settings > Secrets and variables > Actions`):

#### Required Secrets
```
CLOUDFLARE_API_TOKEN=your_cloudflare_api_token
CLOUDFLARE_ACCOUNT_ID=your_cloudflare_account_id
CLOUDFLARE_PROJECT_NAME=your_project_name
VITE_GITHUB_TOKEN=ghp_your_github_token
VITE_EMAILJS_SERVICE_ID=service_xxxxxxxxx
VITE_EMAILJS_TEMPLATE_ID=template_xxxxxxxx
VITE_EMAILJS_PUBLIC_KEY=your_public_key
```

#### Optional Secrets
```
VITE_ANALYTICS_ID=G-XXXXXXXXXX
CODECOV_TOKEN=your_codecov_token
LHCI_GITHUB_APP_TOKEN=your_lighthouse_token
```

### Step 2: Cloudflare Setup

1. **Create Cloudflare API Token**
   - Go to Cloudflare Dashboard > My Profile > API Tokens
   - Create Token > Custom token
   - Permissions: Account:Cloudflare Pages:Edit, Zone:Zone:Read
   - Include all accounts and zones

2. **Create Cloudflare Pages Project**
   - Go to Cloudflare Dashboard > Pages
   - Create a project
   - Connect to Git (GitHub)
   - Select your repository
   - Build settings:
     - Framework preset: None
     - Build command: `npm run build`
     - Build output directory: `dist`
     - Root directory: `/`

### Step 3: GitHub Actions Deploy

The deployment workflow (`.github/workflows/deploy.yml`) will automatically:

1. **On Push to Main:**
   - Run tests and linting
   - Build production bundle
   - Deploy to Cloudflare Pages
   - Run Lighthouse performance audit
   - Run security scan

2. **On Pull Requests:**
   - Run tests and validation
   - Create preview deployment
   - Comment PR with preview URL

### Step 4: Custom Domain (Optional)

1. In Cloudflare Pages project settings
2. Go to Custom domains
3. Add your domain
4. Update DNS settings as prompted
5. SSL will be automatically configured

### Step 5: Performance Monitoring

The workflow includes automatic:
- **Lighthouse CI**: Performance, accessibility, SEO audits
- **Bundle Analysis**: Size optimization tracking
- **Security Scanning**: Dependency vulnerability checks
- **Test Coverage**: Code quality metrics

## 🔧 Local Development Setup

```bash
# Clone and setup
git clone https://github.com/brandonjplambert/portfolio-website.git
cd portfolio-website
npm install

# Environment setup
cp .env.example .env
# Edit .env with your values

# Start development
npm run dev
```

## 📦 Build Commands

```bash
npm run build              # Standard build
npm run build:production   # Production build with optimizations
npm run build:analyze      # Build with bundle analysis
npm run preview            # Preview production build
```

## 🧪 Testing Commands

```bash
npm test                   # Run tests
npm run test:coverage      # Run with coverage report
npm run lint               # Run linting
npm run type-check         # TypeScript validation
```

## 🐛 Troubleshooting

### Build Failures
1. Check that all environment variables are set
2. Verify Node.js version is 18+
3. Clear cache: `npm run clean && npm install`

### Deployment Issues
1. Verify Cloudflare API token permissions
2. Check GitHub secrets are correctly named
3. Review GitHub Actions logs for specific errors

### Performance Issues
1. Run `npm run build:analyze` to check bundle sizes
2. Review Lighthouse reports in GitHub Actions
3. Optimize images and assets as needed

## 🔐 Security Considerations

- Never commit `.env` files
- Use environment-specific secrets
- Enable Cloudflare security features
- Regular dependency updates
- CSP headers are configured
- HTTPS-only in production

## 📊 Monitoring Setup

1. **Analytics**: Configure Google Analytics or Plausible
2. **Error Tracking**: Set up Sentry for error monitoring  
3. **Uptime**: Use StatusPage or similar service
4. **Performance**: Lighthouse CI provides ongoing monitoring

## 🚦 Deployment Status

Current configuration supports:
- ✅ Automatic deployments on push
- ✅ Preview deployments for PRs  
- ✅ Performance monitoring
- ✅ Security scanning
- ✅ Test coverage reporting
- ✅ Bundle size tracking

## 📋 Pre-Deployment Checklist

- [ ] Environment variables configured
- [ ] GitHub secrets added
- [ ] Cloudflare Pages project created
- [ ] Domain configured (if using custom domain)
- [ ] Build passes locally
- [ ] Tests pass
- [ ] Lighthouse audit scores acceptable
- [ ] Email service configured (EmailJS)
- [ ] Analytics set up
- [ ] Error monitoring configured

## 🎯 Production Optimizations Applied

- **Minification**: Terser for JavaScript, CSS optimization
- **Code Splitting**: Vendor chunks separated
- **Tree Shaking**: Unused code removal
- **Image Optimization**: WebP formats with fallbacks
- **Caching**: Aggressive caching for static assets
- **Compression**: Gzip/Brotli enabled
- **CDN**: Cloudflare global edge network
- **Security Headers**: CSP, HSTS, security headers
- **Prerendering**: Static generation for better SEO

---

**Ready for production deployment!** 🚀