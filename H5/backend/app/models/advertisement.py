from __future__ import annotations

import enum
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Direction(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


class Advertisement(Base):
    __tablename__ = "advertisements"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    external_id: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, comment="ID объявления на бирже"
    )
    price: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    volume: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    min_limit: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    max_limit: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    direction: Mapped[Direction] = mapped_column(String(4), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    payment_methods: Mapped[list[str]] = mapped_column(
        ARRAY(String), default=list, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    risk_score: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    risk_category: Mapped[str | None] = mapped_column(
        String(10), nullable=True, comment="low/medium/high"
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    merchant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False
    )
    merchant: Mapped[Merchant] = relationship("Merchant", back_populates="advertisements")

    __table_args__ = (
        Index("ix_ads_currency_direction_active", "currency", "direction", "is_active"),
        Index("ix_ads_fetched_at", "fetched_at"),
        Index("ix_ads_merchant_id", "merchant_id"),
    )
