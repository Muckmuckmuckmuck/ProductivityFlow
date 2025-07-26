#!/usr/bin/env python3
"""
Database Migration Script - ProductivityFlow
Adds reset_token and reset_expires fields to User table for forgot password functionality
"""

import os
import sqlite3
from datetime import datetime

def migrate_database():
    """Migrate the database to add forgot password fields"""
    print("🔧 DATABASE MIGRATION - PRODUCTIVITYFLOW")
    print("=" * 60)
    
    # Database file path
    db_path = 'productivityflow.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        print("Creating new database with required fields...")
        return create_new_database(db_path)
    
    try:
        # Connect to existing database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"✅ Connected to database: {db_path}")
        
        # Check if fields already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"📋 Current columns in users table: {columns}")
        
        # Add reset_token field if it doesn't exist
        if 'reset_token' not in columns:
            print("➕ Adding reset_token column...")
            cursor.execute("ALTER TABLE users ADD COLUMN reset_token TEXT")
            print("✅ reset_token column added successfully")
        else:
            print("✅ reset_token column already exists")
        
        # Add reset_expires field if it doesn't exist
        if 'reset_expires' not in columns:
            print("➕ Adding reset_expires column...")
            cursor.execute("ALTER TABLE users ADD COLUMN reset_expires DATETIME")
            print("✅ reset_expires column added successfully")
        else:
            print("✅ reset_expires column already exists")
        
        # Commit changes
        conn.commit()
        
        # Verify the migration
        cursor.execute("PRAGMA table_info(users)")
        updated_columns = [column[1] for column in cursor.fetchall()]
        print(f"📋 Updated columns in users table: {updated_columns}")
        
        # Check if all required fields are present
        required_fields = ['reset_token', 'reset_expires']
        missing_fields = [field for field in required_fields if field not in updated_columns]
        
        if missing_fields:
            print(f"❌ Missing fields: {missing_fields}")
            return False
        else:
            print("✅ All required fields are present")
        
        conn.close()
        print("🎉 Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False

def create_new_database(db_path):
    """Create a new database with all required fields"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create teams table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teams (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                employee_code TEXT UNIQUE NOT NULL,
                manager_code TEXT UNIQUE NOT NULL
            )
        ''')
        
        # Create users table with all required fields
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                team_id TEXT,
                role TEXT DEFAULT 'employee' NOT NULL,
                reset_token TEXT,
                reset_expires DATETIME,
                FOREIGN KEY (team_id) REFERENCES teams (id)
            )
        ''')
        
        # Create activities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                team_id TEXT NOT NULL,
                date DATE NOT NULL,
                active_app TEXT,
                productive_hours REAL DEFAULT 0.0,
                unproductive_hours REAL DEFAULT 0.0
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print("✅ New database created with all required fields")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create new database: {str(e)}")
        return False

def verify_migration():
    """Verify that the migration was successful"""
    print("\n🔍 VERIFYING MIGRATION")
    print("-" * 40)
    
    try:
        conn = sqlite3.connect('productivityflow.db')
        cursor = conn.cursor()
        
        # Check users table structure
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        print("📋 Users table structure:")
        for column in columns:
            print(f"  - {column[1]} ({column[2]})")
        
        # Check if required fields exist
        column_names = [column[1] for column in columns]
        required_fields = ['reset_token', 'reset_expires']
        
        for field in required_fields:
            if field in column_names:
                print(f"✅ {field}: Present")
            else:
                print(f"❌ {field}: Missing")
        
        conn.close()
        
        # Test the forgot password functionality
        print("\n🧪 Testing forgot password functionality...")
        test_forgot_password_functionality()
        
    except Exception as e:
        print(f"❌ Verification failed: {str(e)}")

def test_forgot_password_functionality():
    """Test the forgot password functionality after migration"""
    try:
        from application_with_forgot_password import application, db, User
        
        with application.app_context():
            # Test creating a user with reset fields
            test_user = User(
                id='test_user_123',
                email='test@example.com',
                password_hash='test_hash',
                name='Test User',
                reset_token='test_token_123',
                reset_expires=datetime.now()
            )
            
            db.session.add(test_user)
            db.session.commit()
            
            print("✅ User created with reset fields successfully")
            
            # Clean up test user
            db.session.delete(test_user)
            db.session.commit()
            
            print("✅ Test user cleaned up")
            
    except Exception as e:
        print(f"❌ Forgot password functionality test failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting database migration...")
    success = migrate_database()
    
    if success:
        verify_migration()
        print("\n🎉 MIGRATION COMPLETED SUCCESSFULLY!")
        print("The database now supports forgot password functionality.")
    else:
        print("\n❌ MIGRATION FAILED!")
        print("Please check the error messages above.")