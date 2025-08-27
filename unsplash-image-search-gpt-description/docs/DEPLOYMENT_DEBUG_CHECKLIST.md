# Vercel Deployment Debug Checklist 🔧

## Pre-Deployment Verification

### ✅ Local Build Test
```bash
# 1. Clean build
npm run build

# 2. Verify build output
npm run verify-build

# 3. Test locally
npm run preview
# Visit http://localhost:4173 - should work perfectly
```

### ✅ File Structure Check
```
dist/
├── index.html          ← Must exist
├── assets/             ← Must contain JS/CSS files
│   ├── index-*.js     ← Vite-generated JS bundle
│   ├── index-*.css    ← Vite-generated CSS bundle  
│   └── manifest.json  ← PWA manifest
└── test.html          ← Test file for debugging
```

## Deployment Process

### ✅ GitHub Push
```bash
git add .
git commit -m "Fix Vercel deployment configuration"
git push origin main
```

### ✅ Vercel Configuration

**vercel.json** (simplified):
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": null,
  "routes": [
    {"handle": "filesystem"},
    {"src": "/(.*)", "dest": "/index.html"}
  ]
}
```

**Dashboard Settings:**
- Framework: **Other** (not Vite)
- Build Command: `npm run build`
- Output Directory: `dist`
- Node Version: `20.x`

## Testing Deployment

### ✅ Static File Test
```bash
# Test 1: Static HTML serving
curl -I https://vocablens-pwa.vercel.app/test.html
# Expected: 200 OK

# Test 2: Main app
curl -I https://vocablens-pwa.vercel.app/
# Expected: 200 OK, Content-Type: text/html
```

### ✅ Browser Test
1. **Open**: https://vocablens-pwa.vercel.app/test.html
   - Should show green "WORKING" message
2. **Open**: https://vocablens-pwa.vercel.app/
   - Should show your PWA application
3. **Refresh any route**: Should not show 404

## Debug Vercel Build Logs

### 📊 Build Log Analysis

**Good Build Log Should Show:**
```
✓ Building for production...
✓ [BUILD] Completed in Xs
[INFO] Build completed
[INFO] Deploying...
✓ Deployment completed
```

**Red Flags in Build Log:**
```
❌ Error: Cannot resolve module
❌ Build failed
❌ No index.html found
❌ ENOENT: no such file or directory
```

### 🔍 Common Issues & Fixes

| Issue | Symptom | Fix |
|-------|---------|-----|
| **Wrong Output Dir** | Build succeeds, 404 error | Check `outputDirectory: "dist"` |
| **Build Fails** | Red errors in logs | Fix TypeScript/lint errors |
| **No Routing** | SPA routes show 404 | Add routes config in vercel.json |
| **Missing Assets** | White screen, console errors | Check asset paths in built files |

## Emergency Fixes

### 🚨 If Still Getting 404

**Option 1: Force Clean Deploy**
```bash
# Delete dist/ and redeploy
rm -rf dist/
git add -A
git commit -m "Force clean deployment"
git push
```

**Option 2: Minimal Configuration**
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist"
}
```

**Option 3: Manual Deployment**
```bash
# Build locally and deploy with Vercel CLI
npm run build
npx vercel --prod
```

## Success Indicators ✨

### ✅ Deployment Successful When:
1. **Test page loads**: `/test.html` shows green checkmark
2. **Main app loads**: `/` shows PWA interface  
3. **Routing works**: `/random-route` redirects to main app
4. **No console errors**: Browser dev tools clean
5. **PWA features work**: Can install as app

### 📱 Mobile/PWA Test
- Open on mobile browser
- "Add to Home Screen" option appears
- Works offline (service worker active)
- App icon shows correctly

## Timeline Expectations

- **Code Push → Deployment**: 2-3 minutes
- **First Time Setup**: 5-10 minutes  
- **Issue Resolution**: 15-30 minutes max

## Contact Points

- **Build Issues**: Check Vercel dashboard build logs
- **Routing Issues**: Verify vercel.json configuration
- **Asset Issues**: Run `npm run verify-build` locally
- **PWA Issues**: Check service worker in browser dev tools

---

**Quick Success Check:**
```bash
curl -s https://vocablens-pwa.vercel.app/test.html | grep -q "WORKING" && echo "✅ DEPLOYED!" || echo "❌ Still broken"
```