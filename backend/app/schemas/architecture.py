from __future__ import annotations

"""Architecture management Pydantic schemas."""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ModuleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="模块名称")


class ModuleCreate(ModuleBase):
    parent_id: Optional[int] = Field(None, description="父模块ID")


class ModuleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    parent_id: Optional[int] = Field(None, description="父模块ID")


class ModuleMove(BaseModel):
    parent_id: int = Field(..., description="新的父模块ID")


class ModuleResponse(ModuleBase):
    id: int
    parent_id: Optional[int] = None
    children: List["ModuleResponse"] = []
    # Use function IDs instead of FunctionModuleResponse to avoid circular dependency
    function_ids: List[int] = []
    created_at: datetime


# Function Schemas
class FunctionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="功能名称")


class FunctionCreate(FunctionBase):
    parent_id: Optional[int] = Field(None, description="父功能ID")
    responsibility_id: Optional[int] = Field(None, description="责任田ID")


class FunctionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    parent_id: Optional[int] = Field(None)
    responsibility_id: Optional[int] = Field(None)


class FunctionMove(BaseModel):
    parent_id: int = Field(..., description="新的父功能ID")


class FunctionModuleCreate(BaseModel):
    function_id: int = Field(..., description="功能ID")
    module_id: int = Field(..., description="模块ID")
    order: int = Field(0, description="排序")


class FunctionModuleResponse(BaseModel):
    id: int
    function_id: int
    module_id: int
    order: int


class DataFlowCreate(BaseModel):
    source_function_id: int = Field(..., description="源功能ID")
    target_function_id: int = Field(..., description="目标功能ID")
    order: int = Field(0, description="排序")
    description: Optional[str] = Field(None, max_length=500)


class DataFlowUpdate(BaseModel):
    order: Optional[int] = Field(None, ge=0)
    description: Optional[str] = Field(None, max_length=500)


class DataFlowResponse(BaseModel):
    id: int
    source_function_id: int
    target_function_id: int
    order: int
    description: Optional[str] = None


class FunctionResponse(FunctionBase):
    id: int
    parent_id: Optional[int] = None
    children: List["FunctionResponse"] = []
    responsibility_id: Optional[int] = None
    created_at: datetime


# Relationship Schemas
class ResponsibilityFunctionRelationCreate(BaseModel):
    responsibility_id: int = Field(..., description="责任田ID")
    function_id: int = Field(..., description="功能ID")


class ResponsibilityFunctionRelationResponse(BaseModel):
    id: int
    responsibility_id: int
    function_id: int
    function_name: str


class ResponsibilityFunctionRelationDelete(BaseModel):
    id: int
