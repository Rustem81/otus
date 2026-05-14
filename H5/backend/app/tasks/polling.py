from __future__ import annotations

import asyncio
import logging
import random
from datetime import datetime, timezone
from typing import Any

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import async_session
from app.core.redis import redis_client
from app.models.advertisement import Direction
from app.models.polling_error import PollingError
from app.services.p2p_processor import P2PDataProcessor
from app.services.p2p_source import MockP2PClient, P2PArmyClient, P2PDataSource
from app.services.reference_price import ReferencePriceCalculator

logger = logging.getLogger(__name__)
settings = get_settings()

# Global state
_polling_task: asyncio.Task | None = None
_polling_running = False


class PollingErrorAggregator:
    """Aggregate polling errors for admin monitoring."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def log_error(
        self,
        source: str,
        error_type: str,
        message: str,
    ) -> None:
        """Log polling error to database."""
        from sqlalchemy import insert

        hour_bucket = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)

        error = PollingError(
            source=source,
            error_type=error_type,
            message=message,
            hour_bucket=hour_bucket,
        )
        self._session.add(error)
        await self._session.flush()


async def _acquire_poll_lock(redis: Redis, lock_key: str, ttl: int = 60) -> bool:
    """
    Try to acquire distributed lock for polling.

    Prevents multiple instances from polling simultaneously.
    """
    acquired = await redis.set(lock_key, "1", nx=True, ex=ttl)
    return bool(acquired)


async def _release_poll_lock(redis: Redis, lock_key: str) -> None:
    """Release distributed lock."""
    await redis.delete(lock_key)


async def _poll_with_backoff(
    data_source: P2PDataSource,
    processor: P2PDataProcessor,
    error_aggregator: PollingErrorAggregator,
    currency: str,
    direction: Direction,
) -> tuple[int, int]:
    """
    Poll data source with exponential backoff on error.

    Returns:
        Tuple of (processed_count, error_count)
    """
    max_retries = 3
    base_delay = 1.0

    for attempt in range(max_retries):
        try:
            raw_data = await data_source.get_order_book(
                market="mexc",
                fiat=currency,
                asset="USDT",
                side=direction.value,
                limit=50,
            )

            if raw_data.get("status") != 1:
                raise ValueError(f"Invalid response status: {raw_data.get('status')}")

            ads = raw_data.get("ads", [])
            processed, errors = await processor.process_advertisements(
                ads, currency, direction
            )

            logger.info(f"Processed {processed} ads for {currency} {direction.value}")
            return processed, errors

        except Exception as e:
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            logger.warning(f"Poll attempt {attempt + 1} failed: {e}. Retrying in {delay:.1f}s")

            if attempt < max_retries - 1:
                await asyncio.sleep(delay)
            else:
                logger.error(f"All poll attempts failed for {currency} {direction.value}: {e}")
                await error_aggregator.log_error(
                    source=settings.P2P_DATA_SOURCE,
                    error_type=type(e).__name__,
                    message=str(e)[:500],
                )
                return 0, 0

    return 0, 0


async def _polling_loop() -> None:
    """Main polling loop."""
    global _polling_running

    logger.info("Starting P2P polling loop")

    # Initialize data source based on config
    if settings.P2P_DATA_SOURCE == "p2p_army":
        data_source: P2PDataSource = P2PArmyClient()
    else:
        data_source = MockP2PClient()

    lock_key = "polling:lock"
    redis = redis_client

    while _polling_running:
        session: AsyncSession | None = None
        try:
            # Try to acquire lock
            if not await _acquire_poll_lock(redis, lock_key):
                logger.debug("Another instance is polling, skipping")
                await asyncio.sleep(settings.POLLING_INTERVAL_SEC)
                continue

            try:
                session = async_session()
                processor = P2PDataProcessor(session)
                error_aggregator = PollingErrorAggregator(session)

                # Poll for both BUY and SELL
                for direction in [Direction.BUY, Direction.SELL]:
                    if not _polling_running:
                        break

                    processed, errors = await _poll_with_backoff(
                        data_source,
                        processor,
                        error_aggregator,
                        "RUB",
                        direction,
                    )

                # Mark stale ads as inactive
                stale_count = await processor.mark_stale_ads(settings.INACTIVE_TTL_SEC)
                if stale_count > 0:
                    logger.info(f"Marked {stale_count} ads as inactive")

                # Calculate reference prices
                ref_calc = ReferencePriceCalculator(session)
                for direction in [Direction.BUY, Direction.SELL]:
                    ref_price = await ref_calc.calculate_reference_price("RUB", direction)
                    if ref_price:
                        logger.debug(f"Reference price {direction.value}: {ref_price}")

                await session.commit()

            finally:
                await _release_poll_lock(redis, lock_key)
                if session:
                    await session.close()

            # Wait for next polling interval
            await asyncio.sleep(settings.POLLING_INTERVAL_SEC)

        except Exception as e:
            logger.exception(f"Unexpected error in polling loop: {e}")
            await asyncio.sleep(settings.POLLING_INTERVAL_SEC)

    logger.info("Polling loop stopped")

    # Cleanup
    if hasattr(data_source, 'close'):
        await data_source.close()


async def start_polling_task() -> None:
    """Start the polling background task."""
    global _polling_task, _polling_running

    if _polling_task is not None and not _polling_task.done():
        logger.warning("Polling task already running")
        return

    _polling_running = True
    _polling_task = asyncio.create_task(_polling_loop())
    logger.info("Polling task started")


async def stop_polling_task() -> None:
    """Stop the polling background task."""
    global _polling_task, _polling_running

    _polling_running = False

    if _polling_task is not None and not _polling_task.done():
        _polling_task.cancel()
        try:
            await _polling_task
        except asyncio.CancelledError:
            pass

    logger.info("Polling task stopped")
