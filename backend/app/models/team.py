"""Team management models."""
from typing import List, TYPE_CHECKING
from datetime import date
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, JSON
from sqlalchemy.orm import relationship, Mapped
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.project import Task
    from app.models.audit import AuditLog


class Person(Base):
    """Person model for team members."""

    __tablename__ = "persons"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name: Mapped[str] = Column(String(100), nullable=False)
    emp_id: Mapped[str] = Column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = Column(String(255), nullable=False)
    group_id: Mapped[int] = Column(Integer, ForeignKey("groups.id"), nullable=True)
    role: Mapped[str] = Column(String(100), nullable=False)

    # Relations
    user: Mapped["User"] = relationship(
        "User",
        primaryjoin="Person.emp_id == User.emp_id",
        foreign_keys="Person.emp_id",
        back_populates="person"
    )
    group: Mapped["Group"] = relationship(
        "Group",
        foreign_keys=[group_id],
        back_populates="members"
    )
    capabilities: Mapped[List["Capability"]] = relationship(
        "Capability", back_populates="person", cascade="all, delete-orphan"
    )
    responsibilities_owner: Mapped[List["Responsibility"]] = relationship(
        "Responsibility", foreign_keys="Responsibility.owner_id"
    )
    responsibilities_backup: Mapped[List["Responsibility"]] = relationship(
        "Responsibility", foreign_keys="Responsibility.backup_id"
    )
    dev_tasks: Mapped[List["Task"]] = relationship(
        "Task", foreign_keys="Task.developer_id"
    )
    test_tasks: Mapped[List["Task"]] = relationship(
        "Task", foreign_keys="Task.tester_id"
    )


class CapabilityDimension(Base):
    """Capability dimension model."""

    __tablename__ = "capability_dimensions"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name: Mapped[str] = Column(String(100), unique=True, nullable=False)
    description: Mapped[str] = Column(String(500), nullable=True)
    is_active: Mapped[bool] = Column(Boolean, default=True, nullable=False)


class Capability(Base):
    """Capability model for person skills."""

    __tablename__ = "capabilities"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    person_id: Mapped[int] = Column(Integer, ForeignKey("persons.id"), nullable=False)
    dimension: Mapped[str] = Column(String(100), nullable=False)
    level: Mapped[int] = Column(Integer, nullable=False)  # 1-5

    # Relations
    person: Mapped["Person"] = relationship("Person", back_populates="capabilities")


class Group(Base):
    """Group model for team organization."""

    __tablename__ = "groups"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name: Mapped[str] = Column(String(100), unique=True, nullable=False)
    leader_id: Mapped[int] = Column(Integer, ForeignKey("persons.id"), nullable=False)

    # Relations
    leader: Mapped["Person"] = relationship("Person", foreign_keys=[leader_id])
    members: Mapped[List["Person"]] = relationship(
        "Person",
        foreign_keys="Person.group_id",
        back_populates="group"
    )
    responsibilities: Mapped[List["Responsibility"]] = relationship(
        "Responsibility", back_populates="group"
    )
    key_figures: Mapped[List["KeyFigure"]] = relationship(
        "KeyFigure", back_populates="group", cascade="all, delete-orphan"
    )


class KeyFigure(Base):
    """Key figure model for group roles."""

    __tablename__ = "key_figures"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    group_id: Mapped[int] = Column(Integer, ForeignKey("groups.id"), nullable=False)
    type: Mapped[str] = Column(String(50), nullable=False)  # PL, MDE, etc.
    person_id: Mapped[int] = Column(Integer, ForeignKey("persons.id"), nullable=False)

    # Relations
    group: Mapped["Group"] = relationship("Group", back_populates="key_figures")
    person: Mapped["Person"] = relationship("Person")


class Responsibility(Base):
    """Responsibility model for ownership."""

    __tablename__ = "responsibilities"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name: Mapped[str] = Column(String(200), nullable=False)
    group_id: Mapped[int] = Column(Integer, ForeignKey("groups.id"), nullable=False)
    owner_id: Mapped[int] = Column(Integer, ForeignKey("persons.id"), nullable=False)
    backup_id: Mapped[int] = Column(Integer, ForeignKey("persons.id"), nullable=True)
    current_year_tasks: Mapped[List[int]] = Column(JSON, nullable=True)  # Store task ID list

    # Relations
    group: Mapped["Group"] = relationship("Group", back_populates="responsibilities")
    owner: Mapped["Person"] = relationship("Person", foreign_keys=[owner_id])
    backup: Mapped["Person"] = relationship("Person", foreign_keys=[backup_id])
    functions: Mapped[List["Function"]] = relationship("Function", back_populates="responsibility")
