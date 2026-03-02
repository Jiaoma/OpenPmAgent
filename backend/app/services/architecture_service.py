"""Architecture management business logic."""
from typing import List, Optional, Dict
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.architecture import (
    Module, Function, FunctionModule, DataFlow
)
from app.models.team import Responsibility
from app.schemas.architecture import (
    ModuleCreate, ModuleUpdate, ModuleMove,
    FunctionCreate, FunctionUpdate, FunctionMove,
    FunctionModuleCreate,
    DataFlowCreate, DataFlowUpdate,
    ResponsibilityFunctionRelationCreate, ResponsibilityFunctionRelationDelete
)


class ArchitectureService:
    """Architecture management service."""

    # Module Management
    async def get_modules(
        self, db: AsyncSession
    ) -> List[Module]:
        """Get all modules as a tree."""
        # Get all modules with parent and children
        result = await db.execute(
            select(Module)
            .options(selectinload(Module.parent), selectinload(Module.children))
            .order_by(Module.id)
        )
        return result.scalars().all()

    async def get_module(
        self, db: AsyncSession, id: int
    ) -> Optional[Module]:
        """Get module by ID."""
        result = await db.execute(
            select(Module)
            .options(
                selectinload(Module.parent),
                selectinload(Module.children),
                selectinload(Module.function_modules).selectinload(FunctionModule.function)
            )
            .where(Module.id == id)
        )
        return result.scalar_one_or_none()

    async def create_module(
        self, db: AsyncSession, schema: ModuleCreate
    ) -> Module:
        """Create a module."""
        # Verify parent exists if provided
        if schema.parent_id:
            parent = await db.get(Module, schema.parent_id)
            if not parent:
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=404,
                    detail=f"父模块 {schema.parent_id} 不存在"
                )

        db_module = Module(**schema.model_dump())
        db.add(db_module)
        await db.commit()
        await db.refresh(db_module)
        return db_module

    async def update_module(
        self, db: AsyncSession, id: int, schema: ModuleUpdate
    ) -> Module:
        """Update a module."""
        db_module = await db.get(Module, id)
        if not db_module:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=404,
                detail=f"模块 {id} 不存在"
            )

        # Verify parent exists if provided
        if schema.parent_id is not None:
            # Prevent moving to self or descendants
            if schema.parent_id == id:
                raise HTTPException(
                    status_code=400,
                    detail="不能将模块移动到自身"
                )

            parent = await db.get(Module, schema.parent_id)
            if not parent:
                raise HTTPException(
                    status_code=404,
                    detail=f"父模块 {schema.parent_id} 不存在"
                )

        update_data = schema.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_module, field, value)

        await db.commit()
        await db.refresh(db_module)
        return db_module

    async def move_module(
        self, db: AsyncSession, id: int, schema: ModuleMove
    ) -> Module:
        """Move a module to a new parent (drag and drop)."""
        db_module = await db.get(Module, id)
        if not db_module:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=404,
                detail=f"模块 {id} 不存在"
            )

        # Verify parent exists
        parent = await db.get(Module, schema.parent_id)
        if not parent:
            raise HTTPException(
                status_code=404,
                detail=f"父模块 {schema.parent_id} 不存在"
            )

        # Prevent moving to self or descendants
        if schema.parent_id == id:
            raise HTTPException(
                status_code=400,
                detail="不能将模块移动到自身"
            )

        # Check if new parent is a descendant (would create cycle)
        current_parent = parent
        while current_parent.parent_id is not None:
            if current_parent.parent_id == id:
                raise HTTPException(
                    status_code=400,
                    detail="不能将模块移动到其子节点"
                )
            current_parent = await db.get(Module, current_parent.parent_id)

        db_module.parent_id = schema.parent_id
        await db.commit()
        await db.refresh(db_module)
        return db_module

    async def delete_module(
        self, db: AsyncSession, id: int
    ) -> bool:
        """Delete a module."""
        db_module = await db.get(Module, id)
        if not db_module:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=404,
                detail=f"模块 {id} 不存在"
            )

        # Cascade delete will handle children and function_modules
        await db.delete(db_module)
        await db.commit()
        return True

    async def export_modules_mermaid(
        self, db: AsyncSession
    ) -> str:
        """Export modules as Mermaid flowchart."""
        modules = await self.get_modules(db)

        # Build tree structure
        module_map = {m.id: m for m in modules}
        root_modules = [m for m in modules if m.parent_id is None]

        def build_mermaid_tree(module, level=0):
            indent = "  " * level
            lines = []
            lines.append(f"{indent}{module.name}")
            for child in sorted(module.children, key=lambda x: x.name):
                lines.extend(build_mermaid_tree(child, level + 1))
            return lines

        lines = ["graph TD"]
        for root in sorted(root_modules, key=lambda x: x.name):
            lines.extend(build_mermaid_tree(root, 1))

        return "\n".join(lines)

    # Function Management
    async def get_functions(
        self, db: AsyncSession, responsibility_id: Optional[int] = None
    ) -> List[Function]:
        """Get all functions as a tree."""
        query = select(Function).options(
            selectinload(Function.parent),
            selectinload(Function.children),
            selectinload(Function.responsibility)
        )

        if responsibility_id:
            query = query.where(Function.responsibility_id == responsibility_id)

        result = await db.execute(query.order_by(Function.id))
        return result.scalars().all()

    async def get_function(
        self, db: AsyncSession, id: int
    ) -> Optional[Function]:
        """Get function by ID."""
        result = await db.execute(
            select(Function)
            .options(
                selectinload(Function.parent),
                selectinload(Function.children),
                selectinload(Function.responsibility),
                selectinload(Function.function_modules).selectinload(FunctionModule.module),
                selectinload(Function.source_flows).selectinload(DataFlow.target_function),
                selectinload(Function.target_flows).selectinload(DataFlow.source_function)
            )
            .where(Function.id == id)
        )
        return result.scalar_one_or_none()

    async def create_function(
        self, db: AsyncSession, schema: FunctionCreate
    ) -> Function:
        """Create a function."""
        # Verify parent exists if provided
        if schema.parent_id:
            parent = await db.get(Function, schema.parent_id)
            if not parent:
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=404,
                    detail=f"父功能 {schema.parent_id} 不存在"
                )

        # Verify responsibility exists if provided
        if schema.responsibility_id:
            resp = await db.get(Responsibility, schema.responsibility_id)
            if not resp:
                raise HTTPException(
                    status_code=404,
                    detail=f"责任田 {schema.responsibility_id} 不存在"
                )

        db_function = Function(**schema.model_dump())
        db.add(db_function)
        await db.commit()
        await db.refresh(db_function)
        return db_function

    async def update_function(
        self, db: AsyncSession, id: int, schema: FunctionUpdate
    ) -> Function:
        """Update a function."""
        db_function = await db.get(Function, id)
        if not db_function:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=404,
                detail=f"功能 {id} 不存在"
            )

        # Verify parent exists if provided
        if schema.parent_id is not None:
            # Prevent moving to self or descendants
            if schema.parent_id == id:
                raise HTTPException(
                    status_code=400,
                    detail="不能将功能移动到自身"
                )

            parent = await db.get(Function, schema.parent_id)
            if not parent:
                raise HTTPException(
                    status_code=404,
                    detail=f"父功能 {schema.parent_id} 不存在"
                )

        # Verify responsibility exists if provided
        if schema.responsibility_id is not None:
            resp = await db.get(Responsibility, schema.responsibility_id)
            if not resp:
                raise HTTPException(
                    status_code=404,
                    detail=f"责任田 {schema.responsibility_id} 不存在"
                )

        update_data = schema.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_function, field, value)

        await db.commit()
        await db.refresh(db_function)
        return db_function

    async def move_function(
        self, db: AsyncSession, id: int, schema: FunctionMove
    ) -> Function:
        """Move a function to a new parent (drag and drop)."""
        db_function = await db.get(Function, id)
        if not db_function:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=404,
                detail=f"功能 {id} 不存在"
            )

        # Verify parent exists
        parent = await db.get(Function, schema.parent_id)
        if not parent:
            raise HTTPException(
                status_code=404,
                detail=f"父功能 {schema.parent_id} 不存在"
            )

        # Prevent moving to self or descendants
        if schema.parent_id == id:
            raise HTTPException(
                status_code=400,
                detail="不能将功能移动到自身"
            )

        # Check if new parent is a descendant (would create cycle)
        current_parent = parent
        while current_parent.parent_id is not None:
            if current_parent.parent_id == id:
                raise HTTPException(
                    status_code=400,
                    detail="不能将功能移动到其子节点"
                )
            current_parent = await db.get(Function, current_parent.parent_id)

        db_function.parent_id = schema.parent_id
        await db.commit()
        await db.refresh(db_function)
        return db_function

    async def delete_function(
        self, db: AsyncSession, id: int
    ) -> bool:
        """Delete a function."""
        db_function = await db.get(Function, id)
        if not db_function:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=404,
                detail=f"功能 {id} 不存在"
            )

        # Cascade delete will handle children and other relations
        await db.delete(db_function)
        await db.commit()
        return True

    async def get_function_modules(
        self, db: AsyncSession, function_id: int
    ) -> List[FunctionModule]:
        """Get modules associated with a function."""
        result = await db.execute(
            select(FunctionModule)
            .options(
                selectinload(FunctionModule.module),
                selectinload(FunctionModule.function)
            )
            .where(FunctionModule.function_id == function_id)
            .order_by(FunctionModule.order)
        )
        return result.scalars().all()

    async def update_function_modules(
        self, db: AsyncSession, function_id: int,
        module_schemas: List[FunctionModuleCreate]
    ) -> List[FunctionModule]:
        """Update function-module associations."""
        # Delete existing associations
        await db.execute(
            select(FunctionModule).where(FunctionModule.function_id == function_id)
        )
        # Note: SQLAlchemy doesn't have a direct async delete like this
        from sqlalchemy import delete
        await db.execute(
            delete(FunctionModule).where(FunctionModule.function_id == function_id)
        )

        # Create new associations
        for schema in module_schemas:
            db_fm = FunctionModule(
                function_id=function_id,
                module_id=schema.module_id,
                order=schema.order
            )
            db.add(db_fm)

        await db.commit()
        return await self.get_function_modules(db, function_id)

    async def get_function_data_flows(
        self, db: AsyncSession, function_id: int
    ) -> List[DataFlow]:
        """Get data flows for a function (both source and target)."""
        result = await db.execute(
            select(DataFlow)
            .options(
                selectinload(DataFlow.source_function),
                selectinload(DataFlow.target_function)
            )
            .where(
                (DataFlow.source_function_id == function_id) |
                (DataFlow.target_function_id == function_id)
            )
            .order_by(DataFlow.order)
        )
        return result.scalars().all()

    async def update_function_data_flows(
        self, db: AsyncSession, function_id: int,
        flow_schemas: List[DataFlowCreate]
    ) -> List[DataFlow]:
        """Update function data flows."""
        from sqlalchemy import delete

        # Delete existing flows where this function is source
        await db.execute(
            delete(DataFlow).where(DataFlow.source_function_id == function_id)
        )

        # Create new flows
        for schema in flow_schemas:
            db_flow = DataFlow(**schema.model_dump())
            db.add(db_flow)

        await db.commit()
        return await self.get_function_data_flows(db, function_id)

    async def export_functions_mermaid(
        self, db: AsyncSession
    ) -> str:
        """Export functions as Mermaid flowchart."""
        functions = await self.get_functions(db)

        # Build tree structure
        function_map = {f.id: f for f in functions}
        root_functions = [f for f in functions if f.parent_id is None]

        def build_mermaid_tree(function, level=0):
            indent = "  " * level
            lines = []
            resp_label = f" ({function.responsibility.name})" if function.responsibility else ""
            lines.append(f"{indent}{function.name}{resp_label}")
            for child in sorted(function.children, key=lambda x: x.name):
                lines.extend(build_mermaid_tree(child, level + 1))
            return lines

        lines = ["graph TD"]
        for root in sorted(root_functions, key=lambda x: x.name):
            lines.extend(build_mermaid_tree(root, 1))

        # Add data flows
        result = await db.execute(
            select(DataFlow).options(
                selectinload(DataFlow.source_function),
                selectinload(DataFlow.target_function)
            )
        )
        flows = result.scalars().all()

        for flow in flows:
            lines.append(
                f"  {flow.source_function.name} -->|{flow.description or ''}| {flow.target_function.name}"
            )

        return "\n".join(lines)

    # Responsibility-Function Relations
    async def get_responsibility_function_relations(
        self, db: AsyncSession
    ) -> List[Dict]:
        """Get all responsibility-function relations."""
        result = await db.execute(
            select(Responsibility, Function)
            .join(Function, Responsibility.id == Function.responsibility_id)
            .options(selectinload(Function.parent))
        )

        return [
            {
                "id": resp.id,
                "responsibility_id": resp.id,
                "function_id": func.id,
                "function_name": func.name,
                "responsibility_name": resp.name
            }
            for resp, func in result.all()
        ]

    async def create_responsibility_function_relation(
        self, db: AsyncSession, schema: ResponsibilityFunctionRelationCreate
    ) -> Function:
        """Create responsibility-function relation."""
        func = await db.get(Function, schema.function_id)
        if not func:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=404,
                detail=f"功能 {schema.function_id} 不存在"
            )

        resp = await db.get(Responsibility, schema.responsibility_id)
        if not resp:
            raise HTTPException(
                status_code=404,
                detail=f"责任田 {schema.responsibility_id} 不存在"
            )

        func.responsibility_id = schema.responsibility_id
        await db.commit()
        await db.refresh(func)
        return func

    async def delete_responsibility_function_relation(
        self, db: AsyncSession, schema: ResponsibilityFunctionRelationDelete
    ) -> bool:
        """Delete responsibility-function relation."""
        func = await db.get(Function, schema.id)
        if not func:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=404,
                detail=f"功能 {schema.id} 不存在"
            )

        func.responsibility_id = None
        await db.commit()
        return True


# Global service instance
architecture_service = ArchitectureService()
