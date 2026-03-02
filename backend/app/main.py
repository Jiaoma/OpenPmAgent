"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import get_db

app = FastAPI(
    title="OpenPmAgent API",
    description="企业级项目管理和团队管理平台",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
from app.api.v1 import auth, team, architecture, project, backup, audit
app.include_router(auth.router, prefix="/api/v1")
app.include_router(team.router, prefix="/api/v1")
app.include_router(architecture.router, prefix="/api/v1")
app.include_router(project.router, prefix="/api/v1")
app.include_router(backup.router, prefix="/api/v1")
app.include_router(audit.router, prefix="/api/v1")

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "OpenPmAgent API is running",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "env": settings.env,
        "llm_enabled": settings.llm_type != "none",
    }

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "env": settings.env,
        "llm_enabled": settings.llm_type != "none",
        "db_url": settings.database_url[:20] + "..." if len(settings.database_url) > 20 else "...",
    }
