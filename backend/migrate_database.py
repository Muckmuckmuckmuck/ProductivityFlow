#!/usr/bin/env python3
"""
Database Migration Script for ProductivityFlow
Adds manager_id column to teams table
"""

from application import application, db
import sqlite3

def migrate_database():
    """Migrate the database to add manager_id column"""
    
    with application.app_context():
        try:
            # Get database connection
            engine = db.engine
            
            # Check if manager_id column exists
            inspector = db.inspect(engine)
            columns = [col['name'] for col in inspector.get_columns('teams')]
            
            if 'manager_id' not in columns:
                print("🔄 Adding manager_id column to teams table...")
                
                # Add the column
                with engine.connect() as conn:
                    conn.execute(db.text("ALTER TABLE teams ADD COLUMN manager_id VARCHAR(80)"))
                    conn.commit()
                
                print("✅ manager_id column added successfully")
                
                # Update existing teams with manager_id from memberships
                print("🔄 Updating existing teams with manager information...")
                
                # Get all teams and their managers
                result = conn.execute(db.text("""
                    SELECT DISTINCT t.id, m.user_id 
                    FROM teams t 
                    JOIN memberships m ON t.id = m.team_id 
                    WHERE m.role = 'manager'
                """)).fetchall()
                
                for team_id, manager_id in result:
                    conn.execute(
                        db.text("UPDATE teams SET manager_id = :manager_id WHERE id = :team_id"),
                        {"manager_id": manager_id, "team_id": team_id}
                    )
                
                conn.commit()
                print(f"✅ Updated {len(result)} teams with manager information")
                
            else:
                print("✅ manager_id column already exists")
            
            # Verify the migration
            columns = [col['name'] for col in inspector.get_columns('teams')]
            if 'manager_id' in columns:
                print("✅ Database migration completed successfully")
                return True
            else:
                print("❌ Migration failed - manager_id column not found")
                return False
                
        except Exception as e:
            print(f"❌ Migration error: {e}")
            return False

if __name__ == "__main__":
    print("🚀 ProductivityFlow Database Migration")
    print("=" * 50)
    
    success = migrate_database()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("The database is now ready for the updated schema.")
    else:
        print("\n❌ Migration failed!")
        print("Please check the error messages above.")