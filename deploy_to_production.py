#!/usr/bin/env python3
"""
Production Deployment Script for ProductivityFlow
Deploys the secure backend to Google Cloud Run
"""

import subprocess
import sys
import os
import time

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    print(f"   Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return result.stdout
        else:
            print(f"❌ {description} failed:")
            print(f"   Error: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ {description} failed with exception: {str(e)}")
        return None

def check_prerequisites():
    """Check if all prerequisites are installed"""
    print("🔍 Checking prerequisites...")
    
    # Check gcloud
    if not run_command("gcloud --version", "Checking gcloud CLI"):
        print("❌ gcloud CLI not found. Please install Google Cloud SDK")
        return False
    
    # Check Docker
    if not run_command("docker --version", "Checking Docker"):
        print("❌ Docker not found. Please install Docker")
        return False
    
    # Check if authenticated
    auth_result = run_command("gcloud auth list --filter=status:ACTIVE --format='value(account)'", "Checking authentication")
    if not auth_result or not auth_result.strip():
        print("❌ Not authenticated with gcloud. Please run: gcloud auth login")
        return False
    
    print("✅ All prerequisites met")
    return True

def create_production_dockerfile():
    """Create a production-ready Dockerfile"""
    dockerfile_content = """FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY start_secure_backend.py .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8080/health || exit 1

# Start the application
CMD ["python", "start_secure_backend.py"]
"""
    
    with open("Dockerfile.prod", "w") as f:
        f.write(dockerfile_content)
    
    print("✅ Production Dockerfile created")

def create_requirements_file():
    """Create requirements.txt for production"""
    requirements = """Flask==3.1.1
Flask-CORS==6.0.1
bcrypt==4.3.0
PyJWT==2.10.1
gunicorn==21.2.0
"""
    
    with open("requirements.txt", "w") as f:
        f.write(requirements)
    
    print("✅ Requirements.txt created")

def deploy_to_cloud_run():
    """Deploy to Google Cloud Run"""
    print("🚀 Deploying to Google Cloud Run...")
    
    # Get project ID
    project_result = run_command("gcloud config get-value project", "Getting project ID")
    if not project_result:
        print("❌ Could not get project ID")
        return False
    
    project_id = project_result.strip()
    print(f"   Project ID: {project_id}")
    
    # Build and push Docker image
    image_name = f"gcr.io/{project_id}/productivityflow-backend"
    
    build_result = run_command(
        f"docker build -f Dockerfile.prod -t {image_name} .",
        "Building Docker image"
    )
    if not build_result:
        return False
    
    push_result = run_command(
        f"docker push {image_name}",
        "Pushing Docker image"
    )
    if not push_result:
        return False
    
    # Deploy to Cloud Run
    deploy_result = run_command(
        f"gcloud run deploy productivityflow-backend-secure "
        f"--image {image_name} "
        f"--platform managed "
        f"--region us-central1 "
        f"--allow-unauthenticated "
        f"--port 8080 "
        f"--memory 512Mi "
        f"--cpu 1 "
        f"--max-instances 10 "
        f"--min-instances 0 "
        f"--set-env-vars FLASK_ENV=production "
        f"--set-env-vars DATABASE_URL=sqlite:///productivityflow_secure.db",
        "Deploying to Cloud Run"
    )
    if not deploy_result:
        return False
    
    # Get the service URL
    url_result = run_command(
        "gcloud run services describe productivityflow-backend-secure "
        "--platform managed --region us-central1 --format='value(status.url)'",
        "Getting service URL"
    )
    
    if url_result:
        service_url = url_result.strip()
        print(f"✅ Deployment successful!")
        print(f"🌐 Service URL: {service_url}")
        print(f"🔒 Health check: {service_url}/health")
        
        # Test the deployment
        print("🧪 Testing deployment...")
        time.sleep(10)  # Wait for deployment to be ready
        
        test_result = run_command(
            f"curl -s {service_url}/health",
            "Testing deployed service"
        )
        
        if test_result:
            print("✅ Deployment test successful!")
            return True
        else:
            print("⚠️ Deployment test failed, but service may still be starting up")
            return True
    
    return False

def main():
    print("🚀 ProductivityFlow Production Deployment")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        print("❌ Prerequisites not met. Please fix the issues above.")
        sys.exit(1)
    
    # Create production files
    create_production_dockerfile()
    create_requirements_file()
    
    # Deploy
    if deploy_to_cloud_run():
        print("\n🎉 Production deployment completed successfully!")
        print("Your secure backend is now live on Google Cloud Run!")
        print("\nNext steps:")
        print("1. Update your frontend apps to use the new Cloud Run URL")
        print("2. Set up a production database (PostgreSQL recommended)")
        print("3. Configure environment variables for production secrets")
        print("4. Set up monitoring and logging")
    else:
        print("\n❌ Deployment failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 