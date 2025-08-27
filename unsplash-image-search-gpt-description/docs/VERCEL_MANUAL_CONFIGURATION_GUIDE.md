# Vercel Manual Configuration Guide
## VocabLens PWA - Complete Deployment Setup

This guide provides step-by-step instructions for manually configuring Vercel deployment when automated deployment fails.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Vercel Dashboard Configuration](#vercel-dashboard-configuration)
- [Environment Variables Setup](#environment-variables-setup)
- [Build Settings Configuration](#build-settings-configuration)
- [Project Settings Overview](#project-settings-overview)
- [Troubleshooting Common Issues](#troubleshooting-common-issues)
- [Alternative Deployment Platforms](#alternative-deployment-platforms)

## Prerequisites

Before configuring Vercel, ensure you have:
- A GitHub repository with your code
- A Vercel account linked to your GitHub
- All required API keys (Unsplash, OpenAI, Supabase)
- Node.js 18+ installed locally for testing

## Vercel Dashboard Configuration

### Step 1: Create New Project

1. **Login to Vercel Dashboard**
   - Navigate to [vercel.com](https://vercel.com)
   - Click "Dashboard" in the top right
   - If prompted, sign in with GitHub

2. **Import Repository**
   - Click "New Project" button
   - Select "Import Git Repository"
   - Choose your GitHub repository: `unsplash-image-search-gpt-description`
   - Click "Import"

### Step 2: Project Settings → General

Navigate to your project dashboard, then click "Settings" tab.

#### 2.1 Root Directory Configuration
```
Screenshot Description: Settings page with "General" tab selected, showing "Root Directory" field
```

**Setting:** Root Directory
**Value:** `.` (leave empty or use dot)
**Explanation:** Since package.json is in the root, no subdirectory is needed

#### 2.2 Framework Preset
```
Screenshot Description: Dropdown menu showing framework options
```

**Setting:** Framework Preset  
**Value:** `Vite`
**Explanation:** Project uses Vite as the build tool (detected from vite.config.ts)

#### 2.3 Node.js Version
```
Screenshot Description: Node.js version dropdown in Build & Development Settings
```

**Setting:** Node.js Version
**Value:** `18.x`
**Explanation:** Project requires Node.js 18+ (specified in package.json engines)

### Step 3: Build & Development Settings

#### 3.1 Build Command
```
Screenshot Description: Build command input field with custom command
```

**Setting:** Build Command  
**Value:** `npm install && npm run build`
**Explanation:** Ensures dependencies are installed before building

**Alternative Build Commands:**
- Standard: `npm run build`
- With verification: `npm install && npm run build && ls -la dist/`
- Using package-lock: `npm ci && npm run build`

#### 3.2 Output Directory
```
Screenshot Description: Output directory field showing "dist"
```

**Setting:** Output Directory
**Value:** `dist`
**Explanation:** Vite builds to /dist directory by default

#### 3.3 Install Command  
```
Screenshot Description: Install command field
```

**Setting:** Install Command
**Value:** `npm install`
**Alternative:** `npm ci` (for production builds)

#### 3.4 Development Command
```
Screenshot Description: Development command field
```

**Setting:** Development Command (optional)
**Value:** `npm run dev`
**Port:** `3000` (auto-detected)

## Environment Variables Setup

### Step 4: Environment Variables Configuration

Navigate to Settings → Environment Variables

#### 4.1 Required Environment Variables

Add these variables for **Production**, **Preview**, and **Development** environments:

```env
# Supabase Configuration
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key

# API Keys
VITE_UNSPLASH_ACCESS_KEY=your_unsplash_access_key
VITE_OPENAI_API_KEY=your_openai_api_key

# Optional App Configuration
VITE_APP_NAME=VocabLens
VITE_APP_VERSION=1.0.0
VITE_APP_DESCRIPTION=AI-Powered Vocabulary Learning

# API Configuration (Optional - with fallbacks)
VITE_UNSPLASH_API_URL=https://api.unsplash.com
VITE_OPENAI_API_URL=https://api.openai.com/v1

# Performance Settings (Optional)
VITE_API_RATE_LIMIT_PER_MINUTE=60
VITE_MAX_CONCURRENT_REQUESTS=5
VITE_MAX_IMAGES_PER_SEARCH=30
VITE_IMAGE_CACHE_SIZE_MB=50

# AI Configuration (Optional)
VITE_DEFAULT_AI_MODEL=gpt-3.5-turbo
VITE_MAX_DESCRIPTION_LENGTH=500
VITE_AI_TEMPERATURE=0.7

# PWA Features (Optional)
VITE_ENABLE_PWA=true
VITE_ENABLE_OFFLINE_MODE=true
VITE_ENABLE_PUSH_NOTIFICATIONS=false

# Learning Settings (Optional)
VITE_DEFAULT_DAILY_GOAL=10
VITE_MAX_VOCABULARY_ITEMS=10000
VITE_SRS_INITIAL_INTERVAL=1

# Development/Security (Optional)
VITE_ENABLE_CONTENT_SECURITY_POLICY=true
VITE_SECURE_HEADERS=true
VITE_DEV_TOOLS=false
VITE_ENABLE_DEBUG=false
VITE_LOG_LEVEL=info
```

#### 4.2 Environment Variable Entry Process

For each environment variable:

1. **Click "Add New" button**
2. **Enter Variable Name** (e.g., `VITE_SUPABASE_URL`)
3. **Enter Value** (your actual API key/URL)
4. **Select Environments:**
   - ✅ Production  
   - ✅ Preview
   - ✅ Development (if needed)
5. **Click "Save"**

```
Screenshot Description: Environment variable form with name field, value field, and environment checkboxes
```

### Step 5: Advanced Settings

#### 5.1 Serverless Function Region
```
Screenshot Description: Functions section showing region dropdown
```

**Setting:** Serverless Function Region
**Value:** `Washington D.C. (IAD)` or closest to your users
**Explanation:** Choose region closest to your target audience

#### 5.2 Ignored Build Step
```
Screenshot Description: Git settings with ignored paths
```

**Setting:** Ignored Build Step (if needed)
**Value:** Leave empty unless you have specific requirements
**Use Case:** Only set if you want to skip builds for certain commits

## Project Settings Overview

### Complete Vercel Project Configuration Checklist

- [ ] **Framework:** Vite selected
- [ ] **Root Directory:** `.` (empty/root)
- [ ] **Build Command:** `npm install && npm run build`
- [ ] **Output Directory:** `dist`
- [ ] **Install Command:** `npm install`
- [ ] **Node.js Version:** `18.x`
- [ ] **Environment Variables:** All required variables added
- [ ] **Region:** Appropriate region selected

### File Structure Verification

Ensure your project has these key files:
```
├── package.json          ✅ (Build configuration)
├── vite.config.ts        ✅ (Build tool config)
├── tsconfig.json         ✅ (TypeScript config)
├── vercel.json           ✅ (Vercel routing config)
├── src/
│   ├── main.tsx         ✅ (Entry point)
│   └── ...
├── public/
│   ├── manifest.json    ✅ (PWA manifest)
│   └── sw.js           ✅ (Service worker)
└── dist/               🔄 (Generated during build)
```

## Troubleshooting Common Issues

### Issue 1: Build Fails with "Module not found"
**Solution:**
1. Check that all dependencies are in package.json
2. Verify Build Command includes `npm install`
3. Clear deployment cache in Vercel settings

### Issue 2: Environment Variables Not Working
**Solution:**
1. Ensure all variables start with `VITE_`
2. Verify variables are set for correct environment (Production/Preview)
3. Redeploy after adding variables

### Issue 3: 404 Errors on Route Navigation
**Solution:**
Verify `vercel.json` contains proper SPA routing:
```json
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/"
    }
  ]
}
```

### Issue 4: Build Timeout
**Solution:**
1. Optimize build command: use `npm ci` instead of `npm install`
2. Remove unnecessary dev dependencies from build
3. Check if build runs locally first

### Issue 5: TypeScript Errors During Build
**Solution:**
1. Run `npm run typecheck` locally first
2. Fix all TypeScript errors
3. Ensure `tsconfig.json` excludes `node_modules`

## Alternative Deployment Platforms

If Vercel continues to fail, consider these alternatives:

### Option 1: Netlify

#### Netlify Configuration:
```yaml
# netlify.toml
[build]
  publish = "dist"
  command = "npm run build"

[build.environment]
  NODE_VERSION = "18"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

#### Setup Steps:
1. Connect GitHub repository to Netlify
2. Set build command: `npm run build`
3. Set publish directory: `dist`  
4. Add environment variables in Netlify dashboard
5. Deploy

#### Pros:
- Excellent performance
- Built-in form handling
- Easy SSL setup
- Good CDN coverage

#### Cons:
- Limited serverless functions in free tier
- Less integration with Vite projects than Vercel

### Option 2: GitHub Pages

#### GitHub Pages Configuration:

```yaml
# .github/workflows/gh-pages.yml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
      
      - run: npm ci
      - run: npm run build
        env:
          VITE_SUPABASE_URL: ${{ secrets.VITE_SUPABASE_URL }}
          VITE_SUPABASE_ANON_KEY: ${{ secrets.VITE_SUPABASE_ANON_KEY }}
          VITE_UNSPLASH_ACCESS_KEY: ${{ secrets.VITE_UNSPLASH_ACCESS_KEY }}
          VITE_OPENAI_API_KEY: ${{ secrets.VITE_OPENAI_API_KEY }}
      
      - uses: actions/upload-pages-artifact@v3
        with:
          path: ./dist

  deploy:
    runs-on: ubuntu-latest
    needs: build
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/deploy-pages@v4
        id: deployment
```

#### Setup Steps:
1. Enable GitHub Pages in repository settings
2. Set source to "GitHub Actions"
3. Add environment variables to repository secrets
4. Create workflow file above
5. Push to main branch

#### Pros:
- Free hosting
- Integrated with GitHub
- Automatic deployments
- Good for open source projects

#### Cons:
- No serverless functions
- Static hosting only
- Custom domain setup more complex
- No server-side features

### Option 3: Cloudflare Pages

#### Cloudflare Pages Configuration:

```toml
# wrangler.toml
name = "vocablens-pwa"

[build]
command = "npm run build"
cwd = "."
watch_dir = "src"

[build.upload]
format = "directory"
dir = "dist"

[[build.upload.rules]]
type = "Text"
globs = ["**/*.html"]
compress = true

[env.production.vars]
NODE_ENV = "production"
```

#### Setup Steps:
1. Connect GitHub repository to Cloudflare Pages
2. Set build command: `npm run build`
3. Set build output directory: `dist`
4. Add environment variables in Cloudflare dashboard
5. Configure custom domain (optional)

#### Pros:
- Excellent global performance
- Free SSL certificates
- Advanced caching options
- Integrated with Cloudflare services
- Good security features

#### Cons:
- Learning curve for Cloudflare ecosystem
- Limited serverless function execution time
- More complex configuration options

## Performance Optimization Tips

### Build Optimization:
1. Use `npm ci` for faster, reliable installs
2. Optimize Vite configuration for production builds
3. Enable compression and minification
4. Use code splitting for better loading performance

### Deployment Optimization:
1. Choose deployment region closest to users
2. Enable CDN features when available  
3. Configure caching headers appropriately
4. Monitor build times and optimize dependencies

### Environment Management:
1. Use different API keys for development/production
2. Set appropriate rate limits for production
3. Configure proper CORS settings
4. Use environment-specific feature flags

## Support and Resources

### Documentation Links:
- [Vercel Deployment Documentation](https://vercel.com/docs/deployments/overview)
- [Vite Build Configuration](https://vitejs.dev/guide/build.html)
- [Environment Variables in Vite](https://vitejs.dev/guide/env-and-mode.html)

### Getting Help:
1. Check Vercel deployment logs for specific errors
2. Test builds locally before deploying
3. Use Vercel CLI for debugging: `npx vercel dev`
4. Contact Vercel support for platform-specific issues

---

## Conclusion

This guide provides comprehensive instructions for manually configuring Vercel deployment. If you continue to experience issues, the alternative platforms (Netlify, GitHub Pages, Cloudflare Pages) offer reliable hosting options with their own advantages.

**Next Steps:**
1. Follow the Vercel configuration checklist
2. Test deployment with a simple commit
3. Monitor deployment logs for any issues
4. Set up proper monitoring and analytics

For additional support, refer to the project's GitHub issues or contact the development team.