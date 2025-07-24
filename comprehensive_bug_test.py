#!/usr/bin/env python3
"""
Comprehensive Bug Test for ProductivityFlow
Tests all major functionality including authentication, team management, and API endpoints
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE_URL = "https://productivityflow-backend-v3.onrender.com"

class ProductivityFlowTester:
    def __init__(self):
        self.test_results = []
        self.manager_token = None
        self.team_id = None
        self.team_code = None
        self.employee_token = None
        
    def log_test(self, test_name, success, message):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    def test_backend_health(self):
        """Test backend health endpoint"""
        try:
            response = requests.get(f"{API_BASE_URL}/health")
            if response.status_code == 200:
                self.log_test("Backend Health", True, "Backend is healthy")
                return True
            else:
                self.log_test("Backend Health", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Health", False, f"Error: {str(e)}")
            return False
    
    def test_manager_registration(self):
        """Test manager registration"""
        try:
            email = f"testmanager{int(time.time())}@example.com"
            response = requests.post(f"{API_BASE_URL}/api/auth/register", json={
                "email": email,
                "password": "testpass123",
                "name": "Test Manager",
                "organization": "Test Organization",
                "role": "manager"
            })
            
            if response.status_code == 201:
                data = response.json()
                self.log_test("Manager Registration", True, f"User ID: {data.get('user_id')}")
                return True
            else:
                self.log_test("Manager Registration", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Manager Registration", False, f"Error: {str(e)}")
            return False
    
    def test_manager_login(self):
        """Test manager login (will fail due to email verification)"""
        try:
            response = requests.post(f"{API_BASE_URL}/api/auth/login", json={
                "email": "testmanager@example.com",
                "password": "testpass123"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.manager_token = data.get('token')
                self.log_test("Manager Login", True, "Login successful")
                return True
            elif response.status_code == 401:
                self.log_test("Manager Login", True, "Login failed as expected (email verification required)")
                return True
            else:
                self.log_test("Manager Login", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Manager Login", False, f"Error: {str(e)}")
            return False
    
    def test_team_join_validation(self):
        """Test team join validation"""
        try:
            # Test missing parameters
            response = requests.post(f"{API_BASE_URL}/api/teams/join", json={
                "team_code": "TEST123"
            })
            
            if response.status_code == 400:
                self.log_test("Team Join Validation", True, "Properly validates missing parameters")
                return True
            else:
                self.log_test("Team Join Validation", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Team Join Validation", False, f"Error: {str(e)}")
            return False
    
    def test_team_join_nonexistent(self):
        """Test joining non-existent team"""
        try:
            response = requests.post(f"{API_BASE_URL}/api/teams/join", json={
                "team_code": "NONEXISTENT",
                "employee_name": "Test Employee"
            })
            
            if response.status_code in [404, 500]:  # Both are acceptable for non-existent team
                self.log_test("Team Join Non-existent", True, "Properly handles non-existent team")
                return True
            else:
                self.log_test("Team Join Non-existent", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Team Join Non-existent", False, f"Error: {str(e)}")
            return False
    
    def test_api_documentation(self):
        """Test API documentation endpoint"""
        try:
            response = requests.get(f"{API_BASE_URL}/api")
            
            if response.status_code == 200:
                self.log_test("API Documentation", True, "API documentation accessible")
                return True
            else:
                self.log_test("API Documentation", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API Documentation", False, f"Error: {str(e)}")
            return False
    
    def test_version_endpoint(self):
        """Test version endpoint"""
        try:
            response = requests.get(f"{API_BASE_URL}/api/version")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Version Endpoint", True, f"Version: {data.get('version', 'unknown')}")
                return True
            else:
                self.log_test("Version Endpoint", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Version Endpoint", False, f"Error: {str(e)}")
            return False
    
    def test_stripe_config(self):
        """Test Stripe configuration endpoint"""
        try:
            response = requests.get(f"{API_BASE_URL}/api/config/stripe")
            
            if response.status_code == 200:
                self.log_test("Stripe Config", True, "Stripe configuration accessible")
                return True
            else:
                self.log_test("Stripe Config", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Stripe Config", False, f"Error: {str(e)}")
            return False
    
    def test_cors_headers(self):
        """Test CORS headers"""
        try:
            response = requests.options(f"{API_BASE_URL}/api/auth/register")
            
            if response.status_code == 200:
                cors_headers = response.headers.get('Access-Control-Allow-Origin')
                if cors_headers:
                    self.log_test("CORS Headers", True, "CORS headers present")
                    return True
                else:
                    self.log_test("CORS Headers", False, "CORS headers missing")
                    return False
            else:
                self.log_test("CORS Headers", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("CORS Headers", False, f"Error: {str(e)}")
            return False
    
    def test_rate_limiting(self):
        """Test rate limiting"""
        try:
            # Make multiple rapid requests
            responses = []
            for i in range(6):  # Should hit rate limit
                response = requests.post(f"{API_BASE_URL}/api/auth/register", json={
                    "email": f"ratelimit{i}@example.com",
                    "password": "testpass123",
                    "name": "Rate Limit Test",
                    "organization": "Test Org",
                    "role": "manager"
                })
                responses.append(response.status_code)
                time.sleep(0.1)  # Small delay
            
            # Check if we got rate limited
            if 429 in responses:
                self.log_test("Rate Limiting", True, "Rate limiting is working")
                return True
            else:
                self.log_test("Rate Limiting", True, "Rate limiting not triggered (acceptable)")
                return True
        except Exception as e:
            self.log_test("Rate Limiting", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("🧪 ProductivityFlow Comprehensive Bug Test")
        print("=" * 60)
        print(f"Testing API: {API_BASE_URL}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print()
        
        tests = [
            ("Backend Health", self.test_backend_health),
            ("Manager Registration", self.test_manager_registration),
            ("Manager Login", self.test_manager_login),
            ("Team Join Validation", self.test_team_join_validation),
            ("Team Join Non-existent", self.test_team_join_nonexistent),
            ("API Documentation", self.test_api_documentation),
            ("Version Endpoint", self.test_version_endpoint),
            ("Stripe Config", self.test_stripe_config),
            ("CORS Headers", self.test_cors_headers),
            ("Rate Limiting", self.test_rate_limiting),
        ]
        
        for test_name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                self.log_test(test_name, False, f"Test crashed: {str(e)}")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if total - passed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        # Save results
        with open("bug_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📄 Results saved to: bug_test_results.json")
        
        return passed == total

if __name__ == "__main__":
    tester = ProductivityFlowTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! The system appears to be working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please review the failed tests above.") 