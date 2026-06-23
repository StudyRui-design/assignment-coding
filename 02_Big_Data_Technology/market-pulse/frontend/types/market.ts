// Market data types shared across all dashboard components

export interface IndexData {
  code: string
  name: string
  price: number
  change: number
  change_pct: number
  volume: number | null
  amount: number | null
  update_time: string
}

export interface SectorData {
  name: string
  code: string
  change_pct: number
  rank: number
}

export interface MarketBreadthData {
  advancing: number
  declining: number
  unchanged: number
  total: number
  adv_decl_ratio: number
  update_time: string | null
}

export interface AnomalyEvent {
  type: "index_move" | "volume_spike" | "breadth_extreme"
  level: "info" | "warning" | "alert"
  message: string
  value: number
  threshold: number
  timestamp: string
}

export interface MarketOverview {
  indices: IndexData[]
  sectors: SectorData[]
  breadth: MarketBreadthData | null
  anomalies: AnomalyEvent[]
  update_time: string
}
