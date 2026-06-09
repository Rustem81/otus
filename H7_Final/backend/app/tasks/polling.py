from __future__ import annotations

import asyncio
import random
from datetime import UTC, datetime

import structlog
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import async_session
from app.core.metrics import p2p_ads_active_total, p2p_polling_duration_seconds
from app.core.redis import redis_client
from app.models.advertisement import Direction
from app.models.polling_error import PollingError
from app.services.p2p_processor import P2PDataProcessor
from app.services.p2p_source import MockP2PClient, P2PArmyClient, P2PDataSource
from app.services.reference_price import ReferencePriceCalculator

logger = structlog.get_logger()
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

        hour_bucket = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)

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

            logger.info("poll_processed", currency=currency, direction=direction.value, processed=processed)
            return processed, errors

        except Exception as e:
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            logger.warning("poll_attempt_failed", attempt=attempt + 1, error=str(e), retry_delay=f"{delay:.1f}s")

            if attempt < max_retries - 1:
                await asyncio.sleep(delay)
            else:
                logger.error("poll_all_attempts_failed", currency=currency, direction=direction.value, error=str(e))
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

    logger.info("polling_loop_starting")

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
                logger.debug("polling_lock_held", msg="Another instance is polling, skipping")
                await asyncio.sleep(settings.POLLING_INTERVAL_SEC)
                continue

            try:
                session = async_session()
                processor = P2PDataProcessor(session)
                error_aggregator = PollingErrorAggregator(session)

                # Time the polling cycle
                import time as _time
                _poll_start = _time.monotonic()

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
                    logger.info("polling_stale_ads_marked", stale_count=stale_count)

                # Calculate reference prices
                ref_calc = ReferencePriceCalculator(session)
                for direction in [Direction.BUY, Direction.SELL]:
                    ref_price = await ref_calc.calculate_reference_price("RUB", direction)
                    if ref_price:
                        logger.debug("polling_reference_price", direction=direction.value, price=ref_price)

                await session.commit()

                # Record polling duration metric
                _poll_duration = _time.monotonic() - _poll_start
                p2p_polling_duration_seconds.observe(_poll_duration)

                # Update active ads gauge
                from sqlalchemy import func, select

                from app.models.advertisement import Advertisement

                for dir_label in [Direction.BUY, Direction.SELL]:
                    count_result = await session.execute(
                        select(func.count(Advertisement.id)).where(
                            Advertisement.is_active.is_(True),
                            Advertisement.direction == dir_label,
                        )
                    )
                    active_count = count_result.scalar() or 0
                    p2p_ads_active_total.labels(direction=dir_label.value).set(active_count)

                await session.commit()

            finally:
                await _release_poll_lock(redis, lock_key)
                if session:
                    await session.close()

            # Wait for next polling interval
            await asyncio.sleep(settings.POLLING_INTERVAL_SEC)

        except Exception as e:
            logger.exception("polling_loop_unexpected_error", error=str(e))
            await asyncio.sleep(settings.POLLING_INTERVAL_SEC)

    logger.info("polling_loop_stopped")

    # Cleanup
    if hasattr(data_source, 'close'):
        await data_source.close()


async def start_polling_task() -> None:
    """Start the polling background task."""
    global _polling_task, _polling_running

    if _polling_task is not None and not _polling_task.done():
        logger.warning("polling_task_already_running")
        return

    _polling_running = True
    _polling_task = asyncio.create_task(_polling_loop())
    logger.info("polling_task_started")


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

    logger.info("polling_task_stopped")
