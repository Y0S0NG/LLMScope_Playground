#!/bin/bash
# Test Chat Endpoint

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get backend URL
cd backend
BACKEND_URL=$(eb status | grep CNAME | awk '{print $2}')
cd ..

echo "=================================="
echo "Chat Endpoint Test"
echo "=================================="
echo "Backend URL: http://$BACKEND_URL"
echo ""

# Create session
echo -e "${YELLOW}Creating session...${NC}"
SESSION_RESPONSE=$(curl -s -X POST http://$BACKEND_URL/api/v1/sessions/create)
SESSION_ID=$(echo "$SESSION_RESPONSE" | jq -r '.session_id')
echo "Session ID: $SESSION_ID"
echo ""

# Test chat
echo -e "${YELLOW}Testing chat endpoint...${NC}"
CHAT_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: $SESSION_ID" \
  -d '{"message":"Say hello in one sentence"}' \
  http://$BACKEND_URL/api/v1/playground/chat)

echo "$CHAT_RESPONSE" | jq .
echo ""

# Check for error
ERROR=$(echo "$CHAT_RESPONSE" | jq -r '.detail // empty')
if [ -n "$ERROR" ]; then
    echo -e "${RED}❌ Error: $ERROR${NC}"
    echo ""
    echo "Common issues:"
    echo "1. ANTHROPIC_API_KEY not set or invalid"
    echo "2. API key doesn't have credits"
    echo "3. Network connectivity issue"
    echo ""
    echo "Check backend logs:"
    echo "  cd backend && eb logs"
    exit 1
else
    RESPONSE=$(echo "$CHAT_RESPONSE" | jq -r '.response')
    if [ -n "$RESPONSE" ] && [ "$RESPONSE" != "null" ]; then
        echo -e "${GREEN}✅ Chat successful!${NC}"
        echo "Response: $RESPONSE"
    else
        echo -e "${RED}❌ Unexpected response format${NC}"
        exit 1
    fi
fi
echo ""

# Get metrics to verify event was logged
echo -e "${YELLOW}Checking metrics...${NC}"
METRICS=$(curl -s -H "X-Session-ID: $SESSION_ID" \
  http://$BACKEND_URL/api/v1/sessions/current/metrics)
echo "$METRICS" | jq .
echo ""

TOTAL_EVENTS=$(echo "$METRICS" | jq -r '.total_events')
if [ "$TOTAL_EVENTS" -gt 0 ]; then
    echo -e "${GREEN}✅ Event logged successfully (Total events: $TOTAL_EVENTS)${NC}"
else
    echo -e "${RED}❌ Event not logged${NC}"
fi
