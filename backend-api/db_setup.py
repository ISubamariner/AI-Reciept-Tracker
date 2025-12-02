# db_setup.py

from app import create_app, db
import logging

logging.basicConfig(level=logging.INFO)

app = create_app()

def initialize_database():
    """
    Initializes the database using the production environment variables.
    """
    logging.info("Attempting to initialize database tables...")
    try:
        with app.app_context():
            db.create_all()
            logging.info("Database tables initialized successfully (if they didn't exist).")
    except Exception as e:
        logging.error(f"Database initialization failed: {e}")
        # Re-raise the exception to stop the deployment if setup is critical
        raise

if __name__ == '__main__':
    initialize_database()