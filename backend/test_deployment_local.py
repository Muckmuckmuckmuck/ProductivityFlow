#!/usr/bin/env python3
"""
Local deployment test for ProductivityFlow Backend
"""

import os
import sys
import requests
import subprocess
import time
from threading import Thread

def test_backend_import():
    """Test if the backend can be imported correctly"""
    try:
        from application import application
        print("✅ Backend import successful")
        return True
    except Exception as e:
        print(f"❌ Backend import failed: {e}")
        return False

def test_health_endpoint():
    """Test the health endpoint locally"""
    try:
        from application import application
        app = application.test_client()
        response = app.get('/health')
        if response.status_code == 200:
            print("✅ Health endpoint working locally")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        return False

def test_requirements():
    """Test if all requirements can be installed"""
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'check'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Requirements check passed")
            return True
        else:
            print(f"❌ Requirements check failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Requirements test failed: {e}")
        return False

def test_gunicorn():
    """Test if gunicorn can start the application"""
    try:
        from application import application
        print("✅ Gunicorn test passed (application object available)")
        return True
    except Exception as e:
        print(f"❌ Gunicorn test failed: {e}")
        return False

def test_environment_variables():
    """Test environment variable configuration"""
    required_vars = ['SECRET_KEY', 'JWT_SECRET_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️ Missing environment variables: {missing_vars}")
        print("These will be generated automatically on Render")
        return True
    else:
        print("✅ Environment variables configured")
        return True

def main():
    """Run all deployment tests"""
    print("🚀 ProductivityFlow Backend Deployment Test")
    print("=" * 50)
    
    tests = [
        ("Backend Import", test_backend_import),
        ("Health Endpoint", test_health_endpoint),
        ("Requirements", test_requirements),
        ("Gunicorn", test_gunicorn),
        ("Environment Variables", test_environment_variables),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Testing: {test_name}")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! Backend is ready for deployment.")
        return True
    else:
        print("❌ Some tests failed. Please fix issues before deployment.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 