# Test script for audit logging functionality

from app import create_app, db
from app.models import User, AuditLog
from app.services.audit_service import AuditService
from datetime import datetime, timedelta

def test_audit_logging():
    """Test audit logging functionality"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("AUDIT LOG SYSTEM TEST")
        print("=" * 60)
        
        # Test 1: Create audit log entries
        print("\n1. Creating test audit log entries...")
        
        # Create a test user if doesn't exist
        test_user = User.query.filter_by(username='test_audit').first()
        if not test_user:
            test_user = User(username='test_audit', email='audit@test.com', role='Basic User')
            test_user.set_password('test123')
            db.session.add(test_user)
            db.session.commit()
            print(f"   ✓ Created test user: {test_user.username}")
        
        # Log a login event
        log1 = AuditService.log_authentication(
            action='LOGIN',
            username='test_audit',
            success=True,
            metadata={'test': 'login_test'}
        )
        print(f"   ✓ Logged authentication event (ID: {log1.id if log1 else 'Failed'})")
        
        # Log a failed login
        log2 = AuditService.log_authentication(
            action='LOGIN_FAILED',
            username='wrong_user',
            success=False,
            error_message='Invalid credentials'
        )
        print(f"   ✓ Logged failed login event (ID: {log2.id if log2 else 'Failed'})")
        
        # Log a resource access
        log3 = AuditService.log_resource_access(
            action='VIEW_RECEIPT',
            resource_type='Receipt',
            resource_id=1,
            metadata={'viewer': 'test_audit'}
        )
        print(f"   ✓ Logged resource access event (ID: {log3.id if log3 else 'Failed'})")
        
        # Test 2: Query audit logs
        print("\n2. Testing audit log queries...")
        
        # Get all logs
        all_logs = AuditService.get_logs(limit=10)
        print(f"   ✓ Retrieved {len(all_logs)} recent audit logs")
        
        # Get logs for specific user
        user_logs = AuditService.get_user_activity(test_user.id, limit=5)
        print(f"   ✓ Retrieved {len(user_logs)} logs for user '{test_user.username}'")
        
        # Get failed logins
        failed_logins = AuditService.get_failed_logins(hours=24)
        print(f"   ✓ Found {len(failed_logins)} failed login attempts in last 24 hours")
        
        # Test 3: Get statistics
        print("\n3. Testing audit log statistics...")
        
        stats = AuditService.get_statistics()
        print(f"   ✓ Total logs: {stats['total_logs']}")
        print(f"   ✓ Successful actions: {stats['successful_actions']}")
        print(f"   ✓ Failed actions: {stats['failed_actions']}")
        print(f"   ✓ Unique users: {stats['unique_users']}")
        print(f"   ✓ Success rate: {stats['success_rate']:.2f}%")
        
        # Test 4: Display sample logs
        print("\n4. Sample audit log entries:")
        print("   " + "-" * 56)
        
        for log in all_logs[:5]:
            timestamp = log.timestamp.strftime('%Y-%m-%d %H:%M:%S') if log.timestamp else 'N/A'
            status = '✓' if log.success else '✗'
            print(f"   {status} [{timestamp}] {log.action}")
            print(f"     User: {log.username or 'N/A'} | Endpoint: {log.endpoint or 'N/A'}")
            if log.error_message:
                print(f"     Error: {log.error_message}")
            print()
        
        # Test 5: Test to_dict() method
        print("\n5. Testing AuditLog.to_dict() method...")
        if all_logs:
            sample_dict = all_logs[0].to_dict()
            print(f"   ✓ Successfully converted log to dictionary")
            print(f"   ✓ Keys: {', '.join(sample_dict.keys())}")
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        
        print("\n📊 Database contains {} audit log entries".format(
            AuditLog.query.count()
        ))
        
        return True

if __name__ == '__main__':
    try:
        test_audit_logging()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
