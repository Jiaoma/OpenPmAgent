"""Audit log model."""
from typing import List, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship, Mapped
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class AuditLog(Base):
    """Audit log model for tracking operations."""

    __tablename__ = "audit_logs"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False)
    action: Mapped[str] = Column(
        String(100), nullable=False
    )  # create, update, delete
    resource_type: Mapped[str] = Column(
        String(100), nullable=False
    )  # person, group, task, etc.
    resource_id: Mapped[int] = Column(Integer, nullable=False)
    changes: Mapped[dict] = Column(JSON, nullable=True)
    timestamp: Mapped[datetime] = Column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    status: Mapped[str] = Column(
        String(50), default="success"
    )  # success, failure

    # Relations
    user: Mapped["User"] = relationship("User", back_populates="audit_logs")
