#!/usr/bin/env node

/**
 * Bulletproof Health Check System for VocabLens
 * Comprehensive system validation and monitoring
 * 
 * Features:
 * - Development environment validation
 * - Build system health checks
 * - Dependency integrity verification
 * - Configuration validation
 * - Performance monitoring
 * - Security checks
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const https = require('https');
const { promisify } = require('util');

// Configuration
const PROJECT_ROOT = path.join(__dirname, '..');
const PACKAGE_JSON_PATH = path.join(PROJECT_ROOT, 'package.json');
const NODE_MODULES_PATH = path.join(PROJECT_ROOT, 'node_modules');

// ANSI colors for console output
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m',
  bright: '\x1b[1m'
};

const log = {
  info: (msg) => console.log(`${colors.blue}ℹ${colors.reset} ${msg}`),
  success: (msg) => console.log(`${colors.green}✅${colors.reset} ${msg}`),
  warn: (msg) => console.log(`${colors.yellow}⚠️${colors.reset} ${msg}`),
  error: (msg) => console.log(`${colors.red}❌${colors.reset} ${msg}`),
  title: (msg) => console.log(`\n${colors.cyan}${colors.bright}${msg}${colors.reset}\n`),
  subtitle: (msg) => console.log(`${colors.magenta}📋 ${msg}${colors.reset}`)
};

/**
 * System Information Check
 */
function checkSystemInfo() {
  log.subtitle('System Information');
  
  try {
    const nodeVersion = process.version;
    const npmVersion = execSync('npm --version', { encoding: 'utf8' }).trim();
    const platform = process.platform;
    const arch = process.arch;
    
    log.info(`Node.js: ${nodeVersion}`);
    log.info(`NPM: v${npmVersion}`);
    log.info(`Platform: ${platform} (${arch})`);
    log.info(`Working Directory: ${process.cwd()}`);
    
    // Check Node.js version compatibility
    const majorVersion = parseInt(nodeVersion.split('.')[0].substring(1));
    if (majorVersion >= 18) {
      log.success('Node.js version is compatible');
    } else {
      log.warn(`Node.js version ${nodeVersion} may not be fully compatible. Recommended: 18+`);
    }
    
    return true;
  } catch (error) {
    log.error(`System info check failed: ${error.message}`);
    return false;
  }
}

/**
 * Project Structure Check
 */
function checkProjectStructure() {
  log.subtitle('Project Structure');
  
  const requiredDirs = [
    'src',
    'public',
    'scripts'
  ];
  
  const requiredFiles = [
    'package.json',
    'vite.config.ts',
    'tsconfig.json',
    'tailwind.config.js',
    'src/main.tsx',
    'src/App.tsx',
    'public/manifest.json'
  ];
  
  let allChecksPass = true;
  
  // Check directories
  requiredDirs.forEach(dir => {
    const dirPath = path.join(PROJECT_ROOT, dir);
    if (fs.existsSync(dirPath) && fs.statSync(dirPath).isDirectory()) {
      log.success(`Directory exists: ${dir}/`);
    } else {
      log.error(`Missing directory: ${dir}/`);
      allChecksPass = false;
    }
  });
  
  // Check files
  requiredFiles.forEach(file => {
    const filePath = path.join(PROJECT_ROOT, file);
    if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
      log.success(`File exists: ${file}`);
    } else {
      log.error(`Missing file: ${file}`);
      allChecksPass = false;
    }
  });
  
  return allChecksPass;
}

/**
 * Dependencies Check
 */
function checkDependencies() {
  log.subtitle('Dependencies');
  
  if (!fs.existsSync(PACKAGE_JSON_PATH)) {
    log.error('package.json not found');
    return false;
  }
  
  if (!fs.existsSync(NODE_MODULES_PATH)) {
    log.error('node_modules directory not found. Run: npm install');
    return false;
  }
  
  let packageJson;
  try {
    packageJson = JSON.parse(fs.readFileSync(PACKAGE_JSON_PATH, 'utf8'));
  } catch (error) {
    log.error(`Failed to parse package.json: ${error.message}`);
    return false;
  }
  
  log.success('package.json is valid');
  log.success('node_modules directory exists');
  
  // Check for critical dependencies
  const criticalDeps = ['react', 'react-dom', 'vite'];
  const deps = { ...packageJson.dependencies, ...packageJson.devDependencies };
  
  criticalDeps.forEach(dep => {
    if (deps[dep]) {
      log.success(`${dep}: ${deps[dep]}`);
    } else {
      log.error(`Missing critical dependency: ${dep}`);
      return false;
    }
  });
  
  // Check for potentially problematic dependencies
  const problematicPatterns = [
    /^0\./,  // Pre-1.0 versions
    /beta|alpha|rc/i  // Pre-release versions
  ];
  
  Object.entries(deps).forEach(([name, version]) => {
    if (problematicPatterns.some(pattern => pattern.test(version))) {
      log.warn(`Potentially unstable dependency: ${name}@${version}`);
    }
  });
  
  return true;
}

/**
 * Configuration Files Check
 */
