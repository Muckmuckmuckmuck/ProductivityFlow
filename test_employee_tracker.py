#!/usr/bin/env python3
"""
Test script for employee tracker functionality
"""

import requests
import json

# Configuration
API_BASE_URL = "https://productivityflow-backend-v3.onrender.com"

def test_employee_tracker():
    """Test the employee tracker functionality"""
    print("🧪 Testing Employee Tracker Functionality")
    print("=" * 50)
    
    # Test 1: Try to join with a non-existent team code
    print("\n1. Testing with non-existent team code...")
    response = requests.post(f"{API_BASE_URL}/api/teams/join", json={
        "team_code": "NONEXISTENT",
        "employee_name": "Test Employee"
    })
    
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
    
    # Test 2: Try to join with missing parameters
    print("\n2. Testing with missing parameters...")
    response = requests.post(f"{API_BASE_URL}/api/teams/join", json={
        "team_code": "TEST123"
    })
    
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
    
    # Test 3: Try to join with empty parameters
    print("\n3. Testing with empty parameters...")
    response = requests.post(f"{API_BASE_URL}/api/teams/join", json={
        "team_code": "",
        "employee_name": ""
    })
    
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
    
    print("\n✅ Employee tracker API tests completed!")

if __name__ == "__main__":
    test_employee_tracker() 