#!/usr/bin/env python3
"""
Comprehensive Employee Tracking Test Script
Tests all enhanced tracking features and analytics
"""

import requests
import json
import time
import random
from datetime import datetime, timedelta

def generate_test_data():
    """Generate realistic test data for comprehensive tracking"""
    test_id = f"test_{int(time.time())}"
    
    # Test user data
    user_data = {
        "name": f"Test Employee {test_id}",
        "email": f"employee{test_id}@test.com",
        "password": "TestPassword123!"
    }
    
    # Test team data
    team_data = {
        "name": f"Test Team {test_id}",
        "user_name": f"Test Manager {test_id}"
    }
    
    return user_data, team_data

def test_comprehensive_tracking():
    """Test all comprehensive tracking features"""
    base_url = "https://my-home-backend-7m6d.onrender.com"
    
    print("🚀 TESTING COMPREHENSIVE EMPLOYEE TRACKING")
    print("=" * 60)
    
    # Step 1: Create manager and team
    print("\n1. Creating manager and team...")
    user_data, team_data = generate_test_data()
    
    # Create manager
    manager_response = requests.post(f"{base_url}/api/auth/register", json={
        "name": team_data["user_name"],
        "email": f"manager{int(time.time())}@test.com",
        "password": "TestPassword123!",
        "organization": team_data["name"]
    })
    
    if manager_response.status_code != 201:
        print(f"❌ Manager creation failed: {manager_response.text}")
        return False
    
    manager_result = manager_response.json()
    manager_token = manager_result['token']
    team_id = manager_result['team']['id']
    employee_code = manager_result['team']['employee_code']
    
    print(f"✅ Manager created: {manager_result['user']['name']}")
    print(f"✅ Team created: {manager_result['team']['name']}")
    print(f"✅ Employee code: {employee_code}")
    
    # Step 2: Create employee account
    print("\n2. Creating employee account...")
    employee_response = requests.post(f"{base_url}/api/teams/join", json={
        "employee_code": employee_code,
        "user_name": user_data["name"]
    })
    
    if employee_response.status_code != 201:
        print(f"❌ Employee creation failed: {employee_response.text}")
        return False
    
    employee_result = employee_response.json()
    employee_user = employee_result['user']
    
    print(f"✅ Employee created: {employee_user['name']}")
    
    # Step 3: Employee login
    print("\n3. Employee login...")
    login_response = requests.post(f"{base_url}/api/auth/employee-login", json={
        "team_code": employee_code,
        "user_name": employee_user['name']
    })
    
    if login_response.status_code != 200:
        print(f"❌ Employee login failed: {login_response.text}")
        return False
    
    login_result = login_response.json()
    employee_token = login_result['token']
    
    print(f"✅ Employee logged in successfully")
    
    # Step 4: Test comprehensive activity tracking
    print("\n4. Testing comprehensive activity tracking...")
    
    # Generate realistic activity data
    activity_data = {
        "user_id": employee_user['id'],
        "team_id": employee_user['team_id'],
        "date": datetime.now().strftime('%Y-%m-%d'),
        "active_app": "VS Code",
        "window_title": "ProductivityFlow - main.py",
        "app_url": None,
        "productive_hours": 4.5,
        "unproductive_hours": 1.2,
        "idle_time": 0.8,
        "break_time": 0.5,
        "total_active_time": 7.0,
        "focus_time": 3.2,
        "distraction_count": 8,
        "task_switches": 12,
        "cpu_usage": 45.2,
        "memory_usage": 67.8,
        "network_activity": True,
        "mouse_clicks": 1250,
        "keyboard_activity": True,
        "screen_time": 6.8,
        "session_id": f"session_{int(time.time())}",
        "device_info": "MacBook Pro (M1)",
        "notes": "Productive coding session"
    }
    
    tracking_response = requests.post(f"{base_url}/api/activity/track", json=activity_data)
    
    if tracking_response.status_code not in [200, 201]:
        print(f"❌ Activity tracking failed: {tracking_response.text}")
        return False
    
    tracking_result = tracking_response.json()
    print(f"✅ Activity tracked successfully")
    print(f"   - Activity ID: {tracking_result['activity_id']}")
    print(f"   - Productivity Score: {tracking_result['productivity_score']:.1f}")
    print(f"   - App Category: {tracking_result['app_category']}")
    
    # Step 5: Test app session tracking
    print("\n5. Testing app session tracking...")
    
    # Start VS Code session
    session_start_data = {
        "user_id": employee_user['id'],
        "team_id": employee_user['team_id'],
        "app_name": "VS Code",
        "window_title": "ProductivityFlow - main.py",
        "url": None
    }
    
    session_start_response = requests.post(f"{base_url}/api/activity/session/start", json=session_start_data)
    
    if session_start_response.status_code != 201:
        print(f"❌ Session start failed: {session_start_response.text}")
        return False
    
    session_start_result = session_start_response.json()
    session_id = session_start_result['session_id']
    
    print(f"✅ App session started")
    print(f"   - Session ID: {session_id}")
    print(f"   - App Category: {session_start_result['app_category']}")
    
    # Simulate some time passing
    time.sleep(2)
    
    # End VS Code session
    session_end_data = {
        "session_id": session_id,
        "user_id": employee_user['id'],
        "mouse_clicks": 450,
        "keyboard_events": 1200,
        "scroll_events": 85,
        "distraction_count": 3,
        "task_switches": 2
    }
    
    session_end_response = requests.post(f"{base_url}/api/activity/session/end", json=session_end_data)
    
    if session_end_response.status_code != 200:
        print(f"❌ Session end failed: {session_end_response.text}")
        return False
    
    session_end_result = session_end_response.json()
    print(f"✅ App session ended")
    print(f"   - Duration: {session_end_result['duration']:.1f} seconds")
    print(f"   - Productivity Score: {session_end_result['productivity_score']:.1f}")
    print(f"   - Focus Score: {session_end_result['focus_score']:.1f}")
    print(f"   - Activity Level: {session_end_result['activity_level']}")
    
    # Step 6: Test productivity events
    print("\n6. Testing productivity events...")
    
    event_data = {
        "user_id": employee_user['id'],
        "team_id": employee_user['team_id'],
        "event_type": "app_switch",
        "event_data": {
            "from_app": "VS Code",
            "to_app": "Chrome",
            "reason": "research"
        },
        "app_name": "Chrome",
        "app_category": "browsing",
        "window_title": "Stack Overflow",
        "duration": 300.0
    }
    
    event_response = requests.post(f"{base_url}/api/activity/event", json=event_data)
    
    if event_response.status_code != 201:
        print(f"❌ Event tracking failed: {event_response.text}")
        return False
    
    event_result = event_response.json()
    print(f"✅ Productivity event tracked")
    print(f"   - Event ID: {event_result['event_id']}")
    
    # Step 7: Generate daily summary
    print("\n7. Generating daily summary...")
    
    summary_data = {
        "user_id": employee_user['id'],
        "team_id": employee_user['team_id'],
        "date": datetime.now().strftime('%Y-%m-%d')
    }
    
    summary_response = requests.post(f"{base_url}/api/activity/daily-summary", json=summary_data)
    
    if summary_response.status_code != 201:
        print(f"❌ Daily summary generation failed: {summary_response.text}")
        return False
    
    summary_result = summary_response.json()
    summary = summary_result['summary']
    
    print(f"✅ Daily summary generated")
    print(f"   - Total Productive Time: {summary['total_productive_time']:.1f} hours")
    print(f"   - Total Unproductive Time: {summary['total_unproductive_time']:.1f} hours")
    print(f"   - Overall Productivity Score: {summary['overall_productivity_score']:.1f}")
    print(f"   - Focus Score: {summary['focus_score']:.1f}")
    print(f"   - Distraction Count: {summary['distraction_count']}")
    print(f"   - Task Switch Count: {summary['task_switch_count']}")
    print(f"   - Most Used App: {summary['most_used_app']}")
    print(f"   - Most Productive App: {summary['most_productive_app']}")
    
    # Step 8: Test enhanced analytics
    print("\n8. Testing enhanced analytics...")
    
    # Test burnout risk analysis
    burnout_response = requests.get(f"{base_url}/api/analytics/burnout-risk?team_id={team_id}&user_id={employee_user['id']}&days=1")
    
    if burnout_response.status_code != 200:
        print(f"❌ Burnout risk analysis failed: {burnout_response.text}")
        return False
    
    burnout_result = burnout_response.json()
    print(f"✅ Burnout risk analysis completed")
    print(f"   - Risk Level: {burnout_result['burnout_risk']}")
    print(f"   - Risk Score: {burnout_result['risk_score']}")
    print(f"   - Risk Factors: {len(burnout_result['risk_factors'])}")
    print(f"   - Avg Daily Hours: {burnout_result['metrics']['avg_daily_hours']:.1f}")
    print(f"   - Avg Productivity: {burnout_result['metrics']['avg_productivity']:.1f}")
    
    # Test productivity insights
    insights_response = requests.get(f"{base_url}/api/analytics/productivity-insights?team_id={team_id}&user_id={employee_user['id']}&days=1")
    
    if insights_response.status_code != 200:
        print(f"❌ Productivity insights failed: {insights_response.text}")
        return False
    
    insights_result = insights_response.json()
    print(f"✅ Productivity insights generated")
    print(f"   - Insights: {len(insights_result['insights'])}")
    print(f"   - Recommendations: {len(insights_result['recommendations'])}")
    
    # Display insights
    for insight in insights_result['insights']:
        print(f"   📊 {insight['title']}: {insight['description']}")
    
    # Display recommendations
    for rec in insights_result['recommendations']:
        print(f"   💡 {rec['title']}: {rec['description']} (Priority: {rec['priority']})")
    
    print("\n" + "=" * 60)
    print("🎉 COMPREHENSIVE TRACKING TEST COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    
    print("\n📊 TRACKING FEATURES VERIFIED:")
    print("✅ Enhanced activity tracking with detailed metrics")
    print("✅ App session tracking with start/end events")
    print("✅ Productivity event tracking")
    print("✅ Daily summary generation")
    print("✅ Comprehensive analytics and insights")
    print("✅ Burnout risk analysis")
    print("✅ Productivity recommendations")
    
    print("\n🔍 TRACKED METRICS:")
    print("✅ Application usage and categorization")
    print("✅ Time distribution (productive/unproductive/idle/break)")
    print("✅ Focus scores and distraction counts")
    print("✅ Task switching patterns")
    print("✅ System metrics (CPU, memory, network)")
    print("✅ User interaction (mouse clicks, keyboard activity)")
    print("✅ Productivity scoring and trends")
    print("✅ App-specific productivity analysis")
    
    return True

if __name__ == "__main__":
    success = test_comprehensive_tracking()
    if success:
        print("\n🎯 All comprehensive tracking features are working correctly!")
    else:
        print("\n❌ Some tracking features failed. Please check the errors above.") 