"""
Lightweight background scheduler that refreshes cached data on a fixed cadence.

Jobs (4 registered):
  - Indices:  every 30 s (spot prices change fast during trading hours)
  - Sectors:  every 65 s (staggered to avoid overlapping with other jobs)
  - Breadth:  every 70 s (expensive — queries all ~5000 A-shares, runs alone)
  - Anomaly:  every 75 s (rule engine over indices + breadth — lightweight)

Design decisions:
  - Jobs are **staggered** so they never start at the same time,
    preventing network congestion & external API rate-limiting.
  - A dedicated thread-pool executor (max_workers=4) avoids blocking the
    uvicorn async event loop.
  - All external HTTP calls include generous but finite timeouts so a
    stuck request cannot park a worker forever.

All errors are logged rather than swallowed; stale cache is preferred over crashing.
"""

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

from cache.memory_cache import cache
from fetcher.index_data import get_indices
from fetcher.sector_data import get_sectors
from fetcher.market_breadth import get_market_breadth
from fetcher.anomaly import detect_all_anomalies

logger = logging.getLogger(__name__)

_executor = ThreadPoolExecutor(max_workers=4)
scheduler = BackgroundScheduler(daemon=True, executors={"default": _executor},
                                misfire_grace_time=30)


def _refresh_indices() -> None:
    try:
        indices = get_indices()
        cache.set("indices", indices, ttl=60)
        logger.debug("Indices refreshed: %d", len(indices))
    except Exception:
        logger.exception("Failed to refresh index data")


def _refresh_sectors() -> None:
    try:
        sectors = get_sectors(top_n=20)
        cache.set("sectors", sectors, ttl=90)
        logger.debug("Sectors refreshed: %d", len(sectors))
    except Exception:
        logger.exception("Failed to refresh sector data")


def _refresh_breadth() -> None:
    try:
        breadth = get_market_breadth()
        cache.set("breadth", breadth, ttl=150)
        logger.debug("Breadth refreshed: advancing=%d declining=%d total=%d",
                     breadth.advancing, breadth.declining, breadth.total)
    except Exception:
        logger.exception("Failed to refresh market breadth")


def _refresh_anomalies() -> None:
    """Independent anomaly detection — reads indices + breadth from cache."""
    try:
        indices = cache.get("indices") or []
        breadth = cache.get("breadth")
        anomalies = detect_all_anomalies(indices, breadth)
        cache.set("anomalies", anomalies, ttl=90)
        if anomalies:
            logger.info("Anomalies detected: %d events", len(anomalies))
        else:
            logger.debug("Anomalies: none")
    except Exception:
        logger.exception("Failed to run anomaly detection")


def start() -> None:
    """Register jobs with staggered intervals and start the scheduler.

    Jobs are spread across the 60-second cycle so they never fire
    simultaneously, preventing external API rate-limiting:

      indices  →  0 s, 30 s        (every 30 s)
      sectors  →  5 s              (every 60 s, offset by 5 s)
      breadth  → 10 s              (every 120 s, offset by 10 s — heavy)
      anomaly  → 15 s              (every 60 s, offset by 15 s)
    """
    # All jobs aligned to minute boundaries with staggered offsets.
    # Using start_date with epoch-based alignment ensures jobs never fire
    # at the same second, preventing external API rate-limiting.
    scheduler.add_job(_refresh_indices,  "interval", seconds=30, id="indices",
                      start_date="1970-01-01T00:00:00",
                      max_instances=1, misfire_grace_time=15)
    scheduler.add_job(_refresh_sectors,  "interval", seconds=60, id="sectors",
                      start_date="1970-01-01T00:00:05",
                      max_instances=1, misfire_grace_time=30)
    scheduler.add_job(_refresh_breadth,  "interval", seconds=120, id="breadth",
                      start_date="1970-01-01T00:00:10",
                      max_instances=1, misfire_grace_time=30)
    scheduler.add_job(_refresh_anomalies,"interval", seconds=60, id="anomalies",
                      start_date="1970-01-01T00:00:15",
                      max_instances=1, misfire_grace_time=30)

    # Run once immediately — but sequentially, NOT concurrently
    logger.info("Warming cache (sequential)…")
    _refresh_indices()
    _refresh_breadth()
    _refresh_sectors()
    _refresh_anomalies()

    scheduler.start()
    logger.info("Scheduler started with %d jobs", len(scheduler.get_jobs()))


def stop() -> None:
    scheduler.shutdown(wait=False)
    logger.info("Scheduler stopped")
