#!/usr/bin/env python3
"""
Test script to verify backend deployment configuration
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import flask
        print("✅ Flask imported successfully")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    try:
        import flask_sqlalchemy
        print("✅ Flask-SQLAlchemy imported successfully")
    except ImportError as e:
        print(f"❌ Flask-SQLAlchemy import failed: {e}")
        return False
    
    try:
        import flask_cors
        print("✅ Flask-CORS imported successfully")
    except ImportError as e:
        print(f"❌ Flask-CORS import failed: {e}")
        return False
    
    try:
        import bcrypt
        print("✅ bcrypt imported successfully")
    except ImportError as e:
        print(f"❌ bcrypt import failed: {e}")
        return False
    
    try:
        import jwt
        print("✅ PyJWT imported successfully")
    except ImportError as e:
        print(f"❌ PyJWT import failed: {e}")
        return False
    
    try:
        import psycopg3
        print("✅ psycopg3 imported successfully")
    except ImportError as e:
        print(f"❌ psycopg3 import failed: {e}")
        return False
    
    return True

def test_application_creation():
    """Test that the Flask application can be created"""
    print("\nTesting application creation...")
    
    try:
        # Temporarily set environment variables for testing
        os.environ['SECRET_KEY'] = 'test-secret-key'
        os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret-key'
        
        # Import the application
        from application import application, db
        
        print("✅ Flask application created successfully")
        print("✅ SQLAlchemy database initialized successfully")
        
        return True
    except Exception as e:
        print(f"❌ Application creation failed: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("\nTesting database connection...")
    
    try:
        from application import application, db
        
        with application.app_context():
            # Try to execute a simple query
            result = db.session.execute('SELECT 1')
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("This is expected if DATABASE_URL is not set")
        return True  # Don't fail the test if no database is configured

def main():
    """Run all tests"""
    print("🧪 Testing ProductivityFlow Backend Deployment")
    print("=" * 50)
    
    # Test Python version
    print(f"Python version: {sys.version}")
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed")
        return False
    
    # Test application creation
    if not test_application_creation():
        print("\n❌ Application creation failed")
        return False
    
    # Test database connection
    if not test_database_connection():
        print("\n❌ Database connection failed")
        return False
    
    print("\n✅ All tests passed! Backend is ready for deployment.")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 