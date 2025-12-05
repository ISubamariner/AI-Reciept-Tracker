# app/auth/routes.py

from flask import Blueprint, request, jsonify, g
from app import db
from app.models import User, UserRole
from app.services.audit_service import AuditService
from app.utils import generate_session_id

# Define the Blueprint. The URL prefix will be '/api/auth' when registered.
bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['POST'])
def register():
    """API endpoint for new user registration."""
    data = request.get_json()

    # 1. Input Validation: Check for required fields
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing required fields: username, email, and password.'}), 400

    username = data['username']
    email = data['email']
    password = data['password']
    
    # Optional: Allow setting a role for initial setup, default to BASIC_USER
    role_str = data.get('role', 'BASIC_USER').upper()
    try:
        # Convert string input to the defined UserRole Enum
        role_enum = UserRole[role_str]
        role = role_enum.value
    except KeyError:
        return jsonify({'message': f'Invalid role specified. Must be one of: {", ".join(r.name for r in UserRole)}'}), 400

    # 2. Check if user already exists
    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists.'}), 409
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already registered.'}), 409

    # 3. Create and save the new user
    user = User(username=username, email=email, role=role)
    user.set_password(password) # Hash the password
    
    db.session.add(user)
    db.session.commit()

    # Log registration
    AuditService.log_action(
        action='USER_REGISTRATION',
        resource_type='User',
        resource_id=user.id,
        username=username,
        user_role=role,
        status_code=201,
        success=True,
        metadata={'email': email}
    )

    return jsonify({
        'message': 'User registered successfully.', 
        'user_id': user.id,
        'role': str(user.role)
    }), 201


@bp.route('/login', methods=['POST'])
def login():
    """API endpoint for user login and JWT token generation."""
    try:
        data = request.get_json()

        # 1. Input Validation
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'message': 'Missing username or password.'}), 400

        # 2. Verify User Credentials
        user = User.query.filter_by(username=data['username']).first()
        
        if user is None or not user.check_password(data['password']):
            # Log failed login attempt
            AuditService.log_authentication(
                action='LOGIN_FAILED',
                username=data['username'],
                success=False,
                error_message='Invalid username or password',
                metadata={'reason': 'invalid_credentials'}
            )
            return jsonify({'message': 'Invalid username or password.'}), 401 # 401: Unauthorized

        # 3. Generate session ID and JWT
        session_id = generate_session_id()
        token = user.generate_auth_token()
        
        # Log successful login
        AuditService.log_authentication(
            action='LOGIN',
            username=user.username,
            success=True,
            metadata={
                'user_id': user.id,
                'role': user.role,
                'session_id': session_id
            }
        )
        
        return jsonify({
            'message': 'Login successful.',
            'access_token': token,
            'token_type': 'Bearer',
            'expires_in': 3600 # 1 hour
        })
    except Exception as e:
        import traceback
        print(f"Login error: {e}")
        print(traceback.format_exc())
        
        # Log error
        AuditService.log_authentication(
            action='LOGIN_ERROR',
            username=data.get('username') if data else 'unknown',
            success=False,
            error_message=str(e)
        )
        
        return jsonify({'message': 'Internal server error', 'error': str(e)}), 500


@bp.route('/logout', methods=['POST'])
def logout():
    """API endpoint for user logout (audit logging only)."""
    from app.utils import jwt_required
    from functools import wraps
    
    # Try to extract user info if token is present
    auth_header = request.headers.get('Authorization')
    user_info = None
    
    if auth_header:
        try:
            token = auth_header.split()[1]
            user = User.verify_auth_token(token)
            if user:
                user_info = {
                    'user_id': user.id,
                    'username': user.username,
                    'role': user.role
                }
        except:
            pass
    
    # Log logout
    if user_info:
        AuditService.log_authentication(
            action='LOGOUT',
            username=user_info['username'],
            success=True,
            metadata=user_info
        )
    
    return jsonify({
        'message': 'Logout successful.'
    }), 200