#!/usr/bin/env python3
"""
Test Cloud SQL Connection
"""

import os
import psycopg2
import time

def test_direct_connection():
    """Test direct connection to Cloud SQL"""
    print("🔍 Testing direct connection to Cloud SQL...")
    print("=============================================")
    
    # Cloud SQL connection details
    host = "35.238.243.118"
    port = 5432
    database = "postgres"
    user = "postgres"
    password = "ProductivityFlow2025"
    
    try:
        print(f"Connecting to {host}:{port}...")
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            connect_timeout=10
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Connection successful!")
        print(f"PostgreSQL version: {version[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def test_localhost_connection():
    """Test localhost connection (Cloud SQL Proxy)"""
    print("\n🔍 Testing localhost connection (Cloud SQL Proxy)...")
    print("=============================================")
    
    try:
        print("Connecting to localhost:5432...")
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="postgres",
            user="postgres",
            password="ProductivityFlow2025",
            connect_timeout=10
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Connection successful!")
        print(f"PostgreSQL version: {version[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 CLOUD SQL CONNECTION TEST")
    print("=" * 50)
    
    # Test 1: Direct connection
    direct_success = test_direct_connection()
    
    # Test 2: Localhost connection
    localhost_success = test_localhost_connection()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    print(f"Direct Connection: {'✅ SUCCESS' if direct_success else '❌ FAILED'}")
    print(f"Localhost Connection: {'✅ SUCCESS' if localhost_success else '❌ FAILED'}")
    
    if direct_success:
        print("\n🎉 Direct connection works! Use direct IP connection.")
    elif localhost_success:
        print("\n🎉 Localhost connection works! Use Cloud SQL Proxy.")
    else:
        print("\n❌ Both connection methods failed.")
        print("🔧 Check Cloud SQL instance configuration.")

if __name__ == "__main__":
    main() 