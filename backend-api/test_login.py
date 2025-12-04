"""Test the login endpoint with detailed error reporting."""
import requests
import json
import traceback

url = 'http://localhost:5000/api/auth/login'
data = {'username': 'test', 'password': 'test'}

print(f"Testing login at {url}")
print(f"Payload: {json.dumps(data)}")
print("="*50)

try:
    response = requests.post(
        url,
        json=data,
        headers={'Content-Type': 'application/json'},
        timeout=5
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Content: {response.text}")
    
    if response.status_code == 200:
        print("\nLogin successful!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"\nLogin failed with status {response.status_code}")
        
except requests.exceptions.ConnectionError as e:
    print(f"Connection Error: {e}")
    print("\nThe server may have crashed. Check the server terminal for errors.")
except requests.exceptions.Timeout:
    print("Request timed out")
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
