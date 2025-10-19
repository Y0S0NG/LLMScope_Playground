#!/bin/bash
# Comprehensive Backend API Test Script

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get backend URL
cd backend
BACKEND_URL=$(eb status | grep CNAME | awk '{print $2}')
cd ..

if [ -z "$BACKEND_URL" ]; then
    echo -e "${RED}❌ Could not get backend URL${NC}"
    exit 1
fi

echo "=================================="
echo "Backend API Test Suite"
echo "=================================="
echo "Backend URL: http://$BACKEND_URL"
echo ""

# Test 1: Health Check
echo -e "${YELLOW}Test 1: Health Check${NC}"
HEALTH=$(curl -s http://$BACKEND_URL/health)
echo "$HEALTH" | jq .
STATUS=$(echo "$HEALTH" | jq -r '.status')
if [ "$STATUS" = "healthy" ]; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${RED}❌ Health check failed${NC}"
    exit 1
fi
echo ""

# Test 2: API Docs
echo -e "${YELLOW}Test 2: API Documentation${NC}"
DOCS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://$BACKEND_URL/docs)
if [ "$DOCS_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ API docs accessible at http://$BACKEND_URL/docs${NC}"
else
    echo -e "${RED}❌ API docs not accessible (HTTP $DOCS_STATUS)${NC}"
fi
echo ""

# Test 3: Create Session
echo -e "${YELLOW}Test 3: Create Session${NC}"
SESSION_RESPONSE=$(curl -s -X POST http://$BACKEND_URL/api/v1/sessions/create)
echo "$SESSION_RESPONSE" | jq .
SESSION_ID=$(echo "$SESSION_RESPONSE" | jq -r '.session_id')
if [ "$SESSION_ID" != "null" ] && [ -n "$SESSION_ID" ]; then
    echo -e "${GREEN}✅ Session created: $SESSION_ID${NC}"
else
    echo -e "${RED}❌ Session creation failed${NC}"
    exit 1
fi
echo ""

# Test 4: Get Session Info
echo -e "${YELLOW}Test 4: Get Session Info${NC}"
SESSION_INFO=$(curl -s -H "X-Session-ID: $SESSION_ID" \
  http://$BACKEND_URL/api/v1/sessions/current/info)
echo "$SESSION_INFO" | jq .
INFO_SESSION_ID=$(echo "$SESSION_INFO" | jq -r '.session_id')
if [ "$INFO_SESSION_ID" = "$SESSION_ID" ]; then
    echo -e "${GREEN}✅ Session info retrieved${NC}"
else
    echo -e "${RED}❌ Session info mismatch${NC}"
fi
echo ""

# Test 5: Get Session Metrics
echo -e "${YELLOW}Test 5: Get Session Metrics${NC}"
METRICS=$(curl -s -H "X-Session-ID: $SESSION_ID" \
  http://$BACKEND_URL/api/v1/sessions/current/metrics)
echo "$METRICS" | jq .
TOTAL_EVENTS=$(echo "$METRICS" | jq -r '.total_events')
if [ "$TOTAL_EVENTS" = "0" ]; then
    echo -e "${GREEN}✅ Session metrics retrieved (0 events - expected)${NC}"
else
    echo -e "${YELLOW}⚠️  Session has $TOTAL_EVENTS events${NC}"
fi
echo ""

# Test 6: Reset Session
echo -e "${YELLOW}Test 6: Reset Session${NC}"
RESET_RESPONSE=$(curl -s -X POST \
  -H "X-Session-ID: $SESSION_ID" \
  http://$BACKEND_URL/api/v1/sessions/current/reset)
echo "$RESET_RESPONSE" | jq .
RESET_MSG=$(echo "$RESET_RESPONSE" | jq -r '.message')
if [ "$RESET_MSG" = "Session reset successfully" ]; then
    echo -e "${GREEN}✅ Session reset successful${NC}"
else
    echo -e "${RED}❌ Session reset failed${NC}"
fi
echo ""

# Test 7: Cleanup Stats
echo -e "${YELLOW}Test 7: Cleanup Statistics${NC}"
CLEANUP_STATS=$(curl -s http://$BACKEND_URL/api/v1/cleanup/stats)
echo "$CLEANUP_STATS" | jq .
TOTAL_SESSIONS=$(echo "$CLEANUP_STATS" | jq -r '.total_sessions')
echo -e "${GREEN}✅ Cleanup stats retrieved (Total sessions: $TOTAL_SESSIONS)${NC}"
echo ""

# Test 8: Cleanup Dry Run
echo -e "${YELLOW}Test 8: Cleanup Dry Run${NC}"
CLEANUP_DRY=$(curl -s -X POST "http://$BACKEND_URL/api/v1/cleanup/run?dry_run=true")
echo "$CLEANUP_DRY" | jq .
IS_DRY_RUN=$(echo "$CLEANUP_DRY" | jq -r '.dry_run')
if [ "$IS_DRY_RUN" = "true" ]; then
    echo -e "${GREEN}✅ Cleanup dry run successful${NC}"
else
    echo -e "${RED}❌ Cleanup dry run failed${NC}"
fi
echo ""

# Test 9: OpenAPI Spec
echo -e "${YELLOW}Test 9: OpenAPI Specification${NC}"
OPENAPI_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://$BACKEND_URL/openapi.json)
if [ "$OPENAPI_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ OpenAPI spec accessible${NC}"
else
    echo -e "${RED}❌ OpenAPI spec not accessible (HTTP $OPENAPI_STATUS)${NC}"
fi
echo ""

# Summary
echo "=================================="
echo -e "${GREEN}✅ All Tests Completed!${NC}"
echo "=================================="
echo ""
echo "📊 Summary:"
echo "   Backend URL: http://$BACKEND_URL"
echo "   API Docs:    http://$BACKEND_URL/docs"
echo "   Session ID:  $SESSION_ID"
echo ""
echo "🌐 URLs:"
echo "   Health:   http://$BACKEND_URL/health"
echo "   Docs:     http://$BACKEND_URL/docs"
echo "   ReDoc:    http://$BACKEND_URL/redoc"
echo "   OpenAPI:  http://$BACKEND_URL/openapi.json"
echo ""
