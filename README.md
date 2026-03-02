# OpenPmAgent

> 企业级项目管理和团队管理平台

## 项目概述

OpenPmAgent是一个面向企业中层管理者的项目管理和团队管理平台，支持同时管理20+人并划分为多个小组的场景。

## 技术栈

### 后端
- **框架**: FastAPI 0.104+ (Python 3.11+)
- **数据库**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0+
- **认证**: JWT + OAuth2
- **LLM集成**: LangChain 0.1+
- **任务队列**: Celery + Redis

### 前端
- **框架**: React 18+ + TypeScript 5.0+
- **UI**: Ant Design 5.0+
- **状态管理**: Zustand 4.0+
- **HTTP客户端**: Axios + React Query
- **构建工具**: Vite 5.0+

### 部署
- **容器化**: Docker Compose
- **反向代理**: Nginx 1.24+

## 项目结构

```
OpenPmAgent/
├── backend/          # FastAPI后端
│   ├── app/
│   │   ├── api/        # API路由
│   │   ├── models/     # 数据模型
│   │   ├── schemas/    # Pydantic模型
│   │   ├── services/   # 业务逻辑
│   │   ├── core/       # 核心模块（认证、LLM等）
│   │   └── utils/      # 工具函数
│   ├── tests/           # 后端测试
│   ├── Dockerfile
│   ├── requirements.txt
│   └── docker-compose.yml
├── frontend/         # React前端
│   ├── src/
│   │   ├── api/        # API客户端
│   │   ├── components/ # 组件
│   │   ├── pages/      # 页面
│   │   ├── stores/     # 状态管理
│   │   ├── types/      # TypeScript类型
│   │   └── styles/     # 样式
│   ├── tests/           # 前端测试
│   ├── package.json
│   └── vite.config.ts
├── nginx/             # Nginx配置
├── scripts/           # 部署脚本
├── SPEC.md            # 技术规格说明书
└── README.md          # 项目说明文档
```

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+

### 开发环境启动

1. **配置环境变量**
   ```bash
   cp backend/.env.example backend/.env
   cp backend/.env.example frontend/.env
   # 编辑.env文件，配置数据库连接等
   ```

2. **启动后端**
   ```bash
   cd backend
   docker-compose up -d postgres redis backend
   # 或者本地运行
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

3. **启动前端**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### 生产环境部署

1. **一键部署**
   ```bash
   ./scripts/deploy.sh
   ```

2. **访问应用**
   - 前端: http://localhost:8080
   - API文档: http://localhost:8080/docs
   - ReDoc: http://localhost:8080/redoc

## 核心功能

### 团队管理
- 人员档案管理（基本信息、能力模型、小组归属）
- 能力维度定义和评估
- 小组管理和关键人物管理
- 责任田管理
- 任务负载分析
- 团队结构可视化

### 技术架构档案
- 模块管理（树状结构、拖拽编辑）
- 功能管理（关联模块、数据流）
- 责任田-功能关联管理

### 项目管理
- 版本、迭代、任务管理
- 任务依赖关系管理
- 甘特图展示
- 任务图分析（最长路径、负载最高人员）
- 任务达成统计

### 系统管理
- Admin/普通用户登录
- 操作日志记录
- 权限控制

## LLM集成

支持三种LLM运行模式：
- **无LLM**: 基础功能，AI推荐禁用
- **OpenAI API**: 使用OpenAI兼容API
- **本地LLM**: 使用本地llama.cpp服务

## 开发说明

### 后端开发

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 运行开发服务器
uvicorn app.main:app --reload

# 运行测试
pytest

# 数据库迁移
alembic upgrade head
```

### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 运行开发服务器
npm run dev

# 构建
npm run build

# 运行测试
npm run test
```

## 测试

### 后端测试
```bash
cd backend
pytest tests/
```

### 前端测试
```bash
cd frontend
npm run test
```

### E2E测试
```bash
cd frontend
npx playwright test
```

## 许可证

MIT

## 贡献

欢迎提交 Pull Request！

## 联系方式

如有问题或建议，请提交Issue。
