# app/services/user_management_service.py

from app import db
from app.models import User, UserRole
from sqlalchemy.exc import IntegrityError
from datetime import datetime

class UserManagementService:
    """
    Service class for handling user management operations.
    Provides methods for creating, updating, and managing user accounts.
    """
    
    @staticmethod
    def create_user(username, email, password, role='BASIC_USER', is_active=True):
        """
        Create a new user account.
        
        Args:
            username (str): Unique username
            email (str): Unique email address
            password (str): Plain text password (will be hashed)
            role (str): User role (SYSTEM_ADMIN, RECEIPT_LOGGER, BASIC_USER)
            is_active (bool): Account active status
            
        Returns:
            tuple: (success: bool, result: dict or str)
        """
        try:
            # Validate role
            role_str = role.upper()
            try:
                role_enum = UserRole[role_str]
                role_value = role_enum.value
            except KeyError:
                return False, f'Invalid role. Must be one of: {", ".join(r.name for r in UserRole)}'
            
            # Check if username or email already exists
            if User.query.filter_by(username=username).first():
                return False, 'Username already exists'
            
            if User.query.filter_by(email=email).first():
                return False, 'Email already registered'
            
            # Create new user
            user = User(
                username=username,
                email=email,
                role=role_value,
                is_active=is_active
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            return True, {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'is_active': user.is_active
            }
            
        except IntegrityError as e:
            db.session.rollback()
            return False, f'Database integrity error: {str(e)}'
        except Exception as e:
            db.session.rollback()
            return False, f'Error creating user: {str(e)}'
    
    @staticmethod
    def get_user_by_id(user_id):
        """
        Retrieve a user by ID.
        
        Args:
            user_id (int): User ID
            
        Returns:
            User object or None
        """
        return User.query.get(user_id)
    
    @staticmethod
    def get_all_users(include_inactive=False):
        """
        Retrieve all users.
        
        Args:
            include_inactive (bool): Include deactivated users
            
        Returns:
            list: List of user dictionaries
        """
        query = User.query
        if not include_inactive:
            query = query.filter_by(is_active=True)
        
        users = query.all()
        return [{
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'is_active': user.is_active
        } for user in users]
    
    @staticmethod
    def update_user_details(user_id, username=None, email=None):
        """
        Update user's basic details (username and/or email).
        
        Args:
            user_id (int): User ID
            username (str, optional): New username
            email (str, optional): New email
            
        Returns:
            tuple: (success: bool, result: dict or str)
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return False, 'User not found'
            
            # Update username if provided
            if username and username != user.username:
                # Check if new username already exists
                existing_user = User.query.filter_by(username=username).first()
                if existing_user and existing_user.id != user_id:
                    return False, 'Username already taken'
                user.username = username
            
            # Update email if provided
            if email and email != user.email:
                # Check if new email already exists
                existing_user = User.query.filter_by(email=email).first()
                if existing_user and existing_user.id != user_id:
                    return False, 'Email already registered'
                user.email = email
            
            db.session.commit()
            
            return True, {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'is_active': user.is_active
            }
            
        except IntegrityError as e:
            db.session.rollback()
            return False, f'Database integrity error: {str(e)}'
        except Exception as e:
            db.session.rollback()
            return False, f'Error updating user: {str(e)}'
    
    @staticmethod
    def change_password(user_id, current_password, new_password):
        """
        Change user's password with current password verification.
        
        Args:
            user_id (int): User ID
            current_password (str): Current password for verification
            new_password (str): New password
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return False, 'User not found'
            
            # Verify current password
            if not user.check_password(current_password):
                return False, 'Current password is incorrect'
            
            # Set new password
            user.set_password(new_password)
            db.session.commit()
            
            return True, 'Password changed successfully'
            
        except Exception as e:
            db.session.rollback()
            return False, f'Error changing password: {str(e)}'
    
    @staticmethod
    def admin_reset_password(user_id, new_password):
        """
        Admin function to reset a user's password without requiring current password.
        
        Args:
            user_id (int): User ID
            new_password (str): New password
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return False, 'User not found'
            
            user.set_password(new_password)
            db.session.commit()
            
            return True, 'Password reset successfully'
            
        except Exception as e:
            db.session.rollback()
            return False, f'Error resetting password: {str(e)}'
    
    @staticmethod
    def change_user_role(user_id, new_role):
        """
        Change a user's role.
        
        Args:
            user_id (int): User ID
            new_role (str): New role (SYSTEM_ADMIN, RECEIPT_LOGGER, BASIC_USER)
            
        Returns:
            tuple: (success: bool, result: dict or str)
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return False, 'User not found'
            
            # Validate new role
            role_str = new_role.upper()
            try:
                role_enum = UserRole[role_str]
                role_value = role_enum.value
            except KeyError:
                return False, f'Invalid role. Must be one of: {", ".join(r.name for r in UserRole)}'
            
            user.role = role_value
            db.session.commit()
            
            return True, {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'is_active': user.is_active
            }
            
        except Exception as e:
            db.session.rollback()
            return False, f'Error changing role: {str(e)}'
    
    @staticmethod
    def deactivate_user(user_id):
        """
        Deactivate a user account.
        
        Args:
            user_id (int): User ID
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return False, 'User not found'
            
            user.is_active = False
            db.session.commit()
            
            return True, f'User {user.username} deactivated successfully'
            
        except Exception as e:
            db.session.rollback()
            return False, f'Error deactivating user: {str(e)}'
    
    @staticmethod
    def reactivate_user(user_id):
        """
        Reactivate a deactivated user account.
        
        Args:
            user_id (int): User ID
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return False, 'User not found'
            
            user.is_active = True
            db.session.commit()
            
            return True, f'User {user.username} reactivated successfully'
            
        except Exception as e:
            db.session.rollback()
            return False, f'Error reactivating user: {str(e)}'
    
    @staticmethod
    def delete_user(user_id):
        """
        Permanently delete a user account.
        WARNING: This is irreversible. Consider deactivation instead.
        
        Args:
            user_id (int): User ID
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return False, 'User not found'
            
            username = user.username
            db.session.delete(user)
            db.session.commit()
            
            return True, f'User {username} deleted permanently'
            
        except Exception as e:
            db.session.rollback()
            return False, f'Error deleting user: {str(e)}'
