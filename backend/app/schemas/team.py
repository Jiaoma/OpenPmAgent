from __future__ import annotations

"""Team management Pydantic schemas."""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import date


# Capability Schemas
class CapabilityDimensionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="维度名称")
    description: Optional[str] = Field(None, max_length=500, description="维度描述")
    is_active: bool = Field(True, description="是否启用")


class CapabilityDimensionCreate(CapabilityDimensionBase):
    pass


class CapabilityDimensionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = Field(None)


class CapabilityDimensionResponse(CapabilityDimensionBase):
    id: int
    created_at: str


class CapabilityBase(BaseModel):
    person_id: int = Field(..., description="人员ID")
    dimension: str = Field(..., min_length=1, max_length=100)
    level: int = Field(..., ge=1, le=5, description="能力等级 1-5")


class CapabilityCreate(BaseModel):
    capabilities: List[CapabilityBase]


class CapabilityUpdate(BaseModel):
    level: Optional[int] = Field(None, ge=1, le=5)


class CapabilityResponse(CapabilityBase):
    id: int
    person_id: int
    dimension: str
    level: int
    created_at: str


# Person Schemas
class PersonBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    emp_id: str = Field(..., min_length=1, max_length=50, pattern=r'^[A-Za-z0-9_]+$')
    email: str
    group_id: Optional[int] = Field(None, description="小组ID")
    role: str = Field(..., max_length=100)


class PersonCreate(PersonBase):
    capabilities: List[CapabilityBase]


class PersonUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    emp_id: Optional[str] = Field(None, min_length=1, max_length=50, pattern=r'^[A-Za-z0-9_]+$')
    email: Optional[str] = None
    group_id: Optional[int] = Field(None)
    role: Optional[str] = Field(None, max_length=100)
    capabilities: Optional[List[CapabilityBase]] = None


class PersonResponse(PersonBase):
    id: int
    group: Optional[GroupResponse] = None
    capabilities: List[CapabilityResponse] = []
    responsibilities: List[ResponsibilityResponse] = []
    created_at: str


# Key Figure Schemas
class KeyFigureCreate(BaseModel):
    group_id: int
    type: str = Field(..., min_length=1, max_length=50)
    person_id: int


class KeyFigureResponse(BaseModel):
    id: int
    group_id: int
    type: str
    person_id: int
    person: Optional[PersonResponse] = None
    created_at: str


# Group Schemas
class GroupBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    leader_id: int


class GroupCreate(GroupBase):
    pass


class GroupUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    leader_id: Optional[int] = None


class GroupResponse(GroupBase):
    id: int
    leader: Optional[PersonResponse] = None
    members: List[PersonResponse] = []
    responsibilities: List[ResponsibilityResponse] = []
    key_figures: List[KeyFigureResponse] = []
    created_at: str


# Responsibility Schemas
class ResponsibilityBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    group_id: int = Field(..., description="小组ID")
    owner_id: int
    backup_id: Optional[int] = None
    current_year_tasks: Optional[List[int]] = None


class ResponsibilityCreate(ResponsibilityBase):
    pass


class ResponsibilityUpdate(BaseModel):
    name: Optional[str] = None
    group_id: Optional[int] = None
    owner_id: Optional[int] = None
    backup_id: Optional[int] = None
    current_year_tasks: Optional[List[int]] = None


class ResponsibilityResponse(ResponsibilityBase):
    id: int
    group: GroupResponse
    owner: PersonResponse
    backup: Optional[PersonResponse] = None
    # Use function_ids instead of FunctionResponse to avoid cross-module circular dependency
    function_ids: List[int] = []
    created_at: str


# Workload Schemas
class WorkloadPersonResponse(BaseModel):
    person_id: int
    person_name: str
    workload: float
    task_count: int
    # Use task_ids instead of TaskResponse to avoid cross-module circular dependency
    task_ids: List[int] = []


class WorkloadGroupResponse(BaseModel):
    group_id: int
    group_name: str
    workload: float
    member_workloads: List[WorkloadPersonResponse]
    forecast: List[dict]  # [{date: date, workload: float}]


class WorkloadMonthlySummary(BaseModel):
    total_workload: float
    avg_workload: float
    highest_load: dict  # {name: string, workload: float}


# Capability Radar Schemas
class CapabilityRadarResponse(BaseModel):
    person_id: Optional[int] = None
    dimensions: List[str]  # 能力维度列表
    capabilities: dict  # {person_id: {dimension: level, ...}, ...}
    team_id: Optional[int] = None  # 小组ID（用于小组能力统计）
