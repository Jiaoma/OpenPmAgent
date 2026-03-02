"""后端测试服务器"""
import os

os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///./test.db'
os.environ['DEBUG'] = 'true'
os.environ['LLM_TYPE'] = 'none'

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="OpenPmAgent Test API",
    description="后端测试服务器",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "OpenPmAgent API Server", "version": "0.1.0", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "environment": "test"}

@app.get("/api/v1/test/ping")
async def ping():
    return {"message": "pong"}

if __name__ == "__main__":
    import uvicorn
    print("启动后端测试服务器...")
    uvicorn.run(app, host='0.0.0.0', port=8000, log_level='info')
