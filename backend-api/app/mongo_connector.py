# app/mongo_connector.py

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MongoDBConnector:
    """
    MongoDB connector for managing receipt documents with archiving capabilities.
    """
    
    _client = None
    _db = None
    
    @classmethod
    def initialize(cls):
        """Initialize MongoDB connection."""
        if cls._client is None:
            mongodb_url = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/')
            
            try:
                cls._client = MongoClient(
                    mongodb_url,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=10000
                )
                
                # Test connection
                cls._client.admin.command('ping')
                
                # Get database (defaults to 'receipts')
                db_name = 'receipts'
                cls._db = cls._client[db_name]
                
                # Create collections and indexes
                cls._setup_collections()
                
                logger.info(f"MongoDB connected successfully to database: {db_name}")
                
            except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                logger.error(f"Failed to connect to MongoDB: {e}")
                raise
    
    @classmethod
    def _setup_collections(cls):
        """Set up collections and indexes for optimal performance."""
        if cls._db is None:
            return
        
        # Receipts collection
        receipts_collection = cls._db.receipts
        
        # Create indexes for efficient querying
        receipts_collection.create_index([('receipt_id', 1)], unique=True)
        receipts_collection.create_index([('uploader_id', 1)])
        receipts_collection.create_index([('status', 1)])
        receipts_collection.create_index([('created_at', -1)])
        receipts_collection.create_index([('archived', 1)])
        receipts_collection.create_index([('archive_date', 1)])
        
        # Compound indexes for common queries
        receipts_collection.create_index([('uploader_id', 1), ('status', 1)])
        receipts_collection.create_index([('archived', 1), ('created_at', -1)])
        
        logger.info("MongoDB collections and indexes set up successfully")
    
    @classmethod
    def get_db(cls):
        """Get the database instance."""
        if cls._db is None:
            cls.initialize()
        return cls._db
    
    @classmethod
    def get_collection(cls, collection_name='receipts'):
        """Get a specific collection."""
        db = cls.get_db()
        return db[collection_name]
    
    @classmethod
    def close(cls):
        """Close MongoDB connection."""
        if cls._client:
            cls._client.close()
            cls._client = None
            cls._db = None
            logger.info("MongoDB connection closed")


class ReceiptDocument:
    """
    Helper class for working with receipt documents in MongoDB.
    
    Document Structure:
    {
        "receipt_id": int,              # Reference to PostgreSQL receipt ID
        "uploader_id": int,             # User who uploaded
        "image_url": str,               # Location of receipt image
        "image_data": Binary,           # Optional: store actual image data
        "status": str,                  # PENDING, CONFIRMED, ERROR
        "raw_ai_data": dict,            # Extracted data from Gemini
        "extracted_items": [            # Line items from receipt
            {
                "description": str,
                "amount": float,
                "quantity": int,
                "unit_price": float
            }
        ],
        "metadata": {
            "vendor_name": str,
            "total_amount": float,
            "currency": str,
            "transaction_date": datetime,
            "receipt_number": str
        },
        "archived": bool,               # Archive flag
        "archive_date": datetime,       # When it was archived
        "archive_reason": str,          # Why it was archived
        "created_at": datetime,
        "updated_at": datetime,
        "tags": [str],                  # For categorization
        "file_size": int,               # Size in bytes
        "mime_type": str                # Image format
    }
    """
    
    @staticmethod
    def create_document(receipt_id, uploader_id, image_url, **kwargs):
        """Create a new receipt document."""
        document = {
            'receipt_id': receipt_id,
            'uploader_id': uploader_id,
            'image_url': image_url,
            'status': kwargs.get('status', 'PENDING'),
            'raw_ai_data': kwargs.get('raw_ai_data', {}),
            'extracted_items': kwargs.get('extracted_items', []),
            'metadata': kwargs.get('metadata', {}),
            'archived': False,
            'archive_date': None,
            'archive_reason': None,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'tags': kwargs.get('tags', []),
            'file_size': kwargs.get('file_size'),
            'mime_type': kwargs.get('mime_type'),
            'image_data': kwargs.get('image_data')  # Optional binary data
        }
        
        return document
    
    @staticmethod
    def archive_document(receipt_id, reason='user_requested'):
        """
        Archive a receipt document.
        
        Args:
            receipt_id: The receipt ID to archive
            reason: Reason for archiving (e.g., 'old_data', 'user_requested', 'processed')
        """
        collection = MongoDBConnector.get_collection('receipts')
        
        result = collection.update_one(
            {'receipt_id': receipt_id, 'archived': False},
            {
                '$set': {
                    'archived': True,
                    'archive_date': datetime.utcnow(),
                    'archive_reason': reason,
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def unarchive_document(receipt_id):
        """Unarchive a receipt document."""
        collection = MongoDBConnector.get_collection('receipts')
        
        result = collection.update_one(
            {'receipt_id': receipt_id, 'archived': True},
            {
                '$set': {
                    'archived': False,
                    'archive_date': None,
                    'archive_reason': None,
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def get_by_receipt_id(receipt_id, include_archived=False):
        """Get a receipt document by receipt_id."""
        collection = MongoDBConnector.get_collection('receipts')
        
        query = {'receipt_id': receipt_id}
        if not include_archived:
            query['archived'] = False
        
        return collection.find_one(query)
    
    @staticmethod
    def get_by_user(uploader_id, include_archived=False, limit=100, skip=0):
        """Get all receipts for a user."""
        collection = MongoDBConnector.get_collection('receipts')
        
        query = {'uploader_id': uploader_id}
        if not include_archived:
            query['archived'] = False
        
        return list(
            collection.find(query)
            .sort('created_at', -1)
            .skip(skip)
            .limit(limit)
        )
    
    @staticmethod
    def get_archived_receipts(uploader_id=None, days_old=None):
        """
        Get archived receipts with optional filters.
        
        Args:
            uploader_id: Filter by specific user
            days_old: Filter receipts archived more than X days ago
        """
        collection = MongoDBConnector.get_collection('receipts')
        
        query = {'archived': True}
        
        if uploader_id:
            query['uploader_id'] = uploader_id
        
        if days_old:
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            query['archive_date'] = {'$lt': cutoff_date}
        
        return list(collection.find(query).sort('archive_date', -1))
    
    @staticmethod
    def update_document(receipt_id, updates):
        """Update a receipt document."""
        collection = MongoDBConnector.get_collection('receipts')
        
        updates['updated_at'] = datetime.utcnow()
        
        result = collection.update_one(
            {'receipt_id': receipt_id},
            {'$set': updates}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def delete_document(receipt_id, permanent=False):
        """
        Delete a receipt document.
        
        Args:
            receipt_id: The receipt ID to delete
            permanent: If False, archives instead of deleting
        """
        collection = MongoDBConnector.get_collection('receipts')
        
        if permanent:
            result = collection.delete_one({'receipt_id': receipt_id})
            return result.deleted_count > 0
        else:
            return ReceiptDocument.archive_document(receipt_id, reason='deleted')


# Initialize MongoDB connection when module is imported
def init_mongo_app(app):
    """Initialize MongoDB with Flask app context."""
    with app.app_context():
        try:
            MongoDBConnector.initialize()
            app.logger.info("MongoDB initialized successfully")
        except Exception as e:
            app.logger.error(f"Failed to initialize MongoDB: {e}")
            # Don't fail app startup if MongoDB is unavailable
            # The app can still function with PostgreSQL only
