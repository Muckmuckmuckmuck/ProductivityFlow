#!/bin/bash

echo "🛑 Stopping ProductivityFlow System..."
echo "====================================="

# Kill processes by PID files
if [ -f .backend.pid ]; then
    BACKEND_PID=$(cat .backend.pid)
    echo "🔄 Stopping backend (PID: $BACKEND_PID)..."
    kill $BACKEND_PID 2>/dev/null || true
    rm -f .backend.pid
fi

if [ -f .proxy.pid ]; then
    PROXY_PID=$(cat .proxy.pid)
    echo "🔄 Stopping CORS proxy (PID: $PROXY_PID)..."
    kill $PROXY_PID 2>/dev/null || true
    rm -f .proxy.pid
fi

if [ -f .http.pid ]; then
    HTTP_PID=$(cat .http.pid)
    echo "🔄 Stopping HTTP server (PID: $HTTP_PID)..."
    kill $HTTP_PID 2>/dev/null || true
    rm -f .http.pid
fi

# Kill any remaining processes on our ports
echo "🧹 Cleaning up any remaining processes..."
lsof -ti:5000 | xargs kill -9 2>/dev/null || true
lsof -ti:3001 | xargs kill -9 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

echo "✅ All services stopped"
echo "🎉 ProductivityFlow System shutdown complete!" 