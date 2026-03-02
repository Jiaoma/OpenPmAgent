"""Backup management API routes."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import json

from app.database import get_db
from app.dependencies import CurrentUser, CurrentAdmin
from app.schemas.common import APIResponse
from app.schemas.backup import BackupCreate, BackupResponse, RestoreRequest, RestoreResponse
from app.services.backup_service import backup_service

router = APIRouter(prefix="/backup", tags=["Backup Management"])


# ==================== Backup Management ====================
@router.post("/create", response_model=APIResponse[BackupResponse])
async def create_backup(
    schema: BackupCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Create a database backup (Admin only)."""
    backup_data = await backup_service.create_backup(
        db,
        name=schema.name,
        description=schema.description
    )
    return APIResponse[BackupResponse](
        code=200,
        message="备份创建成功",
        data=BackupResponse(**backup_data)
    )


@router.get("/download")
async def download_backup(
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Download backup as JSON file (Admin only)."""
    backup_data = await backup_service.create_backup(db)
    json_str = json.dumps(backup_data, indent=2, ensure_ascii=False)
    json_bytes = json_str.encode('utf-8')

    return StreamingResponse(
        content=iter([json_bytes]),
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        }
    )


@router.post("/restore", response_model=APIResponse[RestoreResponse])
async def restore_from_backup(
    schema: RestoreRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Restore database from backup (Admin only)."""
    # Apply restore options if provided
    restore_data = None
    if schema.restore_options:
        restore_data = {}
        original_data = schema.backup_data.get("data", {})
        if schema.restore_options.get("team") and "team" in original_data:
            restore_data["team"] = original_data["team"]
        if schema.restore_options.get("architecture") and "architecture" in original_data:
            restore_data["architecture"] = original_data["architecture"]
        if schema.restore_options.get("project") and "project" in original_data:
            restore_data["project"] = original_data["project"]

    result = await backup_service.restore_from_backup(
        db,
        backup_data=schema.backup_data,
        current_user_id=current_admin.id,
        restore_data=restore_data
    )
    return APIResponse[RestoreResponse](
        code=200,
        message="恢复操作完成",
        data=RestoreResponse(**result)
    )
