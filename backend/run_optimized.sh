#!/bin/bash
"""
Optimized Server Startup Script
Uses the correct Python environment with all optimizations
"""

echo "🚀 Starting Optimized Travel Agent Server"
echo "=========================================="

# Set the correct Python path
PYTHON_PATH="/usr/local/bin/python3"

# Check if Python is available
if ! command -v $PYTHON_PATH &> /dev/null; then
    echo "❌ Python not found at $PYTHON_PATH"
    echo "Please install Python or update the path in this script"
    exit 1
fi

# Check if packages are available
echo "🔍 Checking dependencies..."
$PYTHON_PATH -c "import fastapi, uvicorn, redis, sqlalchemy, cachetools, aiohttp, psutil" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ All dependencies available"
else
    echo "❌ Missing dependencies. Installing..."
    $PYTHON_PATH -m pip install -r requirements.txt
fi

# Start the optimized server
echo "🚀 Starting server with optimizations..."
echo "📊 Available endpoints:"
echo "  • http://localhost:8000/health - Health check"
echo "  • http://localhost:8000/metrics - Performance metrics"
echo "  • http://localhost:8000/performance - Performance insights"
echo "  • http://localhost:8000/optimize - Optimization suggestions"
echo "  • http://localhost:8000/chat - Main chat endpoint"
echo ""
echo "⏳ Server starting... Press Ctrl+C to stop"
echo ""

# Start the server with optimizations
$PYTHON_PATH -m uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --loop asyncio \
    --access-log \
    --log-level info
