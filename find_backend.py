#!/usr/bin/env python3
"""
Script to find the correct backend URL by testing various possibilities
"""

import requests
import time
from urllib.parse import urljoin

def test_backend_url(base_url):
    """Test if a backend URL is working"""
    try:
        # Test health endpoint
        health_url = urljoin(base_url, '/api/health')
        response = requests.get(health_url, timeout=10)
        
        if response.status_code == 200:
            try:
                data = response.json()
                return True, f"✅ {base_url} - Online (Health: {data})"
            except:
                return True, f"✅ {base_url} - Online (Status: {response.status_code})"
        else:
            return False, f"❌ {base_url} - Error {response.status_code}"
            
    except requests.exceptions.RequestException as e:
        return False, f"❌ {base_url} - Offline ({str(e)})"

def main():
    print("🔍 Searching for working backend URLs...\n")
    
    # List of possible backend URLs - Google Cloud Run format
    possible_urls = [
        # Google Cloud Run URLs (from user)
        "https://productivityflow-backend-00012-72v.a.run.app",
        "https://productivityflow-backend.a.run.app",
        "https://productivityflow-api.a.run.app",
        "https://productivityflow-backend-v1.a.run.app",
        "https://productivityflow-backend-v2.a.run.app",
        "https://productivityflow-backend-v3.a.run.app",
        
        # Render URLs (fallback)
        "https://productivityflow-backend-v3.onrender.com",
        "https://productivityflow-backend-v2.onrender.com", 
        "https://productivityflow-backend-v1.onrender.com",
        "https://productivityflow-backend.onrender.com",
        "https://productivityflow-api.onrender.com",
        "https://productivityflow-backend-v4.onrender.com",
        "https://productivityflow-backend-v5.onrender.com",
        "https://productivityflow.onrender.com",
        "https://productivityflow-api-v3.onrender.com",
        "https://productivityflow-api-v2.onrender.com",
        "https://productivityflow-api-v1.onrender.com"
    ]
    
    working_urls = []
    
    for url in possible_urls:
        print(f"Testing {url}...")
        is_working, message = test_backend_url(url)
        print(f"  {message}")
        
        if is_working:
            working_urls.append(url)
        
        # Small delay to avoid overwhelming servers
        time.sleep(1)
    
    print(f"\n📊 Results:")
    print(f"Total URLs tested: {len(possible_urls)}")
    print(f"Working URLs found: {len(working_urls)}")
    
    if working_urls:
        print(f"\n✅ Working backend URLs:")
        for url in working_urls:
            print(f"  - {url}")
        
        print(f"\n🎯 Recommended URL: {working_urls[0]}")
    else:
        print(f"\n❌ No working backend URLs found!")
        print(f"This could mean:")
        print(f"  1. All backends are down")
        print(f"  2. Deployment is in progress")
        print(f"  3. URLs have changed")
        print(f"  4. Network connectivity issues")
        print(f"\n🔧 Next steps:")
        print(f"  1. Check Google Cloud Run console for deployment status")
        print(f"  2. Wait for deployment to complete (usually 5-10 minutes)")
        print(f"  3. Use local backend for immediate testing: python3 start_local_backend.py")

if __name__ == "__main__":
    main() 