from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Merchant(Base):
    __tablename__ = "merchants"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    external_id: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, comment="ID мерчанта на бирже"
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    trades_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    success_rate: Mapped[float | None] = mapped_column(
        Float, nullable=True, comment="0 to 1"
    )
    closing_speed: Mapped[float | None] = mapped_column(
        Float, nullable=True, comment="seconds"
    )
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    advertisements: Mapped[list[Advertisement]] = relationship(
        "Advertisement", back_populates="merchant"
    )
