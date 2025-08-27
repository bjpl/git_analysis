#!/usr/bin/env node

/**
 * Test script to verify API endpoints work locally
 * Run: node test-apis.js
 */

import http from 'http';
import path from 'path';

const BASE_URL = 'http://localhost:3000';

const tests = [
    {
        name: 'Debug API Endpoint',
        path: '/api/debug',
        expected: 200
    },
    {
        name: 'Health Check API',
        path: '/api/health', 
        expected: 200
    },
    {
        name: 'Static Test Page',
        path: '/public/test.html',
        expected: 200
    },
    {
        name: 'Main Index Page',
        path: '/public/index.html',
        expected: 200
    },
    {
        name: 'Route Test Page',
        path: '/public/route-test.html',
        expected: 200
    }
];

async function testEndpoint(test) {
    return new Promise((resolve) => {
        const startTime = Date.now();
        
        http.get(`${BASE_URL}${test.path}`, (res) => {
            const duration = Date.now() - startTime;
            let data = '';
            
            res.on('data', (chunk) => {
                data += chunk;
            });
            
            res.on('end', () => {
                const success = res.statusCode === test.expected;
                resolve({
                    ...test,
                    status: res.statusCode,
                    success,
                    duration,
                    size: data.length,
                    contentType: res.headers['content-type']
                });
            });
        }).on('error', (err) => {
            resolve({
                ...test,
                error: err.message,
                success: false,
                duration: Date.now() - startTime
            });
        });
    });
}

async function runTests() {
    console.log('🚀 Testing Vercel Deployment Setup...\n');
    
    const results = [];
    
    for (const test of tests) {
        process.stdout.write(`Testing ${test.name}... `);
        const result = await testEndpoint(test);
        results.push(result);
        
        if (result.success) {
            console.log(`✅ ${result.status} (${result.duration}ms)`);
        } else {
            console.log(`❌ ${result.error || `${result.status} (expected ${test.expected})`}`);
        }
    }
    
    console.log('\n📊 Test Summary:');
    console.log(`✅ Passed: ${results.filter(r => r.success).length}`);
    console.log(`❌ Failed: ${results.filter(r => !r.success).length}`);
    console.log(`📈 Total: ${results.length}`);
    
    if (results.every(r => r.success)) {
        console.log('\n🎉 All tests passed! Ready for Vercel deployment.');
        process.exit(0);
    } else {
        console.log('\n⚠️  Some tests failed. Check your local server setup.');
        process.exit(1);
    }
}

// Check if we should test locally or just show info
if (process.argv.includes('--info')) {
    console.log('📝 Vercel Deployment Test Configuration:');
    console.log('\nFiles created:');
    console.log('- /public/test.html - Basic HTML test page');
    console.log('- /public/index.html - React CDN test page');  
    console.log('- /public/route-test.html - Routing test page');
    console.log('- /api/debug.js - Debug API endpoint');
    console.log('- /vercel.json - Vercel routing configuration');
    console.log('- /package-minimal.json - Minimal package.json');
    console.log('\nTo test locally: npx http-server . -p 3000 & node test-apis.js');
    console.log('To deploy: vercel --prod');
} else {
    runTests().catch(console.error);
}