# Image Upload Feature - Quick Guide

## Overview
Your receipt processing app now supports **direct image file uploads** in addition to image URLs. Users can upload receipt images directly from their device for AI processing.

## What Was Changed

### Backend Changes

1. **`gemini_service.py`** - Updated to accept both file uploads and URLs
   - New parameter: `image_file` (optional)
   - Handles file-like objects and bytes
   - Falls back to URL download if no file provided

2. **`config.py`** - Added file upload configuration
   - `MAX_CONTENT_LENGTH`: 16MB max file size
   - `ALLOWED_EXTENSIONS`: png, jpg, jpeg, gif, webp, heic

3. **`receipts/routes.py`** - Updated upload endpoint
   - Detects `multipart/form-data` requests
   - Validates file extensions
   - Processes both file uploads and URL submissions

### Frontend Changes

1. **`ReceiptUploadView.vue`** - Enhanced UI
   - Upload mode toggle (File or URL)
   - File input with preview
   - Image preview before upload
   - Form validation for both modes

2. **`receiptService.js`** - New upload method
   - `uploadReceiptFile()` method for file uploads
   - Uses FormData for multipart requests
   - Maintains backward compatibility with URL uploads

## How to Use

### For Users

1. **File Upload Mode** (Default)
   - Select "📁 Upload File" option
   - Click "Select Receipt Image"
   - Choose image from device (PNG, JPEG, GIF, WebP)
   - Preview appears automatically
   - Click "🤖 Analyze Receipt"

2. **URL Mode**
   - Select "🔗 Image URL" option
   - Paste public image URL
   - Click "🤖 Analyze Receipt"

### For Developers

**Backend API Usage:**

```python
# Upload with file
POST /api/receipts/upload
Content-Type: multipart/form-data
Authorization: Bearer <token>

Body:
- image: <file>

# Upload with URL (still supported)
POST /api/receipts/upload
Content-Type: application/json
Authorization: Bearer <token>

Body:
{
  "image_url": "https://example.com/receipt.jpg"
}
```

**Frontend Service Usage:**

```javascript
// File upload
import { receiptService } from '@/services/receiptService';

const file = event.target.files[0];
const result = await receiptService.uploadReceiptFile(file);

// URL upload (existing)
const result = await receiptService.uploadReceipt(imageUrl);
```

## Testing

### Test File Upload Backend
```bash
cd backend-api
python test_file_upload.py
```

### Test with cURL
```bash
# File upload
curl -X POST http://localhost:5000/api/receipts/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "image=@path/to/receipt.jpg"

# URL upload
curl -X POST http://localhost:5000/api/receipts/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://example.com/receipt.jpg"}'
```

## Technical Details

### Supported File Types
- PNG (.png)
- JPEG (.jpg, .jpeg)
- GIF (.gif)
- WebP (.webp)
- HEIC (.heic)

### File Size Limit
- Maximum: 16MB per file

### Security Features
- File extension validation
- Secure filename processing (Werkzeug)
- Content-type verification
- JWT authentication required
- Role-based access control

### Image Processing
- Images are processed in-memory (not saved to disk by default)
- PIL/Pillow handles format conversion
- Direct streaming to Gemini API

## Benefits

1. **Better User Experience**
   - No need to upload images to external hosting
   - Direct upload from mobile/desktop
   - Instant preview

2. **Privacy & Security**
   - Images processed server-side
   - No third-party hosting required
   - Controlled access with authentication

3. **Reliability**
   - No dependency on external image URLs
   - No CORS or hotlinking issues
   - Better error handling

## Next Steps (Optional Enhancements)

1. **Add Local Storage**
   - Save uploaded images to disk or cloud storage (S3/R2)
   - Generate permanent URLs for receipts

2. **Image Optimization**
   - Compress images before sending to Gemini
   - Auto-rotate based on EXIF data
   - Convert HEIC to JPEG

3. **Batch Upload**
   - Allow multiple receipt uploads
   - Queue processing

4. **Progress Indication**
   - Show upload progress bar
   - Stream processing status

## Troubleshooting

**"File type not allowed" error:**
- Check file extension is in allowed list
- Verify file is an actual image

**"Request Entity Too Large" error:**
- File exceeds 16MB limit
- Compress image before upload

**"No image file provided" error:**
- Ensure form field name is "image"
- Verify Content-Type is multipart/form-data

**Preview not showing:**
- Check browser file reader support
- Verify image format is valid
