# Cloudflare Pages Deployment Guide

This guide walks you through deploying your SvelteKit application to Cloudflare Pages with optimized performance and security settings.

## Quick Start

1. **Setup Environment**
   ```bash
   npm run env:setup
   # Edit .env file with your actual values
   ```

2. **Optimize Performance**
   ```bash
   npm run cf:optimize
   ```

3. **Deploy to Preview**
   ```bash
   npm run deploy:preview
   ```

## Detailed Setup

### 1. Prerequisites

- Node.js 18+ and npm 9+
- Cloudflare account
- Wrangler CLI installed globally: `npm install -g wrangler`

### 2. Authentication

```bash
# Login to Cloudflare
npm run cf:login

# Verify authentication
npm run cf:whoami
```

### 3. Environment Configuration

Copy the example environment file:
```bash
cp config/cloudflare/env.example .env
```

Update `.env` with your values:
```env
PRISMIC_REPO_NAME=your-repo-name
PRISMIC_ACCESS_TOKEN=your-access-token
CUSTOM_DOMAIN=yourdomain.com
```

### 4. Project Configuration

The deployment uses these key configuration files:

- `config/cloudflare/wrangler.toml` - Main Cloudflare configuration
- `config/cloudflare/pages.json` - Pages-specific settings
- `config/svelte/svelte.config.js` - SvelteKit with Cloudflare adapter

### 5. Deployment Commands

```bash
# Deploy to different environments
npm run deploy:preview    # Preview deployment
npm run deploy:staging    # Staging deployment
npm run deploy:production # Production deployment

# Dry run (see what would happen)
npm run deploy:dry-run
```

## Performance Optimizations

### Cache Configuration

The deployment includes optimized caching rules:

- **Static Assets**: 1 year cache with immutable headers
- **Images**: 30 days cache with compression
- **HTML**: 5 minutes cache with revalidation
- **API**: 1 minute cache with revalidation

### Compression

- **Gzip**: Level 6 compression for text content
- **Brotli**: Quality 6 compression (better than gzip)
- **Minimum Size**: 1KB threshold for compression

### Security Headers

Comprehensive security headers are applied:

- Content Security Policy (CSP)
- HTTP Strict Transport Security (HSTS)
- X-Frame-Options, X-Content-Type-Options
- Referrer Policy and Permissions Policy

## Custom Domain Setup

### 1. Add Domain to Cloudflare

1. Add your domain to Cloudflare
2. Update nameservers to Cloudflare's
3. Wait for DNS propagation

### 2. Configure Pages Domain

```bash
# Via Cloudflare Dashboard
# Pages > Your Project > Custom domains > Set up a custom domain

# Or via wrangler.toml (update the configuration)
[env.production]
route = "yourdomain.com/*"
```

### 3. SSL/TLS Settings

- Set SSL/TLS encryption mode to "Full (strict)"
- Enable "Always Use HTTPS"
- Consider enabling HSTS preload

## Environment Variables

### Setting Secrets

For sensitive values, use Wrangler secrets:

```bash
# Set individual secrets
wrangler pages secret put PRISMIC_ACCESS_TOKEN --env=production
wrangler pages secret put API_KEY --env=production

# The deploy script will prompt for secrets automatically
```

### Public Variables

Non-sensitive variables can be set in `wrangler.toml`:

```toml
[vars]
NODE_ENV = "production"
API_BASE_URL = "https://api.yourdomain.com"
```

## Advanced Features

### Edge Functions

Create functions in the `functions/` directory:

```javascript
// functions/api/hello.js
export async function onRequest(context) {
  return new Response('Hello from the edge!');
}
```

### KV Storage

Add KV namespaces in `wrangler.toml`:

```toml
[[kv_namespaces]]
binding = "CACHE"
id = "your-kv-namespace-id"
```

### D1 Database

Add D1 databases in `wrangler.toml`:

```toml
[[d1_databases]]
binding = "DB"
database_name = "your-database"
database_id = "your-database-id"
```

## Monitoring and Analytics

### Web Analytics

Enable Cloudflare Web Analytics:
1. Go to Cloudflare Dashboard > Analytics & Logs > Web Analytics
2. Add your site
3. Include the beacon script or use the API

### Performance Monitoring

The deployment includes Core Web Vitals tracking:
- Largest Contentful Paint (LCP)
- First Input Delay (FID)
- Cumulative Layout Shift (CLS)
- Time to First Byte (TTFB)

### Error Tracking

Configure Sentry for error tracking:
```env
SENTRY_DSN=your-sentry-dsn
SENTRY_ORG=your-org
SENTRY_PROJECT=your-project
```

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check Node.js version (must be 18+)
   - Verify all dependencies are installed
   - Check for TypeScript errors

2. **Authentication Issues**
   - Run `wrangler login` to re-authenticate
   - Check if you have access to the Cloudflare account

3. **Environment Variables**
   - Verify secrets are set correctly
   - Check variable names match exactly

4. **Custom Domain Issues**
   - Ensure DNS is properly configured
   - Check SSL/TLS settings
   - Verify domain is added to the Pages project

### Debug Commands

```bash
# Check project status
npm run cf:pages:list

# View build logs
wrangler pages deployment list --project-name=project-workspace-prod

# Test locally with Cloudflare bindings
wrangler pages dev build
```

## Performance Tips

1. **Enable HTTP/2 Push**
   - Configure critical resources in `wrangler.toml`

2. **Optimize Images**
   - Use WebP/AVIF formats
   - Enable automatic optimization in Cloudflare

3. **Minimize Bundle Size**
   - Use code splitting
   - Tree shake unused code
   - Compress assets

4. **Cache Strategy**
   - Set appropriate cache TTLs
   - Use cache tags for invalidation
   - Implement stale-while-revalidate

## Security Best Practices

1. **Content Security Policy**
   - Regularly audit and update CSP rules
   - Use nonce or hash for inline scripts

2. **HTTPS Everywhere**
   - Force HTTPS redirects
   - Use HSTS with preloading

3. **Environment Variables**
   - Never commit secrets to git
   - Use Wrangler secrets for sensitive data

4. **Regular Updates**
   - Keep dependencies updated
   - Monitor security advisories

## Support Resources

- [Cloudflare Pages Documentation](https://developers.cloudflare.com/pages/)
- [SvelteKit Cloudflare Adapter](https://kit.svelte.dev/docs/adapter-cloudflare)
- [Wrangler CLI Reference](https://developers.cloudflare.com/workers/wrangler/)
- [Cloudflare Community](https://community.cloudflare.com/)