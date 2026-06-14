#!/bin/bash
# Script to build EchoType as a standalone executable for macOS

echo "🔨 Building EchoType Python Desktop App..."

# Check if venv is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not activated. Activating venv..."
    source venv/bin/activate
fi

# Install build dependencies
echo "📦 Installing build dependencies..."
pip install pyinstaller

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build dist "EchoType.app"

# Build the app
echo "🏗️  Building application..."
pyinstaller echotype.spec

# Check if build succeeded
if [ -d "dist/EchoType.app" ]; then
    echo "✅ Build successful!"
    echo "📍 Location: dist/EchoType.app"
    echo ""
    echo "To run the app:"
    echo "  open dist/EchoType.app"
else
    echo "❌ Build failed!"
    exit 1
fi
