#!/usr/bin/env python3
"""
Script to start the ProductivityFlow backend locally for testing
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import psycopg2
        import bcrypt
        import jwt
        print("✅ All required dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r backend/requirements.txt")
        return False

def start_backend():
    """Start the backend server"""
    backend_dir = Path("backend")
    
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Set environment variables for local development
    env = os.environ.copy()
    env['FLASK_ENV'] = 'development'
    env['PORT'] = '5000'
    
    # Check if we have a .env file
    if Path('.env').exists():
        print("✅ Found .env file")
    else:
        print("⚠️ No .env file found - using default settings")
    
    print("🚀 Starting local backend server...")
    print("📍 Backend will be available at: http://localhost:5000")
    print("🔧 API endpoints will be at: http://localhost:5000/api/")
    print("📊 Health check: http://localhost:5000/api/health")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        # Start the backend using the simple startup script
        subprocess.run([sys.executable, "start_simple.py"], env=env)
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped")
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return False
    
    return True

def test_backend():
    """Test if the backend is running"""
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running and responding")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend is not responding: {e}")
        return False

if __name__ == "__main__":
    print("🔧 ProductivityFlow Local Backend Starter")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Start backend
    start_backend() 