#!/bin/bash
set -e

echo "Starting LLMScope Playground Backend..."

# Initialize database
echo "Initializing database..."
python init_db.py

# Start the application
echo "Starting uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
