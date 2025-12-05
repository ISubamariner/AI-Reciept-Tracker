# app/receipts/routes.py

from flask import Blueprint, request, jsonify, g
from app import db
from app.models import UserRole, Receipt, Transaction
from app.utils import jwt_required, role_required, audit_log
from app.services.gemini_service import extract_receipt_data
from app.services.audit_service import AuditService
from decimal import Decimal, InvalidOperation # For robust currency handling

bp = Blueprint('receipts', __name__)

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
        from werkzeug.utils import secure_filename
        filename = secure_filename(file.filename)
        if not filename or '.' not in filename:
            return jsonify({'message': 'Invalid file name.'}), 400
        
        file_ext = filename.rsplit('.', 1)[1].lower()
        from config import Config
        if file_ext not in Config.ALLOWED_EXTENSIONS:
            return jsonify({'message': f'File type not allowed. Allowed types: {Config.ALLOWED_EXTENSIONS}'}), 400
        
        # Store the file object for processing
        image_file = file
        image_url = f"uploaded://{filename}"  # Store a reference in the database
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
    
    # Create the transaction with user-confirmed data
    new_transaction = Transaction(
        receipt_id=receipt_id,
        vendor_name=data.get('vendor_name'),
        receipt_number=data.get('receipt_number'),
        total_amount=total_amount,
        currency=data.get('currency', 'USD'),
        transaction_date=transaction_date,
        payer_name=data.get('payer_name'),
        payer_id=uploader_id,
        description=data.get('description', f"Transaction processed from Receipt ID {receipt_id}"),
    )
    
    db.session.add(new_transaction)
    
    # Mark receipt as processed
    receipt.status = 'PROCESSED'
    db.session.commit()
    
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
            'total_amount': float(txn.total_amount),
            'currency': txn.currency,
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