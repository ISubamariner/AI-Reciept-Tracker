# app/receipts/routes.py

from flask import Blueprint, request, jsonify, g, send_from_directory
from app import db
from app.models import UserRole, Receipt, Transaction
from app.utils import jwt_required, role_required, audit_log
from app.services.gemini_service import extract_receipt_data
from app.services.audit_service import AuditService
from app.services.receipt_mongo_service import ReceiptMongoService
from decimal import Decimal, InvalidOperation # For robust currency handling
import os
from werkzeug.utils import secure_filename
from config import Config

bp = Blueprint('receipts', __name__)

@bp.route('/uploads/<filename>', methods=['GET'])
def serve_uploaded_file(filename):
    """
    Serve uploaded receipt images.
    Public endpoint - no authentication required for viewing images.
    """
    try:
        upload_folder = Config.UPLOAD_FOLDER
        return send_from_directory(upload_folder, filename)
    except FileNotFoundError:
        return jsonify({'message': 'File not found'}), 404

@bp.route('/upload', methods=['POST'])
@audit_log(action='UPLOAD_RECEIPT', resource_type='Receipt')
@jwt_required()
@role_required([UserRole.SYSTEM_ADMIN, UserRole.RECEIPT_LOGGER])
def upload_receipt():
    """
    Step 1: Extract data from receipt and return for user validation.
    
    1. Authenticates user and checks role.
    2. Receives either an uploaded image file or a public URL.
    3. Calls the Gemini service to extract data.
    4. Saves receipt with PENDING_CONFIRMATION status.
    5. Returns extracted data for user to review and confirm.
    
    NOTE: Data is NOT committed to transactions table until /confirm endpoint is called.
    """
    uploader_id = g.current_user.id
    image_url = None
    image_file = None
    
    # Check if this is a file upload or JSON with URL
    if request.content_type and 'multipart/form-data' in request.content_type:
        # File upload
        if 'image' not in request.files:
            return jsonify({'message': 'No image file provided in the request.'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'message': 'No file selected.'}), 400
        
        # Validate file extension
        filename = secure_filename(file.filename)
        if not filename or '.' not in filename:
            return jsonify({'message': 'Invalid file name.'}), 400
        
        file_ext = filename.rsplit('.', 1)[1].lower()
        if file_ext not in Config.ALLOWED_EXTENSIONS:
            return jsonify({'message': f'File type not allowed. Allowed types: {Config.ALLOWED_EXTENSIONS}'}), 400
        
        # Create unique filename to avoid collisions
        import time
        unique_filename = f"{int(time.time())}_{filename}"
        
        # Ensure uploads directory exists
        upload_folder = Config.UPLOAD_FOLDER
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        # Save file to disk
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        # Store the file object for processing (reset pointer after save)
        file.seek(0)
        image_file = file
        image_url = f"uploaded://{unique_filename}"  # Store a reference in the database
    else:
        # JSON with URL
        data = request.get_json()
        if not data or not data.get('image_url'):
            return jsonify({'message': 'Missing required field: either upload an image file or provide image_url.'}), 400
        image_url = data['image_url']
    
    # 2. Log the Receipt Entry (Initial PENDING_CONFIRMATION state)
    new_receipt = Receipt(
        uploader_id=uploader_id,
        image_url=image_url,
        status='PENDING_CONFIRMATION'
    )
    db.session.add(new_receipt)
    db.session.commit()
    
    receipt_id = new_receipt.id
    
    # --- AI INTEGRATION ---
    
    # 3. Call the Gemini Extraction Service
    if image_file:
        extracted_data = extract_receipt_data(image_file=image_file)
    else:
        extracted_data = extract_receipt_data(image_url=image_url)
    
    # 4. Handle Extraction Failure
    if not extracted_data or 'error' in extracted_data:
        new_receipt.status = 'ERROR'
        error_msg = extracted_data.get('error', 'Unknown error') if extracted_data else 'AI extraction returned no data'
        db.session.commit()
        return jsonify({
            'message': 'AI extraction failed.',
            'error': error_msg,
            'receipt_id': receipt_id
        }), 500
        
    # --- Save extracted data for confirmation ---
    
    # Update receipt with raw data
    new_receipt.raw_ai_data = extracted_data
    db.session.commit()

    # --- Save to MongoDB for long-term storage ---
    try:
        # Prepare metadata for MongoDB
        metadata = {
            'vendor_name': extracted_data.get('vendor_name'),
            'total_amount': float(extracted_data.get('total_amount', 0)) if extracted_data.get('total_amount') else None,
            'currency': extracted_data.get('currency', 'USD'),
            'transaction_date': extracted_data.get('transaction_date'),
            'receipt_number': extracted_data.get('receipt_number')
        }
        
        # Get file info if available
        file_size = None
        mime_type = None
        if image_file:
            image_file.seek(0, 2)  # Seek to end
            file_size = image_file.tell()
            image_file.seek(0)  # Reset
            mime_type = image_file.content_type
        
        # Save to MongoDB
        ReceiptMongoService.save_receipt(
            receipt_id=receipt_id,
            uploader_id=uploader_id,
            image_url=image_url,
            raw_ai_data=extracted_data,
            metadata=metadata,
            status='PENDING_CONFIRMATION',
            file_size=file_size,
            mime_type=mime_type
        )
    except Exception as e:
        # Log error but don't fail the request
        import logging
        logging.error(f"Failed to save receipt to MongoDB: {e}")

    # Return extracted data for user confirmation
    return jsonify({
        'message': 'Receipt uploaded and data extracted successfully. Please review and confirm.',
        'receipt_id': receipt_id,
        'extracted_data': {
            'vendor_name': extracted_data.get('vendor_name'),
            'receipt_number': extracted_data.get('receipt_number'),
            'total_amount': extracted_data.get('total_amount'),
            'currency': extracted_data.get('currency', 'USD'),
            'transaction_date': extracted_data.get('transaction_date'),
            'payer_name': extracted_data.get('payer_name')
        },
        'requires_confirmation': True
    }), 200


