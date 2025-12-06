from app import db, create_app
from sqlalchemy import inspect

app = create_app()

with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print('All tables:', tables)
    print('\ncurrencies exists:', 'currencies' in tables)
    print('exchange_rates exists:', 'exchange_rates' in tables)
    
    # Check users table columns
    if 'users' in tables:
        columns = inspector.get_columns('users')
        column_names = [col['name'] for col in columns]
        print('\nUsers table columns:', column_names)
        print('preferred_currency column exists:', 'preferred_currency' in column_names)
