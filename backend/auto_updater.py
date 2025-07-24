#!/usr/bin/env python3
"""
ProductivityFlow Auto-Updater System
Handles automatic updates for both Employee Tracker and Manager Dashboard applications
"""

import os
import sys
import json
import hashlib
import requests
import subprocess
import platform
import zipfile
import shutil
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AutoUpdater:
    def __init__(self, app_name="productivityflow"):
        self.app_name = app_name
        self.current_version = self.get_current_version()
        self.update_server_url = "https://productivityflow-backend.onrender.com"
        self.platform = self.get_platform()
        self.app_data_dir = self.get_app_data_directory()
        
    def get_current_version(self):
        """Get current application version"""
        try:
            # Try to read version from package.json or similar
            if os.path.exists("package.json"):
                with open("package.json", "r") as f:
                    data = json.load(f)
                    return data.get("version", "1.0.0")
            elif os.path.exists("version.txt"):
                with open("version.txt", "r") as f:
                    return f.read().strip()
            else:
                return "1.0.0"
        except Exception as e:
            logger.warning(f"Could not read current version: {e}")
            return "1.0.0"
    
    def get_platform(self):
        """Get current platform information"""
        system = platform.system().lower()
        machine = platform.machine().lower()
        
        if system == "darwin":
            if "arm" in machine or "aarch64" in machine:
                return "macos-arm64"
            else:
                return "macos-x64"
        elif system == "windows":
            return "windows-x64"
        elif system == "linux":
            return "linux-x64"
        else:
            return "unknown"
    
    def get_app_data_directory(self):
        """Get application data directory for storing updates"""
        if platform.system() == "Darwin":
            return os.path.expanduser("~/Library/Application Support/ProductivityFlow")
        elif platform.system() == "Windows":
            return os.path.join(os.getenv("APPDATA"), "ProductivityFlow")
        else:
            return os.path.expanduser("~/.productivityflow")
    
    def check_for_updates(self):
        """Check for available updates"""
        try:
            url = f"{self.update_server_url}/api/updates/{self.app_name}/latest"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                update_info = response.json()
                latest_version = update_info.get("version")
                
                if self.is_newer_version(latest_version, self.current_version):
                    return {
                        "available": True,
                        "current_version": self.current_version,
                        "latest_version": latest_version,
                        "download_url": update_info.get("download_url"),
                        "release_notes": update_info.get("release_notes", ""),
                        "file_size": update_info.get("file_size", 0),
                        "checksum": update_info.get("checksum", "")
                    }
            
            return {"available": False}
            
        except Exception as e:
            logger.error(f"Failed to check for updates: {e}")
            return {"available": False, "error": str(e)}
    
    def is_newer_version(self, new_version, current_version):
        """Compare version strings to determine if new version is newer"""
        try:
            new_parts = [int(x) for x in new_version.split('.')]
            current_parts = [int(x) for x in current_version.split('.')]
            
            # Pad with zeros if needed
            max_len = max(len(new_parts), len(current_parts))
            new_parts.extend([0] * (max_len - len(new_parts)))
            current_parts.extend([0] * (max_len - len(current_parts)))
            
            return new_parts > current_parts
        except Exception:
            return False
    
    def download_update(self, download_url, file_size=0):
        """Download the update file"""
        try:
            # Create downloads directory
            downloads_dir = os.path.join(self.app_data_dir, "downloads")
            os.makedirs(downloads_dir, exist_ok=True)
            
            # Generate filename
            filename = f"{self.app_name}-{self.platform}-update.zip"
            filepath = os.path.join(downloads_dir, filename)
            
            logger.info(f"Downloading update from {download_url}")
            
            # Download with progress
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Log progress
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            logger.info(f"Download progress: {progress:.1f}%")
            
            logger.info(f"Download completed: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to download update: {e}")
            raise
    
    def verify_checksum(self, filepath, expected_checksum):
        """Verify file checksum"""
        try:
            with open(filepath, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            
            return file_hash == expected_checksum
        except Exception as e:
            logger.error(f"Failed to verify checksum: {e}")
            return False
    
    def install_update(self, update_filepath):
        """Install the downloaded update"""
        try:
            logger.info("Starting update installation...")
            
            # Create backup directory
            backup_dir = os.path.join(self.app_data_dir, "backups")
            os.makedirs(backup_dir, exist_ok=True)
            
            # Create backup of current version
            backup_name = f"backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            backup_path = os.path.join(backup_dir, backup_name)
            
            if os.path.exists("app"):
                shutil.copytree("app", backup_path)
                logger.info(f"Created backup at {backup_path}")
            
            # Extract update
            with zipfile.ZipFile(update_filepath, 'r') as zip_ref:
                zip_ref.extractall("temp_update")
            
            # Install update
            if os.path.exists("temp_update/app"):
                if os.path.exists("app"):
                    shutil.rmtree("app")
                shutil.move("temp_update/app", "app")
            
            # Clean up
            shutil.rmtree("temp_update")
            os.remove(update_filepath)
            
            logger.info("Update installation completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Failed to install update: {e}")
            
            # Try to restore from backup
            try:
                if os.path.exists(backup_path):
                    if os.path.exists("app"):
                        shutil.rmtree("app")
                    shutil.move(backup_path, "app")
                    logger.info("Restored from backup after failed update")
            except Exception as restore_error:
                logger.error(f"Failed to restore from backup: {restore_error}")
            
            raise
    
    def restart_application(self):
        """Restart the application after update"""
        try:
            logger.info("Restarting application...")
            
            # Get the current script path
            script_path = sys.argv[0]
            
            # Start new process
            subprocess.Popen([sys.executable, script_path])
            
            # Exit current process
            sys.exit(0)
            
        except Exception as e:
            logger.error(f"Failed to restart application: {e}")
    
    def run_auto_update(self, auto_install=True):
        """Run the complete auto-update process"""
        try:
            logger.info("Checking for updates...")
            
            # Check for updates
            update_info = self.check_for_updates()
            
            if not update_info.get("available"):
                logger.info("No updates available")
                return {"success": True, "message": "No updates available"}
            
            logger.info(f"Update available: {update_info['latest_version']}")
            
            if not auto_install:
                return {
                    "success": True,
                    "update_available": True,
                    "update_info": update_info
                }
            
            # Download update
            download_url = update_info["download_url"]
            filepath = self.download_update(download_url, update_info.get("file_size", 0))
            
            # Verify checksum if provided
            if update_info.get("checksum"):
                if not self.verify_checksum(filepath, update_info["checksum"]):
                    raise Exception("Checksum verification failed")
            
            # Install update
            self.install_update(filepath)
            
            # Restart application
            self.restart_application()
            
            return {"success": True, "message": "Update completed successfully"}
            
        except Exception as e:
            logger.error(f"Auto-update failed: {e}")
            return {"success": False, "error": str(e)}

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ProductivityFlow Auto-Updater")
    parser.add_argument("--check", action="store_true", help="Check for updates only")
    parser.add_argument("--install", action="store_true", help="Install available updates")
    parser.add_argument("--app", default="productivityflow", help="Application name")
    
    args = parser.parse_args()
    
    updater = AutoUpdater(args.app)
    
    if args.check:
        update_info = updater.check_for_updates()
        if update_info.get("available"):
            print(f"Update available: {update_info['latest_version']}")
            print(f"Current version: {update_info['current_version']}")
            if update_info.get("release_notes"):
                print(f"Release notes: {update_info['release_notes']}")
        else:
            print("No updates available")
    
    elif args.install:
        result = updater.run_auto_update(auto_install=True)
        if result["success"]:
            print("Update completed successfully")
        else:
            print(f"Update failed: {result['error']}")
            sys.exit(1)
    
    else:
        # Default: check and install if available
        result = updater.run_auto_update(auto_install=True)
        if not result["success"]:
            print(f"Auto-update failed: {result['error']}")
            sys.exit(1)

if __name__ == "__main__":
    main() 