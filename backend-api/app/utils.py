# app/utils.py

from functools import wraps
from flask import request, jsonify, g
from app.models import User # We use User.verify_auth_token here
from app.models import UserRole # We use this for role checks

def jwt_required():
    """
    Decorator to protect API routes. Checks for a valid JWT in the Authorization header.
    Stores the current authenticated user in the Flask global object (g.current_user).
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            
            # 1. Get token from header
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({'message': 'Authorization token is missing.'}), 401 # Unauthorized

            try:
                # Expects format: "Bearer <token>"
                token = auth_header.split()[1]
            except IndexError:
                return jsonify({'message': 'Token format is invalid. Use "Bearer <token>".'}), 401

            # 2. Verify token and retrieve user
            user = User.verify_auth_token(token)
            
            if user is None:
                # This covers invalid signature and token expiration
                return jsonify({'message': 'Invalid or expired token.'}), 401

            # 3. Store user in global context (g) for route access
            g.current_user = user
            
            # 4. Execute the original route function
            return f(*args, **kwargs)

        return decorated_function
    return decorator

def role_required(roles):
    """
    Decorator to enforce specific user roles (Role-Based Access Control).
    'roles' should be a list/tuple of UserRole Enum members (e.g., [UserRole.SYSTEM_ADMIN]).
    Must be placed *after* @jwt_required in the decorator stack.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if the authenticated user's role is in the list of allowed roles
            # Handle both Enum objects and string values from the DB
            user_role = g.current_user.role
            allowed_values = [r.value for r in roles]
            
            if user_role not in allowed_values and user_role not in roles:
                 return jsonify({'message': 'Permission denied: Insufficient role access.'}), 403 # Forbidden
            return f(*args, **kwargs)
        return decorated_function
    return decorator