#!/usr/bin/env python3
"""
Database Schema Fix Script
Fixes the database schema to match the current application code
"""

from application import application, db, Team, User
from sqlalchemy import text

def fix_database_schema():
    with application.app_context():
        print("=== FIXING DATABASE SCHEMA ===")
        
        try:
            # Check if manager_code column exists
            result = db.session.execute(text("PRAGMA table_info(teams)"))
            columns = [row[1] for row in result.fetchall()]
            
            print(f"Current columns in teams table: {columns}")
            
            # Add manager_code column if it doesn't exist
            if 'manager_code' not in columns:
                print("Adding manager_code column to teams table...")
                db.session.execute(text("ALTER TABLE teams ADD COLUMN manager_code VARCHAR(10)"))
                db.session.commit()
                print("✅ manager_code column added")
            else:
                print("✅ manager_code column already exists")
            
            # Check if employee_code column exists
            if 'employee_code' not in columns:
                print("Adding employee_code column to teams table...")
                db.session.execute(text("ALTER TABLE teams ADD COLUMN employee_code VARCHAR(10)"))
                db.session.commit()
                print("✅ employee_code column added")
            else:
                print("✅ employee_code column already exists")
            
            # Fix users table
            print("\n=== FIXING USERS TABLE ===")
            result = db.session.execute(text("PRAGMA table_info(users)"))
            user_columns = [row[1] for row in result.fetchall()]
            
            print(f"Current columns in users table: {user_columns}")
            
            # Add team_id column if it doesn't exist
            if 'team_id' not in user_columns:
                print("Adding team_id column to users table...")
                db.session.execute(text("ALTER TABLE users ADD COLUMN team_id VARCHAR(80)"))
                db.session.commit()
                print("✅ team_id column added")
            else:
                print("✅ team_id column already exists")
            
            # Add role column if it doesn't exist
            if 'role' not in user_columns:
                print("Adding role column to users table...")
                db.session.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'employee'"))
                db.session.commit()
                print("✅ role column added")
            else:
                print("✅ role column already exists")
            
            # Update existing teams with codes if they don't have them
            teams = Team.query.all()
            for team in teams:
                updated = False
                
                if not team.employee_code:
                    from application import generate_team_code
                    team.employee_code = generate_team_code()
                    updated = True
                    print(f"Added employee_code to team {team.name}: {team.employee_code}")
                
                if not team.manager_code:
                    from application import generate_team_code
                    team.manager_code = generate_team_code()
                    updated = True
                    print(f"Added manager_code to team {team.name}: {team.manager_code}")
                
                if updated:
                    db.session.commit()
            
            print("\n=== DATABASE SCHEMA FIXED ===")
            
            # Show final state
            print("\n=== FINAL TEAMS STATE ===")
            teams = Team.query.all()
            for team in teams:
                print(f"Team: {team.name}")
                print(f"  ID: {team.id}")
                print(f"  Employee Code: {team.employee_code}")
                print(f"  Manager Code: {team.manager_code}")
                print("-" * 40)
            
            print("\n=== FINAL USERS STATE ===")
            users = User.query.all()
            for user in users:
                print(f"User: {user.name}")
                print(f"  Email: {user.email}")
                print(f"  Role: {user.role}")
                print(f"  Team ID: {user.team_id}")
                print("-" * 40)
                
        except Exception as e:
            print(f"Error fixing database schema: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    fix_database_schema() 