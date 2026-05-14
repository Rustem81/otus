"""Merchant blacklist endpoints."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user, require_user
from app.core.database import get_db
from app.models.user import User
from app.repositories.blacklist_repository import BlacklistRepository

router = APIRouter()


class BlacklistEntry(BaseModel):
    merchant_id: str
    created_at: str | None = None

    model_config = {"from_attributes": True}


class BlacklistAddRequest(BaseModel):
    merchant_id: str


class BlacklistResponse(BaseModel):
    items: list[BlacklistEntry]


@router.get("", response_model=BlacklistResponse, dependencies=[require_user])
async def get_blacklist(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BlacklistResponse:
    """Get user's merchant blacklist."""
    repo = BlacklistRepository(db)
    entries = await repo.get_all(current_user.id)
    return BlacklistResponse(
        items=[
            BlacklistEntry(
                merchant_id=e.merchant_id,
                created_at=e.created_at.isoformat() if e.created_at else None,
            )
            for e in entries
        ]
    )


@router.post("", response_model=BlacklistEntry, dependencies=[require_user])
async def add_to_blacklist(
    data: BlacklistAddRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BlacklistEntry:
    """Add merchant to blacklist."""
    repo = BlacklistRepository(db)
    try:
        entry = await repo.add(current_user.id, data.merchant_id)
        await db.commit()
        return BlacklistEntry(
            merchant_id=entry.merchant_id,
            created_at=entry.created_at.isoformat() if entry.created_at else None,
        )
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Merchant already blacklisted")


@router.delete("/{merchant_id}", dependencies=[require_user])
async def remove_from_blacklist(
    merchant_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Remove merchant from blacklist."""
    repo = BlacklistRepository(db)
    removed = await repo.remove(current_user.id, merchant_id)
    await db.commit()
    if not removed:
        raise HTTPException(status_code=404, detail="Merchant not in blacklist")
    return {"detail": "Merchant removed from blacklist"}
