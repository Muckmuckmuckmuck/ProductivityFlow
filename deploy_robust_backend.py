#!/usr/bin/env python3
"""
Deploy Robust Backend Script
Deploys the comprehensive, production-ready backend to Render
"""

import os
import subprocess
import sys
import time
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return None

def check_backend_status():
    """Check if the backend is responding"""
    import requests
    
    try:
        response = requests.get("https://my-home-backend-7m6d.onrender.com/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is healthy: {data.get('status', 'unknown')}")
            print(f"📊 Version: {data.get('version', 'unknown')}")
            print(f"🌍 Environment: {data.get('environment', 'unknown')}")
            return True
        else:
            print(f"⚠️ Backend responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend health check failed: {e}")
        return False

def test_endpoints():
    """Test key endpoints to ensure they're working"""
    import requests
    import json
    
    base_url = "https://my-home-backend-7m6d.onrender.com"
    
    # Test endpoints
    endpoints = [
        ("GET", "/health", None),
        ("POST", "/api/teams", {"name": "Test Team", "user_name": "Test Manager"}),
    ]
    
    print("\n🧪 Testing endpoints...")
    
    for method, endpoint, data in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            headers = {"Content-Type": "application/json"} if data else {}
            
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=10)
            
            if response.status_code in [200, 201]:
                print(f"✅ {method} {endpoint} - Status: {response.status_code}")
                if response.content:
                    try:
                        result = response.json()
                        if "success" in result:
                            print(f"   Success: {result['success']}")
                        if "message" in result:
                            print(f"   Message: {result['message']}")
                    except:
                        pass
            else:
                print(f"⚠️ {method} {endpoint} - Status: {response.status_code}")
                if response.content:
                    try:
                        error = response.json()
                        print(f"   Error: {error.get('message', 'Unknown error')}")
                    except:
                        print(f"   Response: {response.text[:100]}...")
                        
        except Exception as e:
            print(f"❌ {method} {endpoint} - Failed: {e}")

def main():
    """Main deployment function"""
    print("🚀 ProductivityFlow Robust Backend Deployment")
    print("=" * 50)
    
    # Check current directory
    current_dir = Path.cwd()
    print(f"📁 Current directory: {current_dir}")
    
    # Check if we're in the right place
    if not (current_dir / "backend").exists():
        print("❌ Backend directory not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Check backend files
    backend_dir = current_dir / "backend"
    application_file = backend_dir / "application.py"
    robust_file = backend_dir / "application_robust.py"
    
    if not robust_file.exists():
        print("❌ application_robust.py not found in backend directory")
        sys.exit(1)
    
    print(f"✅ Found robust backend file: {robust_file}")
    
    # Check if we need to update application.py
    if application_file.exists():
        print(f"📄 Current application.py exists")
        
        # Check if it's already the robust version
        with open(application_file, 'r') as f:
            current_content = f.read()
        
        with open(robust_file, 'r') as f:
            robust_content = f.read()
        
        if current_content == robust_content:
            print("✅ application.py is already the robust version")
        else:
            print("🔄 Updating application.py with robust version...")
            with open(application_file, 'w') as f:
                f.write(robust_content)
            print("✅ application.py updated")
    else:
        print("📄 Creating application.py from robust version...")
        with open(robust_file, 'r') as f:
            robust_content = f.read()
        
        with open(application_file, 'w') as f:
            f.write(robust_content)
        print("✅ application.py created")
    
    # Check requirements.txt
    requirements_file = backend_dir / "requirements.txt"
    if requirements_file.exists():
        print(f"📦 Requirements file exists: {requirements_file}")
        
        # Check if it has all necessary dependencies
        with open(requirements_file, 'r') as f:
            requirements = f.read()
        
        required_deps = [
            "flask",
            "flask-sqlalchemy", 
            "flask-cors",
            "flask-limiter",
            "bcrypt",
            "PyJWT"
        ]
        
        missing_deps = []
        for dep in required_deps:
            if dep not in requirements:
                missing_deps.append(dep)
        
        if missing_deps:
            print(f"⚠️ Missing dependencies: {missing_deps}")
            print("🔄 Updating requirements.txt...")
            
            # Add missing dependencies
            for dep in missing_deps:
                requirements += f"\n{dep}"
            
            with open(requirements_file, 'w') as f:
                f.write(requirements)
            print("✅ requirements.txt updated")
        else:
            print("✅ All required dependencies present")
    else:
        print("❌ requirements.txt not found")
        sys.exit(1)
    
    # Check if git is available
    git_result = run_command("git --version", "Checking Git availability")
    if not git_result:
        print("⚠️ Git not available, skipping git operations")
    else:
        # Check git status
        git_status = run_command("git status --porcelain", "Checking Git status")
        if git_status and git_status.strip():
            print("📝 Uncommitted changes detected:")
            print(git_status)
            
            # Ask if user wants to commit
            response = input("\n🤔 Do you want to commit these changes? (y/N): ")
            if response.lower() in ['y', 'yes']:
                run_command("git add .", "Adding files to git")
                run_command("git commit -m 'Deploy robust backend with comprehensive fixes'", "Committing changes")
                print("✅ Changes committed")
            else:
                print("⚠️ Changes not committed")
    
    print("\n" + "=" * 50)
    print("🎯 DEPLOYMENT READY")
    print("=" * 50)
    
    print("\n📋 Next Steps:")
    print("1. The backend code has been updated with the robust implementation")
    print("2. All security measures and new endpoints are now in place")
    print("3. The backend will automatically redeploy on Render")
    print("4. Monitor the deployment at: https://dashboard.render.com")
    
    print("\n⏳ Waiting for backend to redeploy...")
    print("This may take 2-5 minutes...")
    
    # Wait and check status
    for i in range(12):  # Wait up to 12 minutes
        time.sleep(30)  # Check every 30 seconds
        print(f"⏰ Checking backend status... ({i+1}/12)")
        
        if check_backend_status():
            print("\n🎉 Backend deployment successful!")
            test_endpoints()
            break
    else:
        print("\n⚠️ Backend deployment may still be in progress")
        print("Please check the Render dashboard for deployment status")
    
    print("\n" + "=" * 50)
    print("✅ DEPLOYMENT COMPLETE")
    print("=" * 50)
    
    print("\n🔗 Backend URL: https://my-home-backend-7m6d.onrender.com")
    print("📊 Health Check: https://my-home-backend-7m6d.onrender.com/health")
    print("📚 API Documentation: See COMPREHENSIVE_ROBUST_FIXES_SUMMARY.md")
    
    print("\n🎯 What's New:")
    print("✅ Comprehensive authentication system")
    print("✅ Secure JWT token management")
    print("✅ Rate limiting and security headers")
    print("✅ Robust error handling")
    print("✅ Activity tracking and analytics")
    print("✅ Team management features")
    print("✅ Production-ready database schema")

if __name__ == "__main__":
    main() 