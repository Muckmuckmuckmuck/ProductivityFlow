#!/usr/bin/env python3
"""
Database migration script to add manager_id field to teams table
"""

import sqlite3
import os
import sys

def migrate_database():
    """Add manager_id column to teams table if it doesn't exist"""
    
    # Get database path
    db_path = os.environ.get('DATABASE_URL', 'sqlite:///productivity_flow.db')
    
    # Handle SQLite database
    if db_path.startswith('sqlite:///'):
        db_file = db_path.replace('sqlite:///', '')
        if db_file == 'productivity_flow.db':
            db_file = 'instance/productivity_flow.db'
    else:
        print("❌ This migration script only supports SQLite databases")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Check if manager_id column exists
        cursor.execute("PRAGMA table_info(teams)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'manager_id' not in columns:
            print("🔄 Adding manager_id column to teams table...")
            
            # Add the manager_id column
            cursor.execute("ALTER TABLE teams ADD COLUMN manager_id VARCHAR(80)")
            
            # Update existing teams to set manager_id based on membership
            print("🔄 Updating existing teams with manager information...")
            
            # Get all teams and their managers
            cursor.execute("""
                SELECT DISTINCT t.id, m.user_id 
                FROM teams t 
                JOIN memberships m ON t.id = m.team_id 
                WHERE m.role = 'manager'
            """)
            
            team_managers = cursor.fetchall()
            
            for team_id, manager_id in team_managers:
                cursor.execute(
                    "UPDATE teams SET manager_id = ? WHERE id = ?",
                    (manager_id, team_id)
                )
                print(f"✅ Updated team {team_id} with manager {manager_id}")
            
            conn.commit()
            print("✅ Migration completed successfully!")
        else:
            print("✅ manager_id column already exists in teams table")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting database migration...")
    success = migrate_database()
    if success:
        print("🎉 Migration completed successfully!")
        sys.exit(0)
    else:
        print("💥 Migration failed!")
        sys.exit(1) 