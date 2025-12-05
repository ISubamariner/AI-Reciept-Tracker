# app/services/audit_service.py

from app import db
from app.models import AuditLog
from flask import request, g
from datetime import datetime
from sqlalchemy import and_, or_


class AuditService:
    """
    Service for creating and managing audit log entries.
    Provides methods to log user actions, API calls, and query audit history.
    """
    
    @staticmethod
    def log_action(
        action,
        method=None,
        endpoint=None,
        user_id=None,
        username=None,
        user_role=None,
        resource_type=None,
        resource_id=None,
        status_code=None,
        success=True,
        error_message=None,
        metadata=None,
        ip_address=None,
        user_agent=None,
        session_id=None
    ):
        """
        Create an audit log entry.
        
        Args:
            action (str): Action performed (e.g., 'LOGIN', 'UPLOAD_RECEIPT')
            method (str): HTTP method
            endpoint (str): API endpoint
            user_id (int): ID of user performing action
            username (str): Username of user
            user_role (str): Role of user
            resource_type (str): Type of resource affected
            resource_id (int): ID of resource affected
            status_code (int): HTTP status code
            success (bool): Whether action succeeded
            error_message (str): Error message if failed
            metadata (dict): Additional context
            ip_address (str): Client IP address
            user_agent (str): Client user agent
            session_id (str): Session identifier
        
        Returns:
            AuditLog: The created audit log entry
        """
        try:
            # Auto-populate from Flask request context if available
            if not method and request:
                method = request.method
            
            if not endpoint and request:
                endpoint = request.path
            
            if not ip_address and request:
                # Get real IP if behind proxy
                ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
                if ip_address and ',' in ip_address:
                    ip_address = ip_address.split(',')[0].strip()
            
            if not user_agent and request:
                user_agent = request.headers.get('User-Agent', '')[:512]
            
            # Try to get user from Flask g context if not provided
            if not user_id and hasattr(g, 'current_user') and g.current_user:
                user_id = g.current_user.id
                username = username or g.current_user.username
                user_role = user_role or g.current_user.role
            
            # Create audit log entry
            audit_log = AuditLog(
                user_id=user_id,
                username=username,
                user_role=user_role,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                method=method,
                endpoint=endpoint,
                ip_address=ip_address,
                user_agent=user_agent,
                timestamp=datetime.utcnow(),
                status_code=status_code,
                success=success,
                error_message=error_message,
                request_metadata=metadata,
                session_id=session_id
            )
            
            db.session.add(audit_log)
            db.session.commit()
            
            return audit_log
            
        except Exception as e:
            # Don't let audit logging break the application
            # Log the error but don't raise
            print(f"Error creating audit log: {e}")
            try:
                db.session.rollback()
            except:
                pass
            return None
    
    @staticmethod
    def log_authentication(action, username, success, error_message=None, metadata=None):
        """
        Log authentication events (login, logout, failed login attempts).
        
        Args:
            action (str): 'LOGIN', 'LOGOUT', 'LOGIN_FAILED'
            username (str): Username attempting authentication
            success (bool): Whether authentication succeeded
            error_message (str): Error message if failed
            metadata (dict): Additional context
        """
        return AuditService.log_action(
            action=action,
            username=username,
            success=success,
            error_message=error_message,
            metadata=metadata
        )
    
    @staticmethod
    def log_resource_access(action, resource_type, resource_id=None, metadata=None):
        """
        Log resource access events (view, create, update, delete).
        
        Args:
            action (str): Action performed (e.g., 'VIEW_RECEIPT', 'CREATE_USER')
            resource_type (str): Type of resource (e.g., 'Receipt', 'User')
            resource_id (int): ID of resource
            metadata (dict): Additional context
        """
        return AuditService.log_action(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata=metadata
        )
    
    @staticmethod
    def get_logs(
        user_id=None,
        action=None,
        resource_type=None,
        start_date=None,
        end_date=None,
        success=None,
        limit=100,
        offset=0,
        order_by='desc'
    ):
        """
        Query audit logs with filters.
        
        Args:
            user_id (int): Filter by user ID
            action (str): Filter by action type
            resource_type (str): Filter by resource type
            start_date (datetime): Filter logs after this date
            end_date (datetime): Filter logs before this date
            success (bool): Filter by success status
            limit (int): Maximum number of logs to return
            offset (int): Number of logs to skip (pagination)
            order_by (str): 'asc' or 'desc' for timestamp ordering
        
        Returns:
            list: List of AuditLog objects
        """
        query = AuditLog.query
        
        # Apply filters
        if user_id is not None:
            query = query.filter(AuditLog.user_id == user_id)
        
        if action:
            query = query.filter(AuditLog.action == action)
        
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)
        
        if success is not None:
            query = query.filter(AuditLog.success == success)
        
        # Order by timestamp
        if order_by.lower() == 'desc':
            query = query.order_by(AuditLog.timestamp.desc())
        else:
            query = query.order_by(AuditLog.timestamp.asc())
        
        # Apply pagination
        query = query.limit(limit).offset(offset)
        
        return query.all()
    
    @staticmethod
    def get_user_activity(user_id, limit=50):
        """
        Get recent activity for a specific user.
        
        Args:
            user_id (int): User ID
            limit (int): Maximum number of logs to return
        
        Returns:
            list: List of recent audit logs for the user
        """
        return AuditLog.query.filter_by(user_id=user_id)\
            .order_by(AuditLog.timestamp.desc())\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_failed_logins(username=None, hours=24, limit=100):
        """
        Get recent failed login attempts.
        
        Args:
            username (str): Filter by username (optional)
            hours (int): Number of hours to look back
            limit (int): Maximum number of logs to return
        
        Returns:
            list: List of failed login attempts
        """
        from datetime import timedelta
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        query = AuditLog.query.filter(
            and_(
                AuditLog.action == 'LOGIN_FAILED',
                AuditLog.timestamp >= cutoff_time
            )
        )
        
        if username:
            query = query.filter(AuditLog.username == username)
        
        return query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
    
    @staticmethod
    def get_resource_history(resource_type, resource_id, limit=50):
        """
        Get audit history for a specific resource.
        
        Args:
            resource_type (str): Type of resource
            resource_id (int): Resource ID
            limit (int): Maximum number of logs to return
        
        Returns:
            list: List of audit logs for the resource
        """
        return AuditLog.query.filter_by(
            resource_type=resource_type,
            resource_id=resource_id
        ).order_by(AuditLog.timestamp.desc()).limit(limit).all()
    
    @staticmethod
    def get_statistics(start_date=None, end_date=None):
        """
        Get audit log statistics.
        
        Args:
            start_date (datetime): Start date for statistics
            end_date (datetime): End date for statistics
        
        Returns:
            dict: Statistics about audit logs
        """
        query = AuditLog.query
        
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)
        
        total_logs = query.count()
        successful_actions = query.filter(AuditLog.success == True).count()
        failed_actions = query.filter(AuditLog.success == False).count()
        
        # Get unique users
        unique_users = db.session.query(AuditLog.user_id)\
            .filter(AuditLog.user_id.isnot(None))\
            .distinct()\
            .count()
        
        return {
            'total_logs': total_logs,
            'successful_actions': successful_actions,
            'failed_actions': failed_actions,
            'unique_users': unique_users,
            'success_rate': (successful_actions / total_logs * 100) if total_logs > 0 else 0
        }
