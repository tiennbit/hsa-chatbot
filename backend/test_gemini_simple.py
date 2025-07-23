#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Gemini Simple
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai

def test_gemini_simple():
    """Test Gemini with simple query"""
    print("Testing Gemini Simple...")
    
    # Configure Gemini
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found")
        return
    
    genai.configure(api_key=api_key)
    
    # Test with gemini-1.5-flash
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = """Bạn là trợ lý AI hỗ trợ thí sinh tham dự kỳ thi HSA (High School Assessment) của Đại học Quốc gia Hà Nội.

HSA (High School Assessment) là kỳ thi đánh giá năng lực học sinh THPT của Đại học Quốc gia Hà Nội, được tổ chức để đánh giá năng lực tư duy định lượng, tư duy định tính và khoa học của học sinh.

Hãy trả lời ngắn gọn bằng tiếng Việt: HSA là gì?"""
        response = model.generate_content(prompt)
        print(f"✅ Gemini Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_gemini_simple() 