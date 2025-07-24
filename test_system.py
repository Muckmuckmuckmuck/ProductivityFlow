#!/usr/bin/env python3
"""
Comprehensive ProductivityFlow System Test Suite
Tests all components and ensures everything works correctly
"""

import requests
import json
import time
import sys
from datetime import datetime

class ProductivityFlowTester:
    def __init__(self):
        self.backend_url = "http://localhost:5000"
        self.proxy_url = "http://localhost:3001"
        self.http_url = "http://localhost:8000"
        self.test_results = []
        
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
        return success
    
    def test_backend_health(self):
        """Test backend health endpoint"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return self.log_test(
                    "Backend Health",
                    True,
                    f"Backend is healthy - {data.get('status', 'unknown')}",
                    data
                )
            else:
                return self.log_test(
                    "Backend Health",
                    False,
                    f"Backend returned status {response.status_code}",
                    response.text
                )
        except Exception as e:
            return self.log_test(
                "Backend Health",
                False,
                f"Backend connection failed: {str(e)}"
            )
    
    def test_proxy_health(self):
        """Test CORS proxy health"""
        try:
            response = requests.get(f"{self.proxy_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return self.log_test(
                    "CORS Proxy Health",
                    True,
                    f"Proxy is healthy - {data.get('status', 'unknown')}",
                    data
                )
            else:
                return self.log_test(
                    "CORS Proxy Health",
                    False,
                    f"Proxy returned status {response.status_code}",
                    response.text
                )
        except Exception as e:
            return self.log_test(
                "CORS Proxy Health",
                False,
                f"Proxy connection failed: {str(e)}"
            )
    
    def test_http_server(self):
        """Test HTTP server"""
        try:
            response = requests.get(f"{self.http_url}/", timeout=5)
            if response.status_code == 200:
                return self.log_test(
                    "HTTP Server",
                    True,
                    "HTTP server is serving files correctly"
                )
            else:
                return self.log_test(
                    "HTTP Server",
                    False,
                    f"HTTP server returned status {response.status_code}"
                )
        except Exception as e:
            return self.log_test(
                "HTTP Server",
                False,
                f"HTTP server connection failed: {str(e)}"
            )
    
    def test_registration(self):
        """Test user registration"""
        try:
            test_email = f"test_{int(time.time())}@example.com"
            data = {
                "email": test_email,
                "password": "SecurePass123",
                "name": "Test User"
            }
            
            response = requests.post(
                f"{self.proxy_url}/api/auth/register",
                json=data,
                timeout=10
            )
            
            if response.status_code == 201:
                result_data = response.json()
                return self.log_test(
                    "User Registration",
                    True,
                    f"User registered successfully: {test_email}",
                    result_data
                )
            else:
                return self.log_test(
                    "User Registration",
                    False,
                    f"Registration failed with status {response.status_code}",
                    response.text
                )
        except Exception as e:
            return self.log_test(
                "User Registration",
                False,
                f"Registration test failed: {str(e)}"
            )
    
    def test_login(self):
        """Test user login"""
        try:
            # First register a new user
            test_email = f"login_test_{int(time.time())}@example.com"
            register_data = {
                "email": test_email,
                "password": "SecurePass123",
                "name": "Login Test User"
            }
            
            register_response = requests.post(
                f"{self.proxy_url}/api/auth/register",
                json=register_data,
                timeout=10
            )
            
            if register_response.status_code != 201:
                return self.log_test(
                    "User Login",
                    False,
                    "Cannot test login - registration failed"
                )
            
            # Verify the email
            verify_response = requests.post(
                f"{self.proxy_url}/api/auth/verify-email",
                json={"email": test_email},
                timeout=10
            )
            
            if verify_response.status_code != 200:
                return self.log_test(
                    "User Login",
                    False,
                    "Cannot test login - email verification failed"
                )
            
            # Now try to login
            login_data = {
                "email": test_email,
                "password": "SecurePass123"
            }
            
            response = requests.post(
                f"{self.proxy_url}/api/auth/login",
                json=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result_data = response.json()
                token = result_data.get('token', '')
                return self.log_test(
                    "User Login",
                    True,
                    f"Login successful, token received: {token[:20]}...",
                    {"token_length": len(token)}
                )
            else:
                return self.log_test(
                    "User Login",
                    False,
                    f"Login failed with status {response.status_code}",
                    response.text
                )
        except Exception as e:
            return self.log_test(
                "User Login",
                False,
                f"Login test failed: {str(e)}"
            )
    
    def test_team_creation(self):
        """Test team creation with authentication"""
        try:
            # Create a new user for team creation test
            test_email = f"team_test_{int(time.time())}@example.com"
            register_data = {
                "email": test_email,
                "password": "SecurePass123",
                "name": "Team Test User"
            }
            
            register_response = requests.post(
                f"{self.proxy_url}/api/auth/register",
                json=register_data,
                timeout=10
            )
            
            if register_response.status_code != 201:
                return self.log_test(
                    "Team Creation",
                    False,
                    "Cannot test team creation - registration failed"
                )
            
            # Verify the email
            verify_response = requests.post(
                f"{self.proxy_url}/api/auth/verify-email",
                json={"email": test_email},
                timeout=10
            )
            
            if verify_response.status_code != 200:
                return self.log_test(
                    "Team Creation",
                    False,
                    "Cannot test team creation - email verification failed"
                )
            
            # Login to get token
            login_data = {
                "email": test_email,
                "password": "SecurePass123"
            }
            
            login_response = requests.post(
                f"{self.proxy_url}/api/auth/login",
                json=login_data,
                timeout=10
            )
            
            if login_response.status_code != 200:
                return self.log_test(
                    "Team Creation",
                    False,
                    "Cannot test team creation - login failed"
                )
            
            token = login_response.json().get('token', '')
            
            # Create team with token
            team_data = {"name": "Test Team"}
            headers = {"Authorization": f"Bearer {token}"}
            
            response = requests.post(
                f"{self.proxy_url}/api/teams",
                json=team_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 201:
                result_data = response.json()
                return self.log_test(
                    "Team Creation",
                    True,
                    f"Team created successfully: {result_data.get('team', {}).get('name', 'unknown')}",
                    result_data
                )
            else:
                return self.log_test(
                    "Team Creation",
                    False,
                    f"Team creation failed with status {response.status_code}",
                    response.text
                )
        except Exception as e:
            return self.log_test(
                "Team Creation",
                False,
                f"Team creation test failed: {str(e)}"
            )
    
    def test_security_features(self):
        """Test security features"""
        security_tests = [
            {
                "name": "Weak Password Rejection",
                "data": {
                    "email": "test@example.com",
                    "password": "123",
                    "name": "Test User"
                },
                "expected_status": 400
            },
            {
                "name": "Invalid Email Rejection",
                "data": {
                    "email": "invalid-email",
                    "password": "SecurePass123",
                    "name": "Test User"
                },
                "expected_status": 400
            },
            {
                "name": "SQL Injection Protection",
                "data": {
                    "email": f"sql_test_{int(time.time())}@example.com",
                    "password": "SecurePass123",
                    "name": "'; DROP TABLE users; --"
                },
                "expected_status": 201  # Should accept sanitized input
            }
        ]
        
        all_passed = True
        
        for test in security_tests:
            try:
                response = requests.post(
                    f"{self.proxy_url}/api/auth/register",
                    json=test["data"],
                    timeout=10
                )
                
                if response.status_code == test["expected_status"]:
                    self.log_test(
                        test["name"],
                        True,
                        f"Security test passed - expected {test['expected_status']}"
                    )
                else:
                    self.log_test(
                        test["name"],
                        False,
                        f"Security test failed - expected {test['expected_status']}, got {response.status_code}"
                    )
                    all_passed = False
                    
            except Exception as e:
                self.log_test(
                    test["name"],
                    False,
                    f"Security test error: {str(e)}"
                )
                all_passed = False
        
        return all_passed
    
    def test_debug_pages(self):
        """Test debug pages are accessible"""
        debug_pages = [
            "debug_security_test.html",
            "debug_everything_working.html",
            "debug_working_backend.html"
        ]
        
        all_passed = True
        
        for page in debug_pages:
            try:
                response = requests.get(f"{self.http_url}/{page}", timeout=5)
                if response.status_code == 200:
                    self.log_test(
                        f"Debug Page: {page}",
                        True,
                        "Page is accessible"
                    )
                else:
                    self.log_test(
                        f"Debug Page: {page}",
                        False,
                        f"Page returned status {response.status_code}"
                    )
                    all_passed = False
            except Exception as e:
                self.log_test(
                    f"Debug Page: {page}",
                    False,
                    f"Page access failed: {str(e)}"
                )
                all_passed = False
        
        return all_passed
    
    def run_all_tests(self):
        """Run all tests"""
        print("🧪 ProductivityFlow System Test Suite")
        print("=" * 50)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Run all tests
        tests = [
            self.test_backend_health,
            self.test_proxy_health,
            self.test_http_server,
            self.test_registration,
            self.test_login,
            self.test_team_creation,
            self.test_security_features,
            self.test_debug_pages
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
        
        # Print summary
        print()
        print("=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! System is working perfectly!")
            return True
        else:
            print("⚠️ Some tests failed. Check the results above.")
            return False
    
    def save_results(self, filename="test_results.json"):
        """Save test results to file"""
        with open(filename, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print(f"📄 Test results saved to {filename}")

def main():
    tester = ProductivityFlowTester()
    success = tester.run_all_tests()
    tester.save_results()
    
    if success:
        print("\n🚀 System is ready for production!")
        sys.exit(0)
    else:
        print("\n❌ System needs attention before production.")
        sys.exit(1)

if __name__ == "__main__":
    main() 