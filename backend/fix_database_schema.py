#!/usr/bin/env python3
"""
Database Schema Fix Script
"""

import os
import sys
from datetime import datetime
from application import application, db, Team, User, Activity

def fix_database_schema():
    """Fix the database schema by recreating tables"""
    try:
        with application.app_context():
            print("🔄 Fixing database schema...")
            
            # Drop all tables
            print("🔄 Dropping existing tables...")
            db.drop_all()
            print("✅ Tables dropped")
            
            # Create all tables with correct schema
            print("🔄 Creating tables with correct schema...")
            db.create_all()
            print("✅ Tables created successfully")
            
            # Create some test data
            print("🔄 Creating test data...")
            
            # Create test users
            from application import generate_id, hash_password
            
            test_users = [
                {
                    'id': generate_id('user'),
                    'email': 'manager@productivityflow.com',
                    'password_hash': hash_password('password123'),
                    'name': 'Manager User',
                    'created_at': datetime.utcnow()
                },
                {
                    'id': generate_id('user'),
                    'email': 'employee@productivityflow.com',
                    'password_hash': hash_password('password123'),
                    'name': 'Employee User',
                    'created_at': datetime.utcnow()
                },
                {
                    'id': generate_id('user'),
                    'email': 'test@example.com',
                    'password_hash': hash_password('password123'),
                    'name': 'Test User',
                    'created_at': datetime.utcnow()
                }
            ]
            
            for user_data in test_users:
                new_user = User(**user_data)
                db.session.add(new_user)
                print(f"✅ Created user: {user_data['email']}")
            
            # Create test team
            from application import generate_team_code
            
            team_data = {
                'id': generate_id('team'),
                'name': 'ProductivityFlow Team',
                'employee_code': generate_team_code(),
                'created_at': datetime.utcnow()
            }
            
            new_team = Team(**team_data)
            db.session.add(new_team)
            print(f"✅ Created team: {team_data['name']} ({team_data['employee_code']})")
            
            db.session.commit()
            print("\n✅ Database schema fixed successfully!")
            
            # Print summary
            users = User.query.all()
            teams = Team.query.all()
            print(f"\n📊 Database Summary:")
            print(f"   Users: {len(users)}")
            print(f"   Teams: {len(teams)}")
            
            print(f"\n📋 Available Teams:")
            for team in teams:
                print(f"   - {team.name}: {team.employee_code}")
            
            print(f"\n📋 Available Users:")
            for user in users:
                print(f"   - {user.email}: {user.name}")
            
    except Exception as e:
        print(f"❌ Database schema fix failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    print("🚀 Starting Database Schema Fix")
    fix_database_schema() 