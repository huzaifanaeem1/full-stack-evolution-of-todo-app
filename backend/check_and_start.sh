#!/bin/bash
# Script to check system readiness and start the backend server

echo "=== Backend Server Readiness Check ==="

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: python3 is not installed or not in PATH"
    exit 1
else
    echo "✅ python3 is available: $(python3 --version)"
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ ERROR: pip3 is not installed or not in PATH"
    echo "   Try: sudo apt install python3-pip"
    exit 1
else
    echo "✅ pip3 is available"
fi

# Check if python3-venv package is available by trying to create a simple venv
echo "Checking if python3-venv package is installed..."
temp_dir=$(mktemp -d)
if python3 -m venv "$temp_dir/test_venv" 2>/dev/null; then
    echo "✅ python3-venv package is installed"
    rm -rf "$temp_dir"
else
    echo "❌ ERROR: python3-venv package is not installed"
    echo "   Please run: sudo apt install python3.12-venv"
    rm -rf "$temp_dir"
    exit 1
fi

# Check if we're in the correct directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ ERROR: Not in the backend directory or requirements.txt not found"
    echo "   Navigate to /mnt/d/evolution-of-todo/backend first"
    exit 1
else
    echo "✅ In correct directory with requirements.txt"
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment does not exist, creating one..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    else
        echo "✅ Virtual environment created"
    fi
fi

# Activate virtual environment
source venv/bin/activate

# Check if dependencies are installed
if [ ! -f "venv/bin/uvicorn" ]; then
    echo "⚠️  Backend dependencies not installed, installing..."
    pip install --upgrade pip
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    else
        echo "✅ Dependencies installed"
    fi
else
    echo "✅ Dependencies already installed"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ ERROR: .env file not found"
    echo "   Please create .env file with DATABASE_URL, BETTER_AUTH_SECRET, etc."
    exit 1
else
    echo "✅ .env file exists"
fi

echo ""
echo "=== All checks passed! Ready to start backend server ==="
echo ""
echo "To start the backend server, run:"
echo "  source venv/bin/activate && uvicorn src.main:app --reload --port 8000"
echo ""