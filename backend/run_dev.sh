#!/bin/bash

# LLMScope Playground Development Server Startup Script

echo "🚀 Starting LLMScope Playground Development Server"
echo "=================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it with your settings."
    echo "   Especially set PLAYGROUND_ANTHROPIC_API_KEY"
fi

# Wait for database (if using Docker)
echo "⏳ Waiting for PostgreSQL..."
until PGPASSWORD=postgres psql -h localhost -p 5434 -U postgres -d llmscope -c '\q' 2>/dev/null; do
    echo "   PostgreSQL is unavailable - waiting..."
    sleep 2
done
echo "✅ PostgreSQL is ready"

# Run migrations
echo "🔄 Running database migrations..."
alembic upgrade head

# Start server
echo ""
echo "✅ Starting FastAPI server on http://localhost:8001"
echo "📚 API documentation available at http://localhost:8001/docs"
echo ""
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
