#!/usr/bin/env node
/**
 * Deployment Health Check Script
 * Comprehensive validation for build output and deployment readiness
 */

import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('🔍 VocabLens Deployment Health Check\n');

// Configuration
const distPath = './dist';
const requiredFiles = [
  'index.html',
  'manifest.json',
  'sw.js',
  '_redirects'
];

const requiredAssets = [
  'index-ClymW5aY.css',
  'index-DmXXmnPV.js',
  'react-vendor-BvX3KSce.js'
];

let issues = [];
let warnings = [];

// 1. Check build output exists
console.log('✅ Checking build output...');
if (!fs.existsSync(distPath)) {
  issues.push('❌ dist/ directory not found. Run `npm run build` first.');
} else {
  console.log('   ✓ dist/ directory exists');
}

// 2. Check required files
console.log('\n✅ Checking required files...');
requiredFiles.forEach(file => {
  const filePath = path.join(distPath, file);
  if (fs.existsSync(filePath)) {
    console.log(`   ✓ ${file}`);
  } else {
    issues.push(`❌ Missing required file: ${file}`);
  }
});

// 3. Check index.html structure
console.log('\n✅ Validating index.html...');
const indexPath = path.join(distPath, 'index.html');
if (fs.existsSync(indexPath)) {
  const indexContent = fs.readFileSync(indexPath, 'utf8');
  
  // Check for required elements
  const checks = [
    { test: /<div id="root"><\/div>/, message: 'React root element' },
    { test: /src="\/assets\/index-[a-zA-Z0-9-]+\.js"/, message: 'Main JS bundle reference' },
    { test: /href="\/assets\/index-[a-zA-Z0-9-]+\.css"/, message: 'CSS bundle reference' },
    { test: /<meta name="viewport"/, message: 'Viewport meta tag' },
    { test: /<title>VocabLens/, message: 'Page title' }
  ];
  
  checks.forEach(check => {
    if (check.test.test(indexContent)) {
      console.log(`   ✓ ${check.message}`);
    } else {
      issues.push(`❌ index.html missing: ${check.message}`);
    }
  });
} else {
  issues.push('❌ index.html not found in dist/');
}

// 4. Check assets directory
console.log('\n✅ Checking assets...');
const assetsPath = path.join(distPath, 'assets');
if (fs.existsSync(assetsPath)) {
  const assets = fs.readdirSync(assetsPath);
  console.log(`   ✓ Found ${assets.length} asset files`);
  
  // Check for critical assets (pattern matching since filenames have hashes)
  const hasMainJS = assets.some(file => file.match(/^index-[a-zA-Z0-9-]+\.js$/));
  const hasMainCSS = assets.some(file => file.match(/^index-[a-zA-Z0-9-]+\.css$/));
  const hasReactVendor = assets.some(file => file.match(/^react-vendor-[a-zA-Z0-9-]+\.js$/));
  
  if (hasMainJS) console.log('   ✓ Main JS bundle found');
  else issues.push('❌ Main JS bundle missing');
  
  if (hasMainCSS) console.log('   ✓ Main CSS bundle found');
  else issues.push('❌ Main CSS bundle missing');
  
  if (hasReactVendor) console.log('   ✓ React vendor bundle found');
  else warnings.push('⚠️ React vendor bundle missing - may impact performance');
  
} else {
  issues.push('❌ assets/ directory not found');
}

// 5. Check PWA files
console.log('\n✅ Checking PWA configuration...');
const pwaDependencies = ['manifest.json', 'sw.js', 'icon-192.png', 'icon-512.png'];
pwaDependencies.forEach(file => {
  if (fs.existsSync(path.join(distPath, file))) {
    console.log(`   ✓ ${file}`);
  } else {
    warnings.push(`⚠️ PWA file missing: ${file}`);
  }
});

// 6. Check routing configuration
console.log('\n✅ Checking SPA routing...');
const redirectsPath = path.join(distPath, '_redirects');
if (fs.existsSync(redirectsPath)) {
  const redirectsContent = fs.readFileSync(redirectsPath, 'utf8');
  if (redirectsContent.includes('/*    /index.html   200')) {
    console.log('   ✓ SPA routing configured correctly');
  } else {
    issues.push('❌ _redirects file incorrect format');
  }
} else {
  issues.push('❌ _redirects file missing');
}

// 7. Environment check
console.log('\n✅ Checking environment configuration...');
try {
  const packageJson = JSON.parse(fs.readFileSync('./package.json', 'utf8'));
  console.log(`   ✓ Project: ${packageJson.name} v${packageJson.version}`);
  console.log(`   ✓ Build script: ${packageJson.scripts.build}`);
  
  // Check if build was run recently
  const indexStat = fs.statSync(indexPath);
  const buildAge = Date.now() - indexStat.mtime.getTime();
  const buildAgeMinutes = Math.floor(buildAge / (1000 * 60));
  
  if (buildAgeMinutes < 60) {
    console.log(`   ✓ Build is recent (${buildAgeMinutes} minutes ago)`);
  } else {
    warnings.push(`⚠️ Build is ${buildAgeMinutes} minutes old - consider rebuilding`);
  }
  
} catch (error) {
  warnings.push('⚠️ Could not read package.json');
}

// 8. Size analysis
console.log('\n✅ Build size analysis...');
if (fs.existsSync(assetsPath)) {
  let totalSize = 0;
  let jsSize = 0;
  let cssSize = 0;
  
  const assets = fs.readdirSync(assetsPath);
  assets.forEach(file => {
    const filePath = path.join(assetsPath, file);
    const stat = fs.statSync(filePath);
    totalSize += stat.size;
    
    if (file.endsWith('.js')) jsSize += stat.size;
    if (file.endsWith('.css')) cssSize += stat.size;
  });
  
  console.log(`   ✓ Total assets: ${(totalSize / 1024).toFixed(1)} KB`);
  console.log(`   ✓ JavaScript: ${(jsSize / 1024).toFixed(1)} KB`);
  console.log(`   ✓ CSS: ${(cssSize / 1024).toFixed(1)} KB`);
  
  if (totalSize > 2 * 1024 * 1024) { // 2MB
    warnings.push('⚠️ Large bundle size - consider code splitting');
  }
}

// Summary
console.log('\n📊 Health Check Summary');
console.log('========================');

if (issues.length === 0 && warnings.length === 0) {
  console.log('🎉 All checks passed! Deployment ready.');
  console.log('\n🚀 Next steps:');
  console.log('   1. Test locally: npm run preview');
  console.log('   2. Deploy to staging');
  console.log('   3. Run production smoke tests');
  process.exit(0);
} else {
  if (issues.length > 0) {
    console.log('\n❌ Critical Issues Found:');
    issues.forEach(issue => console.log(issue));
  }
  
  if (warnings.length > 0) {
    console.log('\n⚠️ Warnings:');
    warnings.forEach(warning => console.log(warning));
  }
  
  console.log('\n🔧 Recommended Actions:');
  if (issues.length > 0) {
    console.log('   1. Run: npm run build');
    console.log('   2. Check build logs for errors');
    console.log('   3. Verify vite.config.ts configuration');
  }
  
  if (warnings.length > 0) {
    console.log('   4. Review warnings above');
    console.log('   5. Test locally before deploying');
  }
  
  process.exit(issues.length > 0 ? 1 : 0);
}