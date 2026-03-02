"""Backup management Pydantic schemas."""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class BackupCreate(BaseModel):
    """Schema for creating a backup."""
    name: Optional[str] = Field(None, max_length=255, description="备份名称")
    description: Optional[str] = Field(None, max_length=1000, description="备份描述")


class BackupResponse(BaseModel):
    """Schema for backup response."""
    name: str
    description: str
    timestamp: str
    data: Dict[str, Any]


class RestoreRequest(BaseModel):
    """Schema for restore request."""
    backup_data: Dict[str, Any] = Field(..., description="备份数据")
    restore_options: Optional[Dict[str, bool]] = Field(
        None,
        description="恢复选项：{'team': bool, 'architecture': bool, 'project': bool}"
    )


class RestoreResponse(BaseModel):
    """Schema for restore response."""
    team: str
    architecture: str
    project: str
    errors: List[str]
