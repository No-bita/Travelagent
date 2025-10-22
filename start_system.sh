#!/bin/bash

echo "🚀 Starting Travel Agent System"
echo "================================"

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -ti:$port > /dev/null 2>&1; then
        echo "⚠️  Port $port is already in use. Attempting to free it..."
        lsof -ti:$port | xargs kill -9 2>/dev/null
        sleep 2
        if lsof -ti:$port > /dev/null 2>&1; then
            echo "❌ Could not free port $port. Please stop the service manually."
            exit 1
        fi
    fi
}

# Function to wait for service with retry
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo "✅ $service_name is running"
            return 0
        fi
        echo "⏳ Waiting for $service_name... (attempt $attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done
    
    echo "❌ $service_name failed to start after $max_attempts attempts"
    return 1
}

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python first."
    exit 1
fi

echo "✅ Node.js version: $(node --version)"
echo "✅ Python version: $(python --version)"

# Check for port conflicts
echo ""
echo "🔍 Checking for port conflicts..."
check_port 8000
check_port 3000

# Install frontend dependencies if needed
echo ""
echo "📦 Installing frontend dependencies..."
if ! npm install; then
    echo "❌ Failed to install frontend dependencies"
    exit 1
fi

# Install backend dependencies if needed
echo ""
echo "📦 Installing backend dependencies..."
cd backend
if ! pip install -r requirements.txt; then
    echo "❌ Failed to install backend dependencies"
    exit 1
fi
cd ..

echo ""
echo "🚀 Starting Backend Server (Port 8000)..."
cd backend
python -m uvicorn main_async:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to start with retry logic
if ! wait_for_service "http://localhost:8000/api/health" "Backend server"; then
    echo "❌ Backend server failed to start"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo ""
echo "🚀 Starting Frontend Server (Port 3000)..."
npm start &
FRONTEND_PID=$!

# Wait for frontend to start with retry logic
if ! wait_for_service "http://localhost:3000/api/health" "Frontend server"; then
    echo "❌ Frontend server failed to start"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 1
fi

echo ""
echo "🎉 System is running!"
echo "====================="
echo "🌐 Frontend: http://localhost:3000"
echo "🌐 Backend:  http://localhost:8000"
echo "🌐 Chat UI:  Open index.html in your browser"
echo ""
echo "🧪 Test the system:"
echo "   curl -X POST http://localhost:3000/api/chat \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"message\": \"bom to del tomorrow\", \"context\": {\"step\": \"initial\"}}'"
echo ""
echo "📊 Check backend city API:"
echo "   curl -X POST http://localhost:8000/api/cities/match \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"input\": \"coimbatore\"}'"
echo ""
echo "🛑 To stop the system, press Ctrl+C"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping system..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ System stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Keep the script running
wait