@bp.route('/confirm', methods=['POST'])
@audit_log(action='CONFIRM_RECEIPT', resource_type='Receipt')
@jwt_required()
@role_required([UserRole.SYSTEM_ADMIN, UserRole.RECEIPT_LOGGER])
def confirm_receipt():
    """
    Step 2: Confirm and save validated receipt data to transactions table.
    
    Accepts the receipt_id and validated/corrected data from the user.
    Creates the transaction record and marks receipt as PROCESSED.
    
    Expected JSON body:
    {
        "receipt_id": 123,
        "vendor_name": "Store Name",
        "receipt_number": "INV-12345",
        "total_amount": 45.99,
        "currency": "USD",
        "transaction_date": "2024-12-05",
        "payer_name": "John Doe"
    }
    """
    data = request.get_json()
    
    if not data or not data.get('receipt_id'):
        return jsonify({'message': 'Missing required field: receipt_id'}), 400
    
    receipt_id = data.get('receipt_id')
    uploader_id = g.current_user.id
    
    # Verify receipt exists and belongs to the user
    receipt = Receipt.query.filter_by(id=receipt_id, uploader_id=uploader_id).first()
    
    if not receipt:
        return jsonify({'message': 'Receipt not found or you do not have permission to confirm it.'}), 404
    
    if receipt.status == 'PROCESSED':
        return jsonify({'message': 'Receipt has already been processed.'}), 400
    
    if receipt.status != 'PENDING_CONFIRMATION':
        return jsonify({'message': f'Receipt cannot be confirmed. Current status: {receipt.status}'}), 400
    
    # Validate required fields
    required_fields = ['vendor_name', 'total_amount', 'transaction_date']
    missing_fields = [field for field in required_fields if not data.get(field)]
    
    if missing_fields:
        return jsonify({'message': f'Missing required fields: {", ".join(missing_fields)}'}), 400
    
    # Validate and convert data
    try:
        from datetime import datetime
        total_amount = Decimal(str(data.get('total_amount')))
        transaction_date = datetime.strptime(data.get('transaction_date'), '%Y-%m-%d')
        
    except (InvalidOperation, ValueError) as e:
        return jsonify({
            'message': f'Invalid data format: {e}',
            'hint': 'Ensure total_amount is a valid number and transaction_date is in YYYY-MM-DD format'
        }), 400
    
    # Get original currency and convert to USD (base currency)
    original_currency = data.get('currency', 'USD')
    original_amount = total_amount
    
    # Convert to USD if needed
    from app.services.currency_service import CurrencyService
    usd_amount = total_amount
    exchange_rate_used = None
    
    if original_currency != 'USD':
        try:
            converted_amount, rate_used, _ = CurrencyService.convert_amount(
                float(total_amount),
                original_currency,
                'USD'
            )
            usd_amount = Decimal(str(converted_amount))
            exchange_rate_used = Decimal(str(rate_used))
        except Exception as e:
            import logging
            logging.warning(f"Currency conversion failed: {e}. Using original amount.")
            # If conversion fails, use original amount and log warning
    
    # Create the transaction with user-confirmed data
    new_transaction = Transaction(
        receipt_id=receipt_id,
        vendor_name=data.get('vendor_name'),
        receipt_number=data.get('receipt_number'),
        original_amount=original_amount,
        original_currency=original_currency,
        total_amount=usd_amount,
        currency='USD',
        exchange_rate_used=exchange_rate_used,
        transaction_date=transaction_date,
        payer_name=data.get('payer_name'),
        payer_id=uploader_id,
        description=data.get('description', f"Transaction processed from Receipt ID {receipt_id}"),
    )
    
    db.session.add(new_transaction)
    
    # Mark receipt as processed
    receipt.status = 'PROCESSED'
    db.session.commit()
    
    # Update MongoDB with confirmed data
    try:
        ReceiptMongoService.update_receipt(
            receipt_id=receipt_id,
            updates={
                'status': 'PROCESSED',
                'metadata': {
                    'vendor_name': data.get('vendor_name'),
                    'total_amount': float(total_amount),
                    'currency': data.get('currency', 'USD'),
                    'transaction_date': transaction_date.isoformat(),
                    'receipt_number': data.get('receipt_number')
                }
            }
        )
    except Exception as e:
        import logging
        logging.error(f"Failed to update receipt in MongoDB: {e}")
    
    return jsonify({
        'message': 'Receipt confirmed and transaction saved successfully.',
        'receipt_id': receipt_id,
        'transaction_id': new_transaction.id,
        'transaction_data': {
            'vendor_name': new_transaction.vendor_name,
            'receipt_number': new_transaction.receipt_number,
            'total_amount': float(new_transaction.total_amount),
            'currency': new_transaction.currency,
            'transaction_date': new_transaction.transaction_date.isoformat(),
            'payer_name': new_transaction.payer_name
        }
    }), 201


@bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    """
    Retrieves all transactions for the authenticated user.
    Returns a list of transactions with receipt information.
    """
    user_id = g.current_user.id
    
    # Query transactions where the user is the payer
    transactions = Transaction.query.filter_by(payer_id=user_id).order_by(Transaction.transaction_date.desc()).all()
    
    # Format the response
    result = []
    for txn in transactions:
        result.append({
            'id': txn.id,
            'vendor_name': txn.vendor_name,
            'receipt_number': txn.receipt_number,
            'original_amount': float(txn.original_amount) if hasattr(txn, 'original_amount') and txn.original_amount else float(txn.total_amount),
            'original_currency': txn.original_currency if hasattr(txn, 'original_currency') and txn.original_currency else txn.currency,
            'total_amount': float(txn.total_amount),
            'currency': txn.currency,
            'exchange_rate_used': float(txn.exchange_rate_used) if hasattr(txn, 'exchange_rate_used') and txn.exchange_rate_used else None,
            'transaction_date': txn.transaction_date.isoformat() if txn.transaction_date else None,
            'payer_name': txn.payer_name,
            'description': txn.description,
            'receipt_id': txn.receipt_id,
            'image_url': txn.source_receipt.image_url if txn.source_receipt else None,
            'status': txn.source_receipt.status if txn.source_receipt else None
        })
    
    return jsonify({
        'transactions': result,
        'count': len(result)
    }), 200


