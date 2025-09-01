#!/usr/bin/env node

/**
 * Bulletproof Deployment Validator
 * Validates deployments across Vercel, Netlify, and GitHub Pages
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const { execSync } = require('child_process');

// Configuration
const CONFIG = {
  timeout: 30000,
  retries: 3,
  distDir: path.join(__dirname, '..', 'dist'),
  requiredFiles: [
    'index.html',
    'manifest.json',
    'assets'
  ],
  endpoints: {
    vercel: process.env.VERCEL_URL,
    netlify: process.env.NETLIFY_URL || process.env.URL,
    github: process.env.GITHUB_PAGES_URL
  }
};

// Utility functions
const colors = {
  green: (text) => `\x1b[32m${text}\x1b[0m`,
  red: (text) => `\x1b[31m${text}\x1b[0m`,
  yellow: (text) => `\x1b[33m${text}\x1b[0m`,
  blue: (text) => `\x1b[34m${text}\x1b[0m`,
  cyan: (text) => `\x1b[36m${text}\x1b[0m`
};

const log = {
  info: (msg) => console.log(`${colors.blue('ℹ')} ${msg}`),
  success: (msg) => console.log(`${colors.green('✅')} ${msg}`),
  error: (msg) => console.log(`${colors.red('❌')} ${msg}`),
  warning: (msg) => console.log(`${colors.yellow('⚠️')} ${msg}`),
  step: (msg) => console.log(`${colors.cyan('🔍')} ${msg}`)
};

// Validation functions
async function validateBuildOutput() {
  log.step('Validating build output...');
  
  if (!fs.existsSync(CONFIG.distDir)) {
    log.error('Build directory (dist) not found');
    return false;
  }
  
  const missing = [];
  for (const file of CONFIG.requiredFiles) {
    const filePath = path.join(CONFIG.distDir, file);
    if (!fs.existsSync(filePath)) {
      missing.push(file);
    }
  }
  
  if (missing.length > 0) {
    log.error(`Missing required files: ${missing.join(', ')}`);
    return false;
  }
  
  // Validate HTML files
  const indexHtml = path.join(CONFIG.distDir, 'index.html');
  const htmlContent = fs.readFileSync(indexHtml, 'utf-8');
  
  const requiredTags = [
    '<meta charset="utf-8">',
    '<meta name="viewport"',
    '<link rel="manifest"',
    '<script'
  ];
  
  for (const tag of requiredTags) {
    if (!htmlContent.includes(tag)) {
      log.warning(`HTML missing recommended tag: ${tag}`);
    }
  }
  
  // Check for PWA manifest
  try {
    const manifestPath = path.join(CONFIG.distDir, 'manifest.json');
    const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf-8'));
    
    const requiredManifestFields = ['name', 'short_name', 'start_url', 'display', 'icons'];
    for (const field of requiredManifestFields) {
      if (!manifest[field]) {
        log.warning(`Manifest missing field: ${field}`);
      }
    }
  } catch (error) {
    log.error(`Invalid manifest.json: ${error.message}`);
    return false;
  }
  
  log.success('Build output validation passed');
  return true;
}

async function checkDeploymentHealth(url, platform) {
  return new Promise((resolve) => {
    log.step(`Checking ${platform} deployment health: ${url}`);
    
    if (!url) {
      log.warning(`No URL provided for ${platform}`);
      resolve({ success: false, error: 'No URL provided' });
      return;
    }
    
    const startTime = Date.now();
    
    const request = https.get(url, {
      timeout: CONFIG.timeout,
      headers: {
        'User-Agent': 'VocabLens-Deployment-Validator/1.0'
      }
    }, (res) => {
      const responseTime = Date.now() - startTime;
      
      if (res.statusCode === 200) {
        log.success(`${platform} deployment is healthy (${responseTime}ms)`);
        resolve({ success: true, responseTime, statusCode: res.statusCode });
      } else {
        log.error(`${platform} deployment returned status ${res.statusCode}`);
        resolve({ success: false, statusCode: res.statusCode });
      }
    });
    
    request.on('error', (error) => {
      log.error(`${platform} deployment check failed: ${error.message}`);
      resolve({ success: false, error: error.message });
    });
    
    request.on('timeout', () => {
      log.error(`${platform} deployment check timed out`);
      request.destroy();
      resolve({ success: false, error: 'Timeout' });
    });
  });
}

async function validatePerformance(url) {
  log.step('Running performance validation...');
  
  try {
    // Simple performance check - measure response time
    const start = Date.now();
    const result = await checkDeploymentHealth(url, 'Performance Test');
    const responseTime = Date.now() - start;
    
    if (responseTime > 3000) {
      log.warning(`Slow response time: ${responseTime}ms`);
    } else if (responseTime > 1000) {
      log.info(`Good response time: ${responseTime}ms`);
    } else {
      log.success(`Excellent response time: ${responseTime}ms`);
    }
    
    return { responseTime, success: result.success };
  } catch (error) {
    log.error(`Performance validation failed: ${error.message}`);
    return { success: false, error: error.message };
  }
}

async function checkSecurityHeaders(url) {
  return new Promise((resolve) => {
    log.step('Checking security headers...');
    
    if (!url) {
      log.warning('No URL provided for security check');
      resolve({ success: false, error: 'No URL provided' });
      return;
    }
    
    https.get(url, (res) => {
      const securityHeaders = {
        'x-frame-options': res.headers['x-frame-options'],
        'x-content-type-options': res.headers['x-content-type-options'],
        'x-xss-protection': res.headers['x-xss-protection'],
        'strict-transport-security': res.headers['strict-transport-security'],
        'content-security-policy': res.headers['content-security-policy']
      };
      
      const missingHeaders = [];
      const expectedHeaders = {
        'x-frame-options': ['DENY', 'SAMEORIGIN'],
        'x-content-type-options': ['nosniff'],
        'x-xss-protection': ['1; mode=block']
      };
      
      for (const [header, expectedValues] of Object.entries(expectedHeaders)) {
        const value = securityHeaders[header];
        if (!value || !expectedValues.some(expected => value.includes(expected))) {
          missingHeaders.push(header);
        }
      }
      
      if (missingHeaders.length === 0) {
        log.success('Security headers validation passed');
        resolve({ success: true, headers: securityHeaders });
      } else {
        log.warning(`Missing security headers: ${missingHeaders.join(', ')}`);
        resolve({ success: true, warnings: missingHeaders, headers: securityHeaders });
      }
    }).on('error', (error) => {
      log.error(`Security headers check failed: ${error.message}`);
      resolve({ success: false, error: error.message });
    });
  });
}

async function generateReport(results) {
  log.step('Generating deployment report...');
  
  const report = {
    timestamp: new Date().toISOString(),
    buildValidation: results.buildValidation,
    deploymentHealth: results.deploymentHealth,
    securityCheck: results.securityCheck,
    performance: results.performance,
    summary: {
      total: 0,
      passed: 0,
      failed: 0,
      warnings: 0
    }
  };
  
  // Calculate summary
  Object.values(results).forEach(result => {
    if (typeof result === 'object' && result.success !== undefined) {
      report.summary.total++;
      if (result.success) {
        report.summary.passed++;
      } else {
        report.summary.failed++;
      }
      if (result.warnings && result.warnings.length > 0) {
        report.summary.warnings++;
      }
    }
  });
  
  const reportPath = path.join(__dirname, '..', 'deployment-validation-report.json');
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
  
  log.success(`Report generated: ${reportPath}`);
  return report;
}

// Main execution
async function main() {
  console.log(colors.cyan('🚀 VocabLens Deployment Validator\n'));
  
  const results = {};
  let hasErrors = false;
  
  try {
    // 1. Validate build output
    results.buildValidation = { success: await validateBuildOutput() };
    if (!results.buildValidation.success) hasErrors = true;
    
    // 2. Check deployment health for all platforms
    results.deploymentHealth = {};
    for (const [platform, url] of Object.entries(CONFIG.endpoints)) {
      if (url) {
        results.deploymentHealth[platform] = await checkDeploymentHealth(url, platform);
        if (!results.deploymentHealth[platform].success) hasErrors = true;
      }
    }
    
    // 3. Security headers check (use first available URL)
    const testUrl = Object.values(CONFIG.endpoints).find(url => url);
    if (testUrl) {
      results.securityCheck = await checkSecurityHeaders(testUrl);
      results.performance = await validatePerformance(testUrl);
    } else {
      log.warning('No deployment URL found for security and performance checks');
    }
    
    // 4. Generate report
    const report = await generateReport(results);
    
    // 5. Display summary
    console.log('\n' + colors.cyan('📊 Validation Summary:'));
    console.log(`Total checks: ${report.summary.total}`);
    console.log(`${colors.green('Passed:')} ${report.summary.passed}`);
    console.log(`${colors.red('Failed:')} ${report.summary.failed}`);
    console.log(`${colors.yellow('Warnings:')} ${report.summary.warnings}`);
    
    if (hasErrors) {
      console.log('\n' + colors.red('❌ Deployment validation failed'));
      process.exit(1);
    } else {
      console.log('\n' + colors.green('✅ Deployment validation passed'));
      process.exit(0);
    }
    
  } catch (error) {
    log.error(`Validation failed: ${error.message}`);
    console.error(error);
    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  main();
}

module.exports = {
  validateBuildOutput,
  checkDeploymentHealth,
  validatePerformance,
  checkSecurityHeaders,
  generateReport
};