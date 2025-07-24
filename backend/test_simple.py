#!/usr/bin/env python3
"""
Simple Backend Test
"""

import os
import sys

print("🔍 BACKEND DIAGNOSTIC TEST")
print("=" * 50)

# Check Python version
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")

# Check if we can import Flask
try:
    import flask
    print(f"✅ Flask version: {flask.__version__}")
except Exception as e:
    print(f"❌ Flask import failed: {e}")

# Check if we can import SQLAlchemy
try:
    from sqlalchemy import func
    print(f"✅ SQLAlchemy func: {func.now}")
    print(f"✅ SQLAlchemy func.now type: {type(func.now)}")
except Exception as e:
    print(f"❌ SQLAlchemy import failed: {e}")

# Check if we can import psycopg2
try:
    import psycopg2
    print(f"✅ psycopg2 version: {psycopg2.__version__}")
except Exception as e:
    print(f"❌ psycopg2 import failed: {e}")

# Check environment variables
print(f"\n📋 Environment Variables:")
print(f"DATABASE_URL: {'✅ Set' if os.environ.get('DATABASE_URL') else '❌ Not set'}")
print(f"FLASK_ENV: {os.environ.get('FLASK_ENV', 'Not set')}")

print("\n🎯 Test completed!") 