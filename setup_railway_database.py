#!/usr/bin/env python3
"""
Setup Railway PostgreSQL Database for Google Cloud Run Backend
"""

import os
import subprocess
import sys

def check_railway_cli():
    """Check if Railway CLI is installed"""
    try:
        result = subprocess.run(['railway', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Railway CLI is installed")
            return True
        else:
            print("❌ Railway CLI is not installed")
            return False
    except FileNotFoundError:
        print("❌ Railway CLI is not installed")
        return False

def setup_railway_project():
    """Setup Railway project and PostgreSQL database"""
    print("🔧 Setting up Railway PostgreSQL database...")
    print("=============================================")
    
    # Check if Railway CLI is installed
    if not check_railway_cli():
        print("\n📋 To install Railway CLI:")
        print("1. Visit: https://railway.app/cli")
        print("2. Follow the installation instructions")
        print("3. Run: railway login")
        print("4. Then run this script again")
        return None
    
    try:
        # Create new Railway project
        print("🚀 Creating new Railway project...")
        result = subprocess.run(['railway', 'init'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Failed to create Railway project: {result.stderr}")
            return None
        
        # Add PostgreSQL service
        print("🗄️ Adding PostgreSQL service...")
        result = subprocess.run(['railway', 'add'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Failed to add PostgreSQL service: {result.stderr}")
            return None
        
        # Get the DATABASE_URL
        print("🔗 Getting DATABASE_URL...")
        result = subprocess.run(['railway', 'variables'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Railway project setup complete!")
            print("\n📋 Next steps:")
            print("1. Copy the DATABASE_URL from Railway dashboard")
            print("2. Update Google Cloud Run with the new DATABASE_URL")
            print("3. Test the connection")
            return True
        else:
            print(f"❌ Failed to get variables: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error setting up Railway: {e}")
        return None

def update_cloud_run_database():
    """Update Google Cloud Run with Railway DATABASE_URL"""
    print("\n🔧 Updating Google Cloud Run with Railway database...")
    print("=============================================")
    
    # Get DATABASE_URL from user
    database_url = input("Enter the Railway DATABASE_URL: ").strip()
    
    if not database_url:
        print("❌ No DATABASE_URL provided")
        return False
    
    try:
        # Update Google Cloud Run
        cmd = [
            'gcloud', 'run', 'services', 'update', 'productivityflow-backend',
            '--update-env-vars', f'DATABASE_URL={database_url}',
            '--region=us-central1'
        ]
        
        print("🚀 Updating Google Cloud Run...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Google Cloud Run updated successfully!")
            return True
        else:
            print(f"❌ Failed to update Google Cloud Run: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating Google Cloud Run: {e}")
        return False

def test_connection():
    """Test the database connection"""
    print("\n🧪 Testing database connection...")
    print("=============================================")
    
    try:
        import requests
        import json
        
        url = "https://productivityflow-backend-496367590729.us-central1.run.app/health"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check response: {json.dumps(data, indent=2)}")
            
            if data.get('database') == 'connected':
                print("🎉 Database connection successful!")
                return True
            else:
                print("⚠️ Database is still disconnected")
                return False
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False

def main():
    """Main function"""
    print("🚀 RAILWAY DATABASE SETUP FOR GOOGLE CLOUD RUN")
    print("=" * 50)
    
    # Step 1: Setup Railway project
    if not setup_railway_project():
        print("\n❌ Railway setup failed")
        return
    
    # Step 2: Update Google Cloud Run
    if not update_cloud_run_database():
        print("\n❌ Google Cloud Run update failed")
        return
    
    # Step 3: Test connection
    if test_connection():
        print("\n🎉 SUCCESS! Google Cloud Run is now connected to Railway database!")
        print("✅ Backend is fully operational")
        print("✅ Database is connected and working")
        print("✅ Ready for production use")
    else:
        print("\n⚠️ Connection test failed")
        print("🔧 Check the Railway dashboard and try again")

if __name__ == "__main__":
    main() 