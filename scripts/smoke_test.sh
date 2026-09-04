#!/bin/bash
# scripts/smoke_test.sh
# Simple smoke test to verify staging environment before Friday demo

STAGING_URL=${STAGING_URL:-"http://localhost:3000"}
API_URL=${API_URL:-"http://localhost:8000"}

# Terminal colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Starting smoke tests for Staging env..."
echo "------------------------------------------------"

FAILED=0

# 1. Frontend check
echo -n "Checking Frontend URL ($STAGING_URL)... "
if curl -s -o /dev/null -w "%{http_code}" "$STAGING_URL" | grep -qE "(200|30[127])"; then
    echo -e "${GREEN}[OK]${NC}"
else
    echo -e "${RED}[FAILED]${NC}"
    FAILED=1
fi

# 2. Login page check
echo -n "Checking Login page... "
if curl -s -o /dev/null -w "%{http_code}" "$STAGING_URL/login" | grep -qE "(200|30[127])"; then
    echo -e "${GREEN}[OK]${NC}"
else
    echo -e "${RED}[FAILED]${NC}"
    FAILED=1
fi

# 3. Backend health check
echo -n "Checking Backend /health endpoint... "
if curl -s -o /dev/null -w "%{http_code}" "$API_URL/health" | grep -q "200"; then
    echo -e "${GREEN}[OK]${NC}"
else
    echo -e "${RED}[FAILED]${NC}"
    FAILED=1
fi

# 4. Database check
echo -n "Checking Postgres connection... "
# Get container ID from compose
DB_CONTAINER=$(docker compose -f infra/docker-compose.staging.yml ps -q db 2>/dev/null)

if [ -z "$DB_CONTAINER" ]; then
    echo -e "${RED}[FAILED] - Container not found${NC}"
    FAILED=1
else
   if docker exec "$DB_CONTAINER" pg_isready -U openlearn > /dev/null 2>&1; then
         echo -e "${GREEN}[OK]${NC}"
    else
        echo -e "${RED}[FAILED] - DB not ready${NC}"
        FAILED=1
    fi
fi

echo "------------------------------------------------"
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All checks passed. System is ready.${NC}"
    exit 0
else
    echo -e "${RED}Smoke tests failed. Please check the logs.${NC}"
    exit 1
fi