"""Architecture models."""
from typing import List, TYPE_CHECKING
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Mapped
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.team import Responsibility


class Module(Base):
    """Module model for software architecture."""

    __tablename__ = "modules"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name: Mapped[str] = Column(String(200), nullable=False)
    parent_id: Mapped[int] = Column(Integer, ForeignKey("modules.id"), nullable=True)

    # Relations
    parent: Mapped["Module"] = relationship(
        "Module", remote_side=[id], back_populates="children"
    )
    children: Mapped[List["Module"]] = relationship(
        "Module", back_populates="parent", cascade="all, delete-orphan"
    )
    function_modules: Mapped[List["FunctionModule"]] = relationship(
        "FunctionModule", back_populates="module"
    )


class Function(Base):
    """Function model for software features."""

    __tablename__ = "functions"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name: Mapped[str] = Column(String(200), nullable=False)
    parent_id: Mapped[int] = Column(Integer, ForeignKey("functions.id"), nullable=True)
    responsibility_id: Mapped[int] = Column(
        Integer, ForeignKey("responsibilities.id"), nullable=True
    )

    # Relations
    parent: Mapped["Function"] = relationship(
        "Function", remote_side=[id], back_populates="children"
    )
    children: Mapped[List["Function"]] = relationship(
        "Function", back_populates="parent", cascade="all, delete-orphan"
    )
    responsibility: Mapped["Responsibility"] = relationship(
        "Responsibility", back_populates="functions"
    )
    function_modules: Mapped[List["FunctionModule"]] = relationship(
        "FunctionModule", back_populates="function"
    )
    source_flows: Mapped[List["DataFlow"]] = relationship(
        "DataFlow", foreign_keys="DataFlow.source_function_id"
    )
    target_flows: Mapped[List["DataFlow"]] = relationship(
        "DataFlow", foreign_keys="DataFlow.target_function_id"
    )


class FunctionModule(Base):
    """Function-Module association model."""

    __tablename__ = "function_modules"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    function_id: Mapped[int] = Column(Integer, ForeignKey("functions.id"), nullable=False)
    module_id: Mapped[int] = Column(Integer, ForeignKey("modules.id"), nullable=False)
    order: Mapped[int] = Column(Integer, default=0, nullable=False)

    # Relations
    function: Mapped["Function"] = relationship("Function", back_populates="function_modules")
    module: Mapped["Module"] = relationship("Module", back_populates="function_modules")


class DataFlow(Base):
    """Data flow model for module interactions."""

    __tablename__ = "data_flows"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    source_function_id: Mapped[int] = Column(
        Integer, ForeignKey("functions.id"), nullable=False
    )
    target_function_id: Mapped[int] = Column(
        Integer, ForeignKey("functions.id"), nullable=False
    )
    order: Mapped[int] = Column(Integer, default=0, nullable=False)
    description: Mapped[str] = Column(String(500), nullable=True)

    # Relations
    source_function: Mapped["Function"] = relationship(
        "Function", foreign_keys=[source_function_id]
    )
    target_function: Mapped["Function"] = relationship(
        "Function", foreign_keys=[target_function_id]
    )
