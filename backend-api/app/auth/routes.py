# app/auth/routes.py

from flask import Blueprint, request, jsonify
from app import db
from app.models import User, UserRole

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

    return jsonify({
        'message': 'User registered successfully.', 
        'user_id': user.id,
        'role': str(user.role)
    }), 201


@bp.route('/login', methods=['POST'])
def login():
    """API endpoint for user login and JWT token generation."""
    data = request.get_json()

    # 1. Input Validation
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Missing username or password.'}), 400

    # 2. Verify User Credentials
    user = User.query.filter_by(username=data['username']).first()
    
    if user is None or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid username or password.'}), 401 # 401: Unauthorized

    # 3. Generate and return JWT
    # The token is the key to accessing protected routes
    token = user.generate_auth_token()
    
    return jsonify({
        'message': 'Login successful.',
        'access_token': token,
        'token_type': 'Bearer',
        'expires_in': 3600 # 1 hour
    })