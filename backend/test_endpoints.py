#!/usr/bin/env python3
"""
Test script to verify all API endpoints are working
"""

import requests
import json
import time

# Test configuration
BASE_URL = "http://localhost:5000"
API_URL = "https://productivityflow-backend-496367590729.us-central1.run.app"

def test_endpoint(endpoint, method="GET", data=None, description=""):
    """Test a single endpoint"""
    url = f"{API_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
        
        if response.status_code in [200, 201]:
            print(f"✅ {description} - {endpoint}")
            return True
        else:
            print(f"❌ {description} - {endpoint} (Status: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ {description} - {endpoint} (Error: {str(e)})")
        return False

def main():
    """Test all required endpoints"""
    print("🧪 Testing ProductivityFlow Backend Endpoints")
    print("=" * 50)
    
    # Test basic endpoints
    test_endpoint("/health", "GET", description="Health Check")
    
    # Test authentication endpoints
    test_endpoint("/api/auth/register", "POST", {
        "email": "test@example.com",
        "password": "test123",
        "name": "Test User"
    }, "User Registration")
    
    test_endpoint("/api/auth/login", "POST", {
        "email": "test@example.com",
        "password": "test123"
    }, "User Login")
    
    # Test team endpoints
    test_endpoint("/api/teams", "GET", description="Get Teams")
    
    test_endpoint("/api/teams", "POST", {
        "name": "Test Team",
        "manager_id": "test_manager"
    }, "Create Team")
    
    test_endpoint("/api/teams/join", "POST", {
        "employee_code": "TEST123",
        "user_name": "Test Employee"
    }, "Join Team")
    
    # Test team-specific endpoints
    test_endpoint("/api/teams/test_team/members", "GET", description="Get Team Members")
    test_endpoint("/api/teams/test_team/analytics", "GET", description="Get Team Analytics")
    test_endpoint("/api/teams/test_team/members/realtime", "GET", description="Get Real-time Members")
    test_endpoint("/api/teams/test_team/tasks", "GET", description="Get Team Tasks")
    
    # Test analytics endpoints
    test_endpoint("/api/analytics/burnout-risk", "GET", description="Burnout Risk Analysis")
    test_endpoint("/api/analytics/distraction-profile", "GET", description="Distraction Profile")
    
    # Test subscription endpoints
    test_endpoint("/api/subscription/status", "GET", description="Subscription Status")
    
    # Test employee endpoints
    test_endpoint("/api/employee/daily-summary", "GET", description="Daily Summary")
    
    # Test activity tracking
    test_endpoint("/api/activity/track", "POST", {
        "user_id": "test_user",
        "team_id": "test_team",
        "active_app": "VS Code",
        "productive_hours": 2.5,
        "unproductive_hours": 0.5
    }, "Activity Tracking")
    
    print("\n" + "=" * 50)
    print("🎉 Endpoint testing completed!")

if __name__ == "__main__":
    main() 