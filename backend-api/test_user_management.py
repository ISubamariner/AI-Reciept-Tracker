# test_user_management.py
"""
Test script for User Management API endpoints.
Run this after starting the server to test user management functionality.
"""

import requests
import json

BASE_URL = "http://localhost:5000/api"

def print_response(response):
    """Pretty print response"""
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    print("-" * 50)

def test_user_management():
    """Test user management endpoints"""
    
    print("=" * 50)
    print("USER MANAGEMENT API TESTS")
    print("=" * 50)
    
    # Step 1: Register an admin user
    print("\n1. Registering admin user...")
    response = requests.post(f"{BASE_URL}/auth/register", json={
        "username": "admin",
        "email": "admin@example.com",
        "password": "admin123",
        "role": "SYSTEM_ADMIN"
    })
    print_response(response)
    
    # Step 2: Login as admin
    print("\n2. Logging in as admin...")
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    print_response(response)
    
    if response.status_code == 200:
        admin_token = response.json()['access_token']
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Step 3: Get current user profile
        print("\n3. Getting current user profile...")
        response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        print_response(response)
        
        # Step 4: Get available roles
        print("\n4. Getting available roles...")
        response = requests.get(f"{BASE_URL}/users/roles", headers=headers)
        print_response(response)
        
        # Step 5: Create a new user
        print("\n5. Creating new user...")
        response = requests.post(f"{BASE_URL}/users", headers=headers, json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "test123",
            "role": "BASIC_USER"
        })
        print_response(response)
        
        if response.status_code == 201:
            user_id = response.json()['user']['id']
            
            # Step 6: Get all users
            print("\n6. Getting all users...")
            response = requests.get(f"{BASE_URL}/users", headers=headers)
            print_response(response)
            
            # Step 7: Get specific user
            print(f"\n7. Getting user {user_id}...")
            response = requests.get(f"{BASE_URL}/users/{user_id}", headers=headers)
            print_response(response)
            
            # Step 8: Update user details
            print(f"\n8. Updating user {user_id} details...")
            response = requests.put(f"{BASE_URL}/users/{user_id}", headers=headers, json={
                "username": "testuser_updated",
                "email": "testuser_updated@example.com"
            })
            print_response(response)
            
            # Step 9: Change user role
            print(f"\n9. Changing user {user_id} role...")
            response = requests.put(f"{BASE_URL}/users/{user_id}/role", headers=headers, json={
                "role": "RECEIPT_LOGGER"
            })
            print_response(response)
            
            # Step 10: Reset user password (admin)
            print(f"\n10. Resetting user {user_id} password (admin)...")
            response = requests.post(f"{BASE_URL}/users/{user_id}/reset-password", headers=headers, json={
                "new_password": "newpassword123"
            })
            print_response(response)
            
            # Step 11: Deactivate user
            print(f"\n11. Deactivating user {user_id}...")
            response = requests.post(f"{BASE_URL}/users/{user_id}/deactivate", headers=headers)
            print_response(response)
            
            # Step 12: Get all users including inactive
            print("\n12. Getting all users (including inactive)...")
            response = requests.get(f"{BASE_URL}/users?include_inactive=true", headers=headers)
            print_response(response)
            
            # Step 13: Reactivate user
            print(f"\n13. Reactivating user {user_id}...")
            response = requests.post(f"{BASE_URL}/users/{user_id}/reactivate", headers=headers)
            print_response(response)
            
            # Step 14: Login as the test user
            print("\n14. Logging in as test user...")
            response = requests.post(f"{BASE_URL}/auth/login", json={
                "username": "testuser_updated",
                "password": "newpassword123"
            })
            print_response(response)
            
            if response.status_code == 200:
                user_token = response.json()['access_token']
                user_headers = {"Authorization": f"Bearer {user_token}"}
                
                # Step 15: Test user changing their own password
                print(f"\n15. User {user_id} changing own password...")
                response = requests.put(f"{BASE_URL}/users/{user_id}/password", 
                                       headers=user_headers, 
                                       json={
                    "current_password": "newpassword123",
                    "new_password": "mynewpassword"
                })
                print_response(response)
                
                # Step 16: Test user updating their own profile
                print(f"\n16. User {user_id} updating own profile...")
                response = requests.put(f"{BASE_URL}/users/{user_id}", 
                                       headers=user_headers, 
                                       json={
                    "email": "mynewemail@example.com"
                })
                print_response(response)
            
            # Step 17: Delete user (as admin)
            print(f"\n17. Deleting user {user_id} (as admin)...")
            response = requests.delete(f"{BASE_URL}/users/{user_id}", headers=headers)
            print_response(response)
    
    print("\n" + "=" * 50)
    print("TESTS COMPLETED")
    print("=" * 50)

if __name__ == "__main__":
    try:
        test_user_management()
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to server. Make sure the server is running on http://localhost:5000")
    except Exception as e:
        print(f"ERROR: {e}")
