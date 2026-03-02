"""Project management models."""
from typing import List, TYPE_CHECKING
from datetime import date, datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Float, DateTime
from sqlalchemy.orm import relationship, Mapped
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.team import Person


class Version(Base):
    """Version model for project releases."""

    __tablename__ = "versions"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name: Mapped[str] = Column(String(100), nullable=False)
    pm_name: Mapped[str] = Column(String(100), nullable=False)  # 项目经理
    sm_name: Mapped[str] = Column(String(100), nullable=False)  # 软件经理
    tm_name: Mapped[str] = Column(String(100), nullable=False)  # 测试经理

    # Relations
    iterations: Mapped[List["Iteration"]] = relationship(
        "Iteration", back_populates="version", cascade="all, delete-orphan"
    )


class Iteration(Base):
    """Iteration model for project sprints."""

    __tablename__ = "iterations"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    version_id: Mapped[int] = Column(Integer, ForeignKey("versions.id"), nullable=False)
    name: Mapped[str] = Column(String(100), nullable=False)
    start_date: Mapped[date] = Column(Date, nullable=False)
    end_date: Mapped[date] = Column(Date, nullable=False)
    estimated_man_months: Mapped[float] = Column(Float, default=0.0)

    # Relations
    version: Mapped["Version"] = relationship("Version", back_populates="iterations")
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="iteration")


class Task(Base):
    """Task model for project work items."""

    __tablename__ = "tasks"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    iteration_id: Mapped[int] = Column(Integer, ForeignKey("iterations.id"), nullable=False)
    name: Mapped[str] = Column(String(200), nullable=False)
    start_date: Mapped[date] = Column(Date, nullable=False)
    end_date: Mapped[date] = Column(Date, nullable=False)
    man_months: Mapped[float] = Column(Float, nullable=False)
    status: Mapped[str] = Column(String(50), default="pending")  # pending, in_progress, completed

    # 关键角色
    delivery_owner_id: Mapped[int] = Column(Integer, ForeignKey("persons.id"), nullable=False)
    developer_id: Mapped[int] = Column(Integer, ForeignKey("persons.id"), nullable=False)
    tester_id: Mapped[int] = Column(Integer, ForeignKey("persons.id"), nullable=False)

    # 文档
    design_doc_url: Mapped[str] = Column(String(500), nullable=True)

    # Relations
    iteration: Mapped["Iteration"] = relationship("Iteration", back_populates="tasks")
    delivery_owner: Mapped["Person"] = relationship("Person", foreign_keys=[delivery_owner_id])
    developer: Mapped["Person"] = relationship("Person", foreign_keys=[developer_id])
    tester: Mapped["Person"] = relationship("Person", foreign_keys=[tester_id])
    assignees: Mapped[List["Person"]] = relationship(
        "Person", secondary="task_assignees"
    )

    # 依赖和关联
    dependencies: Mapped[List["TaskDependency"]] = relationship(
        "TaskDependency", foreign_keys="TaskDependency.task_id"
    )
    dependents: Mapped[List["TaskDependency"]] = relationship(
        "TaskDependency", foreign_keys="TaskDependency.depends_on_id"
    )
    relations: Mapped[List["TaskRelation"]] = relationship(
        "TaskRelation", foreign_keys="TaskRelation.task_id"
    )
    related_tasks: Mapped[List["TaskRelation"]] = relationship(
        "TaskRelation", foreign_keys="TaskRelation.related_task_id"
    )

    # 完成记录
    completion: Mapped["TaskCompletion"] = relationship(
        "TaskCompletion", back_populates="task", uselist=False
    )


class TaskAssignee(Base):
    """Task assignee association model."""

    __tablename__ = "task_assignees"

    task_id: Mapped[int] = Column(Integer, ForeignKey("tasks.id"), primary_key=True)
    person_id: Mapped[int] = Column(Integer, ForeignKey("persons.id"), primary_key=True)


class TaskDependency(Base):
    """Task dependency model."""

    __tablename__ = "task_dependencies"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    task_id: Mapped[int] = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    depends_on_id: Mapped[int] = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    type: Mapped[str] = Column(
        String(50), default="finish_to_start"
    )  # finish_to_start, start_to_start, finish_to_finish, start_to_finish


class TaskRelation(Base):
    """Task relation model for concurrent tasks."""

    __tablename__ = "task_relations"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    task_id: Mapped[int] = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    related_task_id: Mapped[int] = Column(Integer, ForeignKey("tasks.id"), nullable=False)


class TaskCompletion(Base):
    """Task completion record model."""

    __tablename__ = "task_completions"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    task_id: Mapped[int] = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    actual_end_date: Mapped[datetime] = Column(DateTime, nullable=False)
    completion_status: Mapped[str] = Column(
        String(50), nullable=False
    )  # early, on_time, slightly_late, severely_late

    # Relations
    task: Mapped["Task"] = relationship("Task", back_populates="completion")
