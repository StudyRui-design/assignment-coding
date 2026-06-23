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

from datetime import datetime
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from cache.memory_cache import cache
from scheduler import start as start_scheduler, stop as stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    start_scheduler()
    yield
    # Shutdown
    stop_scheduler()


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


# ── Endpoints ──────────────────────────────────────────────────────

@app.get("/api/v1/market/health")
def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


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


# ── Entry point ────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
