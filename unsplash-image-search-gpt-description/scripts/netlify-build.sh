#!/bin/bash

# Netlify Bulletproof Build Script - Complete Submodule Bypass
# This script ensures NO submodule processing occurs during Netlify builds

set -e  # Exit on any error

echo "🚀 Starting bulletproof Netlify build (submodule-free)"

# CRITICAL: Disable all git submodule operations globally
echo "🔒 Configuring git to completely ignore submodules..."
git config --global submodule.recurse false || true
git config --global fetch.recurseSubmodules false || true
git config --global push.recurseSubmodules false || true
git config --global status.submodulesummary 0 || true

# Additional safety: disable submodule commands entirely
git config --global alias.submodule '!echo "Submodules disabled for Netlify build" && false' || true

# Prevent any existing .gitmodules from being processed
if [ -f ".gitmodules" ]; then
    echo "⚠️  Found .gitmodules - temporarily disabling..."
    mv .gitmodules .gitmodules.disabled || true
fi

# Clean any potential submodule artifacts
echo "🧹 Cleaning potential submodule artifacts..."
find . -name "*.git*" -not -path "./.git/*" -delete 2>/dev/null || true

# Verify we're in a clean state
echo "📍 Current directory: $(pwd)"
echo "📂 Directory contents:"
ls -la | head -10

# Check Node.js and npm versions
echo "🔍 Node.js version: $(node --version)"
echo "🔍 npm version: $(npm --version)"

# Install dependencies with explicit timeout and retry
echo "📦 Installing dependencies (with retry logic)..."
for i in {1..3}; do
    if npm install --no-optional --no-audit --no-fund --prefer-offline; then
        echo "✅ Dependencies installed successfully"
        break
    else
        echo "⚠️  Attempt $i failed, retrying..."
        rm -rf node_modules package-lock.json 2>/dev/null || true
        sleep 2
    fi
    if [ $i -eq 3 ]; then
        echo "❌ Failed to install dependencies after 3 attempts"
        exit 1
    fi
done

# Verify critical dependencies
echo "🔍 Verifying build dependencies..."
if ! npm list vite --depth=0 2>/dev/null; then
    echo "📦 Installing vite explicitly..."
    npm install vite --save-dev
fi

# Run the build with error handling
echo "🏗️  Building application..."
if npm run build; then
    echo "✅ Build completed successfully"
else
    echo "❌ Build failed, attempting recovery..."
    # Try alternative build approach
    if npx vite build; then
        echo "✅ Recovery build successful"
    else
        echo "❌ All build attempts failed"
        exit 1
    fi
fi

# Verify build output
if [ -d "dist" ] && [ "$(ls -A dist)" ]; then
    echo "✅ Build artifacts verified in dist/"
    ls -la dist/ | head -5
else
    echo "❌ Build output missing or empty"
    exit 1
fi

# Restore .gitmodules if it was disabled (though it shouldn't matter for build)
if [ -f ".gitmodules.disabled" ]; then
    echo "🔄 Restoring .gitmodules..."
    mv .gitmodules.disabled .gitmodules || true
fi

echo "🎉 Bulletproof build completed successfully - no submodules processed!"