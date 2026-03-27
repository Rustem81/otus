from __future__ import annotations

from typing import Annotated
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import require_admin
from app.core.config import get_settings
from app.core.database import get_db
from app.models.polling_error import PollingError
from app.schemas.admin import (
    ErrorStatsResponse,
    MonitoringResponse,
    SourceStatus,
    SourceStatusResponse,
)

router = APIRouter(dependencies=[require_admin])
settings = get_settings()


@router.get("/sources", response_model=SourceStatusResponse)
async def get_sources_status() -> SourceStatusResponse:
    """
    Get status of all P2P data sources.

    Admin only.
    """
    # For MVP, return mock status
    # In production, would check actual source health
    sources = [
        SourceStatus(
            id="mexc_rub_usdt",
            name="MEXC RUB/USDT",
            type="pair",
            status="ok",
            last_updated=datetime.now(timezone.utc),
        ),
        SourceStatus(
            id="p2p_army",
            name="p2p.army API",
            type="source",
            status="ok" if settings.P2P_DATA_SOURCE == "p2p_army" else "mock",
            last_updated=datetime.now(timezone.utc),
        ),
    ]

    return SourceStatusResponse(sources=sources)


@router.put("/sources/{source_id}", response_model=SourceStatus)
async def toggle_source(
    source_id: str,
    enabled: bool,
) -> SourceStatus:
    """
    Enable or disable a data source.

    Admin only.
    """
    # For MVP, just return the status
    # In production, would actually toggle the source
    return SourceStatus(
        id=source_id,
        name=source_id.replace("_", " ").upper(),
        type="pair",
        status="ok" if enabled else "disabled",
        last_updated=datetime.now(timezone.utc),
    )


@router.get("/monitoring", response_model=MonitoringResponse)
async def get_monitoring_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MonitoringResponse:
    """
    Get monitoring statistics for the last 24 hours.

    Admin only.
    """
    # Get error counts by hour
    since = datetime.now(timezone.utc) - timedelta(hours=24)

    stmt = (
        select(
            PollingError.hour_bucket,
            PollingError.error_type,
            func.count(PollingError.id).label("count"),
        )
        .where(PollingError.hour_bucket >= since)
        .group_by(PollingError.hour_bucket, PollingError.error_type)
        .order_by(PollingError.hour_bucket.desc())
    )

    result = await db.execute(stmt)
    rows = result.all()

    # Aggregate by hour
    hourly_stats = {}
    for row in rows:
        hour_key = row.hour_bucket.isoformat()
        if hour_key not in hourly_stats:
            hourly_stats[hour_key] = {"total": 0, "by_type": {}}
        hourly_stats[hour_key]["total"] += row.count
        hourly_stats[hour_key]["by_type"][row.error_type] = row.count

    # Get total errors
    total_errors = sum(row.count for row in rows)

    return MonitoringResponse(
        status="ok",
        total_errors_24h=total_errors,
        hourly_stats=hourly_stats,
        sources=[
            {
                "id": "p2p_army",
                "status": "ok",
                "errors_24h": total_errors,
            }
        ],
    )


@router.get("/errors", response_model=ErrorStatsResponse)
async def get_error_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
    hours: int = 24,
) -> ErrorStatsResponse:
    """
    Get detailed error statistics.

    Admin only.
    """
    since = datetime.now(timezone.utc) - timedelta(hours=hours)

    stmt = (
        select(
            PollingError.error_type,
            func.count(PollingError.id).label("count"),
        )
        .where(PollingError.hour_bucket >= since)
        .group_by(PollingError.error_type)
    )

    result = await db.execute(stmt)
    rows = result.all()

    errors_by_type = {row.error_type: row.count for row in rows}
    total = sum(errors_by_type.values())

    return ErrorStatsResponse(
        total=total,
        by_type=errors_by_type,
        period_hours=hours,
    )
