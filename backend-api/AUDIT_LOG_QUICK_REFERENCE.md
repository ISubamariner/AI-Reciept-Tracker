# Audit Log System - Quick Reference

## What's Been Implemented

✅ **Complete audit logging system for tracking user sessions and API calls**

### Components Created

1. **Database Model** (`app/models.py`)
   - `AuditLog` model with all standard audit fields
   - Tracks: user, action, resource, timestamp, IP, status, metadata, session ID

2. **Audit Service** (`app/services/audit_service.py`)
   - `AuditService.log_action()` - Main logging method
   - `AuditService.log_authentication()` - For login/logout events
   - `AuditService.log_resource_access()` - For resource operations
   - Query methods: `get_logs()`, `get_user_activity()`, `get_failed_logins()`, etc.
   - `get_statistics()` - Audit analytics

3. **Utilities** (`app/utils.py`)
   - `@audit_log()` decorator - Automatic logging for routes
   - `generate_session_id()` - Session tracking

4. **API Routes** (`app/audit/routes.py`)
   - `GET /api/audit/logs` - Query audit logs (admin)
   - `GET /api/audit/logs/<id>` - Get specific log (admin)
   - `GET /api/audit/user/<user_id>/activity` - User activity
   - `GET /api/audit/user/me/activity` - Current user activity
   - `GET /api/audit/failed-logins` - Failed login attempts (admin)
   - `GET /api/audit/resource/<type>/<id>/history` - Resource history (admin)
   - `GET /api/audit/statistics` - Statistics (admin)
   - `GET /api/audit/export` - Export as CSV/JSON (admin)

5. **Authentication Logging** (Updated `app/auth/routes.py`)
   - Login events logged with session ID
   - Failed login attempts logged
   - Logout events logged
   - User registration logged

6. **Route Logging** (Updated existing routes)
   - Receipt upload/confirm with `@audit_log()` decorator
   - User management operations logged
   - Automatic capture of request details

## Quick Start

### 1. Set Up Database

**For new installations:**
```bash
cd portfolio-ai-app/backend-api
python init_db.py
```

**For existing installations:**
```bash
cd portfolio-ai-app/backend-api
python migrate_add_audit_logs.py
```

### 2. Test the System

```bash
cd portfolio-ai-app/backend-api
python test_audit_logging.py
```

### 3. Use in Your Routes

```python
from app.utils import audit_log

@bp.route('/my-endpoint', methods=['POST'])
@audit_log(action='MY_ACTION', resource_type='MyResource')
@jwt_required()
def my_endpoint():
    # Your code here
    pass
```

### 4. Query Audit Logs

```bash
# Get recent logs (admin token required)
curl -X GET "http://localhost:5000/api/audit/logs?limit=50" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Get your own activity
curl -X GET "http://localhost:5000/api/audit/user/me/activity" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get statistics
curl -X GET "http://localhost:5000/api/audit/statistics?period=week" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Export as CSV
curl -X GET "http://localhost:5000/api/audit/export?format=csv" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" > audit_logs.csv
```

## What Gets Logged

### Automatically Logged (via @audit_log decorator)
- HTTP method and endpoint
- User ID, username, and role
- Timestamp
- IP address and user agent
- Status code and success/failure
- Request duration
- Query parameters
- Session ID

### Authentication Events
- Login attempts (success and failure)
- Logout
- User registration

### Resource Operations
- Receipt uploads and confirmations
- User creation and management
- Transaction operations
- Any other decorated routes

## Audit Log Fields

| Field | Description | Example |
|-------|-------------|---------|
| `action` | What happened | 'LOGIN', 'UPLOAD_RECEIPT' |
| `user_id` | Who did it | 123 |
| `username` | User's name | 'john_doe' |
| `user_role` | User's role | 'System Admin' |
| `resource_type` | What was affected | 'Receipt', 'User' |
| `resource_id` | Which resource | 456 |
| `method` | HTTP method | 'POST', 'GET' |
| `endpoint` | API path | '/api/receipts/upload' |
| `ip_address` | Client IP | '192.168.1.100' |
| `timestamp` | When | '2024-12-05T10:30:00Z' |
| `status_code` | HTTP status | 200, 401, 500 |
| `success` | Succeeded? | true/false |
| `error_message` | Error details | 'Invalid token' |
| `metadata` | Extra context | JSON object |
| `session_id` | Session ID | UUID |

## Security & Permissions

- **Regular Users**: Can view their own activity logs
- **Admins**: Can view all logs, statistics, and export data
- **Unauthenticated**: Login/registration attempts are logged (no token required)

## Common Queries

```python
from app.services.audit_service import AuditService

# Get all failed logins in last 24 hours
failed = AuditService.get_failed_logins(hours=24)

# Get specific user's activity
activity = AuditService.get_user_activity(user_id=123, limit=50)

# Get history of a receipt
history = AuditService.get_resource_history('Receipt', 456)

# Get statistics
stats = AuditService.get_statistics()
```

## Files Modified/Created

### Created:
- `app/services/audit_service.py` - Core audit logging service
- `app/audit/__init__.py` - Audit module init
- `app/audit/routes.py` - Audit log API endpoints
- `backend-api/migrate_add_audit_logs.py` - Database migration
- `backend-api/test_audit_logging.py` - Test script
- `backend-api/AUDIT_LOG_GUIDE.md` - Full documentation
- `backend-api/AUDIT_LOG_QUICK_REFERENCE.md` - This file

### Modified:
- `app/models.py` - Added AuditLog model
- `app/utils.py` - Added @audit_log decorator and session functions
- `app/__init__.py` - Registered audit blueprint
- `app/auth/routes.py` - Added authentication logging
- `app/receipts/routes.py` - Added @audit_log decorators
- `app/users/routes.py` - Added @audit_log decorators

## Next Steps

1. **Run migration** to create the audit_logs table
2. **Test the system** using test_audit_logging.py
3. **Start using** the logging in production
4. **Monitor logs** via the API endpoints
5. **Set up data retention** policy for log cleanup
6. **Configure alerts** for suspicious activity (e.g., multiple failed logins)

## Troubleshooting

**Issue**: Logs not appearing
- **Fix**: Run `python migrate_add_audit_logs.py`

**Issue**: Permission denied on queries
- **Fix**: Ensure you're using an admin token for admin endpoints

**Issue**: Session ID not consistent
- **Fix**: Ensure `generate_session_id()` is called in auth flow

## Support

For detailed information, see:
- **Full Documentation**: `AUDIT_LOG_GUIDE.md`
- **Test Script**: `test_audit_logging.py`
- **Service Code**: `app/services/audit_service.py`
- **Model Definition**: `app/models.py` (AuditLog class)
