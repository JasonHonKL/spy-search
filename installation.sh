#!/bin/bash
set -e  # Exit on any error

echo "Starting installation process..."

# Check if uv is installed
command_exists() {
  command -v "$1" > /dev/null 2>&1
}

if command_exists uv; then
  echo "uv is installed"
else
  echo "uv not found, installing uv..."
  pip install uv || { echo "Failed to install uv"; exit 1; }
fi

# Install uvicorn and other requirements directly (no virtual environment)
echo "Installing uvicorn..."
uv pip install --system uvicorn || { echo "Failed to install uvicorn"; exit 1; }

echo "Installing Python requirements..."
uv pip install --system -r requirements.txt || { echo "Failed to install requirements"; exit 1; }

# Install playwright browsers
echo "Installing playwright browsers..."
playwright install || { echo "Failed to install playwright browsers"; exit 1; }

# Navigate to frontend directory and install npm dependencies
echo "Installing frontend dependencies..."
cd frontend || { echo "Failed to enter frontend directory"; exit 1; }
npm install --legacy-peer-deps || { echo "npm install failed"; exit 1; }

echo "Installation completed successfully!"