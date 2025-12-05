# test_swagger.py
# Quick test to verify Swagger UI is working

import requests
import sys

BASE_URL = "http://localhost:5000"

def test_health_endpoint():
    """Test the health check endpoint"""
    print("Testing /api/health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check successful!")
            print(f"   Status: {data.get('status')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Database: {data.get('services', {}).get('database')}")
            print(f"   Gemini API: {data.get('services', {}).get('gemini_api')}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to server: {e}")
        print("   Make sure the server is running on http://localhost:5000")
        return False

def test_swagger_json():
    """Test if swagger.json is accessible"""
    print("\nTesting /swagger.json endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/swagger.json", timeout=5)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Swagger JSON accessible!")
            print(f"   API Title: {data.get('info', {}).get('title')}")
            print(f"   API Version: {data.get('info', {}).get('version')}")
            print(f"   Endpoints defined: {len(data.get('paths', {}))}")
            return True
        else:
            print(f"❌ Swagger JSON failed with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return False

def test_swagger_ui():
    """Test if Swagger UI page is accessible"""
    print("\nTesting /api/docs (Swagger UI) endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/docs/", timeout=5)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Swagger UI is accessible!")
            print(f"   URL: {BASE_URL}/api/docs/")
            return True
        else:
            print(f"❌ Swagger UI failed with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("API & Swagger Integration Test")
    print("=" * 60)
    print()
    
    results = []
    results.append(test_health_endpoint())
    results.append(test_swagger_json())
    results.append(test_swagger_ui())
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ All tests passed!")
        print(f"\n🎉 Swagger UI is available at: {BASE_URL}/api/docs/")
        print("   You can now view and test all API endpoints!")
    else:
        print("❌ Some tests failed")
        print("   Please check the server logs for details")
        sys.exit(1)
    print("=" * 60)
