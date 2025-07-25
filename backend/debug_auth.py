#!/usr/bin/env python3
"""
Authentication Debug Script
"""

from application import application, User, db, hash_password, verify_password
from sqlalchemy import text

def debug_database():
    """Debug database connection and users"""
    print("=== DATABASE DEBUG ===")
    
    # Check database connection
    try:
        result = db.session.execute(text('SELECT 1'))
        print(f"✅ Database connected: {result.fetchone()}")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    # Check existing users
    try:
        users = User.query.all()
        print(f"📊 Total users: {len(users)}")
        for user in users:
            print(f"   User: {user.email} | Name: {user.name} | Password hash: {user.password_hash[:20]}...")
    except Exception as e:
        print(f"❌ Error querying users: {e}")

def debug_password_verification():
    """Debug password verification"""
    print("\n=== PASSWORD VERIFICATION DEBUG ===")
    
    # Test password hashing and verification
    test_password = "password123"
    hashed = hash_password(test_password)
    print(f"🔐 Test password: {test_password}")
    print(f"🔐 Hashed password: {hashed}")
    print(f"🔐 Verification result: {verify_password(test_password, hashed)}")
    
    # Check existing user
    test_user = User.query.filter_by(email='test@example.com').first()
    if test_user:
        print(f"\n👤 Found user: {test_user.email}")
        print(f"🔐 Stored hash: {test_user.password_hash}")
        print(f"🔐 Verification with 'password123': {verify_password('password123', test_user.password_hash)}")
        print(f"🔐 Verification with 'wrong': {verify_password('wrong', test_user.password_hash)}")
    else:
        print("\n❌ User 'test@example.com' not found")

def debug_register():
    """Debug registration process"""
    print("\n=== REGISTRATION DEBUG ===")
    
    app = application.test_client()
    
    # Test registration with new user
    test_data = {
        'email': 'debug@example.com',
        'password': 'password123',
        'name': 'Debug User'
    }
    
    print(f"📝 Attempting to register: {test_data['email']}")
    response = app.post('/api/auth/register', json=test_data)
    print(f"📝 Status: {response.status_code}")
    print(f"📝 Response: {response.data.decode()}")
    
    # Check if user was created
    new_user = User.query.filter_by(email='debug@example.com').first()
    if new_user:
        print(f"✅ User created successfully: {new_user.email}")
        print(f"🔐 Password verification: {verify_password('password123', new_user.password_hash)}")
    else:
        print("❌ User was not created")

def debug_login():
    """Debug login process"""
    print("\n=== LOGIN DEBUG ===")
    
    app = application.test_client()
    
    # Test manager login
    print("🔑 Testing manager login...")
    login_data = {'email': 'debug@example.com', 'password': 'password123'}
    response = app.post('/api/auth/login', json=login_data)
    print(f"🔑 Manager login status: {response.status_code}")
    print(f"🔑 Manager login response: {response.data.decode()}")
    
    # Test employee login
    print("\n🔑 Testing employee login...")
    response = app.post('/api/auth/employee-login', json=login_data)
    print(f"🔑 Employee login status: {response.status_code}")
    print(f"🔑 Employee login response: {response.data.decode()}")

def debug_team_join():
    """Debug team join process"""
    print("\n=== TEAM JOIN DEBUG ===")
    
    app = application.test_client()
    
    # Create a team first
    print("🏢 Creating test team...")
    team_data = {'name': 'Debug Team', 'manager_id': 'debug_manager'}
    response = app.post('/api/teams', json=team_data)
    print(f"🏢 Team creation status: {response.status_code}")
    print(f"🏢 Team creation response: {response.data.decode()}")
    
    if response.status_code == 201:
        team_info = response.get_json()
        team_code = team_info['team']['employee_code']
        
        # Join team
        print(f"\n👥 Joining team with code: {team_code}")
        join_data = {'employee_code': team_code, 'user_name': 'Team Member'}
        response = app.post('/api/teams/join', json=join_data)
        print(f"👥 Join status: {response.status_code}")
        print(f"👥 Join response: {response.data.decode()}")
        
        if response.status_code == 200:
            join_info = response.get_json()
            user_email = f"team.member@{join_info['team']['id']}.local"
            
            # Test employee login with generated credentials
            print(f"\n🔑 Testing employee login with generated email: {user_email}")
            login_data = {'email': user_email, 'password': 'default123'}
            response = app.post('/api/auth/employee-login', json=login_data)
            print(f"🔑 Employee login status: {response.status_code}")
            print(f"🔑 Employee login response: {response.data.decode()}")

def main():
    """Run all debug tests"""
    print("🚀 ProductivityFlow Authentication Debug")
    print("=" * 50)
    
    with application.app_context():
        debug_database()
        debug_password_verification()
        debug_register()
        debug_login()
        debug_team_join()
    
    print("\n" + "=" * 50)
    print("🏁 Debug complete!")

if __name__ == '__main__':
    main() 