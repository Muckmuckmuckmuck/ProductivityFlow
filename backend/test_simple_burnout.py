#!/usr/bin/env python3
"""
Simple test for burnout risk endpoint
"""

import requests
import json

def test_burnout():
    base_url = "http://localhost:5000"
    
    # Step 1: Register a new user
    register_data = {
        "email": "burnout.test@productivityflow.com",
        "password": "testpass123",
        "name": "Burnout Test User"
    }
    
    response = requests.post(f"{base_url}/api/auth/register", json=register_data)
    print(f"Register response: {response.status_code}")
    
    if response.status_code not in [201, 409]:  # 409 means user already exists
        print(f"Register failed: {response.text}")
        return
    
    # Step 2: Login
    login_data = {
        "email": "burnout.test@productivityflow.com",
        "password": "testpass123"
    }
    
    response = requests.post(f"{base_url}/api/auth/login", json=login_data)
    print(f"Login response: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
    
    token = response.json().get('token')
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 3: Create a team
    team_data = {
        "name": "Burnout Test Team",
        "user_name": "Burnout Test User"
    }
    
    response = requests.post(f"{base_url}/api/teams", json=team_data, headers=headers)
    print(f"Team creation response: {response.status_code}")
    
    if response.status_code != 201:
        print(f"Team creation failed: {response.text}")
        return
    
    team_response = response.json()
    team_id = team_response.get('team', {}).get('id')
    new_token = team_response.get('token')
    print(f"Team ID: {team_id}")
    print(f"Full team response: {team_response}")
    
    # Update headers with new token
    if new_token:
        headers = {"Authorization": f"Bearer {new_token}"}
        print(f"Updated token for team: {new_token[:50]}...")
    
    # Step 4: Submit some activity data
    activity_data = {
        "productive_hours": 8.0,
        "unproductive_hours": 2.0,
        "idle_time": 1.0,
        "active_app": "test_app",
        "window_title": "Test Window"
    }
    
    response = requests.post(f"{base_url}/api/teams/{team_id}/activity", json=activity_data, headers=headers)
    print(f"Activity submission response: {response.status_code}")
    
    # Step 5: Test burnout endpoint
    response = requests.get(f"{base_url}/api/analytics/burnout-risk", headers=headers)
    print(f"Burnout response: {response.status_code}")
    print(f"Response body: {response.text}")
    
    # Step 6: Test with specific team
    response = requests.get(f"{base_url}/api/analytics/burnout-risk?team_id={team_id}", headers=headers)
    print(f"Burnout with team_id response: {response.status_code}")
    print(f"Response body: {response.text}")

if __name__ == "__main__":
    test_burnout() 