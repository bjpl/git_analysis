#!/usr/bin/env node

/**
 * Bulletproof Build Verification Script
 * Ensures build output is complete and deployment-ready
 * 
 * Checks:
 * - Required files exist
 * - HTML structure is valid
 * - Assets are properly generated
 * - PWA manifest is valid
 * - No missing critical resources
 * - Bundle sizes are within limits
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Configuration
const DIST_DIR = path.join(__dirname, '../dist');
const MAX_BUNDLE_SIZE_KB = 500; // Maximum total bundle size in KB
const MAX_CHUNK_SIZE_KB = 150;  // Maximum individual chunk size in KB

// ANSI colors for console output
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m'
};

const log = {
  info: (msg) => console.log(`${colors.blue}ℹ${colors.reset} ${msg}`),
  success: (msg) => console.log(`${colors.green}✅${colors.reset} ${msg}`),
  warn: (msg) => console.log(`${colors.yellow}⚠️${colors.reset} ${msg}`),
  error: (msg) => console.log(`${colors.red}❌${colors.reset} ${msg}`),
  title: (msg) => console.log(`\n${colors.cyan}🔍 ${msg}${colors.reset}\n`)
};

/**
 * Check if build directory exists
 */
function checkBuildDirectory() {
  log.title('Checking Build Directory');
  
  if (!fs.existsSync(DIST_DIR)) {
    throw new Error('Build output directory not found at: ' + DIST_DIR);
  }
  
  const stats = fs.statSync(DIST_DIR);
  if (!stats.isDirectory()) {
    throw new Error('Build output path exists but is not a directory');
  }
  
  log.success('Build directory exists: ' + DIST_DIR);
  return true;
}

/**
 * Check required files exist
 */
function checkRequiredFiles() {
  log.title('Checking Required Files');
  
  const requiredFiles = [
    'index.html',
    'manifest.json'
  ];
  
  const requiredPatterns = [
    /assets\/index-[a-f0-9]+\.js$/,  // Main JS bundle
    /assets\/index-[a-f0-9]+\.css$/, // Main CSS bundle
  ];
  
  // Check exact files
  requiredFiles.forEach(file => {
    const filePath = path.join(DIST_DIR, file);
    if (!fs.existsSync(filePath)) {
      throw new Error(`Required file missing: ${file}`);
    }
    log.success(`Found required file: ${file}`);
  });
  
  // Check pattern-based files
  const allFiles = getAllFiles(DIST_DIR);
  requiredPatterns.forEach((pattern, index) => {
    const matchingFile = allFiles.find(file => {
      const relativePath = path.relative(DIST_DIR, file);
      return pattern.test(relativePath);
    });
    
    if (!matchingFile) {
      throw new Error(`No file found matching pattern: ${pattern}`);
    }
    
    const relativePath = path.relative(DIST_DIR, matchingFile);
    log.success(`Found pattern match: ${relativePath}`);
  });
  
  return true;
}

/**
 * Validate HTML structure
 */
function validateHTML() {
  log.title('Validating HTML Structure');
  
  const htmlPath = path.join(DIST_DIR, 'index.html');
  const htmlContent = fs.readFileSync(htmlPath, 'utf8');
  
  const requiredElements = [
    { tag: '<meta name="viewport"', description: 'Viewport meta tag' },
    { tag: '<meta name="theme-color"', description: 'Theme color meta tag' },
    { tag: '<link rel="manifest"', description: 'Manifest link' },
    { tag: '<title>', description: 'Page title' },
    { tag: '<div id="root"', description: 'React root element' },
    { tag: '<script type="module"', description: 'Module script tag' }
  ];
  
  requiredElements.forEach(({ tag, description }) => {
    if (!htmlContent.includes(tag)) {
      throw new Error(`Missing required HTML element: ${description}`);
    }
    log.success(`Found: ${description}`);
  });
  
  // Check for potential issues
  const potentialIssues = [
    { 
      pattern: /src="[^"]*\.js"/, 
      message: 'Non-module script detected - may cause issues' 
    },
    { 
      pattern: /href="[^"]*\.css".*rel="stylesheet"/, 
      message: 'CSS stylesheet found - good' 
    }
  ];
  
  potentialIssues.forEach(({ pattern, message }) => {
    if (pattern.test(htmlContent)) {
      log.info(message);
    }
  });
  
  return true;
}

/**
 * Validate PWA manifest
 */
