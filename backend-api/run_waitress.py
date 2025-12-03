"""Run Flask app with Waitress server for Windows compatibility"""
from app import create_app, db
from app.models import User, UserRole
from waitress import serve

app = create_app()

def initialize_database(app):
    """Creates tables within the application context if they do not already exist."""
    with app.app_context():
        db.create_all()
        print("Database tables initialized (if they didn't exist).")

if __name__ == '__main__':
    initialize_database(app)
    print("Starting Waitress server on http://127.0.0.1:5000")
    serve(app, host='127.0.0.1', port=5000)
