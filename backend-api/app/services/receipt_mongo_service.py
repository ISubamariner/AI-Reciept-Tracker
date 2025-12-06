# app/services/receipt_mongo_service.py

from app.mongo_connector import MongoDBConnector, ReceiptDocument
from datetime import datetime, timedelta
import logging
from bson import ObjectId

logger = logging.getLogger(__name__)


class ReceiptMongoService:
    """
    Service layer for managing receipt documents in MongoDB.
    Handles CRUD operations and archiving logic.
    """
    
    @staticmethod
    def save_receipt(receipt_id, uploader_id, image_url, raw_ai_data=None, 
                     extracted_items=None, metadata=None, **kwargs):
        """
        Save a receipt to MongoDB.
        
        Args:
            receipt_id: PostgreSQL receipt ID
            uploader_id: User who uploaded the receipt
            image_url: URL or path to receipt image
            raw_ai_data: Raw data from AI extraction
            extracted_items: List of line items
            metadata: Additional metadata (vendor, amount, etc.)
            **kwargs: Additional fields (file_size, mime_type, etc.)
        
        Returns:
            dict: The saved document or None on error
        """
        try:
            collection = MongoDBConnector.get_collection('receipts')
            
            # Check if document already exists
            existing = collection.find_one({'receipt_id': receipt_id})
            if existing:
                logger.warning(f"Receipt {receipt_id} already exists in MongoDB")
                return existing
            
            # Create document
            document = ReceiptDocument.create_document(
                receipt_id=receipt_id,
                uploader_id=uploader_id,
                image_url=image_url,
                raw_ai_data=raw_ai_data or {},
                extracted_items=extracted_items or [],
                metadata=metadata or {},
                **kwargs
            )
            
            # Insert into MongoDB
            result = collection.insert_one(document)
            document['_id'] = result.inserted_id
            
            logger.info(f"Receipt {receipt_id} saved to MongoDB")
            return document
            
        except Exception as e:
            logger.error(f"Error saving receipt to MongoDB: {e}")
            return None
    
    @staticmethod
    def get_receipt(receipt_id, include_archived=False):
        """
        Get a receipt by ID.
        
        Args:
            receipt_id: The receipt ID
            include_archived: Whether to include archived receipts
        
        Returns:
            dict: Receipt document or None
        """
        try:
            return ReceiptDocument.get_by_receipt_id(receipt_id, include_archived)
        except Exception as e:
            logger.error(f"Error getting receipt from MongoDB: {e}")
            return None
    
    @staticmethod
    def get_user_receipts(uploader_id, include_archived=False, limit=100, skip=0):
        """
        Get all receipts for a user.
        
        Args:
            uploader_id: User ID
            include_archived: Whether to include archived receipts
            limit: Maximum number of results
            skip: Number of results to skip (for pagination)
        
        Returns:
            list: List of receipt documents
        """
        try:
            receipts = ReceiptDocument.get_by_user(
                uploader_id, 
                include_archived, 
                limit, 
                skip
            )
            
            # Convert ObjectId to string for JSON serialization
            for receipt in receipts:
                if '_id' in receipt:
                    receipt['_id'] = str(receipt['_id'])
            
            return receipts
        except Exception as e:
            logger.error(f"Error getting user receipts from MongoDB: {e}")
            return []
    
    @staticmethod
    def update_receipt(receipt_id, updates):
        """
        Update a receipt document.
        
        Args:
            receipt_id: The receipt ID
            updates: Dictionary of fields to update
        
        Returns:
            bool: True if updated, False otherwise
        """
        try:
            success = ReceiptDocument.update_document(receipt_id, updates)
            if success:
                logger.info(f"Receipt {receipt_id} updated in MongoDB")
            return success
        except Exception as e:
            logger.error(f"Error updating receipt in MongoDB: {e}")
            return False
    
    @staticmethod
    def archive_receipt(receipt_id, reason='user_requested'):
        """
        Archive a receipt (soft delete).
        
        Args:
            receipt_id: The receipt ID
            reason: Reason for archiving
        
        Returns:
            bool: True if archived, False otherwise
        """
        try:
            success = ReceiptDocument.archive_document(receipt_id, reason)
            if success:
                logger.info(f"Receipt {receipt_id} archived: {reason}")
            return success
        except Exception as e:
            logger.error(f"Error archiving receipt in MongoDB: {e}")
            return False
    
    @staticmethod
    def unarchive_receipt(receipt_id):
        """
        Unarchive a receipt.
        
        Args:
            receipt_id: The receipt ID
        
        Returns:
            bool: True if unarchived, False otherwise
        """
        try:
            success = ReceiptDocument.unarchive_document(receipt_id)
            if success:
                logger.info(f"Receipt {receipt_id} unarchived")
            return success
        except Exception as e:
            logger.error(f"Error unarchiving receipt in MongoDB: {e}")
            return False
    
    @staticmethod
    def get_archived_receipts(uploader_id=None, days_old=None):
        """
        Get archived receipts with optional filters.
        
        Args:
            uploader_id: Filter by user (optional)
            days_old: Get receipts archived more than X days ago (optional)
        
        Returns:
            list: List of archived receipt documents
        """
        try:
            receipts = ReceiptDocument.get_archived_receipts(uploader_id, days_old)
            
            # Convert ObjectId to string
            for receipt in receipts:
                if '_id' in receipt:
                    receipt['_id'] = str(receipt['_id'])
            
            return receipts
        except Exception as e:
            logger.error(f"Error getting archived receipts from MongoDB: {e}")
            return []
    
    @staticmethod
    def delete_receipt(receipt_id, permanent=False):
        """
        Delete a receipt (permanently or soft delete via archive).
        
        Args:
            receipt_id: The receipt ID
            permanent: If True, permanently delete. If False, archive instead.
        
        Returns:
            bool: True if deleted, False otherwise
        """
        try:
            success = ReceiptDocument.delete_document(receipt_id, permanent)
            if success:
                action = "permanently deleted" if permanent else "archived"
                logger.info(f"Receipt {receipt_id} {action}")
            return success
        except Exception as e:
            logger.error(f"Error deleting receipt from MongoDB: {e}")
            return False
    
    @staticmethod
    def bulk_archive_old_receipts(days_old=90, uploader_id=None):
        """
        Bulk archive receipts older than specified days.
        
        Args:
            days_old: Archive receipts older than this many days
            uploader_id: Optional user filter
        
        Returns:
            int: Number of receipts archived
        """
        try:
            collection = MongoDBConnector.get_collection('receipts')
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            query = {
                'created_at': {'$lt': cutoff_date},
                'archived': False
            }
            
            if uploader_id:
                query['uploader_id'] = uploader_id
            
            result = collection.update_many(
                query,
                {
                    '$set': {
                        'archived': True,
                        'archive_date': datetime.utcnow(),
                        'archive_reason': f'auto_archived_after_{days_old}_days',
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            logger.info(f"Bulk archived {result.modified_count} receipts")
            return result.modified_count
            
        except Exception as e:
            logger.error(f"Error bulk archiving receipts: {e}")
            return 0
    
    @staticmethod
    def get_receipt_stats(uploader_id=None):
        """
        Get statistics about receipts.
        
        Args:
            uploader_id: Optional user filter
        
        Returns:
            dict: Statistics including total, archived, pending, etc.
        """
        try:
            collection = MongoDBConnector.get_collection('receipts')
            
            query = {}
            if uploader_id:
                query['uploader_id'] = uploader_id
            
            pipeline = [
                {'$match': query},
                {
                    '$group': {
                        '_id': None,
                        'total': {'$sum': 1},
                        'archived': {
                            '$sum': {'$cond': [{'$eq': ['$archived', True]}, 1, 0]}
                        },
                        'active': {
                            '$sum': {'$cond': [{'$eq': ['$archived', False]}, 1, 0]}
                        },
                        'pending': {
                            '$sum': {'$cond': [{'$eq': ['$status', 'PENDING']}, 1, 0]}
                        },
                        'confirmed': {
                            '$sum': {'$cond': [{'$eq': ['$status', 'CONFIRMED']}, 1, 0]}
                        },
                        'total_size': {'$sum': '$file_size'}
                    }
                }
            ]
            
            result = list(collection.aggregate(pipeline))
            
            if result:
                stats = result[0]
                stats.pop('_id', None)
                return stats
            
            return {
                'total': 0,
                'archived': 0,
                'active': 0,
                'pending': 0,
                'confirmed': 0,
                'total_size': 0
            }
            
        except Exception as e:
            logger.error(f"Error getting receipt stats: {e}")
            return {}
    
    @staticmethod
    def search_receipts(query_text, uploader_id=None, include_archived=False):
        """
        Search receipts by text (vendor name, receipt number, etc.).
        
        Args:
            query_text: Text to search for
            uploader_id: Optional user filter
            include_archived: Whether to include archived receipts
        
        Returns:
            list: List of matching receipt documents
        """
        try:
            collection = MongoDBConnector.get_collection('receipts')
            
            # Build search query
            search_conditions = {
                '$or': [
                    {'metadata.vendor_name': {'$regex': query_text, '$options': 'i'}},
                    {'metadata.receipt_number': {'$regex': query_text, '$options': 'i'}},
                    {'tags': {'$regex': query_text, '$options': 'i'}}
                ]
            }
            
            if uploader_id:
                search_conditions['uploader_id'] = uploader_id
            
            if not include_archived:
                search_conditions['archived'] = False
            
            receipts = list(collection.find(search_conditions).sort('created_at', -1))
            
            # Convert ObjectId to string
            for receipt in receipts:
                if '_id' in receipt:
                    receipt['_id'] = str(receipt['_id'])
            
            return receipts
            
        except Exception as e:
            logger.error(f"Error searching receipts: {e}")
            return []
