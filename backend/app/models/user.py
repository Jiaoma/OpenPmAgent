"""User model."""
from typing import List, TYPE_CHECKING
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship, Mapped
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.audit import AuditLog
    from app.models.team import Person


class User(Base):
    """User model for authentication."""

    __tablename__ = "users"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    emp_id: Mapped[str] = Column(String(50), unique=True, index=True, nullable=False)
    is_admin: Mapped[bool] = Column(Boolean, default=False, nullable=False)
    password_hash: Mapped[str] = Column(String(255), nullable=True)

    # Relations - use primaryjoin to specify the join condition
    person: Mapped["Person"] = relationship(
        "Person",
        primaryjoin="User.emp_id == Person.emp_id",
        foreign_keys="Person.emp_id",
        back_populates="user",
        uselist=False
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="user")
