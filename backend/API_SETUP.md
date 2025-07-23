# Hướng dẫn thiết lập API Keys cho HSA Chatbot

## Tổng quan
HSA Chatbot hỗ trợ 3 LLM providers chính:
- **Google Gemini** (Khuyến nghị)
- **DeepSeek**
- **OpenAI**

## Bước 1: Tạo file .env
Tạo file `.env` trong thư mục `backend` với nội dung sau:

```env
# HSA Chatbot Environment Variables

# Database
DATABASE_URL=sqlite:///hsa_chatbot.db

# Secret Key
SECRET_KEY=hsa-chatbot-secret-key-2024

# Admin Account
ADMIN_USERNAME=admin
ADMIN_PASSWORD=hsa_admin_2024
ADMIN_EMAIL=admin@hsa.edu.vn

# LLM Providers
DEFAULT_LLM_PROVIDER=gemini

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Google Gemini
GEMINI_API_KEY=your_gemini_api_key_here

# DeepSeek
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# ChromaDB
CHROMA_PERSIST_DIRECTORY=./chroma_db

# Response Settings
RESPONSE_MAX_TOKENS=1000
TEMPERATURE=0.7

# App Settings
APP_NAME=HSA Chatbot
MAX_CONTENT_LENGTH=52428800
```

## Bước 2: Lấy API Keys

### Google Gemini (Khuyến nghị)
1. Truy cập [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Đăng nhập bằng tài khoản Google
3. Tạo API key mới
4. Copy API key và thay thế `your_gemini_api_key_here` trong file `.env`

### DeepSeek
1. Truy cập [DeepSeek Console](https://platform.deepseek.com/)
2. Đăng ký tài khoản
3. Tạo API key mới
4. Copy API key và thay thế `your_deepseek_api_key_here` trong file `.env`

### OpenAI
1. Truy cập [OpenAI Platform](https://platform.openai.com/api-keys)
2. Đăng nhập hoặc đăng ký tài khoản
3. Tạo API key mới
4. Copy API key và thay thế `your_openai_api_key_here` trong file `.env`

## Bước 3: Kiểm tra kết nối
Chạy script test để kiểm tra kết nối:

```bash
cd backend
python test_api_connection.py
```

## Bước 4: Khởi động ứng dụng
```bash
cd backend
python main.py
```

## Lưu ý quan trọng

### Fallback Mode
- Nếu không có API keys, chatbot sẽ hoạt động ở chế độ fallback
- Fallback mode sử dụng keyword-based responses
- Vẫn có thể trả lời các câu hỏi cơ bản về HSA

### Bảo mật
- Không commit file `.env` lên git
- File `.env` đã được thêm vào `.gitignore`
- Bảo vệ API keys của bạn

### Chi phí
- **Google Gemini**: Miễn phí với quota hàng tháng
- **DeepSeek**: Có gói miễn phí và trả phí
- **OpenAI**: Trả phí theo usage

## Troubleshooting

### Lỗi "API key not found"
- Kiểm tra file `.env` có tồn tại không
- Kiểm tra tên biến môi trường có đúng không
- Restart ứng dụng sau khi thêm API keys

### Lỗi "Provider not available"
- Kiểm tra API key có hợp lệ không
- Kiểm tra kết nối internet
- Thử provider khác

### Lỗi "Rate limit exceeded"
- Đợi một lúc rồi thử lại
- Kiểm tra quota của API provider
- Cân nhắc nâng cấp gói dịch vụ 