#!/bin/bash

# FashnAI Startup Script
# This script starts both the backend (agents) and frontend simultaneously

set -e

echo "🚀 Starting FashnAI..."
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file with your API keys:"
    echo "  GEMINI_API_KEY=your-gemini-api-key"
    echo "  SERPER_API_KEY=your-serper-api-key"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d .venv ]; then
    echo "❌ Error: Virtual environment not found!"
    echo "Please run: uv sync"
    exit 1
fi

# Always update frontend dependencies to ensure latest code
echo "📦 Updating frontend dependencies..."
cd frontend
npm install
cd ..

echo "✅ Starting backend and frontend..."
echo ""
echo "Backend API: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Kill any existing processes to ensure clean start
echo "🧹 Cleaning up any existing processes..."
pkill -f "uvicorn.*api:app" 2>/dev/null || true
pkill -f "next dev" 2>/dev/null || true
sleep 1

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $(jobs -p) 2>/dev/null
    pkill -f "uvicorn.*api:app" 2>/dev/null || true
    pkill -f "next dev" 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend in background
echo "🔧 Starting backend API server..."
uv run backend/api.py > backend_log.txt 2>&1 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Start frontend in background
echo "🎨 Starting frontend..."
cd frontend
npm run dev > ../frontend_log.txt 2>&1 &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ All services started!"
echo "   Backend PID: $BACKEND_PID"
echo "   Frontend PID: $FRONTEND_PID"
echo ""
echo "📝 Logs:"
echo "   Backend: tail -f backend_log.txt"
echo "   Frontend: tail -f frontend_log.txt"
echo ""

# Wait for both processes
wait
