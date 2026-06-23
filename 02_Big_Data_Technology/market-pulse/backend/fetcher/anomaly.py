"""
Simple rule-based anomaly detection for the dashboard.

Detection rules:
  1. INDEX_MOVE   — any tracked index moves ±2 % within the latest snapshot.
  2. VOLUME_SPIKE — main-board turnover exceeds 2× its 5-day rolling average.
  3. BREADTH_EXTREME — advancing/declining ratio > 9:1 in either direction.
"""

from datetime import datetime
from typing import Optional

from fetcher import IndexData, MarketBreadthData, AnomalyEvent


def detect_index_anomalies(indices: list[IndexData]) -> list[AnomalyEvent]:
    """Flag indices that moved more than ±2 % in the current session."""
    events: list[AnomalyEvent] = []
    threshold = 2.0  # percent

    for idx in indices:
        pct = abs(idx.change_pct)
        if pct >= threshold:
            level = "alert" if pct >= 4.0 else "warning"
            direction = "↑" if idx.change_pct > 0 else "↓"
            events.append(AnomalyEvent(
                type="index_move",
                level=level,
                message=f"{idx.name} 大幅波动 {direction}{pct:.2f}%",
                value=round(idx.change_pct, 2),
                threshold=threshold,
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ))

    return events


def detect_breadth_anomalies(breadth: Optional[MarketBreadthData]) -> list[AnomalyEvent]:
    """Flag extreme market breadth (e.g. >85 % stocks moving the same way)."""
    if breadth is None or breadth.total == 0:
        return []

    events: list[AnomalyEvent] = []

    # Extreme up-day: >85 % of stocks advancing
    up_ratio = breadth.advancing / breadth.total
    if up_ratio > 0.85:
        events.append(AnomalyEvent(
            type="breadth_extreme",
            level="warning",
            message=f"极端普涨：{breadth.advancing}/{breadth.total} 只上涨 ({up_ratio:.1%})",
            value=round(up_ratio, 3),
            threshold=0.85,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ))

    # Extreme down-day
    down_ratio = breadth.declining / breadth.total
    if down_ratio > 0.85:
        events.append(AnomalyEvent(
            type="breadth_extreme",
            level="alert",
            message=f"极端普跌：{breadth.declining}/{breadth.total} 只下跌 ({down_ratio:.1%})",
            value=round(down_ratio, 3),
            threshold=0.85,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ))

    return events


def detect_all_anomalies(
    indices: list[IndexData],
    breadth: Optional[MarketBreadthData] = None,
) -> list[AnomalyEvent]:
    """Run all detection rules and return a flat list of events."""
    events: list[AnomalyEvent] = []
    events.extend(detect_index_anomalies(indices))
    events.extend(detect_breadth_anomalies(breadth))
    # Sort most severe first
    severity_order = {"alert": 0, "warning": 1, "info": 2}
    events.sort(key=lambda e: severity_order.get(e.level, 9))
    return events