@bp.route('/cancel', methods=['POST'])
@jwt_required()
@role_required([UserRole.SYSTEM_ADMIN, UserRole.RECEIPT_LOGGER])
def cancel_receipt():
    """
    Cancel a receipt that is pending confirmation.
    
    This allows users to reject extracted data and mark the receipt as cancelled.
    
    Expected JSON body:
    {
        "receipt_id": 123
    }
    """
    data = request.get_json()
    
    if not data or not data.get('receipt_id'):
        return jsonify({'message': 'Missing required field: receipt_id'}), 400
    
    receipt_id = data.get('receipt_id')
    uploader_id = g.current_user.id
    
    # Verify receipt exists and belongs to the user
    receipt = Receipt.query.filter_by(id=receipt_id, uploader_id=uploader_id).first()
    
    if not receipt:
        return jsonify({'message': 'Receipt not found or you do not have permission to cancel it.'}), 404
    
    if receipt.status == 'PROCESSED':
        return jsonify({'message': 'Cannot cancel a receipt that has already been processed.'}), 400
    
    # Mark receipt as cancelled
    receipt.status = 'CANCELLED'
    db.session.commit()
    
    return jsonify({
        'message': 'Receipt cancelled successfully.',
        'receipt_id': receipt_id
    }), 200


@bp.route('/reject', methods=['POST'])
@audit_log(action='REJECT_RECEIPT', resource_type='Receipt')
@jwt_required()
@role_required([UserRole.SYSTEM_ADMIN, UserRole.RECEIPT_LOGGER])
def reject_receipt():
    """
    Reject a receipt that is pending confirmation.
    
    This allows users to reject receipts (e.g., duplicates, errors) and mark them as rejected.
    Optionally accepts a reason for the rejection.
    
    Expected JSON body:
    {
        "receipt_id": 123,
        "reason": "Duplicate receipt" (optional)
    }
    """
    data = request.get_json()
    
    if not data or not data.get('receipt_id'):
        return jsonify({'message': 'Missing required field: receipt_id'}), 400
    
    receipt_id = data.get('receipt_id')
    reason = data.get('reason', 'No reason provided')
    uploader_id = g.current_user.id
    
    # Verify receipt exists and belongs to the user
    receipt = Receipt.query.filter_by(id=receipt_id, uploader_id=uploader_id).first()
    
    if not receipt:
        return jsonify({'message': 'Receipt not found or you do not have permission to reject it.'}), 404
    
    if receipt.status == 'PROCESSED':
        return jsonify({'message': 'Cannot reject a receipt that has already been processed.'}), 400
    
    # Mark receipt as rejected and store the reason
    receipt.status = 'REJECTED'
    
    # Store rejection reason in raw_ai_data if it exists, otherwise create new dict
    if receipt.raw_ai_data:
        receipt.raw_ai_data['rejection_reason'] = reason
    else:
        receipt.raw_ai_data = {'rejection_reason': reason}
    
    db.session.commit()
    
    return jsonify({
        'message': 'Receipt rejected successfully.',
        'receipt_id': receipt_id,
        'reason': reason
    }), 200


@bp.route('/pending', methods=['GET'])
@jwt_required()
@role_required([UserRole.SYSTEM_ADMIN, UserRole.RECEIPT_LOGGER])
def get_pending_receipts():
    """
    Get all receipts pending confirmation for the authenticated user.
    
    Returns receipts with status 'PENDING_CONFIRMATION' along with their extracted data.
    """
    uploader_id = g.current_user.id
    
    # Query receipts with PENDING_CONFIRMATION status
    pending_receipts = Receipt.query.filter_by(
        uploader_id=uploader_id,
        status='PENDING_CONFIRMATION'
    ).order_by(Receipt.timestamp.desc()).all()
    
    # Format the response
    result = []
    for receipt in pending_receipts:
        extracted_data = receipt.raw_ai_data or {}
        result.append({
            'receipt_id': receipt.id,
            'image_url': receipt.image_url,
            'timestamp': receipt.timestamp.isoformat() if receipt.timestamp else None,
            'extracted_data': {
                'vendor_name': extracted_data.get('vendor_name'),
                'receipt_number': extracted_data.get('receipt_number'),
                'total_amount': extracted_data.get('total_amount'),
                'currency': extracted_data.get('currency', 'USD'),
                'transaction_date': extracted_data.get('transaction_date'),
                'payer_name': extracted_data.get('payer_name')
            }
        })
    
    return jsonify({
        'pending_receipts': result,
        'count': len(result)
    }), 200


# ==================== MONGODB RECEIPT STORAGE ROUTES ====================

