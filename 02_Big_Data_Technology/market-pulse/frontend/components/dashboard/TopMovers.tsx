import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { SectorData } from "@/types/market"

interface Props {
  sectors: SectorData[]
}

export function TopMovers({ sectors }: Props) {
  if (!sectors.length) {
    return (
      <Card className="glass border-0">
        <CardHeader className="pb-1">
          <CardTitle className="text-sm font-semibold tracking-wide text-white">
            涨跌榜
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            {Array.from({ length: 2 }).map((_, col) => (
              <div key={col} className="space-y-2">
                {Array.from({ length: 5 }).map((_, i) => (
                  <div
                    key={i}
                    className="flex items-center gap-2 animate-pulse"
                  >
                    <div className="w-4 h-4 rounded bg-white/[0.03]" />
                    <div className="flex-1 h-4 rounded bg-white/[0.03]" />
                    <div className="w-14 h-4 rounded bg-white/[0.03]" />
                  </div>
                ))}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  const mid = Math.floor(sectors.length / 2)
  const gainers = sectors.slice(0, mid).slice(0, 5)
  const losers = [...sectors.slice(mid)].reverse().slice(0, 5)

  return (
    <div className="grid grid-cols-2 gap-4">
      {/* Gainers */}
      <Card className="glass border-0">
        <CardHeader className="pb-1">
          <CardTitle className="text-xs font-semibold uppercase tracking-wider text-[#FF3B5C]">
            涨幅 TOP 5
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-0.5">
            {gainers.map((s, i) => (
              <div
                key={s.code}
                className="flex items-center gap-2.5 text-sm group/item hover:bg-white/[0.04] rounded-md px-2 py-1.5 -mx-2 transition-colors"
              >
                <span className="w-4 text-[10px] text-[#5B6090] tabular-nums text-right font-mono shrink-0">
                  {i + 1}
                </span>
                <span className="flex-1 truncate text-[#EDEFF5] text-xs leading-tight">
                  {s.name}
                </span>
                <span className="text-xs font-mono font-semibold tabular-nums text-[#FF3B5C] shrink-0">
                  +{s.change_pct.toFixed(2)}%
                </span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Losers */}
      <Card className="glass border-0">
        <CardHeader className="pb-1">
          <CardTitle className="text-xs font-semibold uppercase tracking-wider text-[#00C853]">
            跌幅 TOP 5
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-0.5">
            {losers.map((s, i) => (
              <div
                key={s.code}
                className="flex items-center gap-2.5 text-sm group/item hover:bg-white/[0.04] rounded-md px-2 py-1.5 -mx-2 transition-colors"
              >
                <span className="w-4 text-[10px] text-[#5B6090] tabular-nums text-right font-mono shrink-0">
                  {i + 1}
                </span>
                <span className="flex-1 truncate text-[#EDEFF5] text-xs leading-tight">
                  {s.name}
                </span>
                <span
                  className={`text-xs font-mono font-semibold tabular-nums shrink-0 ${
                    s.change_pct >= 0 ? "text-[#FF3B5C]" : "text-[#00C853]"
                  }`}
                >
                  {s.change_pct >= 0 ? "+" : ""}
                  {s.change_pct.toFixed(2)}%
                </span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
