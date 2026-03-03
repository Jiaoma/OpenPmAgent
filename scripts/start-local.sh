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
else
    echo -e "${GREEN}✓ Virtual environment exists${NC}"
fi

source venv/bin/activate

# Create local test database
if [ ! -f "openpm_local.db" ]; then
    echo -e "${YELLOW}Initializing local database...${NC}"
else
    echo -e "${GREEN}✓ Database already exists${NC}"
fi
export DATABASE_URL="sqlite+aiosqlite:///./openpm_local.db"

# Start backend in background
export DATABASE_URL="sqlite+aiosqlite:///./openpm_local.db"
export SECRET_KEY="local_dev_secret_key_for_testing"
export LLM_TYPE="none"
export ENV="development"
export DEBUG="true"
export REDIS_URL=""

# Install without Redis and PostgreSQL drivers (using SQLite for local dev)
# Create local requirements file for development
cat > requirements_local.txt <<'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
gunicorn==21.2.0
sqlalchemy>=2.0.36
alembic>=1.14.0
aiosqlite==0.19.0
python-jose[cryptography]==3.3.0
passlib==1.7.4
bcrypt==4.1.2
python-multipart==0.0.6
langchain==0.1.0
openai==1.3.0
pydantic>=2.10.0
pydantic-settings>=2.6.0
python-dotenv==1.0.0
openpyxl==3.1.2
python-docx==1.1.0
loguru==0.7.2
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.1
EOF

# Check if dependencies are already installed
if ! pip show fastapi > /dev/null 2>&1; then
    # Install with compiler fix and prefer binary wheels
    echo -e "${YELLOW}Installing Python dependencies...${NC}"
    pip install --prefer-binary -r requirements_local.txt
else
    echo -e "${GREEN}✓ Python dependencies already installed${NC}"
fi

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

# Create default admin user if not exists
echo -e "${YELLOW}Creating default admin user if needed...${NC}"
python3 <<'EOF'
import asyncio
import sys
sys.path.insert(0, '.')
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.models.team import Person
from app.models.project import Version, Iteration, Task
from app.models.architecture import Module, Function, DataFlow
from app.core.security import get_password_hash

async def create_admin():
    engine = create_async_engine("sqlite+aiosqlite:///./openpm_local.db", echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Initialize database tables
    async with engine.begin() as conn:
        from app.database import Base
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.emp_id == "admin001"))
        existing = result.scalar_one_or_none()

        if not existing:
            admin = User(
                emp_id="admin001",
                password_hash=get_password_hash("admin123"),
                is_admin=True,
            )
            session.add(admin)
            await session.commit()
            print("✓ Default admin user created: admin001 / admin123")
        else:
            print("✓ Default admin user already exists")

    await engine.dispose()

asyncio.run(create_admin())
EOF

# 2. Start Frontend
echo -e "${GREEN}Starting frontend...${NC}"
cd ../frontend

cat > .env <<'EOF'
VITE_API_BASE_URL=http://localhost:8000/api/v1
EOF

cat > vite.config.ts <<'EOF'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/docs': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/redoc': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
EOF

# Install frontend dependencies
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    npm install
else
    echo -e "${GREEN}✓ Frontend dependencies already installed${NC}"
fi

# Build frontend
if [ ! -d "dist" ] || [ ! "$(ls -A dist 2>/dev/null)" ]; then
    echo -e "${YELLOW}Building frontend...${NC}"
    npm run build
else
    echo -e "${GREEN}✓ Frontend already built${NC}"
fi

# Start frontend
echo -e "${GREEN}Starting frontend on port 3000...${NC}"
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
echo -e "  ${GREEN}Frontend:${NC}  http://localhost:3000"
echo -e "  ${GREEN}Backend API:${NC}  http://localhost:8000"
echo -e "  ${GREEN}API Docs:${NC}  http://localhost:8000/docs"
echo -e "  ${GREEN}Health Check:${NC}  http://localhost:8000/health"
echo ""
echo "=========================================="
echo -e "${YELLOW}Login Information${NC}"
echo "=========================================="
echo ""
echo -e "${GREEN}Admin Login (Default):${NC}"
echo -e "  Employee ID: ${YELLOW}admin001${NC}"
echo -e "  Password:    ${YELLOW}admin123${NC}"
echo ""
echo -e "${GREEN}User Login:${NC}"
echo "  Use any employee ID from your team (no password required)"
echo ""
echo -e "${YELLOW}Note:${NC} You can create new users via the API or directly in the database"
echo ""
echo "=========================================="
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

# Keep script running (services run in background)