@bp.route('/mongo/<int:receipt_id>', methods=['GET'])
@jwt_required()
@role_required([UserRole.SYSTEM_ADMIN, UserRole.RECEIPT_LOGGER, UserRole.BASIC_USER])
def get_mongo_receipt(receipt_id):
    """
    Get a receipt from MongoDB by receipt_id.
    Includes archived receipts if user has permission.
    """
    include_archived = request.args.get('include_archived', 'false').lower() == 'true'
    
    # Verify receipt exists in PostgreSQL first
    receipt = Receipt.query.filter_by(id=receipt_id).first()
    if not receipt:
        return jsonify({'message': 'Receipt not found'}), 404
    
    # Check if user has permission to view this receipt
    if receipt.uploader_id != g.current_user.id and g.current_user.role != UserRole.SYSTEM_ADMIN.value:
        return jsonify({'message': 'You do not have permission to view this receipt'}), 403
    
    # Get from MongoDB
    mongo_receipt = ReceiptMongoService.get_receipt(receipt_id, include_archived)
    
    if not mongo_receipt:
        return jsonify({'message': 'Receipt not found in MongoDB storage'}), 404
    
    # Convert ObjectId to string for JSON serialization
    if '_id' in mongo_receipt:
        mongo_receipt['_id'] = str(mongo_receipt['_id'])
    
    return jsonify({
        'receipt': mongo_receipt
    }), 200


@bp.route('/mongo/user/<int:user_id>', methods=['GET'])
@jwt_required()
@role_required([UserRole.SYSTEM_ADMIN, UserRole.RECEIPT_LOGGER, UserRole.BASIC_USER])
def get_user_mongo_receipts(user_id):
    """
    Get all receipts for a user from MongoDB.
    Supports pagination and filtering.
    """
    # Check permission
    if user_id != g.current_user.id and g.current_user.role != UserRole.SYSTEM_ADMIN.value:
        return jsonify({'message': 'You do not have permission to view these receipts'}), 403
    
    # Parse query parameters
    include_archived = request.args.get('include_archived', 'false').lower() == 'true'
    limit = int(request.args.get('limit', 100))
    skip = int(request.args.get('skip', 0))
    
    # Limit maximum results
    limit = min(limit, 500)
    
    receipts = ReceiptMongoService.get_user_receipts(
        uploader_id=user_id,
        include_archived=include_archived,
        limit=limit,
        skip=skip
    )
    
    return jsonify({
        'receipts': receipts,
        'count': len(receipts),
        'limit': limit,
        'skip': skip
    }), 200


@bp.route('/mongo/archive/<int:receipt_id>', methods=['POST'])
@audit_log(action='ARCHIVE_RECEIPT', resource_type='Receipt')
@jwt_required()
@role_required([UserRole.SYSTEM_ADMIN, UserRole.RECEIPT_LOGGER])
def archive_mongo_receipt(receipt_id):
    """
    Archive a receipt in MongoDB (soft delete for easy storage management).
    """
    # Verify receipt exists and user has permission
    receipt = Receipt.query.filter_by(id=receipt_id).first()
    if not receipt:
        return jsonify({'message': 'Receipt not found'}), 404
    
    if receipt.uploader_id != g.current_user.id and g.current_user.role != UserRole.SYSTEM_ADMIN.value:
        return jsonify({'message': 'You do not have permission to archive this receipt'}), 403
    
    # Get optional reason
    data = request.get_json() or {}
    reason = data.get('reason', 'user_requested')
    
    # Archive in MongoDB
    success = ReceiptMongoService.archive_receipt(receipt_id, reason)
    
    if not success:
        return jsonify({'message': 'Failed to archive receipt'}), 500
    
    return jsonify({
        'message': 'Receipt archived successfully',
        'receipt_id': receipt_id,
        'reason': reason
    }), 200


