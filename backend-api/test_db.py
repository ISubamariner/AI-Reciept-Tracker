from app import create_app, db

app = create_app()

with app.app_context():
    try:
        db.create_all()
        print("✓ Database connection successful")
    except Exception as e:
        print(f"✗ Database error: {e}")
