"""
Lightweight background scheduler that refreshes cached data on a fixed cadence.

Jobs (4 registered):
  - Indices:  every 30 s (spot prices change fast during trading hours)
  - Sectors:  every 60 s
  - Breadth:  every 60 s (expensive — queries all ~5000 A-shares)
  - Anomaly:  every 60 s (rule engine over indices + breadth — decoupled from breadth)

All errors are logged rather than swallowed; stale cache is preferred over crashing.
"""

import logging

from apscheduler.schedulers.background import BackgroundScheduler

from cache.memory_cache import cache
from fetcher.index_data import get_indices
from fetcher.sector_data import get_sectors
from fetcher.market_breadth import get_market_breadth
from fetcher.anomaly import detect_all_anomalies

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler(daemon=True)


def _refresh_indices() -> None:
    try:
        indices = get_indices()
        cache.set("indices", indices, ttl=45)  # slightly > poll interval
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
        cache.set("breadth", breadth, ttl=90)
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
    """Register jobs and start the scheduler."""
    scheduler.add_job(_refresh_indices, "interval", seconds=30, id="indices")
    scheduler.add_job(_refresh_sectors, "interval", seconds=60, id="sectors")
    scheduler.add_job(_refresh_breadth, "interval", seconds=60, id="breadth")
    scheduler.add_job(_refresh_anomalies, "interval", seconds=60, id="anomalies")

    # Run once immediately so the cache is warm when the first request arrives
    _refresh_indices()
    _refresh_sectors()
    _refresh_breadth()
    _refresh_anomalies()

    scheduler.start()
    logger.info("Scheduler started with %d jobs", len(scheduler.get_jobs()))


def stop() -> None:
    scheduler.shutdown(wait=False)
    logger.info("Scheduler stopped")