function validateManifest() {
  log.title('Validating PWA Manifest');
  
  const manifestPath = path.join(DIST_DIR, 'manifest.json');
  if (!fs.existsSync(manifestPath)) {
    log.warn('manifest.json not found - PWA features will not work');
    return false;
  }
  
  let manifest;
  try {
    const manifestContent = fs.readFileSync(manifestPath, 'utf8');
    manifest = JSON.parse(manifestContent);
  } catch (error) {
    throw new Error('Invalid manifest.json: ' + error.message);
  }
  
  const requiredFields = [
    'name',
    'short_name',
    'start_url',
    'display',
    'theme_color',
    'background_color',
    'icons'
  ];
  
  requiredFields.forEach(field => {
    if (!(field in manifest)) {
      throw new Error(`Missing required manifest field: ${field}`);
    }
    log.success(`Manifest field present: ${field}`);
  });
  
  // Validate icons
  if (!Array.isArray(manifest.icons) || manifest.icons.length === 0) {
    throw new Error('Manifest must contain at least one icon');
  }
  
  manifest.icons.forEach((icon, index) => {
    const requiredIconFields = ['src', 'sizes', 'type'];
    requiredIconFields.forEach(field => {
      if (!(field in icon)) {
        throw new Error(`Icon ${index} missing required field: ${field}`);
      }
    });
    
    // Check if icon file exists
    const iconPath = path.join(DIST_DIR, icon.src.replace(/^\//, ''));
    if (!fs.existsSync(iconPath)) {
      log.warn(`Icon file not found: ${icon.src}`);
    } else {
      log.success(`Icon file exists: ${icon.src}`);
    }
  });
  
  log.success('PWA manifest is valid');
  return true;
}

/**
 * Check bundle sizes
 */
function checkBundleSizes() {
  log.title('Checking Bundle Sizes');
  
  const assetsDir = path.join(DIST_DIR, 'assets');
  if (!fs.existsSync(assetsDir)) {
    log.warn('Assets directory not found');
    return false;
  }
  
  const files = fs.readdirSync(assetsDir);
  let totalSizeKB = 0;
  let maxChunkSizeKB = 0;
  
  files.forEach(file => {
    const filePath = path.join(assetsDir, file);
    const stats = fs.statSync(filePath);
    const sizeKB = Math.round(stats.size / 1024 * 100) / 100;
    
    totalSizeKB += sizeKB;
    maxChunkSizeKB = Math.max(maxChunkSizeKB, sizeKB);
    
    if (file.endsWith('.js') || file.endsWith('.css')) {
      if (sizeKB > MAX_CHUNK_SIZE_KB) {
        log.warn(`Large chunk detected: ${file} (${sizeKB}KB > ${MAX_CHUNK_SIZE_KB}KB)`);
      } else {
        log.success(`${file}: ${sizeKB}KB`);
      }
    }
  });
  
  log.info(`Total bundle size: ${Math.round(totalSizeKB * 100) / 100}KB`);
  log.info(`Largest chunk: ${Math.round(maxChunkSizeKB * 100) / 100}KB`);
  
  if (totalSizeKB > MAX_BUNDLE_SIZE_KB) {
    log.warn(`Total bundle size exceeds limit: ${totalSizeKB}KB > ${MAX_BUNDLE_SIZE_KB}KB`);
  }
  
  if (maxChunkSizeKB > MAX_CHUNK_SIZE_KB) {
    log.warn(`Largest chunk exceeds limit: ${maxChunkSizeKB}KB > ${MAX_CHUNK_SIZE_KB}KB`);
  }
  
  return true;
}

/**
 * Check asset integrity
 */
function checkAssetIntegrity() {
  log.title('Checking Asset Integrity');
  
  const htmlPath = path.join(DIST_DIR, 'index.html');
  const htmlContent = fs.readFileSync(htmlPath, 'utf8');
  
  // Extract asset references from HTML
  const assetMatches = htmlContent.match(/(?:src|href)="([^"]+)"/g) || [];
  const assets = assetMatches.map(match => {
    const url = match.split('"')[1];
    return url.startsWith('/') ? url.substring(1) : url;
  }).filter(asset => 
    !asset.startsWith('http') && 
    !asset.startsWith('data:') && 
    asset.length > 0
  );
  
  assets.forEach(asset => {
    const assetPath = path.join(DIST_DIR, asset);
    if (!fs.existsSync(assetPath)) {
      throw new Error(`Referenced asset not found: ${asset}`);
    }
    log.success(`Asset exists: ${asset}`);
  });
  
  return true;
}

/**
 * Check for common issues
 */
function checkCommonIssues() {
  log.title('Checking for Common Issues');
  
  const checks = [
    {
      name: 'Empty files',
      check: () => {
        const files = getAllFiles(DIST_DIR);
        const emptyFiles = files.filter(file => {
          const stats = fs.statSync(file);
          return stats.size === 0;
        });
        
        if (emptyFiles.length > 0) {
          log.warn(`Found ${emptyFiles.length} empty files`);
          emptyFiles.forEach(file => {
            const relativePath = path.relative(DIST_DIR, file);
            log.warn(`  Empty: ${relativePath}`);
          });
        } else {
          log.success('No empty files found');
        }
        return true;
      }
    },
    {
      name: 'Source maps in production',
      check: () => {
        const files = getAllFiles(DIST_DIR);
        const sourceMaps = files.filter(file => file.endsWith('.map'));
        
        if (sourceMaps.length > 0) {
          log.warn(`Found ${sourceMaps.length} source map files in production build`);
        } else {
          log.success('No source maps in production build');
        }
        return true;
      }
    },
    {
      name: 'Unminified code',
      check: () => {
        const assetsDir = path.join(DIST_DIR, 'assets');
        if (!fs.existsSync(assetsDir)) return true;
        
        const jsFiles = fs.readdirSync(assetsDir).filter(file => file.endsWith('.js'));
        const unminified = jsFiles.filter(file => {
          const filePath = path.join(assetsDir, file);
          const content = fs.readFileSync(filePath, 'utf8');
          // Simple heuristic: minified code has very long lines
          const avgLineLength = content.split('\n')
            .reduce((sum, line) => sum + line.length, 0) / content.split('\n').length;
          return avgLineLength < 100; // Probably not minified
        });
        
        if (unminified.length > 0) {
          log.warn(`Potentially unminified JS files: ${unminified.join(', ')}`);
        } else {
          log.success('All JS files appear to be minified');
        }
        return true;
      }
    }
  ];
  
  checks.forEach(({ name, check }) => {
    try {
      check();
    } catch (error) {
      log.error(`${name} check failed: ${error.message}`);
    }
  });
  
  return true;
}

/**
 * Get all files in directory recursively
 */
function getAllFiles(dir, files = []) {
  const fileList = fs.readdirSync(dir);
  
  fileList.forEach(file => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    
    if (stat.isDirectory()) {
      getAllFiles(filePath, files);
    } else {
      files.push(filePath);
    }
  });
  
  return files;
}

