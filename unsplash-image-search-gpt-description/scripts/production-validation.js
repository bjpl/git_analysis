#!/usr/bin/env node

/**
 * Production Validation Script for VocabLens
 * Comprehensive validation of production deployment readiness
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.join(__dirname, '..');

// ANSI color codes for console output
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  bold: '\x1b[1m'
};

class ProductionValidator {
  constructor() {
    this.results = [];
    this.errors = [];
    this.warnings = [];
  }

  log(level, message, details = null) {
    const timestamp = new Date().toISOString();
    const entry = { timestamp, level, message, details };
    
    switch (level) {
      case 'ERROR':
        this.errors.push(entry);
        console.log(`${colors.red}❌ ${message}${colors.reset}`);
        break;
      case 'WARN':
        this.warnings.push(entry);
        console.log(`${colors.yellow}⚠️  ${message}${colors.reset}`);
        break;
      case 'SUCCESS':
        console.log(`${colors.green}✅ ${message}${colors.reset}`);
        break;
      case 'INFO':
        console.log(`${colors.blue}ℹ️  ${message}${colors.reset}`);
        break;
      default:
        console.log(message);
    }
    
    this.results.push(entry);
  }

  async validateBuildOutput() {
    console.log(`\n${colors.bold}${colors.cyan}📦 Build Output Validation${colors.reset}`);
    
    const distPath = path.join(rootDir, 'dist');
    
    if (!fs.existsSync(distPath)) {
      this.log('ERROR', 'Build output directory (dist/) not found. Run npm run build first.');
      return false;
    }
    
    this.log('SUCCESS', 'Build output directory exists');
    
    // Check essential files
    const essentialFiles = [
      'index.html',
      'manifest.json',
      'sw.js',
      '_redirects'
    ];
    
    let allFilesExist = true;
    essentialFiles.forEach(file => {
      const filePath = path.join(distPath, file);
      if (fs.existsSync(filePath)) {
        this.log('SUCCESS', `Essential file present: ${file}`);
      } else {
        this.log('ERROR', `Missing essential file: ${file}`);
        allFilesExist = false;
      }
    });
    
    // Check assets directory
    const assetsPath = path.join(distPath, 'assets');
    if (fs.existsSync(assetsPath)) {
      const assets = fs.readdirSync(assetsPath);
      const jsFiles = assets.filter(f => f.endsWith('.js'));
      const cssFiles = assets.filter(f => f.endsWith('.css'));
      
      this.log('SUCCESS', `Found ${assets.length} assets (${jsFiles.length} JS, ${cssFiles.length} CSS)`);
      
      // Check bundle sizes
      let totalSize = 0;
      assets.forEach(asset => {
        const stat = fs.statSync(path.join(assetsPath, asset));
        totalSize += stat.size;
        
        if (stat.size > 5 * 1024 * 1024) { // 5MB
          this.log('WARN', `Large asset detected: ${asset} (${(stat.size / 1024 / 1024).toFixed(2)}MB)`);
        }
      });
      
      const totalMB = totalSize / 1024 / 1024;
      if (totalMB < 20) {
        this.log('SUCCESS', `Total bundle size: ${totalMB.toFixed(2)}MB`);
      } else {
        this.log('WARN', `Large total bundle size: ${totalMB.toFixed(2)}MB`);
      }
    } else {
      this.log('WARN', 'Assets directory not found');
    }
    
    return allFilesExist;
  }

  async validatePWAConfiguration() {
    console.log(`\n${colors.bold}${colors.cyan}📱 PWA Configuration Validation${colors.reset}`);
    
    const manifestPath = path.join(rootDir, 'dist', 'manifest.json');
    
    if (!fs.existsSync(manifestPath)) {
      this.log('ERROR', 'PWA manifest.json not found');
      return false;
    }
    
    try {
      const manifestContent = fs.readFileSync(manifestPath, 'utf8');
      const manifest = JSON.parse(manifestContent);
      
      // Validate required manifest fields
      const requiredFields = [
        'name',
        'short_name',
        'description',
        'start_url',
        'display',
        'theme_color',
        'background_color',
        'icons'
      ];
      
      let allFieldsValid = true;
      requiredFields.forEach(field => {
        if (manifest[field]) {
          this.log('SUCCESS', `Manifest field present: ${field}`);
        } else {
          this.log('ERROR', `Missing manifest field: ${field}`);
          allFieldsValid = false;
        }
      });
      
      // Validate icons
      if (manifest.icons && Array.isArray(manifest.icons)) {
        manifest.icons.forEach((icon, index) => {
          if (icon.src && icon.sizes && icon.type) {
            this.log('SUCCESS', `Icon ${index + 1}: ${icon.sizes} (${icon.type})`);
          } else {
            this.log('ERROR', `Invalid icon configuration at index ${index}`);
          }
        });
      }
      
      // Check service worker
      const swPath = path.join(rootDir, 'dist', 'sw.js');
      if (fs.existsSync(swPath)) {
        const swContent = fs.readFileSync(swPath, 'utf8');
        if (swContent.length > 100) {
          this.log('SUCCESS', 'Service worker present and has content');
        } else {
          this.log('WARN', 'Service worker is too small, may not be functional');
        }
      } else {
        this.log('ERROR', 'Service worker not found');
      }
      
      return allFieldsValid;
    } catch (error) {
      this.log('ERROR', 'Failed to parse manifest.json', error.message);
      return false;
    }
  }

  async validateSecurityConfiguration() {
    console.log(`\n${colors.bold}${colors.cyan}🔒 Security Configuration Validation${colors.reset}`);
    
    // Check Netlify configuration
    const netlifyConfigPath = path.join(rootDir, 'netlify.toml');
    if (fs.existsSync(netlifyConfigPath)) {
      const configContent = fs.readFileSync(netlifyConfigPath, 'utf8');
      
      const securityHeaders = [
        'X-Frame-Options',
        'X-XSS-Protection',
        'X-Content-Type-Options',
        'Strict-Transport-Security',
        'Cache-Control'
      ];
      
      let allHeadersConfigured = true;
      securityHeaders.forEach(header => {
        if (configContent.includes(header)) {
          this.log('SUCCESS', `Security header configured: ${header}`);
        } else {
          this.log('ERROR', `Missing security header: ${header}`);
          allHeadersConfigured = false;
        }
      });
      
      // Check SPA routing
      if (configContent.includes('to = "/index.html"')) {
        this.log('SUCCESS', 'SPA routing configured');
      } else {
        this.log('ERROR', 'SPA routing not properly configured');
        allHeadersConfigured = false;
      }
      
      return allHeadersConfigured;
    } else {
      this.log('ERROR', 'netlify.toml configuration not found');
      return false;
    }
  }

  async validateIndexHTML() {
    console.log(`\n${colors.bold}${colors.cyan}📄 Index HTML Validation${colors.reset}`);
    
    const indexPath = path.join(rootDir, 'dist', 'index.html');
    if (!fs.existsSync(indexPath)) {
      this.log('ERROR', 'index.html not found in dist/');
      return false;
    }
    
    const htmlContent = fs.readFileSync(indexPath, 'utf8');
    
    // Check HTML5 doctype
    if (htmlContent.match(/<!doctype html>/i)) {
      this.log('SUCCESS', 'HTML5 doctype present');
    } else {
      this.log('ERROR', 'Missing HTML5 doctype');
    }
    
    // Check meta tags
    const metaTags = [
      { name: 'viewport', regex: /name="viewport"/ },
      { name: 'theme-color', regex: /name="theme-color"/ },
      { name: 'description', regex: /name="description"/ },
      { name: 'charset', regex: /charset="UTF-8"/ }
    ];
    
    metaTags.forEach(tag => {
      if (tag.regex.test(htmlContent)) {
        this.log('SUCCESS', `Meta tag present: ${tag.name}`);
      } else {
        this.log('ERROR', `Missing meta tag: ${tag.name}`);
      }
    });
    
    // Check preconnect hints
    const preconnectDomains = [
      'api.unsplash.com',
      'images.unsplash.com',
      'api.openai.com'
    ];
    
    preconnectDomains.forEach(domain => {
      if (htmlContent.includes(domain)) {
        this.log('SUCCESS', `Preconnect configured for: ${domain}`);
      } else {
        this.log('WARN', `Missing preconnect for performance: ${domain}`);
      }
    });
    
    // Check for sensitive data
    const sensitivePatterns = [
      /sk-[a-zA-Z0-9]{32,}/,  // OpenAI API keys
      /your_api_key/,          // Placeholder keys
      /localhost:\d+/,         // Development URLs
      /127\.0\.0\.1:\d+/       // Local IPs
    ];
    
    let hasSensitiveData = false;
    sensitivePatterns.forEach(pattern => {
      if (pattern.test(htmlContent)) {
        this.log('ERROR', `Sensitive data detected in HTML: ${pattern}`);
        hasSensitiveData = true;
      }
    });
    
    if (!hasSensitiveData) {
      this.log('SUCCESS', 'No sensitive data detected in HTML');
    }
    
    return !hasSensitiveData;
  }

  async validateEnvironmentConfiguration() {
    console.log(`\n${colors.bold}${colors.cyan}⚙️  Environment Configuration Validation${colors.reset}`);
    
    const envExamplePath = path.join(rootDir, '.env.example');
    if (!fs.existsSync(envExamplePath)) {
      this.log('ERROR', '.env.example not found');
      return false;
    }
    
    const envContent = fs.readFileSync(envExamplePath, 'utf8');
    
    const requiredVars = [
      'VITE_APP_NAME',
      'VITE_APP_VERSION',
      'VITE_UNSPLASH_ACCESS_KEY',
      'VITE_OPENAI_API_KEY',
      'VITE_API_TIMEOUT_MS',
      'VITE_ENABLE_PWA'
    ];
    
    let allVarsDocumented = true;
    requiredVars.forEach(varName => {
      if (envContent.includes(varName)) {
        this.log('SUCCESS', `Environment variable documented: ${varName}`);
      } else {
        this.log('ERROR', `Missing environment variable: ${varName}`);
        allVarsDocumented = false;
      }
    });
    
    // Check for actual .env file (should not exist in production)
    const envPath = path.join(rootDir, '.env');
    if (fs.existsSync(envPath)) {
      this.log('WARN', '.env file found - ensure it\'s not deployed to production');
    } else {
      this.log('SUCCESS', 'No .env file in repository (good for security)');
    }
    
    return allVarsDocumented;
  }

  async validatePackageConfiguration() {
    console.log(`\n${colors.bold}${colors.cyan}📦 Package Configuration Validation${colors.reset}`);
    
    const packagePath = path.join(rootDir, 'package.json');
    const packageContent = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
    
    // Check required scripts
    const requiredScripts = ['build', 'dev', 'preview', 'test'];
    let allScriptsPresent = true;
    
    requiredScripts.forEach(script => {
      if (packageContent.scripts && packageContent.scripts[script]) {
        this.log('SUCCESS', `Script present: ${script}`);
      } else {
        this.log('ERROR', `Missing script: ${script}`);
        allScriptsPresent = false;
      }
    });
    
    // Check production build script
    if (packageContent.scripts?.build) {
      if (packageContent.scripts.build.includes('vite build')) {
        this.log('SUCCESS', 'Production build script uses Vite');
      } else {
        this.log('WARN', 'Build script may not be optimized for production');
      }
    }
    
    // Check dependencies vs devDependencies
    const buildTools = ['vite', 'typescript', '@vitejs/plugin-react-swc', 'vitest'];
    buildTools.forEach(tool => {
      if (packageContent.devDependencies?.[tool]) {
        this.log('SUCCESS', `Build tool in devDependencies: ${tool}`);
      } else if (packageContent.dependencies?.[tool]) {
        this.log('WARN', `Build tool should be in devDependencies: ${tool}`);
      }
    });
    
    return allScriptsPresent;
  }

  async validateDeploymentReadiness() {
    console.log(`\n${colors.bold}${colors.cyan}🚀 Deployment Readiness Check${colors.reset}`);
    
    const deploymentFiles = [
      { file: 'netlify.toml', required: true },
      { file: 'dist/_redirects', required: true },
      { file: '.gitignore', required: true },
      { file: 'README.md', required: false }
    ];
    
    let deploymentReady = true;
    deploymentFiles.forEach(({ file, required }) => {
      const filePath = path.join(rootDir, file);
      if (fs.existsSync(filePath)) {
        this.log('SUCCESS', `Deployment file present: ${file}`);
      } else if (required) {
        this.log('ERROR', `Missing required deployment file: ${file}`);
        deploymentReady = false;
      } else {
        this.log('WARN', `Optional deployment file missing: ${file}`);
      }
    });
    
    return deploymentReady;
  }

  generateReport() {
    console.log(`\n${colors.bold}${colors.magenta}📊 Production Validation Report${colors.reset}`);
    console.log('='.repeat(50));
    
    const totalTests = this.results.length;
    const errors = this.errors.length;
    const warnings = this.warnings.length;
    const passed = totalTests - errors - warnings;
    
    console.log(`\n${colors.bold}Summary:${colors.reset}`);
    console.log(`  Total Checks: ${totalTests}`);
    console.log(`  ${colors.green}✅ Passed: ${passed}${colors.reset}`);
    console.log(`  ${colors.yellow}⚠️  Warnings: ${warnings}${colors.reset}`);
    console.log(`  ${colors.red}❌ Errors: ${errors}${colors.reset}`);
    
    if (errors > 0) {
      console.log(`\n${colors.bold}${colors.red}Critical Issues:${colors.reset}`);
      this.errors.forEach(error => {
        console.log(`  ❌ ${error.message}`);
        if (error.details) {
          console.log(`     Details: ${error.details}`);
        }
      });
    }
    
    if (warnings > 0) {
      console.log(`\n${colors.bold}${colors.yellow}Warnings:${colors.reset}`);
      this.warnings.forEach(warning => {
        console.log(`  ⚠️  ${warning.message}`);
      });
    }
    
    const score = ((passed / totalTests) * 100).toFixed(1);
    console.log(`\n${colors.bold}Production Readiness Score: ${score}%${colors.reset}`);
    
    if (errors === 0) {
      console.log(`\n${colors.green}${colors.bold}🎉 Production deployment ready!${colors.reset}`);
      return 0; // Exit code 0 for success
    } else {
      console.log(`\n${colors.red}${colors.bold}⛔ Production deployment NOT ready - fix errors first${colors.reset}`);
      return 1; // Exit code 1 for failure
    }
  }

  async validateAll() {
    console.log(`${colors.bold}${colors.cyan}`);
    console.log('🔍 VocabLens Production Validation');
    console.log('==================================');
    console.log(colors.reset);
    
    const validations = [
      this.validateBuildOutput(),
      this.validatePWAConfiguration(),
      this.validateSecurityConfiguration(),
      this.validateIndexHTML(),
      this.validateEnvironmentConfiguration(),
      this.validatePackageConfiguration(),
      this.validateDeploymentReadiness()
    ];
    
    await Promise.all(validations);
    
    return this.generateReport();
  }
}

// Run validation
const validator = new ProductionValidator();
validator.validateAll().then(exitCode => {
  process.exit(exitCode);
}).catch(error => {
  console.error(`${colors.red}Validation failed with error:${colors.reset}`, error);
  process.exit(1);
});