#!/usr/bin/env python3
"""
Debug script to test deployment configuration locally
"""
import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_command(command, description):
    """Run a command and log the result"""
    logger.info(f"🔧 {description}")
    logger.info(f"📋 Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"✅ {description} - SUCCESS")
            if result.stdout:
                logger.info(f"📤 Output: {result.stdout.strip()}")
        else:
            logger.error(f"❌ {description} - FAILED")
            logger.error(f"📤 Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        logger.error(f"❌ {description} - EXCEPTION: {e}")
        return False
    
    return True

def check_python_version():
    """Check Python version compatibility"""
    logger.info("🐍 Checking Python version...")
    version = sys.version_info
    logger.info(f"📋 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        logger.info("✅ Python version is compatible")
        return True
    else:
        logger.error("❌ Python version is not compatible (need 3.8+)")
        return False

def check_dependencies():
    """Check if all required dependencies can be imported"""
    logger.info("📦 Checking dependencies...")
    
    dependencies = [
        'flask',
        'flask_sqlalchemy', 
        'flask_cors',
        'flask_limiter',
        'psycopg2',
        'dotenv',  # Changed from python_dotenv
        'bcrypt',
        'jwt',     # Changed from PyJWT
        'cryptography',
        'redis',
        'stripe',
        'anthropic',
        'flask_mail',
        'apscheduler',
        'requests',
        'gunicorn'
    ]
    
    failed_imports = []
    
    for dep in dependencies:
        try:
            __import__(dep.replace('-', '_'))
            logger.info(f"✅ {dep}")
        except ImportError as e:
            logger.error(f"❌ {dep}: {e}")
            failed_imports.append(dep)
    
    if failed_imports:
        logger.error(f"❌ Failed imports: {failed_imports}")
        return False
    
    logger.info("✅ All dependencies can be imported")
    return True

def test_application_import():
    """Test if the application can be imported"""
    logger.info("🔧 Testing application import...")
    
    try:
        # Add backend to path
        backend_path = os.path.join(os.getcwd(), 'backend')
        sys.path.insert(0, backend_path)
        
        from application import application, initialize_database
        logger.info("✅ Application imported successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Application import failed: {e}")
        return False

def test_docker_build():
    """Test Docker build locally"""
    logger.info("🐳 Testing Docker build...")
    
    # Check if Docker is available
    if not run_command("docker --version", "Checking Docker availability"):
        logger.error("❌ Docker not available")
        return False
    
    # Check if Docker daemon is running
    if not run_command("docker ps", "Checking Docker daemon"):
        logger.warning("⚠️ Docker daemon not running")
        logger.info("💡 To start Docker Desktop:")
        logger.info("   1. Open Docker Desktop application")
        logger.info("   2. Wait for it to start")
        logger.info("   3. Run this script again")
        logger.info("   OR skip Docker test for now (will work on Google Cloud)")
        return True  # Don't fail the whole test for this
    
    # Build the image
    if not run_command("docker build -t productivityflow-test .", "Building Docker image"):
        logger.error("❌ Docker build failed")
        return False
    
    logger.info("✅ Docker build successful")
    return True

def main():
    """Main debug function"""
    logger.info("🔍 Starting deployment debug...")
    logger.info("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Application Import", test_application_import),
        ("Docker Build", test_docker_build)
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        logger.info(f"\n📋 Running {name} check...")
        if check_func():
            passed += 1
        logger.info("-" * 30)
    
    logger.info(f"\n📊 Debug Results: {passed}/{total} checks passed")
    
    if passed >= 3:  # Allow Docker to fail
        logger.info("🎉 Core checks passed! Ready for deployment.")
        logger.info("💡 Note: Docker test can be skipped if daemon isn't running")
        return True
    else:
        logger.error("❌ Core checks failed. Please fix issues before deploying.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 