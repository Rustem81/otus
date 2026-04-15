from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class UserRole(str, enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        String(10), default=UserRole.USER, nullable=False
    )
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    onboarding_completed: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    profile: Mapped[TraderProfile | None] = relationship(
        "TraderProfile", back_populates="user", uselist=False
    )
    saved_filters: Mapped[SavedFilters | None] = relationship(
        "SavedFilters", back_populates="user", uselist=False
    )
