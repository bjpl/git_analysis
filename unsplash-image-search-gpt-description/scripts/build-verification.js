#!/usr/bin/env node

/**
 * Build Verification Script for VocabLens PWA
 * 
 * This script performs comprehensive verification that the project can build
 * without submodules and is ready for Netlify deployment.
 */

import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class BuildVerifier {
  constructor() {
    this.projectRoot = process.cwd();
    this.errors = [];
    this.warnings = [];
    this.passed = [];
  }

  log(message, type = 'info') {
    const timestamp = new Date().toISOString();
    const prefix = {
      error: '❌ ERROR',
      warning: '⚠️  WARN',
      success: '✅ PASS',
      info: 'ℹ️  INFO'
    }[type];
    console.log(`${prefix} [${timestamp}] ${message}`);
  }

  addResult(message, type) {
    const result = { message, timestamp: new Date().toISOString() };
    
    switch (type) {
      case 'error':
        this.errors.push(result);
        this.log(message, 'error');
        break;
      case 'warning':
        this.warnings.push(result);
        this.log(message, 'warning');
        break;
      case 'success':
        this.passed.push(result);
        this.log(message, 'success');
        break;
    }
  }

  async checkPackageJson() {
    this.log('Checking package.json configuration...', 'info');
    
    try {
      const packagePath = path.join(this.projectRoot, 'package.json');
      const packageContent = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
      
      // Check build script exists
      if (packageContent.scripts && packageContent.scripts.build) {
        this.addResult('Build script found in package.json', 'success');
      } else {
        this.addResult('No build script found in package.json', 'error');
      }
      
      // Check essential dependencies
      const essentialDeps = ['react', 'react-dom', 'vite'];
      const missingDeps = essentialDeps.filter(dep => 
        !packageContent.dependencies?.[dep] && !packageContent.devDependencies?.[dep]
      );
      
      if (missingDeps.length === 0) {
        this.addResult('All essential dependencies are present', 'success');
      } else {
        this.addResult(`Missing essential dependencies: ${missingDeps.join(', ')}`, 'error');
      }
      
      return true;
    } catch (error) {
      this.addResult(`Failed to read or parse package.json: ${error.message}`, 'error');
      return false;
    }
  }

  async checkSubmoduleReferences() {
    this.log('Checking for submodule references...', 'info');
    
    try {
      // Check .gitmodules file
      const gitmodulesPath = path.join(this.projectRoot, '.gitmodules');
      if (fs.existsSync(gitmodulesPath)) {
        const content = fs.readFileSync(gitmodulesPath, 'utf8').trim();
        if (content.length > 0) {
          this.addResult('.gitmodules file contains submodule references', 'warning');
        } else {
          this.addResult('.gitmodules file is empty', 'success');
        }
      } else {
        this.addResult('No .gitmodules file found', 'success');
      }
      
      // Check git status for submodule references
      try {
        const gitStatus = execSync('git status --porcelain', { 
          cwd: this.projectRoot, 
          encoding: 'utf8' 
        });
        
        const submoduleLines = gitStatus.split('\n')
          .filter(line => line.includes('../') && (line.includes('D ') || line.includes('M ')));
        
        if (submoduleLines.length > 0) {
          this.addResult(`Found ${submoduleLines.length} submodule references in git status`, 'warning');
        } else {
          this.addResult('No submodule references in git status', 'success');
        }
      } catch (error) {
        this.addResult(`Could not check git status: ${error.message}`, 'warning');
      }
      
      return true;
    } catch (error) {
      this.addResult(`Error checking submodule references: ${error.message}`, 'error');
      return false;
    }
  }

  async checkImportStatements() {
    this.log('Checking for problematic import statements...', 'info');
    
    const checkDirectory = (dir) => {
      const files = fs.readdirSync(dir, { withFileTypes: true });
      let problemImports = [];
      
      for (const file of files) {
        const fullPath = path.join(dir, file.name);
        
        if (file.isDirectory() && !['node_modules', 'dist', 'build', '.git'].includes(file.name)) {
          problemImports.push(...checkDirectory(fullPath));
        } else if (file.isFile() && /\.(ts|tsx|js|jsx)$/.test(file.name)) {
          try {
            const content = fs.readFileSync(fullPath, 'utf8');
            const lines = content.split('\n');
            
            lines.forEach((line, index) => {
              // Check for parent directory imports that might reference submodules
              if (/import.*['"`]\.\.\/\.\.\//.test(line)) {
                problemImports.push({
                  file: path.relative(this.projectRoot, fullPath),
                  line: index + 1,
                  content: line.trim()
                });
              }
            });
          } catch (error) {
            // Skip files that can't be read
          }
        }
      }
      
      return problemImports;
    };
    
    try {
      const srcPath = path.join(this.projectRoot, 'src');
      if (fs.existsSync(srcPath)) {
        const problemImports = checkDirectory(srcPath);
        
        if (problemImports.length === 0) {
          this.addResult('No problematic parent directory imports found', 'success');
        } else {
          problemImports.forEach(issue => {
            this.addResult(`Potential issue in ${issue.file}:${issue.line} - ${issue.content}`, 'warning');
          });
        }
      } else {
        this.addResult('No src directory found', 'warning');
      }
      
      return true;
    } catch (error) {
      this.addResult(`Error checking import statements: ${error.message}`, 'error');
      return false;
    }
  }

  async testNpmInstall() {
    this.log('Testing npm install...', 'info');
    
    try {
      // Test npm install in a clean environment
      execSync('npm install', { 
        cwd: this.projectRoot,
        stdio: 'pipe',
        timeout: 300000 // 5 minutes timeout
      });
      
      this.addResult('npm install completed successfully', 'success');
      return true;
    } catch (error) {
      this.addResult(`npm install failed: ${error.message}`, 'error');
      return false;
    }
  }

  async testBuild() {
    this.log('Testing build process...', 'info');
    
    try {
      // Clean previous build
      const distPath = path.join(this.projectRoot, 'dist');
      if (fs.existsSync(distPath)) {
        fs.rmSync(distPath, { recursive: true, force: true });
      }
      
      // Run build
      const buildOutput = execSync('npm run build', { 
        cwd: this.projectRoot,
        encoding: 'utf8',
        timeout: 300000 // 5 minutes timeout
      });
      
      // Check if dist directory was created
      if (fs.existsSync(distPath)) {
        const distFiles = fs.readdirSync(distPath);
        if (distFiles.length > 0) {
          this.addResult(`Build successful - dist directory contains ${distFiles.length} files/folders`, 'success');
          
          // Check for essential build artifacts
          const hasIndex = distFiles.some(file => file.startsWith('index.'));
          const hasAssets = fs.existsSync(path.join(distPath, 'assets')) || 
                          distFiles.some(file => file.includes('assets'));
          
          if (hasIndex) {
            this.addResult('Index file found in build output', 'success');
          } else {
            this.addResult('No index file found in build output', 'warning');
          }
          
          if (hasAssets) {
            this.addResult('Asset files found in build output', 'success');
          } else {
            this.addResult('No asset files found in build output', 'warning');
          }
          
        } else {
          this.addResult('Build completed but dist directory is empty', 'error');
        }
      } else {
        this.addResult('Build completed but no dist directory was created', 'error');
      }
      
      return true;
    } catch (error) {
      this.addResult(`Build failed: ${error.message}`, 'error');
      return false;
    }
  }

  async checkNetlifyConfig() {
    this.log('Checking Netlify configuration...', 'info');
    
    try {
      const netlifyConfigPath = path.join(this.projectRoot, 'netlify.toml');
      if (fs.existsSync(netlifyConfigPath)) {
        const content = fs.readFileSync(netlifyConfigPath, 'utf8');
        
        // Check for proper build configuration
        if (content.includes('build') && content.includes('publish')) {
          this.addResult('Netlify configuration file found with build settings', 'success');
        } else {
          this.addResult('Netlify configuration exists but may be incomplete', 'warning');
        }
        
        // Check for submodule references in netlify.toml
        if (content.includes('../')) {
          this.addResult('Netlify config contains parent directory references', 'warning');
        }
      } else {
        this.addResult('No netlify.toml configuration found', 'warning');
      }
      
      return true;
    } catch (error) {
      this.addResult(`Error checking Netlify configuration: ${error.message}`, 'error');
      return false;
    }
  }

  async runVerification() {
    console.log('🔍 Starting VocabLens PWA Build Verification\n');
    
    const checks = [
      { name: 'Package.json Check', fn: () => this.checkPackageJson() },
      { name: 'Submodule References Check', fn: () => this.checkSubmoduleReferences() },
      { name: 'Import Statements Check', fn: () => this.checkImportStatements() },
      { name: 'NPM Install Test', fn: () => this.testNpmInstall() },
      { name: 'Build Process Test', fn: () => this.testBuild() },
      { name: 'Netlify Configuration Check', fn: () => this.checkNetlifyConfig() }
    ];
    
    for (const check of checks) {
      console.log(`\n--- ${check.name} ---`);
      try {
        await check.fn();
      } catch (error) {
        this.addResult(`${check.name} threw an exception: ${error.message}`, 'error');
      }
    }
    
    this.generateReport();
  }

  generateReport() {
    console.log('\n' + '='.repeat(60));
    console.log('📊 VERIFICATION REPORT');
    console.log('='.repeat(60));
    
    console.log(`\n✅ Passed: ${this.passed.length}`);
    console.log(`⚠️  Warnings: ${this.warnings.length}`);
    console.log(`❌ Errors: ${this.errors.length}`);
    
    if (this.errors.length > 0) {
      console.log('\n🚨 ERRORS THAT NEED ATTENTION:');
      this.errors.forEach((error, index) => {
        console.log(`${index + 1}. ${error.message}`);
      });
    }
    
    if (this.warnings.length > 0) {
      console.log('\n⚠️  WARNINGS TO REVIEW:');
      this.warnings.forEach((warning, index) => {
        console.log(`${index + 1}. ${warning.message}`);
      });
    }
    
    console.log('\n' + '='.repeat(60));
    
    if (this.errors.length === 0) {
      console.log('🎉 BUILD VERIFICATION SUCCESSFUL!');
      console.log('✅ The project can be built without submodules and is ready for Netlify deployment.');
      process.exit(0);
    } else {
      console.log('❌ BUILD VERIFICATION FAILED!');
      console.log('🔧 Please address the errors above before deploying to Netlify.');
      process.exit(1);
    }
  }
}

// Run verification if this script is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  const verifier = new BuildVerifier();
  verifier.runVerification().catch(error => {
    console.error('❌ Verification script failed:', error);
    process.exit(1);
  });
}

export default BuildVerifier;