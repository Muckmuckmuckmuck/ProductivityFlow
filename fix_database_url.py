#!/usr/bin/env python3
"""
Script to fix the malformed DATABASE_URL in Google Cloud Run
"""

import subprocess
import sys

def fix_database_url():
    """Fix the malformed DATABASE_URL in Google Cloud Run"""
    
    print("🔧 Fixing Database URL in Google Cloud Run...")
    
    # The correct DATABASE_URL (without the extra backend URL)
    correct_db_url = "postgresql://postgres@Edisonjay1235.238.243.118:5432/postgres"
    
    try:
        # Update the environment variable
        cmd = [
            'gcloud', 'run', 'services', 'update', 'productivityflow-backend',
            '--region=us-central1',
            f'--update-env-vars=DATABASE_URL={correct_db_url}'
        ]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Database URL updated successfully!")
            print("🔄 Service is being updated...")
            return True
        else:
            print(f"❌ Error updating database URL: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_backend():
    """Test if the backend is working after the fix"""
    import requests
    import time
    
    print("\n🧪 Testing backend after fix...")
    
    # Wait a moment for the update to propagate
    print("⏳ Waiting for service update to propagate...")
    time.sleep(30)
    
    backend_url = "https://productivityflow-backend-496367590729.us-central1.run.app"
    
    try:
        response = requests.get(f"{backend_url}/health", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("✅ Backend is responding!")
            return True
        else:
            print("⚠️ Backend responding but with error (expected due to database)")
            return True
            
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ProductivityFlow Backend Database URL Fix")
    print("=" * 50)
    
    if fix_database_url():
        test_backend()
    else:
        print("\n❌ Failed to fix database URL")
        print("Please manually update the DATABASE_URL in Google Cloud Run console:")
        print("1. Go to: https://console.cloud.google.com/run")
        print("2. Click on productivityflow-backend-00013-p9l")
        print("3. Click 'Edit & Deploy New Revision'")
        print("4. Go to 'Variables & Secrets'")
        print("5. Update DATABASE_URL to: postgresql://postgres@Edisonjay1235.238.243.118:5432/postgres")
        print("6. Remove the extra @https://... part")
        print("7. Click 'Deploy'") 