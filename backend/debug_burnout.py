#!/usr/bin/env python3
"""
Debug script for burnout risk analysis
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:5000"
TEST_EMAIL = "integration_test@example.com"
TEST_PASSWORD = "testpassword123"

def debug_burnout_analysis():
    """Debug the burnout risk analysis step by step"""
    
    print("🔍 Debugging Burnout Risk Analysis")
    print("=" * 50)
    
    # Step 1: Login
    print("1. Logging in...")
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        return
    
    login_result = response.json()
    token = login_result.get('token')
    print(f"✅ Login successful, token: {token[:50]}...")
    
    # Step 2: Get teams
    print("\n2. Getting teams...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/teams", headers=headers)
    print(f"Teams response: {response.status_code}")
    if response.status_code == 200:
        teams = response.json()
        print(f"Teams: {teams}")
    
    # Step 3: Test burnout analysis
    print("\n3. Testing burnout analysis...")
    response = requests.get(f"{BASE_URL}/api/analytics/burnout-risk", headers=headers)
    print(f"Burnout response: {response.status_code}")
    print(f"Response body: {response.text}")
    
    # Step 4: Test with specific team ID
    if response.status_code != 200 and teams:
        team_id = teams.get('teams', [{}])[0].get('id')
        if team_id:
            print(f"\n4. Testing with specific team ID: {team_id}")
            response = requests.get(f"{BASE_URL}/api/analytics/burnout-risk?team_id={team_id}", headers=headers)
            print(f"Burnout response with team_id: {response.status_code}")
            print(f"Response body: {response.text}")

if __name__ == "__main__":
    debug_burnout_analysis() 