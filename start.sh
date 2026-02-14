#!/bin/bash
# Quick start script for development

set -e

echo "🎬 AI Video Editor - Development Setup"
echo "======================================="

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker check passed"

# Create .env files if they don't exist
if [ ! -f backend/.env ]; then
    echo "📝 Creating backend/.env from example..."
    cp backend/.env.example backend/.env
fi

if [ ! -f frontend/.env ]; then
    echo "📝 Creating frontend/.env from example..."
    cp frontend/.env.example frontend/.env
fi

echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

echo ""
echo "✅ Services are running!"
echo ""
echo "📍 Application URLs:"
echo "   Frontend: http://localhost:3000"
echo "   API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   MinIO Console: http://localhost:9001"
echo ""
echo "🔐 Default Credentials:"
echo "   MinIO: minioadmin / minioadmin"
echo "   Database: video_editor / password123"
echo ""
echo "📝 Next steps:"
echo "   1. Register a new account at http://localhost:3000"
echo "   2. Create a project"
echo "   3. Upload videos or images"
echo "   4. Enter a prompt (e.g., '30 second fast montage with upbeat music')"
echo "   5. Click 'Generate Video'"
echo ""
echo "🔗 Service endpoints:"
echo "   docker-compose logs -f     # View logs"
echo "   docker-compose down        # Stop all services"
echo "   docker-compose restart     # Restart services"
echo ""
