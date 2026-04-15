"""Repository for advertisement view history."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.view_history import ViewHistory


class ViewHistoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record_view(self, user_id: str, advertisement_id: str) -> ViewHistory:
        """Record that user viewed an advertisement."""
        entry = ViewHistory(user_id=user_id, advertisement_id=advertisement_id)
        self._session.add(entry)
        await self._session.flush()
        return entry

    async def get_recent(self, user_id: str, limit: int = 50) -> list[ViewHistory]:
        """Get recent view history for user."""
        stmt = (
            select(ViewHistory)
            .where(ViewHistory.user_id == user_id)
            .order_by(ViewHistory.viewed_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
