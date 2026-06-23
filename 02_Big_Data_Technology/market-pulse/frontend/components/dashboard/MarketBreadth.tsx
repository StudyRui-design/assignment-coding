import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { MarketBreadthData } from "@/types/market"

interface Props {
  breadth: MarketBreadthData | null
}

export function MarketBreadth({ breadth }: Props) {
  if (!breadth) {
    return (
      <Card className="glass border-0 h-full">
        <CardHeader className="pb-1">
          <CardTitle className="text-sm font-semibold tracking-wide text-white">
            市场宽度
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div
              className="h-3 rounded-full animate-pulse"
              style={{
                background:
                  "linear-gradient(90deg, rgba(255,255,255,0.02) 25%, rgba(255,255,255,0.06) 50%, rgba(255,255,255,0.02) 75%)",
                backgroundSize: "200% 100%",
                animation: "shimmer 1.5s infinite",
              }}
            />
            <div className="flex gap-3">
              <div className="flex-1 h-12 rounded-lg bg-white/[0.02] animate-pulse" />
              <div className="flex-1 h-12 rounded-lg bg-white/[0.02] animate-pulse" />
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  const advancing = breadth.advancing ?? 0
  const declining = breadth.declining ?? 0
  const unchanged = breadth.unchanged ?? 0
  const total = breadth.total ?? 0
  const advDeclRatio = breadth.adv_decl_ratio ?? 0
  const upPct = total > 0 ? (advancing / total) * 100 : 0
  const downPct = total > 0 ? (declining / total) * 100 : 0
  const flatPct = total > 0 ? (unchanged / total) * 100 : 0

  return (
    <Card className="glass border-0 h-full">
      <CardHeader className="pb-1">
        <CardTitle className="text-sm font-semibold tracking-wide text-white">
          市场宽度
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* ── Ratio Hero ── */}
        <div className="flex items-baseline gap-3">
          <div>
            <span className="text-[1.65rem] font-mono font-bold tabular-nums text-[#FF3B5C]">
              {advancing.toLocaleString()}
            </span>
            <span className="text-xs text-[#8B90B5] ml-1.5">涨</span>
          </div>
          <span className="text-xl font-mono font-medium text-[#5B6090]">:</span>
          <div>
            <span className="text-[1.65rem] font-mono font-bold tabular-nums text-[#00C853]">
              {declining.toLocaleString()}
            </span>
            <span className="text-xs text-[#8B90B5] ml-1.5">跌</span>
          </div>
          <div className="ml-auto text-right">
            <p className="text-[10px] text-[#5B6090] uppercase tracking-wider">
              涨跌比
            </p>
            <p className="text-lg font-mono font-semibold tabular-nums text-white">
              {advDeclRatio === Infinity || advDeclRatio == null
                ? "∞"
                : advDeclRatio.toFixed(2)}
            </p>
          </div>
        </div>

        {/* ── Bar: single horizontal stacked bar ── */}
        <div className="space-y-1.5">
          <div className="flex h-2.5 rounded-full overflow-hidden bg-[#0F1535]">
            <div
              className="bg-[#FF3B5C] transition-all duration-500"
              style={{ width: `${Math.max(upPct, 1)}%` }}
            />
            <div
              className="bg-[#5B6090]/30 transition-all duration-500"
              style={{ width: `${Math.max(flatPct, 0)}%` }}
            />
            <div
              className="bg-[#00C853] transition-all duration-500"
              style={{ width: `${Math.max(downPct, 1)}%` }}
            />
          </div>

          <div className="flex justify-between text-[10px] text-[#5B6090]">
            <span>
              上涨 {upPct.toFixed(1)}%
            </span>
            <span>
              共 {total.toLocaleString()} 只
            </span>
            <span>
              下跌 {downPct.toFixed(1)}%
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
