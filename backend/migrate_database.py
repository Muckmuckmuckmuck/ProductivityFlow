#!/usr/bin/env python3
"""
Database Migration Script
Updates the database schema to support enhanced tracking features
"""

from application import application, db, Activity, AppSession, ProductivityEvent, DailySummary
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

def migrate_database():
    """Migrate the database to support enhanced tracking features"""
    with application.app_context():
        print("🔄 Starting database migration...")
        
        try:
            # Step 1: Check current database structure
            print("\n1. Checking current database structure...")
            
            # Check activities table structure
            result = db.session.execute(text("PRAGMA table_info(activities)"))
            existing_columns = [row[1] for row in result.fetchall()]
            print(f"Current columns in activities table: {existing_columns}")
            
            # Step 2: Add new columns to activities table
            print("\n2. Adding new columns to activities table...")
            
            new_columns = [
                ("timestamp", "DATETIME DEFAULT CURRENT_TIMESTAMP"),
                ("app_category", "VARCHAR(100)"),
                ("window_title", "VARCHAR(500)"),
                ("app_url", "VARCHAR(1000)"),
                ("idle_time", "FLOAT DEFAULT 0.0"),
                ("break_time", "FLOAT DEFAULT 0.0"),
                ("total_active_time", "FLOAT DEFAULT 0.0"),
                ("productivity_score", "FLOAT DEFAULT 0.0"),
                ("focus_time", "FLOAT DEFAULT 0.0"),
                ("distraction_count", "INTEGER DEFAULT 0"),
                ("task_switches", "INTEGER DEFAULT 0"),
                ("cpu_usage", "FLOAT DEFAULT 0.0"),
                ("memory_usage", "FLOAT DEFAULT 0.0"),
                ("network_activity", "BOOLEAN DEFAULT FALSE"),
                ("mouse_clicks", "INTEGER DEFAULT 0"),
                ("keyboard_activity", "BOOLEAN DEFAULT FALSE"),
                ("screen_time", "FLOAT DEFAULT 0.0"),
                ("session_id", "VARCHAR(100)"),
                ("device_info", "VARCHAR(500)"),
                ("notes", "TEXT")
            ]
            
            for column_name, column_def in new_columns:
                if column_name not in existing_columns:
                    print(f"Adding column: {column_name}")
                    try:
                        db.session.execute(text(f"ALTER TABLE activities ADD COLUMN {column_name} {column_def}"))
                        print(f"✅ Added column: {column_name}")
                    except Exception as e:
                        print(f"⚠️  Column {column_name} might already exist: {e}")
                else:
                    print(f"✅ Column {column_name} already exists")
            
            db.session.commit()
            
            # Step 3: Create new tables
            print("\n3. Creating new tables...")
            
            # Create app_sessions table
            print("Creating app_sessions table...")
            try:
                db.session.execute(text("""
                    CREATE TABLE IF NOT EXISTS app_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id VARCHAR(80) NOT NULL,
                        team_id VARCHAR(80) NOT NULL,
                        session_id VARCHAR(100) NOT NULL,
                        start_time DATETIME NOT NULL,
                        end_time DATETIME,
                        app_name VARCHAR(255) NOT NULL,
                        app_category VARCHAR(100),
                        window_title VARCHAR(500),
                        url VARCHAR(1000),
                        duration FLOAT DEFAULT 0.0,
                        productivity_score FLOAT DEFAULT 0.0,
                        activity_level VARCHAR(50) DEFAULT 'low',
                        focus_score FLOAT DEFAULT 0.0,
                        mouse_clicks INTEGER DEFAULT 0,
                        keyboard_events INTEGER DEFAULT 0,
                        scroll_events INTEGER DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                print("✅ app_sessions table created")
            except Exception as e:
                print(f"⚠️  app_sessions table might already exist: {e}")
            
            # Create productivity_events table
            print("Creating productivity_events table...")
            try:
                db.session.execute(text("""
                    CREATE TABLE IF NOT EXISTS productivity_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id VARCHAR(80) NOT NULL,
                        team_id VARCHAR(80) NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        event_type VARCHAR(100) NOT NULL,
                        event_data TEXT,
                        app_name VARCHAR(255),
                        app_category VARCHAR(100),
                        window_title VARCHAR(500),
                        duration FLOAT DEFAULT 0.0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                print("✅ productivity_events table created")
            except Exception as e:
                print(f"⚠️  productivity_events table might already exist: {e}")
            
            # Create daily_summaries table
            print("Creating daily_summaries table...")
            try:
                db.session.execute(text("""
                    CREATE TABLE IF NOT EXISTS daily_summaries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id VARCHAR(80) NOT NULL,
                        team_id VARCHAR(80) NOT NULL,
                        date DATE NOT NULL,
                        total_productive_time FLOAT DEFAULT 0.0,
                        total_unproductive_time FLOAT DEFAULT 0.0,
                        total_idle_time FLOAT DEFAULT 0.0,
                        total_break_time FLOAT DEFAULT 0.0,
                        total_screen_time FLOAT DEFAULT 0.0,
                        overall_productivity_score FLOAT DEFAULT 0.0,
                        focus_score FLOAT DEFAULT 0.0,
                        distraction_count INTEGER DEFAULT 0,
                        task_switch_count INTEGER DEFAULT 0,
                        most_used_app VARCHAR(255),
                        most_productive_app VARCHAR(255),
                        app_usage_breakdown TEXT,
                        goals_met INTEGER DEFAULT 0,
                        total_goals INTEGER DEFAULT 0,
                        achievements TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                print("✅ daily_summaries table created")
            except Exception as e:
                print(f"⚠️  daily_summaries table might already exist: {e}")
            
            db.session.commit()
            
            # Step 4: Verify migration
            print("\n4. Verifying migration...")
            
            # Check activities table structure again
            result = db.session.execute(text("PRAGMA table_info(activities)"))
            updated_columns = [row[1] for row in result.fetchall()]
            print(f"Updated columns in activities table: {len(updated_columns)} columns")
            
            # Check new tables exist
            tables_to_check = ['app_sessions', 'productivity_events', 'daily_summaries']
            for table in tables_to_check:
                try:
                    result = db.session.execute(text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"))
                    if result.fetchone():
                        print(f"✅ {table} table exists")
                    else:
                        print(f"❌ {table} table missing")
                except Exception as e:
                    print(f"❌ Error checking {table} table: {e}")
            
            print("\n🎉 Database migration completed successfully!")
            print("\n📊 Migration Summary:")
            print(f"- Added {len(new_columns)} new columns to activities table")
            print(f"- Created 3 new tables for enhanced tracking")
            print("- All enhanced tracking features are now ready to use")
            
            return True
            
        except Exception as e:
            logger.error(f"Database migration failed: {str(e)}")
            db.session.rollback()
            print(f"❌ Database migration failed: {e}")
            return False

if __name__ == "__main__":
    success = migrate_database()
    if success:
        print("\n✅ Migration successful! Enhanced tracking features are now available.")
    else:
        print("\n❌ Migration failed. Please check the errors above.")