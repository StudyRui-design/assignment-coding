from pydantic import BaseModel
from typing import Optional


class IndexData(BaseModel):
    """实时指数行情"""
    code: str          # 指数代码，如 "000001" (上证)
    name: str          # 指数名称，如 "上证指数"
    price: float       # 最新价
    change: float      # 涨跌额
    change_pct: float  # 涨跌幅 (%)
    volume: Optional[float] = None   # 成交量
    amount: Optional[float] = None   # 成交额
    update_time: Optional[str] = None


class SectorData(BaseModel):
    """行业板块数据"""
    name: str          # 板块名称
    code: str          # 板块代码
    change_pct: float  # 涨跌幅 (%)
    rank: int          # 排名


class MarketBreadthData(BaseModel):
    """市场宽度数据"""
    advancing: int     # 上涨家数
    declining: int     # 下跌家数
    unchanged: int     # 平盘家数
    total: int         # 总家数
    adv_decl_ratio: float = 0.0  # 涨跌比
    update_time: Optional[str] = None


class AnomalyEvent(BaseModel):
    """异动事件"""
    type: str          # 事件类型: "volume_spike" / "index_move" / "breadth_extreme"
    level: str         # 严重程度: "info" / "warning" / "alert"
    message: str       # 事件描述
    value: float       # 当前值
    threshold: float   # 阈值
    timestamp: str


class MarketOverview(BaseModel):
    """市场总览 - 聚合所有维度的数据"""
    indices: list[IndexData]
    sectors: list[SectorData]
    breadth: Optional[MarketBreadthData] = None
    anomalies: list[AnomalyEvent]
    update_time: str
