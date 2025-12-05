# app/utils.py

from functools import wraps
from flask import request, jsonify, g
from app.models import User # We use User.verify_auth_token here
from app.models import UserRole # We use this for role checks
import uuid

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

            # Check if user is active
            if not user.is_active:
                return jsonify({'message': 'Account is deactivated.'}), 403

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

def admin_required():
    """
    Decorator to enforce admin-only access.
    Must be placed *after* @jwt_required in the decorator stack.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user has admin role
            if g.current_user.role != UserRole.SYSTEM_ADMIN.value:
                return jsonify({
                    'message': 'Admin privileges required',
                    'current_role': g.current_user.role
                }), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def audit_log(action=None, resource_type=None):
    """
    Decorator to automatically log API calls to the audit log.
    Captures request details, user information, and response status.
    
    Args:
        action (str): Custom action name (if None, derives from function name)
        resource_type (str): Type of resource being accessed
    
    Usage:
        @audit_log(action='CREATE_USER', resource_type='User')
        @jwt_required()
        def create_user():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from app.services.audit_service import AuditService
            
            # Generate session ID if not exists
            if not hasattr(g, 'session_id'):
                g.session_id = str(uuid.uuid4())
            
            # Determine action name
            action_name = action or f.__name__.upper().replace('_', '_')
            
            # Store start time for duration tracking
            import time
            start_time = time.time()
            
            # Execute the route function
            try:
                response = f(*args, **kwargs)
                
                # Extract status code from response
                if isinstance(response, tuple):
                    status_code = response[1] if len(response) > 1 else 200
                    response_data = response[0]
                else:
                    status_code = 200
                    response_data = response
                
                # Extract resource_id from kwargs if available
                resource_id = kwargs.get('id') or kwargs.get('user_id') or kwargs.get('receipt_id')
                
                # Calculate duration
                duration = time.time() - start_time
                
                # Log successful action
                AuditService.log_action(
                    action=action_name,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    status_code=status_code,
                    success=200 <= status_code < 400,
                    metadata={
                        'duration_seconds': round(duration, 3),
                        'query_params': dict(request.args) if request.args else None,
                        'path_params': kwargs
                    },
                    session_id=g.session_id
                )
                
                return response
                
            except Exception as e:
                # Log failed action
                AuditService.log_action(
                    action=action_name,
                    resource_type=resource_type,
                    status_code=500,
                    success=False,
                    error_message=str(e),
                    metadata={
                        'error_type': type(e).__name__,
                        'query_params': dict(request.args) if request.args else None
                    },
                    session_id=g.session_id
                )
                # Re-raise the exception
                raise
        
        return decorated_function
    return decorator


def generate_session_id():
    """
    Generate a unique session ID for tracking user sessions.
    Call this at the start of authentication.
    
    Returns:
        str: UUID session identifier
    """
    if not hasattr(g, 'session_id'):
        g.session_id = str(uuid.uuid4())
    return g.session_id