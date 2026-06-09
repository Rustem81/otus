from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class SourceStatus(BaseModel):
    """Status of a data source."""

    id: str
    name: str
    type: str  # pair or source
    status: str  # ok, degraded, down, disabled
    last_updated: datetime


class SourceStatusResponse(BaseModel):
    """Response with list of source statuses."""

    sources: list[SourceStatus]


class MonitoringResponse(BaseModel):
    """Monitoring statistics response."""

    status: str
    total_errors_24h: int
    hourly_stats: dict[str, Any]
    sources: list[dict[str, Any]]


class ErrorStatsResponse(BaseModel):
    """Error statistics response."""

    total: int
    by_type: dict[str, int]
    period_hours: int
