# migrate_add_currency_system.py

"""
Database migration script to add currency system tables and update existing models.

This script:
1. Creates Currency table
2. Creates ExchangeRate table
3. Adds preferred_currency to User table
4. Updates Transaction table to include original_currency and exchange_rate_used
5. Initializes currency catalog
6. Fetches initial exchange rates
"""

import sys
import os

# Add parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models import Currency, ExchangeRate, User, Transaction
from app.services.currency_service import CurrencyService
from sqlalchemy import inspect, text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_table_exists(table_name):
    """Check if a table exists in the database."""
    inspector = inspect(db.engine)
    return table_name in inspector.get_table_names()

def check_column_exists(table_name, column_name):
    """Check if a column exists in a table."""
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def migrate():
    """Run the migration."""
    app = create_app()
    
    with app.app_context():
        logger.info("Starting currency system migration...")
        
        try:
            # Step 1: Create new tables
            logger.info("Step 1: Creating new tables...")
            
            if not check_table_exists('currencies'):
                logger.info("Creating 'currencies' table...")
                Currency.__table__.create(db.engine)
                logger.info("✓ 'currencies' table created")
            else:
                logger.info("✓ 'currencies' table already exists")
            
            if not check_table_exists('exchange_rates'):
                logger.info("Creating 'exchange_rates' table...")
                ExchangeRate.__table__.create(db.engine)
                logger.info("✓ 'exchange_rates' table created")
            else:
                logger.info("✓ 'exchange_rates' table already exists")
            
            # Step 2: Add columns to existing tables
            logger.info("\nStep 2: Adding new columns to existing tables...")
            
            # Add preferred_currency to users table
            if check_table_exists('users'):
                if not check_column_exists('users', 'preferred_currency'):
                    logger.info("Adding 'preferred_currency' column to 'users' table...")
                    with db.engine.connect() as conn:
                        conn.execute(text(
                            "ALTER TABLE users ADD COLUMN preferred_currency VARCHAR(3) DEFAULT 'USD'"
                        ))
                        conn.commit()
                    logger.info("✓ Added 'preferred_currency' column")
                else:
                    logger.info("✓ 'preferred_currency' column already exists")
            
            # Add original_currency, original_amount, and exchange_rate_used to transactions table
            if check_table_exists('transactions'):
                if not check_column_exists('transactions', 'original_currency'):
                    logger.info("Adding 'original_currency' column to 'transactions' table...")
                    with db.engine.connect() as conn:
                        conn.execute(text(
                            "ALTER TABLE transactions ADD COLUMN original_currency VARCHAR(3) DEFAULT 'USD'"
                        ))
                        conn.commit()
                    logger.info("✓ Added 'original_currency' column")
                else:
                    logger.info("✓ 'original_currency' column already exists")
                
                if not check_column_exists('transactions', 'original_amount'):
                    logger.info("Adding 'original_amount' column to 'transactions' table...")
                    with db.engine.connect() as conn:
                        # Copy existing total_amount to original_amount
                        conn.execute(text(
                            "ALTER TABLE transactions ADD COLUMN original_amount NUMERIC(10, 2)"
                        ))
                        conn.execute(text(
                            "UPDATE transactions SET original_amount = total_amount WHERE original_amount IS NULL"
                        ))
                        conn.execute(text(
                            "ALTER TABLE transactions ALTER COLUMN original_amount SET NOT NULL"
                        ))
                        conn.commit()
                    logger.info("✓ Added 'original_amount' column")
                else:
                    logger.info("✓ 'original_amount' column already exists")
                
                if not check_column_exists('transactions', 'exchange_rate_used'):
                    logger.info("Adding 'exchange_rate_used' column to 'transactions' table...")
                    with db.engine.connect() as conn:
                        conn.execute(text(
                            "ALTER TABLE transactions ADD COLUMN exchange_rate_used NUMERIC(20, 10)"
                        ))
                        conn.commit()
                    logger.info("✓ Added 'exchange_rate_used' column")
                else:
                    logger.info("✓ 'exchange_rate_used' column already exists")
            
            # Step 3: Initialize currency catalog
            logger.info("\nStep 3: Initializing currency catalog...")
            added_count = CurrencyService.initialize_currencies()
            logger.info(f"✓ Initialized {added_count} currencies")
            
            # Step 4: Fetch initial exchange rates
            logger.info("\nStep 4: Fetching initial exchange rates...")
            success = CurrencyService.update_exchange_rates()
            if success:
                logger.info("✓ Successfully fetched initial exchange rates")
            else:
                logger.warning("⚠ Failed to fetch exchange rates from API, will retry later")
            
            # Step 5: Add foreign key constraints (if not exists)
            logger.info("\nStep 5: Adding foreign key constraints...")
            
            # This is handled by SQLAlchemy model definitions
            # but we'll ensure they exist
            try:
                with db.engine.connect() as conn:
                    # Check if FK for users.preferred_currency exists
                    inspector = inspect(db.engine)
                    fks = inspector.get_foreign_keys('users')
                    fk_exists = any(fk['constrained_columns'] == ['preferred_currency'] for fk in fks)
                    
                    if not fk_exists and check_column_exists('users', 'preferred_currency'):
                        conn.execute(text(
                            "ALTER TABLE users ADD CONSTRAINT fk_users_preferred_currency "
                            "FOREIGN KEY (preferred_currency) REFERENCES currencies(code)"
                        ))
                        conn.commit()
                        logger.info("✓ Added foreign key constraint for users.preferred_currency")
                    else:
                        logger.info("✓ Foreign key constraint already exists")
                        
            except Exception as e:
                logger.warning(f"⚠ Could not add foreign key constraints: {e}")
                logger.info("  This is okay if they already exist or if using SQLite")
            
            logger.info("\n" + "="*50)
            logger.info("✓ Currency system migration completed successfully!")
            logger.info("="*50)
            
        except Exception as e:
            logger.error(f"\n✗ Migration failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise

if __name__ == '__main__':
    migrate()
