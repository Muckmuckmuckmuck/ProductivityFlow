#!/usr/bin/env python3
"""
Create Test Users Script for ProductivityFlow Backend
"""

import os
import sys
from datetime import datetime
from application import application, db, User, generate_id, hash_password

def create_test_users():
    """Create test users for the application"""
    try:
        with application.app_context():
            print("🔄 Creating test users...")
            
            # Check if users already exist
            existing_users = User.query.count()
            if existing_users > 0:
                print(f"✅ Database already has {existing_users} users")
                
                # List existing users
                users = User.query.all()
                print("\n📋 Existing Users:")
                for user in users:
                    print(f"  - {user.email}: {user.name}")
                return
            
            # Create test users
            test_users = [
                {
                    'email': 'manager@productivityflow.com',
                    'password': 'password123',
                    'name': 'Manager User'
                },
                {
                    'email': 'employee@productivityflow.com',
                    'password': 'password123',
                    'name': 'Employee User'
                },
                {
                    'email': 'test@example.com',
                    'password': 'password123',
                    'name': 'Test User'
                }
            ]
            
            for user_data in test_users:
                # Check if user already exists
                existing_user = User.query.filter_by(email=user_data['email']).first()
                if existing_user:
                    print(f"⚠️ User {user_data['email']} already exists")
                    continue
                
                # Create new user
                new_user = User(
                    id=generate_id('user'),
                    email=user_data['email'],
                    password_hash=hash_password(user_data['password']),
                    name=user_data['name'],
                    created_at=datetime.utcnow()
                )
                
                db.session.add(new_user)
                print(f"✅ Created user: {user_data['email']}")
            
            db.session.commit()
            print("\n✅ Test users created successfully!")
            
            # List all users
            users = User.query.all()
            print("\n📋 All Users:")
            for user in users:
                print(f"  - {user.email}: {user.name}")
            
    except Exception as e:
        print(f"❌ Failed to create test users: {e}")
        sys.exit(1)

if __name__ == '__main__':
    print("🚀 Creating ProductivityFlow Test Users")
    create_test_users() 