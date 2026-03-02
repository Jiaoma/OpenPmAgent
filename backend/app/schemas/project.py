from __future__ import annotations

"""Project management Pydantic schemas."""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import date


# Version Schemas
class VersionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="版本名称")
    pm_name: str = Field(..., min_length=1, max_length=100, description="项目经理姓名")
    sm_name: str = Field(..., min_length=1, max_length=100, description="软件经理姓名")
    tm_name: str = Field(..., min_length=1, max_length=100, description="测试经理姓名")


class VersionCreate(VersionBase):
    pass


class VersionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    pm_name: Optional[str] = None
    sm_name: Optional[str] = None
    tm_name: Optional[str] = None


class VersionResponse(VersionBase):
    id: int
    created_at: str


# Iteration Schemas
class IterationBase(BaseModel):
    version_id: int = Field(..., description="版本ID")
    name: str = Field(..., min_length=1, max_length=100, description="迭代名称")
    start_date: date
    end_date: date
    estimated_man_months: float = Field(..., ge=0, description="预计工作量（人月）")


class IterationCreate(IterationBase):
    pass


class IterationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    estimated_man_months: Optional[float] = Field(None, ge=0)


class IterationResponse(IterationBase):
    id: int
    created_at: str


# Task Schemas
class TaskBase(BaseModel):
    iteration_id: int = Field(..., description="迭代ID")
    name: str = Field(..., min_length=1, max_length=200, description="任务名称")
    start_date: date
    end_date: date
    man_months: float = Field(..., ge=0, description="工作量（人月）")
    status: str = Field("pending", pattern="^(pending|in_progress|completed)$", description="任务状态")


class TaskCreate(TaskBase):
    delivery_owner_id: int = Field(..., description="交付责任人ID")
    developer_id: int = Field(..., description="开发责任人ID")
    tester_id: int = Field(..., description="测试人员ID")
    design_doc_url: Optional[str] = Field(None, max_length=500, description="设计文档URL")


class TaskUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    man_months: Optional[float] = Field(None, ge=0)
    status: Optional[str] = Field(None, pattern="^(pending|in_progress|completed)$")
    delivery_owner_id: Optional[int] = None
    developer_id: Optional[int] = None
    tester_id: Optional[int] = None
    design_doc_url: Optional[str] = None


class TaskResponse(TaskBase):
    id: int
    iteration_id: int
    iteration: Optional[IterationResponse] = None
    # Use person IDs instead of PersonResponse to avoid cross-module circular dependency
    delivery_owner_id: int
    developer_id: int
    tester_id: int
    design_doc_url: Optional[str] = None
    created_at: str


# Task Dependency Schemas
class TaskDependencyBase(BaseModel):
    task_id: int = Field(..., description="任务ID")
    depends_on_id: int = Field(..., description="依赖的任务ID")
    type: str = Field(
        "finish_to_start",
        pattern="^(finish_to_start|start_to_start|finish_to_finish|start_to_finish)$",
        description="依赖关系类型"
    )


class TaskDependencyCreate(TaskDependencyBase):
    pass


class TaskRelationBase(BaseModel):
    task_id: int = Field(..., description="任务ID")
    related_task_id: int = Field(..., description="关联的任务ID")


class TaskRelationCreate(TaskRelationBase):
    pass


class TaskCompletionBase(BaseModel):
    task_id: int = Field(..., description="任务ID")
    actual_end_date: str = Field(..., description="实际完成时间")
    completion_status: str = Field(
        "early|on_time|slightly_late|severely_late",
        description="完成状态"
    )


class TaskCompletionCreate(TaskCompletionBase):
    pass


# Achievement Schemas
class TaskAchievementStats(BaseModel):
    person_id: int
    person_name: str
    person_role: str
    total_tasks: int
    completed: int
    failed: int
    early: int
    on_time: int
    slightly_late: int
    severely_late: int


class AchievementExportRequest(BaseModel):
    version_ids: List[int] = Field(..., description="版本ID列表")
    iteration_ids: List[int] = Field(..., description="迭代ID列表")
    person_ids: Optional[List[int]] = Field(None, description="人员ID列表（可选，空表示全部）")
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class AchievementExportResponse(BaseModel):
    file_path: str
    file_name: str
    created_at: str
