#!/usr/bin/env python3
"""
Test distraction profile endpoint
"""

import requests
import json

def test_distraction_profile():
    base_url = "http://localhost:5000"
    
    # Step 1: Register a new user
    register_data = {
        "email": "distraction.test@productivityflow.com",
        "password": "testpass123",
        "name": "Distraction Test User"
    }
    
    response = requests.post(f"{base_url}/api/auth/register", json=register_data)
    print(f"Register response: {response.status_code}")
    
    if response.status_code not in [201, 409]:  # 409 means user already exists
        print(f"Register failed: {response.text}")
        return
    
    # Step 2: Login
    login_data = {
        "email": "distraction.test@productivityflow.com",
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
        "name": "Distraction Test Team",
        "user_name": "Distraction Test User"
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
        "active_app": "chrome",
        "window_title": "Google - Chrome",
        "productive_hours": 2.5,
        "unproductive_hours": 1.0,
        "idle_time": 0.5,
        "goals_completed": 3
    }
    
    response = requests.post(f"{base_url}/api/teams/{team_id}/activity", json=activity_data, headers=headers)
    print(f"Activity submission response: {response.status_code}")
    
    # Step 5: Test distraction profile endpoint
    response = requests.get(f"{base_url}/api/analytics/distraction-profile", headers=headers)
    print(f"Distraction profile response: {response.status_code}")
    print(f"Response body: {response.text}")
    
    # Step 6: Test with team_id parameter
    response = requests.get(f"{base_url}/api/analytics/distraction-profile?team_id={team_id}", headers=headers)
    print(f"Distraction profile with team_id response: {response.status_code}")
    print(f"Response body: {response.text}")

if __name__ == "__main__":
    test_distraction_profile() 