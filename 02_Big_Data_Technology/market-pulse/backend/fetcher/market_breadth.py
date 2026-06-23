"""
Fetcher: market breadth (advancing vs declining stock counts).

AKShare's `stock_zh_a_spot_em` uses East Money → blocked here.
We use Sina's real-time quote API directly to count up/down/flat stocks
across a representative sample of A-shares.
"""

from datetime import datetime

import requests
from fetcher import MarketBreadthData


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
    """Return a representative list of ~800 A-share Sina symbols."""
    # Shanghai 600xxx-605xxx + 688xxx (科创), Shenzhen 000xxx-003xxx + 300xxx (创业)
    symbols = []

    # Shanghai main board: 600000-605999 (most active range)
    for code in range(600000, 600501):  # 500 stocks
        symbols.append(f"sh{code}")
    for code in range(601000, 601501):
        symbols.append(f"sh{code}")

    # STAR market (科创): 688000-688500
    for code in range(688000, 688201):
        symbols.append(f"sh{code}")

    # Shenzhen main board
    for code in range(2000, 2501):  # 000001 → sz002000-sz002500
        symbols.append(f"sz{code:06d}")

    # ChiNext (创业板): 300000-300500
    for code in range(300000, 300201):
        symbols.append(f"sz{code}")

    return symbols


def _count_batch(symbols: list[str]) -> tuple[int, int, int]:
    """Query one Sina batch and return (advancing, declining, unchanged)."""
    # Sina batch URL: comma-separated symbols
    sym_str = ",".join(symbols)
    url = f"http://hq.sinajs.cn/list={sym_str}"

    try:
        s = requests.Session()
        s.trust_env = False
        resp = s.get(url, headers={"Referer": "https://finance.sina.com.cn"}, timeout=10)
        resp.encoding = "gbk"
        text = resp.text
    except Exception:
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
