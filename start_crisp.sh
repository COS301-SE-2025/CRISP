#!/bin/bash

# CRISP Platform Startup Script
# This script starts both the Django backend and React frontend

echo "🚀 Starting CRISP Platform..."
echo "================================"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Define paths
BACKEND_DIR="$SCRIPT_DIR/UserManagment"
FRONTEND_DIR="$SCRIPT_DIR/UI/crisp-react"

# Function to check if a directory exists
check_directory() {
    if [ ! -d "$1" ]; then
        echo "❌ Error: Directory $1 not found!"
        echo "   Please make sure you're running this script from the CRISP root directory."
        exit 1
    fi
}

# Function to check if a command exists
check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo "❌ Error: $1 is not installed or not in PATH"
        echo "   Please install $1 and try again."
        exit 1
    fi
}

# Verify directories exist
echo "📂 Checking directories..."
check_directory "$BACKEND_DIR"
check_directory "$FRONTEND_DIR"

# Verify required commands
echo "🔍 Checking dependencies..."
check_command "python3"
check_command "npm"

# Check if frontend dependencies are installed
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd "$FRONTEND_DIR"
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install frontend dependencies"
        exit 1
    fi
    echo "✅ Frontend dependencies installed"
    cd "$SCRIPT_DIR"
fi

# Function to start backend
start_backend() {
    echo "🔧 Starting Django backend on port 8000..."
    cd "$BACKEND_DIR"
    python3 manage.py runserver &
    BACKEND_PID=$!
    echo "   Backend PID: $BACKEND_PID"
    cd "$SCRIPT_DIR"
}

# Function to start frontend
start_frontend() {
    echo "⚛️  Starting React frontend on port 5173..."
    cd "$FRONTEND_DIR"
    npm run dev &
    FRONTEND_PID=$!
    echo "   Frontend PID: $FRONTEND_PID"
    cd "$SCRIPT_DIR"
}

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down CRISP Platform..."
    if [ ! -z "$BACKEND_PID" ]; then
        echo "   Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        echo "   Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null
    fi
    echo "✅ CRISP Platform stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start both services
start_backend
sleep 3  # Give backend time to start
start_frontend

echo ""
echo "✅ CRISP Platform is starting up!"
echo "================================"
echo "📊 Backend API:      http://127.0.0.1:8000/api/"
echo "🛠️  Admin Interface: http://127.0.0.1:8000/admin/"
echo "🌐 Frontend UI:      http://localhost:5173/"
echo ""
echo "💡 Tips:"
echo "   • Test API endpoints: python3 UserManagment/tests/api/test_api_endpoints.py"
echo "   • Access API overview: http://127.0.0.1:8000/api/"
echo "   • Login to admin: admin / admin123"
echo ""
echo "Press Ctrl+C to stop both services"
echo "================================"

# Wait for background processes
wait