#!/bin/bash

echo "🔧 ProductivityFlow Quick Debug Commands"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check service status
check_service() {
    local service_name=$1
    local process_name=$2
    echo -e "${BLUE}📡 Checking $service_name...${NC}"
    if pgrep -f "$process_name" > /dev/null; then
        echo -e "${GREEN}✅ $service_name is running${NC}"
        return 0
    else
        echo -e "${RED}❌ $service_name is not running${NC}"
        return 1
    fi
}

# Function to start service
start_service() {
    local service_name=$1
    local command=$2
    echo -e "${YELLOW}🚀 Starting $service_name...${NC}"
    eval "$command" &
    sleep 2
    check_service "$service_name" "$3"
}

echo "🔍 Service Status Check:"
echo "======================="
check_service "Backend" "start_working_backend_with_reset.py"
check_service "CORS Proxy" "cors_proxy.js"
check_service "Debug Server" "debug_server.py"
echo ""

echo "🌐 API Tests:"
echo "============"
echo -e "${BLUE}Testing Backend Health:${NC}"
curl -s http://localhost:5000/health | python3 -m json.tool 2>/dev/null || echo -e "${RED}❌ Backend not responding${NC}"
echo ""

echo -e "${BLUE}Testing CORS Proxy:${NC}"
curl -s http://localhost:3002/health | python3 -m json.tool 2>/dev/null || echo -e "${RED}❌ CORS Proxy not responding${NC}"
echo ""

echo -e "${BLUE}Testing Login:${NC}"
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:3002/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"Jaymreddy12@gmail.com","password":"password123"}')

if echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print('✅ Login successful' if 'token' in data else '❌ Login failed')" 2>/dev/null; then
    echo -e "${GREEN}✅ Login working${NC}"
    TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])" 2>/dev/null)
    echo -e "${BLUE}Testing Team Creation:${NC}"
    curl -s -X POST http://localhost:3002/api/teams \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOKEN" \
      -d '{"name":"Debug Test Team"}' | python3 -m json.tool 2>/dev/null || echo -e "${RED}❌ Team creation failed${NC}"
else
    echo -e "${RED}❌ Login failed${NC}"
fi
echo ""

echo "🔧 Quick Fix Commands:"
echo "====================="
echo ""
echo -e "${YELLOW}🚀 Start Backend:${NC}"
echo "   python3 start_working_backend_with_reset.py &"
echo ""
echo -e "${YELLOW}🌐 Start CORS Proxy:${NC}"
echo "   node cors_proxy.js &"
echo ""
echo -e "${YELLOW}🔧 Start Debug Server:${NC}"
echo "   python3 debug_server.py &"
echo ""
echo -e "${YELLOW}🔨 Rebuild Manager Dashboard:${NC}"
echo "   cd manager-dashboard-tauri && npm run build"
echo ""
echo -e "${YELLOW}🔨 Rebuild Employee Tracker:${NC}"
echo "   cd employee-tracker-tauri && npm run build"
echo ""
echo -e "${YELLOW}📊 Check Database:${NC}"
echo "   sqlite3 productivityflow_working.db '.tables'"
echo ""
echo -e "${YELLOW}👥 Check Users:${NC}"
echo "   sqlite3 productivityflow_working.db 'SELECT id, email, name FROM users;'"
echo ""
echo -e "${YELLOW}🏢 Check Teams:${NC}"
echo "   sqlite3 productivityflow_working.db 'SELECT id, name FROM teams;'"
echo ""
echo -e "${YELLOW}🛑 Kill All Services:${NC}"
echo "   pkill -f start_working_backend_with_reset.py"
echo "   pkill -f cors_proxy.js"
echo "   pkill -f debug_server.py"
echo ""
echo -e "${YELLOW}🎯 Open Debug Page:${NC}"
echo "   open http://localhost:8080/debug_login.html"
echo ""
echo -e "${YELLOW}🎯 Open Debug Page (Alternative):${NC}"
echo "   python3 debug_server.py"
echo "   # Then open: http://localhost:8080/debug_login.html"
echo ""

echo "📱 Debug URLs:"
echo "============="
echo -e "${BLUE}Debug Page:${NC} http://localhost:8080/debug_login.html"
echo -e "${BLUE}Backend Health:${NC} http://localhost:5000/health"
echo -e "${BLUE}CORS Proxy Health:${NC} http://localhost:3002/health"
echo -e "${BLUE}Direct Backend:${NC} http://localhost:5000"
echo ""

echo "🔧 Manual Test Commands:"
echo "======================="
echo ""
echo -e "${BLUE}Test Login:${NC}"
echo 'curl -X POST http://localhost:3002/api/auth/login -H "Content-Type: application/json" -d '"'"'{"email":"Jaymreddy12@gmail.com","password":"password123"}'"'"''
echo ""
echo -e "${BLUE}Test Team Creation:${NC}"
echo 'curl -X POST http://localhost:3002/api/teams -H "Content-Type: application/json" -H "Authorization: Bearer YOUR_TOKEN" -d '"'"'{"name":"Test Team"}'"'"''
echo ""
echo -e "${BLUE}Test Team Joining:${NC}"
echo 'curl -X POST http://localhost:3002/api/teams/join -H "Content-Type: application/json" -d '"'"'{"team_code":"TEAM6","user_name":"Test User"}'"'"''
echo "" 