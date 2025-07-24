#!/usr/bin/env python3
"""
Production startup script for Google Cloud Run
"""
import os
import sys
import logging
import traceback

# Configure logging for Cloud Run with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Add backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__))
sys.path.insert(0, backend_path)

try:
    from application import application, initialize_database
    logger.info("✅ Successfully imported application modules")
except ImportError as e:
    logger.error(f"❌ Failed to import application: {e}")
    traceback.print_exc()
    sys.exit(1)

if __name__ == '__main__':
    # Cloud Run sets PORT environment variable
    port = int(os.environ.get('PORT', 8080))
    
    logger.info(f"🚀 Starting ProductivityFlow on port {port}")
    logger.info(f"🌐 Environment: {os.environ.get('FLASK_ENV', 'production')}")
    logger.info(f"📦 Python version: {sys.version}")
    logger.info(f"📁 Working directory: {os.getcwd()}")
    logger.info(f"🐍 Python path: {sys.path}")

    try:
        # Initialize database with better error handling
        logger.info("🔧 Initializing database...")
        try:
            if initialize_database():
                logger.info("✅ Database initialized successfully")
            else:
                logger.warning("⚠️ Database initialization failed, continuing anyway")
        except Exception as db_error:
            logger.error(f"❌ Database initialization error: {db_error}")
            traceback.print_exc()
            logger.warning("⚠️ Continuing without database initialization")

        # Start the application
        logger.info("🌐 Starting Flask application...")
        application.run(
            host='0.0.0.0', 
            port=port, 
            debug=False,
            threaded=True
        )
    except Exception as e:
        logger.error(f"❌ Failed to start: {e}")
        traceback.print_exc()
        sys.exit(1)