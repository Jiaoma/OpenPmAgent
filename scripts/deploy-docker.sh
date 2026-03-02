#!/bin/bash
# OpenPmAgent Docker Deployment Fix and Launch Script
# 修复Docker网络问题并启动服务

set -e

echo "=========================================="
echo "OpenPmAgent Docker部署脚本"
echo "=========================================="

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 颜色定义
echo_step() {
    echo -e "\n${YELLOW}[$(date '+%H:%M:%S')] $1${NC}"
}

echo_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

echo_error() {
    echo -e "${RED}✗ $1${NC}"
}

# ==================== 步骤1: 检查Docker状态 ====================
echo_step "步骤1: 检查Docker状态"

if command -v docker &> /dev/null; then
    echo_success "Docker已安装: $(docker --version)"
else
    echo_error "Docker未安装"
    exit 1
fi

if command -v docker-compose &> /dev/null || command -v docker compose &> /dev/null; then
    if command -v docker compose &> /dev/null; then
        echo_success "Docker Compose已安装: $(docker compose version)"
        COMPOSE_CMD="docker compose"
    else
        echo_success "Docker Compose已安装: $(docker-compose --version)"
        COMPOSE_CMD="docker-compose"
    fi
else
    echo_error "Docker Compose未安装"
    exit 1
fi

# 检查Docker服务状态
echo_step "检查Docker服务状态"
if systemctl is-active --quiet docker 2>/dev/null; then
    echo_success "Docker服务正在运行"
else
    echo -e "${YELLOW}⚠ Docker服务未运行，尝试启动...${NC}"
    sudo systemctl start docker || {
        echo_error "无法启动Docker服务"
        exit 1
    }
    echo_success "Docker服务已启动"
fi

# ==================== 步骤2: 测试Docker网络 ====================
echo_step "步骤2: 测试Docker网络连接"

echo "测试Docker Hub连接..."
if ping -c 1 registry-1.docker.io &> /dev/null; then
    echo_success "可以连接到Docker Hub"
else
    echo_error "无法连接到Docker Hub，配置镜像加速器..."
    
    # 配置镜像加速器
    echo_step "配置Docker镜像加速器"
    sudo mkdir -p /etc/docker 2>/dev/null || true
    
    # 写入daemon.json
    sudo tee /etc/docker/daemon.json > /dev/null <<'EOF'
{
  "registry-mirrors": [
    "https://docker.1panel.live",
    "https://docker.awsl9527.cn",
    "https://dockerhub.icu"
  ],
  "max-concurrent-downloads": 10
}
EOF
    
    echo "重启Docker服务以应用配置..."
    sudo systemctl restart docker
    sleep 5
    echo_success "镜像加速器配置完成"
fi

# 测试拉取小镜像
echo "测试镜像拉取..."
if docker pull alpine:latest &> /dev/null; then
    echo_success "镜像拉取测试通过"
else
    echo_error "镜像拉取测试失败，请检查网络配置"
    exit 1
fi

# ==================== 步骤3: 预拉取所需镜像 ====================
echo_step "步骤3: 预拉取所需Docker镜像"

REQUIRED_IMAGES=(
    "postgres:15-alpine"
    "redis:7-alpine"
    "python:3.11-slim"
    "nginx:1.24-alpine"
)

PULL_FAILED=0

for image in "${REQUIRED_IMAGES[@]}"; do
    echo -e "${YELLOW}正在拉取: $image...${NC}"
    if docker pull "$image" &> /dev/null; then
        echo_success "$image 拉取成功"
    else
        echo_error "$image 拉取失败"
        PULL_FAILED=$((PULL_FAILED + 1))
    fi
done

if [ $PULL_FAILED -gt 0 ]; then
    echo_error "部分镜像拉取失败，将尝试继续启动服务..."
fi

# ==================== 步骤4: 停止现有容器 ====================
echo_step "步骤4: 清理现有容器"

