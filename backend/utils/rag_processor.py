#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG Processor - Xử lý Retrieval-Augmented Generation
"""

import os
import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

# Document processing
import PyPDF2
from docx import Document as DocxDocument
import pandas as pd
from pptx import Presentation

# AI and embeddings
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# LLM providers
import openai
import google.generativeai as genai
import requests

class RAGProcessor:
    """Xử lý RAG cho chatbot HSA"""
    
    def __init__(self):
        self.embedding_model = None
        self.chroma_client = None
        self.collection = None
        self.llm_providers = {}
        self.initialize()
    
    def initialize(self):
        """Khởi tạo các thành phần RAG"""
        try:
            # Initialize embedding model
            model_name = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
            self.embedding_model_name = model_name
            
            if model_name.startswith('sentence-transformers/'):
                # Local sentence-transformers model
                self.embedding_model = SentenceTransformer(model_name)
                self.embedding_type = 'local'
            elif model_name == 'gemini-embedding-001':
                # Gemini embedding API
                if not os.getenv('GEMINI_API_KEY'):
                    raise ValueError("GEMINI_API_KEY required for Gemini embedding")
                genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
                self.embedding_model = None
                self.embedding_type = 'gemini'
            elif model_name == 'text-embedding-ada-002':
                # OpenAI embedding API
                if not os.getenv('OPENAI_API_KEY'):
                    raise ValueError("OPENAI_API_KEY required for OpenAI embedding")
                openai.api_key = os.getenv('OPENAI_API_KEY')
                self.embedding_model = None
                self.embedding_type = 'openai'
            else:
                # Fallback to local model
                self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
                self.embedding_type = 'local'
            
            # Initialize ChromaDB
            persist_dir = os.getenv('CHROMA_PERSIST_DIRECTORY', './chroma_db')
            self.chroma_client = chromadb.PersistentClient(path=persist_dir)
            
            # Get or create collection
            try:
                self.collection = self.chroma_client.get_collection("hsa_documents")
            except:
                self.collection = self.chroma_client.create_collection(
                    name="hsa_documents",
                    metadata={"description": "HSA Chatbot Documents"}
                )
            
            # Initialize LLM providers
            self._initialize_llm_providers()
            
            print(f"RAG Processor initialized successfully with {self.embedding_type} embedding")
            
        except Exception as e:
            print(f"Error initializing RAG Processor: {e}")
            raise
    
    def _initialize_llm_providers(self):
        """Khởi tạo các LLM providers"""
        # OpenAI
        if os.getenv('OPENAI_API_KEY'):
            openai.api_key = os.getenv('OPENAI_API_KEY')
            self.llm_providers['openai'] = True
        
        # Google Gemini
        if os.getenv('GEMINI_API_KEY'):
            genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
            self.llm_providers['gemini'] = True
        
        # DeepSeek
        if os.getenv('DEEPSEEK_API_KEY'):
            self.llm_providers['deepseek'] = True
    
    def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Tạo embeddings cho danh sách text"""
        try:
            if self.embedding_type == 'local':
                # Local sentence-transformers
                return self.embedding_model.encode(texts).tolist()
            
            elif self.embedding_type == 'gemini':
                # Gemini embedding API using HTTP requests
                embeddings = []
                api_key = os.getenv('GEMINI_API_KEY')
                url = "https://generativelanguage.googleapis.com/v1beta/models/embedding-001:embedContent"
                
                for text in texts:
                    try:
                        headers = {
                            "Content-Type": "application/json",
                        }
                        
                        data = {
                            "model": "models/embedding-001",
                            "content": {
                                "parts": [
                                    {
                                        "text": text
                                    }
                                ]
                            }
                        }
                        
                        # Add API key to URL
                        full_url = f"{url}?key={api_key}"
                        
                        response = requests.post(full_url, headers=headers, json=data)
                        response.raise_for_status()
                        
                        result = response.json()
                        embedding = result["embedding"]["values"]
                        embeddings.append(embedding)
                        
                    except Exception as e:
                        print(f"Error with Gemini embedding: {e}")
                        # Fallback to local model
                        fallback_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
                        embeddings.append(fallback_model.encode([text]).tolist()[0])
                return embeddings
            
            elif self.embedding_type == 'openai':
                # OpenAI embedding API
                embeddings = []
                for text in texts:
                    try:
                        response = openai.Embedding.create(
                            input=text,
                            model="text-embedding-ada-002"
                        )
                        embeddings.append(response['data'][0]['embedding'])
                    except Exception as e:
                        print(f"Error with OpenAI embedding: {e}")
                        # Fallback to local model
                        fallback_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
                        embeddings.append(fallback_model.encode([text]).tolist()[0])
                return embeddings
            
            else:
                # Fallback to local model
                fallback_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
                return fallback_model.encode(texts).tolist()
                
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            # Final fallback
            fallback_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            return fallback_model.encode(texts).tolist()
    
    def extract_text_from_file(self, file_path: str, file_type: str) -> str:
        """Trích xuất text từ file"""
        try:
            if file_type.lower() == 'pdf':
                return self._extract_from_pdf(file_path)
            elif file_type.lower() == 'docx':
                return self._extract_from_docx(file_path)
            elif file_type.lower() == 'txt':
                return self._extract_from_txt(file_path)
            elif file_type.lower() == 'pptx':
                return self._extract_from_pptx(file_path)
            elif file_type.lower() in ['xlsx', 'csv']:
                return self._extract_from_excel(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        
        except Exception as e:
            print(f"Error extracting text from {file_path}: {e}")
            raise
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Trích xuất text từ PDF"""
        try:
            import pdfplumber
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except Exception as e:
            print(f"pdfplumber failed: {e}")
            # Fallback to PyPDF2
            try:
                text = ""
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                return text
            except Exception as e2:
                print(f"PyPDF2 also failed: {e2}")
                return ""
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Trích xuất text từ DOCX"""
        doc = DocxDocument(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    
    def _extract_from_txt(self, file_path: str) -> str:
        """Trích xuất text từ TXT"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def _extract_from_pptx(self, file_path: str) -> str:
        """Trích xuất text từ PPTX"""
        prs = Presentation(file_path)
        text = ""
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text += shape.text + "\n"
        return text
    
    def _extract_from_excel(self, file_path: str) -> str:
        """Trích xuất text từ Excel/CSV"""
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        # Convert dataframe to text
        text = df.to_string(index=False)
        return text
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Chia text thành các chunks"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                for i in range(end, max(start + chunk_size - 200, start), -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks
    
    def process_document(self, document_id: int, file_path: str, file_type: str, 
                        title: str = None, category: str = None) -> Dict[str, Any]:
        """Xử lý tài liệu và lưu vào vector database"""
        try:
            start_time = time.time()
            
            # Extract text
            text = self.extract_text_from_file(file_path, file_type)
            
            if not text.strip():
                raise ValueError("No text extracted from document")
            
            # Chunk text
            chunks = self.chunk_text(text)
            
            # Generate embeddings
            embeddings = self._generate_embeddings(chunks)
            
            # Prepare metadata
            vector_ids = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                vector_id = f"doc_{document_id}_chunk_{i}"
                vector_ids.append(vector_id)
                
                metadata = {
                    "document_id": document_id,
                    "chunk_index": i,
                    "title": title or f"Document {document_id}",
                    "category": category or "general",
                    "file_type": file_type,
                    "created_at": datetime.utcnow().isoformat()
                }
                
                # Add to ChromaDB
                self.collection.add(
                    ids=[vector_id],
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[metadata]
                )
            
            processing_time = time.time() - start_time
            
            return {
                "success": True,
                "vector_ids": vector_ids,
                "chunk_count": len(chunks),
                "processing_time": processing_time,
                "text_length": len(text)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "processing_time": time.time() - start_time if 'start_time' in locals() else 0
            }
    
    def search_documents(self, query: str, n_results: int = 5, 
                        category_filter: str = None) -> List[Dict[str, Any]]:
        """Tìm kiếm tài liệu liên quan"""
        try:
            # Generate query embedding
            query_embedding = self._generate_embeddings([query])[0]
            
            # Prepare where clause for filtering
            where_clause = {}
            if category_filter:
                where_clause["category"] = category_filter
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_clause if where_clause else None
            )
            
            # Format results
            search_results = []
            for i in range(len(results['ids'][0])):
                result = {
                    "id": results['ids'][0][i],
                    "document": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if 'distances' in results else None
                }
                search_results.append(result)
            
            return search_results
            
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    def generate_response(self, query: str, context_docs: List[Dict[str, Any]], 
                         provider: str = None, chat_history: List[Dict] = None) -> Dict[str, Any]:
        """Tạo phản hồi từ LLM"""
        try:
            start_time = time.time()
            
            # Use default provider if not specified
            if not provider:
                provider = os.getenv('DEFAULT_LLM_PROVIDER', 'gemini')
            
            # Prepare context
            context = self._prepare_context(context_docs)
            
            # Prepare prompt
            prompt = self._create_prompt(query, context, chat_history)
            
            # Generate response based on provider
            if provider == 'openai' and 'openai' in self.llm_providers:
                response_data = self._generate_openai_response(prompt)
            elif provider == 'gemini' and 'gemini' in self.llm_providers:
                response_data = self._generate_gemini_response(prompt)
            elif provider == 'deepseek' and 'deepseek' in self.llm_providers:
                response_data = self._generate_deepseek_response(prompt)
            else:
                raise ValueError(f"Provider {provider} not available")
            
            processing_time = time.time() - start_time
            
            return {
                "success": True,
                "response": response_data["response"],
                "provider": provider,
                "model": response_data.get("model"),
                "tokens_used": response_data.get("tokens_used"),
                "processing_time": processing_time,
                "sources": [doc["metadata"] for doc in context_docs]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "processing_time": time.time() - start_time if 'start_time' in locals() else 0
            }
    
    def _prepare_context(self, context_docs: List[Dict[str, Any]]) -> str:
        """Chuẩn bị context từ các tài liệu"""
        if not context_docs:
            return ""
        
        context_parts = []
        for i, doc in enumerate(context_docs, 1):
            title = doc["metadata"].get("title", "Tài liệu")
            content = doc["document"]
            context_parts.append(f"[Tài liệu {i}: {title}]\n{content}")
        
        return "\n\n".join(context_parts)
    
    def _create_prompt(self, query: str, context: str, chat_history: List[Dict] = None) -> str:
        """Tạo prompt cho LLM"""
        system_prompt = """Bạn là trợ lý AI hỗ trợ thí sinh tham dự kỳ thi HSA (High School Assessment) của Đại học Quốc gia Hà Nội. 

HSA (High School Assessment) là kỳ thi đánh giá năng lực học sinh THPT của Đại học Quốc gia Hà Nội, được tổ chức để đánh giá năng lực tư duy định lượng, tư duy định tính và khoa học của học sinh.

Nhiệm vụ của bạn:
- Trả lời các câu hỏi về kỳ thi HSA, quy trình đăng ký, nội dung thi, điểm số, tuyển sinh
- Cung cấp thông tin chính xác và hữu ích cho thí sinh
- Sử dụng ngôn ngữ thân thiện, dễ hiểu
- Nếu không có thông tin trong tài liệu, hãy thành thật nói rằng bạn không biết

Hãy trả lời bằng tiếng Việt và dựa trên thông tin trong các tài liệu được cung cấp."""
        
        # Add chat history if available
        history_text = ""
        if chat_history:
            history_parts = []
            for msg in chat_history[-5:]:  # Last 5 messages
                role = "Người dùng" if msg.get("message_type") == "user" else "Trợ lý"
                history_parts.append(f"{role}: {msg.get('content', '')}")
            history_text = f"\n\nLịch sử trò chuyện:\n" + "\n".join(history_parts)
        
        prompt = f"""{system_prompt}

Thông tin từ tài liệu:
{context}
{history_text}

Câu hỏi của thí sinh: {query}

Trả lời:"""
        
        return prompt
    
    def _generate_openai_response(self, prompt: str) -> Dict[str, Any]:
        """Tạo phản hồi từ OpenAI"""
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=int(os.getenv('RESPONSE_MAX_TOKENS', 1000)),
            temperature=float(os.getenv('TEMPERATURE', 0.7))
        )
        
        return {
            "response": response.choices[0].message.content,
            "model": response.model,
            "tokens_used": response.usage.total_tokens
        }
    
    def _generate_gemini_response(self, prompt: str) -> Dict[str, Any]:
        """Tạo phản hồi từ Google Gemini"""
        try:
            # Try gemini-1.5-flash first (faster and more available)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            
            return {
                "response": response.text,
                "model": "gemini-1.5-flash",
                "tokens_used": None  # Gemini doesn't provide token count
            }
        except Exception as e:
            # Fallback to gemini-1.5-pro if flash is not available
            try:
                model = genai.GenerativeModel('gemini-1.5-pro')
                response = model.generate_content(prompt)
                
                return {
                    "response": response.text,
                    "model": "gemini-1.5-pro",
                    "tokens_used": None
                }
            except Exception as e2:
                # Final fallback to fallback response
                raise Exception(f"Gemini API error: {e2}")
    
    def _generate_deepseek_response(self, prompt: str) -> Dict[str, Any]:
        """Tạo phản hồi từ DeepSeek"""
        api_key = os.getenv('DEEPSEEK_API_KEY')
        url = "https://api.deepseek.com/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": int(os.getenv('RESPONSE_MAX_TOKENS', 1000)),
            "temperature": float(os.getenv('TEMPERATURE', 0.7))
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        
        return {
            "response": result["choices"][0]["message"]["content"],
            "model": result["model"],
            "tokens_used": result["usage"]["total_tokens"]
        }
    
    def delete_document_vectors(self, vector_ids: List[str]) -> bool:
        """Xóa vectors của tài liệu"""
        try:
            if vector_ids:
                self.collection.delete(ids=vector_ids)
            return True
        except Exception as e:
            print(f"Error deleting vectors: {e}")
            return False
    
    def process_query(self, query: str, chat_history: List[Dict] = None) -> str:
        """Xử lý câu hỏi và trả về phản hồi"""
        try:
            # Tìm kiếm tài liệu liên quan
            context_docs = self.search_documents(query, n_results=3)

            # Tạo phản hồi
            if context_docs:
                try:
                    # Sử dụng LLM provider mặc định
                    default_provider = os.getenv('DEFAULT_LLM_PROVIDER', 'gemini')
                    response_data = self.generate_response(query, context_docs, provider=default_provider, chat_history=chat_history)
                    
                    # Check if response_data has the expected structure
                    if isinstance(response_data, dict) and "response" in response_data:
                        return response_data["response"]
                    elif isinstance(response_data, str):
                        return response_data
                    else:
                        print(f"Unexpected response format: {response_data}")
                        return self._generate_fallback_response(query, context_docs)
                        
                except Exception as e:
                    print(f"Error generating response with LLM: {e}")
                    # Fallback response based on context
                    return self._generate_fallback_response(query, context_docs)
            else:
                # Không tìm thấy tài liệu liên quan, sử dụng fallback
                return self._generate_fallback_response(query, [])

        except Exception as e:
            print(f"Error processing query: {e}")
            return "Xin lỗi, có lỗi xảy ra khi xử lý câu hỏi của bạn. Vui lòng thử lại sau."
    
    def _generate_fallback_response(self, query: str, context_docs: List[Dict[str, Any]]) -> str:
        """Tạo phản hồi fallback khi không có LLM"""
        # Simple keyword-based response
        query_lower = query.lower()
        
        # Common HSA keywords and responses
        hsa_responses = {
            'hsa': 'HSA (High School Assessment) là kỳ thi đánh giá năng lực học sinh THPT của Đại học Quốc gia Hà Nội.',
            'đăng ký': 'Để đăng ký thi HSA, bạn cần truy cập website chính thức và làm theo hướng dẫn đăng ký.',
            'thời gian': 'Thời gian thi HSA thường được công bố vào đầu năm học. Bạn nên theo dõi thông báo chính thức.',
            'điểm': 'Điểm thi HSA được tính dựa trên các bài thi đánh giá năng lực tư duy định lượng, tư duy định tính và khoa học.',
            'tuyển sinh': 'Kết quả thi HSA được sử dụng trong quy trình tuyển sinh của Đại học Quốc gia Hà Nội.',
            'xin chào': 'Xin chào! Tôi là trợ lý AI hỗ trợ thí sinh tham dự kỳ thi HSA. Bạn có câu hỏi gì về kỳ thi không?',
            'giúp': 'Tôi có thể giúp bạn tìm hiểu về kỳ thi HSA, quy trình đăng ký, nội dung thi và tuyển sinh.',
            'thi': 'Kỳ thi HSA đánh giá năng lực tư duy định lượng, tư duy định tính và khoa học của học sinh THPT.',
            'khó': 'Kỳ thi HSA được thiết kế để đánh giá năng lực tư duy của học sinh. Mức độ khó phụ thuộc vào khả năng của từng thí sinh.',
            'làm thế nào': 'Để tham gia kỳ thi HSA, bạn cần đăng ký trực tuyến, chuẩn bị kiến thức và làm theo hướng dẫn của ban tổ chức.',
            'khi nào': 'Thời gian thi HSA thường được công bố vào đầu năm học. Bạn nên theo dõi thông báo chính thức từ Đại học Quốc gia Hà Nội.',
            'như thế nào': 'Quy trình thi HSA bao gồm đăng ký, làm bài thi đánh giá năng lực và nhận kết quả. Chi tiết cụ thể sẽ được hướng dẫn trong thông báo chính thức.'
        }
        
        # Check for keywords in query
        for keyword, response in hsa_responses.items():
            if keyword in query_lower:
                return response
        
        # If no specific keyword found, provide general response
        if context_docs:
            # Use first document as context
            doc_content = context_docs[0]["document"][:500]  # First 500 chars
            return f"Dựa trên thông tin tài liệu: {doc_content}...\n\nĐây là thông tin cơ bản về câu hỏi của bạn. Để biết thêm chi tiết, vui lòng tham khảo tài liệu chính thức."
        else:
            return "Xin chào! Tôi là trợ lý AI hỗ trợ thí sinh tham dự kỳ thi HSA. Hiện tại tôi chưa có đủ thông tin để trả lời câu hỏi của bạn. Bạn có thể hỏi về kỳ thi HSA, quy trình đăng ký, hoặc nội dung thi."
