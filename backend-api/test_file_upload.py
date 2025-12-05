# test_file_upload.py
# Test script to verify the Gemini service works with uploaded files

import os
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test with a sample image
def test_gemini_with_file():
    """Test Gemini extraction with a file upload"""
    from app.services.gemini_service import extract_receipt_data
    
    # Create a simple test image (you would replace this with an actual receipt image)
    print("Creating test image...")
    img = Image.new('RGB', (800, 600), color='white')
    
    # Save to BytesIO to simulate file upload
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)  # Reset to beginning
    
    print("Testing Gemini extraction with file upload...")
    result = extract_receipt_data(image_file=img_bytes)
    
    print("\n=== Extraction Result ===")
    print(result)
    
    if 'error' in result:
        print(f"\n❌ Error: {result['error']}")
    else:
        print("\n✅ Extraction successful!")
        print(f"Vendor: {result.get('vendor_name')}")
        print(f"Amount: {result.get('total_amount')}")
        print(f"Date: {result.get('transaction_date')}")

if __name__ == "__main__":
    print("=== Gemini File Upload Test ===\n")
    
    # Check if API key is set
    if not os.environ.get('GEMINI_API_KEY'):
        print("❌ GEMINI_API_KEY not found in environment variables")
        print("Please set it in your .env file")
        exit(1)
    
    print("✅ GEMINI_API_KEY found")
    print("\nNote: This test uses a blank image, so extraction will likely fail.")
    print("To properly test, you should use an actual receipt image.\n")
    
    test_gemini_with_file()
