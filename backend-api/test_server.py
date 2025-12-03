"""Test script to debug server startup issues"""
import sys
import traceback

try:
    print("Step 1: Importing modules...")
    from app import create_app, db
    from app.models import User, UserRole
    
    print("Step 2: Creating app...")
    app = create_app()
    
    print("Step 3: Initializing database...")
    with app.app_context():
        db.create_all()
        print("Database tables initialized.")
    
    print("Step 4: Starting Flask server...")
    app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)
    
except Exception as e:
    print(f"\nERROR OCCURRED:")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    print(f"\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
