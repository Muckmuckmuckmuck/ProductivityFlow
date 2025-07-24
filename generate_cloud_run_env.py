#!/usr/bin/env python3
"""
Generate environment variables for Google Cloud Run deployment
"""
import secrets
import string

def generate_secret(length=32):
    """Generate a random secret key"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def main():
    print("🔧 Generating Google Cloud Run Environment Variables")
    print("=" * 50)
    
    # Generate secure keys
    secret_key = generate_secret(32)
    jwt_secret = generate_secret(32)
    encryption_key = generate_secret(32)
    
    print("\n📋 Copy these environment variables to Google Cloud Run:")
    print("-" * 50)
    
    env_vars = {
        "DATABASE_URL": "postgresql://postgres:YOUR_PASSWORD@YOUR_DB_IP:5432/productivityflow",
        "SECRET_KEY": secret_key,
        "JWT_SECRET_KEY": jwt_secret,
        "ENCRYPTION_KEY": encryption_key,
        "FLASK_ENV": "production",
        "ENABLE_RATE_LIMITING": "true",
        "STRIPE_SECRET_KEY": "sk_test_YOUR_STRIPE_SECRET_KEY",
        "STRIPE_PUBLISHABLE_KEY": "pk_test_YOUR_STRIPE_PUBLISHABLE_KEY",
        "CLAUDE_API_KEY": "sk-ant-api03-YOUR_CLAUDE_API_KEY",
        "MAIL_SERVER": "smtp.gmail.com",
        "MAIL_PORT": "587",
        "MAIL_USERNAME": "your-email@gmail.com",
        "MAIL_PASSWORD": "your-gmail-app-password",
        "MAIL_DEFAULT_SENDER": "your-email@gmail.com",
        "REDIS_URL": "redis://YOUR_REDIS_URL:6379/0"
    }
    
    for key, value in env_vars.items():
        print(f"{key}={value}")
    
    print("\n" + "=" * 50)
    print("🚨 IMPORTANT NOTES:")
    print("1. Replace YOUR_PASSWORD with your Cloud SQL database password")
    print("2. Replace YOUR_DB_IP with your Cloud SQL instance IP")
    print("3. Replace YOUR_STRIPE_* with your actual Stripe keys")
    print("4. Replace YOUR_CLAUDE_API_KEY with your Anthropic API key")
    print("5. Replace your-email@gmail.com with your actual email")
    print("6. Replace YOUR_REDIS_URL with your Redis instance URL")
    print("7. Generate a Gmail App Password for MAIL_PASSWORD")
    
    print("\n🔗 Helpful Links:")
    print("- Gmail App Password: https://myaccount.google.com/apppasswords")
    print("- Stripe Dashboard: https://dashboard.stripe.com/apikeys")
    print("- Anthropic Console: https://console.anthropic.com/")
    print("- Cloud SQL: https://console.cloud.google.com/sql")
    
    print("\n✅ Ready to deploy to Google Cloud Run!")

if __name__ == "__main__":
    main() 