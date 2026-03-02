#!/bin/bash
# OpenPmAgent Local Development Script
# This script starts backend and frontend locally without Docker

set -e

echo "=========================================="
echo "OpenPmAgent Local Development"
echo "=========================================="

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Kill any existing processes on port 8000 and 3000
echo -e "${YELLOW}Stopping any existing processes...${NC}"
pkill -f "uvicorn" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true

# Create a local .env file for local development
cat > /tmp/local_env.txt <<'EOF'
# Local Development Environment
DATABASE_URL=sqlite+aiosqlite:///./openpm_local.db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=local_dev_secret_key_for_testing
ALGORITHM=HS256
NGINX_PORT=8080
LLM_TYPE=none
ENV=development
DEBUG=true
EOF

# 1. Start Backend
echo -e "${GREEN}Starting backend...${NC}"
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo -e "${YELLOW}Installing backend dependencies...${NC}"
source venv/bin/activate
pip install --upgrade pip -q
pip install -q -r requirements.txt

# Create local test database
echo -e "${YELLOW}Initializing local database...${NC}"
export DATABASE_URL="sqlite+aiosqlite:///./openpm_local.db"

# Start backend in background
export DATABASE_URL="sqlite+aiosqlite:///./openpm_local.db"
export SECRET_KEY="local_dev_secret_key_for_testing"
export LLM_TYPE="none"
export ENV="development"
export DEBUG="true"
export REDIS_URL=""

# Disable Redis for local development
sed -i 's/redis==5.0.1/# redis==5.0.1/' requirements.txt
sed -i 's/celery==5.3.4/# celery==5.3.4/' requirements.txt

# Install without Redis
pip install -q -r requirements.txt

# Start backend
echo -e "${GREEN}Starting FastAPI backend on port 8000...${NC}"
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to start
echo -e "${YELLOW}Waiting for backend to be ready...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend is healthy${NC}"
        break
    fi
    echo "Waiting... ($i/30)"
    sleep 2
done

# Check if backend started successfully
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${RED}✗ Backend failed to start${NC}"
    echo "Backend logs:"
    cat /tmp/backend.log
    exit 1
fi

deactivate

# 2. Start Frontend
echo -e "${GREEN}Starting frontend...${NC}"
cd ../frontend

# Install frontend dependencies
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    npm install
fi

# Build frontend
echo -e "${YELLOW}Building frontend...${NC}"
npm run build

# Start frontend
echo -e "${GREEN}Starting frontend on port 5173...${NC}"
nohup npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# 3. Display deployment info
echo ""
echo "=========================================="
echo -e "${GREEN}Local development started successfully!${NC}"
echo "=========================================="
echo ""
echo "Services are available at:"
echo -e "  ${GREEN}Frontend:${NC}  http://localhost:5173"
echo -e "  ${GREEN}Backend API:${NC}  http://localhost:8000"
echo -e "  ${GREEN}API Docs:${NC}  http://localhost:8000/docs"
echo -e "  ${GREEN}Health Check:${NC}  http://localhost:8000/health"
echo ""
echo "Backend logs: tail -f /tmp/backend.log"
echo "Frontend logs: tail -f /tmp/frontend.log"
echo ""
echo "To stop services:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "Or run:"
echo "  pkill -f 'uvicorn|vite'"
echo ""

# Save PIDs for cleanup
echo "$BACKEND_PID" > /tmp/backend.pid
echo "$FRONTEND_PID" > /tmp/frontend.pid

# Keep script running
wait
