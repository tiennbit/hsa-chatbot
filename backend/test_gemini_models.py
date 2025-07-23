#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Gemini Models
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai

def test_gemini_models():
    """Test different Gemini models"""
    print("Testing Gemini Models...")
    
    # Configure Gemini
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found")
        return
    
    genai.configure(api_key=api_key)
    
    # List available models
    try:
        models = genai.list_models()
        print("Available models:")
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                print(f"  - {model.name}")
    except Exception as e:
        print(f"Error listing models: {e}")
    
    # Test different models
    test_models = [
        'gemini-1.5-pro',
        'gemini-1.5-flash',
        'gemini-pro',
        'gemini-1.0-pro'
    ]
    
    test_prompt = "Xin chào, hãy trả lời ngắn gọn bằng tiếng Việt: HSA là gì?"
    
    for model_name in test_models:
        print(f"\nTesting model: {model_name}")
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(test_prompt)
            print(f"  ✅ Success: {response.text[:100]}...")
        except Exception as e:
            print(f"  ❌ Error: {e}")

if __name__ == '__main__':
    test_gemini_models() 