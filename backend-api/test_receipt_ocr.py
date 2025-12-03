#!/usr/bin/env python3
"""
Test script to verify receipt OCR functionality with a sample image
"""

from app.services.gemini_service import extract_receipt_data

# Test with a sample receipt image URL (you should replace this with a real receipt URL)
# For testing, you can use any publicly accessible receipt image URL

def test_receipt_extraction():
    """Test receipt data extraction"""
    
    print("=" * 60)
    print("Testing Receipt OCR with Gemini")
    print("=" * 60)
    
    # Example: Use a public receipt image for testing
    # You should replace this with your actual receipt image URL
    test_image_url = "https://example.com/sample-receipt.jpg"
    
    print(f"\nTest Image URL: {test_image_url}")
    print("\nNote: Replace the URL above with a real receipt image URL for testing.")
    print("\nAttempting to extract data from receipt...")
    print("-" * 60)
    
    # Uncomment below when you have a real image URL to test
    # result = extract_receipt_data(test_image_url)
    # 
    # if result:
    #     print("\n✓ SUCCESS! Extracted data:")
    #     print(f"  Vendor Name: {result.get('vendor_name')}")
    #     print(f"  Receipt Number: {result.get('receipt_number')}")
    #     print(f"  Total Amount: {result.get('total_amount')}")
    #     print(f"  Currency: {result.get('currency')}")
    #     print(f"  Transaction Date: {result.get('transaction_date')}")
    # else:
    #     print("\n✗ FAILED: Could not extract data from receipt")
    
    print("\nTo test with a real receipt:")
    print("1. Upload a receipt image to a public URL (e.g., Imgur, Google Drive with public link)")
    print("2. Replace test_image_url in this script with your image URL")
    print("3. Uncomment the extraction code above")
    print("4. Run: python test_receipt_ocr.py")
    print("\nAlternatively, use the API endpoint:")
    print("POST http://localhost:5000/api/receipts/upload")
    print('Body: {"image_url": "YOUR_IMAGE_URL"}')
    print('Headers: {"Authorization": "Bearer YOUR_JWT_TOKEN"}')

if __name__ == "__main__":
    test_receipt_extraction()
