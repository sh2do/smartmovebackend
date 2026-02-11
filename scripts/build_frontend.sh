#!/bin/bash
set -e

echo "Building frontend..."

# Define frontend directory
FRONTEND_DIR="smartmovefrontend/smartmove"

# Check if frontend directory exists
if [ ! -d "$FRONTEND_DIR" ]; then
    echo "ERROR: Frontend directory not found at $FRONTEND_DIR"
    exit 1
fi

# Navigate to frontend directory
cd "$FRONTEND_DIR"

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo "ERROR: package.json not found in $FRONTEND_DIR"
    exit 1
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install || {
        echo "ERROR: Failed to install frontend dependencies"
        exit 1
    }
fi

# Run the build
echo "Running Vite build..."
npm run build || {
    echo "ERROR: Frontend build failed"
    exit 1
}

echo "Frontend build complete!"
