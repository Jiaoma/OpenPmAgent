"""Team management API routes."""
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import CurrentUser, CurrentAdmin
from app.schemas.team import (
    PersonCreate, PersonUpdate, PersonResponse,
    CapabilityDimensionCreate, CapabilityDimensionUpdate,
    GroupCreate, GroupUpdate, GroupResponse,
    ResponsibilityCreate, ResponsibilityUpdate, ResponsibilityResponse,
    CapabilityCreate, CapabilityUpdate,
    KeyFigureCreate, KeyFigureResponse,
    WorkloadPersonResponse, WorkloadGroupResponse, WorkloadMonthlySummary
)
from app.schemas.common import APIResponse, PaginatedResponse, PaginatedData
from app.services.team_service import team_service
from app.services.team_service import export_achievement_to_excel

router = APIRouter(prefix="/team", tags=["Team Management"])


# ==================== Person Management ====================
@router.get("/persons", response_model=APIResponse[List[PersonResponse]])
async def get_persons(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Get all persons with pagination and search."""
    persons = await team_service.get_persons(db, skip=skip, limit=limit, search=search)
    return APIResponse[List[PersonResponse]](
        code=200,
        message="Success",
        data=[PersonResponse.model_validate(p) for p in persons]
    )


@router.get("/persons/{id}", response_model=APIResponse[PersonResponse])
async def get_person(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Get person by ID."""
    person = await team_service.get_person(db, id)
    if not person:
        raise HTTPException(status_code=404, detail=f"人员 {id} 不存在")
    return APIResponse[PersonResponse](
        code=200,
        message="Success",
        data=PersonResponse.model_validate(person)
    )


@router.post("/persons", response_model=APIResponse[PersonResponse])
async def create_person(
    schema: PersonCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Create a new person (Admin only)."""
    person = await team_service.create_person(db, schema)
    return APIResponse[PersonResponse](
        code=201,
        message="人员创建成功",
        data=PersonResponse.model_validate(person)
    )


@router.put("/persons/{id}", response_model=APIResponse[PersonResponse])
async def update_person(
    id: int,
    schema: PersonUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Update person (Admin only)."""
    person = await team_service.update_person(db, id, schema)
    return APIResponse[PersonResponse](
        code=200,
        message="人员更新成功",
        data=PersonResponse.model_validate(person)
    )


@router.delete("/persons/{id}", response_model=APIResponse[None])
async def delete_person(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Delete person (Admin only)."""
    await team_service.delete_person(db, id)
    return APIResponse[None](
        code=200,
        message="人员删除成功",
        data=None
    )


# ==================== Capability Management ====================
@router.get("/capability-dimensions", response_model=APIResponse[List])
async def get_capability_dimensions(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Get all capability dimensions."""
    dimensions = await team_service.get_capability_dimensions(db, current_user.is_admin)
    return APIResponse[List](
        code=200,
        message="Success",
        data=[{"id": d.id, "name": d.name, "description": d.description, "is_active": d.is_active} for d in dimensions]
    )


@router.post("/capability-dimensions", response_model=APIResponse[dict])
async def create_capability_dimension(
    schema: CapabilityDimensionCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Create capability dimension (Admin only)."""
    dimension = await team_service.create_capability_dimension(db, schema)
    return APIResponse[dict](
        code=201,
        message="能力维度创建成功",
        data={"id": dimension.id, "name": dimension.name, "description": dimension.description, "is_active": dimension.is_active}
    )


@router.put("/capability-dimensions/{id}", response_model=APIResponse[dict])
async def update_capability_dimension(
    id: int,
    schema: CapabilityDimensionUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Update capability dimension (Admin only)."""
    dimension = await team_service.update_capability_dimension(db, id, schema)
    return APIResponse[dict](
        code=200,
        message="能力维度更新成功",
        data={"id": dimension.id, "name": dimension.name, "description": dimension.description, "is_active": dimension.is_active}
    )


@router.delete("/capability-dimensions/{id}", response_model=APIResponse[None])
async def delete_capability_dimension(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Delete capability dimension (Admin only)."""
    await team_service.delete_capability_dimension(db, id)
    return APIResponse[None](
        code=200,
        message="能力维度删除成功",
        data=None
    )


@router.get("/persons/{id}/capabilities", response_model=APIResponse[List])
async def get_person_capabilities(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Get person capabilities."""
    capabilities = await team_service.get_person_capabilities(db, id)
    return APIResponse[List](
        code=200,
        message="Success",
        data=capabilities
    )


@router.put("/persons/{id}/capabilities", response_model=APIResponse[List])
async def update_person_capabilities(
    id: int,
    capabilities: List[CapabilityCreate],
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Update person capabilities (Admin only)."""
    result = await team_service.update_person_capabilities(db, id, capabilities)
    return APIResponse[List](
        code=200,
        message="能力模型更新成功",
        data=[{"dimension": cap.dimension, "level": cap.level, "description": cap.description} for cap in result]
    )


# ==================== Group Management ====================
@router.get("/groups", response_model=APIResponse[List[GroupResponse]])
async def get_groups(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Get all groups."""
    groups = await team_service.get_groups(db, skip=skip, limit=limit)
    return APIResponse[List[GroupResponse]](
        code=200,
        message="Success",
        data=[GroupResponse.model_validate(g) for g in groups]
    )


@router.get("/groups/{id}", response_model=APIResponse[GroupResponse])
async def get_group(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Get group by ID."""
    group = await team_service.get_group(db, id)
    if not group:
        raise HTTPException(status_code=404, detail=f"小组 {id} 不存在")
    return APIResponse[GroupResponse](
        code=200,
        message="Success",
        data=GroupResponse.model_validate(group)
    )


@router.post("/groups", response_model=APIResponse[GroupResponse])
async def create_group(
    schema: GroupCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Create a new group (Admin only)."""
    group = await team_service.create_group(db, schema)
    return APIResponse[GroupResponse](
        code=201,
        message="小组创建成功",
        data=GroupResponse.model_validate(group)
    )


@router.put("/groups/{id}", response_model=APIResponse[GroupResponse])
async def update_group(
    id: int,
    schema: GroupUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Update group (Admin only)."""
    group = await team_service.update_group(db, id, schema)
    return APIResponse[GroupResponse](
        code=200,
        message="小组更新成功",
        data=GroupResponse.model_validate(group)
    )


@router.delete("/groups/{id}", response_model=APIResponse[None])
async def delete_group(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Delete group (Admin only)."""
    await team_service.delete_group(db, id)
    return APIResponse[None](
        code=200,
        message="小组删除成功",
        data=None
    )


# ==================== Responsibility Management ====================
@router.get("/responsibilities", response_model=APIResponse[List[ResponsibilityResponse]])
async def get_responsibilities(
    group_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Get all responsibilities."""
    responsibilities = await team_service.get_responsibilities(db, group_id=group_id, skip=skip, limit=limit)
    return APIResponse[List[ResponsibilityResponse]](
        code=200,
        message="Success",
        data=[ResponsibilityResponse.model_validate(r) for r in responsibilities]
    )


@router.post("/responsibilities", response_model=APIResponse[ResponsibilityResponse])
async def create_responsibility(
    schema: ResponsibilityCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Create a new responsibility (Admin only)."""
    responsibility = await team_service.create_responsibility(db, schema)
    return APIResponse[ResponsibilityResponse](
        code=201,
        message="责任田创建成功",
        data=ResponsibilityResponse.model_validate(responsibility)
    )


@router.put("/responsibilities/{id}", response_model=APIResponse[ResponsibilityResponse])
async def update_responsibility(
    id: int,
    schema: ResponsibilityUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Update responsibility (Admin only)."""
    responsibility = await team_service.update_responsibility(db, id, schema)
    return APIResponse[ResponsibilityResponse](
        code=200,
        message="责任田更新成功",
        data=ResponsibilityResponse.model_validate(responsibility)
    )


@router.delete("/responsibilities/{id}", response_model=APIResponse[None])
async def delete_responsibility(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Delete responsibility (Admin only)."""
    await team_service.delete_responsibility(db, id)
    return APIResponse[None](
        code=200,
        message="责任田删除成功",
        data=None
    )


# ==================== Key Figures ====================
@router.get("/groups/{id}/key-figures", response_model=APIResponse[List])
async def get_group_key_figures(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Get all key figures for a group."""
    key_figures = await team_service.get_group_key_figures(db, id)
    return APIResponse[List](
        code=200,
        message="Success",
        data=[{
            "id": kf.id,
            "type": kf.type,
            "person_id": kf.person_id,
            "person_name": kf.person.name if kf.person else None
        } for kf in key_figures]
    )


@router.post("/groups/{id}/key-figures", response_model=APIResponse[dict])
async def create_key_figure(
    id: int,
    schema: KeyFigureCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Create a key figure for a group (Admin only)."""
    key_figure = await team_service.create_key_figure(db, id, schema)
    return APIResponse[dict](
        code=201,
        message="关键人物添加成功",
        data={"id": key_figure.id, "type": key_figure.type}
    )


@router.delete("/groups/{id}/key-figures/{kf_id}", response_model=APIResponse[None])
async def delete_key_figure(
    id: int,
    kf_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Delete a key figure (Admin only)."""
    await team_service.delete_key_figure(db, id, kf_id)
    return APIResponse[None](
        code=200,
        message="关键人物删除成功",
        data=None
    )


# ==================== Workload Analysis ====================
@router.get("/workload/person/{id}", response_model=APIResponse[WorkloadPersonResponse])
async def get_person_workload(
    id: int,
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Get person workload for a date range."""
    workload = await team_service.get_person_workload(db, id, start_date, end_date)
    return APIResponse[WorkloadPersonResponse](
        code=200,
        message="Success",
        data=workload
    )


@router.get("/workload/group/{id}", response_model=APIResponse[WorkloadGroupResponse])
async def get_group_workload(
    id: int,
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Get group workload for a date range."""
    workload = await team_service.get_group_workload(db, id, start_date, end_date)
    return APIResponse[WorkloadGroupResponse](
        code=200,
        message="Success",
        data=workload
    )


    @router.get("/workload/monthly-summary", response_model=APIResponse[WorkloadMonthlySummary])
    async def get_monthly_workload_summary(
        month: int = Query(..., ge=1, le=12, description="月份"),
        year: int = Query(..., ge=2020, description="年份"),
        db: AsyncSession = Depends(get_db),
        current_user: CurrentUser = None
    ):
        """Get monthly workload summary."""
        summary = await team_service.get_monthly_workload_summary(db, month, year)
        return APIResponse[WorkloadMonthlySummary](
            code=200,
            message="Success",
            data=summary
        )


# ==================== Team Structure Graph ====================
@router.get("/graph/team-structure", response_model=APIResponse[dict])
async def get_team_structure_graph(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Get team structure graph data."""
    graph = await team_service.get_team_structure_graph(db)
    return APIResponse[dict](
        code=200,
        message="Success",
        data=graph
    )


# ==================== Capability Radar ====================
@router.get("/radar/capability/person/{id}", response_model=APIResponse[dict])
async def get_person_capability_radar(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Get person capability data for radar chart."""
    radar_data = await team_service.get_person_capability_radar(db, id)
    return APIResponse[dict](
        code=200,
        message="Success",
        data=radar_data
    )


@router.get("/radar/capability/group/{id}", response_model=APIResponse[dict])
async def get_group_capability_radar(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Get group capability data for radar chart."""
    radar_data = await team_service.get_group_capability_radar(db, id)
    return APIResponse[dict](
        code=200,
        message="Success",
        data=radar_data
    )


# ==================== Export ====================
@router.get("/achievement/export")
async def export_achievement_excel(
    version_ids: Optional[str] = Query(None, description="版本ID列表，逗号分隔"),
    iteration_ids: Optional[str] = Query(None, description="迭代ID列表，逗号分隔"),
    person_ids: Optional[str] = Query(None, description="人员ID列表，逗号分隔"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Export achievement statistics to Excel."""
    version_id_list = [int(v) for v in version_ids.split(",")] if version_ids else None
    iteration_id_list = [int(i) for i in iteration_ids.split(",")] if iteration_ids else None
    person_id_list = [int(p) for p in person_ids.split(",")] if person_ids else None

    excel_bytes = await export_achievement_to_excel(
        db,
        version_ids=version_id_list,
        iteration_ids=iteration_id_list,
        person_ids=person_id_list,
        start_date=start_date,
        end_date=end_date
    )

    return StreamingResponse(
        content=iter([excel_bytes]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=task_achievement.xlsx"}
    )