@bp.route('/mongo/unarchive/<int:receipt_id>', methods=['POST'])
@audit_log(action='UNARCHIVE_RECEIPT', resource_type='Receipt')
@jwt_required()
@role_required([UserRole.SYSTEM_ADMIN, UserRole.RECEIPT_LOGGER])
def unarchive_mongo_receipt(receipt_id):
    """
    Unarchive a receipt in MongoDB.
    """
    # Verify receipt exists and user has permission
    receipt = Receipt.query.filter_by(id=receipt_id).first()
    if not receipt:
        return jsonify({'message': 'Receipt not found'}), 404
    
    if receipt.uploader_id != g.current_user.id and g.current_user.role != UserRole.SYSTEM_ADMIN.value:
        return jsonify({'message': 'You do not have permission to unarchive this receipt'}), 403
    
    # Unarchive in MongoDB
    success = ReceiptMongoService.unarchive_receipt(receipt_id)
    
    if not success:
        return jsonify({'message': 'Failed to unarchive receipt or receipt not found'}), 500
    
    return jsonify({
        'message': 'Receipt unarchived successfully',
        'receipt_id': receipt_id
    }), 200


@bp.route('/mongo/archived', methods=['GET'])
@jwt_required()
@role_required([UserRole.SYSTEM_ADMIN, UserRole.RECEIPT_LOGGER])
def get_archived_receipts():
    """
    Get all archived receipts with optional filters.
    Admins can see all, others see only their own.
    """
    # Parse query parameters
    days_old = request.args.get('days_old', type=int)
    
    # Filter by user unless admin
    user_id = None if g.current_user.role == UserRole.SYSTEM_ADMIN.value else g.current_user.id
    
    receipts = ReceiptMongoService.get_archived_receipts(
        uploader_id=user_id,
        days_old=days_old
    )
    
    return jsonify({
        'archived_receipts': receipts,
        'count': len(receipts)
    }), 200


@bp.route('/mongo/stats', methods=['GET'])
@jwt_required()
@role_required([UserRole.SYSTEM_ADMIN, UserRole.RECEIPT_LOGGER, UserRole.BASIC_USER])
def get_receipt_stats():
    """
    Get statistics about receipts from MongoDB.
    Users see their own stats, admins can see all.
    """
    # Get user_id from query or use current user
    user_id_param = request.args.get('user_id', type=int)
    
    # Admins can view any user's stats
    if user_id_param and g.current_user.role != UserRole.SYSTEM_ADMIN.value:
        if user_id_param != g.current_user.id:
            return jsonify({'message': 'You do not have permission to view these stats'}), 403
    
    user_id = user_id_param if user_id_param else g.current_user.id
    
    # For admins viewing all stats
    if g.current_user.role == UserRole.SYSTEM_ADMIN.value and not user_id_param:
        user_id = None
    
    stats = ReceiptMongoService.get_receipt_stats(uploader_id=user_id)
    
    return jsonify({
        'stats': stats
    }), 200


@bp.route('/mongo/search', methods=['GET'])
@jwt_required()
@role_required([UserRole.SYSTEM_ADMIN, UserRole.RECEIPT_LOGGER, UserRole.BASIC_USER])
def search_mongo_receipts():
    """
    Search receipts in MongoDB by vendor name, receipt number, or tags.
    """
    query_text = request.args.get('q', '').strip()
    include_archived = request.args.get('include_archived', 'false').lower() == 'true'
    
    if not query_text:
        return jsonify({'message': 'Missing search query parameter: q'}), 400
    
    # Filter by user unless admin
    user_id = None if g.current_user.role == UserRole.SYSTEM_ADMIN.value else g.current_user.id
    
    receipts = ReceiptMongoService.search_receipts(
        query_text=query_text,
        uploader_id=user_id,
        include_archived=include_archived
    )
    
    return jsonify({
        'results': receipts,
        'count': len(receipts),
        'query': query_text
    }), 200


@bp.route('/mongo/bulk-archive', methods=['POST'])
@audit_log(action='BULK_ARCHIVE_RECEIPTS', resource_type='Receipt')
@jwt_required()
@role_required([UserRole.SYSTEM_ADMIN])
def bulk_archive_old_receipts():
    """
    Bulk archive receipts older than specified days.
    Admin only operation.
    """
    data = request.get_json() or {}
    days_old = data.get('days_old', 90)
    user_id = data.get('user_id')  # Optional: filter by user
    
    if days_old < 30:
        return jsonify({'message': 'Cannot bulk archive receipts less than 30 days old'}), 400
    
    archived_count = ReceiptMongoService.bulk_archive_old_receipts(
        days_old=days_old,
        uploader_id=user_id
    )
    
    return jsonify({
        'message': f'Successfully archived {archived_count} receipts',
        'archived_count': archived_count,
        'days_old': days_old
    }), 200