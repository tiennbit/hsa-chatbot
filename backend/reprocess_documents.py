#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reprocess Documents
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

def reprocess_documents():
    """Reprocess all documents"""
    print("Reprocessing Documents...")
    
    with app.app_context():
        try:
            # Initialize RAG processor
            rag = RAGProcessor()
            print("✅ RAG Processor initialized")
            
            # Get all documents
            documents = Document.query.all()
            print(f"📄 Found {len(documents)} documents")
            
            for doc in documents:
                print(f"\n🔄 Processing: {doc.original_filename}")
                print(f"   Status: {doc.status}")
                print(f"   File path: {doc.file_path}")
                
                # Check if file exists
                if not os.path.exists(doc.file_path):
                    print(f"   ❌ File not found: {doc.file_path}")
                    continue
                
                try:
                    # Reprocess document
                    result = rag.process_document(
                        document_id=doc.id,
                        file_path=doc.file_path,
                        file_type=doc.file_type,
                        title=doc.title,
                        category=doc.category
                    )
                    
                    if result["success"]:
                        print(f"   ✅ Successfully processed")
                        print(f"   📊 Chunks: {result['chunk_count']}")
                        print(f"   ⏱️  Time: {result['processing_time']:.2f}s")
                        
                        # Update document status
                        doc.status = 'processed'
                        doc.chunk_count = result['chunk_count']
                        doc.vector_ids = ','.join(result['vector_ids'])
                        db.session.commit()
                    else:
                        print(f"   ❌ Processing failed: {result['error']}")
                        doc.status = 'error'
                        doc.error_message = result['error']
                        db.session.commit()
                        
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                    doc.status = 'error'
                    doc.error_message = str(e)
                    db.session.commit()
            
            # Test search after reprocessing
            print("\n🔍 Testing search after reprocessing:")
            try:
                results = rag.search_documents("HSA", n_results=5)
                print(f"  Found {len(results)} documents")
                for i, result in enumerate(results, 1):
                    print(f"    {i}. {result['metadata'].get('title', 'No title')}")
                    print(f"       Distance: {result['distance']:.4f}")
            except Exception as e:
                print(f"  ❌ Search error: {e}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    reprocess_documents() 