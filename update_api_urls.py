#!/usr/bin/env python3
"""
Update API URLs in desktop apps to use new Google Cloud Run backend
"""

import os
import re

# New backend URL (updated to the latest deployment)
NEW_BACKEND_URL = "https://productivityflow-backend-ilmu4h3uza-uc.a.run.app"

# Old URLs to replace
OLD_URLS = [
    "https://productivityflow-backend.onrender.com",
    "https://productivityflow-backend-496367590729.us-central1.run.app",
    "http://localhost:5000",
    "http://127.0.0.1:5000"
]

def update_file(file_path):
    """Update API URLs in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace old URLs with new URL
        for old_url in OLD_URLS:
            content = content.replace(old_url, NEW_BACKEND_URL)
        
        # If content changed, write it back
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Updated: {file_path}")
            return True
        else:
            print(f"⏭️  No changes needed: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False

def main():
    """Update all desktop app files"""
    print(f"🔄 Updating API URLs to: {NEW_BACKEND_URL}")
    print("=" * 60)
    
    # Files to update
    files_to_update = [
        "employee-tracker-tauri/src/App.tsx",
        "manager-dashboard-tauri/src/App.tsx",
        "desktop-tracker/src/App.jsx",
        "web-dashboard/src/App.jsx"
    ]
    
    updated_count = 0
    for file_path in files_to_update:
        if os.path.exists(file_path):
            if update_file(file_path):
                updated_count += 1
        else:
            print(f"⚠️  File not found: {file_path}")
    
    print("=" * 60)
    print(f"✅ Updated {updated_count} files")
    print(f"🌐 New backend URL: {NEW_BACKEND_URL}")

if __name__ == "__main__":
    main() 