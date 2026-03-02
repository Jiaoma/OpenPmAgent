"""Project management business logic."""
from typing import List, Optional, Dict
from datetime import date, datetime
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.project import (
    Version, Iteration, Task, TaskDependency, TaskRelation, TaskCompletion
)
from app.models.team import Person
from app.schemas.project import (
    VersionCreate, VersionUpdate,
    IterationCreate, IterationUpdate,
    TaskCreate, TaskUpdate,
    TaskDependencyCreate, TaskRelationCreate,
    TaskCompletionCreate,
    TaskAchievementStats, AchievementExportRequest
)
from app.utils.helpers import check_task_conflict, find_longest_path


class ProjectService:
    """Project management service."""

    # Version Management
    async def get_versions(
        self, db: AsyncSession
    ) -> List[Version]:
        """Get all versions."""
        result = await db.execute(
            select(Version)
            .options(selectinload(Version.iterations))
            .order_by(Version.id.desc())
        )
        return result.scalars().all()

    async def get_version(
        self, db: AsyncSession, id: int
    ) -> Optional[Version]:
        """Get version by ID."""
        result = await db.execute(
            select(Version)
            .options(
                selectinload(Version.iterations).selectinload(Iteration.tasks)
            )
            .where(Version.id == id)
        )
        return result.scalar_one_or_none()

    async def create_version(
        self, db: AsyncSession, schema: VersionCreate
    ) -> Version:
        """Create a version."""
        db_version = Version(**schema.model_dump())
        db.add(db_version)
        await db.commit()
        await db.refresh(db_version)
        return db_version

    async def update_version(
        self, db: AsyncSession, id: int, schema: VersionUpdate
    ) -> Version:
        """Update a version."""
        db_version = await db.get(Version, id)
        if not db_version:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=404,
                detail=f"版本 {id} 不存在"
            )

        update_data = schema.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_version, field, value)

        await db.commit()
        await db.refresh(db_version)
        return db_version

    async def delete_version(
        self, db: AsyncSession, id: int
    ) -> bool:
        """Delete a version."""
        db_version = await db.get(Version, id)
        if not db_version:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=404,
                detail=f"版本 {id} 不存在"
            )

        # Cascade delete will handle iterations and tasks
        await db.delete(db_version)
        await db.commit()
        return True

    # Iteration Management
    async def get_iterations(
        self, db: AsyncSession, version_id: Optional[int] = None
    ) -> List[Iteration]:
        """Get all iterations."""
        query = select(Iteration).options(
            selectinload(Iteration.version),
            selectinload(Iteration.tasks)
        )

        if version_id:
            query = query.where(Iteration.version_id == version_id)

        result = await db.execute(query.order_by(Iteration.id.desc()))
        return result.scalars().all()

    async def get_iteration(
        self, db: AsyncSession, id: int
    ) -> Optional[Iteration]:
        """Get iteration by ID."""
        result = await db.execute(
            select(Iteration)
            .options(
                selectinload(Iteration.version),
                selectinload(Iteration.tasks).selectinload(Task.delivery_owner),
                selectinload(Iteration.tasks).selectinload(Task.developer),
                selectinload(Iteration.tasks).selectinload(Task.tester),
                selectinload(Iteration.tasks).selectinload(Task.completion)
            )
            .where(Iteration.id == id)
        )
        return result.scalar_one_or_none()

    async def create_iteration(
        self, db: AsyncSession, schema: IterationCreate
    ) -> Iteration:
        """Create an iteration."""
        # Verify version exists
        version = await db.get(Version, schema.version_id)
        if not version:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=404,
                detail=f"版本 {schema.version_id} 不存在"
            )

        db_iteration = Iteration(**schema.model_dump())
        db.add(db_iteration)
        await db.commit()
        await db.refresh(db_iteration)
        return db_iteration

    async def update_iteration(
        self, db: AsyncSession, id: int, schema: IterationUpdate
    ) -> Iteration:
        """Update an iteration."""
        db_iteration = await db.get(Iteration, id)
        if not db_iteration:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=404,
                detail=f"迭代 {id} 不存在"
            )

        update_data = schema.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_iteration, field, value)

        await db.commit()
        await db.refresh(db_iteration)
        return db_iteration

    async def delete_iteration(
        self, db: AsyncSession, id: int
    ) -> bool:
        """Delete an iteration."""
        db_iteration = await db.get(Iteration, id)
        if not db_iteration:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=404,
                detail=f"迭代 {id} 不存在"
            )

        # Cascade delete will handle tasks
        await db.delete(db_iteration)
        await db.commit()
        return True

    async def check_iteration_conflicts(
        self, db: AsyncSession, iteration_id: int
    ) -> List[Dict]:
        """Check for conflicts within an iteration."""
        result = await db.execute(
            select(Task)
            .options(
                selectinload(Task.developer),
                selectinload(Task.delivery_owner),
                selectinload(Task.tester)
            )
            .where(Task.iteration_id == iteration_id)
        )
        tasks = result.scalars().all()

        conflicts = []
        task_list = [
            {
                "id": t.id,
                "name": t.name,
                "start_date": t.start_date,
                "end_date": t.end_date,
                "developer_id": t.developer_id,
                "delivery_owner_id": t.delivery_owner_id,
                "tester_id": t.tester_id,
            }
            for t in tasks
        ]

        for i, task in enumerate(task_list):
            for other_task in task_list[i+1:]:
                # Check developer conflicts
                if (task["developer_id"] == other_task["developer_id"] and
                    task["developer_id"] is not None):
                    if check_task_conflict(task, other_task):
                        conflicts.append({
                            "task1_id": task["id"],
                            "task1_name": task["name"],
                            "task2_id": other_task["id"],
                            "task2_name": other_task["name"],
                            "conflict_type": "developer",
                            "person_id": task["developer_id"]
                        })

                # Check delivery owner conflicts
                if (task["delivery_owner_id"] == other_task["delivery_owner_id"] and
                    task["delivery_owner_id"] is not None):
                    if check_task_conflict(task, other_task):
                        conflicts.append({
                            "task1_id": task["id"],
                            "task1_name": task["name"],
                            "task2_id": other_task["id"],
                            "task2_name": other_task["name"],
                            "conflict_type": "delivery_owner",
                            "person_id": task["delivery_owner_id"]
                        })

                # Check tester conflicts
                if (task["tester_id"] == other_task["tester_id"] and
                    task["tester_id"] is not None):
                    if check_task_conflict(task, other_task):
                        conflicts.append({
                            "task1_id": task["id"],
                            "task1_name": task["name"],
                            "task2_id": other_task["id"],
                            "task2_name": other_task["name"],
                            "conflict_type": "tester",
                            "person_id": task["tester_id"]
                        })

        return conflicts

    # Task Management
    async def get_tasks(
        self, db: AsyncSession,
        iteration_id: Optional[int] = None,
        version_id: Optional[int] = None,
        person_id: Optional[int] = None
    ) -> List[Task]:
        """Get all tasks with optional filters."""
        query = select(Task).options(
            selectinload(Task.iteration).selectinload(Iteration.version),
            selectinload(Task.delivery_owner),
            selectinload(Task.developer),
            selectinload(Task.tester),
            selectinload(Task.dependencies),
            selectinload(Task.dependents),
            selectinload(Task.relations),
            selectinload(Task.related_tasks),
            selectinload(Task.completion)
        )

        if iteration_id:
            query = query.where(Task.iteration_id == iteration_id)

        if version_id:
            query = query.join(Iteration).where(Iteration.version_id == version_id)

        if person_id:
            query = query.where(
                or_(
                    Task.delivery_owner_id == person_id,
                    Task.developer_id == person_id,
                    Task.tester_id == person_id
                )
            )

        result = await db.execute(query.order_by(Task.id.desc()))
        return result.scalars().all()

    async def get_task(
        self, db: AsyncSession, id: int
    ) -> Optional[Task]:
        """Get task by ID."""
        result = await db.execute(
            select(Task)
            .options(
                selectinload(Task.iteration).selectinload(Iteration.version),
                selectinload(Task.delivery_owner),
                selectinload(Task.developer),
                selectinload(Task.tester),
                selectinload(Task.dependencies),
                selectinload(Task.dependents),
                selectinload(Task.relations),
                selectinload(Task.related_tasks),
                selectinload(Task.completion)
            )
            .where(Task.id == id)
        )
        return result.scalar_one_or_none()

    async def create_task(
        self, db: AsyncSession, schema: TaskCreate
    ) -> Task:
        """Create a task."""
        # Verify iteration exists
        iteration = await db.get(Iteration, schema.iteration_id)
        if not iteration:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=404,
                detail=f"迭代 {schema.iteration_id} 不存在"
            )

        # Verify persons exist
        for person_id in [schema.delivery_owner_id, schema.developer_id, schema.tester_id]:
            person = await db.get(Person, person_id)
            if not person:
                raise HTTPException(
                    status_code=404,
                    detail=f"人员 {person_id} 不存在"
                )

        db_task = Task(**schema.model_dump())
        db.add(db_task)
        await db.commit()
        await db.refresh(db_task)
        return db_task

    async def update_task(
        self, db: AsyncSession, id: int, schema: TaskUpdate
    ) -> Task:
        """Update a task."""
        db_task = await db.get(Task, id)
        if not db_task:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=404,
                detail=f"任务 {id} 不存在"
            )

        # Verify persons exist if provided
        if schema.delivery_owner_id:
            person = await db.get(Person, schema.delivery_owner_id)
            if not person:
                raise HTTPException(
                    status_code=404,
                    detail=f"人员 {schema.delivery_owner_id} 不存在"
                )

        if schema.developer_id:
            person = await db.get(Person, schema.developer_id)
            if not person:
                raise HTTPException(
                    status_code=404,
                    detail=f"人员 {schema.developer_id} 不存在"
                )

        if schema.tester_id:
            person = await db.get(Person, schema.tester_id)
            if not person:
                raise HTTPException(
                    status_code=404,
                    detail=f"人员 {schema.tester_id} 不存在"
                )

        update_data = schema.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_task, field, value)

        await db.commit()
        await db.refresh(db_task)
        return db_task

    async def delete_task(
        self, db: AsyncSession, id: int
    ) -> bool:
        """Delete a task."""
        db_task = await db.get(Task, id)
        if not db_task:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=404,
                detail=f"任务 {id} 不存在"
            )

        # Cascade delete will handle dependencies, relations, completion
        await db.delete(db_task)
        await db.commit()
        return True

    # Task Dependencies
    async def add_task_dependency(
        self, db: AsyncSession, schema: TaskDependencyCreate
    ) -> TaskDependency:
        """Add a task dependency."""
        # Verify tasks exist
        task = await db.get(Task, schema.task_id)
        if not task:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=404,
                detail=f"任务 {schema.task_id} 不存在"
            )

        depends_on = await db.get(Task, schema.depends_on_id)
        if not depends_on:
            raise HTTPException(
                status_code=404,
                detail=f"依赖任务 {schema.depends_on_id} 不存在"
            )

        # Prevent self-dependency
        if schema.task_id == schema.depends_on_id:
            raise HTTPException(
                status_code=400,
                detail="任务不能依赖自身"
            )

        # Check for circular dependency
        # (Simplified check - full implementation would traverse graph)

        db_dep = TaskDependency(**schema.model_dump())
        db.add(db_dep)
        await db.commit()
        await db.refresh(db_dep)
        return db_dep

    async def delete_task_dependency(
        self, db: AsyncSession, task_id: int, dep_id: int
    ) -> bool:
        """Delete a task dependency."""
        result = await db.execute(
            select(TaskDependency).where(
                TaskDependency.id == dep_id,
                TaskDependency.task_id == task_id
            )
        )
        dep = result.scalar_one_or_none()
        if not dep:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=404,
                detail=f"依赖关系 {dep_id} 不存在"
            )

        await db.delete(dep)
        await db.commit()
        return True

    # Task Relations
    async def add_task_relation(
        self, db: AsyncSession, schema: TaskRelationCreate
    ) -> TaskRelation:
        """Add a task relation (concurrent tasks)."""
        # Verify tasks exist
        task = await db.get(Task, schema.task_id)
        if not task:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=404,
                detail=f"任务 {schema.task_id} 不存在"
            )

        related = await db.get(Task, schema.related_task_id)
        if not related:
            raise HTTPException(
                status_code=404,
                detail=f"关联任务 {schema.related_task_id} 不存在"
            )

        # Prevent self-relation
        if schema.task_id == schema.related_task_id:
            raise HTTPException(
                status_code=400,
                detail="任务不能关联自身"
            )

        db_rel = TaskRelation(**schema.model_dump())
        db.add(db_rel)
        await db.commit()
        await db.refresh(db_rel)
        return db_rel

    async def delete_task_relation(
        self, db: AsyncSession, task_id: int, rel_id: int
    ) -> bool:
        """Delete a task relation."""
        result = await db.execute(
            select(TaskRelation).where(
                TaskRelation.id == rel_id,
                TaskRelation.task_id == task_id
            )
        )
        rel = result.scalar_one_or_none()
        if not rel:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=404,
                detail=f"关联关系 {rel_id} 不存在"
            )

        await db.delete(rel)
        await db.commit()
        return True

    async def check_task_conflicts(
        self, db: AsyncSession, task_id: int
    ) -> List[Dict]:
        """Check for task conflicts."""
        result = await db.execute(
            select(Task).where(Task.id == task_id)
        )
        task = result.scalar_one_or_none()
        if not task:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=404,
                detail=f"任务 {task_id} 不存在"
            )

        # Get all tasks in the same iteration
        result = await db.execute(
            select(Task)
            .where(
                Task.iteration_id == task.iteration_id,
                Task.id != task_id
            )
            .options(
                selectinload(Task.developer),
                selectinload(Task.delivery_owner),
                selectinload(Task.tester)
            )
        )
        other_tasks = result.scalars().all()

        conflicts = []
        task_dict = {
            "id": task.id,
            "name": task.name,
            "start_date": task.start_date,
            "end_date": task.end_date,
            "developer_id": task.developer_id,
            "delivery_owner_id": task.delivery_owner_id,
            "tester_id": task.tester_id,
        }

        for other_task in other_tasks:
            other_dict = {
                "id": other_task.id,
                "name": other_task.name,
                "start_date": other_task.start_date,
                "end_date": other_task.end_date,
                "developer_id": other_task.developer_id,
                "delivery_owner_id": other_task.delivery_owner_id,
                "tester_id": other_task.tester_id,
            }

            # Check developer conflicts
            if (task_dict["developer_id"] == other_dict["developer_id"] and
                task_dict["developer_id"] is not None):
                if check_task_conflict(task_dict, other_dict):
                    conflicts.append({
                        "task_id": task.id,
                        "task_name": task.name,
                        "conflicting_task_id": other_task.id,
                        "conflicting_task_name": other_task.name,
                        "conflict_type": "developer",
                        "person_id": task.developer_id
                    })

            # Check delivery owner conflicts
            if (task_dict["delivery_owner_id"] == other_dict["delivery_owner_id"] and
                task_dict["delivery_owner_id"] is not None):
                if check_task_conflict(task_dict, other_dict):
                    conflicts.append({
                        "task_id": task.id,
                        "task_name": task.name,
                        "conflicting_task_id": other_task.id,
                        "conflicting_task_name": other_task.name,
                        "conflict_type": "delivery_owner",
                        "person_id": task.delivery_owner_id
                    })

            # Check tester conflicts
            if (task_dict["tester_id"] == other_dict["tester_id"] and
                task_dict["tester_id"] is not None):
                if check_task_conflict(task_dict, other_dict):
                    conflicts.append({
                        "task_id": task.id,
                        "task_name": task.name,
                        "conflicting_task_id": other_task.id,
                        "conflicting_task_name": other_task.name,
                        "conflict_type": "tester",
                        "person_id": task.tester_id
                    })

        return conflicts

    async def mark_task_complete(
        self, db: AsyncSession, task_id: int, schema: TaskCompletionCreate
    ) -> Task:
        """Mark a task as complete."""
        task = await db.get(Task, task_id)
        if not task:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=404,
                detail=f"任务 {task_id} 不存在"
            )

        # Create or update completion record
        result = await db.execute(
            select(TaskCompletion).where(TaskCompletion.task_id == task_id)
        )
        completion = result.scalar_one_or_none()

        actual_end_date = datetime.fromisoformat(schema.actual_end_date)

        if completion:
            completion.actual_end_date = actual_end_date
            completion.completion_status = schema.completion_status
        else:
            completion = TaskCompletion(
                task_id=task_id,
                actual_end_date=actual_end_date,
                completion_status=schema.completion_status
            )
            db.add(completion)

        task.status = "completed"
        await db.commit()
        await db.refresh(task)
        return task

    # Task Graph Analysis
    async def get_task_graph(
        self, db: AsyncSession, iteration_id: Optional[int] = None
    ) -> List[Dict]:
        """Get task dependency graph data."""
        query = select(Task).options(
            selectinload(Task.dependencies),
            selectinload(Task.dependents),
            selectinload(Task.relations),
            selectinload(Task.related_tasks)
        )

        if iteration_id:
            query = query.where(Task.iteration_id == iteration_id)

        result = await db.execute(query)
        tasks = result.scalars().all()

        nodes = []
        for task in tasks:
            nodes.append({
                "id": task.id,
                "name": task.name,
                "start_date": task.start_date.isoformat() if task.start_date else None,
                "end_date": task.end_date.isoformat() if task.end_date else None,
                "status": task.status,
                "developer_id": task.developer_id,
            })

        # Get dependencies
        result = await db.execute(select(TaskDependency))
        deps = result.scalars().all()
        edges = []
        for dep in deps:
            edges.append({
                "source": dep.task_id,
                "target": dep.depends_on_id,
                "type": dep.type,
                "id": dep.id
            })

        # Get relations
        result = await db.execute(select(TaskRelation))
        rels = result.scalars().all()
        for rel in rels:
            edges.append({
                "source": rel.task_id,
                "target": rel.related_task_id,
                "type": "relation",
                "id": rel.id
            })

        return {"nodes": nodes, "edges": edges}

    async def get_longest_path(
        self, db: AsyncSession, iteration_id: Optional[int] = None
    ) -> List[Dict]:
        """Get the longest path in task dependency graph."""
        query = select(Task)
        if iteration_id:
            query = query.where(Task.iteration_id == iteration_id)

        result = await db.execute(query)
        tasks = result.scalars().all()

        # Build graph structure
        task_map = {t.id: t for t in tasks}
        adj_list = {t.id: [] for t in tasks}

        result = await db.execute(select(TaskDependency))
        deps = result.scalars().all()
        for dep in deps:
            adj_list[dep.task_id].append(dep.depends_on_id)

        # Find longest path
        longest_path_ids = find_longest_path(adj_list)

        return [
            {
                "id": task_map[tid].id,
                "name": task_map[tid].name,
                "start_date": task_map[tid].start_date.isoformat() if task_map[tid].start_date else None,
                "end_date": task_map[tid].end_date.isoformat() if task_map[tid].end_date else None,
                "man_months": task_map[tid].man_months,
                "developer_id": task_map[tid].developer_id,
            }
            for tid in longest_path_ids
        ]

    async def get_highest_load_person(
        self, db: AsyncSession, iteration_id: Optional[int] = None
    ) -> Optional[Dict]:
        """Get the person with highest workload."""
        query = select(Task).options(selectinload(Task.developer))
        if iteration_id:
            query = query.where(Task.iteration_id == iteration_id)

        result = await db.execute(query)
        tasks = result.scalars().all()

        # Calculate workload per person
        person_workload = {}
        for task in tasks:
            if task.developer_id:
                if task.developer_id not in person_workload:
                    person_workload[task.developer_id] = {
                        "person_id": task.developer_id,
                        "person_name": task.developer.name if task.developer else "Unknown",
                        "man_months": 0,
                        "task_count": 0
                    }
                person_workload[task.developer_id]["man_months"] += task.man_months
                person_workload[task.developer_id]["task_count"] += 1

        if not person_workload:
            return None

        # Find highest load
        highest_load = max(person_workload.values(), key=lambda x: x["man_months"])
        return highest_load

    # Gantt Chart
    async def get_gantt_data(
        self, db: AsyncSession,
        iteration_id: Optional[int] = None,
        version_id: Optional[int] = None
    ) -> List[Dict]:
        """Get data for Gantt chart."""
        tasks = await self.get_tasks(db, iteration_id=iteration_id, version_id=version_id)

        gantt_data = []
        for task in tasks:
            gantt_data.append({
                "id": task.id,
                "name": task.name,
                "iteration_id": task.iteration_id,
                "iteration_name": task.iteration.name if task.iteration else "",
                "start_date": task.start_date.isoformat() if task.start_date else None,
                "end_date": task.end_date.isoformat() if task.end_date else None,
                "man_months": task.man_months,
                "status": task.status,
                "progress": 100 if task.status == "completed" else (50 if task.status == "in_progress" else 0),
                "delivery_owner_id": task.delivery_owner_id,
                "delivery_owner_name": task.delivery_owner.name if task.delivery_owner else "",
                "developer_id": task.developer_id,
                "developer_name": task.developer.name if task.developer else "",
                "tester_id": task.tester_id,
                "tester_name": task.tester.name if task.tester else "",
            })

        return gantt_data

    async def export_gantt_mermaid(
        self, db: AsyncSession,
        iteration_id: Optional[int] = None,
        version_id: Optional[int] = None
    ) -> str:
        """Export Gantt chart as Mermaid."""
        tasks = await self.get_tasks(db, iteration_id=iteration_id, version_id=version_id)

        lines = ["gantt", "    title 项目甘特图", "    dateFormat  YYYY-MM-DD"]

        if version_id:
            tasks_by_version = [t for t in tasks if t.iteration.version_id == version_id]
        else:
            tasks_by_version = tasks

        for task in tasks_by_version:
            status_label = {
                "pending": "",
                "in_progress": "active",
                "completed": "done"
            }.get(task.status, "")

            dev_name = task.developer.name if task.developer else "Unknown"
            lines.append(
                f"    {status_label} {task.name} :{dev_name}, {task.start_date}, {task.end_date}"
            )

        return "\n".join(lines)

    # Achievement Statistics
    async def get_achievement_stats(
        self, db: AsyncSession,
        version_ids: Optional[List[int]] = None,
        iteration_ids: Optional[List[int]] = None,
        person_ids: Optional[List[int]] = None
    ) -> List[TaskAchievementStats]:
        """Get task achievement statistics."""
        query = select(Task, TaskCompletion, Person).select_from(
            Task
        ).outerjoin(
            TaskCompletion, Task.id == TaskCompletion.task_id
        ).outerjoin(
            Person, Task.developer_id == Person.id
        )

        if version_ids:
            query = query.join(Iteration).where(Iteration.version_id.in_(version_ids))

        if iteration_ids:
            query = query.where(Task.iteration_id.in_(iteration_ids))

        if person_ids:
            query = query.where(Task.developer_id.in_(person_ids))

        result = await db.execute(query)
        rows = result.all()

        # Group by person
        person_stats = {}
        for task, completion, person in rows:
            if person_id := person.id if person else None:
                if person_id not in person_stats:
                    person_stats[person_id] = {
                        "person_id": person_id,
                        "person_name": person.name if person else "Unknown",
                        "person_role": "developer",
                        "total_tasks": 0,
                        "completed": 0,
                        "early": 0,
                        "on_time": 0,
                        "slightly_late": 0,
                        "severely_late": 0,
                    }

                stats = person_stats[person_id]
                stats["total_tasks"] += 1

                if completion:
                    stats["completed"] += 1
                    stats[completion.completion_status] = stats.get(completion.completion_status, 0) + 1

        return [
            TaskAchievementStats(**stats)
            for stats in person_stats.values()
        ]


# Global service instance
project_service = ProjectService()
