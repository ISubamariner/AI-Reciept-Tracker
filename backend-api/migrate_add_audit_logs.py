# Migration script to add/update audit_logs table
# Run this if you have an existing database

from app import create_app, db
from app.models import AuditLog

app = create_app()

with app.app_context():
    try:
        # Check if table exists and try to create it
        db.create_all()
        print("✓ Audit logs table created/updated successfully.")
        
        # If table already exists but with old column name, we need to rename it
        # This is a simple fix for the metadata -> request_metadata rename
        from sqlalchemy import text
        
        # Check if we need to do the column rename
        try:
            result = db.session.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='audit_logs' AND column_name='metadata'"
            ))
            if result.fetchone():
                print("Found old 'metadata' column, renaming to 'request_metadata'...")
                db.session.execute(text(
                    "ALTER TABLE audit_logs RENAME COLUMN metadata TO request_metadata"
                ))
                db.session.commit()
                print("✓ Column renamed successfully.")
        except Exception as e:
            print(f"Note: Column rename check/update skipped: {e}")
            db.session.rollback()
        
        print("✓ The audit_logs table is now ready to track user sessions and API calls.")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        import traceback
        traceback.print_exc()
