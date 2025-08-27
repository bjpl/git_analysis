#!/usr/bin/env node

/**
 * Manual Deployment Test Script
 * Creates a minimal deployment package for testing
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const DIST_DIR = path.join(process.cwd(), 'dist');
const TEST_DIR = path.join(process.cwd(), 'test-deploy');

function createTestDeployment() {
    console.log('🧪 Creating test deployment package...\n');
    
    // Create test directory
    if (fs.existsSync(TEST_DIR)) {
        fs.rmSync(TEST_DIR, { recursive: true });
    }
    fs.mkdirSync(TEST_DIR, { recursive: true });
    
    // Create minimal index.html
    const indexContent = `<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>VocabLens - Test Deploy</title>
</head>
<body>
    <div id="root">
        <h1>VocabLens Test Deployment</h1>
        <p>If you see this, the basic deployment is working!</p>
        <p>Timestamp: ${new Date().toISOString()}</p>
    </div>
</body>
</html>`;
    
    fs.writeFileSync(path.join(TEST_DIR, 'index.html'), indexContent);
    
    // Create _redirects for SPA
    const redirectsContent = '/*    /index.html   200\n';
    fs.writeFileSync(path.join(TEST_DIR, '_redirects'), redirectsContent);
    
    // Create manifest.json
    const manifestContent = {
        name: "VocabLens Test",
        short_name: "VocabLens",
        start_url: "/",
        display: "standalone",
        theme_color: "#4f46e5",
        background_color: "#ffffff"
    };
    fs.writeFileSync(path.join(TEST_DIR, 'manifest.json'), JSON.stringify(manifestContent, null, 2));
    
    console.log('✅ Test deployment package created:');
    console.log(`   Directory: ${TEST_DIR}`);
    console.log('   Files:');
    const files = fs.readdirSync(TEST_DIR);
    files.forEach(file => {
        const stats = fs.statSync(path.join(TEST_DIR, file));
        console.log(`   - ${file} (${stats.size} bytes)`);
    });
    
    console.log('\n📋 Manual Deployment Instructions:');
    console.log('1. Go to https://app.netlify.com/sites/vocablens-pwa');
    console.log(`2. Drag the entire contents of: ${TEST_DIR}`);
    console.log('3. Wait for deployment to complete');
    console.log('4. Test the site URL');
    console.log('\nIf this basic deployment works, the issue is in the build process.');
    console.log('If it doesn\'t work, the issue is in Netlify configuration.');
}

createTestDeployment();