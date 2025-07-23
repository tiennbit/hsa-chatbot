# HSA Chatbot

Hệ thống chatbot thông minh sử dụng RAG (Retrieval-Augmented Generation) để trả lời các câu hỏi về HSA (High School Assessment).

## Tính năng

- Chatbot thông minh với khả năng trả lời câu hỏi dựa trên tài liệu
- Hệ thống RAG sử dụng ChromaDB để lưu trữ và tìm kiếm vector
- Giao diện web thân thiện với người dùng
- Hệ thống quản trị với dashboard và analytics
- Hỗ trợ upload và xử lý nhiều định dạng tài liệu (PDF, DOCX)

## Cài đặt

### Yêu cầu hệ thống
- Python 3.8+
- Git

### Cài đặt dependencies
```bash
# Clone repository
git clone <repository-url>
cd hsa_chatbot

# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
```

### Cấu hình
1. Tạo file `.env` trong thư mục gốc
2. Cấu hình các biến môi trường cần thiết

### Chạy ứng dụng
```bash
# Chạy backend
cd backend
python main.py

# Hoặc sử dụng Flask development server
flask run
```

## Cấu trúc dự án

```
hsa_chatbot/
├── backend/                 # Backend Flask application
│   ├── app/                # Application modules
│   │   ├── admin/          # Admin routes
│   │   ├── api/            # API routes
│   │   ├── auth/           # Authentication routes
│   │   └── chat/           # Chat routes
│   ├── models/             # Database models
│   ├── templates/          # HTML templates
│   ├── static/             # Static files
│   └── utils/              # Utility functions
├── data/                   # Data files
├── uploads/                # Uploaded documents
├── docs/                   # Documentation
└── docker/                 # Docker configuration
```

## Sử dụng

1. Truy cập ứng dụng qua trình duyệt web
2. Đăng ký tài khoản hoặc đăng nhập
3. Upload tài liệu cần thiết
4. Bắt đầu chat với chatbot

## Đóng góp

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

