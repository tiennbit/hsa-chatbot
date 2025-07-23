#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Chatbot with Fallback Response
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.rag_processor import RAGProcessor

def test_chatbot():
    """Test chatbot functionality"""
    print("Testing Chatbot with Fallback Response...")
    
    try:
        # Initialize RAG processor
        rag = RAGProcessor()
        print("✅ RAG Processor initialized")
        
        # Test queries
        test_queries = [
            "Xin chào",
            "HSA là gì?",
            "Làm thế nào để đăng ký thi HSA?",
            "Thời gian thi HSA khi nào?",
            "Điểm thi HSA được tính như thế nào?",
            "Tuyển sinh HSA như thế nào?",
            "Bạn có thể giúp tôi không?",
            "Thi HSA có khó không?"
        ]
        
        print("\nTesting responses:")
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Query: {query}")
            try:
                response = rag.process_query(query)
                print(f"   Response: {response}")
            except Exception as e:
                print(f"   Error: {e}")
        
        print("\n✅ Chatbot test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_chatbot() 