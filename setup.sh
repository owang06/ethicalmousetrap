#!/bin/bash
# Setup script for mouse detector

echo "=========================================="
echo "Mouse Detector Setup"
echo "=========================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements_detector.txt

if [ $? -eq 0 ]; then
    echo "✓ Python dependencies installed successfully"
else
    echo "✗ Failed to install Python dependencies"
    echo "Try running: pip3 install flask flask-cors opencv-python google-generativeai pillow"
    exit 1
fi

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "To start the application, run:"
echo "  npm run dev"
echo ""

