# app/audit/routes.py

from flask import Blueprint, request, jsonify, g
from app.services.audit_service import AuditService
from app.utils import jwt_required, admin_required
from app.models import UserRole
from datetime import datetime, timedelta

# Define the Blueprint for audit log management
bp = Blueprint('audit', __name__)


@bp.route('/audit/logs', methods=['GET'])
@jwt_required()
@admin_required()
def get_audit_logs():
    """
    Get audit logs with optional filters (Admin only).
    
    Query parameters:
        - user_id (int): Filter by user ID
        - action (str): Filter by action type
        - resource_type (str): Filter by resource type
        - start_date (str): Filter logs after this date (ISO format)
        - end_date (str): Filter logs before this date (ISO format)
        - success (bool): Filter by success status (true/false)
        - limit (int): Maximum number of logs to return (default: 100, max: 1000)
        - offset (int): Number of logs to skip for pagination (default: 0)
        - order_by (str): Sort order - 'asc' or 'desc' (default: desc)
    """
    # Parse query parameters
    user_id = request.args.get('user_id', type=int)
    action = request.args.get('action')
    resource_type = request.args.get('resource_type')
    
    # Parse dates
    start_date = None
    end_date = None
    
    if request.args.get('start_date'):
        try:
            start_date = datetime.fromisoformat(request.args.get('start_date').replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'message': 'Invalid start_date format. Use ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)'}), 400
    
    if request.args.get('end_date'):
        try:
            end_date = datetime.fromisoformat(request.args.get('end_date').replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'message': 'Invalid end_date format. Use ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)'}), 400
    
    # Parse success parameter
    success = None
    if request.args.get('success'):
        success_str = request.args.get('success').lower()
        if success_str in ['true', '1', 'yes']:
            success = True
        elif success_str in ['false', '0', 'no']:
            success = False
    
    # Pagination
    limit = min(request.args.get('limit', 100, type=int), 1000)  # Cap at 1000
    offset = request.args.get('offset', 0, type=int)
    order_by = request.args.get('order_by', 'desc')
    
    # Get logs
    logs = AuditService.get_logs(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        start_date=start_date,
        end_date=end_date,
        success=success,
        limit=limit,
        offset=offset,
        order_by=order_by
    )
    
    return jsonify({
        'logs': [log.to_dict() for log in logs],
        'count': len(logs),
        'limit': limit,
        'offset': offset
    }), 200


@bp.route('/audit/logs/<int:log_id>', methods=['GET'])
@jwt_required()
@admin_required()
def get_audit_log(log_id):
    """
    Get a specific audit log by ID (Admin only).
    """
    from app.models import AuditLog
    
    log = AuditLog.query.get(log_id)
    
    if not log:
        return jsonify({'message': 'Audit log not found'}), 404
    
    return jsonify({
        'log': log.to_dict()
    }), 200


@bp.route('/audit/user/<int:user_id>/activity', methods=['GET'])
@jwt_required()
def get_user_activity(user_id):
    """
    Get activity history for a specific user.
    Users can view their own activity, admins can view any user's activity.
    
    Query parameters:
        - limit (int): Maximum number of logs to return (default: 50, max: 500)
    """
    # Check permissions
    if g.current_user.id != user_id and g.current_user.role != UserRole.SYSTEM_ADMIN.value:
        return jsonify({'message': 'Permission denied'}), 403
    
    limit = min(request.args.get('limit', 50, type=int), 500)
    
    logs = AuditService.get_user_activity(user_id=user_id, limit=limit)
    
    return jsonify({
        'user_id': user_id,
        'logs': [log.to_dict() for log in logs],
        'count': len(logs)
    }), 200


@bp.route('/audit/user/me/activity', methods=['GET'])
@jwt_required()
def get_my_activity():
    """
    Get activity history for the current authenticated user.
    
    Query parameters:
        - limit (int): Maximum number of logs to return (default: 50, max: 500)
    """
    limit = min(request.args.get('limit', 50, type=int), 500)
    
    logs = AuditService.get_user_activity(user_id=g.current_user.id, limit=limit)
    
    return jsonify({
        'user_id': g.current_user.id,
        'username': g.current_user.username,
        'logs': [log.to_dict() for log in logs],
        'count': len(logs)
    }), 200


@bp.route('/audit/failed-logins', methods=['GET'])
@jwt_required()
@admin_required()
def get_failed_logins():
    """
    Get recent failed login attempts (Admin only).
    
    Query parameters:
        - username (str): Filter by username (optional)
        - hours (int): Number of hours to look back (default: 24)
        - limit (int): Maximum number of logs to return (default: 100, max: 500)
    """
    username = request.args.get('username')
    hours = request.args.get('hours', 24, type=int)
    limit = min(request.args.get('limit', 100, type=int), 500)
    
    logs = AuditService.get_failed_logins(
        username=username,
        hours=hours,
        limit=limit
    )
    
    return jsonify({
        'failed_logins': [log.to_dict() for log in logs],
        'count': len(logs),
        'hours': hours
    }), 200


