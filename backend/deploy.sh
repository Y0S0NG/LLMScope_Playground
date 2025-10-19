#!/bin/bash
# Quick deployment script for AWS Elastic Beanstalk

set -e

echo "🚀 Deploying LLMScope Backend to AWS Elastic Beanstalk..."

# Check if eb is initialized
if [ ! -d ".elasticbeanstalk" ]; then
    echo "❌ Elastic Beanstalk not initialized!"
    echo "Run: eb init -p python-3.11 llmscope-backend --region us-east-1"
    exit 1
fi

# Clean up any local build artifacts
echo "🧹 Cleaning up..."
rm -rf __pycache__ *.pyc .pytest_cache

# Deploy
echo "📦 Deploying to Elastic Beanstalk..."
eb deploy

# Check status
echo "✅ Deployment complete! Checking status..."
eb status

echo ""
echo "📊 View logs: eb logs"
echo "🌐 Open app: eb open"
echo "🔍 Health: eb health"
