# Audit Log System Documentation

## Overview

The audit log system tracks all user sessions and API calls in the application. It provides comprehensive logging of who did what, when, where, and the result of each action.

## Features

✅ **Automatic Logging**: API calls are automatically logged using decorators
✅ **User Session Tracking**: Each user session is tracked with a unique session ID
✅ **Authentication Logging**: Login, logout, and failed login attempts are recorded
✅ **Resource Tracking**: Track operations on specific resources (users, receipts, transactions)
✅ **Detailed Context**: IP address, user agent, request metadata, and more
✅ **Query Interface**: Comprehensive API endpoints to query and analyze audit logs
✅ **Export Support**: Export audit logs as CSV or JSON
✅ **Statistics**: Get audit log statistics and analytics

## Database Schema

### AuditLog Table

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| user_id | Integer | Foreign key to users table (nullable for unauthenticated requests) |
| username | String(64) | Username (denormalized for performance) |
| user_role | String(64) | User role at time of action |
| action | String(128) | Action performed (e.g., 'LOGIN', 'UPLOAD_RECEIPT') |
| resource_type | String(64) | Type of resource affected (e.g., 'Receipt', 'User') |
| resource_id | Integer | ID of the affected resource |
| method | String(10) | HTTP method (GET, POST, PUT, DELETE) |
| endpoint | String(256) | API endpoint path |
| ip_address | String(45) | Client IP address (IPv4 or IPv6) |
| user_agent | String(512) | Browser/client information |
| timestamp | DateTime | When the action occurred (indexed) |
| status_code | Integer | HTTP status code |
| success | Boolean | Whether the action succeeded |
| error_message | Text | Error details if failed |
| metadata | JSONB | Additional context (query params, data changes, etc.) |
| session_id | String(128) | Session identifier for tracking user sessions |

## Usage

### 1. Automatic Logging with Decorator

Add the `@audit_log()` decorator to any route to automatically log API calls:

```python
from app.utils import audit_log

@bp.route('/upload', methods=['POST'])
@audit_log(action='UPLOAD_RECEIPT', resource_type='Receipt')
@jwt_required()
def upload_receipt():
    # Your route logic here
    pass
```

**Parameters:**
- `action` (str): Custom action name (defaults to function name if not provided)
- `resource_type` (str): Type of resource being accessed

### 2. Manual Logging

For more control, use the `AuditService` directly:

```python
from app.services.audit_service import AuditService

# Log a simple action
AuditService.log_action(
    action='CUSTOM_ACTION',
    resource_type='CustomResource',
    resource_id=123,
    success=True,
    metadata={'custom_field': 'value'}
)

# Log authentication events
AuditService.log_authentication(
    action='LOGIN',
    username='john_doe',
    success=True,
    metadata={'ip': '192.168.1.1'}
)

# Log resource access
AuditService.log_resource_access(
    action='VIEW_RECEIPT',
    resource_type='Receipt',
    resource_id=456,
    metadata={'viewed_by': 'admin'}
)
```

### 3. Querying Audit Logs

#### Get All Logs (Admin only)

```
GET /api/audit/logs?limit=100&offset=0
```

**Query Parameters:**
- `user_id`: Filter by user ID
- `action`: Filter by action type
- `resource_type`: Filter by resource type
- `start_date`: Filter logs after this date (ISO format)
- `end_date`: Filter logs before this date (ISO format)
- `success`: Filter by success status (true/false)
- `limit`: Maximum number of logs (default: 100, max: 1000)
- `offset`: Number of logs to skip (pagination)
- `order_by`: Sort order ('asc' or 'desc', default: desc)

**Example:**
```bash
curl -X GET "http://localhost:5000/api/audit/logs?action=LOGIN&start_date=2024-12-01&limit=50" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Get Specific Audit Log

```
GET /api/audit/logs/{log_id}
```

#### Get User Activity

Users can view their own activity, admins can view any user's activity:

```
GET /api/audit/user/{user_id}/activity?limit=50
```

Or get your own activity:

```
GET /api/audit/user/me/activity?limit=50
```

#### Get Failed Login Attempts (Admin only)

```
GET /api/audit/failed-logins?username=john_doe&hours=24&limit=100
```

#### Get Resource History (Admin only)

```
GET /api/audit/resource/{resource_type}/{resource_id}/history?limit=50
```

**Example:**
```
GET /api/audit/resource/Receipt/123/history
```

#### Get Audit Statistics (Admin only)

```
GET /api/audit/statistics?period=week
```

**Period options:**
- `today`: Statistics for today
- `week`: Last 7 days
- `month`: Last 30 days
- Custom: Use `start_date` and `end_date` parameters

#### Export Audit Logs (Admin only)

Export as CSV:
```
GET /api/audit/export?format=csv&start_date=2024-12-01&limit=1000
```

Export as JSON:
```
GET /api/audit/export?format=json&start_date=2024-12-01&limit=1000
```

## Common Action Types

### Authentication
- `LOGIN`: Successful login
- `LOGIN_FAILED`: Failed login attempt
- `LOGOUT`: User logout
- `USER_REGISTRATION`: New user registration

### Receipts
- `UPLOAD_RECEIPT`: Receipt uploaded
- `CONFIRM_RECEIPT`: Receipt confirmed and transaction created
- `VIEW_RECEIPT`: Receipt viewed
- `DELETE_RECEIPT`: Receipt deleted

### Users
- `CREATE_USER`: User account created
- `VIEW_USER`: User profile viewed
- `LIST_USERS`: User list retrieved
- `UPDATE_USER`: User account updated
- `DELETE_USER`: User account deleted
- `CHANGE_PASSWORD`: Password changed

### Transactions
- `CREATE_TRANSACTION`: Transaction created
- `VIEW_TRANSACTION`: Transaction viewed
- `UPDATE_TRANSACTION`: Transaction updated
- `DELETE_TRANSACTION`: Transaction deleted

## Session Tracking

Each user session is tracked with a unique session ID (UUID). The session ID is generated on login and stored in the Flask `g` object. All actions within the same session share the same session ID.

**Generating a Session ID:**
```python
from app.utils import generate_session_id