@bp.route('/audit/resource/<string:resource_type>/<int:resource_id>/history', methods=['GET'])
@jwt_required()
@admin_required()
def get_resource_history(resource_type, resource_id):
    """
    Get audit history for a specific resource (Admin only).
    
    Query parameters:
        - limit (int): Maximum number of logs to return (default: 50, max: 200)
    """
    limit = min(request.args.get('limit', 50, type=int), 200)
    
    logs = AuditService.get_resource_history(
        resource_type=resource_type,
        resource_id=resource_id,
        limit=limit
    )
    
    return jsonify({
        'resource_type': resource_type,
        'resource_id': resource_id,
        'logs': [log.to_dict() for log in logs],
        'count': len(logs)
    }), 200


@bp.route('/audit/statistics', methods=['GET'])
@jwt_required()
@admin_required()
def get_audit_statistics():
    """
    Get audit log statistics (Admin only).
    
    Query parameters:
        - start_date (str): Start date for statistics (ISO format, optional)
        - end_date (str): End date for statistics (ISO format, optional)
        - period (str): Predefined period - 'today', 'week', 'month' (overrides dates)
    """
    # Parse period shortcuts
    period = request.args.get('period')
    start_date = None
    end_date = None
    
    if period == 'today':
        start_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = datetime.utcnow()
    elif period == 'week':
        start_date = datetime.utcnow() - timedelta(days=7)
        end_date = datetime.utcnow()
    elif period == 'month':
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow()
    else:
        # Parse custom dates
        if request.args.get('start_date'):
            try:
                start_date = datetime.fromisoformat(request.args.get('start_date').replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'message': 'Invalid start_date format'}), 400
        
        if request.args.get('end_date'):
            try:
                end_date = datetime.fromisoformat(request.args.get('end_date').replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'message': 'Invalid end_date format'}), 400
    
    stats = AuditService.get_statistics(
        start_date=start_date,
        end_date=end_date
    )
    
    return jsonify({
        'statistics': stats,
        'period': {
            'start_date': start_date.isoformat() if start_date else None,
            'end_date': end_date.isoformat() if end_date else None
        }
    }), 200


@bp.route('/audit/export', methods=['GET'])
@jwt_required()
@admin_required()
def export_audit_logs():
    """
    Export audit logs as CSV (Admin only).
    
    Query parameters:
        - Same as /audit/logs endpoint
        - format (str): Export format - 'csv' or 'json' (default: csv)
    """
    import csv
    from io import StringIO
    from flask import make_response
    
    # Get logs with same filters as get_audit_logs
    user_id = request.args.get('user_id', type=int)
    action = request.args.get('action')
    resource_type = request.args.get('resource_type')
    
    start_date = None
    end_date = None
    
    if request.args.get('start_date'):
        try:
            start_date = datetime.fromisoformat(request.args.get('start_date').replace('Z', '+00:00'))
        except ValueError:
            pass
    
    if request.args.get('end_date'):
        try:
            end_date = datetime.fromisoformat(request.args.get('end_date').replace('Z', '+00:00'))
        except ValueError:
            pass
    
    success = None
    if request.args.get('success'):
        success_str = request.args.get('success').lower()
        if success_str in ['true', '1', 'yes']:
            success = True
        elif success_str in ['false', '0', 'no']:
            success = False
    
    limit = min(request.args.get('limit', 1000, type=int), 10000)  # Higher limit for export
    
    logs = AuditService.get_logs(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        start_date=start_date,
        end_date=end_date,
        success=success,
        limit=limit,
        offset=0,
        order_by='desc'
    )
    
    export_format = request.args.get('format', 'csv').lower()
    
    if export_format == 'json':
        # JSON export
        return jsonify({
            'logs': [log.to_dict() for log in logs],
            'count': len(logs),
            'exported_at': datetime.utcnow().isoformat()
        }), 200
    else:
        # CSV export
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'ID', 'Timestamp', 'User ID', 'Username', 'Role', 'Action',
            'Resource Type', 'Resource ID', 'Method', 'Endpoint',
            'IP Address', 'Status Code', 'Success', 'Error Message', 'Session ID'
        ])
        
        # Write data
        for log in logs:
            writer.writerow([
                log.id,
                log.timestamp.isoformat() if log.timestamp else '',
                log.user_id or '',
                log.username or '',
                log.user_role or '',
                log.action or '',
                log.resource_type or '',
                log.resource_id or '',
                log.method or '',
                log.endpoint or '',
                log.ip_address or '',
                log.status_code or '',
                log.success,
                log.error_message or '',
                log.session_id or ''
            ])
        
        # Create response
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=audit_logs_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return response
