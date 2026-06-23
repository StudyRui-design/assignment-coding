"""
Fetcher: industry sector rankings.

Uses AKShare's TongHuaShun (THS / 同花顺) API which hits 10jqka.com,
NOT eastmoney.com — so it bypasses the TLS-fingerprint block that
affects this machine.

Data: stock_board_industry_summary_ths
Columns: 序号, 板块, 涨跌幅, 总成交量, 总成交额, 领涨股, 领涨股-最新价, ...
"""

import akshare as ak

from fetcher import SectorData


def get_sectors(top_n: int = 20) -> list[SectorData]:
    """
    Top-N + bottom-N industry sectors ranked by % change today.
    Source: TongHuaShun via 10jqka.com.
    """
    df = ak.stock_board_industry_summary_ths()

    # Column 板块 = sector name, 涨跌幅 = change %
    # Sort by 涨跌幅 descending
    df_sorted = df.sort_values("涨跌幅", ascending=False)

    results: list[SectorData] = []
    rank = 0
    for _, r in df_sorted.iterrows():
        rank += 1
        results.append(SectorData(
            name=str(r["板块"]),
            code=str(r.get("序号", "")),
            change_pct=round(float(r["涨跌幅"]), 2),
            rank=rank,
        ))
        if len(results) >= top_n * 2:
            break

    top = results[:top_n]
    bottom = results[-top_n:] if len(results) >= top_n else []
    bottom.reverse()
    return top + bottom
