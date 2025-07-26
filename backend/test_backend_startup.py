#!/usr/bin/env python3
"""
Test Backend Startup Script
Tests if the backend can start up without errors
"""

import sys
import traceback

def test_backend_startup():
    print("=== TESTING BACKEND STARTUP ===")
    
    try:
        # Try to import the application
        print("1. Importing application...")
        from application import application, db
        
        print("✅ Application imported successfully")
        
        # Try to create app context
        print("2. Creating app context...")
        with application.app_context():
            print("✅ App context created successfully")
            
            # Try to check database connection
            print("3. Testing database connection...")
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            print("✅ Database connection successful")
            
            # Try to import models
            print("4. Importing models...")
            from application import Team, User
            print("✅ Models imported successfully")
            
            # Try to query database
            print("5. Testing database queries...")
            teams = Team.query.all()
            users = User.query.all()
            print(f"✅ Database queries successful - {len(teams)} teams, {len(users)} users")
            
        print("\n🎉 Backend startup test PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ Backend startup test FAILED!")
        print(f"Error: {e}")
        print(f"Error type: {type(e).__name__}")
        print("\nFull traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_backend_startup()
    sys.exit(0 if success else 1) 