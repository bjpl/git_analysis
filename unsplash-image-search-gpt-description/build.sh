#!/bin/bash

echo "Building Unsplash GPT Tool executable..."
echo

# Clean previous builds
rm -rf dist build

# Create data directory structure
mkdir -p data

# Build executable with PyInstaller
pyinstaller --onefile \
    --windowed \
    --name "unsplash-gpt-tool" \
    --add-data ".env.example:." \
    --add-data "README.md:." \
    --hidden-import "tkinter" \
    --hidden-import "PIL" \
    --hidden-import "openai" \
    --hidden-import "dotenv" \
    main.py

echo
echo "Build complete! Executable is in dist/unsplash-gpt-tool"
echo
echo "To distribute:"
echo "1. Copy dist/unsplash-gpt-tool to a new folder"
echo "2. Users will be prompted for API keys on first run"
echo