#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test API Connection
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from utils.rag_processor import RAGProcessor

def test_api_connection():
    """Test API connection with LLM providers"""
    print("Testing API connections...")
    
    # Check environment variables
    print("\n1. Checking environment variables:")
    providers = {
        'OpenAI': os.getenv('OPENAI_API_KEY'),
        'Google Gemini': os.getenv('GEMINI_API_KEY'),
        'DeepSeek': os.getenv('DEEPSEEK_API_KEY')
    }
    
    for provider, key in providers.items():
        if key and key != 'your_api_key_here':
            print(f"  ✅ {provider}: API key found")
        else:
            print(f"  ❌ {provider}: API key not found or not set")
    
    # Test RAG Processor initialization
    print("\n2. Testing RAG Processor initialization:")
    try:
        rag = RAGProcessor()
        print("  ✅ RAG Processor initialized successfully")
        
        # Check available providers
        print(f"  Available LLM providers: {list(rag.llm_providers.keys())}")
        
        if not rag.llm_providers:
            print("  ⚠️  No LLM providers available. Please set API keys in .env file")
            return
        
        # Test simple query
        print("\n3. Testing simple query:")
        test_query = "Xin chào, bạn có thể giúp tôi hiểu về kỳ thi HSA không?"
        
        try:
            response = rag.process_query(test_query)
            print(f"  ✅ Query processed successfully")
            print(f"  Response: {response[:200]}...")
        except Exception as e:
            print(f"  ❌ Error processing query: {e}")
        
    except Exception as e:
        print(f"  ❌ Error initializing RAG Processor: {e}")

def test_individual_providers():
    """Test individual LLM providers"""
    print("\n4. Testing individual providers:")
    
    # Test Gemini
    if os.getenv('GEMINI_API_KEY') and os.getenv('GEMINI_API_KEY') != 'your_gemini_api_key_here':
        try:
            import google.generativeai as genai
            genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content("Xin chào, hãy trả lời ngắn gọn bằng tiếng Việt.")
            print("  ✅ Google Gemini: Connected successfully")
        except Exception as e:
            print(f"  ❌ Google Gemini: {e}")
    else:
        print("  ⚠️  Google Gemini: API key not set")
    
    # Test DeepSeek
    if os.getenv('DEEPSEEK_API_KEY') and os.getenv('DEEPSEEK_API_KEY') != 'your_deepseek_api_key_here':
        try:
            import requests
            url = "https://api.deepseek.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": "Xin chào, hãy trả lời ngắn gọn bằng tiếng Việt."}],
                "max_tokens": 100
            }
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                print("  ✅ DeepSeek: Connected successfully")
            else:
                print(f"  ❌ DeepSeek: HTTP {response.status_code}")
        except Exception as e:
            print(f"  ❌ DeepSeek: {e}")
    else:
        print("  ⚠️  DeepSeek: API key not set")

if __name__ == '__main__':
    test_api_connection()
    test_individual_providers()
    
    print("\n" + "="*50)
    print("SUMMARY:")
    print("To fix API connection issues:")
    print("1. Create a .env file in the backend directory")
    print("2. Add your API keys:")
    print("   GEMINI_API_KEY=your_actual_gemini_key")
    print("   DEEPSEEK_API_KEY=your_actual_deepseek_key")
    print("   OPENAI_API_KEY=your_actual_openai_key")
    print("3. Restart the application") 