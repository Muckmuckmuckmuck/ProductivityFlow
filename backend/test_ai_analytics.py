#!/usr/bin/env python3
"""
Test script for AI Analytics functionality
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5000"
TEST_EMAIL = "manager@example.com"
TEST_PASSWORD = "testpassword123"
TEST_NAME = "Test Manager"

def test_ai_analytics():
    """Test AI analytics endpoints"""
    
    print("🧪 Testing AI Analytics with Claude API Key")
    print("=" * 50)
    
    # Step 1: Register a new manager user
    print("1. Registering manager user...")
    register_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "name": TEST_NAME
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
    if response.status_code == 201:
        print("   ✅ Manager user registered successfully")
    elif response.status_code == 400 and "already exists" in response.text:
        print("   ✅ Manager user already exists")
    else:
        print(f"   ❌ Failed to register manager: {response.status_code} - {response.text}")
        return False
    
    # Step 2: Login as manager
    print("2. Logging in as manager...")
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code == 200:
        login_result = response.json()
        manager_token = login_result.get('token')
        print("   ✅ Manager login successful")
    else:
        print(f"   ❌ Manager login failed: {response.status_code} - {response.text}")
        return False
    
    # Step 3: Create a team (manager will be automatically assigned as manager)
    print("3. Creating team...")
    team_data = {
        "name": "AI Test Team",
        "user_name": TEST_NAME
    }
    
    headers = {"Authorization": f"Bearer {manager_token}"}
    response = requests.post(f"{BASE_URL}/api/teams", json=team_data, headers=headers)
    if response.status_code == 201:
        team_result = response.json()
        team_id = team_result.get('team', {}).get('id')
        print(f"   ✅ Team created successfully: {team_id}")
    else:
        print(f"   ❌ Team creation failed: {response.status_code} - {response.text}")
        return False
    
    # Step 4: Add some activity data for testing
    print("4. Adding test activity data...")
    activity_data = {
        "activeApp": "VS Code",
        "windowTitle": "test.py - ProductivityFlow",
        "idleTime": 0.25,
        "productiveHours": 2.5,
        "unproductiveHours": 0.5,
        "goalsCompleted": 3
    }
    
    response = requests.post(f"{BASE_URL}/api/teams/{team_id}/activity", 
                           json=activity_data, headers=headers)
    if response.status_code == 201:
        print("   ✅ Activity data added successfully")
    else:
        print(f"   ❌ Activity data addition failed: {response.status_code} - {response.text}")
    
    # Step 5: Test Burnout Risk Analysis
    print("5. Testing Burnout Risk Analysis...")
    response = requests.get(f"{BASE_URL}/api/analytics/burnout-risk", headers=headers)
    if response.status_code == 200:
        result = response.json()
        print("   ✅ Burnout Risk Analysis successful")
        print(f"   📊 Analysis date: {result.get('analysis_date')}")
        print(f"   📊 Team ID: {result.get('team_id')}")
        print(f"   📊 Burnout data: {len(result.get('burnout_analysis', []))} entries")
    else:
        print(f"   ❌ Burnout Risk Analysis failed: {response.status_code} - {response.text}")
    
    # Step 6: Test Distraction Profile Analysis
    print("6. Testing Distraction Profile Analysis...")
    response = requests.get(f"{BASE_URL}/api/analytics/distraction-profile", headers=headers)
    if response.status_code == 200:
        result = response.json()
        print("   ✅ Distraction Profile Analysis successful")
        print(f"   📊 Analysis date: {result.get('analysis_date')}")
        print(f"   📊 Team size: {result.get('team_size')}")
        print(f"   📊 Distraction profile: {len(result.get('distraction_profile', []))} categories")
        print(f"   📊 Insights: {len(result.get('insights', []))} insights")
    else:
        print(f"   ❌ Distraction Profile Analysis failed: {response.status_code} - {response.text}")
    
    print("\n" + "=" * 50)
    print("🎉 AI Analytics Testing Complete!")
    return True

if __name__ == "__main__":
    test_ai_analytics() 