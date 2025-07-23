#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Sample Document
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
from datetime import datetime

def test_sample_document():
    """Test with sample document"""
    print("Testing Sample Document...")
    
    with app.app_context():
        try:
            # Initialize RAG processor
            rag = RAGProcessor()
            print("✅ RAG Processor initialized")
            
            # Sample document path
            sample_file = "test_sample_document.txt"
            print(f"📄 Sample file: {sample_file}")
            
            if not os.path.exists(sample_file):
                print("❌ Sample file not found")
                return
            
            # Create document record
            document = Document(
                filename=sample_file,
                original_filename=sample_file,
                file_path=os.path.abspath(sample_file),
                file_size=os.path.getsize(sample_file),
                file_type='txt',
                title='Quy chế thi HSA 2025',
                description='Tài liệu mẫu về quy chế thi HSA',
                category='hsa_info',
                tags='hsa,quy chế,thi cử',
                is_public=True,
                uploaded_by=1,  # admin user
                status='uploaded'
            )
            
            db.session.add(document)
            db.session.commit()
            print(f"✅ Document created with ID: {document.id}")
            
            # Process document
            print("\n🔄 Processing document...")
            result = rag.process_document(
                document_id=document.id,
                file_path=document.file_path,
                file_type=document.file_type,
                title=document.title,
                category=document.category
            )
            
            if result["success"]:
                print(f"✅ Document processed successfully")
                print(f"📊 Chunks: {result['chunk_count']}")
                print(f"⏱️  Time: {result['processing_time']:.2f}s")
                
                # Update document status
                document.status = 'processed'
                document.chunk_count = result['chunk_count']
                document.vector_ids = ','.join(result['vector_ids'])
                document.processed_at = datetime.utcnow()
                db.session.commit()
                
                # Test search
                print("\n🔍 Testing search...")
                search_queries = [
                    "HSA là gì?",
                    "Thời gian thi HSA khi nào?",
                    "Cách đăng ký thi HSA?",
                    "Cấu trúc bài thi HSA?",
                    "Điểm thi HSA được tính như thế nào?"
                ]
                
                for query in search_queries:
                    print(f"\nQ: {query}")
                    try:
                        response = rag.process_query(query)
                        print(f"A: {response[:200]}...")
                    except Exception as e:
                        print(f"❌ Error: {e}")
                
            else:
                print(f"❌ Processing failed: {result['error']}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_sample_document() 