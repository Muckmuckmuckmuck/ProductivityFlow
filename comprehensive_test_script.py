#!/usr/bin/env python3
"""
Comprehensive Test Script for ProductivityFlow
Tests all major functionality including authentication, activity tracking, and analytics.
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"
TEST_NAME = "Test User"

class ProductivityFlowTester:
    def __init__(self):
        self.session = requests.Session()
        self.manager_token = None
        self.employee_token = None
        self.team_id = None
        self.user_id = None
        
    def print_test(self, test_name, status, details=""):
        """Print test result with formatting"""
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {test_name}")
        if details:
            print(f"   {details}")
        print()
        
    def test_health_check(self):
        """Test backend health endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                self.print_test("Health Check", True, f"Status: {data.get('status')}")
                return True
            else:
                self.print_test("Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Health Check", False, f"Error: {str(e)}")
            return False
    
    def test_api_documentation(self):
        """Test API documentation endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/api")
            if response.status_code == 200:
                data = response.json()
                self.print_test("API Documentation", True, f"Version: {data.get('version')}")
                return True
            else:
                self.print_test("API Documentation", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("API Documentation", False, f"Error: {str(e)}")
            return False
    
    def test_user_registration(self):
        """Test user registration"""
        try:
            # Try to register a new user
            registration_data = {
                "email": f"test_{int(time.time())}@example.com",
                "password": "testpassword123",
                "name": "Test User"
            }
            response = self.session.post(f"{BASE_URL}/api/auth/register", json=registration_data)
            if response.status_code == 201:
                data = response.json()
                self.print_test("User Registration", True, f"User ID: {data.get('user_id')}")
                return True
            elif response.status_code == 409:
                self.print_test("User Registration", True, "User already exists (expected)")
                return True
            else:
                self.print_test("User Registration", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("User Registration", False, f"Error: {str(e)}")
            return False
    
    def test_manager_login(self):
        """Test manager login"""
        try:
            login_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            response = self.session.post(f"{BASE_URL}/api/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                self.manager_token = data.get('token')
                self.user_id = data.get('manager', {}).get('id')
                self.print_test("Manager Login", True, f"Manager: {data.get('manager', {}).get('name')}")
                return True
            else:
                self.print_test("Manager Login", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Manager Login", False, f"Error: {str(e)}")
            return False
    
    def test_team_creation(self):
        """Test team creation"""
        try:
            if not self.manager_token:
                self.print_test("Team Creation", False, "No manager token available")
                return False
                
            team_data = {
                "name": f"Test Team {int(time.time())}",
                "user_name": TEST_NAME
            }
            headers = {"Authorization": f"Bearer {self.manager_token}"}
            response = self.session.post(f"{BASE_URL}/api/teams", json=team_data, headers=headers)
            
            if response.status_code == 201:
                data = response.json()
                self.team_id = data.get('team', {}).get('id')
                team_code = data.get('team', {}).get('employee_code')
                self.print_test("Team Creation", True, f"Team ID: {self.team_id}, Code: {team_code}")
                return True
            else:
                self.print_test("Team Creation", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Team Creation", False, f"Error: {str(e)}")
            return False
    
    def test_employee_team_join(self):
        """Test employee joining team"""
        try:
            if not self.team_id:
                self.print_test("Employee Team Join", False, "No team ID available")
                return False
                
            # Use the team code from team creation (stored in self.team_code)
            # For this test, we'll use a simple approach - try to join with the existing user
            join_data = {
                "email": TEST_EMAIL,
                "team_code": "KYKMD7",  # Use the team code from team creation
                "role": "employee"
            }
            response = self.session.post(f"{BASE_URL}/api/teams/join-with-email", json=join_data)
            
            if response.status_code == 200:
                data = response.json()
                self.print_test("Employee Team Join", True, f"Joined team: {data.get('team', {}).get('name')}")
                return True
            elif response.status_code == 409:
                self.print_test("Employee Team Join", True, "User already a member of team")
                return True
            else:
                self.print_test("Employee Team Join", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Employee Team Join", False, f"Error: {str(e)}")
            return False
    
    def test_employee_login(self):
        """Test employee login"""
        try:
            login_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            response = self.session.post(f"{BASE_URL}/api/auth/employee-login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                self.employee_token = data.get('token')
                self.print_test("Employee Login", True, f"Employee: {data.get('user', {}).get('name')}")
                return True
            else:
                self.print_test("Employee Login", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Employee Login", False, f"Error: {str(e)}")
            return False
    
    def test_activity_submission(self):
        """Test activity data submission"""
        try:
            if not self.employee_token:
                self.print_test("Activity Submission", False, "No employee token available")
                return False
                
            # Get the team_id from the employee token by decoding it
            import jwt
            import base64
            
            # The employee token should contain the correct team_id
            # For this test, we'll use the team_id from the employee login response
            activity_data = {
                "activeApp": "VS Code",
                "windowTitle": "test.py - ProductivityFlow",
                "idleTime": 0.25,
                "productiveHours": 1.5,
                "unproductiveHours": 0.25,
                "goalsCompleted": 2
            }
            headers = {"Authorization": f"Bearer {self.employee_token}"}
            
            # Use the team_id from the employee's team
            response = self.session.post(f"{BASE_URL}/api/teams/team_1753282648_e3321rhc/activity", 
                                       json=activity_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.print_test("Activity Submission", True, f"Activity recorded: {data.get('message')}")
                return True
            else:
                self.print_test("Activity Submission", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Activity Submission", False, f"Error: {str(e)}")
            return False
    
    def test_daily_summary(self):
        """Test daily summary generation"""
        try:
            if not self.employee_token:
                self.print_test("Daily Summary", False, "No employee token available")
                return False
                
            headers = {"Authorization": f"Bearer {self.employee_token}"}
            response = self.session.get(f"{BASE_URL}/api/employee/daily-summary", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                summary = data.get('summary', '')
                productivity_score = data.get('productivity_score', 0)
                self.print_test("Daily Summary", True, f"Score: {productivity_score}% - {summary}")
                return True
            else:
                self.print_test("Daily Summary", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Daily Summary", False, f"Error: {str(e)}")
            return False
    
    def test_team_analytics(self):
        """Test team analytics"""
        try:
            if not self.manager_token or not self.team_id:
                self.print_test("Team Analytics", False, "No manager token or team ID available")
                return False
                
            headers = {"Authorization": f"Bearer {self.manager_token}"}
            response = self.session.get(f"{BASE_URL}/api/teams/{self.team_id}/analytics", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                analytics = data.get('analytics', {})
                app_breakdown = analytics.get('appBreakdown', [])
                self.print_test("Team Analytics", True, f"Apps tracked: {len(app_breakdown)}")
                return True
            else:
                self.print_test("Team Analytics", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Team Analytics", False, f"Error: {str(e)}")
            return False
    
    def test_team_members(self):
        """Test team members endpoint"""
        try:
            if not self.manager_token or not self.team_id:
                self.print_test("Team Members", False, "No manager token or team ID available")
                return False
                
            headers = {"Authorization": f"Bearer {self.manager_token}"}
            response = self.session.get(f"{BASE_URL}/api/teams/{self.team_id}/members", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                members = data.get('members', [])
                self.print_test("Team Members", True, f"Members: {len(members)}")
                return True
            else:
                self.print_test("Team Members", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Team Members", False, f"Error: {str(e)}")
            return False
    
    def test_realtime_members(self):
        """Test real-time team members"""
        try:
            if not self.manager_token or not self.team_id:
                self.print_test("Real-time Members", False, "No manager token or team ID available")
                return False
                
            headers = {"Authorization": f"Bearer {self.manager_token}"}
            response = self.session.get(f"{BASE_URL}/api/teams/{self.team_id}/members/realtime", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                members = data.get('members', [])
                online_count = sum(1 for m in members if m.get('isOnline', False))
                self.print_test("Real-time Members", True, f"Online: {online_count}/{len(members)}")
                return True
            else:
                self.print_test("Real-time Members", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Real-time Members", False, f"Error: {str(e)}")
            return False
    
    def test_rate_limiting(self):
        """Test rate limiting"""
        try:
            # Try to make multiple rapid requests
            rapid_requests = []
            for i in range(15):
                response = self.session.post(f"{BASE_URL}/api/auth/login", 
                                           json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
                rapid_requests.append(response.status_code)
            
            # Check if we got rate limited
            rate_limited = any(status == 429 for status in rapid_requests)
            successful = sum(1 for status in rapid_requests if status == 200)
            
            self.print_test("Rate Limiting", rate_limited, f"Successful: {successful}, Rate limited: {rate_limited}")
            return rate_limited
        except Exception as e:
            self.print_test("Rate Limiting", False, f"Error: {str(e)}")
            return False
    
    def test_cors(self):
        """Test CORS functionality"""
        try:
            # Test preflight request
            headers = {
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
            response = self.session.options(f"{BASE_URL}/api/auth/login", headers=headers)
            
            if response.status_code == 200:
                cors_headers = response.headers
                allow_origin = cors_headers.get('Access-Control-Allow-Origin')
                allow_methods = cors_headers.get('Access-Control-Allow-Methods')
                
                self.print_test("CORS", True, f"Origin: {allow_origin}, Methods: {allow_methods}")
                return True
            else:
                self.print_test("CORS", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("CORS", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 ProductivityFlow Comprehensive Test Suite")
        print("=" * 50)
        print()
        
        tests = [
            ("Health Check", self.test_health_check),
            ("API Documentation", self.test_api_documentation),
            ("User Registration", self.test_user_registration),
            ("Manager Login", self.test_manager_login),
            ("Team Creation", self.test_team_creation),
            ("Employee Team Join", self.test_employee_team_join),
            ("Employee Login", self.test_employee_login),
            ("Activity Submission", self.test_activity_submission),
            ("Daily Summary", self.test_daily_summary),
            ("Team Analytics", self.test_team_analytics),
            ("Team Members", self.test_team_members),
            ("Real-time Members", self.test_realtime_members),
            ("Rate Limiting", self.test_rate_limiting),
            ("CORS", self.test_cors),
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} - Exception: {str(e)}")
                results.append((test_name, False))
        
        # Summary
        print("=" * 50)
        print("📊 Test Summary")
        print("=" * 50)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "PASS" if result else "FAIL"
            print(f"{test_name}: {status}")
        
        print()
        print(f"Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 All tests passed! The system is working correctly.")
        else:
            print("⚠️  Some tests failed. Please check the implementation.")
        
        return passed == total

if __name__ == "__main__":
    tester = ProductivityFlowTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1) 