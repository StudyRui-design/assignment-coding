"""
Market Pulse — A-Share Monitoring Dashboard (Backend)

FastAPI server that:
  1. Warms up caches at startup via APScheduler.
  2. Exposes RESTful endpoints returning real-time A-share market data.
  3. All data is served from an in-memory cache (reads < 10 ms).

Run:
    python main.py
    → API docs at http://localhost:8000/docs
"""

import logging
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import logging_config  # noqa: F401 — initialise stdlib logging
import _proxy_bypass   # noqa: F401 — must execute before any HTTP call

from cache.memory_cache import cache
from scheduler import start as start_scheduler, stop as stop_scheduler, scheduler

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    start_scheduler()
    logger.info("Application startup complete")
    yield
    # Shutdown
    stop_scheduler()
    logger.info("Application shutdown complete")


app = FastAPI(
    title="Market Pulse API",
    version="0.1.0",
    description="A股市场脉搏监控 — 后端数据接口",
    lifespan=lifespan,
)

# Allow the Next.js dev server (and any local UI) to call us
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global exception handler ─────────────────────────────────────────
# Catches unhandled exceptions in route handlers and returns JSON
# instead of leaking HTML 500 stack traces to the frontend.

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# ── Endpoints ────────────────────────────────────────────────────────

@app.get("/api/v1/market/health")
def health():
    """Readiness probe with per-key cache TTL age and scheduler status."""
    import time as _time

    cache_status: dict[str, object] = {}
    cache_keys = ("indices", "sectors", "breadth", "anomalies")

    for key in cache_keys:
        entry = cache._store.get(key)
        if entry is not None:
            expires_at, value = entry
            ttl_remaining = round(expires_at - _time.monotonic(), 1)
            cache_status[key] = {
                "populated": value is not None,
                "ttl_remaining_s": max(ttl_remaining, 0.0),
            }
        else:
            cache_status[key] = {"populated": False, "ttl_remaining_s": 0.0}

    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cache_status": cache_status,
        "scheduler_running": scheduler.running if scheduler else False,
    }


@app.get("/api/v1/market/indices")
def market_indices():
    """Latest prices for all tracked major indices."""
    return {
        "data": cache.get("indices") or [],
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


@app.get("/api/v1/market/indices/history")
def index_history(code: str = Query(..., description="Index code e.g. 000001"),
                  days: int = Query(30, ge=1, le=365)):
    """
    Daily OHLCV history for one index.

    Codes: 000001(上证) 399001(深证) 000300(沪深300) 399006(创业板) 000688(科创50)
    """
    from fetcher.index_data import get_index_history
    return {
        "code": code,
        "data": get_index_history(code, days),
    }


@app.get("/api/v1/market/indices/history/batch")
def index_history_batch(days: int = Query(30, ge=1, le=365)):
    """Daily OHLCV history for all 5 tracked indices in a single request."""
    from fetcher.index_data import get_all_index_history
    return {
        "data": get_all_index_history(days),
        "days": days,
    }


@app.get("/api/v1/market/sectors")
def market_sectors():
    """Top + bottom industry-sector rankings."""
    return {
        "data": cache.get("sectors") or [],
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


@app.get("/api/v1/market/breadth")
def market_breadth():
    """Advancing / declining / unchanged counts for the whole A-share market."""
    breadth = cache.get("breadth")
    return {
        "data": breadth.model_dump() if breadth else None,
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


@app.get("/api/v1/market/anomalies")
def market_anomalies():
    """Active anomaly events detected by the rule engine."""
    return {
        "data": cache.get("anomalies") or [],
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


@app.get("/api/v1/market/overview")
def market_overview():
    """Aggregated snapshot: indices + sectors + breadth + anomalies."""
    indices = cache.get("indices") or []
    sectors = cache.get("sectors") or []
    breadth = cache.get("breadth")
    anomalies = cache.get("anomalies") or []

    return {
        "indices": indices,
        "sectors": sectors,
        "breadth": breadth.model_dump() if breadth else None,
        "anomalies": anomalies,
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


# ── Entry point ──────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
