# Hướng dẫn Triển khai HSA Chatbot

## 🎯 Tổng quan

HSA Chatbot là hệ thống chatbot AI hoàn chỉnh được thiết kế đặc biệt cho thí sinh tham dự kỳ thi HSA của Đại học Quốc gia Hà Nội. Hệ thống bao gồm:

### ✅ Tính năng đã hoàn thành
- **RAG (Retrieval-Augmented Generation)**: Trả lời dựa trên tài liệu thực tế
- **Multi-LLM Support**: Hỗ trợ Gemini, DeepSeek, OpenAI
- **Admin Panel**: Quản lý người dùng, tài liệu, cuộc trò chuyện
- **User Management**: Đăng ký, đăng nhập, phân quyền
- **Document Processing**: Upload và xử lý PDF, DOCX, TXT, PPTX, XLSX
- **Docker Deployment**: Triển khai dễ dàng với container
- **Dashboard Analytics**: Thống kê và báo cáo chi tiết

## 🚀 Triển khai nhanh (5 phút)

### Bước 1: Chuẩn bị
```bash
# Clone source code (hoặc copy thư mục hsa_chatbot)
cd hsa_chatbot

# Chạy script setup tự động
./setup.sh
```

### Bước 2: Cấu hình API Keys
Chỉnh sửa file `.env`:
```env
# Gemini API (Khuyến nghị - Free tier tốt)
GEMINI_API_KEY=AIzaSyCIdCsEn6p24UgiDHkC-PY4ero_sWUohOY

# DeepSeek API (Tùy chọn)
DEEPSEEK_API_KEY=your-deepseek-api-key

# OpenAI API (Tùy chọn)
OPENAI_API_KEY=your-openai-api-key

# Chọn provider mặc định
DEFAULT_LLM_PROVIDER=gemini
```

### Bước 3: Khởi chạy
```bash
docker-compose up -d
```

### Bước 4: Truy cập
- **Chatbot**: http://localhost:5000
- **Admin Panel**: http://localhost:5000/admin
- **Login**: admin / hsa_admin_2024

## 📋 Cấu hình chi tiết

### API Keys Setup

#### 1. Google Gemini (Khuyến nghị)
- **Free tier**: 15 requests/minute, 1 million tokens/month
- **Đăng ký**: https://makersuite.google.com/app/apikey
- **Ưu điểm**: Free tier tốt, chất lượng cao, hỗ trợ tiếng Việt

#### 2. DeepSeek (Tùy chọn)
- **Giá rẻ**: $0.14/1M input tokens, $0.28/1M output tokens
- **Đăng ký**: https://platform.deepseek.com/
- **Ưu điểm**: Giá rẻ, hiệu suất tốt

#### 3. OpenAI (Tùy chọn)
- **Đăng ký**: https://platform.openai.com/api-keys
- **Lưu ý**: Cần thanh toán, đắt hơn

### Cấu hình Admin

#### Thay đổi thông tin admin
```env
ADMIN_USERNAME=your_admin
ADMIN_PASSWORD=your_secure_password
ADMIN_EMAIL=admin@yourdomain.com
```

#### Cấu hình bảo mật
```env
SECRET_KEY=your-very-secure-secret-key-here
```

## 📚 Upload tài liệu HSA

### Bước 1: Chuẩn bị tài liệu
- **Định dạng hỗ trợ**: PDF, DOCX, TXT, PPTX, XLSX
- **Nội dung**: Thông tin về HSA, quy trình thi, tuyển sinh
- **Kích thước**: Tối đa 50MB/file

### Bước 2: Upload qua Admin Panel
1. Đăng nhập Admin Panel
2. Vào **Documents > Upload Document**
3. Chọn file và điền thông tin:
   - **Title**: Tên tài liệu
   - **Category**: hsa_info, exam_guide, faq, study_material
   - **Description**: Mô tả ngắn
   - **Tags**: hsa, tuyển sinh, đại học quốc gia

### Bước 3: Kiểm tra xử lý
- Hệ thống tự động trích xuất text
- Tạo embeddings cho tìm kiếm
- Trạng thái: uploaded → processing → processed

## 🎨 Tùy chỉnh giao diện

### Thay đổi màu sắc HSA
Chỉnh sửa `backend/templates/base.html`:
```css
:root {
    --hsa-primary: #1e40af;    /* Màu chính HSA */
    --hsa-secondary: #3b82f6;  /* Màu phụ */
    --hsa-success: #10b981;    /* Màu thành công */
}
```

### Thay đổi logo và thông tin
```html
<a class="navbar-brand" href="{{ url_for('index') }}">
    <img src="/static/img/hsa-logo.png" alt="HSA" height="30">
    HSA Chatbot
</a>
```

### Tùy chỉnh footer
```html
<div class="col-md-6">
    <h5>Liên hệ</h5>
    <p>
        <i class="fas fa-envelope me-2"></i>hsa@vnu.edu.vn<br>
        <i class="fas fa-phone me-2"></i>(024) 3754 7506<br>
        <i class="fas fa-map-marker-alt me-2"></i>144 Xuân Thủy, Cầu Giấy, Hà Nội
    </p>
</div>
```

## 🔧 Tùy chỉnh Chatbot

