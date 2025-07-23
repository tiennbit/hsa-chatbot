#!/bin/bash

# HSA Chatbot Setup Script
echo "🚀 HSA Chatbot Setup Script"
echo "================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env file and add your API keys:"
    echo "   - GEMINI_API_KEY (recommended)"
    echo "   - DEEPSEEK_API_KEY (optional)"
    echo "   - OPENAI_API_KEY (optional)"
    echo ""
    echo "You can edit the file with: nano .env"
    echo ""
    read -p "Press Enter to continue after editing .env file..."
else
    echo "✅ .env file already exists"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data uploads chroma_db logs
echo "✅ Directories created"

# Build and start the application
echo "🔨 Building Docker image..."
docker-compose build

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully"
else
    echo "❌ Failed to build Docker image"
    exit 1
fi

echo "🚀 Starting HSA Chatbot..."
docker-compose up -d

if [ $? -eq 0 ]; then
    echo "✅ HSA Chatbot started successfully"
    echo ""
    echo "🎉 Setup completed!"
    echo "================================"
    echo "📱 Access your chatbot at: http://localhost:5000"
    echo "⚙️  Admin panel at: http://localhost:5000/admin"
    echo "🔑 Default admin credentials:"
    echo "   Username: admin"
    echo "   Password: hsa_admin_2024"
    echo ""
    echo "📊 Check status: docker-compose ps"
    echo "📋 View logs: docker-compose logs -f"
    echo "🛑 Stop: docker-compose down"
    echo ""
    echo "⚠️  Remember to:"
    echo "   1. Change admin password in production"
    echo "   2. Upload HSA documents via admin panel"
    echo "   3. Configure SSL for production use"
else
    echo "❌ Failed to start HSA Chatbot"
    echo "Check logs with: docker-compose logs"
    exit 1
fi

