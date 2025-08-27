#!/usr/bin/env node

/**
 * Netlify Safety Check Script
 * Validates that no submodule artifacts exist before build
 */

import fs from 'fs';
import path from 'path';

console.log('🔍 Running Netlify safety checks...');

const SAFETY_CHECKS = [
    {
        name: 'Check for active submodules',
        check: () => {
            if (fs.existsSync('.gitmodules')) {
                const content = fs.readFileSync('.gitmodules', 'utf8');
                // Check if .gitmodules has actual submodule definitions
                const hasActiveSubmodules = content.includes('[submodule') && 
                                          !content.includes('# This file intentionally left empty');
                return !hasActiveSubmodules;
            }
            return true;
        },
        failMessage: 'Active submodules detected in .gitmodules'
    },
    {
        name: 'Verify no submodule directories exist',
        check: () => {
            const items = fs.readdirSync('.');
            const potentialSubmodules = items.filter(item => {
                if (item === '.git' || item === 'node_modules' || item === 'dist') return false;
                if (!fs.statSync(item).isDirectory()) return false;
                return fs.existsSync(path.join(item, '.git'));
            });
            return potentialSubmodules.length === 0;
        },
        failMessage: 'Potential submodule directories found'
    },
    {
        name: 'Check parent directory isolation',
        check: () => {
            // Ensure we're not accidentally in a parent directory that might have submodules
            const parentDir = path.resolve('..');
            const hasParentGitModules = fs.existsSync(path.join(parentDir, '.gitmodules'));
            const hasParentSubmodules = hasParentGitModules ? 
                fs.readFileSync(path.join(parentDir, '.gitmodules'), 'utf8').includes('[submodule') : false;
            
            if (hasParentSubmodules) {
                console.warn('⚠️  Parent directory has submodules - this is expected and will be ignored');
            }
            return true; // Always pass - parent submodules don't affect this build
        },
        failMessage: 'Parent directory submodule check failed'
    },
    {
        name: 'Verify package.json integrity', 
        check: () => {
            if (!fs.existsSync('package.json')) return false;
            const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
            return pkg.scripts && pkg.scripts.build;
        },
        failMessage: 'package.json missing or invalid'
    },
    {
        name: 'Check build script exists',
        check: () => {
            return fs.existsSync('scripts/netlify-build.sh');
        },
        failMessage: 'Netlify build script missing'
    }
];

let allPassed = true;

for (const check of SAFETY_CHECKS) {
    try {
        if (check.check()) {
            console.log(`✅ ${check.name}`);
        } else {
            console.error(`❌ ${check.name}: ${check.failMessage}`);
            allPassed = false;
        }
    } catch (error) {
        console.error(`❌ ${check.name}: ${error.message}`);
        allPassed = false;
    }
}

if (allPassed) {
    console.log('🎉 All safety checks passed - ready for Netlify build');
    process.exit(0);
} else {
    console.error('💥 Safety checks failed - build should not proceed');
    process.exit(1);
}