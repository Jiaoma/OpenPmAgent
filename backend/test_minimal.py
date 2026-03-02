"""最小化FastAPI测试服务器"""
from fastapi import FastAPI

app = FastAPI(title="Minimal Test Server")

@app.get("/")
async def root():
    return {
        "message": "OpenPmAgent Minimal Test Server",
        "status": "running",
        "version": "0.1.0"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "minimal-test"
    }

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("Minimal Test Server Starting...")
    print("=" * 60)
    uvicorn.run(app, host='0.0.0.0', port=8001)
