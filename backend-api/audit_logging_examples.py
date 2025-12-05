# Example: How to Add Audit Logging to Your Routes

"""
This file demonstrates different ways to add audit logging to your routes.
"""

# ============================================================================
# METHOD 1: Using the @audit_log Decorator (Recommended)
# ============================================================================

from flask import Blueprint, request, jsonify, g
from app.utils import jwt_required, audit_log
from app.services.audit_service import AuditService

bp = Blueprint('example', __name__)


@bp.route('/my-route', methods=['POST'])
@audit_log(action='MY_CUSTOM_ACTION', resource_type='MyResource')
@jwt_required()
def my_route_with_auto_logging():
    """
    This route automatically logs:
    - User information (from g.current_user)
    - HTTP method and endpoint
    - IP address and user agent
    - Request duration
    - Status code
    - Query parameters
    - Session ID
    """
    # Your route logic here
    data = request.get_json()
    
    # Do something...
    result = {'message': 'Success', 'data': data}
    
    return jsonify(result), 200
    # Audit log is automatically created when the response is returned


# ============================================================================
# METHOD 2: Manual Logging with AuditService
# ============================================================================

@bp.route('/manual-logging', methods=['POST'])
@jwt_required()
def route_with_manual_logging():
    """
    This route manually creates audit logs for more control.
    """
    data = request.get_json()
    
    try:
        # Do your business logic
        result_id = 123  # Example: ID of created resource
        
        # Manually log the action
        AuditService.log_action(
            action='CREATE_CUSTOM_RESOURCE',
            resource_type='CustomResource',
            resource_id=result_id,
            success=True,
            metadata={
                'input_data': data,
                'custom_field': 'value'
            }
        )
        
        return jsonify({'message': 'Success', 'id': result_id}), 201
        
    except Exception as e:
        # Log the failure
        AuditService.log_action(
            action='CREATE_CUSTOM_RESOURCE',
            resource_type='CustomResource',
            success=False,
            error_message=str(e),
            status_code=500
        )
        
        return jsonify({'message': 'Error', 'error': str(e)}), 500


# ============================================================================
# METHOD 3: Logging Authentication Events
# ============================================================================

@bp.route('/custom-auth', methods=['POST'])
def custom_authentication():
    """
    Example of logging authentication events.
    """
    data = request.get_json()
    username = data.get('username')
    
    # Verify credentials (simplified example)
    if username == 'valid_user':
        # Log successful authentication
        AuditService.log_authentication(
            action='CUSTOM_AUTH_SUCCESS',
            username=username,
            success=True,
            metadata={
                'auth_method': 'custom',
                'ip_address': request.remote_addr
            }
        )
        
        return jsonify({'message': 'Authentication successful'}), 200
    else:
        # Log failed authentication
        AuditService.log_authentication(
            action='CUSTOM_AUTH_FAILED',
            username=username,
            success=False,
            error_message='Invalid credentials',
            metadata={
                'auth_method': 'custom',
                'reason': 'invalid_username'
            }
        )
        
        return jsonify({'message': 'Authentication failed'}), 401


# ============================================================================
# METHOD 4: Logging Resource Access
# ============================================================================

@bp.route('/resource/<int:resource_id>', methods=['GET'])
@jwt_required()
def view_resource(resource_id):
    """
    Example of logging resource access.
    """
    # Fetch the resource
    resource = {'id': resource_id, 'name': 'Example Resource'}
    
    # Log the access
    AuditService.log_resource_access(
        action='VIEW_CUSTOM_RESOURCE',
        resource_type='CustomResource',
        resource_id=resource_id,
        metadata={
            'viewer_id': g.current_user.id,
            'viewer_role': g.current_user.role
        }
    )
    
    return jsonify({'resource': resource}), 200


# ============================================================================
# METHOD 5: Combining Decorator with Additional Manual Logging
# ============================================================================

@bp.route('/complex-operation', methods=['POST'])
@audit_log(action='COMPLEX_OPERATION', resource_type='ComplexResource')
@jwt_required()
def complex_operation():
    """
    This route uses the decorator for main logging and adds
    additional manual logs for specific sub-operations.
    """
    data = request.get_json()
    
    # Main operation
    result = {'status': 'started'}
    
    # Log a sub-operation
    AuditService.log_action(
        action='COMPLEX_OPERATION_STEP_1',
        resource_type='ComplexResource',
        success=True,
        metadata={'step': 1, 'data': data}
    )
    
    # Another sub-operation
    AuditService.log_action(
        action='COMPLEX_OPERATION_STEP_2',
        resource_type='ComplexResource',
        success=True,
        metadata={'step': 2, 'result': result}
    )
    
    # The main operation is automatically logged by the decorator
    return jsonify({'message': 'Complex operation completed', 'result': result}), 200