session_id = generate_session_id()  # Returns UUID string
```

## Security Considerations

1. **Access Control**: Only admins can view all audit logs. Regular users can only view their own activity.
2. **Data Retention**: Consider implementing a data retention policy to archive or delete old audit logs.
3. **Sensitive Data**: Be careful not to log sensitive information (passwords, tokens) in metadata fields.
4. **IP Address**: IP addresses are captured for security auditing but respect privacy laws.

## Database Migration

### For New Installations

Run the standard database initialization:
```bash
python init_db.py
```

### For Existing Installations

Run the migration script to add the audit_logs table:
```bash
python migrate_add_audit_logs.py
```

This will create the `audit_logs` table without affecting existing tables.

## Monitoring and Maintenance

### Check Recent Activity

```python
from app.services.audit_service import AuditService

# Get failed logins in last 24 hours
failed_logins = AuditService.get_failed_logins(hours=24)

# Get statistics
stats = AuditService.get_statistics()
print(f"Total logs: {stats['total_logs']}")
print(f"Success rate: {stats['success_rate']}%")
```

### Database Cleanup

For production systems, implement periodic cleanup:

```python
from datetime import datetime, timedelta
from app import db
from app.models import AuditLog

# Delete logs older than 90 days
cutoff = datetime.utcnow() - timedelta(days=90)
old_logs = AuditLog.query.filter(AuditLog.timestamp < cutoff).delete()
db.session.commit()
print(f"Deleted {old_logs} old audit log entries")
```

## Best Practices

1. **Use Decorators**: Use the `@audit_log()` decorator for automatic logging when possible.
2. **Meaningful Actions**: Use clear, descriptive action names (e.g., 'CREATE_USER' not 'create').
3. **Include Context**: Add relevant metadata to help with debugging and analysis.
4. **Resource Tracking**: Always specify resource_type and resource_id when operating on resources.
5. **Error Logging**: Log both successful and failed actions for complete audit trail.
6. **Regular Reviews**: Regularly review audit logs for security and compliance.

## Example Queries

### Find all actions by a specific user
```python
logs = AuditService.get_logs(user_id=123, limit=100)
```

### Find all failed actions in the last hour
```python
from datetime import datetime, timedelta

start = datetime.utcnow() - timedelta(hours=1)
logs = AuditService.get_logs(success=False, start_date=start)
```

### Track a specific receipt's history
```python
logs = AuditService.get_resource_history('Receipt', 456)
```

### Get login activity for a user
```python
logs = AuditService.get_logs(user_id=123, action='LOGIN', limit=50)
```

## Troubleshooting

### Audit logs not appearing

1. Check that the `audit_logs` table exists:
   ```bash
   python migrate_add_audit_logs.py
   ```

2. Verify the decorator order (should be before `@jwt_required()`):
   ```python
   @audit_log()
   @jwt_required()
   def my_route():
       pass
   ```

3. Check for database errors in application logs.

### Performance issues

1. Ensure the `timestamp` field is indexed (it should be by default).
2. Implement log archiving for old records.
3. Consider using background tasks for logging if needed.

## API Response Examples

### Get Audit Logs Response
```json
{
  "logs": [
    {
      "id": 1,
      "user_id": 1,
      "username": "john_doe",
      "user_role": "System Admin",
      "action": "LOGIN",
      "resource_type": null,
      "resource_id": null,
      "method": "POST",
      "endpoint": "/api/auth/login",
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0...",
      "timestamp": "2024-12-05T10:30:00Z",
      "status_code": 200,
      "success": true,
      "error_message": null,
      "metadata": {
        "session_id": "550e8400-e29b-41d4-a716-446655440000"
      },
      "session_id": "550e8400-e29b-41d4-a716-446655440000"
    }
  ],
  "count": 1,
  "limit": 100,
  "offset": 0
}
```

### Get Statistics Response
```json
{
  "statistics": {
    "total_logs": 1523,
    "successful_actions": 1498,
    "failed_actions": 25,
    "unique_users": 15,
    "success_rate": 98.36
  },
  "period": {
    "start_date": "2024-11-28T00:00:00Z",
    "end_date": "2024-12-05T10:30:00Z"
  }
}
```
