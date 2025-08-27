#!/usr/bin/env node

/**
 * Quick production deployment test
 * Tests if the VocabLens app is working in production
 */

import https from 'https';

async function testProduction() {
  console.log('🚀 VocabLens Production Test');
  console.log('============================');
  
  const url = 'https://vocablens.netlify.app';
  
  try {
    console.log(`📡 Testing: ${url}`);
    
    const response = await new Promise((resolve, reject) => {
      const req = https.get(url, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => resolve({
          status: res.statusCode,
          headers: res.headers,
          body: data
        }));
      });
      req.on('error', reject);
      req.setTimeout(10000, () => reject(new Error('Timeout')));
    });
    
    console.log(`📊 Status: HTTP ${response.status}`);
    console.log(`📏 Content Length: ${response.body.length} bytes`);
    
    if (response.status === 200) {
      // Check if it's the VocabLens app
      if (response.body.includes('VocabLens') && response.body.includes('root')) {
        console.log('✅ SUCCESS: VocabLens app is live!');
        console.log('🎉 The app is now accessible to users');
        
        // Check for key elements
        const checks = [
          { name: 'React root element', test: response.body.includes('id="root"') },
          { name: 'VocabLens title', test: response.body.includes('VocabLens') },
          { name: 'Vite assets', test: response.body.includes('/assets/') },
          { name: 'PWA manifest', test: response.body.includes('manifest') }
        ];
        
        console.log('\n🔍 Component checks:');
        checks.forEach(check => {
          console.log(`  ${check.test ? '✅' : '❌'} ${check.name}`);
        });
        
        return true;
      } else {
        console.log('⚠️  WARNING: Site loads but doesn\'t look like VocabLens');
        console.log('   Content preview:', response.body.substring(0, 200) + '...');
        return false;
      }
    } else if (response.status === 404) {
      console.log('❌ FAIL: Site returning 404 - deployment not working');
      console.log('🔧 This means Netlify isn\'t serving the built files properly');
      return false;
    } else {
      console.log(`⚠️  WARNING: Unexpected status ${response.status}`);
      return false;
    }
    
  } catch (error) {
    console.log(`❌ ERROR: ${error.message}`);
    return false;
  }
}

// Test every 15 seconds for 2 minutes
async function monitorDeployment() {
  const maxAttempts = 8; // 2 minutes
  
  for (let i = 1; i <= maxAttempts; i++) {
    console.log(`\n🔄 Attempt ${i}/${maxAttempts}`);
    
    const success = await testProduction();
    
    if (success) {
      console.log('\n🎯 DEPLOYMENT SUCCESSFUL!');
      console.log('✅ VocabLens is now live for users');
      process.exit(0);
    }
    
    if (i < maxAttempts) {
      console.log('⏳ Waiting 15 seconds before next check...');
      await new Promise(resolve => setTimeout(resolve, 15000));
    }
  }
  
  console.log('\n❌ DEPLOYMENT VALIDATION FAILED');
  console.log('🚨 Manual intervention may be required');
  process.exit(1);
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  monitorDeployment().catch(error => {
    console.error('❌ Monitor failed:', error);
    process.exit(1);
  });
}

export default testProduction;