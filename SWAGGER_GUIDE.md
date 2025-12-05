# Swagger API Documentation Guide

## Overview
Your Flask backend now includes **Swagger UI** for interactive API documentation. You can view all available endpoints, test them directly, and check if services are online.

## Quick Access

### Swagger UI (Interactive Documentation)
🌐 **URL**: http://localhost:5000/api/docs/

This provides a beautiful, interactive interface where you can:
- View all API endpoints
- See request/response schemas
- Test endpoints directly in the browser
- Check authentication requirements
- View example requests and responses

### Health Check Endpoint
🏥 **URL**: http://localhost:5000/api/health

Returns:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-05T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "database": "connected",
    "gemini_api": "configured"
  }
}
```

### OpenAPI Specification (JSON)
📄 **URL**: http://localhost:5000/swagger.json

Raw OpenAPI 3.0 specification for API integration tools.

## Available Endpoints

### Authentication
- **POST** `/api/auth/register` - Register new user
- **POST** `/api/auth/login` - User login (returns JWT token)

### Receipts
- **POST** `/api/receipts/upload` - Upload receipt (file or URL) for AI processing
- **GET** `/api/receipts/transactions` - Get user transactions

### Health
- **GET** `/api/health` - API health check

## How to Use Swagger UI

### 1. Access the Interface
Open http://localhost:5000/api/docs/ in your browser

### 2. View Endpoints
- Endpoints are organized by tags (Authentication, Receipts, Health)
- Click on any endpoint to expand details
- View request parameters, body schemas, and response examples

### 3. Test Endpoints (Try it out!)

#### For Public Endpoints (No Auth Required)
1. Click on an endpoint (e.g., `/api/auth/login`)
2. Click **"Try it out"** button
3. Fill in the request body
4. Click **"Execute"**
5. View the response below

#### For Protected Endpoints (Auth Required)
1. First, login to get a JWT token:
   - Go to `/api/auth/login`
   - Try it out with your credentials
   - Copy the `access_token` from the response

2. Authorize Swagger:
   - Click the **"Authorize"** button (🔓 icon at top right)
   - Enter: `Bearer YOUR_TOKEN_HERE`
   - Click "Authorize"
   - Click "Close"

3. Now you can test protected endpoints:
   - Try `/api/receipts/upload`
   - Try `/api/receipts/transactions`

### 4. Upload Receipt Example

To test receipt upload in Swagger:

**Option 1: File Upload**
1. Go to `/api/receipts/upload`
2. Click "Try it out"
3. Click "Choose File" under the `image` parameter
4. Select a receipt image from your computer
5. Click "Execute"

**Option 2: URL Upload**
1. Go to `/api/receipts/upload`
2. Click "Try it out"
3. Select "application/json" from media type dropdown
4. Enter JSON:
   ```json
   {
     "image_url": "https://example.com/receipt.jpg"
   }
   ```
5. Click "Execute"

## Files Added

1. **`swagger.json`** - OpenAPI 3.0 specification
   - Defines all endpoints, schemas, and examples
   - Can be imported into Postman, Insomnia, or other API tools

2. **`test_swagger.py`** - Test script
   - Verifies health endpoint
   - Checks Swagger JSON accessibility
   - Confirms Swagger UI is working

3. **Updated `requirements.txt`**
   - Added `flask-swagger-ui==4.11.1`

4. **Updated `app/__init__.py`**
   - Integrated Swagger UI blueprint
   - Added `/api/docs/` route
   - Added `/swagger.json` route
   - Added `/api/health` endpoint

## Testing

### Run the Test Script
```bash
cd backend-api
python test_swagger.py
```

Expected output:
```
✅ All tests passed!
🎉 Swagger UI is available at: http://localhost:5000/api/docs/
```

### Manual Testing
```bash
# Check health
curl http://localhost:5000/api/health

# Get Swagger spec
curl http://localhost:5000/swagger.json

# Access UI
# Open browser to http://localhost:5000/api/docs/
```

## Benefits

### 1. **Instant Visibility**
- See all available API endpoints at a glance
- Understand request/response formats
- Check which services are online

### 2. **Interactive Testing**
- Test endpoints directly from browser
- No need for Postman or curl commands
- See real-time responses

### 3. **Documentation**
- Self-documenting API
- Always up-to-date with code
- Easy for team members to understand

### 4. **Development Speed**
- Quick endpoint verification
- Easy debugging
- Rapid prototyping

### 5. **Health Monitoring**
- Check if API is online
- Verify database connection
- Confirm Gemini API configuration

## Customization

### Update API Documentation
Edit `swagger.json` to:
- Add new endpoints
- Update descriptions
- Add examples
- Modify schemas

### Change Swagger UI URL
In `app/__init__.py`, modify:
```python
SWAGGER_URL = '/api/docs'  # Change this
```

### Add Custom Swagger Config
In `app/__init__.py`, update:
```python
config={
    'app_name': "Your App Name",
    'docExpansion': 'list',  # or 'none', 'full'
    'defaultModelsExpandDepth': 3
}
```

## Troubleshooting

### Swagger UI Not Loading
- Ensure server is running: `python run.py`
- Check http://localhost:5000/api/health
- Verify flask-swagger-ui is installed: `pip install flask-swagger-ui`

### 404 on /api/docs/
- Note the trailing slash: `/api/docs/` (not `/api/docs`)
- Clear browser cache

### Endpoints Not Showing
- Check `swagger.json` is in backend-api folder
- Verify file has valid JSON syntax
- Restart server

### Authorization Not Working
- Make sure to include "Bearer " prefix
- Check token hasn't expired
- Copy full token from login response

## Next Steps

### Optional Enhancements
1. **Auto-generate from Code**: Use flask-smorest or flask-restx for code-first API docs
2. **Add More Details**: Enhance descriptions in swagger.json
3. **Multiple Environments**: Add production/staging server URLs
4. **Rate Limiting Info**: Document API rate limits
5. **Webhooks**: Document webhook endpoints if any

## Production Considerations

### Security
- In production, consider restricting Swagger UI access
- Add authentication to /api/docs if needed
- Don't expose sensitive internal endpoints

### Performance
- Swagger UI is static after load
- No performance impact on API endpoints
- Can be disabled in production if desired

### Alternative URLs
You can access the API at:
- http://localhost:5000 (local)
- http://127.0.0.1:5000 (local)

---

**Quick Start**: Open http://localhost:5000/api/docs/ to get started! 🚀
