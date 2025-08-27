#!/usr/bin/env node

/**
 * Build Output Verification Script
 * Verifies that the Vite build process creates the expected files for Vercel deployment
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const DIST_DIR = path.join(process.cwd(), 'dist');
const REQUIRED_FILES = [
    'index.html',
    'assets'  // Vite creates an assets folder
];

const EXPECTED_PATTERNS = [
    /\.css$/,      // CSS files
    /\.js$/,       // JavaScript files  
    /\.svg$/,      // Icon files
    /\.png$/,      // Image files
    /\.ico$/       // Favicon
];

function checkBuildOutput() {
    console.log('🔍 Verifying Vite build output for Vercel deployment...\n');
    
    // Check if dist directory exists
    if (!fs.existsSync(DIST_DIR)) {
        console.error('❌ ERROR: dist/ directory not found');
        console.error('   Run "npm run build" first');
        process.exit(1);
    }
    
    console.log('✅ dist/ directory exists');
    
    // Check required files
    for (const file of REQUIRED_FILES) {
        const filePath = path.join(DIST_DIR, file);
        if (!fs.existsSync(filePath)) {
            console.error(`❌ ERROR: Required file/folder missing: ${file}`);
            process.exit(1);
        }
        console.log(`✅ Found: ${file}`);
    }
    
    // Check index.html content
    const indexPath = path.join(DIST_DIR, 'index.html');
    const indexContent = fs.readFileSync(indexPath, 'utf8');
    
    if (!indexContent.includes('<div id="root">')) {
        console.error('❌ ERROR: index.html missing React root element');
        process.exit(1);
    }
    console.log('✅ index.html contains React root element');
    
    if (!indexContent.includes('/assets/')) {
        console.error('❌ WARNING: No asset references found in index.html');
    } else {
        console.log('✅ index.html references assets correctly');
    }
    
    // List all files in dist
    console.log('\n📁 Build output contents:');
    listDirectory(DIST_DIR, '');
    
    // Check assets folder
    const assetsDir = path.join(DIST_DIR, 'assets');
    if (fs.existsSync(assetsDir)) {
        const assetFiles = fs.readdirSync(assetsDir);
        const hasCSS = assetFiles.some(f => f.endsWith('.css'));
        const hasJS = assetFiles.some(f => f.endsWith('.js'));
        
        console.log(`\n📦 Assets summary:`);
        console.log(`   CSS files: ${hasCSS ? '✅' : '❌'}`);
        console.log(`   JS files: ${hasJS ? '✅' : '❌'}`);
        console.log(`   Total files: ${assetFiles.length}`);
    }
    
    console.log('\n🎉 Build verification complete!');
    console.log('\n📋 Vercel Deployment Checklist:');
    console.log('   1. Push changes to GitHub');
    console.log('   2. Verify vercel.json configuration');
    console.log('   3. Check Vercel build logs for errors');
    console.log('   4. Test deployment URL');
}

function listDirectory(dir, prefix) {
    try {
        const items = fs.readdirSync(dir);
        for (const item of items) {
            const fullPath = path.join(dir, item);
            const stats = fs.statSync(fullPath);
            
            if (stats.isDirectory()) {
                console.log(`${prefix}📁 ${item}/`);
                if (item === 'assets') {
                    // Show assets contents
                    listDirectory(fullPath, prefix + '   ');
                }
            } else {
                const size = (stats.size / 1024).toFixed(1);
                console.log(`${prefix}📄 ${item} (${size} KB)`);
            }
        }
    } catch (error) {
        console.error(`Error reading directory ${dir}:`, error.message);
    }
}

// Run verification
checkBuildOutput();