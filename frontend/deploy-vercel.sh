#!/bin/bash
# Quick deploy to Vercel

set -e

echo "🚀 Deploying Frontend to Vercel..."

# Check if vercel is installed
if ! command -v vercel &> /dev/null; then
    echo "📦 Installing Vercel CLI..."
    npm install -g vercel
fi

# Get backend URL
echo "🔍 Getting backend URL..."
cd ../backend
BACKEND_URL=$(eb status | grep CNAME | awk '{print $2}')
echo "Backend URL: http://$BACKEND_URL"
cd ../frontend

# Create .env.production
echo "📝 Creating .env.production..."
cat > .env.production << EOF
VITE_API_URL=http://$BACKEND_URL
EOF

echo "✅ .env.production created"

echo ""
echo "📤 Deploying to Vercel..."
echo "Follow the prompts to complete deployment."
echo ""

# Deploy
vercel --prod

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Your URLs:"
echo "   Frontend: (shown above)"
echo "   Backend:  http://$BACKEND_URL"
echo "   API Docs: http://$BACKEND_URL/docs"
