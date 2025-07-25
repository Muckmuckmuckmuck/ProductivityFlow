#!/usr/bin/env python3
"""
Database Fix Script for ProductivityFlow Backend
"""

import os
import sys
from datetime import datetime
from application import application, db, Team, User, Activity, generate_id, generate_team_code, hash_password

def init_database():
    """Initialize the database with tables and sample data"""
    try:
        with application.app_context():
            print("🔄 Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Check if we have any teams
            existing_teams = Team.query.count()
            if existing_teams == 0:
                print("🔄 Creating sample teams...")
                
                # Create sample teams
                team1 = Team(
                    id=generate_id('team'),
                    name='ProductivityFlow Team',
                    employee_code=generate_team_code(),
                    created_at=datetime.utcnow()
                )
                
                team2 = Team(
                    id=generate_id('team'),
                    name='Development Team',
                    employee_code=generate_team_code(),
                    created_at=datetime.utcnow()
                )
                
                db.session.add(team1)
                db.session.add(team2)
                db.session.commit()
                print("✅ Sample teams created")
                
                # Create sample users
                print("🔄 Creating sample users...")
                
                manager_user = User(
                    id=generate_id('user'),
                    email='manager@productivityflow.com',
                    password_hash=hash_password('password123'),
                    name='Manager User',
                    created_at=datetime.utcnow()
                )
                
                employee_user = User(
                    id=generate_id('user'),
                    email='employee@productivityflow.com',
                    password_hash=hash_password('password123'),
                    name='Employee User',
                    created_at=datetime.utcnow()
                )
                
                test_user = User(
                    id=generate_id('user'),
                    email='test@example.com',
                    password_hash=hash_password('password123'),
                    name='Test User',
                    created_at=datetime.utcnow()
                )
                
                db.session.add(manager_user)
                db.session.add(employee_user)
                db.session.add(test_user)
                db.session.commit()
                print("✅ Sample users created")
                
                # Create sample activity
                print("🔄 Creating sample activity data...")
                
                activity = Activity(
                    user_id=employee_user.id,
                    team_id=team1.id,
                    date=datetime.utcnow().date(),
                    active_app='VS Code',
                    productive_hours=8.5,
                    unproductive_hours=1.5,
                    last_active=datetime.utcnow()
                )
                
                db.session.add(activity)
                db.session.commit()
                print("✅ Sample activity data created")
                
            else:
                print(f"✅ Database already has {existing_teams} teams")
            
            # Print team codes for reference
            teams = Team.query.all()
            print("\n📋 Available Teams:")
            for team in teams:
                print(f"  - {team.name}: {team.employee_code}")
            
            print("\n✅ Database initialization completed successfully!")
            
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    print("🚀 Starting ProductivityFlow Database Initialization")
    init_database() 