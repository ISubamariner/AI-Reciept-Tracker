# app/users/routes.py

from flask import Blueprint, request, jsonify, g
from app.services.user_management_service import UserManagementService
from app.utils import jwt_required, admin_required, audit_log
from app.models import UserRole

# Define the Blueprint for user management
bp = Blueprint('users', __name__)

@bp.route('/users', methods=['POST'])
@audit_log(action='CREATE_USER', resource_type='User')
@jwt_required()
@admin_required()
def create_user():
    """
    Create a new user account (Admin only).
    
    Required JSON body:
        - username (str): Unique username
        - email (str): Unique email address
        - password (str): User password
        - role (str, optional): User role (default: BASIC_USER)
        - is_active (bool, optional): Account status (default: true)
    """
    data = request.get_json()
    
    # Validate required fields
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing required fields: username, email, password'}), 400
    
    username = data['username']
    email = data['email']
    password = data['password']
    role = data.get('role', 'BASIC_USER')
    is_active = data.get('is_active', True)
    
    # Create user using service
    success, result = UserManagementService.create_user(
        username=username,
        email=email,
        password=password,
        role=role,
        is_active=is_active
    )
    
    if success:
        return jsonify({
            'message': 'User created successfully',
            'user': result
        }), 201
    else:
        return jsonify({'message': result}), 400


@bp.route('/users', methods=['GET'])
@audit_log(action='LIST_USERS', resource_type='User')
@jwt_required()
@admin_required()
def get_all_users():
    """
    Get all users (Admin only).
    
    Query parameters:
        - include_inactive (bool): Include deactivated users (default: false)
    """
    include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
    
    users = UserManagementService.get_all_users(include_inactive=include_inactive)
    
    return jsonify({
        'users': users,
        'count': len(users)
    }), 200


@bp.route('/users/<int:user_id>', methods=['GET'])
@audit_log(action='VIEW_USER', resource_type='User')
@jwt_required()
def get_user(user_id):
    """
    Get a specific user by ID.
    Users can view their own profile, admins can view any profile.
    """
    # Check if user is requesting their own profile or is admin
    if g.current_user.id != user_id and g.current_user.role != UserRole.SYSTEM_ADMIN.value:
        return jsonify({'message': 'Permission denied'}), 403
    
    user = UserManagementService.get_user_by_id(user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    return jsonify({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'is_active': user.is_active
        }
    }), 200


@bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """
    Update user details (username and/or email).
    Users can update their own profile, admins can update any profile.
    
    JSON body:
        - username (str, optional): New username
        - email (str, optional): New email
    """
    # Check if user is updating their own profile or is admin
    if g.current_user.id != user_id and g.current_user.role != UserRole.SYSTEM_ADMIN.value:
        return jsonify({'message': 'Permission denied'}), 403
    
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    
    username = data.get('username')
    email = data.get('email')
    
    success, result = UserManagementService.update_user_details(
        user_id=user_id,
        username=username,
        email=email
    )
    
    if success:
        return jsonify({
            'message': 'User updated successfully',
            'user': result
        }), 200
    else:
        return jsonify({'message': result}), 400


@bp.route('/users/<int:user_id>/password', methods=['PUT'])
@jwt_required()
def change_password(user_id):
    """
    Change user password.
    Users can change their own password by providing current password.
    
    JSON body:
        - current_password (str): Current password for verification
        - new_password (str): New password
    """
    # Only the user themselves can change their password this way
    if g.current_user.id != user_id:
        return jsonify({'message': 'Permission denied'}), 403
    
    data = request.get_json()
    
    if not data or not data.get('current_password') or not data.get('new_password'):
        return jsonify({'message': 'Missing required fields: current_password, new_password'}), 400
    
    current_password = data['current_password']
    new_password = data['new_password']
    
    success, message = UserManagementService.change_password(
        user_id=user_id,
        current_password=current_password,
        new_password=new_password
    )
    
    if success:
        return jsonify({'message': message}), 200
    else:
        return jsonify({'message': message}), 400


@bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@jwt_required()
@admin_required()
def admin_reset_password(user_id):
    """
    Admin-only password reset (no current password required).
    
    JSON body:
        - new_password (str): New password
    """
    data = request.get_json()
    
    if not data or not data.get('new_password'):
        return jsonify({'message': 'Missing required field: new_password'}), 400
    
    new_password = data['new_password']
    
    success, message = UserManagementService.admin_reset_password(
        user_id=user_id,
        new_password=new_password
    )
    
    if success:
        return jsonify({'message': message}), 200
    else:
        return jsonify({'message': message}), 400


@bp.route('/users/<int:user_id>/role', methods=['PUT'])
@jwt_required()
@admin_required()
def change_user_role(user_id):
    """
    Change user role (Admin only).
    
    JSON body:
        - role (str): New role (SYSTEM_ADMIN, RECEIPT_LOGGER, BASIC_USER)
    """
    data = request.get_json()
    
    if not data or not data.get('role'):
        return jsonify({'message': 'Missing required field: role'}), 400
    
    new_role = data['role']
    
    success, result = UserManagementService.change_user_role(
        user_id=user_id,
        new_role=new_role
    )
    
    if success:
        return jsonify({
            'message': 'User role updated successfully',
            'user': result
        }), 200
    else:
        return jsonify({'message': result}), 400


@bp.route('/users/<int:user_id>/deactivate', methods=['POST'])
@jwt_required()
@admin_required()
def deactivate_user(user_id):
    """
    Deactivate a user account (Admin only).
    The user will not be able to log in until reactivated.
    """
    # Prevent admin from deactivating themselves
    if g.current_user.id == user_id:
        return jsonify({'message': 'Cannot deactivate your own account'}), 400
    
    success, message = UserManagementService.deactivate_user(user_id)
    
    if success:
        return jsonify({'message': message}), 200
    else:
        return jsonify({'message': message}), 400


@bp.route('/users/<int:user_id>/reactivate', methods=['POST'])
@jwt_required()
@admin_required()
def reactivate_user(user_id):
    """
    Reactivate a deactivated user account (Admin only).
    """
    success, message = UserManagementService.reactivate_user(user_id)
    
    if success:
        return jsonify({'message': message}), 200
    else:
        return jsonify({'message': message}), 400


@bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_user(user_id):
    """
    Permanently delete a user account (Admin only).
    WARNING: This action is irreversible. Consider using deactivate instead.
    """
    # Prevent admin from deleting themselves
    if g.current_user.id == user_id:
        return jsonify({'message': 'Cannot delete your own account'}), 400
    
    success, message = UserManagementService.delete_user(user_id)
    
    if success:
        return jsonify({'message': message}), 200
    else:
        return jsonify({'message': message}), 400


@bp.route('/users/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get the currently authenticated user's profile.
    """
    user = g.current_user
    
    return jsonify({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'is_active': user.is_active
        }
    }), 200


@bp.route('/users/roles', methods=['GET'])
@jwt_required()
def get_available_roles():
    """
    Get list of available user roles.
    """
    roles = [
        {
            'name': role.name,
            'value': role.value
        }
        for role in UserRole
    ]
    
    return jsonify({'roles': roles}), 200