# ============================================================================
# METHOD 6: Logging with Custom Session ID
# ============================================================================

from app.utils import generate_session_id

@bp.route('/with-session', methods=['POST'])
@jwt_required()
def operation_with_session_tracking():
    """
    Example of explicit session ID generation and usage.
    """
    # Generate or retrieve session ID
    session_id = generate_session_id()
    
    # Log with explicit session ID
    AuditService.log_action(
        action='SESSION_TRACKED_OPERATION',
        resource_type='SessionResource',
        success=True,
        session_id=session_id,
        metadata={
            'session_info': 'custom session data',
            'session_id': session_id
        }
    )
    
    return jsonify({'message': 'Operation tracked', 'session_id': session_id}), 200


# ============================================================================
# REAL-WORLD EXAMPLE: File Upload with Audit Logging
# ============================================================================

@bp.route('/upload-document', methods=['POST'])
@audit_log(action='UPLOAD_DOCUMENT', resource_type='Document')
@jwt_required()
def upload_document():
    """
    Real-world example: Document upload with comprehensive audit logging.
    """
    from werkzeug.utils import secure_filename
    import os
    
    if 'file' not in request.files:
        # Log the error
        AuditService.log_action(
            action='UPLOAD_DOCUMENT_FAILED',
            resource_type='Document',
            success=False,
            error_message='No file provided',
            status_code=400
        )
        return jsonify({'message': 'No file provided'}), 400
    
    file = request.files['file']
    filename = secure_filename(file.filename)
    
    try:
        # Save the file (simplified)
        # file.save(os.path.join('uploads', filename))
        
        document_id = 456  # Example: ID of saved document
        
        # Log successful upload with details
        AuditService.log_action(
            action='UPLOAD_DOCUMENT_SUCCESS',
            resource_type='Document',
            resource_id=document_id,
            success=True,
            metadata={
                'filename': filename,
                'file_size': request.content_length,
                'content_type': file.content_type,
                'uploader_id': g.current_user.id,
                'uploader_role': g.current_user.role
            }
        )
        
        return jsonify({
            'message': 'Document uploaded successfully',
            'document_id': document_id,
            'filename': filename
        }), 201
        
    except Exception as e:
        # Log upload failure
        AuditService.log_action(
            action='UPLOAD_DOCUMENT_ERROR',
            resource_type='Document',
            success=False,
            error_message=str(e),
            status_code=500,
            metadata={
                'filename': filename,
                'error_type': type(e).__name__
            }
        )
        
        return jsonify({'message': 'Upload failed', 'error': str(e)}), 500


# ============================================================================
# BEST PRACTICES SUMMARY
# ============================================================================

"""
BEST PRACTICES:

1. USE DECORATORS when possible for consistent logging
   @audit_log(action='ACTION_NAME', resource_type='ResourceType')

2. USE MEANINGFUL ACTION NAMES
   Good: 'CREATE_USER', 'DELETE_RECEIPT', 'UPDATE_PROFILE'
   Bad: 'do_stuff', 'action1', 'process'

3. ALWAYS SPECIFY RESOURCE TYPE AND ID when operating on resources
   resource_type='User', resource_id=123

4. INCLUDE RELEVANT METADATA
   metadata={'field1': 'value1', 'context': 'important info'}

5. LOG BOTH SUCCESS AND FAILURE
   Always log failures with error_message

6. RESPECT PRIVACY
   Don't log passwords, tokens, or sensitive personal data

7. BE CONSISTENT
   Use the same action names for similar operations across your app

8. TEST YOUR LOGGING
   Verify logs appear in /api/audit/logs

COMMON ACTION NAMING CONVENTIONS:
- CREATE_<RESOURCE>: Creating new resources
- VIEW_<RESOURCE>: Viewing/reading resources
- UPDATE_<RESOURCE>: Modifying resources
- DELETE_<RESOURCE>: Deleting resources
- LIST_<RESOURCE>: Listing multiple resources
- LOGIN/LOGOUT: Authentication events
- <RESOURCE>_FAILED: Failed operations
"""