echo "停止并删除现有容器..."
$COMPOSE_CMD down -v 2>/dev/null || true
echo_success "清理完成"

# ==================== 步骤5: 构建镜像 ====================
echo_step "步骤5: 构建后端Docker镜像"

echo "正在构建后端镜像..."
$COMPOSE_CMD build backend

if [ $? -eq 0 ]; then
    echo_success "后端镜像构建成功"
else
    echo_error "后端镜像构建失败"
    exit 1
fi

# ==================== 步骤6: 构建前端 ====================
echo_step "步骤6: 构建前端静态文件"

if [ -d "frontend" ]; then
    echo "进入前端目录..."
    cd frontend
    
    if [ ! -d "node_modules" ]; then
        echo "安装前端依赖（这可能需要几分钟）..."
        npm install
    fi
    
    echo "构建前端..."
    npm run build
    
    if [ $? -eq 0 ] && [ -d "dist" ]; then
        echo_success "前端构建成功"
    else
        echo_error "前端构建失败"
        exit 1
    fi
    
    cd ..
else
    echo_error "前端目录不存在"
    exit 1
fi

# ==================== 步骤7: 启动服务 ====================
echo_step "步骤7: 启动所有服务"

echo "启动服务（postgres, redis, backend, nginx）..."
$COMPOSE_CMD up -d postgres redis backend nginx

# ==================== 步骤8: 等待服务就绪 ====================
echo_step "步骤8: 等待服务就绪"

echo "等待服务启动（30秒）..."
sleep 30

# 检查容器状态
echo ""
echo "容器状态:"
$COMPOSE_CMD ps

# 检查服务健康状态
echo ""
echo "检查服务健康状态..."

MAX_RETRIES=10
RETRY=0

while [ $RETRY -lt $MAX_RETRIES ]; do
    RETRY=$((RETRY + 1))
    
    echo "检查... ($RETRY/$MAX_RETRIES)"
    
    if curl -sf http://localhost:8080/health > /dev/null 2>&1; then
        echo_success "后端服务健康检查通过"
        break
    fi
    
    if [ $RETRY -lt $MAX_RETRIES ]; then
        sleep 3
    fi
done

if [ $RETRY -eq $MAX_RETRIES ]; then
    echo_error "服务健康检查失败"
    echo ""
    echo "查看后端日志:"
    $COMPOSE_CMD logs backend --tail=50
    exit 1
fi

# ==================== 部署完成 ====================
echo ""
echo "=========================================="
echo -e "${GREEN}部署完成！${NC}"
echo "=========================================="
echo ""
echo "应用访问地址:"
echo -e "  ${GREEN}前端界面:${NC}  http://localhost:8080"
echo -e "  ${GREEN}API文档:${NC}  http://localhost:8080/docs"
echo -e "  ${GREEN}API文档:${NC}  http://localhost:8080/redoc"
echo -e "  ${GREEN}健康检查:${NC}  http://localhost:8080/health"
echo ""
echo "常用命令:"
echo "  查看所有日志:  $COMPOSE_CMD logs -f"
echo "  查看后端日志:  $COMPOSE_CMD logs -f backend"
echo "  查看前端日志:  $COMPOSE_CMD logs -f nginx"
echo "  查看数据库日志:  $COMPOSE_CMD logs -f postgres"
echo "  停止所有服务:  $COMPOSE_CMD down"
echo "  重启所有服务:  $COMPOSE_CMD restart"
echo ""
echo "数据库连接信息:"
echo "  数据库: postgres:5432/openpm"
echo "  用户名: openpm"
echo "  密码: openpm_secret_password"
echo ""
echo -e "${YELLOW}提示: ${NC}"
echo "  - 首次启动可能需要1-2分钟"
echo "  - 如果遇到问题，请使用 $COMPOSE_CMD logs 查看日志"
echo "  - 可以使用 docker stats 查看容器资源使用情况"
echo ""
