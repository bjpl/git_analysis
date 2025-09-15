# GitHub Pages Deployment Guide

## Setup Complete ✅

Your project is now configured for GitHub Pages deployment!

## How to Deploy

### Automatic Deployment (Recommended)

1. **Commit and push your changes:**
   ```bash
   git add .
   git commit -m "Setup GitHub Pages deployment"
   git push origin main
   ```

2. **Enable GitHub Pages in your repository:**
   - Go to https://github.com/bjpl/Internet-Infrastructure-Map
   - Click on "Settings" tab
   - Scroll down to "Pages" in the left sidebar
   - Under "Build and deployment":
     - Source: Select "GitHub Actions"
   - Click Save

3. **Wait for deployment:**
   - The GitHub Action will automatically trigger
   - Check progress: Actions tab → "Deploy to GitHub Pages" workflow
   - First deployment takes 2-5 minutes

4. **Access your site:**
   - Your site will be available at:
   - https://bjpl.github.io/Internet-Infrastructure-Map/

## Manual Deployment

If you need to trigger deployment manually:
1. Go to Actions tab in your repository
2. Select "Deploy to GitHub Pages" workflow
3. Click "Run workflow" → "Run workflow"

## Troubleshooting

### Site not loading?
- Check Actions tab for any failed deployments
- Ensure GitHub Pages is enabled in Settings
- Clear browser cache (the site uses service workers)

### Assets not loading?
- The base path is configured correctly in `vite.config.js`
- If you rename the repository, update the base path

### Build failing?
- Check Node version (requires Node 20)
- Run `npm ci` locally to ensure dependencies are correct
- Check the Actions log for specific errors

## Local Testing

Test the production build locally:
```bash
npm run build
npm run preview
```

## Configuration Files

- `.github/workflows/deploy.yml` - GitHub Actions workflow
- `vite.config.js` - Base path configuration
- `package.json` - Build scripts

## Notes

- Deployment triggers on every push to `main` branch
- The site uses Vite for building and bundling
- Large assets are code-split for better performance
- Source maps are included for debugging