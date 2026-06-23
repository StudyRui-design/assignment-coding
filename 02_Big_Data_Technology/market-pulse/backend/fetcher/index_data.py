"""
Fetcher: major A-share index data.

Uses AKShare's Sina-based functions (`stock_zh_index_spot_sina`,
`stock_zh_index_daily`) to avoid East Money's TLS-fingerprint blocking
that affects Python's default ssl module on this machine.

East Money blocks Python's schannel/ssl handshake; Sina does not.
"""

import akshare as ak

from datetime import datetime
from fetcher import IndexData


# ── Constants ──────────────────────────────────────────────────────

# Sina symbol → our internal code + display name
# AKShare's stock_zh_index_spot_sina returns rows keyed by Sina symbols.
SINA_SYMBOLS = {
    "sh000001": ("000001", "上证指数"),
    "sz399001": ("399001", "深证成指"),
    "sh000300": ("000300", "沪深300"),
    "sz399006": ("399006", "创业板指"),
    "sh000688": ("000688", "科创50"),
}

# History lookup: our code → AKShare symbol (same for Sina daily API)
HISTORY_SYMBOL_MAP = {
    "000001": "sh000001",
    "399001": "sz399001",
    "000300": "sh000300",
    "399006": "sz399006",
    "000688": "sh000688",
}


# ── Public API ─────────────────────────────────────────────────────

def get_indices() -> list[IndexData]:
    """Real-time spot quotes for all tracked major indices (via Sina)."""
    df = ak.stock_zh_index_spot_sina()

    # The DataFrame uses Sina symbols as index/key.  Columns ≈
    #   名称, 最新价, 涨跌幅, 涨跌额, 成交量, 成交额, 今开, 昨收, ...
    results: list[IndexData] = []

    for sina_sym, (code, name) in SINA_SYMBOLS.items():
        row = df[df["代码"] == sina_sym]  # "代码" column contains e.g. "sh000001"
        if row.empty:
            continue

        r = row.iloc[0]
        price = _safe_float(r, "最新价")
        yesterday_close = _safe_float(r, "昨收")
        change = round(price - yesterday_close, 2) if yesterday_close else 0
        change_pct = round(change / yesterday_close * 100, 2) if yesterday_close else 0

        results.append(IndexData(
            code=code,
            name=name,
            price=round(price, 2),
            change=change,
            change_pct=change_pct,
            volume=_safe_float(r, "成交量"),
            amount=_safe_float(r, "成交额"),
            update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ))

    return results


def get_index_history(code: str, days: int = 30) -> list[dict]:
    """Daily OHLCV history for one index (via Sina daily API)."""
    symbol = HISTORY_SYMBOL_MAP.get(code)
    if not symbol:
        return []

    df = ak.stock_zh_index_daily(symbol=symbol)

    rows = []
    for _, r in df.tail(days).iterrows():
        close = _safe_float(r, "close")
        open_ = _safe_float(r, "open")
        rows.append({
            "date": str(r["date"]),
            "open": open_,
            "high": _safe_float(r, "high"),
            "low": _safe_float(r, "low"),
            "close": close,
            "volume": _safe_float(r, "volume"),
            "change_pct": round((close - open_) / open_ * 100, 2) if open_ else 0,
        })

    return rows


def get_all_index_history(days: int = 30) -> dict[str, list[dict]]:
    """History for all tracked indices."""
    return {code: get_index_history(code, days) for code in HISTORY_SYMBOL_MAP}


# ── Helpers ────────────────────────────────────────────────────────

def _safe_float(row, col: str, default: float = 0.0) -> float:
    try:
        v = row.get(col)
        if v is None or v == "":
            return default
        return float(v)
    except (ValueError, TypeError):
        return default
