# run.py

from app import create_app, db # These must be available in app/__init__.py
from app.models import User, UserRole 

app = create_app()

def initialize_database(app):
    """
    Creates tables within the application context if they do not already exist.
    """
    with app.app_context():
        # This function only creates tables that don't exist, making it safe to run at startup.
        db.create_all()
        print("Database tables initialized (if they didn't exist).")


@app.shell_context_processor
def make_shell_context():
    """
    Allows quick access to 'db' and 'User' objects in the Flask shell.
    """
    return {'db': db, 'User': User, 'UserRole': UserRole}

if __name__ == '__main__':
    try:
        # Initialize database tables
        initialize_database(app)
        
        # Use Waitress WSGI server for Windows compatibility
        # Waitress is production-grade and doesn't have the issues Flask's dev server has on Windows
        print("="*60)
        print("Starting server with Waitress (production-ready WSGI server)")
        print("Server will be available at: http://127.0.0.1:5000")
        print("Press CTRL+C to quit")
        print("="*60)
        
        from waitress import serve
        serve(app, host='127.0.0.1', port=5000, threads=4)
    except Exception as e:
        print(f"\nERROR: Failed to start server!")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")