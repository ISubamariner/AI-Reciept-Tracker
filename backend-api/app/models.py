# app/models.py

from app import db
from flask_bcrypt import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt
from config import Config
from enum import Enum
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB # Recommended for flexible structured data

# Define the user roles for the database using Python Enum
# This ensures roles are consistent and database-enforced
class UserRole(Enum):
    SYSTEM_ADMIN = 'System Admin'
    RECEIPT_LOGGER = 'Receipt Logger'
    BASIC_USER = 'Basic User'

    def __str__(self):
        return self.value

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    # FIX: Pass the string values of the UserRole members to db.Enum
    role = db.Column(
        db.Enum(
            # Extract the string value from each member of the UserRole enum
            *[r.value for r in list(UserRole)],
            name='user_roles_enum' # Optional: name the enum type in the database
        ),
        default=UserRole.BASIC_USER.value,
        nullable=False
    )
    
    # Optional: Track status
    is_active = db.Column(db.Boolean, default=True)
    
    # User preferences (nullable to avoid FK constraint before currency tables exist)
    preferred_currency = db.Column(db.String(3), nullable=True, default='USD')

    # Relationship to transactions (will be defined later)
    # transactions = db.relationship('Transaction', backref='user', lazy='dynamic')

    def set_password(self, password):
        """Hashes the plain-text password and stores it."""
        self.password_hash = generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Checks the stored hash against the provided password."""
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expires_in=3600):
        """Generates a JWT for API authentication (valid for 1 hour by default)."""
        now = datetime.utcnow()
        return jwt.encode({
            'user_id': self.id,
            'username': self.username,
            'role': str(self.role),
            'exp': now + timedelta(seconds=expires_in), # Expiration time
            'iat': now # Issued at time
        },
        Config.SECRET_KEY,
        algorithm='HS256'
        )

    @staticmethod
    def verify_auth_token(token):
        """Decodes and verifies a JWT token."""
        try:
            data = jwt.decode(
                token, 
                Config.SECRET_KEY, 
                algorithms=['HS256']
            )
        except:
            return None
        
        # Return the User object if verification is successful
        return User.query.get(data['user_id'])

    def __repr__(self):
        return f'<User {self.username}, Role: {self.role}>'
    
class Receipt(db.Model):
    """
    Model for storing receipt metadata and the raw image location/data.
    """
    __tablename__ = 'receipts'

    id = db.Column(db.Integer, primary_key=True)
    
    # Link to the user who uploaded the receipt
    uploader_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Store the URL or file path to the actual receipt image (e.g., in Cloudflare R2)
    image_url = db.Column(db.String(512), nullable=False)
    
    # Metadata from the AI extraction (raw, unstructured output)
    raw_ai_data = db.Column(JSONB)
    
    # Status tracking
    status = db.Column(db.String(50), default='PENDING', nullable=False) # E.g., PENDING, PROCESSED, ERROR
    
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    # Relationship to transactions (One-to-One: one receipt creates one transaction)
    transaction = db.relationship('Transaction', backref='source_receipt', uselist=False)

    def __repr__(self):
        return f'<Receipt {self.id} Status: {self.status}>'

class Transaction(db.Model):
    """
    Model for storing structured, validated financial data.
    """
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Link back to the receipt that created this transaction
    receipt_id = db.Column(db.Integer, db.ForeignKey('receipts.id'), unique=True, nullable=False)

    # Core transaction data
    vendor_name = db.Column(db.String(128))
    receipt_number = db.Column(db.String(128), index=True)
    
    # Financial data (use Decimal in production for currency, but Float/Numeric for simplicity here)
    original_amount = db.Column(db.Numeric(10, 2), nullable=True)  # Original amount from receipt (nullable for backwards compatibility)
    original_currency = db.Column(db.String(3), nullable=True, default='USD')  # Original currency (no FK to avoid dependency)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)  # Amount in USD (base currency)
    currency = db.Column(db.String(10), default='USD', nullable=False)  # Base currency (USD)
    exchange_rate_used = db.Column(db.Numeric(20, 10), nullable=True)  # Rate used for conversion
    transaction_date = db.Column(db.DateTime, index=True)
    
    # Payer information
    payer_name = db.Column(db.String(128))  # Name extracted from receipt (e.g., card holder, customer name)
    
    # Status/Description
    description = db.Column(db.String(256))

    # Link to the user who *paid* (The user who incurred the expense)
    payer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) 
    
    # Relationship to the Receipt (Back-reference is 'source_receipt')
    
    # Future: You will likely need another table (a relationship table) to handle money flow
    # between multiple users, but we'll start with a single payer/uploader for now.

    def __repr__(self):
        return f'<Transaction {self.id} Total: {self.total_amount}>'


class Currency(db.Model):
    """
    Model for storing available currencies with their metadata.
    """
    __tablename__ = 'currencies'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(3), unique=True, nullable=False, index=True)  # ISO 4217 code (e.g., USD, EUR, PHP)
    name = db.Column(db.String(64), nullable=False)  # Full name (e.g., United States Dollar)
    symbol = db.Column(db.String(10), nullable=False)  # Symbol (e.g., $, €, ₱)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Currency {self.code} - {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'symbol': self.symbol,
            'is_active': self.is_active
        }


class ExchangeRate(db.Model):
    """
    Model for storing daily exchange rates with USD as base currency.
    Updates every 12 hours.
    """
    __tablename__ = 'exchange_rates'
    
    id = db.Column(db.Integer, primary_key=True)
    currency_code = db.Column(db.String(3), db.ForeignKey('currencies.code'), nullable=False, index=True)
    rate_to_usd = db.Column(db.Numeric(20, 10), nullable=False)  # Rate to convert to USD
    rate_from_usd = db.Column(db.Numeric(20, 10), nullable=False)  # Rate to convert from USD
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    source = db.Column(db.String(64), default='manual')  # Source of the rate (e.g., 'exchangerate-api', 'manual')
    
    # Relationship to currency
    currency = db.relationship('Currency', backref=db.backref('exchange_rates', lazy='dynamic'))
    
    # Composite unique constraint to prevent duplicate rates for same currency at same time
    __table_args__ = (
        db.Index('idx_currency_timestamp', 'currency_code', 'timestamp'),
    )
    
    def __repr__(self):
        return f'<ExchangeRate {self.currency_code}: 1 USD = {self.rate_from_usd} at {self.timestamp}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'currency_code': self.currency_code,
            'rate_to_usd': float(self.rate_to_usd),
            'rate_from_usd': float(self.rate_from_usd),
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'source': self.source
        }


class AuditLog(db.Model):
    """
    Model for storing audit log entries for user sessions and API calls.
    Tracks who did what, when, where, and the result.
    """
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Who: User information
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Null for unauthenticated requests
    username = db.Column(db.String(64), nullable=True)  # Denormalized for performance/retention
    user_role = db.Column(db.String(64), nullable=True)
    
    # What: Action details
    action = db.Column(db.String(128), nullable=False)  # E.g., 'LOGIN', 'UPLOAD_RECEIPT', 'DELETE_USER'
    resource_type = db.Column(db.String(64), nullable=True)  # E.g., 'Receipt', 'User', 'Transaction'
    resource_id = db.Column(db.Integer, nullable=True)  # ID of the affected resource
    
    # How: Request details
    method = db.Column(db.String(10), nullable=False)  # HTTP method: GET, POST, PUT, DELETE
    endpoint = db.Column(db.String(256), nullable=False)  # API endpoint path
    
    # Where: Network information
    ip_address = db.Column(db.String(45), nullable=True)  # IPv4 or IPv6
    user_agent = db.Column(db.String(512), nullable=True)  # Browser/client information
    
    # When: Timestamp
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow, nullable=False)
    
    # Result: Status and details
    status_code = db.Column(db.Integer, nullable=True)  # HTTP status code
    success = db.Column(db.Boolean, default=True, nullable=False)
    error_message = db.Column(db.Text, nullable=True)  # Error details if failed
    
    # Additional context (flexible JSON field)
    request_metadata = db.Column(JSONB, nullable=True)  # Additional context like query params, data changes, etc.
    
    # Session tracking
    session_id = db.Column(db.String(128), nullable=True)  # For tracking user sessions
    
    # Relationship to User
    user = db.relationship('User', backref=db.backref('audit_logs', lazy='dynamic'))
    
    def __repr__(self):
        return f'<AuditLog {self.id}: {self.action} by {self.username} at {self.timestamp}>'
    
    def to_dict(self):
        """Convert audit log to dictionary for API responses."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'user_role': self.user_role,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'method': self.method,
            'endpoint': self.endpoint,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'status_code': self.status_code,
            'success': self.success,
            'error_message': self.error_message,
            'metadata': self.request_metadata,
            'session_id': self.session_id
        }