#!/usr/bin/env python3
"""
Simple test script to verify Gemini API key is working
"""

import google.generativeai as genai
from config import Config

def test_gemini_connection():
    """Test if the Gemini API key is valid and working"""
    try:
        # Configure the API
        genai.configure(api_key=Config.GEMINI_API_KEY)
        
        # List available models
        print("\nAvailable models:")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"  - {m.name}")
        
        # Try a simple text generation
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content("Say 'Hello from Gemini!'")
        
        print("✓ Gemini API is working!")
        print(f"Response: {response.text}")
        return True
        
    except Exception as e:
        print(f"✗ Gemini API Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing Gemini API connection...")
    print(f"API Key configured: {'Yes' if Config.GEMINI_API_KEY else 'No'}")
    print(f"API Key (first 10 chars): {Config.GEMINI_API_KEY[:10]}...")
    print()
    test_gemini_connection()
