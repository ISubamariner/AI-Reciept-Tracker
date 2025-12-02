import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"

def test_api():
    print("Starting API Test...")
    try:
        requests.get(BASE_URL.replace("/api", "/")) # Check root if possible, or just proceed
    except Exception as e:
        print(f"Server check failed: {e}")
        # return # Don't return, try endpoints anyway

    # 1. Register
    print("\n--- 1. Testing Registration ---")
    register_url = f"{BASE_URL}/auth/register"
    user_data = {
        "username": "testuser_logger",
        "email": "logger@example.com",
        "password": "password123",
        "role": "RECEIPT_LOGGER"
    }
    response = requests.post(register_url, json=user_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 409:
        print("User already exists, proceeding to login...")

    # 2. Login
    print("\n--- 2. Testing Login ---")
    login_url = f"{BASE_URL}/auth/login"
    login_data = {
        "username": "testuser_logger",
        "password": "password123"
    }
    response = requests.post(login_url, json=login_data)
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Response: {data}")
    
    if response.status_code != 200:
        print("Login failed, exiting.")
        return

    token = data['access_token']
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Upload Receipt
    print("\n--- 3. Testing Receipt Upload ---")
    upload_url = f"{BASE_URL}/receipts/upload"
    # Using a sample receipt image URL
    receipt_data = {
        "image_url": "https://templates.invoicehome.com/receipt-template-us-classic-white-750px.png" 
    }
    
    response = requests.post(upload_url, json=receipt_data, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    test_api()
