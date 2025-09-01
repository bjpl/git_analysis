#!/usr/bin/env node

/**
 * Cloudflare Pages Deployment Script
 * Handles deployment with environment-specific configurations
 */

import { execSync } from 'child_process';
import { existsSync, readFileSync } from 'fs';
import { join } from 'path';

const ENVIRONMENTS = {
  production: 'project-workspace-prod',
  staging: 'project-workspace-staging',
  preview: 'project-workspace-preview'
};

class CloudflareDeployer {
  constructor() {
    this.environment = process.argv[2] || 'preview';
    this.projectName = ENVIRONMENTS[this.environment];
    this.dryRun = process.argv.includes('--dry-run');
  }

  log(message, type = 'info') {
    const colors = {
      info: '\x1b[36m',
      success: '\x1b[32m',
      warning: '\x1b[33m',
      error: '\x1b[31m'
    };
    const reset = '\x1b[0m';
    console.log(`${colors[type]}[${type.toUpperCase()}]${reset} ${message}`);
  }

  async validateEnvironment() {
    this.log('Validating deployment environment...');
    
    if (!this.projectName) {
      throw new Error(`Invalid environment: ${this.environment}. Use: production, staging, or preview`);
    }

    // Check if wrangler is installed
    try {
      execSync('wrangler --version', { stdio: 'pipe' });
      this.log('Wrangler CLI found', 'success');
    } catch (error) {
      throw new Error('Wrangler CLI not found. Install with: npm install -g wrangler');
    }

    // Check if user is authenticated
    try {
      execSync('wrangler whoami', { stdio: 'pipe' });
      this.log('Cloudflare authentication verified', 'success');
    } catch (error) {
      throw new Error('Not authenticated with Cloudflare. Run: wrangler login');
    }
  }

  async buildProject() {
    this.log('Building project for Cloudflare Pages...');
    
    try {
      const buildCommand = this.environment === 'production' 
        ? 'npm run build:prod' 
        : 'npm run build';
      
      if (!this.dryRun) {
        execSync(buildCommand, { stdio: 'inherit' });
      }
      this.log('Project built successfully', 'success');
    } catch (error) {
      throw new Error(`Build failed: ${error.message}`);
    }
  }

  async deployToPages() {
    this.log(`Deploying to Cloudflare Pages (${this.environment})...`);
    
    try {
      const deployCommand = [
        'wrangler pages deploy build',
        `--project-name=${this.projectName}`,
        `--compatibility-date=2024-08-29`,
        this.environment === 'production' ? '--env=production' : `--env=${this.environment}`
      ].join(' ');

      if (!this.dryRun) {
        execSync(deployCommand, { stdio: 'inherit' });
      } else {
        this.log(`Would run: ${deployCommand}`, 'warning');
      }
      
      this.log('Deployment completed successfully', 'success');
    } catch (error) {
      throw new Error(`Deployment failed: ${error.message}`);
    }
  }

  async setEnvironmentVariables() {
    this.log('Setting up environment variables...');
    
    const envFile = join(process.cwd(), '.env');
    if (!existsSync(envFile)) {
      this.log('No .env file found, skipping environment variables', 'warning');
      return;
    }

    try {
      const envContent = readFileSync(envFile, 'utf-8');
      const envVars = envContent
        .split('\n')
        .filter(line => line && !line.startsWith('#'))
        .map(line => {
          const [key, ...valueParts] = line.split('=');
          return { key: key.trim(), value: valueParts.join('=').trim() };
        });

      for (const { key, value } of envVars) {
        if (!this.dryRun) {
          try {
            execSync(`wrangler pages secret put ${key} --env=${this.environment}`, {
              input: value,
              stdio: 'pipe'
            });
            this.log(`Set environment variable: ${key}`, 'success');
          } catch (error) {
            this.log(`Failed to set ${key}: ${error.message}`, 'warning');
          }
        } else {
          this.log(`Would set: ${key}`, 'warning');
        }
      }
    } catch (error) {
      this.log(`Failed to process environment variables: ${error.message}`, 'warning');
    }
  }

  async validateDeployment() {
    this.log('Validating deployment...');
    
    try {
      const listCommand = `wrangler pages project list`;
      const result = execSync(listCommand, { encoding: 'utf-8' });
      
      if (result.includes(this.projectName)) {
        this.log('Deployment validation successful', 'success');
        this.log(`Project URL: https://${this.projectName}.pages.dev`, 'info');
      } else {
        this.log('Deployment validation failed', 'warning');
      }
    } catch (error) {
      this.log(`Validation failed: ${error.message}`, 'warning');
    }
  }

  async deploy() {
    try {
      await this.validateEnvironment();
      await this.buildProject();
      await this.setEnvironmentVariables();
      await this.deployToPages();
      await this.validateDeployment();
      
      this.log(`\n🚀 Deployment completed successfully!`, 'success');
      this.log(`Environment: ${this.environment}`, 'info');
      this.log(`Project: ${this.projectName}`, 'info');
      this.log(`URL: https://${this.projectName}.pages.dev`, 'info');
      
    } catch (error) {
      this.log(`\n❌ Deployment failed: ${error.message}`, 'error');
      process.exit(1);
    }
  }
}

// Main execution
if (import.meta.url === `file://${process.argv[1]}`) {
  const deployer = new CloudflareDeployer();
  deployer.deploy();
}

export default CloudflareDeployer;