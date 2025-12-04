#!/usr/bin/env python3
"""
Create a test user for development purposes.
"""
from app import create_app, db
from app.models import User, UserRole

app = create_app()

with app.app_context():
    # Check if test user already exists
    existing_user = User.query.filter_by(username='test').first()
    
    if existing_user:
        print("Test user 'test' already exists.")
        print(f"  - ID: {existing_user.id}")
        print(f"  - Email: {existing_user.email}")
        print(f"  - Role: {existing_user.role}")
    else:
        # Create test user
        test_user = User(
            username='test',
            email='test@example.com',
            role=UserRole.BASIC_USER.value
        )
        test_user.set_password('test')
        
        db.session.add(test_user)
        db.session.commit()
        
        print("Test user created successfully!")
        print(f"  - Username: test")
        print(f"  - Password: test")
        print(f"  - Email: test@example.com")
        print(f"  - Role: {test_user.role}")
