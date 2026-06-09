"""View history endpoints."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user, require_user
from app.core.database import get_db
from app.models.user import User
from app.repositories.history_repository import ViewHistoryRepository

router = APIRouter()


class ViewHistoryEntry(BaseModel):
    advertisement_id: str
    viewed_at: str

    model_config = {"from_attributes": True}


class ViewHistoryResponse(BaseModel):
    items: list[ViewHistoryEntry]


class RecordViewRequest(BaseModel):
    advertisement_id: str


@router.get("", response_model=ViewHistoryResponse, dependencies=[require_user])
async def get_view_history(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ViewHistoryResponse:
    """Get user's recent view history (last 50)."""
    repo = ViewHistoryRepository(db)
    entries = await repo.get_recent(current_user.id, limit=50)
    return ViewHistoryResponse(
        items=[
            ViewHistoryEntry(
                advertisement_id=e.advertisement_id,
                viewed_at=e.viewed_at.isoformat(),
            )
            for e in entries
        ]
    )


@router.post("", response_model=ViewHistoryEntry, dependencies=[require_user])
async def record_view(
    data: RecordViewRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ViewHistoryEntry:
    """Record that user viewed an advertisement."""
    repo = ViewHistoryRepository(db)
    entry = await repo.record_view(current_user.id, data.advertisement_id)
    await db.commit()
    return ViewHistoryEntry(
        advertisement_id=entry.advertisement_id,
        viewed_at=entry.viewed_at.isoformat(),
    )
