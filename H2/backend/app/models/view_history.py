"""View history model — tracks which advertisements a user has viewed."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ViewHistory(Base):
    __tablename__ = "view_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    advertisement_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("advertisements.id", ondelete="CASCADE"), nullable=False
    )
    viewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_view_history_user_id", "user_id"),
    )