function checkConfigFiles() {
  log.subtitle('Configuration Files');
  
  const configs = [
    {
      file: 'vite.config.ts',
      validator: (content) => {
        return content.includes('defineConfig') && 
               content.includes('@vitejs/plugin-react');
      }
    },
    {
      file: 'tsconfig.json',
      validator: (content) => {
        try {
          const config = JSON.parse(content);
          return config.compilerOptions && config.include;
        } catch {
          return false;
        }
      }
    },
    {
      file: 'tailwind.config.js',
      validator: (content) => {
        return content.includes('content') && 
               content.includes('./src');
      }
    }
  ];
  
  let allValid = true;
  
  configs.forEach(({ file, validator }) => {
    const filePath = path.join(PROJECT_ROOT, file);
    
    if (!fs.existsSync(filePath)) {
      log.error(`Configuration file missing: ${file}`);
      allValid = false;
      return;
    }
    
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      if (validator(content)) {
        log.success(`Configuration valid: ${file}`);
      } else {
        log.warn(`Configuration may be invalid: ${file}`);
      }
    } catch (error) {
      log.error(`Failed to validate ${file}: ${error.message}`);
      allValid = false;
    }
  });
  
  return allValid;
}

/**
 * Build System Check
 */
function checkBuildSystem() {
  log.subtitle('Build System');
  
  const commands = [
    {
      name: 'TypeScript Check',
      command: 'npx tsc --noEmit --skipLibCheck',
      critical: true
    },
    {
      name: 'Vite Build Test',
      command: 'npm run build',
      critical: true,
      timeout: 60000 // 1 minute
    }
  ];
  
  let allPass = true;
  
  commands.forEach(({ name, command, critical, timeout = 30000 }) => {
    try {
      log.info(`Running: ${name}...`);
      execSync(command, { 
        cwd: PROJECT_ROOT, 
        stdio: 'pipe',
        timeout 
      });
      log.success(`${name} passed`);
    } catch (error) {
      const message = `${name} failed`;
      if (critical) {
        log.error(message);
        allPass = false;
      } else {
        log.warn(message);
      }
    }
  });
  
  return allPass;
}

/**
 * Security Check
 */
async function checkSecurity() {
  log.subtitle('Security');
  
  const checks = [
    {
      name: 'NPM Audit',
      check: () => {
        try {
          execSync('npm audit --audit-level=high', { 
            cwd: PROJECT_ROOT,
            stdio: 'pipe' 
          });
          log.success('No high-severity vulnerabilities found');
          return true;
        } catch (error) {
          log.warn('Security vulnerabilities detected. Run: npm audit fix');
          return false;
        }
      }
    },
    {
      name: 'Sensitive Files',
      check: () => {
        const sensitivePatterns = [
          '.env',
          '.env.local',
          '.env.production',
          'secrets.json',
          'private.key'
        ];
        
        let foundSensitive = false;
        sensitivePatterns.forEach(pattern => {
          const filePath = path.join(PROJECT_ROOT, pattern);
          if (fs.existsSync(filePath)) {
            log.warn(`Sensitive file found: ${pattern}`);
            foundSensitive = true;
          }
        });
        
        if (!foundSensitive) {
          log.success('No sensitive files found in project root');
        }
        
        return true; // Not critical
      }
    },
    {
      name: 'Git Status',
      check: () => {
        try {
          const status = execSync('git status --porcelain', { 
            cwd: PROJECT_ROOT,
            encoding: 'utf8' 
          });
          
          if (status.trim()) {
            log.info('Git working directory has changes');
          } else {
            log.success('Git working directory is clean');
          }
          return true;
        } catch (error) {
          log.warn('Not a git repository or git not available');
          return true;
        }
      }
    }
  ];
  
  let allPass = true;
  for (const { name, check } of checks) {
    try {
      if (!await check()) {
        allPass = false;
      }
    } catch (error) {
      log.error(`${name} check failed: ${error.message}`);
      allPass = false;
    }
  }
  
  return allPass;
}

/**
 * Performance Check
 */
function checkPerformance() {
  log.subtitle('Performance');
  
  // Check build output size (if exists)
  const distPath = path.join(PROJECT_ROOT, 'dist');
  if (fs.existsSync(distPath)) {
    try {
      const totalSize = calculateDirectorySize(distPath);
      const sizeKB = Math.round(totalSize / 1024);
      
      log.info(`Build size: ${sizeKB}KB`);
      
      if (sizeKB < 500) {
        log.success('Build size is optimal');
      } else if (sizeKB < 1000) {
        log.warn('Build size is acceptable but could be optimized');
      } else {
        log.warn('Build size is large - consider optimization');
      }
    } catch (error) {
      log.warn('Could not calculate build size');
    }
  } else {
    log.info('No build output found (run npm run build first)');
  }
  
  // Memory usage check
  const memUsage = process.memoryUsage();
  const memUsageMB = Math.round(memUsage.heapUsed / 1024 / 1024);
  log.info(`Memory usage: ${memUsageMB}MB`);
  
  return true;
}

/**
 * Network Connectivity Check
 */
