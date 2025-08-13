#!/usr/bin/env python3
"""
Post-deployment verification script
"""
import os
import sys
import requests
import time

def verify_health_endpoint(url, max_retries=5, retry_delay=10):
    """Verify the health endpoint is responding correctly"""
    health_url = f"{url}/health/"
    
    for attempt in range(max_retries):
        try:
            print(f"Attempting to reach {health_url} (attempt {attempt + 1}/{max_retries})")
            response = requests.get(health_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy':
                    print(f"✅ Health check passed: {data}")
                    return True
                else:
                    print(f"❌ Health check failed: {data}")
            else:
                print(f"❌ Health endpoint returned status {response.status_code}")
                
        except requests.RequestException as e:
            print(f"❌ Error connecting to health endpoint: {e}")
        
        if attempt < max_retries - 1:
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
    
    return False

def verify_main_site(url):
    """Verify the main site is accessible"""
    try:
        print(f"Checking main site: {url}")
        response = requests.get(url, timeout=10, allow_redirects=True)
        
        if response.status_code == 200:
            print("✅ Main site is accessible")
            return True
        else:
            print(f"❌ Main site returned status {response.status_code}")
            
    except requests.RequestException as e:
        print(f"❌ Error connecting to main site: {e}")
    
    return False

def main():
    """Main verification function"""
    urls_to_test = [
        "https://openlinguify.com",
        "https://www.openlinguify.com",
        "https://linguify-portal.onrender.com"
    ]
    
    all_passed = True
    
    for url in urls_to_test:
        print(f"\n==> Testing {url}")
        
        # Test health endpoint
        health_passed = verify_health_endpoint(url)
        
        # Test main site
        site_passed = verify_main_site(url)
        
        if health_passed and site_passed:
            print(f"✅ {url} - All checks passed")
        else:
            print(f"❌ {url} - Some checks failed")
            all_passed = False
    
    if all_passed:
        print("\n🎉 All deployment verifications passed!")
        sys.exit(0)
    else:
        print("\n❌ Some deployment verifications failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()