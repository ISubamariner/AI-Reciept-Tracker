# app/services/gemini_service.py

import os
import json
import google.generativeai as genai
from config import Config

# Gemini API will be configured when first used (lazy initialization)
_gemini_configured = False

def _ensure_gemini_configured():
    """Configure Gemini API if not already configured"""
    global _gemini_configured
    if not _gemini_configured:
        api_key = Config.GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set in environment variables")
        genai.configure(api_key=api_key)
        _gemini_configured = True

# Define the exact structured output we want from the model
# This is crucial for reliable data extraction.
EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "vendor_name": {"type": "string", "description": "The name of the store or vendor."},
        "receipt_number": {"type": "string", "description": "The unique transaction number, often labeled INV or TNX."},
        "total_amount": {"type": "number", "description": "The final total amount paid."},
        "currency": {"type": "string", "description": "The currency of the transaction (e.g., USD, EUR)."},
        "transaction_date": {"type": "string", "description": "The date of the transaction in YYYY-MM-DD format."},
    },
    "required": ["vendor_name", "total_amount", "transaction_date"],
}

def extract_receipt_data(image_url: str):
    """
    Uses the Gemini API to extract structured data from a receipt image.
    
    Args:
        image_url: The public URL of the receipt image.
        
    Returns:
        A dictionary of structured data or None if extraction fails.
    """
    try:
        # Ensure Gemini is configured before using
        _ensure_gemini_configured()
        # Initialize the model with JSON mode for structured output
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            generation_config={
                "temperature": 0.1,  # Lower temperature for more consistent extraction
            }
        )

        # Define the prompt with clear instructions
        prompt = """
        You are an expert financial data extraction system. Extract the following information from the receipt image:
        
        - vendor_name: The name of the store or vendor
        - receipt_number: The unique transaction number (often labeled as INV, TNX, or Receipt #)
        - total_amount: The final total amount paid (just the number, no currency symbol)
        - currency: The currency of the transaction (e.g., USD, EUR, GBP)
        - transaction_date: The date of the transaction in YYYY-MM-DD format
        
        Return ONLY a valid JSON object with these fields. No additional text, no markdown formatting, just the raw JSON.
        If a field cannot be found, use null for optional fields.
        Ensure vendor_name, total_amount, and transaction_date are always present.
        
        Example format:
        {"vendor_name": "Example Store", "receipt_number": "INV-12345", "total_amount": 45.99, "currency": "USD", "transaction_date": "2024-01-15"}
        """

        # For image URLs, we need to download the image first
        import requests
        from io import BytesIO
        from PIL import Image
        
        # Download the image with proper headers
        print(f"Downloading image from: {image_url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(image_url, headers=headers, timeout=30)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        
        # Generate content with the image
        print("Sending image to Gemini for analysis...")
        response = model.generate_content([prompt, img])
        
        # Extract the text response
        response_text = response.text.strip()
        print(f"Raw response from Gemini: {response_text}")
        
        # Clean up the response if it contains markdown code blocks
        if response_text.startswith("```"):
            # Remove markdown code blocks
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        
        # Parse the JSON string result
        extracted_data = json.loads(response_text)
        print(f"Successfully extracted data: {extracted_data}")
        return extracted_data

    except requests.exceptions.RequestException as e:
        print(f"Image Download Error: {e}")
        import traceback
        traceback.print_exc()
        return {'error': f'Failed to download image: {str(e)}'}
    except json.JSONDecodeError as e:
        print(f"JSON Parsing Error: {e}")
        print(f"Response text was: {response_text if 'response_text' in locals() else 'N/A'}")
        import traceback
        traceback.print_exc()
        return {'error': f'Failed to parse Gemini response: {str(e)}'}
    except Exception as e:
        print(f"Gemini API Error: {e}")
        import traceback
        traceback.print_exc()
        return {'error': f'Gemini API error: {str(e)}'}