# run.py

from app import create_app, db # These must be available in app/__init__.py
from app.models import User, UserRole 

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """
    Allows quick access to 'db' and 'User' objects in the Flask shell.
    """
    return {'db': db, 'User': User, 'UserRole': UserRole}

if __name__ == '__main__':
    app.run(debug=False)