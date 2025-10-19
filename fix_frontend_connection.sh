#!/bin/bash
# Complete fix for frontend-backend connection

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=================================="
echo "Fixing Frontend-Backend Connection"
echo "=================================="
echo ""

# Step 1: Get backend URL
echo -e "${YELLOW}Step 1: Getting backend URL...${NC}"
cd backend
BACKEND_URL=$(eb status | grep CNAME | awk '{print $2}')
echo "Backend URL: http://$BACKEND_URL"
cd ..

# Step 2: Get frontend URL
echo -e "${YELLOW}Step 2: Getting frontend URL...${NC}"
cd frontend
FRONTEND_URL=$(vercel ls 2>/dev/null | grep -i production | awk '{print $2}' | head -1)
if [ -z "$FRONTEND_URL" ]; then
    echo "Could not auto-detect frontend URL"
    echo "Please enter your Vercel frontend URL (e.g., llmscope-frontend.vercel.app):"
    read FRONTEND_URL
fi
echo "Frontend URL: https://$FRONTEND_URL"
cd ..

# Step 3: Configure CORS on backend
echo -e "${YELLOW}Step 3: Configuring CORS on backend...${NC}"
cd backend

# Set comprehensive CORS settings
eb setenv \
  CORS_ORIGINS="https://$FRONTEND_URL,https://*.vercel.app,http://localhost:5173,http://localhost:4173" \
  PLAYGROUND_CORS_ORIGINS="https://$FRONTEND_URL,https://*.vercel.app,http://localhost:5173,http://localhost:4173"

echo -e "${GREEN}✅ CORS configured${NC}"

# Step 4: Verify CORS is set
echo -e "${YELLOW}Step 4: Verifying CORS settings...${NC}"
eb printenv | grep CORS
echo ""

# Step 5: Deploy backend with new CORS
echo -e "${YELLOW}Step 5: Deploying backend with CORS fix...${NC}"
echo "This will take 2-3 minutes..."
eb deploy

echo -e "${GREEN}✅ Backend deployed${NC}"
echo ""
cd ..

# Step 6: Update frontend environment variable
echo -e "${YELLOW}Step 6: Updating frontend environment variable...${NC}"
cd frontend

# Check if env var exists
vercel env ls | grep VITE_API_URL || {
    echo "Adding VITE_API_URL to Vercel..."
    echo "http://$BACKEND_URL" | vercel env add VITE_API_URL production
}

# Also create .env.production
echo "VITE_API_URL=http://$BACKEND_URL" > .env.production
echo -e "${GREEN}✅ Frontend configured${NC}"

# Step 7: Redeploy frontend
echo -e "${YELLOW}Step 7: Redeploying frontend...${NC}"
vercel --prod

echo -e "${GREEN}✅ Frontend deployed${NC}"
echo ""
cd ..

# Step 8: Test the connection
echo -e "${YELLOW}Step 8: Testing connection...${NC}"
sleep 5

SESSION_ID=$(curl -s -X POST http://$BACKEND_URL/api/v1/sessions/create | jq -r '.session_id')
echo "Created test session: $SESSION_ID"

CHAT_RESULT=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: $SESSION_ID" \
  -d '{"message":"test"}' \
  http://$BACKEND_URL/api/v1/playground/chat)

RESPONSE=$(echo "$CHAT_RESULT" | jq -r '.response // .detail // "error"')
echo "Chat test result: $RESPONSE"

if [ "$RESPONSE" != "error" ] && [ "$RESPONSE" != "" ]; then
    echo -e "${GREEN}✅ Backend chat is working!${NC}"
else
    echo "⚠️  Chat test inconclusive, check manually"
fi

echo ""
echo "=================================="
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "=================================="
echo ""
echo "📊 Your URLs:"
echo "   Backend:  http://$BACKEND_URL"
echo "   API Docs: http://$BACKEND_URL/docs"
echo "   Frontend: https://$FRONTEND_URL"
echo ""
echo "🧪 Test your frontend now:"
echo "   1. Open: https://$FRONTEND_URL"
echo "   2. Send a chat message"
echo "   3. Check browser console (F12) for errors"
echo ""
echo "If still not working:"
echo "   1. Wait 1-2 minutes for DNS/cache to update"
echo "   2. Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)"
echo "   3. Check browser console for exact error"
echo ""