/**
 * Main verification function
 */
async function verifyBuild() {
  console.log(`${colors.magenta}🚀 VocabLens Build Verification${colors.reset}\n`);
  
  const checks = [
    { name: 'Build Directory', fn: checkBuildDirectory },
    { name: 'Required Files', fn: checkRequiredFiles },
    { name: 'HTML Structure', fn: validateHTML },
    { name: 'PWA Manifest', fn: validateManifest },
    { name: 'Bundle Sizes', fn: checkBundleSizes },
    { name: 'Asset Integrity', fn: checkAssetIntegrity },
    { name: 'Common Issues', fn: checkCommonIssues }
  ];
  
  let passedChecks = 0;
  let failedChecks = 0;
  
  for (const { name, fn } of checks) {
    try {
      await fn();
      passedChecks++;
    } catch (error) {
      log.error(`${name} check failed: ${error.message}`);
      failedChecks++;
    }
  }
  
  // Summary
  console.log(`\n${colors.cyan}📊 Verification Summary${colors.reset}`);
  console.log(`   Passed: ${colors.green}${passedChecks}${colors.reset}`);
  console.log(`   Failed: ${colors.red}${failedChecks}${colors.reset}`);
  console.log(`   Total:  ${passedChecks + failedChecks}`);
  
  if (failedChecks === 0) {
    console.log(`\n${colors.green}🎉 Build verification completed successfully!${colors.reset}`);
    console.log(`${colors.green}✨ Build is ready for deployment${colors.reset}`);
    return true;
  } else {
    console.log(`\n${colors.red}💥 Build verification failed with ${failedChecks} errors${colors.reset}`);
    console.log(`${colors.red}🔧 Please fix the issues before deploying${colors.reset}`);
    return false;
  }
}

// Run verification if called directly
if (require.main === module) {
  verifyBuild()
    .then(success => {
      process.exit(success ? 0 : 1);
    })
    .catch(error => {
      log.error('Verification failed: ' + error.message);
      process.exit(1);
    });
}

module.exports = { verifyBuild };