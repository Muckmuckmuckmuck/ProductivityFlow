#!/usr/bin/env python3
"""
Script to set up a local PostgreSQL database for testing
"""

import subprocess
import sys
import os
import time

def check_docker():
    """Check if Docker is installed and running"""
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker is installed")
            return True
        else:
            print("❌ Docker is not installed or not running")
            return False
    except FileNotFoundError:
        print("❌ Docker is not installed")
        return False

def setup_postgres_docker():
    """Set up PostgreSQL using Docker"""
    print("🐳 Setting up PostgreSQL with Docker...")
    
    # Stop any existing container
    subprocess.run(['docker', 'stop', 'productivityflow-postgres'], capture_output=True)
    subprocess.run(['docker', 'rm', 'productivityflow-postgres'], capture_output=True)
    
    # Start PostgreSQL container
    cmd = [
        'docker', 'run', '-d',
        '--name', 'productivityflow-postgres',
        '-e', 'POSTGRES_PASSWORD=postgres',
        '-e', 'POSTGRES_DB=productivityflow',
        '-p', '5432:5432',
        'postgres:15'
    ]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ PostgreSQL container started")
        print("⏳ Waiting for PostgreSQL to be ready...")
        time.sleep(10)
        return True
    else:
        print(f"❌ Failed to start PostgreSQL: {result.stderr}")
        return False

def create_database_schema():
    """Create the database schema"""
    print("🗄️ Creating database schema...")
    
    # SQL commands to create tables
    schema_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        name VARCHAR(255) NOT NULL,
        is_verified BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS teams (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        manager_id INTEGER REFERENCES users(id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS team_members (
        id SERIAL PRIMARY KEY,
        team_id INTEGER REFERENCES teams(id),
        user_id INTEGER REFERENCES users(id),
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(team_id, user_id)
    );
    """
    
    # Execute schema
    cmd = [
        'docker', 'exec', '-i', 'productivityflow-postgres',
        'psql', '-U', 'postgres', '-d', 'productivityflow'
    ]
    
    result = subprocess.run(cmd, input=schema_sql, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Database schema created")
        return True
    else:
        print(f"❌ Failed to create schema: {result.stderr}")
        return False

def update_backend_env():
    """Update the backend to use local database"""
    print("🔧 Updating backend environment...")
    
    local_db_url = "postgresql://postgres:postgres@localhost:5432/productivityflow"
    
    cmd = [
        'gcloud', 'run', 'services', 'update', 'productivityflow-backend',
        '--region=us-central1',
        f'--update-env-vars=DATABASE_URL={local_db_url}'
    ]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Backend environment updated")
        return True
    else:
        print(f"❌ Failed to update backend: {result.stderr}")
        return False

def test_connection():
    """Test the database connection"""
    print("🧪 Testing database connection...")
    
    test_sql = "SELECT 1;"
    cmd = [
        'docker', 'exec', '-i', 'productivityflow-postgres',
        'psql', '-U', 'postgres', '-d', 'productivityflow', '-c', test_sql
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Database connection successful")
        return True
    else:
        print(f"❌ Database connection failed: {result.stderr}")
        return False

def main():
    print("🚀 ProductivityFlow Local Database Setup")
    print("=" * 50)
    
    if not check_docker():
        print("\n❌ Please install Docker first:")
        print("   https://docs.docker.com/get-docker/")
        return False
    
    if not setup_postgres_docker():
        return False
    
    if not create_database_schema():
        return False
    
    if not test_connection():
        return False
    
    if not update_backend_env():
        return False
    
    print("\n🎉 Setup complete!")
    print("📊 Database URL: postgresql://postgres:postgres@localhost:5432/productivityflow")
    print("🌐 Backend URL: https://productivityflow-backend-496367590729.us-central1.run.app")
    print("\n⏳ Waiting for backend to update...")
    time.sleep(30)
    
    return True

if __name__ == "__main__":
    main() 