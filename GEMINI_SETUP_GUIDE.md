# Gemini API Setup for Receipt OCR - Quick Reference

## ✅ What Was Fixed

Your Gemini API from Google AI Studio is now properly configured and working! Here's what was updated:

### 1. **Updated Package Dependencies**
- Changed from `google-genai` to `google-generativeai` (the correct SDK)
- Added `Pillow` for image processing
- Updated `requirements.txt` with correct versions

### 2. **Fixed Gemini Service (`app/services/gemini_service.py`)**
- Updated to use the correct API: `import google.generativeai as genai`
- Changed model to `gemini-2.5-flash` (which supports image analysis)
- Fixed configuration: `genai.configure(api_key=Config.GEMINI_API_KEY)`
- Improved prompt for better JSON extraction
- Added image download and processing with PIL

### 3. **Environment Configuration**
Your `.env` file should have the following format:
```env
GEMINI_API_KEY="your-api-key-here"
```
**Note:** Replace `your-api-key-here` with your actual API key from Google AI Studio.

## 🚀 How to Use

### Testing the API Connection
```bash
cd portfolio-ai-app/backend-api
python test_gemini.py
```
This will verify your API key is working and list available models.

### Testing Receipt OCR
1. Get a receipt image URL (must be publicly accessible)
2. Edit `test_receipt_ocr.py` and add your image URL
3. Run:
```bash
python test_receipt_ocr.py
```

### Using the API Endpoint

**1. Start the Flask server:**
```bash
python run.py
```

**2. Register/Login to get a JWT token:**
```bash
# Register
POST http://localhost:5000/api/auth/register
Body: {"username": "testuser", "password": "password123", "email": "test@example.com"}

# Login
POST http://localhost:5000/api/auth/login
Body: {"username": "testuser", "password": "password123"}
```

**3. Upload receipt for OCR:**
```bash
POST http://localhost:5000/api/receipts/upload
Headers: 
  Authorization: Bearer YOUR_JWT_TOKEN
  Content-Type: application/json
Body: 
  {"image_url": "https://your-receipt-image-url.com/receipt.jpg"}
```

## 📝 What the OCR Extracts

The Gemini API will extract the following information from your receipt:
- `vendor_name` - Store/business name
- `receipt_number` - Transaction/invoice number
- `total_amount` - Final amount (number only)
- `currency` - Currency code (USD, EUR, etc.)
- `transaction_date` - Date in YYYY-MM-DD format

## ⚠️ Important Notes

1. **Image URL Requirements:**
   - Must be publicly accessible (no authentication required)
   - Supported formats: JPEG, PNG
   - Clear, readable receipt images work best

2. **API Key Security:**
   - Never commit your `.env` file to git (it's already in `.gitignore`)
   - Keep your API key private
   - Regenerate it from Google AI Studio if exposed

3. **Model Used:**
   - Currently using `gemini-2.5-flash` which is fast and cost-effective
   - Supports vision/image analysis
   - Other available models: `gemini-2.5-pro` (more accurate but slower)

## 🔧 Troubleshooting

### "Image URL not accessible"
- Make sure the URL is publicly accessible
- Try opening it in an incognito browser window
- Check if it requires authentication

### "Failed to extract data"
- Ensure the receipt image is clear and readable
- Try a different image
- Check the console logs for detailed error messages

### "API Key Error"
- Verify your API key in `.env` is correct
- Check if you have API quota remaining in Google AI Studio
- Regenerate the API key if needed

## 📚 File Structure

```
backend-api/
├── .env                              # Your API keys and config
├── config.py                         # Loads environment variables
├── app/
│   └── services/
│       └── gemini_service.py         # Gemini OCR logic
│   └── receipts/
│       └── routes.py                 # Receipt upload endpoint
├── test_gemini.py                    # Test API connection
└── test_receipt_ocr.py               # Test receipt extraction
```

## 🎯 Next Steps

1. Test the connection: `python test_gemini.py` ✅
2. Get a sample receipt image URL
3. Test OCR: Edit and run `test_receipt_ocr.py`
4. Integrate with your frontend application

Your Gemini API is now ready to use for optical receipt scanning! 🎉
