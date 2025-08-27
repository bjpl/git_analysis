#!/usr/bin/env node

/**
 * VocabLens Deployment Health Check
 * Validates that the deployed application is working correctly
 */

import https from 'https';
import fs from 'fs';

const DEPLOYMENT_URLS = [
  'https://vocablens.netlify.app',
  // Add backup URLs if needed
];

const HEALTH_CHECKS = [
  {
    name: 'Homepage loads',
    path: '/',
    expect: ['VocabLens', 'root', 'index-']
  },
  {
    name: 'Assets loading',
    path: '/assets/',
    expect: ['js', 'css']
  },
  {
    name: 'SPA routing works',
    path: '/search',
    expect: ['VocabLens', 'root']
  },
  {
    name: 'Vocabulary page',
    path: '/vocabulary',
    expect: ['VocabLens', 'root']
  }
];

function makeRequest(url, timeout = 10000) {
  return new Promise((resolve, reject) => {
    const req = https.get(url, { timeout }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        resolve({
          status: res.statusCode,
          headers: res.headers,
          body: data,
          url: url
        });
      });
    });
    
    req.on('error', reject);
    req.on('timeout', () => {
      req.destroy();
      reject(new Error(`Request timeout after ${timeout}ms`));
    });
  });
}

async function checkHealth(baseUrl) {
  const results = [];
  
  console.log(`\n🔍 Testing deployment: ${baseUrl}`);
  
  for (const check of HEALTH_CHECKS) {
    const url = baseUrl + check.path;
    console.log(`  Testing: ${check.name}...`);
    
    try {
      const response = await makeRequest(url);
      
      if (response.status !== 200) {
        results.push({
          ...check,
          status: 'FAIL',
          error: `HTTP ${response.status}`,
          url
        });
        console.log(`    ❌ FAIL: HTTP ${response.status}`);
        continue;
      }
      
      // Check content expectations
      const hasExpectedContent = check.expect.every(expected => 
        response.body.includes(expected)
      );
      
      if (!hasExpectedContent) {
        const missing = check.expect.filter(expected => 
          !response.body.includes(expected)
        );
        results.push({
          ...check,
          status: 'FAIL',
          error: `Missing content: ${missing.join(', ')}`,
          url
        });
        console.log(`    ❌ FAIL: Missing content: ${missing.join(', ')}`);
      } else {
        results.push({
          ...check,
          status: 'PASS',
          url
        });
        console.log(`    ✅ PASS`);
      }
      
    } catch (error) {
      results.push({
        ...check,
        status: 'ERROR',
        error: error.message,
        url
      });
      console.log(`    ❌ ERROR: ${error.message}`);
    }
  }
  
  return results;
}

async function main() {
  console.log('🚀 VocabLens Production Health Check');
  console.log('=====================================');
  
  const allResults = [];
  
  for (const url of DEPLOYMENT_URLS) {
    const results = await checkHealth(url);
    allResults.push({ url, results });
  }
  
  // Summary
  console.log('\n📊 Health Check Summary');
  console.log('=======================');
  
  let overallPassed = true;
  
  for (const deployment of allResults) {
    console.log(`\n🌐 ${deployment.url}`);
    
    const passed = deployment.results.filter(r => r.status === 'PASS').length;
    const total = deployment.results.length;
    const percentage = Math.round((passed / total) * 100);
    
    console.log(`  Status: ${passed}/${total} checks passed (${percentage}%)`);
    
    if (percentage < 100) {
      overallPassed = false;
      console.log('  Failed checks:');
      deployment.results
        .filter(r => r.status !== 'PASS')
        .forEach(r => {
          console.log(`    • ${r.name}: ${r.error || 'Unknown error'}`);
        });
    }
  }
  
  console.log('\n' + '='.repeat(50));
  
  if (overallPassed) {
    console.log('🎉 ALL HEALTH CHECKS PASSED!');
    console.log('✅ VocabLens is ready for production use');
    process.exit(0);
  } else {
    console.log('❌ SOME HEALTH CHECKS FAILED');
    console.log('🚨 Deployment needs attention before production use');
    process.exit(1);
  }
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(error => {
    console.error('❌ Health check failed:', error);
    process.exit(1);
  });
}

export { checkHealth, makeRequest };