#!/bin/bash
# Production startup script for LLMScope Playground

set -e  # Exit on error

echo "🚀 Starting LLMScope Playground..."

# Run database migrations
echo "📦 Running database migrations..."
alembic upgrade head

# Start the FastAPI server
echo "✅ Starting server on port ${PORT:-8001}..."
exec uvicorn app.main:app --host ${HOST:-0.0.0.0} --port ${PORT:-8001}
