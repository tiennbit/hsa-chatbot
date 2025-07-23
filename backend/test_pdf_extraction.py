#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test PDF Extraction
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.rag_processor import RAGProcessor

def test_pdf_extraction():
    """Test PDF text extraction"""
    print("Testing PDF Extraction...")
    
    # Initialize RAG processor
    rag = RAGProcessor()
    
    # Test file path
    file_path = r"D:\Nextcloud\Data\IDT\2025\source_code\hsa_chatbot\backend\..\uploads\20250722_123706_2025_QUY_CHE_THI_HSA.pdf"
    
    print(f"📄 File path: {file_path}")
    print(f"📄 File exists: {os.path.exists(file_path)}")
    
    if os.path.exists(file_path):
        print(f"📄 File size: {os.path.getsize(file_path)} bytes")
        
        try:
            # Test PDF extraction
            text = rag._extract_from_pdf(file_path)
            print(f"📝 Extracted text length: {len(text)} characters")
            print(f"📝 First 200 characters: {text[:200]}...")
            
            if text.strip():
                print("✅ PDF extraction successful")
                
                # Test chunking
                chunks = rag.chunk_text(text)
                print(f"📊 Number of chunks: {len(chunks)}")
                for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
                    print(f"   Chunk {i+1}: {len(chunk)} characters")
                    print(f"   Preview: {chunk[:100]}...")
            else:
                print("❌ No text extracted from PDF")
                
        except Exception as e:
            print(f"❌ Error extracting PDF: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ File not found")

if __name__ == '__main__':
    test_pdf_extraction() 