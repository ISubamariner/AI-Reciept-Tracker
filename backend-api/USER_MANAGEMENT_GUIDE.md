# User Management System Documentation

## Overview

This user management system provides comprehensive functionality for managing user accounts, including:

- **User Creation** - Admin can create new user accounts
- **Profile Management** - Users can view and edit their profiles
- **Password Management** - Users can change passwords; admins can reset passwords
- **Role Management** - Admin can assign and change user roles
- **Account Status** - Admin can deactivate/reactivate accounts
- **User Listing** - Admin can view all users

## User Roles

The system supports three user roles:

1. **SYSTEM_ADMIN** - Full administrative access
   - Can create, update, and delete users
   - Can change user roles
   - Can reset passwords without verification
   - Can deactivate/reactivate accounts

2. **RECEIPT_LOGGER** - Can upload and manage receipts
   - Can upload receipts
   - Can view own transactions
   - Can manage own profile

3. **BASIC_USER** - Standard user access
   - Can view own profile
   - Can change own password
   - Can update own profile details

## API Endpoints

### Authentication Required
All user management endpoints require authentication via JWT token in the Authorization header:
```
Authorization: Bearer <your_token>
```

### 1. Create User (Admin Only)
**POST** `/api/users`

Create a new user account.

**Request Body:**
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "securePassword123",
  "role": "BASIC_USER",
  "is_active": true
}
```

**Response (201):**
```json
{
  "message": "User created successfully",
  "user": {
    "id": 1,
    "username": "newuser",
    "email": "newuser@example.com",
    "role": "Basic User",
    "is_active": true
  }
}
```

---

### 2. Get All Users (Admin Only)
**GET** `/api/users?include_inactive=false`

Retrieve list of all users.

**Query Parameters:**
- `include_inactive` (boolean, optional) - Include deactivated users (default: false)

**Response (200):**
```json
{
  "users": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "role": "System Admin",
      "is_active": true
    },
    {
      "id": 2,
      "username": "user1",
      "email": "user1@example.com",
      "role": "Basic User",
      "is_active": true
    }
  ],
  "count": 2
}
```

---

### 3. Get Current User Profile
**GET** `/api/users/me`

Get the authenticated user's profile.

**Response (200):**
```json
{
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "johndoe@example.com",
    "role": "Basic User",
    "is_active": true
  }
}
```

---

### 4. Get User by ID
**GET** `/api/users/{user_id}`

Get a specific user's profile. Users can view their own profile; admins can view any profile.

**Response (200):**
```json
{
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "johndoe@example.com",
    "role": "Basic User",
    "is_active": true
  }
}
```

---

### 5. Update User Details
**PUT** `/api/users/{user_id}`

Update username and/or email. Users can update their own profile; admins can update any profile.

**Request Body:**
```json
{
  "username": "newusername",
  "email": "newemail@example.com"
}
```

**Response (200):**
```json
{
  "message": "User updated successfully",
  "user": {
    "id": 1,
    "username": "newusername",
    "email": "newemail@example.com",
    "role": "Basic User",
    "is_active": true
  }
}
```

---

### 6. Change Password (Self)
**PUT** `/api/users/{user_id}/password`

Change user password with current password verification. Users can only change their own password.

**Request Body:**
```json
{
  "current_password": "oldPassword123",
  "new_password": "newPassword456"
}
```

**Response (200):**
```json
{
  "message": "Password changed successfully"
}
```

---

### 7. Reset Password (Admin Only)
**POST** `/api/users/{user_id}/reset-password`

Admin-only password reset without current password verification.

**Request Body:**
```json
{
  "new_password": "newPassword456"
}
```

**Response (200):**
```json
{
  "message": "Password reset successfully"
}
```

---

### 8. Change User Role (Admin Only)
**PUT** `/api/users/{user_id}/role`

Change a user's role.

**Request Body:**
```json
{
  "role": "RECEIPT_LOGGER"
}
```

**Response (200):**
```json
{
  "message": "User role updated successfully",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "johndoe@example.com",
    "role": "Receipt Logger",
    "is_active": true
  }
}
```

---

### 9. Deactivate User (Admin Only)
**POST** `/api/users/{user_id}/deactivate`

Deactivate a user account. The user will not be able to log in until reactivated. Admin cannot deactivate themselves.

**Response (200):**
```json
{
  "message": "User johndoe deactivated successfully"
}
```

---

### 10. Reactivate User (Admin Only)
**POST** `/api/users/{user_id}/reactivate`

Reactivate a deactivated user account.

**Response (200):**
```json
{
  "message": "User johndoe reactivated successfully"
}
```

---

### 11. Delete User (Admin Only)
**DELETE** `/api/users/{user_id}`

Permanently delete a user account. This action is irreversible. Consider using deactivate instead. Admin cannot delete themselves.

**Response (200):**
```json
{
  "message": "User johndoe deleted permanently"
}
```

---

### 12. Get Available Roles
**GET** `/api/users/roles`

Get list of available user roles.

**Response (200):**
```json
{
  "roles": [
    {
      "name": "SYSTEM_ADMIN",
      "value": "System Admin"
    },
    {
      "name": "RECEIPT_LOGGER",
      "value": "Receipt Logger"
    },
    {
      "name": "BASIC_USER",
      "value": "Basic User"
    }
  ]
}
```

## Error Responses

### 400 Bad Request
```json
{
  "message": "Error description"
}
```

### 401 Unauthorized
```json
{
  "message": "Invalid or expired token"
}
```

### 403 Forbidden
```json
{
  "message": "Admin privileges required",
  "current_role": "Basic User"
}
```

### 404 Not Found
```json
{
  "message": "User not found"
}
```

## Usage Examples

### Python Example

```python
import requests

