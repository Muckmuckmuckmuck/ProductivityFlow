#!/bin/bash

echo "🔧 ProductivityFlow Debug Commands"
echo "=================================="
echo ""

# Function to check if a service is running
check_service() {
    local service_name=$1
    local process_name=$2
    echo "📡 Checking $service_name..."
    if pgrep -f "$process_name" > /dev/null; then
        echo "✅ $service_name is running"
        return 0
    else
        echo "❌ $service_name is not running"
        return 1
    fi
}

# Check backend services
echo "🔍 Checking Backend Services:"
check_service "Backend" "start_working_backend_with_reset.py"
check_service "CORS Proxy" "cors_proxy.js"
echo ""

# Test backend health
echo "🌐 Testing Backend Health:"
curl -s http://localhost:5000/health | python3 -m json.tool 2>/dev/null || echo "❌ Backend not responding"
echo ""

# Test CORS proxy
echo "🌐 Testing CORS Proxy:"
curl -s http://localhost:3002/health | python3 -m json.tool 2>/dev/null || echo "❌ CORS Proxy not responding"
echo ""

# Test login
echo "👤 Testing Login:"
curl -X POST http://localhost:3002/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"Jaymreddy12@gmail.com","password":"password123"}' \
  | python3 -m json.tool 2>/dev/null || echo "❌ Login failed"
echo ""

# Test team creation
echo "🏢 Testing Team Creation:"
TOKEN=$(curl -s -X POST http://localhost:3002/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"Jaymreddy12@gmail.com","password":"password123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])" 2>/dev/null)

if [ ! -z "$TOKEN" ]; then
    curl -X POST http://localhost:3002/api/teams \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOKEN" \
      -d '{"name":"Debug Test Team"}' \
      | python3 -m json.tool 2>/dev/null || echo "❌ Team creation failed"
else
    echo "❌ Could not get auth token"
fi
echo ""

echo "🔧 Quick Fix Commands:"
echo "====================="
echo ""
echo "🚀 Start Backend:"
echo "   python3 start_working_backend_with_reset.py &"
echo ""
echo "🌐 Start CORS Proxy:"
echo "   node cors_proxy.js &"
echo ""
echo "🔨 Rebuild Manager Dashboard:"
echo "   cd manager-dashboard-tauri && npm run build"
echo ""
echo "🔨 Rebuild Employee Tracker:"
echo "   cd employee-tracker-tauri && npm run build"
echo ""
echo "📊 Check Database:"
echo "   sqlite3 productivityflow_working.db '.tables'"
echo ""
echo "👥 Check Users:"
echo "   sqlite3 productivityflow_working.db 'SELECT id, email, name FROM users;'"
echo ""
echo "🏢 Check Teams:"
echo "   sqlite3 productivityflow_working.db 'SELECT id, name FROM teams;'"
echo ""
echo "🔗 Check Team Members:"
echo "   sqlite3 productivityflow_working.db 'SELECT * FROM team_members;'"
echo ""
echo "🛑 Kill All Services:"
echo "   pkill -f start_working_backend_with_reset.py"
echo "   pkill -f cors_proxy.js"
echo ""
echo "🎯 Open Debug Page:"
echo "   open debug_login.html"
echo "" 