async function checkNetworkConnectivity() {
  log.subtitle('Network Connectivity');
  
  const endpoints = [
    { name: 'NPM Registry', url: 'https://registry.npmjs.org/' },
    { name: 'GitHub', url: 'https://api.github.com/' },
    { name: 'Unsplash API', url: 'https://api.unsplash.com/' }
  ];
  
  const results = await Promise.allSettled(
    endpoints.map(async ({ name, url }) => {
      try {
        await fetch(url, { 
          method: 'HEAD', 
          timeout: 5000,
          signal: AbortSignal.timeout(5000)
        });
        log.success(`${name} is reachable`);
        return true;
      } catch (error) {
        log.warn(`${name} is not reachable: ${error.message}`);
        return false;
      }
    })
  );
  
  const successful = results.filter(result => result.status === 'fulfilled' && result.value).length;
  log.info(`Network connectivity: ${successful}/${endpoints.length} endpoints reachable`);
  
  return true; // Non-critical
}

/**
 * Calculate directory size recursively
 */
function calculateDirectorySize(dirPath) {
  let size = 0;
  
  const files = fs.readdirSync(dirPath);
  files.forEach(file => {
    const filePath = path.join(dirPath, file);
    const stats = fs.statSync(filePath);
    
    if (stats.isFile()) {
      size += stats.size;
    } else if (stats.isDirectory()) {
      size += calculateDirectorySize(filePath);
    }
  });
  
  return size;
}

/**
 * Main health check function
 */
async function runHealthCheck() {
  console.log(`${colors.bright}${colors.magenta}🏥 VocabLens Health Check System${colors.reset}\n`);
  console.log(`${colors.cyan}Starting comprehensive system validation...${colors.reset}\n`);
  
  const checks = [
    { name: 'System Information', fn: checkSystemInfo, critical: false },
    { name: 'Project Structure', fn: checkProjectStructure, critical: true },
    { name: 'Dependencies', fn: checkDependencies, critical: true },
    { name: 'Configuration Files', fn: checkConfigFiles, critical: true },
    { name: 'Build System', fn: checkBuildSystem, critical: true },
    { name: 'Security', fn: checkSecurity, critical: false },
    { name: 'Performance', fn: checkPerformance, critical: false },
    { name: 'Network Connectivity', fn: checkNetworkConnectivity, critical: false }
  ];
  
  let passedChecks = 0;
  let failedChecks = 0;
  let criticalFailures = 0;
  
  for (const { name, fn, critical } of checks) {
    log.title(`${name} Check`);
    
    try {
      const result = await fn();
      if (result) {
        passedChecks++;
      } else {
        failedChecks++;
        if (critical) {
          criticalFailures++;
        }
      }
    } catch (error) {
      log.error(`${name} check encountered an error: ${error.message}`);
      failedChecks++;
      if (critical) {
        criticalFailures++;
      }
    }
  }
  
  // Health Summary
  console.log(`\n${colors.bright}${colors.cyan}📊 Health Check Summary${colors.reset}`);
  console.log(`${colors.white}═══════════════════════════════════${colors.reset}`);
  console.log(`   Passed: ${colors.green}${passedChecks}${colors.reset}`);
  console.log(`   Failed: ${colors.red}${failedChecks}${colors.reset}`);
  console.log(`   Critical Failures: ${colors.red}${criticalFailures}${colors.reset}`);
  console.log(`   Total Checks: ${passedChecks + failedChecks}`);
  
  // Overall Status
  if (criticalFailures === 0) {
    console.log(`\n${colors.green}${colors.bright}🎉 System Health: EXCELLENT${colors.reset}`);
    console.log(`${colors.green}✨ All critical systems are operational${colors.reset}`);
    
    if (failedChecks === 0) {
      console.log(`${colors.green}🏆 Perfect health score!${colors.reset}`);
    }
  } else {
    console.log(`\n${colors.red}${colors.bright}🚨 System Health: CRITICAL ISSUES DETECTED${colors.reset}`);
    console.log(`${colors.red}🔧 Please resolve critical issues before proceeding${colors.reset}`);
  }
  
  // Recommendations
  if (failedChecks > 0) {
    console.log(`\n${colors.yellow}💡 Recommendations:${colors.reset}`);
    if (criticalFailures > 0) {
      console.log(`   • Fix critical issues immediately`);
      console.log(`   • Run 'npm install' if dependencies are missing`);
      console.log(`   • Check configuration files for syntax errors`);
    }
    console.log(`   • Run 'npm audit fix' to resolve security issues`);
    console.log(`   • Consider optimizing build size if it's large`);
    console.log(`   • Ensure stable internet connection for external services`);
  }
  
  return criticalFailures === 0;
}

// Global error handler
process.on('uncaughtException', (error) => {
  log.error(`Uncaught exception: ${error.message}`);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  log.error(`Unhandled rejection at: ${promise}, reason: ${reason}`);
  process.exit(1);
});

// Run health check if called directly
if (require.main === module) {
  runHealthCheck()
    .then(success => {
      process.exit(success ? 0 : 1);
    })
    .catch(error => {
      log.error('Health check failed: ' + error.message);
      process.exit(1);
    });
}

module.exports = { runHealthCheck };