### Thay đổi system prompt
Chỉnh sửa `backend/utils/rag_processor.py`:
```python
system_prompt = """Bạn là trợ lý AI chính thức của Đại học Quốc gia Hà Nội, 
chuyên hỗ trợ thí sinh về kỳ thi HSA.

Nhiệm vụ:
- Trả lời về HSA, quy trình đăng ký, nội dung thi, điểm số
- Hướng dẫn tuyển sinh các trường thành viên
- Cung cấp thông tin chính xác từ tài liệu chính thức
- Sử dụng ngôn ngữ thân thiện, chuyên nghiệp

Lưu ý:
- Chỉ trả lời dựa trên tài liệu được cung cấp
- Nếu không biết, hướng dẫn liên hệ hotline: (024) 3754 7506
"""
```

### Thêm câu hỏi gợi ý
```python
suggested_questions = [
    "HSA là gì?",
    "Cách đăng ký thi HSA?",
    "Nội dung thi HSA gồm những gì?",
    "Điểm HSA được tính như thế nào?",
    "Các trường nào nhận điểm HSA?",
    "Lệ phí thi HSA bao nhiêu?",
    "Khi nào có kết quả thi HSA?",
    "Làm thế nào để phúc khảo điểm HSA?"
]
```

## 🚀 Triển khai Production

### 1. Cấu hình Domain và SSL

#### Nginx Configuration
Tạo file `nginx/nginx.conf`:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    location / {
        proxy_pass http://hsa-chatbot:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Khởi chạy với SSL
```bash
docker-compose --profile production up -d
```

### 2. Backup và Monitoring

#### Backup tự động
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec hsa-chatbot cp /app/hsa_chatbot.db /app/data/backup_$DATE.db
docker-compose exec hsa-chatbot tar -czf /app/data/chroma_backup_$DATE.tar.gz /app/chroma_db
```

#### Monitoring
```bash
# Health check
curl -f http://localhost:5000/health

# View logs
docker-compose logs -f hsa-chatbot

# Resource usage
docker stats hsa-chatbot
```

### 3. Scaling

#### Horizontal scaling
```yaml
# docker-compose.prod.yml
services:
  hsa-chatbot:
    deploy:
      replicas: 3
    
  nginx:
    depends_on:
      - hsa-chatbot
```

#### Load balancer
```nginx
upstream hsa_backend {
    server hsa-chatbot-1:5000;
    server hsa-chatbot-2:5000;
    server hsa-chatbot-3:5000;
}
```

## 📊 Analytics và Reporting

### Dashboard Metrics
- **Users**: Tổng số người dùng, người dùng mới
- **Sessions**: Số phiên trò chuyện, thời gian trung bình
- **Messages**: Tổng tin nhắn, tin nhắn/ngày
- **Documents**: Tài liệu đã xử lý, lỗi xử lý
- **Performance**: Thời gian phản hồi, độ chính xác

### Export Reports
```python
# Xuất báo cáo CSV
@admin_bp.route('/export/users')
def export_users():
    users = User.query.all()
    # Generate CSV...
```

## 🔒 Bảo mật Production

### 1. Environment Variables
```env
# Production settings
FLASK_ENV=production
SECRET_KEY=your-super-secure-key-256-bits
ADMIN_PASSWORD=very-secure-admin-password

# Database encryption
DATABASE_ENCRYPTION_KEY=your-db-encryption-key

# Rate limiting
RATE_LIMIT_PER_MINUTE=60
```

### 2. Security Headers
```python
# app.py
from flask_talisman import Talisman

Talisman(app, force_https=True)
```

### 3. Input Validation
```python
# Validate file uploads
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'pptx', 'xlsx'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
```

## 🆘 Troubleshooting

### Lỗi thường gặp

#### 1. Container không khởi động
```bash
# Check logs
docker-compose logs hsa-chatbot

# Common issues:
# - Missing .env file
# - Invalid API keys
# - Port conflicts
```

#### 2. API không hoạt động
```bash
# Test API endpoints
curl http://localhost:5000/health
curl http://localhost:5000/api/chat -X POST -H "Content-Type: application/json" -d '{"message":"test"}'
```

#### 3. Database issues
```bash
# Reset database
docker-compose down
docker volume rm hsa_chatbot_data
docker-compose up -d
```

#### 4. Vector database issues
```bash
# Reset ChromaDB
rm -rf chroma_db/*
# Re-upload documents via admin panel
```

### Performance Tuning

#### 1. Memory optimization
```yaml
# docker-compose.yml
services:
  hsa-chatbot:
    mem_limit: 4g
    memswap_limit: 4g
```

#### 2. CPU optimization
```python
# utils/rag_processor.py
# Use smaller embedding model for faster processing
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # Faster
# EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"  # Better quality
```

## 📞 Hỗ trợ

### Liên hệ
- **Email**: support@hsa-chatbot.com
- **GitHub Issues**: [Repository Issues]
- **Documentation**: Xem thêm trong thư mục `docs/`

### Community
- **Discord**: [HSA Chatbot Community]
- **Forum**: [HSA Chatbot Forum]

---

**Chúc bạn triển khai thành công HSA Chatbot! 🎉**

