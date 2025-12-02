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
    total_amount = db.Column(db.Numeric(10, 2), nullable=False) 
    transaction_date = db.Column(db.DateTime, index=True)
    
    # Status/Description
    description = db.Column(db.String(256))

    # Link to the user who *paid* (The user who incurred the expense)
    payer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) 
    
    # Relationship to the Receipt (Back-reference is 'source_receipt')
    
    # Future: You will likely need another table (a relationship table) to handle money flow
    # between multiple users, but we'll start with a single payer/uploader for now.

    def __repr__(self):
        return f'<Transaction {self.id} Total: {self.total_amount}>'