BASE_URL = "http://localhost:5000/api"

# Login to get token
response = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "admin",
    "password": "admin123"
})
token = response.json()['access_token']
headers = {"Authorization": f"Bearer {token}"}

# Create a new user
response = requests.post(f"{BASE_URL}/users", headers=headers, json={
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "password123",
    "role": "BASIC_USER"
})
print(response.json())

# Get all users
response = requests.get(f"{BASE_URL}/users", headers=headers)
print(response.json())

# Update user role
user_id = 2
response = requests.put(f"{BASE_URL}/users/{user_id}/role", 
                       headers=headers, 
                       json={"role": "RECEIPT_LOGGER"})
print(response.json())
```

### cURL Example

```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Create user (replace TOKEN with actual token)
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "password123",
    "role": "BASIC_USER"
  }'

# Get all users
curl -X GET http://localhost:5000/api/users \
  -H "Authorization: Bearer TOKEN"

# Deactivate user
curl -X POST http://localhost:5000/api/users/2/deactivate \
  -H "Authorization: Bearer TOKEN"
```

## Architecture

### Service Layer
The `UserManagementService` class in `app/services/user_management_service.py` handles all business logic:

- User creation and validation
- Password management
- Role changes
- Account activation/deactivation
- User deletion

### Routes Layer
The `app/users/routes.py` blueprint provides REST API endpoints with:

- Request validation
- Authentication and authorization checks
- Error handling
- Response formatting

### Security Features

1. **JWT Authentication** - All endpoints require valid JWT token
2. **Role-Based Access Control** - Admin-only operations are protected
3. **Password Hashing** - Bcrypt hashing for all passwords
4. **Account Status Check** - Deactivated users cannot authenticate
5. **Self-Protection** - Admins cannot deactivate or delete themselves

## Testing

Run the test script to verify all functionality:

```bash
python test_user_management.py
```

This will test:
- User registration
- Login
- User creation
- Profile viewing
- Profile updates
- Password changes
- Role changes
- Account deactivation/reactivation
- User deletion

## Database Schema

The User model includes:

```python
class User(db.Model):
    id = Integer (Primary Key)
    username = String(64) (Unique, Not Null)
    email = String(120) (Unique, Not Null)
    password_hash = String(128) (Not Null)
    role = Enum (Not Null, Default: BASIC_USER)
    is_active = Boolean (Default: True)
```

## Integration with Existing System

The user management system integrates seamlessly with:

- **Authentication** - Uses existing JWT token system
- **Receipts** - Users can upload receipts based on their role
- **Transactions** - Transactions are linked to user accounts

## Swagger Documentation

All endpoints are documented in Swagger UI at:
```
http://localhost:5000/api/docs
```

Navigate to the "User Management" section to see:
- Interactive API testing
- Request/response schemas
- Authentication requirements
- Example payloads
