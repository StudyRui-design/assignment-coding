"""
Fetcher: market breadth (advancing vs declining stock counts).

AKShare's `stock_zh_a_spot_em` uses East Money → blocked here.
We use Sina's real-time quote API directly to count up/down/flat stocks
across a representative sample of A-shares.
"""

import logging
from datetime import datetime

import requests
from fetcher import MarketBreadthData

logger = logging.getLogger(__name__)

# Module-level session: reuse TCP connection across batch fetches.
_session = requests.Session()
_session.trust_env = False


def get_market_breadth() -> MarketBreadthData:
    """
    Count advancing / declining / unchanged stocks.

    Approach: call the Sina real-time batch-quote API for a large set
    of representative A-share symbols, then count the change signs.
    """
    # Build a list of representative symbols across Shanghai + Shenzhen
    symbols = _build_symbol_list()

    # Fetch in batches of ~200 (Sina's batch limit is generous)
    advancing = 0
    declining = 0
    unchanged = 0

    batch_size = 200
    for i in range(0, len(symbols), batch_size):
        batch = symbols[i:i + batch_size]
        adv, decl, unch = _count_batch(batch)
        advancing += adv
        declining += decl
        unchanged += unch

    total = advancing + declining + unchanged
    ratio = round(advancing / declining, 2) if declining > 0 else 0.0

    return MarketBreadthData(
        advancing=advancing,
        declining=declining,
        unchanged=unchanged,
        total=total,
        adv_decl_ratio=ratio,
        update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )


# ── Internals ──────────────────────────────────────────────────────

def _build_symbol_list() -> list[str]:
    """Return a representative sample of ~3700 A-share Sina symbols.

    Covers Shanghai main board (600xxx–605xxx), STAR market (688xxx),
    Shenzhen main board (000xxx–003xxx), and ChiNext (300xxx).
    """
    symbols: list[str] = []

    # Shanghai main board
    symbols.extend(f"sh{code}" for code in range(600000, 600801))  # 801 stocks
    symbols.extend(f"sh{code}" for code in range(601000, 601801))  # 801 stocks
    symbols.extend(f"sh{code}" for code in range(603000, 603501))  # 501 stocks

    # STAR market (科创): 688000-688500
    symbols.extend(f"sh{code}" for code in range(688000, 688501))  # 501 stocks

    # Shenzhen main board (修复: 原 range(2000,2501) 产出 sz002000–sz002500,
    # 注释却写 "000001 → …" — 意图与实现不一致)
    symbols.extend(f"sz{code:06d}" for code in range(1, 501))      # 500 stocks

    # SME board
    symbols.extend(f"sz{code:06d}" for code in range(2000, 2501))  # 501 stocks

    # ChiNext (创业板): 300000-300800
    symbols.extend(f"sz{code}" for code in range(300000, 300501))  # 501 stocks

    logger.info("Built symbol list: %d candidate symbols", len(symbols))
    return symbols


def _count_batch(symbols: list[str]) -> tuple[int, int, int]:
    """Query one Sina batch and return (advancing, declining, unchanged)."""
    # Sina batch URL: comma-separated symbols
    sym_str = ",".join(symbols)
    url = f"http://hq.sinajs.cn/list={sym_str}"

    try:
        resp = _session.get(
            url,
            headers={"Referer": "https://finance.sina.com.cn"},
            timeout=10,
        )
        resp.encoding = "gbk"
        text = resp.text
    except Exception as exc:
        logger.error("Sina batch query failed for %d symbols: %s", len(symbols), exc)
        return 0, 0, 0

    advancing = declining = unchanged = 0

    for line in text.strip().split("\n"):
        if "=" not in line:
            continue
        try:
            data = line.split('"')[1]
            if not data:
                continue
            fields = data.split(",")
            if len(fields) < 4:
                continue

            price = float(fields[3])  # current price
            yesterday_close = float(fields[2])  # previous close

            if price <= 0 or yesterday_close <= 0:
                unchanged += 1
            elif price > yesterday_close:
                advancing += 1
            elif price < yesterday_close:
                declining += 1
            else:
                unchanged += 1
        except (IndexError, ValueError):
            unchanged += 1

    return advancing, declining, unchanged
