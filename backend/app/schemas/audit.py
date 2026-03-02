"""Audit log schemas."""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class AuditLogBase(BaseModel):
    """Base audit log schema."""
    user_id: Optional[int] = None
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[int] = None
    changes: Optional[Dict[str, Any]] = None
    status: Optional[str] = "success"
    timestamp: Optional[datetime] = None


class AuditLogCreate(AuditLogBase):
    """Schema for creating an audit log."""
    pass


class AuditLogUpdate(BaseModel):
    """Schema for updating an audit log."""
    user_id: Optional[int] = None
    action: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[int] = None
    changes: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class AuditLogResponse(AuditLogBase):
    """Schema for audit log response."""
    id: int

    class Config:
        from_attributes = True
