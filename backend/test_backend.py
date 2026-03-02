"""最小化后端测试服务器"""
import os
os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///./test.db'
os.environ['DEBUG'] = 'true'
os.environ['LLM_TYPE'] = 'none'

import sys
sys.path.insert(0, '/home/jetson/workplace/OpenPmAgent/backend')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="OpenPmAgent Test API",
    description="测试后端服务器",
    version="0.1.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 根路径
@app.get("/")
async def root():
    return {
        "message": "OpenPmAgent API Server",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs"
    }

# 健康检查
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "environment": "test"
    }

# 测试API路由
@app.get("/api/v1/test/ping")
async def ping():
    return {
        "message": "pong",
        "timestamp": "2024-01-01"
    }

# 测试数据库连接（仅测试）
@app.get("/api/v1/test/db-check")
async def db_check():
    try:
        from app.database import engine
        return {
            "status": "connected",
            "database": os.getenv('DATABASE_URL')
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("后端测试服务器启动...")
    print("=" * 60)
    print("访问地址：")
    print("  http://localhost:8000/")
    print("  http://localhost:8000/docs")
    print("  http://localhost:8000/health")
    print("  http://localhost:8000/api/v1/test/ping")
    print("=" * 60)
    uvicorn.run(app, host='0.0.0.0', port=8000, log_level='info')
