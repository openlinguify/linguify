"""
Test SEO URLs and functionality
"""

import requests
import sys

def test_seo_urls():
    """Test all SEO URLs"""
    base_url = "http://127.0.0.1:8000"
    
    urls_to_test = [
        "/robots.txt",
        "/sitemap.xml", 
        "/sitemap-index.xml",
        "/sitemap-static.xml",
        "/sitemap-images.xml",
        "/sitemap-videos.xml",
        "/seo/status/",
    ]
    
    print("🧪 Testing SEO URLs...")
    print("⚠️  Make sure Django server is running: python manage.py runserver")
    print()
    
    success_count = 0
    total_count = len(urls_to_test)
    
    for url in urls_to_test:
        full_url = base_url + url
        try:
            response = requests.get(full_url, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {url} - OK ({len(response.content)} bytes)")
                success_count += 1
            elif response.status_code == 404:
                print(f"❌ {url} - Not Found (404)")
            else:
                print(f"⚠️  {url} - HTTP {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"🔌 {url} - Server not running")
        except Exception as e:
            print(f"❌ {url} - Error: {e}")
    
    print()
    print(f"📊 Results: {success_count}/{total_count} URLs working")
    
    if success_count == total_count:
        print("🎉 All SEO URLs are working perfectly!")
        return True
    elif success_count > 0:
        print("⚠️  Some URLs are working, check server configuration")
        return False
    else:
        print("💥 No URLs working - check if Django server is running")
        return False

if __name__ == "__main__":
    success = test_seo_urls()
    sys.exit(0 if success else 1)