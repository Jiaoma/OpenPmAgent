"""Architecture management API routes."""
from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import CurrentUser, CurrentAdmin
from app.schemas.architecture import (
    ModuleCreate, ModuleUpdate, ModuleMove, ModuleResponse,
    FunctionCreate, FunctionUpdate, FunctionMove, FunctionModuleCreate, FunctionModuleResponse,
    DataFlowCreate, DataFlowResponse, DataFlowUpdate,
    ResponsibilityFunctionRelationCreate, ResponsibilityFunctionRelationDelete
)
from app.schemas.common import APIResponse
from app.services.architecture_service import architecture_service

router = APIRouter(prefix="/architecture", tags=["Architecture Management"])

@router.get("/modules", response_model=APIResponse[List[ModuleResponse]])
async def get_modules(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Get all modules as a tree."""
    modules = await architecture_service.get_modules(db)
    return APIResponse[List](
        code=200,
        message="Success",
        data=modules
    )


@router.get("/modules/{id}", response_model=APIResponse[ModuleResponse])
async def get_module(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Get module by ID."""
    module = await architecture_service.get_module(db, id)
    if not module:
        raise HTTPException(status_code=404, detail=f"模块 {id} 不存在")
    return APIResponse[ModuleResponse](
        code=200,
        message="Success",
        data=ModuleResponse.model_validate(module)
    )


@router.post("/modules", response_model=APIResponse[ModuleResponse])
async def create_module(
    schema: ModuleCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Create a new module (Admin only)."""
    module = await architecture_service.create_module(db, schema)
    return APIResponse[ModuleResponse](
        code=201,
        message="模块创建成功",
        data=ModuleResponse.model_validate(module)
    )


@router.put("/modules/{id}", response_model=APIResponse[ModuleResponse])
async def update_module(
    id: int,
    schema: ModuleUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Update module (Admin only)."""
    module = await architecture_service.update_module(db, id, schema)
    return APIResponse[ModuleResponse](
        code=200,
        message="模块更新成功",
        data=ModuleResponse.model_validate(module)
    )


@router.delete("/modules/{id}", response_model=APIResponse[None])
async def delete_module(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Delete module (Admin only)."""
    await architecture_service.delete_module(db, id)
    return APIResponse[None](
        code=200,
        message="模块删除成功",
        data=None
    )


@router.post("/modules/{id}/move", response_model=APIResponse[ModuleResponse])
async def move_module(
    id: int,
    schema: ModuleMove,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Move module to a new parent (drag and drop, Admin only)."""
    module = await architecture_service.move_module(db, id, schema)
    return APIResponse[ModuleResponse](
        code=200,
        message="模块移动成功",
        data=ModuleResponse.model_validate(module)
    )


@router.get("/modules/mermaid", response_model=APIResponse[dict])
async def export_modules_mermaid(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Export modules as Mermaid flowchart."""
    mermaid = await architecture_service.export_modules_mermaid(db)
    return APIResponse[dict](
        code=200,
        message="Success",
        data={"mermaid": mermaid}
    )


# ==================== Function Management ====================
@router.get("/functions", response_model=APIResponse[List])
async def get_functions(
    responsibility_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Get all functions as a tree."""
    functions = await architecture_service.get_functions(db, responsibility_id=responsibility_id)
    return APIResponse[List](
        code=200,
        message="Success",
        data=[{
            "id": f.id,
            "name": f.name,
            "parent_id": f.parent_id,
            "responsibility_id": f.responsibility_id,
            "responsibility_name": f.responsibility.name if f.responsibility else None
        } for f in functions]
    )


@router.get("/functions/{id}", response_model=APIResponse[dict])
async def get_function(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Get function by ID."""
    function = await architecture_service.get_function(db, id)
    if not function:
        raise HTTPException(status_code=404, detail=f"功能 {id} 不存在")
    return APIResponse[dict](
        code=200,
        message="Success",
        data={
            "id": function.id,
            "name": function.name,
            "parent_id": function.parent_id,
            "responsibility_id": function.responsibility_id,
            "responsibility_name": function.responsibility.name if function.responsibility else None,
        }
    )


@router.post("/functions", response_model=APIResponse[dict])
async def create_function(
    schema: FunctionCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Create a new function (Admin only)."""
    function = await architecture_service.create_function(db, schema)
    return APIResponse[dict](
        code=201,
        message="功能创建成功",
        data={"id": function.id, "name": function.name}
    )


@router.put("/functions/{id}", response_model=APIResponse[dict])
async def update_function(
    id: int,
    schema: FunctionUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Update function (Admin only)."""
    function = await architecture_service.update_function(db, id, schema)
    return APIResponse[dict](
        code=200,
        message="功能更新成功",
        data={"id": function.id, "name": function.name}
    )


@router.delete("/functions/{id}", response_model=APIResponse[None])
async def delete_function(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Delete function (Admin only)."""
    await architecture_service.delete_function(db, id)
    return APIResponse[None](
        code=200,
        message="功能删除成功",
        data=None
    )


@router.post("/functions/{id}/move", response_model=APIResponse[dict])
async def move_function(
    id: int,
    schema: FunctionMove,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Move function to a new parent (drag and drop, Admin only)."""
    function = await architecture_service.move_function(db, id, schema)
    return APIResponse[dict](
        code=200,
        message="功能移动成功",
        data={"id": function.id, "name": function.name}
    )


@router.get("/functions/{id}/modules", response_model=APIResponse[List[FunctionModuleResponse]])
async def get_function_modules(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Get modules associated with a function."""
    modules = await architecture_service.get_function_modules(db, id)
    return APIResponse[List[FunctionModuleResponse]](
        code=200,
        message="Success",
        data=[FunctionModuleResponse.model_validate(m) for m in modules]
    )


@router.post("/functions/{id}/modules", response_model=APIResponse[List[FunctionModuleResponse]])
async def update_function_modules(
    id: int,
    modules: List[FunctionModuleCreate],
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Update function-module associations (Admin only)."""
    result = await architecture_service.update_function_modules(db, id, modules)
    return APIResponse[List[FunctionModuleResponse]](
        code=200,
        message="功能模块关联更新成功",
        data=[FunctionModuleResponse.model_validate(m) for m in result]
    )


@router.get("/functions/{id}/data-flows", response_model=APIResponse[List[DataFlowResponse]])
async def get_function_data_flows(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Get data flows for a function."""
    flows = await architecture_service.get_function_data_flows(db, id)
    return APIResponse[List[DataFlowResponse]](
        code=200,
        message="Success",
        data=[DataFlowResponse.model_validate(f) for f in flows]
    )


@router.post("/functions/{id}/data-flows", response_model=APIResponse[List[DataFlowResponse]])
async def update_function_data_flows(
    id: int,
    flows: List[DataFlowCreate],
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Update function data flows (Admin only)."""
    result = await architecture_service.update_function_data_flows(db, id, flows)
    return APIResponse[List[DataFlowResponse]](
        code=200,
        message="数据流更新成功",
        data=[DataFlowResponse.model_validate(f) for f in result]
    )


@router.get("/functions/mermaid", response_model=APIResponse[dict])
async def export_functions_mermaid(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Export functions as Mermaid flowchart."""
    mermaid = await architecture_service.export_functions_mermaid(db)
    return APIResponse[dict](
        code=200,
        message="Success",
        data={"mermaid": mermaid}
    )


# ==================== Architecture Relations ====================
@router.get("/relations/responsibility-functions", response_model=APIResponse[List])
async def get_responsibility_function_relations(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """Get all responsibility-function relations."""
    relations = await architecture_service.get_responsibility_function_relations(db)
    return APIResponse[List](
        code=200,
        message="Success",
        data=relations
    )


@router.post("/relations/responsibility-functions", response_model=APIResponse[dict])
async def create_responsibility_function_relation(
    schema: ResponsibilityFunctionRelationCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Create responsibility-function relation (Admin only)."""
    function = await architecture_service.create_responsibility_function_relation(db, schema)
    return APIResponse[dict](
        code=201,
        message="责任田-功能关联创建成功",
        data={"id": function.id, "name": function.name}
    )


@router.delete("/relations/responsibility-functions/{id}", response_model=APIResponse[None])
async def delete_responsibility_function_relation(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    """Delete responsibility-function relation (Admin only)."""
    from app.schemas.architecture import ResponsibilityFunctionRelationDelete
    schema = ResponsibilityFunctionRelationDelete(id=id)
    await architecture_service.delete_responsibility_function_relation(db, schema)
    return APIResponse[None](
        code=200,
        message="责任田-功能关联删除成功",
        data=None
    )
