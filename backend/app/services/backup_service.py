"""Backup and restore service."""
import asyncio
from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy import select, delete, insert, table
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.team import Person, Group, Responsibility, Capability
from app.models.architecture import Module, Function, FunctionModule, DataFlow
from app.models.project import Version, Iteration, Task, TaskDependency, TaskRelation, TaskCompletion
from app.models.audit import AuditLog
import json


class BackupService:
    """Backup and restore service."""

    async def create_backup(
        self, db: AsyncSession,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict:
        """Create a database backup."""
        if not name:
            name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        backup_data = {
            "name": name,
            "description": description or f"Backup created at {datetime.now().isoformat()}",
            "timestamp": datetime.now().isoformat(),
            "data": {},
        }

        # Export team data
        backup_data["data"]["team"] = await self._export_team_data(db)

        # Export architecture data
        backup_data["data"]["architecture"] = await self._export_architecture_data(db)

        # Export project data
        backup_data["data"]["project"] = await self._export_project_data(db)

        # Store backup (for now, save as JSON file)
        # In production, this would go to a proper backup service
        return backup_data

    async def _export_team_data(
        self, db: AsyncSession
    ) -> Dict:
        """Export all team-related data."""
        data = {
            "persons": [],
            "groups": [],
            "responsibilities": [],
            "capabilities": [],
        }

        # Export persons
        result = await db.execute(
            select(Person)
            .options(
                selectinload(Person.group),
                selectinload(Person.capabilities),
                selectinload(Person.responsibilities_owner),
                selectinload(Person.responsibilities_backup)
            )
        )
        persons = result.scalars().all()
        for person in persons:
            data["persons"].append({
                "id": person.id,
                "name": person.name,
                "emp_id": person.emp_id,
                "email": person.email,
                "phone": person.phone,
                "position": person.position,
                "group_id": person.group_id,
                "capabilities": [
                    {
                        "dimension": cap.dimension,
                        "level": cap.level,
                        "description": cap.description
                    }
                    for cap in person.capabilities
                ],
            })

        # Export groups
        result = await db.execute(
            select(Group).options(
                selectinload(Group.leader),
                selectinload(Group.members)
            )
        )
        groups = result.scalars().all()
        for group in groups:
            data["groups"].append({
                "id": group.id,
                "name": group.name,
                "leader_id": group.leader_id,
                "description": group.description,
                "members": [
                    {"id": m.id, "name": m.name}
                    for m in group.members
                ],
            })

        # Export responsibilities
        result = await db.execute(
            select(Responsibility)
            .options(
                selectinload(Responsibility.owner),
                selectinload(Responsibility.backup),
                selectinload(Responsibility.group)
            )
        )
        responsibilities = result.scalars().all()
        for resp in responsibilities:
            data["responsibilities"].append({
                "id": resp.id,
                "name": resp.name,
                "description": resp.description,
                "owner_id": resp.owner_id,
                "backup_id": resp.backup_id,
                "group_id": resp.group_id,
            })

        return data

    async def _export_architecture_data(
        self, db: AsyncSession
    ) -> Dict:
        """Export all architecture data."""
        data = {
            "modules": [],
            "functions": [],
            "function_modules": [],
            "data_flows": [],
        }

        # Export modules (tree structure)
        result = await db.execute(select(Module))
        modules = result.scalars().all()
        module_map = {m.id: m for m in modules}
        root_modules = [m for m in modules if not m.parent_id]

        def build_module_tree(module):
            children = [
                build_module_tree(child)
                for child in module.children
            ]
            return {
                "id": module.id,
                "name": module.name,
                "parent_id": module.parent_id,
                "children": children
            }

        for root in root_modules:
            data["modules"].append(build_module_tree(root))

        # Export functions
        result = await db.execute(
            select(Function)
            .options(
                selectinload(Function.parent),
                selectinload(Function.responsibility),
                selectinload(Function.function_modules).selectinload(FunctionModule.module)
            )
        )
        functions = result.scalars().all()

        for func in functions:
            data["functions"].append({
                "id": func.id,
                "name": func.name,
                "parent_id": func.parent_id,
                "responsibility_id": func.responsibility_id,
                "function_modules": [
                    {
                        "id": fm.id,
                        "function_id": fm.function_id,
                        "module_id": fm.module_id,
                        "order": fm.order
                    }
                    for fm in func.function_modules
                ],
            })

        # Export data flows
        result = await db.execute(
            select(DataFlow)
            .options(
                selectinload(DataFlow.source_function),
                selectinload(DataFlow.target_function)
            )
        )
        flows = result.scalars().all()

        for flow in flows:
            data["data_flows"].append({
                "id": flow.id,
                "source_function_id": flow.source_function_id,
                "target_function_id": flow.target_function_id,
                "order": flow.order,
                "description": flow.description,
            })

        return data

    async def _export_project_data(
        self, db: AsyncSession
    ) -> Dict:
        """Export all project data."""
        data = {
            "versions": [],
            "iterations": [],
            "tasks": [],
            "task_dependencies": [],
            "task_relations": [],
            "task_completions": [],
        }

        # Export versions
        result = await db.execute(
            select(Version)
            .options(
                selectinload(Version.iterations)
            )
        )
        versions = result.scalars().all()
        for version in versions:
            data["versions"].append({
                "id": version.id,
                "name": version.name,
                "pm_name": version.pm_name,
                "sm_name": version.sm_name,
                "tm_name": version.tm_name,
                "iterations": [
                    {
                        "id": it.id,
                        "name": it.name,
                        "version_id": it.version_id,
                        "start_date": it.start_date.isoformat() if it.start_date else None,
                        "end_date": it.end_date.isoformat() if it.end_date else None,
                        "estimated_man_months": it.estimated_man_months
                    }
                    for it in version.iterations
                ],
            })

        # Export iterations and tasks
        result = await db.execute(
            select(Iteration)
            .options(
                selectinload(Iteration.version),
                selectinload(Iteration.tasks)
            )
        )
        iterations = result.scalars().all()
        iteration_map = {it.id: it for it in iterations}

        # Export tasks
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
        )
        tasks = result.scalars().all()
        task_map = {t.id: t for t in tasks}

        for task in tasks:
            data["tasks"].append({
                "id": task.id,
                "name": task.name,
                "iteration_id": task.iteration_id,
                "start_date": task.start_date.isoformat() if task.start_date else None,
                "end_date": task.end_date.isoformat() if task.end_date else None,
                "man_months": task.man_months,
                "status": task.status,
                "delivery_owner_id": task.delivery_owner_id,
                "developer_id": task.developer_id,
                "tester_id": task.tester_id,
                "design_doc_url": task.design_doc_url,
                "dependencies": [
                    {
                        "id": dep.id,
                        "task_id": dep.task_id,
                        "depends_on_id": dep.depends_on_id,
                        "type": dep.type
                    }
                    for dep in task.dependencies
                ],
                "relations": [
                    {
                        "id": rel.id,
                        "task_id": rel.task_id,
                        "related_task_id": rel.related_task_id
                    }
                    for rel in task.relations
                ],
                "completion": {
                    "id": task.completion.id if task.completion else None,
                    "actual_end_date": task.completion.actual_end_date.isoformat() if task.completion else None,
                    "completion_status": task.completion.completion_status if task.completion else None
                } if task.completion else None,
            })

        # Export dependencies
        result = await db.execute(select(TaskDependency))
        deps = result.scalars().all()
        for dep in deps:
            data["task_dependencies"].append({
                "id": dep.id,
                "task_id": dep.task_id,
                "depends_on_id": dep.depends_on_id,
                "type": dep.type,
            })

        # Export relations
        result = await db.execute(select(TaskRelation))
        rels = result.scalars().all()
        for rel in rels:
            data["task_relations"].append({
                "id": rel.id,
                "task_id": rel.task_id,
                "related_task_id": rel.related_task_id,
            })

        # Export completions
        result = await db.execute(select(TaskCompletion))
        completions = result.scalars().all()
        for comp in completions:
            data["task_completions"].append({
                "id": comp.id,
                "task_id": comp.task_id,
                "actual_end_date": comp.actual_end_date.isoformat(),
                "completion_status": comp.completion_status,
            })

        return data

    async def restore_from_backup(
        self, db: AsyncSession,
        backup_data: Dict,
        current_user_id: int,
        restore_data: Optional[Dict] = None
    ) -> Dict:
        """Restore database from backup."""
        if not restore_data:
            restore_data = backup_data.get("data", {})

        restored = {
            "team": {},
            "architecture": {},
            "project": {},
            "errors": [],
        }

        # Restore team data
        if "team" in restore_data:
            try:
                await self._restore_team_data(db, restore_data["team"])
                restored["team"] = "success"
            except Exception as e:
                restored["team"] = f"failed: {str(e)}"
                restored["errors"].append(f"Team restore: {str(e)}")

        # Restore architecture data
        if "architecture" in restore_data:
            try:
                await self._restore_architecture_data(db, restore_data["architecture"])
                restored["architecture"] = "success"
            except Exception as e:
                restored["architecture"] = f"failed: {str(e)}"
                restored["errors"].append(f"Architecture restore: {str(e)}")

        # Restore project data
        if "project" in restore_data:
            try:
                await self._restore_project_data(db, restore_data["project"])
                restored["project"] = "success"
            except Exception as e:
                restored["project"] = f"failed: {str(e)}"
                restored["errors"].append(f"Project restore: {str(e)}")

        # Record restore audit log
        if current_user_id:
            log = AuditLog(
                user_id=current_user_id,
                action="restore",
                resource_type="backup",
                resource_id=backup_data.get("name"),
                details=f"Restored from backup: {backup_data.get('name', 'unknown')}"
            )
            db.add(log)
            await db.commit()

        return restored

    async def _restore_team_data(
        self, db: AsyncSession,
        data: Dict
    ) -> None:
        """Restore team data."""
        # Restore persons
        person_map = {}
        for person_data in data.get("persons", []):
            person = Person(**person_data)
            person_map[person_data["id"]] = person
            db.add(person)

        # Restore groups and assign members
        for group_data in data.get("groups", []):
            group = Group(**group_data)
            if "leader_id" in group_data:
                group.leader = person_map.get(group_data["leader_id"])
            if "members" in group_data:
                group.members = [
                    person_map.get(m["id"])
                    for m in group_data["members"]
                    if m["id"] in person_map
                ]
            db.add(group)

        # Restore responsibilities
        for resp_data in data.get("responsibilities", []):
            resp = Responsibility(**resp_data)
            if "owner_id" in resp_data:
                resp.owner = person_map.get(resp_data["owner_id"])
            if "backup_id" in resp_data:
                resp.backup = person_map.get(resp_data["backup_id"])
            if "group_id" in resp_data:
                # Find the group by original id, will be remapped
                # In production, need to implement proper remapping
                pass
            db.add(resp)

        # Restore capabilities
        for person_data in data.get("persons", []):
            person_id = person_map[person_data["id"]].id
            for cap_data in person_data.get("capabilities", []):
                cap = Capability(
                    person_id=person_id,
                    **cap_data
                )
                db.add(cap)

        await db.commit()

    async def _restore_architecture_data(
        self, db: AsyncSession,
        data: Dict
    ) -> None:
        """Restore architecture data."""
        # Restore modules (need to rebuild hierarchy)
        module_map = {}
        for module_data in data.get("modules", []):
            module = Module(**module_data)
            # Save temporarily, will fix parent_id after all modules created
            module.parent_id = None  # Reset parent_id for now
            db.add(module)
            module_map[module_data["id"]] = module

        # Fix parent_id references
        for module_data in data.get("modules", []):
            if module_data["parent_id"] and module_data["parent_id"] in module_map:
                module = module_map.get(module_data["id"])
                if module:
                    module.parent_id = module_data["parent_id"]

        # Restore functions
        function_map = {}
        for func_data in data.get("functions", []):
            function = Function(**func_data)
            # Reset parent_id for now
            function.parent_id = None
            function.responsibility_id = func_data.get("responsibility_id")
            db.add(function)
            function_map[func_data["id"]] = function

        # Fix function parent_id
        for func_data in data.get("functions", []):
            if func_data["parent_id"] and func_data["parent_id"] in function_map:
                function = function_map.get(func_data["id"])
                if function:
                    function.parent_id = func_data["parent_id"]

        # Restore function-module associations
        for func_data in data.get("functions", []):
            for fm_data in func_data.get("function_modules", []):
                fm = FunctionModule(**fm_data)
                fm.module = module_map.get(fm_data["module_id"])
                fm.function = function_map.get(fm_data["function_id"])
                db.add(fm)

        # Restore data flows
        for flow_data in data.get("data_flows", []):
            flow = DataFlow(**flow_data)
            flow.source_function = function_map.get(flow_data["source_function_id"])
            flow.target_function = function_map.get(flow_data["target_function_id"])
            db.add(flow)

        await db.commit()

    async def _restore_project_data(
        self, db: AsyncSession,
        data: Dict
    ) -> None:
        """Restore project data."""
        # Restore versions
        version_map = {}
        for version_data in data.get("versions", []):
            version = Version(**version_data)
            db.add(version)
            version_map[version_data["id"]] = version

        # Restore iterations
        iteration_map = {}
        for iteration_data in data.get("iterations", []):
            iteration = Iteration(**iteration_data)
            iteration.version = version_map.get(iteration_data["version_id"])
            db.add(iteration)
            iteration_map[iteration_data["id"]] = iteration

        # Restore tasks
        task_map = {}
        for task_data in data.get("tasks", []):
            task = Task(**task_data)
            task.iteration = iteration_map.get(task_data["iteration_id"])
            task.delivery_owner = db.get(Person, task_data["delivery_owner_id"])
            task.developer = db.get(Person, task_data["developer_id"])
            task.tester = db.get(Person, task_data["tester_id"])
            db.add(task)
            task_map[task_data["id"]] = task

        # Restore task dependencies
        for dep_data in data.get("task_dependencies", []):
            dep = TaskDependency(**dep_data)
            dep.task = task_map.get(dep_data["task_id"])
            dep.depends_on = task_map.get(dep_data["depends_on_id"])
            db.add(dep)

        # Restore task relations
        for rel_data in data.get("task_relations", []):
            rel = TaskRelation(**rel_data)
            rel.task = task_map.get(rel_data["task_id"])
            rel.related_task = task_map.get(rel_data["related_task_id"])
            db.add(rel)

        # Restore task completions
        for comp_data in data.get("task_completions", []):
            comp = TaskCompletion(**comp_data)
            comp.task = task_map.get(comp_data["task_id"])
            db.add(comp)

        await db.commit()


# Global service instance
backup_service = BackupService()
