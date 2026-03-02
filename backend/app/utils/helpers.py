"""Common utility functions."""
from datetime import datetime, date
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import Base


def calculate_workload(
    tasks: List[dict],
    start_date: date,
    end_date: date
) -> float:
    """
    Calculate workload for a person or group.

    Args:
        tasks: List of tasks with man_months and date ranges
        start_date: Start date for workload calculation
        end_date: End date for workload calculation

    Returns:
        Workload in person-months
    """
    total_man_months = 0.0

    for task in tasks:
        task_start = task.get("start_date")
        task_end = task.get("end_date")
        man_months = task.get("man_months", 0.0)

        # Calculate overlapping period
        overlap_start = max(start_date, task_start) if task_start else start_date
        overlap_end = min(end_date, task_end) if task_end else end_date

        if overlap_start < overlap_end:
            # Proportion of task within the date range
            total_task_days = (task_end - task_start).days if task_end and task_start else 30
            overlap_days = (overlap_end - overlap_start).days
            proportion = overlap_days / total_task_days if total_task_days > 0 else 1.0
            total_man_months += man_months * proportion

    return total_man_months


def determine_completion_status(
    planned_end_date: date,
    actual_end_date: datetime
) -> str:
    """
    Determine task completion status based on timing.

    Args:
        planned_end_date: Planned end date
        actual_end_date: Actual completion datetime

    Returns:
        Status: 'early', 'on_time', 'slightly_late', 'severely_late'
    """
    planned = datetime.combine(planned_end_date, datetime.min.time())
    delta_hours = (actual_end_date - planned).total_seconds() / 3600

    if delta_hours < 0:
        return "early"
    elif delta_hours <= 24:
        return "on_time"
    elif delta_hours <= 48:
        return "slightly_late"
    else:
        return "severely_late"


def check_task_conflict(
    task: dict,
    dependencies: List[dict],
    iteration_start: Optional[date] = None,
    iteration_end: Optional[date] = None
) -> List[str]:
    """
    Check for task conflicts.

    Args:
        task: Task to check
        dependencies: List of dependent tasks
        iteration_start: Iteration start date (optional)
        iteration_end: Iteration end date (optional)

    Returns:
        List of conflict messages
    """
    conflicts = []

    task_start = task.get("start_date")
    task_end = task.get("end_date")

    # Check iteration boundaries
    if iteration_end and task_end:
        if task_end > iteration_end:
            conflicts.append(
                f"任务终止时间 {task_end} 晚于迭代终止时间 {iteration_end}"
            )

    if iteration_start and task_start:
        if task_start < iteration_start:
            conflicts.append(
                f"任务起始时间 {task_start} 早于迭代起始时间 {iteration_start}"
            )

    # Check dependencies
    for dep in dependencies:
        dep_end = dep.get("end_date")
        dep_type = dep.get("type", "finish_to_start")

        if dep_type == "finish_to_start":
            if dep_end and task_start:
                if task_start <= dep_end:
                    conflicts.append(
                        f"依赖任务 {dep.get('name')} 终止于 {dep_end}，"
                        f"当前任务起始于 {task_start}（finish_to_start依赖）"
                    )
        elif dep_type == "start_to_start":
            dep_start = dep.get("start_date")
            if dep_start and task_start:
                if task_start < dep_start:
                    conflicts.append(
                        f"依赖任务 {dep.get('name')} 起始于 {dep_start}，"
                        f"当前任务起始于 {task_start}（start_to_start依赖）"
                    )
        elif dep_type == "finish_to_finish":
            if dep_end and task_end:
                if task_end < dep_end:
                    conflicts.append(
                        f"依赖任务 {dep.get('name')} 终止于 {dep_end}，"
                        f"当前任务终止于 {task_end}（finish_to_finish依赖）"
                    )
        elif dep_type == "start_to_finish":
            dep_start = dep.get("start_date")
            if dep_start and task_end:
                if task_end < dep_start:
                    conflicts.append(
                        f"依赖任务 {dep.get('name')} 起始于 {dep_start}，"
                        f"当前任务终止于 {task_end}（start_to_finish依赖）"
                    )

    return conflicts


def find_longest_path(tasks: List[dict], dependencies: List[dict]) -> List[str]:
    """
    Find longest path in task dependency graph (critical path).

    Args:
        tasks: List of all tasks
        dependencies: List of task dependencies

    Returns:
        List of task names in longest path
    """
    # Build adjacency list
    task_map = {t["id"]: t for t in tasks}
    graph = {t["id"]: [] for t in tasks}

    for dep in dependencies:
        task_id = dep.get("task_id")
        depends_on_id = dep.get("depends_on_id")
        if task_id and depends_on_id:
            graph[depends_on_id].append(task_id)

    # Topological sort with longest path tracking
    visited = set()
    longest_dist = {t["id"]: 0 for t in tasks}
    predecessor = {}

    def dfs(node_id):
        if node_id in visited:
            return
        visited.add(node_id)

        for neighbor in graph.get(node_id, []):
            if neighbor in longest_dist:
                if longest_dist[node_id] + 1 > longest_dist[neighbor]:
                    longest_dist[neighbor] = longest_dist[node_id] + 1
                    predecessor[neighbor] = node_id
            dfs(neighbor)

    # Run DFS from all nodes
    for task_id in task_map.keys():
        dfs(task_id)

    # Find node with max distance
    end_node = max(longest_dist, key=longest_dist.get)

    # Reconstruct path
    path = []
    current = end_node
    while current in predecessor:
        task = task_map.get(current)
        if task:
            path.append(task["name"])
        current = predecessor[current]
    task = task_map.get(current)
    if task:
        path.append(task["name"])

    return list(reversed(path))
