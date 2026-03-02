"""Project management API routes."""
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import CurrentUser, CurrentAdmin
from app.schemas.project import (
    VersionCreate, VersionUpdate,
    IterationCreate, IterationUpdate,
    TaskCreate, TaskUpdate,
    TaskDependencyCreate, TaskRelationCreate,
    TaskCompletionCreate,
    TaskAchievementStats
)
from app.schemas.common import APIResponse
from app.services.project_service import project_service

router = APIRouter(prefix="/project", tags=["Project Management"])


# ==================== Version Management ====================
@router.get("/versions", response_model=APIResponse[List])
async def get_versions(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Get all versions."""
    versions = await project_service.get_versions(db)
    return APIResponse[List](
        code=200,
        message="Success",
        data=[{
            "id": v.id,
            "name": v.name,
            "pm_name": v.pm_name,
            "sm_name": v.sm_name,
            "tm_name": v.tm_name,
            "created_at": v.created_at.isoformat() if v.created_at else None
        } for v in versions]
    )


@router.get("/versions/{id}", response_model=APIResponse[dict])
async def get_version(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Get version by ID."""
    version = await project_service.get_version(db, id)
    if not version:
        raise HTTPException(status_code=404, detail=f"版本 {id} 不存在")
    return APIResponse[dict](
        code=200,
        message="Success",
        data={
            "id": version.id,
            "name": version.name,
            "pm_name": version.pm_name,
            "sm_name": version.sm_name,
            "tm_name": version.tm_name,
            "iterations": [{
                "id": i.id,
                "name": i.name,
                "version_id": i.version_id
            } for i in version.iterations]
        }
    )


@router.post("/versions", response_model=APIResponse[dict])
async def create_version(
    schema: VersionCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Create a new version (Admin only)."""
    version = await project_service.create_version(db, schema)
    return APIResponse[dict](
        code=201,
        message="版本创建成功",
        data={"id": version.id, "name": version.name, "pm_name": version.pm_name, "sm_name": version.sm_name, "tm_name": version.tm_name}
    )


@router.put("/versions/{id}", response_model=APIResponse[dict])
async def update_version(
    id: int,
    schema: VersionUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Update version (Admin only)."""
    version = await project_service.update_version(db, id, schema)
    return APIResponse[dict](
        code=200,
        message="版本更新成功",
        data={"id": version.id, "name": version.name, "pm_name": version.pm_name, "sm_name": version.sm_name, "tm_name": version.tm_name}
    )


@router.delete("/versions/{id}", response_model=APIResponse[None])
async def delete_version(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Delete version (Admin only)."""
    await project_service.delete_version(db, id)
    return APIResponse[None](
        code=200,
        message="版本删除成功",
        data=None
    )


# ==================== Iteration Management ====================
@router.get("/iterations", response_model=APIResponse[List])
async def get_iterations(
    version_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Get all iterations."""
    iterations = await project_service.get_iterations(db, version_id=version_id)
    return APIResponse[List](
        code=200,
        message="Success",
        data=[{
            "id": i.id,
            "name": i.name,
            "version_id": i.version_id,
            "version_name": i.version.name if i.version else None,
            "start_date": i.start_date.isoformat() if i.start_date else None,
            "end_date": i.end_date.isoformat() if i.end_date else None,
            "estimated_man_months": i.estimated_man_months
        } for i in iterations]
    )


@router.get("/iterations/{id}", response_model=APIResponse[dict])
async def get_iteration(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Get iteration by ID."""
    iteration = await project_service.get_iteration(db, id)
    if not iteration:
        raise HTTPException(status_code=404, detail=f"迭代 {id} 不存在")
    return APIResponse[dict](
        code=200,
        message="Success",
        data={
            "id": iteration.id,
            "name": iteration.name,
            "version_id": iteration.version_id,
            "start_date": iteration.start_date.isoformat() if iteration.start_date else None,
            "end_date": iteration.end_date.isoformat() if iteration.end_date else None,
            "estimated_man_months": iteration.estimated_man_months
        }
    )


@router.post("/iterations", response_model=APIResponse[dict])
async def create_iteration(
    schema: IterationCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Create a new iteration (Admin only)."""
    iteration = await project_service.create_iteration(db, schema)
    return APIResponse[dict](
        code=201,
        message="迭代创建成功",
        data={"id": iteration.id, "name": iteration.name, "version_id": iteration.version_id}
    )


@router.put("/iterations/{id}", response_model=APIResponse[dict])
async def update_iteration(
    id: int,
    schema: IterationUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Update iteration (Admin only)."""
    iteration = await project_service.update_iteration(db, id, schema)
    return APIResponse[dict](
        code=200,
        message="迭代更新成功",
        data={"id": iteration.id, "name": iteration.name}
    )


@router.delete("/iterations/{id}", response_model=APIResponse[None])
async def delete_iteration(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Delete iteration (Admin only)."""
    await project_service.delete_iteration(db, id)
    return APIResponse[None](
        code=200,
        message="迭代删除成功",
        data=None
    )


@router.post("/iterations/{id}/check-conflicts", response_model=APIResponse[List])
async def check_iteration_conflicts(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Check for conflicts within an iteration."""
    conflicts = await project_service.check_iteration_conflicts(db, id)
    return APIResponse[List](
        code=200,
        message="Success",
        data=conflicts
    )


# ==================== Task Management ====================
@router.get("/tasks", response_model=APIResponse[List])
async def get_tasks(
    iteration_id: Optional[int] = Query(None),
    version_id: Optional[int] = Query(None),
    person_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Get all tasks with optional filters."""
    tasks = await project_service.get_tasks(db, iteration_id=iteration_id, version_id=version_id, person_id=person_id)
    return APIResponse[List](
        code=200,
        message="Success",
        data=[{
            "id": t.id,
            "name": t.name,
            "iteration_id": t.iteration_id,
            "iteration_name": t.iteration.name if t.iteration else None,
            "start_date": t.start_date.isoformat() if t.start_date else None,
            "end_date": t.end_date.isoformat() if t.end_date else None,
            "man_months": t.man_months,
            "status": t.status
        } for t in tasks]
    )


@router.get("/tasks/{id}", response_model=APIResponse[dict])
async def get_task(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Get task by ID."""
    task = await project_service.get_task(db, id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务 {id} 不存在")
    return APIResponse[dict](
        code=200,
        message="Success",
        data={
            "id": task.id,
            "name": task.name,
            "iteration_id": task.iteration_id,
            "start_date": task.start_date.isoformat() if task.start_date else None,
            "end_date": task.end_date.isoformat() if task.end_date else None,
            "man_months": task.man_months,
            "status": task.status,
            "delivery_owner_id": task.delivery_owner_id,
            "delivery_owner_name": task.delivery_owner.name if task.delivery_owner else None,
            "developer_id": task.developer_id,
            "developer_name": task.developer.name if task.developer else None,
            "tester_id": task.tester_id,
            "tester_name": task.tester.name if task.tester else None,
            "design_doc_url": task.design_doc_url
        }
    )


@router.post("/tasks", response_model=APIResponse[dict])
async def create_task(
    schema: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Create a new task (Admin only)."""
    task = await project_service.create_task(db, schema)
    return APIResponse[dict](
        code=201,
        message="任务创建成功",
        data={"id": task.id, "name": task.name}
    )


@router.put("/tasks/{id}", response_model=APIResponse[dict])
async def update_task(
    id: int,
    schema: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Update task (Admin only)."""
    task = await project_service.update_task(db, id, schema)
    return APIResponse[dict](
        code=200,
        message="任务更新成功",
        data={"id": task.id, "name": task.name}
    )


@router.delete("/tasks/{id}", response_model=APIResponse[None])
async def delete_task(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Delete task (Admin only)."""
    await project_service.delete_task(db, id)
    return APIResponse[None](
        code=200,
        message="任务删除成功",
        data=None
    )


@router.post("/tasks/{id}/complete", response_model=APIResponse[dict])
async def mark_task_complete(
    id: int,
    schema: TaskCompletionCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Mark task as complete (Admin only)."""
    task = await project_service.mark_task_complete(db, id, schema)
    return APIResponse[dict](
        code=200,
        message="任务标记完成成功",
        data={"id": task.id, "name": task.name, "status": task.status}
    )


# ==================== Task Dependencies ====================
@router.post("/tasks/{id}/dependencies", response_model=APIResponse[dict])
async def add_task_dependency(
    id: int,
    schema: TaskDependencyCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Add a task dependency (Admin only)."""
    dependency = await project_service.add_task_dependency(db, schema)
    return APIResponse[dict](
        code=201,
        message="任务依赖添加成功",
        data={"id": dependency.id, "task_id": dependency.task_id, "depends_on_id": dependency.depends_on_id}
    )


@router.delete("/tasks/{id}/dependencies/{dep_id}", response_model=APIResponse[None])
async def delete_task_dependency(
    id: int,
    dep_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Delete a task dependency (Admin only)."""
    await project_service.delete_task_dependency(db, id, dep_id)
    return APIResponse[None](
        code=200,
        message="任务依赖删除成功",
        data=None
    )


# ==================== Task Relations ====================
@router.post("/tasks/{id}/relations", response_model=APIResponse[dict])
async def add_task_relation(
    id: int,
    schema: TaskRelationCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Add a task relation (Admin only)."""
    relation = await project_service.add_task_relation(db, schema)
    return APIResponse[dict](
        code=201,
        message="任务关联添加成功",
        data={"id": relation.id, "task_id": relation.task_id, "related_task_id": relation.related_task_id}
    )


@router.delete("/tasks/{id}/relations/{rel_id}", response_model=APIResponse[None])
async def delete_task_relation(
    id: int,
    rel_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Delete a task relation (Admin only)."""
    await project_service.delete_task_relation(db, id, rel_id)
    return APIResponse[None](
        code=200,
        message="任务关联删除成功",
        data=None
    )


# ==================== Task Conflict Check ====================
@router.post("/tasks/{id}/check-conflicts", response_model=APIResponse[List])
async def check_task_conflicts(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Check for task conflicts."""
    conflicts = await project_service.check_task_conflicts(db, id)
    return APIResponse[List](
        code=200,
        message="Success",
        data=conflicts
    )


# ==================== Task Graph Analysis ====================
@router.get("/tasks/graph", response_model=APIResponse[dict])
async def get_task_graph(
    iteration_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Get task dependency graph data."""
    graph = await project_service.get_task_graph(db, iteration_id=iteration_id)
    return APIResponse[dict](
        code=200,
        message="Success",
        data=graph
    )


@router.get("/tasks/longest-path", response_model=APIResponse[List])
async def get_longest_path(
    iteration_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Get longest path in task dependency graph."""
    path = await project_service.get_longest_path(db, iteration_id=iteration_id)
    return APIResponse[List](
        code=200,
        message="Success",
        data=path
    )


@router.get("/tasks/highest-load", response_model=APIResponse[dict])
async def get_highest_load_person(
    iteration_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Get person with highest workload."""
    result = await project_service.get_highest_load_person(db, iteration_id=iteration_id)
    return APIResponse[dict](
        code=200,
        message="Success",
        data=result
    )


# ==================== Gantt Chart ====================
@router.get("/gantt", response_model=APIResponse[List])
async def get_gantt_data(
    iteration_id: Optional[int] = Query(None),
    version_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Get data for Gantt chart."""
    gantt_data = await project_service.get_gantt_data(db, iteration_id=iteration_id, version_id=version_id)
    return APIResponse[List](
        code=200,
        message="Success",
        data=gantt_data
    )


@router.get("/gantt/mermaid", response_model=APIResponse[dict])
async def export_gantt_mermaid(
    iteration_id: Optional[int] = Query(None),
    version_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Export Gantt chart as Mermaid."""
    mermaid = await project_service.export_gantt_mermaid(db, iteration_id=iteration_id, version_id=version_id)
    return APIResponse[dict](
        code=200,
        message="Success",
        data={"mermaid": mermaid}
    )


# ==================== Achievement Statistics ====================
@router.get("/achievement", response_model=APIResponse[List])
async def get_achievement_stats(
    version_ids: Optional[str] = Query(None, description="版本ID列表，逗号分隔"),
    iteration_ids: Optional[str] = Query(None, description="迭代ID列表，逗号分隔"),
    person_ids: Optional[str] = Query(None, description="人员ID列表，逗号分隔"),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Get task achievement statistics."""
    version_id_list = [int(v) for v in version_ids.split(",")] if version_ids else None
    iteration_id_list = [int(i) for i in iteration_ids.split(",")] if iteration_ids else None
    person_id_list = [int(p) for p in person_ids.split(",")] if person_ids else None

    stats = await project_service.get_achievement_stats(
        db,
        version_ids=version_id_list,
        iteration_ids=iteration_id_list,
        person_ids=person_id_list
    )
    return APIResponse[List](
        code=200,
        message="Success",
        data=[s.model_dump() for s in stats]
    )
