"use client"

import { useEffect, useState, useCallback } from "react"
import { fetchOverview } from "@/lib/api"
import type { MarketOverview } from "@/types/market"
import { IndexCards } from "@/components/dashboard/IndexCards"
import { IndexChart } from "@/components/dashboard/IndexChart"
import { MarketBreadth } from "@/components/dashboard/MarketBreadth"
import { SectorHeatmap } from "@/components/dashboard/SectorHeatmap"
import { TopMovers } from "@/components/dashboard/TopMovers"
import { AnomalyAlert } from "@/components/dashboard/AnomalyAlert"

const REFRESH_MS = 30_000

/* ── Miniature EKG-style pulse bars ── */
function PulseBars() {
  return (
    <span className="pulse-track ml-2" aria-hidden="true">
      <span className="bar" />
      <span className="bar" />
      <span className="bar" />
      <span className="bar" />
      <span className="bar" />
      <span className="bar" />
      <span className="bar" />
      <span className="bar" />
    </span>
  )
}

export default function HomePage() {
  const [data, setData] = useState<MarketOverview | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [refreshing, setRefreshing] = useState(false)

  const load = useCallback(async () => {
    try {
      const overview = await fetchOverview()
      setData(overview)
      setError(null)
      setRefreshing(true)
      setTimeout(() => setRefreshing(false), 600)
    } catch (err) {
      setError(err instanceof Error ? err.message : "数据获取失败")
    }
  }, [])

  useEffect(() => {
    load()
    const timer = setInterval(load, REFRESH_MS)
    return () => clearInterval(timer)
  }, [load])

  const lastUpdate = data?.update_time
    ? new Date(data.update_time).toLocaleTimeString("zh-CN", { hour12: false })
    : "—"

  return (
    <div className="mx-auto max-w-7xl px-5 py-6 space-y-5 min-h-screen">
      {/* ═══════ Header ═══════ */}
      <header className="flex items-end justify-between pb-4 border-b border-white/5">
        <div className="flex items-end gap-4">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold tracking-tight text-white">
                市场脉搏
              </h1>
              <PulseBars />
            </div>
            <p className="text-sm text-[#8B90B5] mt-0.5">
              A股市场实时监测仪表盘
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 text-right">
          {/* Live indicator */}
          <div className="flex items-center gap-2">
            <span
              className={`relative flex h-2 w-2 ${refreshing ? "" : ""}`}
              aria-label="在线"
            >
              <span
                className={`animate-pulse-dot absolute inset-0 rounded-full ${error ? "bg-amber-400" : "bg-emerald-400"}`}
              />
              <span
                className={`relative inline-flex rounded-full h-2 w-2 ${error ? "bg-amber-400" : "bg-emerald-400"}`}
              />
            </span>
            <span className="text-xs text-[#8B90B5]">实时</span>
          </div>

          <div className="w-px h-4 bg-white/10" />

          <div>
            <span className="text-[10px] uppercase tracking-widest text-[#5B6090]">
              最后更新
            </span>
            <p className="text-sm font-mono font-medium tabular-nums text-white">
              {lastUpdate}
            </p>
          </div>

          {error && (
            <p className="text-xs text-amber-400 max-w-48 truncate" title={error}>
              {error}
            </p>
          )}
        </div>
      </header>

      {/* ═══════ Row 1: Index Cards ═══════ */}
      <section className="animate-fade-in">
        <IndexCards indices={data?.indices ?? []} />
      </section>

      {/* ═══════ Row 2: Chart (full width) ═══════ */}
      <section className="animate-fade-in" style={{ "--stagger": "1" } as React.CSSProperties}>
        <IndexChart />
      </section>

      {/* ═══════ Row 3: Breadth + Sectors ═══════ */}
      <section
        className="grid grid-cols-1 lg:grid-cols-5 gap-4 animate-fade-in"
        style={{ "--stagger": "2" } as React.CSSProperties}
      >
        <div className="lg:col-span-2">
          <MarketBreadth breadth={data?.breadth ?? null} />
        </div>
        <div className="lg:col-span-3">
          <SectorHeatmap sectors={data?.sectors ?? []} />
        </div>
      </section>

      {/* ═══════ Row 4: Top Movers + Anomalies ═══════ */}
      <section
        className="grid grid-cols-1 lg:grid-cols-4 gap-4 animate-fade-in"
        style={{ "--stagger": "3" } as React.CSSProperties}
      >
        <div className="lg:col-span-3">
          <TopMovers sectors={data?.sectors ?? []} />
        </div>
        <AnomalyAlert anomalies={data?.anomalies ?? []} />
      </section>

      {/* ═══════ Footer ═══════ */}
      <footer className="pt-4 pb-2 text-center text-[10px] text-[#5B6090] tracking-wider uppercase">
        数据来源不可作为投资依据 · 仅供参考
      </footer>
    </div>
  )
}
