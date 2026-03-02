#!/bin/bash
# OpenPmAgent Deployment Script

set -e

echo "=========================================="
echo "OpenPmAgent Deployment Script"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}.env file not found. Creating from .env.example...${NC}"
    cp .env.example .env
    echo -e "${RED}Please edit .env file and run this script again.${NC}"
    exit 1
fi

# Load environment variables
export $(grep -v '^#' .env | xargs)

# 1. Stop existing containers
echo -e "${YELLOW}Stopping existing containers...${NC}"
docker-compose down

# 2. Build backend
echo -e "${GREEN}Building backend...${NC}"
docker-compose build backend

# 3. Build frontend (if exists)
if [ -d "frontend" ]; then
    echo -e "${GREEN}Building frontend...${NC}"
    cd frontend
    npm install
    npm run build
    cd ..
fi

# 4. Start services
echo -e "${GREEN}Starting services...${NC}"
docker-compose up -d postgres redis backend nginx

# 5. Wait for services to be ready
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 15

# 6. Check service health
echo -e "${YELLOW}Checking service health...${NC}"
for i in {1..10}; do
    if curl -f http://localhost:${NGINX_PORT:-8080}/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Services are healthy${NC}"
        break
    fi
    if [ $i -eq 10 ]; then
        echo -e "${RED}✗ Services failed to start${NC}"
        docker-compose logs backend
        exit 1
    fi
    echo "Waiting... ($i/10)"
    sleep 5
done

# 7. Display deployment info
echo ""
echo "=========================================="
echo -e "${GREEN}Deployment completed successfully!${NC}"
echo "=========================================="
echo ""
echo "Application is available at:"
echo -e "  ${GREEN}http://localhost:${NGINX_PORT:-8080}${NC}"
echo ""
echo "API Documentation:"
echo -e "  ${GREEN}http://localhost:${NGINX_PORT:-8080}/docs${NC}"
echo ""
echo "Useful commands:"
echo "  View logs:    docker-compose logs -f"
echo "  Stop services: docker-compose down"
echo "  Restart:      docker-compose restart"
echo ""
