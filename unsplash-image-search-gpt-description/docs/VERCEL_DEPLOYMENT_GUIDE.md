# Vercel Deployment Guide - VocabLens PWA

## 🚨 Issue Diagnosis

The 404 error occurs because Vercel can't find the built files. Common causes:
1. **Build Output Location**: Vercel looking in wrong directory
2. **Routing Configuration**: SPA routing not properly configured
3. **Build Process**: Build failing silently or incomplete
4. **Asset References**: Incorrect asset paths in built files

## 📋 Step-by-Step Fix Process

### Step 1: Verify Local Build
```bash
# Clean build to ensure fresh start
rm -rf dist/
npm run build

# Verify build output
node scripts/verify-build.js

# Test locally
npm run preview
```

### Step 2: Simplified Vercel Configuration

The `vercel.json` has been simplified to remove conflicting directives:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": null,
  "routes": [
    {
      "handle": "filesystem"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
```

**Key Changes:**
- ✅ Removed conflicting `rewrites` and `routes` sections
- ✅ Simplified build command (no manual npm install)
- ✅ Clear SPA routing fallback to index.html

### Step 3: Vercel Dashboard Configuration

1. **Go to Vercel Dashboard**: https://vercel.com/dashboard
2. **Find Your Project**: Look for "vocablens-pwa"
3. **Settings → General**:
   - Framework Preset: **Other**
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`

4. **Settings → Environment Variables** (if needed):
   ```
   VITE_SUPABASE_URL=your_supabase_url
   VITE_SUPABASE_ANON_KEY=your_supabase_key
   ```

5. **Settings → Deployments**:
   - Auto-deploy: ✅ Enabled
   - Branch: `main`

### Step 4: Test Deployment

1. **Deploy Test File First**:
   ```bash
   # Test static file serving
   curl https://vocablens-pwa.vercel.app/test.html
   ```

2. **Check Main App**:
   ```bash
   # Test main application
   curl https://vocablens-pwa.vercel.app/
   ```

3. **Verify Build Logs**:
   - Go to Vercel Dashboard → Deployments
   - Click latest deployment
   - Check "Build Logs" tab for errors

## 🐛 Debugging Checklist

### If You Still Get 404:

1. **Check Build Logs**:
   ```bash
   # In Vercel dashboard, look for:
   - "Build completed successfully"
   - "Output: X files, Y KB"
   - No error messages in red
   ```

2. **Verify File Structure**:
   ```bash
   # Expected structure after build:
   dist/
   ├── index.html           # Main HTML file
   ├── assets/
   │   ├── index-[hash].js  # Main JS bundle
   │   ├── index-[hash].css # Main CSS bundle
   │   └── [other-assets]
   └── manifest.json        # PWA manifest
   ```

3. **Test Different Routes**:
   ```bash
   # Test these URLs:
   https://vocablens-pwa.vercel.app/           # Should work
   https://vocablens-pwa.vercel.app/test.html  # Should work
   https://vocablens-pwa.vercel.app/some-page  # Should fallback to index.html
   ```

## 🔧 Alternative Approaches

### Approach 1: Minimal vercel.json
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist"
}
```

### Approach 2: Explicit SPA Configuration
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "cleanUrls": true,
  "trailingSlash": false,
  "rewrites": [
    {
      "source": "/((?!api/.*)(?!_next/static/.*)(?!_next/image/.*)(?!favicon.ico).*)",
      "destination": "/index.html"
    }
  ]
}
```

### Approach 3: Force Rebuild
```bash
# In Vercel dashboard:
# 1. Go to Settings → General
# 2. Change Node.js Version (e.g., 18.x → 20.x)
# 3. Deploy again
# 4. Change back if needed
```

## 🚀 Quick Commands

```bash
# Verify everything is working locally
npm run build && npm run preview

# Check build output
node scripts/verify-build.js

# Test static serving
curl -I https://vocablens-pwa.vercel.app/test.html

# Full deployment test
curl -s https://vocablens-pwa.vercel.app/ | grep -q "VocabLens" && echo "✅ Working" || echo "❌ Failed"
```

## 📞 Support & Troubleshooting

If issues persist:

1. **Check Vercel Status**: https://vercel-status.com/
2. **Redeploy**: Trigger new deployment in dashboard
3. **Contact Vercel Support**: With build logs and deployment URL

## 🎯 Expected Results

After following this guide:
- ✅ `https://vocablens-pwa.vercel.app/` shows your PWA
- ✅ `https://vocablens-pwa.vercel.app/test.html` shows test page
- ✅ Client-side routing works (no 404 on refresh)
- ✅ Static assets load correctly

The deployment should work within 2-3 minutes of pushing changes to GitHub.