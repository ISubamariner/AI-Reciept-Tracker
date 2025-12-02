# app/receipts/routes.py

from flask import Blueprint, request, jsonify, g
from app import db
from app.models import UserRole, Receipt, Transaction
from app.utils import jwt_required, role_required
from app.services.gemini_service import extract_receipt_data
from decimal import Decimal, InvalidOperation # For robust currency handling

bp = Blueprint('receipts', __name__)

@bp.route('/upload', methods=['POST'])
@jwt_required()
@role_required([UserRole.SYSTEM_ADMIN, UserRole.RECEIPT_LOGGER])
def upload_receipt():
    """
    Handles receipt processing: 
    1. Authenticates user and checks role.
    2. Receives a public URL for the image.
    3. Calls the Gemini service to extract data.
    4. Saves the raw and structured data to the database.
    """
    data = request.get_json()

    # 1. Validation and Role Check (Done via decorators, but check input here)
    if not data or not data.get('image_url'):
        return jsonify({'message': 'Missing required field: image_url (public link to the receipt).'}), 400

    image_url = data['image_url']
    
    # Check if user has permission (handled by @role_required, but good to understand)
    # The current user is available via g.current_user thanks to @jwt_required
    uploader_id = g.current_user.id
    
    # 2. Log the Receipt Entry (Initial PENDING state)
    # This is important for auditing, even if the AI fails later.
    new_receipt = Receipt(
        uploader_id=uploader_id,
        image_url=image_url,
        status='PENDING'
    )
    db.session.add(new_receipt)
    db.session.commit()
    
    receipt_id = new_receipt.id
    
    # --- AI INTEGRATION ---
    
    # 3. Call the Gemini Extraction Service
    extracted_data = extract_receipt_data(image_url=image_url)
    
    # 4. Handle Extraction Failure
    if not extracted_data:
        new_receipt.status = 'ERROR'
        db.session.commit()
        return jsonify({
            'message': 'AI extraction failed. Please check the image or API key.',
            'receipt_id': receipt_id
        }), 500
        
    # --- Data Processing and Saving ---
    
    # Update receipt with raw data
    new_receipt.raw_ai_data = extracted_data

    # 5. Validate and Convert Extracted Data
    try:
        total_amount = Decimal(extracted_data.get('total_amount', 0))
        # Ensure transaction_date is saved in the correct format for the database
        transaction_date_str = extracted_data.get('transaction_date')
        
        # Simple date parsing (you'd use a more robust library like dateutil here)
        from datetime import datetime
        transaction_date = datetime.strptime(transaction_date_str, '%Y-%m-%d')
        
    except (KeyError, InvalidOperation, ValueError) as e:
        new_receipt.status = 'ERROR_DATA_PARSE'
        db.session.commit()
        return jsonify({
            'message': f'Extracted data could not be parsed: {e}',
            'raw_data': extracted_data
        }), 400

    # 6. Create the Structured Transaction
    new_transaction = Transaction(
        receipt_id=receipt_id,
        vendor_name=extracted_data.get('vendor_name'),
        receipt_number=extracted_data.get('receipt_number'),
        total_amount=total_amount,
        transaction_date=transaction_date,
        payer_id=uploader_id, # Assume uploader is the payer for simplicity
        description=f"Transaction processed from Receipt ID {receipt_id}",
    )
    
    db.session.add(new_transaction)
    
    # 7. Finalize Status
    new_receipt.status = 'PROCESSED'
    db.session.commit()

    return jsonify({
        'message': 'Receipt processed and data saved successfully.',
        'receipt_id': receipt_id,
        'transaction_id': new_transaction.id,
        'extracted_data': extracted_data
    }), 201