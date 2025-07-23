#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Document Processing
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from utils.rag_processor import RAGProcessor
from models.document import Document
from database import db
from main import app

def test_document_processing():
    """Test document processing"""
    print("Testing Document Processing...")
    
    with app.app_context():
        try:
            # Initialize RAG processor
            rag = RAGProcessor()
            print("✅ RAG Processor initialized")
            
            # Check if there are any documents in database
            documents = Document.query.all()
            print(f"📄 Documents in database: {len(documents)}")
            
            for doc in documents:
                print(f"  - {doc.original_filename} (Status: {doc.status})")
            
            # Test document search
            print("\n🔍 Testing document search:")
            try:
                results = rag.search_documents("HSA", n_results=5)
                print(f"  Found {len(results)} documents")
                for i, result in enumerate(results, 1):
                    print(f"    {i}. {result['metadata'].get('title', 'No title')}")
            except Exception as e:
                print(f"  ❌ Search error: {e}")
            
            # Test query processing
            print("\n💬 Testing query processing:")
            test_queries = [
                "HSA là gì?",
                "Làm thế nào để đăng ký thi HSA?",
                "Thời gian thi HSA khi nào?"
            ]
            
            for query in test_queries:
                try:
                    response = rag.process_query(query)
                    print(f"  Q: {query}")
                    print(f"  A: {response[:100]}...")
                except Exception as e:
                    print(f"  ❌ Error processing '{query}': {e}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_document_processing() 