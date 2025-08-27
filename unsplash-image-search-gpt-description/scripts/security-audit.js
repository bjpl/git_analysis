#!/usr/bin/env node

/**
 * Security Audit Script for VocabLens Production
 * Validates security configurations and identifies vulnerabilities
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.join(__dirname, '..');

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

class SecurityAuditor {
  constructor() {
    this.vulnerabilities = [];
    this.warnings = [];
    this.passed = [];
  }

  log(level, message, severity = 'medium') {
    const entry = { level, message, severity, timestamp: new Date().toISOString() };
    
    switch (level) {
      case 'VULNERABILITY':
        this.vulnerabilities.push(entry);
        const severityColor = severity === 'high' ? colors.red : severity === 'medium' ? colors.yellow : colors.cyan;
        console.log(`${severityColor}🚨 [${severity.toUpperCase()}] ${message}${colors.reset}`);
        break;
      case 'WARNING':
        this.warnings.push(entry);
        console.log(`${colors.yellow}⚠️  ${message}${colors.reset}`);
        break;
      case 'PASS':
        this.passed.push(entry);
        console.log(`${colors.green}✅ ${message}${colors.reset}`);
        break;
      case 'INFO':
        console.log(`${colors.blue}ℹ️  ${message}${colors.reset}`);
        break;
    }
  }

  async auditHttpHeaders() {
    console.log(`\n${colors.bold}${colors.cyan}🛡️  HTTP Security Headers Audit${colors.reset}`);
    
    const netlifyConfigPath = path.join(rootDir, 'netlify.toml');
    if (!fs.existsSync(netlifyConfigPath)) {
      this.log('VULNERABILITY', 'netlify.toml not found - security headers not configured', 'high');
      return;
    }

    const configContent = fs.readFileSync(netlifyConfigPath, 'utf8');
    
    const criticalHeaders = [
      {
        name: 'X-Frame-Options',
        pattern: /X-Frame-Options\s*=\s*"DENY"/,
        description: 'Prevents clickjacking attacks'
      },
      {
        name: 'X-Content-Type-Options',
        pattern: /X-Content-Type-Options\s*=\s*"nosniff"/,
        description: 'Prevents MIME type sniffing'
      },
      {
        name: 'X-XSS-Protection',
        pattern: /X-XSS-Protection\s*=\s*"1; mode=block"/,
        description: 'Enables XSS filtering'
      },
      {
        name: 'Strict-Transport-Security',
        pattern: /Strict-Transport-Security\s*=.*max-age/,
        description: 'Enforces HTTPS connections'
      }
    ];

    criticalHeaders.forEach(header => {
      if (header.pattern.test(configContent)) {
        this.log('PASS', `${header.name} configured correctly - ${header.description}`);
      } else {
        this.log('VULNERABILITY', `Missing ${header.name} - ${header.description}`, 'high');
      }
    });

    // Check for Content Security Policy
    if (configContent.includes('Content-Security-Policy')) {
      this.log('PASS', 'Content Security Policy configured');
    } else {
      this.log('WARNING', 'Content Security Policy not configured - consider adding for enhanced security');
    }
  }

  async auditBuildSecurity() {
    console.log(`\n${colors.bold}${colors.cyan}🔒 Build Security Audit${colors.reset}`);
    
    const distPath = path.join(rootDir, 'dist');
    if (!fs.existsSync(distPath)) {
      this.log('WARNING', 'Build output not found - run npm run build first');
      return;
    }

    // Check for sensitive files in build output
    const sensitiveFiles = [
      '.env',
      '.env.local',
      '.env.production',
      'package-lock.json',
      'yarn.lock',
      '.git',
      'node_modules'
    ];

    sensitiveFiles.forEach(file => {
      const filePath = path.join(distPath, file);
      if (fs.existsSync(filePath)) {
        this.log('VULNERABILITY', `Sensitive file exposed in build: ${file}`, 'high');
      } else {
        this.log('PASS', `Sensitive file properly excluded: ${file}`);
      }
    });

    // Scan for hardcoded secrets in built files
    this.scanForHardcodedSecrets(distPath);
  }

  scanForHardcodedSecrets(directory, scannedDirs = new Set()) {
    if (scannedDirs.has(directory)) return;
    scannedDirs.add(directory);

    const items = fs.readdirSync(directory);
    
    const secretPatterns = [
      { name: 'OpenAI API Key', pattern: /sk-[a-zA-Z0-9]{32,}/ },
      { name: 'AWS Access Key', pattern: /AKIA[0-9A-Z]{16}/ },
      { name: 'GitHub Token', pattern: /ghp_[a-zA-Z0-9]{36}/ },
      { name: 'Generic API Key', pattern: /api[_-]?key['"]\s*[:=]\s*['"][a-zA-Z0-9]{16,}['"]/ },
      { name: 'Database URL', pattern: /mongodb:|postgres:|mysql:|redis:/ },
      { name: 'Private Key', pattern: /-----BEGIN (?:RSA |DSA |EC )?PRIVATE KEY-----/ }
    ];

    items.forEach(item => {
      const itemPath = path.join(directory, item);
      const stat = fs.statSync(itemPath);

      if (stat.isDirectory() && !item.startsWith('.')) {
        this.scanForHardcodedSecrets(itemPath, scannedDirs);
      } else if (stat.isFile() && (item.endsWith('.js') || item.endsWith('.html') || item.endsWith('.css'))) {
        try {
          const content = fs.readFileSync(itemPath, 'utf8');
          
          secretPatterns.forEach(secret => {
            if (secret.pattern.test(content)) {
              this.log('VULNERABILITY', `${secret.name} found in build file: ${path.relative(rootDir, itemPath)}`, 'high');
            }
          });

          // Check for localhost/development URLs
          if (/localhost:\d+|127\.0\.0\.1:\d+|192\.168\.\d+\.\d+/.test(content)) {
            this.log('WARNING', `Development URL found in build file: ${path.relative(rootDir, itemPath)}`);
          }
        } catch (error) {
          // Skip binary files
        }
      }
    });
  }

  async auditDependencies() {
    console.log(`\n${colors.bold}${colors.cyan}📦 Dependency Security Audit${colors.reset}`);
    
    const packagePath = path.join(rootDir, 'package.json');
    const packageLockPath = path.join(rootDir, 'package-lock.json');
    
    if (!fs.existsSync(packagePath)) {
      this.log('VULNERABILITY', 'package.json not found', 'high');
      return;
    }

    const packageJson = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
    
    // Check for outdated/vulnerable dependencies (basic check)
    const dependencies = { ...packageJson.dependencies, ...packageJson.devDependencies };
    
    // Known vulnerable patterns (simplified check)
    const knownVulnerabilities = [
      { name: 'react', vulnerable: /^16\.[0-9]/, reason: 'React < 17 has known vulnerabilities' },
      { name: 'express', vulnerable: /^4\.[0-9]\.|^3\./, reason: 'Old Express versions have security issues' },
      { name: 'lodash', vulnerable: /^4\.([0-9]|1[0-6])\./, reason: 'Lodash < 4.17.0 has prototype pollution' }
    ];

    Object.entries(dependencies).forEach(([name, version]) => {
      const vulnerability = knownVulnerabilities.find(vuln => vuln.name === name);
      if (vulnerability && vulnerability.vulnerable.test(version)) {
        this.log('VULNERABILITY', `${name}@${version}: ${vulnerability.reason}`, 'medium');
      }
    });

    // Check for development dependencies in production
    if (packageJson.dependencies) {
      const devToolsInProduction = [
        'nodemon', 'webpack-dev-server', 'vite', '@vitejs/plugin-react',
        'eslint', 'prettier', 'vitest', 'playwright'
      ];

      devToolsInProduction.forEach(tool => {
        if (packageJson.dependencies[tool]) {
          this.log('WARNING', `Development tool in production dependencies: ${tool}`);
        }
      });
    }

    this.log('PASS', 'Basic dependency security check completed');
  }

  async auditApiConfiguration() {
    console.log(`\n${colors.bold}${colors.cyan}🔑 API Configuration Security Audit${colors.reset}`);
    
    // Check environment variable security
    const envExamplePath = path.join(rootDir, '.env.example');
    if (fs.existsSync(envExamplePath)) {
      const envContent = fs.readFileSync(envExamplePath, 'utf8');
      
      // Check for actual keys in .env.example
      const actualKeyPatterns = [
        /sk-[a-zA-Z0-9]{20,}/,  // Real OpenAI keys
        /[a-f0-9]{40,}/,        // Real access tokens
        /password\s*=\s*[^"'][\w\d]+/i  // Real passwords
      ];

      let hasRealSecrets = false;
      actualKeyPatterns.forEach(pattern => {
        if (pattern.test(envContent)) {
          this.log('VULNERABILITY', 'Real secrets found in .env.example file', 'high');
          hasRealSecrets = true;
        }
      });

      if (!hasRealSecrets) {
        this.log('PASS', '.env.example contains only placeholder values');
      }
    }

    // Check for .env files that shouldn't be committed
    const envFiles = ['.env', '.env.local', '.env.production'];
    envFiles.forEach(file => {
      const filePath = path.join(rootDir, file);
      if (fs.existsSync(filePath)) {
        this.log('WARNING', `Environment file exists: ${file} - ensure it's not committed to git`);
      }
    });

    // Check API key validation in source
    const apiServicePath = path.join(rootDir, 'src', 'services', 'apiConfigService.ts');
    if (fs.existsSync(apiServicePath)) {
      const serviceContent = fs.readFileSync(apiServicePath, 'utf8');
      
      if (serviceContent.includes('validateApiKey')) {
        this.log('PASS', 'API key validation implemented');
      } else {
        this.log('WARNING', 'API key validation not found');
      }

      if (serviceContent.includes('encrypt') || serviceContent.includes('crypto')) {
        this.log('PASS', 'API key encryption implemented');
      } else {
        this.log('WARNING', 'API key encryption not found');
      }
    }
  }

  async auditNetworkSecurity() {
    console.log(`\n${colors.bold}${colors.cyan}🌐 Network Security Audit${colors.reset}`);
    
    const indexPath = path.join(rootDir, 'dist', 'index.html');
    if (fs.existsSync(indexPath)) {
      const htmlContent = fs.readFileSync(indexPath, 'utf8');
      
      // Check for mixed content issues
      if (/src="http:\/\/|href="http:\/\//.test(htmlContent)) {
        this.log('VULNERABILITY', 'Mixed content detected - HTTP resources on HTTPS page', 'medium');
      } else {
        this.log('PASS', 'No mixed content issues detected');
      }

      // Check for preconnect to external domains
      const preconnectDomains = htmlContent.match(/rel="preconnect"[^>]+href="([^"]+)"/g);
      if (preconnectDomains) {
        preconnectDomains.forEach(domain => {
          if (domain.includes('https://')) {
            this.log('PASS', `Secure preconnect: ${domain}`);
          } else {
            this.log('WARNING', `Insecure preconnect: ${domain}`);
          }
        });
      }

      // Check for inline scripts/styles (CSP concern)
      if (/<script(?![^>]*src=)[^>]*>/.test(htmlContent)) {
        this.log('WARNING', 'Inline scripts detected - may conflict with strict CSP');
      }

      if (/<style[^>]*>/.test(htmlContent)) {
        this.log('WARNING', 'Inline styles detected - may conflict with strict CSP');
      }
    }
  }

  async auditDataPrivacy() {
    console.log(`\n${colors.bold}${colors.cyan}🔐 Data Privacy Audit${colors.reset}`);
    
    // Check for tracking/analytics
    const indexPath = path.join(rootDir, 'dist', 'index.html');
    if (fs.existsSync(indexPath)) {
      const htmlContent = fs.readFileSync(indexPath, 'utf8');
      
      const trackingPatterns = [
        { name: 'Google Analytics', pattern: /google-analytics\.com|gtag|ga\(/ },
        { name: 'Facebook Pixel', pattern: /facebook\.net\/tr|fbq\(/ },
        { name: 'Google Tag Manager', pattern: /googletagmanager\.com/ }
      ];

      trackingPatterns.forEach(tracker => {
        if (tracker.pattern.test(htmlContent)) {
          this.log('INFO', `${tracker.name} detected - ensure GDPR compliance`);
        }
      });
    }

    // Check for data collection in services
    const servicesPath = path.join(rootDir, 'src', 'services');
    if (fs.existsSync(servicesPath)) {
      const serviceFiles = fs.readdirSync(servicesPath).filter(f => f.endsWith('.ts'));
      
      serviceFiles.forEach(file => {
        const content = fs.readFileSync(path.join(servicesPath, file), 'utf8');
        
        if (/localStorage|sessionStorage/.test(content)) {
          this.log('INFO', `Local storage usage in ${file} - ensure data privacy compliance`);
        }

        if (/fetch|XMLHttpRequest|axios/.test(content)) {
          this.log('INFO', `Network requests in ${file} - verify data handling policies`);
        }
      });
    }

    this.log('PASS', 'Data privacy audit completed');
  }

  generateSecurityReport() {
    console.log(`\n${colors.bold}${colors.magenta}🛡️  Security Audit Report${colors.reset}`);
    console.log('='.repeat(60));

    const highVulns = this.vulnerabilities.filter(v => v.severity === 'high').length;
    const mediumVulns = this.vulnerabilities.filter(v => v.severity === 'medium').length;
    const lowVulns = this.vulnerabilities.filter(v => v.severity === 'low').length;
    const totalVulns = this.vulnerabilities.length;
    const warnings = this.warnings.length;
    const passed = this.passed.length;

    console.log(`\n${colors.bold}Security Summary:${colors.reset}`);
    console.log(`  ${colors.green}✅ Security Checks Passed: ${passed}${colors.reset}`);
    console.log(`  ${colors.yellow}⚠️  Warnings: ${warnings}${colors.reset}`);
    console.log(`  ${colors.red}🚨 Total Vulnerabilities: ${totalVulns}${colors.reset}`);
    
    if (totalVulns > 0) {
      console.log(`    ${colors.red}  • High Severity: ${highVulns}${colors.reset}`);
      console.log(`    ${colors.yellow}  • Medium Severity: ${mediumVulns}${colors.reset}`);
      console.log(`    ${colors.cyan}  • Low Severity: ${lowVulns}${colors.reset}`);
    }

    if (highVulns > 0) {
      console.log(`\n${colors.bold}${colors.red}🚨 CRITICAL VULNERABILITIES:${colors.reset}`);
      this.vulnerabilities.filter(v => v.severity === 'high').forEach((vuln, i) => {
        console.log(`  ${i + 1}. ${vuln.message}`);
      });
    }

    if (mediumVulns > 0) {
      console.log(`\n${colors.bold}${colors.yellow}⚠️  MEDIUM VULNERABILITIES:${colors.reset}`);
      this.vulnerabilities.filter(v => v.severity === 'medium').forEach((vuln, i) => {
        console.log(`  ${i + 1}. ${vuln.message}`);
      });
    }

    if (warnings > 0) {
      console.log(`\n${colors.bold}${colors.yellow}💡 RECOMMENDATIONS:${colors.reset}`);
      this.warnings.forEach((warning, i) => {
        console.log(`  ${i + 1}. ${warning.message}`);
      });
    }

    // Security score calculation
    const maxScore = 100;
    const securityScore = Math.max(0, maxScore - (highVulns * 25) - (mediumVulns * 10) - (lowVulns * 5) - (warnings * 2));
    
    console.log(`\n${colors.bold}Security Score: ${securityScore}/100${colors.reset}`);
    
    if (securityScore >= 90) {
      console.log(`${colors.green}🛡️  Excellent security posture${colors.reset}`);
    } else if (securityScore >= 75) {
      console.log(`${colors.yellow}⚠️  Good security, minor improvements needed${colors.reset}`);
    } else if (securityScore >= 50) {
      console.log(`${colors.yellow}🔶 Moderate security risks - address vulnerabilities${colors.reset}`);
    } else {
      console.log(`${colors.red}🚨 High security risk - immediate action required${colors.reset}`);
    }

    console.log(`\n${colors.bold}Audit completed at: ${new Date().toISOString()}${colors.reset}`);
    
    return highVulns === 0 ? 0 : 1; // Exit code
  }

  async runFullAudit() {
    console.log(`${colors.bold}${colors.cyan}`);
    console.log('🔍 VocabLens Security Audit');
    console.log('===========================');
    console.log(colors.reset);

    await this.auditHttpHeaders();
    await this.auditBuildSecurity();
    await this.auditDependencies();
    await this.auditApiConfiguration();
    await this.auditNetworkSecurity();
    await this.auditDataPrivacy();

    return this.generateSecurityReport();
  }
}

// Run security audit
const auditor = new SecurityAuditor();
auditor.runFullAudit().then(exitCode => {
  process.exit(exitCode);
}).catch(error => {
  console.error(`${colors.red}Security audit failed:${colors.reset}`, error);
  process.exit(1);
});