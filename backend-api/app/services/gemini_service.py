# app/services/gemini_service.py

import os
import json
from google import genai
from google.genai import types
from config import Config

# Initialize the Gemini Client using the key from config.py (.env file)
client = genai.Client(api_key=Config.GEMINI_API_KEY)

# Define the exact structured output we want from the model (using a Pydantic-like structure)
# This is crucial for reliable data extraction.
EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "vendor_name": {"type": "string", "description": "The name of the store or vendor."},
        "receipt_number": {"type": "string", "description": "The unique transaction number, often labeled INV or TNX."},
        "total_amount": {"type": "number", "description": "The final total amount paid."},
        "currency": {"type": "string", "description": "The currency of the transaction (e.g., USD, EUR)."},
        "transaction_date": {"type": "string", "format": "date", "description": "The date of the transaction in YYYY-MM-DD format."},
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
        # Load the image from the URL (Gemini can process images directly from URLs)
        image_part = types.Part.from_uri(uri=image_url, mime_type="image/jpeg")

        # Define the prompt
        prompt = (
            "You are an expert financial data extraction system. Extract the requested fields "
            "from the provided receipt image. Ensure the output strictly follows the JSON schema. "
            "If a field is not found, omit it unless it is required."
        )

        # Configure the model for structured JSON output
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=EXTRACTION_SCHEMA,
        )

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, image_part],
            config=config,
        )

        # Parse the JSON string result
        return json.loads(response.text)

    except Exception as e:
        print(f"Gemini API Error: {e}")
        return None