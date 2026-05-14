from __future__ import annotations

import enum

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class RiskProfile(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TraderProfile(Base):
    __tablename__ = "trader_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    payment_methods: Mapped[list[str]] = mapped_column(
        ARRAY(String), default=list, nullable=False
    )
    min_amount: Mapped[float] = mapped_column(Numeric(18, 2), nullable=True)
    max_amount: Mapped[float] = mapped_column(Numeric(18, 2), nullable=True)
    currency_pair: Mapped[str] = mapped_column(
        String(20), default="RUB_USDT", nullable=False
    )
    risk_profile: Mapped[RiskProfile] = mapped_column(
        String(10), default=RiskProfile.MEDIUM, nullable=False
    )
    commission_percent: Mapped[float | None] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    commission_fixed: Mapped[float | None] = mapped_column(
        Numeric(18, 2), nullable=True
    )
    kyc_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    country: Mapped[str | None] = mapped_column(String(10), default="RU", nullable=True)
    kyc_limit_warning: Mapped[float | None] = mapped_column(
        Numeric(18, 2), nullable=True
    )

    user: Mapped[User] = relationship("User", back_populates="profile")
