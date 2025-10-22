#!/bin/bash
"""
Start Refactored Travel Agent Server
Clean, testable service with Amadeus integration
"""

echo "🚀 Starting Refactored Travel Agent Server"
echo "=========================================="

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 16+ first."
    exit 1
fi

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install npm first."
    exit 1
fi

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from example..."
    if [ -f "env.example" ]; then
        cp env.example .env
        echo "📝 Please update .env with your Amadeus API credentials"
    else
        echo "❌ env.example file not found. Please create .env manually."
        exit 1
    fi
fi

# Start the server
echo "🚀 Starting server..."
echo "📊 Available endpoints:"
echo "  • http://localhost:3000/health - Health check"
echo "  • http://localhost:3000/api/flights/search - Flight search"
echo "  • http://localhost:3000/api/chat - Legacy chat endpoint"
echo "  • http://localhost:3000/api/flights/airlines - Available airlines"
echo ""
echo "⏳ Server starting... Press Ctrl+C to stop"
echo ""

# Start the server
node server.js
