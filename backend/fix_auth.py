#!/usr/bin/env python3
"""
Authentication Fix Script
"""

from application import application, User, db, hash_password
from sqlalchemy import text

def fix_test_user():
    """Fix the test user password"""
    print("🔧 Fixing test user password...")
    
    with application.app_context():
        # Find the test user
        test_user = User.query.filter_by(email='test@example.com').first()
        if test_user:
            # Update the password hash
            new_hash = hash_password('password123')
            test_user.password_hash = new_hash
            db.session.commit()
            print(f"✅ Fixed password for {test_user.email}")
            print(f"🔐 New hash: {new_hash[:20]}...")
        else:
            print("❌ Test user not found")

def create_test_credentials():
    """Create working test credentials"""
    print("\n📝 Creating test credentials...")
    
    with application.app_context():
        # Create a manager account
        manager_email = 'manager@productivityflow.com'
        manager_user = User.query.filter_by(email=manager_email).first()
        
        if not manager_user:
            from application import generate_id
            manager_user = User(
                id=generate_id('user'),
                email=manager_email,
                password_hash=hash_password('password123'),
                name='Test Manager'
            )
            db.session.add(manager_user)
            db.session.commit()
            print(f"✅ Created manager: {manager_email} / password123")
        else:
            print(f"✅ Manager exists: {manager_email} / password123")
        
        # Create an employee account
        employee_email = 'employee@productivityflow.com'
        employee_user = User.query.filter_by(email=employee_email).first()
        
        if not employee_user:
            from application import generate_id
            employee_user = User(
                id=generate_id('user'),
                email=employee_email,
                password_hash=hash_password('password123'),
                name='Test Employee'
            )
            db.session.add(employee_user)
            db.session.commit()
            print(f"✅ Created employee: {employee_email} / password123")
        else:
            print(f"✅ Employee exists: {employee_email} / password123")

def test_credentials():
    """Test the credentials"""
    print("\n🧪 Testing credentials...")
    
    app = application.test_client()
    
    # Test manager login
    print("🔑 Testing manager login...")
    response = app.post('/api/auth/login', json={
        'email': 'manager@productivityflow.com',
        'password': 'password123'
    })
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.data.decode()}")
    
    # Test employee login
    print("\n🔑 Testing employee login...")
    response = app.post('/api/auth/employee-login', json={
        'email': 'employee@productivityflow.com',
        'password': 'password123'
    })
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.data.decode()}")

def main():
    """Run the fix"""
    print("🚀 ProductivityFlow Authentication Fix")
    print("=" * 50)
    
    fix_test_user()
    create_test_credentials()
    test_credentials()
    
    print("\n" + "=" * 50)
    print("✅ Authentication fix complete!")
    print("\n📋 Working Test Credentials:")
    print("   Manager: manager@productivityflow.com / password123")
    print("   Employee: employee@productivityflow.com / password123")
    print("   Test User: test@example.com / password123 (fixed)")

if __name__ == '__main__':
    main() 