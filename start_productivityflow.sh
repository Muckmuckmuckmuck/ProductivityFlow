#!/bin/bash

# ProductivityFlow Master Startup Script
# This script starts all services in the correct order

echo "🚀 Starting ProductivityFlow System..."
echo "======================================"

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "❌ Port $1 is already in use"
        return 1
    else
        echo "✅ Port $1 is available"
        return 0
    fi
}

# Function to kill processes on a port
kill_port() {
    echo "🔄 Killing processes on port $1..."
    lsof -ti:$1 | xargs kill -9 2>/dev/null || true
    sleep 2
}

# Clean up any existing processes
echo "🧹 Cleaning up existing processes..."
kill_port 5000
kill_port 3001
kill_port 8000

# Check if ports are available
echo "🔍 Checking port availability..."
check_port 5000 || exit 1
check_port 3001 || exit 1
check_port 8000 || exit 1

# Start the secure backend
echo "🔒 Starting secure backend..."
python3 start_secure_backend.py &
BACKEND_PID=$!
sleep 5

# Check if backend started successfully
if ! curl -s http://localhost:5000/health > /dev/null; then
    echo "❌ Backend failed to start"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi
echo "✅ Backend started successfully"

# Start the CORS proxy
echo "🌐 Starting CORS proxy..."
node cors_proxy.js &
PROXY_PID=$!
sleep 3

# Check if proxy started successfully
if ! curl -s http://localhost:3001/health > /dev/null; then
    echo "❌ CORS proxy failed to start"
    kill $BACKEND_PID $PROXY_PID 2>/dev/null
    exit 1
fi
echo "✅ CORS proxy started successfully"

# Start the HTTP server
echo "📁 Starting HTTP server..."
python3 -m http.server 8000 &
HTTP_PID=$!
sleep 2

# Check if HTTP server started successfully
if ! curl -s http://localhost:8000/ > /dev/null; then
    echo "❌ HTTP server failed to start"
    kill $BACKEND_PID $PROXY_PID $HTTP_PID 2>/dev/null
    exit 1
fi
echo "✅ HTTP server started successfully"

# Test the complete system
echo "🧪 Testing complete system..."
echo "Testing backend health..."
curl -s http://localhost:5000/health | python3 -m json.tool

echo "Testing CORS proxy..."
curl -s http://localhost:3001/health | python3 -m json.tool

echo "Testing account creation..."
curl -X POST http://localhost:3001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@productivityflow.com","password":"SecurePass123","name":"Test User"}' \
  | python3 -m json.tool

echo ""
echo "🎉 ProductivityFlow System Started Successfully!"
echo "================================================"
echo "🔒 Secure Backend: http://localhost:5000"
echo "🌐 CORS Proxy: http://localhost:3001"
echo "📁 HTTP Server: http://localhost:8000"
echo ""
echo "📱 Test Pages:"
echo "   • Security Test: http://localhost:8000/debug_security_test.html"
echo "   • Everything Working: http://localhost:8000/debug_everything_working.html"
echo "   • Working Backend: http://localhost:8000/debug_working_backend.html"
echo ""
echo "🛑 To stop all services, run: ./stop_productivityflow.sh"
echo ""

# Save PIDs for later cleanup
echo $BACKEND_PID > .backend.pid
echo $PROXY_PID > .proxy.pid
echo $HTTP_PID > .http.pid

# Keep script running and handle cleanup on exit
trap 'echo "🛑 Shutting down services..."; kill $BACKEND_PID $PROXY_PID $HTTP_PID 2>/dev/null; rm -f .backend.pid .proxy.pid .http.pid; echo "✅ All services stopped"; exit 0' INT TERM

echo "⏳ Services are running. Press Ctrl+C to stop all services."
echo ""

# Monitor services
while true; do
    sleep 30
    echo "🔍 Health check..."
    
    # Check backend
    if ! curl -s http://localhost:5000/health > /dev/null; then
        echo "❌ Backend is down, restarting..."
        kill $BACKEND_PID 2>/dev/null
        python3 start_secure_backend.py &
        BACKEND_PID=$!
        echo $BACKEND_PID > .backend.pid
    fi
    
    # Check proxy
    if ! curl -s http://localhost:3001/health > /dev/null; then
        echo "❌ CORS proxy is down, restarting..."
        kill $PROXY_PID 2>/dev/null
        node cors_proxy.js &
        PROXY_PID=$!
        echo $PROXY_PID > .proxy.pid
    fi
    
    echo "✅ All services healthy"
done 