"""Audit log management API routes."""
from typing import List, Optional, Dict
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.dependencies import CurrentUser, CurrentAdmin
from app.schemas.audit import (
    AuditLogCreate, AuditLogUpdate, AuditLogResponse
)
from app.schemas.common import APIResponse, PaginatedResponse, PaginatedData
from app.models.audit import AuditLog
from app.models.user import User

router = APIRouter(prefix="/audit", tags=["Audit Management"])


# ==================== Audit Log Management ====================
@router.get("/logs", response_model=APIResponse[PaginatedData[AuditLogResponse]])
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    resource_id: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Get all audit logs with pagination and filters."""
    result = await db.execute(
        select(AuditLog)
        .order_by(AuditLog.timestamp.desc())
        .offset(skip)
        .limit(limit)
    )

    total_count = await db.execute(
        select(func.count(AuditLog.id))
        .where(action == action if action else None)
        .where(resource_type == resource_type if resource_type else None)
        .where(resource_id == resource_id if resource_id else None)
        .where(start_date is not None if start_date else AuditLog.start_date >= start_date)
        .where(end_date is not None if end_date else AuditLog.end_date <= end_date)
    )

    logs = result.scalars().all()

    total_count_value = total_count.scalar()
    total = total_count_value if total_count_value else 0

    return APIResponse[PaginatedData[AuditLogResponse]](
        code=200,
        message="Success",
        data=PaginatedData(
            items=logs,
            total=total,
            page=(skip // limit) + 1,
            page_size=limit
        )
    )


@router.get("/logs/{id}", response_model=APIResponse[AuditLogResponse])
async def get_audit_log(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Get audit log by ID."""
    log = await db.get(AuditLog, id)
    if not log:
        raise HTTPException(status_code=404, detail=f"审计日志 {id} 不存在")

    # Include related user
    if log.user_id:
        await db.refresh(log.user)
    else:
        log.user = None

    return APIResponse[AuditLogResponse](
        code=200,
        message="Success",
        data=log
    )


@router.get("/logs/{id}/changes", response_model=APIResponse[Dict])
async def get_audit_log_changes(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Get audit log changes (diff)."""
    log = await db.get(AuditLog, id)
    if not log:
        raise HTTPException(status_code=404, detail=f"审计日志 {id} 不存在")

    # Get previous version for diff
    prev_log_result = await db.execute(
        select(AuditLog)
        .where(AuditLog.id < id)
        .order_by(AuditLog.timestamp.desc())
        .limit(1)
    )
    prev_log = prev_log_result.scalar_one_or_none()

    changes = []
    if prev_log and prev_log.changes:
        try:
            changes = prev_log.changes
        except:
            pass

    return APIResponse[Dict](
        code=200,
        message="Success",
        data={"id": log.id, "changes": changes}
    )


# ==================== Audit Log Management (Admin only) ====================
@router.post("/logs", response_model=APIResponse[AuditLogResponse])
async def create_audit_log(
    schema: AuditLogCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Create an audit log (Admin only)."""
    from app.models.audit import AuditLog

    # Create audit log entry
    log = AuditLog(
        user_id=schema.user_id,
        action=schema.action,
        resource_type=schema.resource_type,
        resource_id=schema.resource_id,
        changes=schema.changes,
        status=schema.status or "success",
        timestamp=datetime.utcnow()
    )

    db.add(log)
    await db.commit()
    await db.refresh(log)

    return APIResponse[AuditLogResponse](
        code=201,
        message="审计日志创建成功",
        data=log
    )


@router.put("/logs/{id}", response_model=APIResponse[AuditLogResponse])
async def update_audit_log(
    id: int,
    schema: AuditLogUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Update audit log (Admin only)."""
    from app.models.audit import AuditLog

    log = await db.get(AuditLog, id)
    if not log:
        raise HTTPException(status_code=404, detail=f"审计日志 {id} 不存在")

    # Update fields
    update_data = schema.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(log, key, value)

    # Update timestamp
    log.timestamp = datetime.utcnow()

    await db.commit()
    await db.refresh(log)

    return APIResponse[AuditLogResponse](
        code=200,
        message="审计日志更新成功",
        data=log
    )


@router.delete("/logs/{id}", response_model=APIResponse[None])
async def delete_audit_log(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Delete audit log (Admin only)."""
    log = await db.get(AuditLog, id)
    if not log:
        raise HTTPException(status_code=404, detail=f"审计日志 {id} 不存在")

    await db.delete(log)
    await db.commit()

    return APIResponse[None](
        code=200,
        message="审计日志删除成功",
        data=None
    )


# ==================== System Info ====================
@router.get("/system/info", response_model=APIResponse[Dict])
async def get_system_info(
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Get system information (Admin only)."""
    from app.database import get_db
    from app.models.audit import AuditLog
    from app.models.user import User

    # Get system statistics
    audit_count = await db.execute(
        select(func.count(AuditLog.id))
    )
    audit_count_value = audit_count.scalar() or 0

    # Get recent activities
    recent_audit_logs = await db.execute(
        select(AuditLog)
        .order_by(AuditLog.timestamp.desc())
        .limit(10)
    )
    recent_logs = recent_audit_logs.scalars().all()

    # Get user statistics
    user_count = await db.execute(
        select(func.count(User.id))
    )
    user_count_value = user_count.scalar() or 0

    admin_count = await db.execute(
        select(func.count(User.id))
        .where(User.is_admin == True)
    )
    admin_count_value = admin_count.scalar() or 0

    return APIResponse[Dict](
        code=200,
        message="Success",
        data={
            "system": {
                "audit_log_count": audit_count_value,
                "recent_activities": [
                    {
                        "id": log.id,
                        "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                        "action": log.action,
                        "resource_type": log.resource_type,
                        "resource_id": log.resource_id,
                        "user_id": log.user_id,
                    }
                    for log in recent_logs
                ],
                "users": {
                    "total_users": user_count_value,
                    "total_admins": admin_count_value,
                }
            }
        }
    )


@router.get("/health", response_model=APIResponse[Dict])
async def health_check(
    db: AsyncSession = Depends(get_db)
):
    """Health check endpoint (no auth)."""
    from app.database import get_db

    # Try database connection
    try:
        await db.execute("SELECT 1")
    except Exception as e:
        return APIResponse[Dict](
            code=200,
            message="Database connection error: " + str(e),
            data={}
        )

    # Check if database is writable
    try:
        await db.execute("SELECT 1 FROM test_audit_logs LIMIT 1")
        await db.rollback()

        return APIResponse[Dict](
            code=200,
            message="healthy",
            data={"database": "connected", "writable": True}
        )
    except Exception as e:
        return APIResponse[Dict](
            code=200,
            message="Database check failed: " + str(e),
            data={"database": "connected", "writable": False}
        )
