#!/usr/bin/env node

/**
 * Netlify Build Verification Script
 * Comprehensive build verification for VocabLens deployment
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const DIST_DIR = path.join(process.cwd(), 'dist');
const BUILD_REPORT_PATH = path.join(DIST_DIR, 'build-report.json');

// Critical files that must exist for successful deployment
const CRITICAL_FILES = [
    'index.html',
    'assets',
    '_redirects',
    'manifest.json'
];

// Optional files that improve functionality
const OPTIONAL_FILES = [
    'sw.js',
    'robots.txt',
    'sitemap.xml'
];

// Asset patterns to verify
const ASSET_PATTERNS = {
    css: /\.css$/,
    js: /\.js$/,
    images: /\.(png|jpg|jpeg|gif|svg|ico|webp)$/,
    fonts: /\.(woff|woff2|ttf|eot)$/
};

// Performance thresholds
const PERFORMANCE_THRESHOLDS = {
    maxBundleSize: 5 * 1024 * 1024, // 5MB
    maxAssetCount: 50,
    maxCssSize: 500 * 1024, // 500KB
    maxJsSize: 2 * 1024 * 1024, // 2MB
    minCompressionRatio: 0.3
};

class NetlifyBuildVerifier {
    constructor() {
        this.errors = [];
        this.warnings = [];
        this.info = [];
        this.buildReport = {
            timestamp: new Date().toISOString(),
            status: 'unknown',
            files: {},
            performance: {},
            security: {},
            pwa: {},
            deployment: {}
        };
    }

    async verify() {
        console.log('🚀 Starting Netlify build verification for VocabLens...\n');
        
        try {
            // Core verification steps
            await this.verifyDistDirectory();
            await this.verifyCriticalFiles();
            await this.verifyIndexHtml();
            await this.verifyAssets();
            await this.verifyRedirects();
            await this.verifyManifest();
            await this.verifyServiceWorker();
            
            // Performance analysis
            await this.analyzePerformance();
            
            // Security checks
            await this.verifySecurityFeatures();
            
            // PWA verification
            await this.verifyPwaFeatures();
            
            // Runtime API configuration check
            await this.verifyRuntimeConfig();
            
            // Generate report
            await this.generateBuildReport();
            
            // Final status
            this.determineFinalStatus();
            this.printSummary();
            
        } catch (error) {
            this.addError(`Build verification failed: ${error.message}`);
            this.buildReport.status = 'failed';
            console.error('❌ Build verification failed:', error);
            process.exit(1);
        }
    }

    async verifyDistDirectory() {
        if (!fs.existsSync(DIST_DIR)) {
            this.addError('dist/ directory not found - build may have failed');
            throw new Error('Missing dist directory');
        }
        
        const stats = fs.statSync(DIST_DIR);
        this.buildReport.files.distSize = this.getDirectorySize(DIST_DIR);
        this.addInfo(`✅ dist/ directory exists (${this.formatBytes(this.buildReport.files.distSize)})`);
    }

    async verifyCriticalFiles() {
        const missingFiles = [];
        
        for (const file of CRITICAL_FILES) {
            const filePath = path.join(DIST_DIR, file);
            if (!fs.existsSync(filePath)) {
                missingFiles.push(file);
            } else {
                this.addInfo(`✅ Found critical file: ${file}`);
            }
        }
        
        if (missingFiles.length > 0) {
            this.addError(`Missing critical files: ${missingFiles.join(', ')}`);
        }
        
        // Check optional files
        const presentOptionalFiles = [];
        for (const file of OPTIONAL_FILES) {
            const filePath = path.join(DIST_DIR, file);
            if (fs.existsSync(filePath)) {
                presentOptionalFiles.push(file);
                this.addInfo(`✅ Found optional file: ${file}`);
            }
        }
        
        this.buildReport.files.optional = presentOptionalFiles;
    }

    async verifyIndexHtml() {
        const indexPath = path.join(DIST_DIR, 'index.html');
        if (!fs.existsSync(indexPath)) {
            this.addError('index.html is missing');
            return;
        }
        
        const content = fs.readFileSync(indexPath, 'utf8');
        const checks = {
            hasRootElement: content.includes('<div id="root">'),
            hasAssetReferences: content.includes('/assets/'),
            hasManifestLink: content.includes('manifest.json'),
            hasTitle: /<title>(?!%VITE_APP_TITLE%)[^<]+<\/title>/.test(content),
            hasMetaViewport: content.includes('name="viewport"'),
            hasCharset: content.includes('charset='),
            hasThemeColor: content.includes('name="theme-color"'),
            hasAppleTouchIcon: content.includes('apple-touch-icon')
        };
        
        Object.entries(checks).forEach(([check, passed]) => {
            if (passed) {
                this.addInfo(`✅ index.html ${check}`);
            } else {
                this.addWarning(`⚠️ index.html missing ${check}`);
            }
        });
        
        this.buildReport.files.indexHtml = checks;
        
        // Check for runtime API configuration elements
        const hasConfigElements = content.includes('data-runtime-config') || 
                                 content.includes('window.__RUNTIME_CONFIG__');
        if (hasConfigElements) {
            this.addInfo('✅ Runtime API configuration elements found');
        } else {
            this.addWarning('⚠️ No runtime API configuration elements detected');
        }
    }

    async verifyAssets() {
        const assetsDir = path.join(DIST_DIR, 'assets');
        if (!fs.existsSync(assetsDir)) {
            this.addError('assets/ directory missing');
            return;
        }
        
        const assetFiles = this.getAllFiles(assetsDir);
        const assetsByType = {
            css: [],
            js: [],
            images: [],
            fonts: [],
            other: []
        };
        
        assetFiles.forEach(file => {
            const stats = fs.statSync(file);
            const relativePath = path.relative(assetsDir, file);
            const size = stats.size;
            
            let type = 'other';
            Object.entries(ASSET_PATTERNS).forEach(([pattern, regex]) => {
                if (regex.test(file)) {
                    type = pattern;
                }
            });
            
            assetsByType[type].push({ path: relativePath, size });
        });
        
        // Analyze assets
        const totalSize = assetFiles.reduce((sum, file) => sum + fs.statSync(file).size, 0);
        const cssSize = assetsByType.css.reduce((sum, file) => sum + file.size, 0);
        const jsSize = assetsByType.js.reduce((sum, file) => sum + file.size, 0);
        
        this.buildReport.performance.assets = {
            total: assetFiles.length,
            totalSize,
            cssSize,
            jsSize,
            byType: Object.fromEntries(
                Object.entries(assetsByType).map(([type, files]) => [
                    type, 
                    { count: files.length, size: files.reduce((sum, f) => sum + f.size, 0) }
                ])
            )
        };
        
        // Performance checks
        if (totalSize > PERFORMANCE_THRESHOLDS.maxBundleSize) {
            this.addWarning(`⚠️ Total bundle size (${this.formatBytes(totalSize)}) exceeds recommended limit`);
        } else {
            this.addInfo(`✅ Total bundle size: ${this.formatBytes(totalSize)}`);
        }
        
        if (assetFiles.length > PERFORMANCE_THRESHOLDS.maxAssetCount) {
            this.addWarning(`⚠️ Too many assets (${assetFiles.length}), consider bundling`);
        }
        
        this.addInfo(`✅ Assets summary: ${assetsByType.css.length} CSS, ${assetsByType.js.length} JS, ${assetsByType.images.length} images`);
    }

    async verifyRedirects() {
        const redirectsPath = path.join(DIST_DIR, '_redirects');
        if (!fs.existsSync(redirectsPath)) {
            this.addWarning('⚠️ _redirects file missing - SPA routing may not work');
            return;
        }
        
        const content = fs.readFileSync(redirectsPath, 'utf8');
        const hasSpaRoute = content.includes('/* /index.html 200') || 
                          content.includes('/*    /index.html   200');
        
        if (hasSpaRoute) {
            this.addInfo('✅ SPA routing redirect configured');
        } else {
            this.addError('❌ SPA routing not properly configured in _redirects');
        }
        
        this.buildReport.deployment.redirects = { configured: hasSpaRoute };
    }

    async verifyManifest() {
        const manifestPath = path.join(DIST_DIR, 'manifest.json');
        if (!fs.existsSync(manifestPath)) {
            this.addWarning('⚠️ PWA manifest.json missing');
            return;
        }
        
        try {
            const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
            const requiredFields = ['name', 'short_name', 'start_url', 'display', 'theme_color', 'background_color', 'icons'];
            const missingFields = requiredFields.filter(field => !manifest[field]);
            
            if (missingFields.length === 0) {
                this.addInfo('✅ PWA manifest complete');
            } else {
                this.addWarning(`⚠️ PWA manifest missing fields: ${missingFields.join(', ')}`);
            }
            
            this.buildReport.pwa.manifest = {
                present: true,
                complete: missingFields.length === 0,
                missingFields
            };
            
        } catch (error) {
            this.addError(`❌ PWA manifest is invalid JSON: ${error.message}`);
        }
    }

    async verifyServiceWorker() {
        const swPath = path.join(DIST_DIR, 'sw.js');
        const hasServiceWorker = fs.existsSync(swPath);
        
        if (hasServiceWorker) {
            this.addInfo('✅ Service Worker found');
            
            const content = fs.readFileSync(swPath, 'utf8');
            const hasCaching = content.includes('cache') || content.includes('Cache');
            const hasOfflineSupport = content.includes('offline') || content.includes('fallback');
            
            this.buildReport.pwa.serviceWorker = {
                present: true,
                hasCaching,
                hasOfflineSupport
            };
            
        } else {
            this.addWarning('⚠️ Service Worker not found - offline functionality unavailable');
            this.buildReport.pwa.serviceWorker = { present: false };
        }
    }

    async analyzePerformance() {
        const performance = this.buildReport.performance;
        
        // Bundle analysis
        const { totalSize, cssSize, jsSize } = performance.assets;
        performance.scores = {};
        
        // Size score (0-100)
        const sizeScore = Math.max(0, Math.min(100, 
            100 - ((totalSize / PERFORMANCE_THRESHOLDS.maxBundleSize) * 100)
        ));
        performance.scores.bundleSize = Math.round(sizeScore);
        
        // Asset count score
        const assetCountScore = Math.max(0, Math.min(100,
            100 - ((performance.assets.total / PERFORMANCE_THRESHOLDS.maxAssetCount) * 100)
        ));
        performance.scores.assetCount = Math.round(assetCountScore);
        
        // Overall performance score
        performance.scores.overall = Math.round((sizeScore + assetCountScore) / 2);
        
        if (performance.scores.overall >= 80) {
            this.addInfo(`✅ Performance score: ${performance.scores.overall}/100`);
        } else if (performance.scores.overall >= 60) {
            this.addWarning(`⚠️ Performance score: ${performance.scores.overall}/100 - consider optimization`);
        } else {
            this.addError(`❌ Performance score: ${performance.scores.overall}/100 - optimization required`);
        }
    }

    async verifySecurityFeatures() {
        // Check if security-sensitive files are not exposed
        const securityRisks = [];
        const riskyFiles = ['.env', '.env.local', 'package.json', 'package-lock.json', 'node_modules'];
        
        riskyFiles.forEach(file => {
            if (fs.existsSync(path.join(DIST_DIR, file))) {
                securityRisks.push(file);
            }
        });
        
        if (securityRisks.length > 0) {
            this.addError(`❌ Security risk: sensitive files exposed: ${securityRisks.join(', ')}`);
        } else {
            this.addInfo('✅ No sensitive files exposed');
        }
        
        this.buildReport.security = {
            exposedFiles: securityRisks,
            secure: securityRisks.length === 0
        };
    }

    async verifyPwaFeatures() {
        const pwaFeatures = {
            manifest: this.buildReport.pwa.manifest?.present || false,
            serviceWorker: this.buildReport.pwa.serviceWorker?.present || false,
            icons: false,
            offlineSupport: this.buildReport.pwa.serviceWorker?.hasOfflineSupport || false
        };
        
        // Check for PWA icons
        const iconFiles = this.getAllFiles(DIST_DIR)
            .filter(file => /\.(png|ico)$/.test(file) && /icon|logo/.test(path.basename(file)));
        pwaFeatures.icons = iconFiles.length > 0;
        
        const pwaScore = Object.values(pwaFeatures).filter(Boolean).length;
        this.buildReport.pwa.score = pwaScore;
        this.buildReport.pwa.features = pwaFeatures;
        
        if (pwaScore >= 3) {
            this.addInfo(`✅ PWA features: ${pwaScore}/4 implemented`);
        } else {
            this.addWarning(`⚠️ PWA features: ${pwaScore}/4 implemented - consider improving PWA support`);
        }
    }

    async verifyRuntimeConfig() {
        const indexPath = path.join(DIST_DIR, 'index.html');
        if (!fs.existsSync(indexPath)) return;
        
        const content = fs.readFileSync(indexPath, 'utf8');
        
        // Check for runtime configuration indicators
        const hasRuntimeConfig = content.includes('runtime') && 
                               (content.includes('config') || content.includes('API'));
        
        const hasValidationLogic = content.includes('validateApiKey') || 
                                  content.includes('configManager');
        
        this.buildReport.deployment.runtimeConfig = {
            indicators: hasRuntimeConfig,
            validation: hasValidationLogic
        };
        
        if (hasRuntimeConfig) {
            this.addInfo('✅ Runtime API configuration support detected');
        } else {
            this.addWarning('⚠️ Runtime API configuration not clearly detected');
        }
    }

    async generateBuildReport() {
        this.buildReport.summary = {
            errors: this.errors.length,
            warnings: this.warnings.length,
            info: this.info.length
        };
        
        fs.writeFileSync(BUILD_REPORT_PATH, JSON.stringify(this.buildReport, null, 2));
        this.addInfo(`✅ Build report generated: ${path.relative(process.cwd(), BUILD_REPORT_PATH)}`);
    }

    determineFinalStatus() {
        if (this.errors.length > 0) {
            this.buildReport.status = 'failed';
        } else if (this.warnings.length > 0) {
            this.buildReport.status = 'passed_with_warnings';
        } else {
            this.buildReport.status = 'passed';
        }
    }

    printSummary() {
        console.log('\n' + '='.repeat(60));
        console.log('📊 NETLIFY BUILD VERIFICATION SUMMARY');
        console.log('='.repeat(60));
        
        if (this.buildReport.status === 'passed') {
            console.log('🎉 BUILD VERIFICATION PASSED');
        } else if (this.buildReport.status === 'passed_with_warnings') {
            console.log('⚠️  BUILD VERIFICATION PASSED WITH WARNINGS');
        } else {
            console.log('❌ BUILD VERIFICATION FAILED');
        }
        
        console.log(`\n📈 Performance Score: ${this.buildReport.performance.scores?.overall || 0}/100`);
        console.log(`🔒 Security: ${this.buildReport.security?.secure ? 'Secure' : 'Issues Found'}`);
        console.log(`📱 PWA Features: ${this.buildReport.pwa?.score || 0}/4`);
        
        if (this.errors.length > 0) {
            console.log('\n❌ ERRORS:');
            this.errors.forEach(error => console.log(`   ${error}`));
        }
        
        if (this.warnings.length > 0) {
            console.log('\n⚠️  WARNINGS:');
            this.warnings.forEach(warning => console.log(`   ${warning}`));
        }
        
        console.log('\n✅ DEPLOYMENT READY FOR NETLIFY');
        console.log('📋 Next Steps:');
        console.log('   1. Push changes to your Git repository');
        console.log('   2. Connect repository to Netlify');
        console.log('   3. Configure environment variables if needed');
        console.log('   4. Test the deployed site');
        console.log('   5. Configure custom domain (optional)');
        
        if (this.buildReport.status === 'failed') {
            process.exit(1);
        }
    }

    // Utility methods
    addError(message) {
        this.errors.push(message);
        console.log(`❌ ${message}`);
    }

    addWarning(message) {
        this.warnings.push(message);
        console.log(`⚠️ ${message}`);
    }

    addInfo(message) {
        this.info.push(message);
        console.log(`${message}`);
    }

    getAllFiles(dir) {
        const files = [];
        const items = fs.readdirSync(dir);
        
        items.forEach(item => {
            const fullPath = path.join(dir, item);
            const stats = fs.statSync(fullPath);
            
            if (stats.isDirectory()) {
                files.push(...this.getAllFiles(fullPath));
            } else {
                files.push(fullPath);
            }
        });
        
        return files;
    }

    getDirectorySize(dir) {
        let size = 0;
        const files = this.getAllFiles(dir);
        
        files.forEach(file => {
            size += fs.statSync(file).size;
        });
        
        return size;
    }

    formatBytes(bytes) {
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        if (bytes === 0) return '0 Bytes';
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
    }
}

// Run verification
const verifier = new NetlifyBuildVerifier();
verifier.verify().catch(error => {
    console.error('Build verification failed:', error);
    process.exit(1);
});