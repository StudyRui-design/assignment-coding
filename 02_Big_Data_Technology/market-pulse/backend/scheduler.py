"""
Lightweight background scheduler that refreshes cached data on a fixed cadence.

- Indices:  every 30 s (spot prices change fast during trading hours).
- Sectors:  every 60 s.
- Breadth:  every 60 s (expensive — queries all ~5000 A-shares).
"""

from apscheduler.schedulers.background import BackgroundScheduler

from cache.memory_cache import cache
from fetcher.index_data import get_indices
from fetcher.sector_data import get_sectors
from fetcher.market_breadth import get_market_breadth
from fetcher.anomaly import detect_all_anomalies

scheduler = BackgroundScheduler(daemon=True)


def _refresh_indices() -> None:
    try:
        indices = get_indices()
        cache.set("indices", indices, ttl=45)  # slightly > poll interval
    except Exception:
        pass  # stale cache is better than crashing the app


def _refresh_sectors() -> None:
    try:
        sectors = get_sectors(top_n=20)
        cache.set("sectors", sectors, ttl=90)
    except Exception:
        pass


def _refresh_breadth() -> None:
    try:
        breadth = get_market_breadth()
        cache.set("breadth", breadth, ttl=90)

        # Anomalies depend on indices + breadth → recompute together
        indices = cache.get("indices") or []
        anomalies = detect_all_anomalies(indices, breadth)
        cache.set("anomalies", anomalies, ttl=90)
    except Exception:
        pass


def start() -> None:
    """Register jobs and start the scheduler."""
    scheduler.add_job(_refresh_indices, "interval", seconds=30, id="indices")
    scheduler.add_job(_refresh_sectors, "interval", seconds=60, id="sectors")
    scheduler.add_job(_refresh_breadth, "interval", seconds=60, id="breadth")

    # Run once immediately so the cache is warm when the first request arrives
    _refresh_indices()
    _refresh_sectors()
    _refresh_breadth()

    scheduler.start()


def stop() -> None:
    scheduler.shutdown(wait=False)
