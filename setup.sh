#!/bin/bash

# Setup script for Telegram Host Manager Bot

echo "🚀 TeleCommand Pro - Setup"
echo "===================================="
echo ""

# Check Python version
echo "Checking Python version..."
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo "✅ Python $PYTHON_VERSION found"
else
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv
echo "✅ Virtual environment created"

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Create config from example if it doesn't exist
if [ ! -f config.json ]; then
    echo ""
    echo "Creating config.json from example..."
    cp config.example.json config.json
    echo "✅ config.json created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit config.json with:"
    echo "   1. Your Telegram bot token"
    echo "   2. Your Telegram user ID(s)"
    echo ""
else
    echo ""
    echo "⚠️  config.json already exists, skipping..."
fi

echo ""
echo "Setup complete! 🎉"
echo ""
echo "Next steps:"
echo "1. Edit config.json with your bot token and user ID"
echo "2. Run: source venv/bin/activate"
echo "3. Run: python3 bot.py"
echo ""
echo "For more information, see README.md"
