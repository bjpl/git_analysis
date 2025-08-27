#!/bin/bash
echo "Starting VocabLens build process..."
echo "Node version: $(node --version)"
echo "NPM version: $(npm --version)"

echo "Installing dependencies..."
npm install

echo "Building application..."
npm run build

echo "Build complete!"
ls -la dist/