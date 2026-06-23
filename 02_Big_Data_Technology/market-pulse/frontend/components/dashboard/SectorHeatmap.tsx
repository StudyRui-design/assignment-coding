import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { SectorData } from "@/types/market"

interface Props {
  sectors: SectorData[]
}

export function SectorHeatmap({ sectors }: Props) {
  if (!sectors.length) {
    return (
      <Card className="glass border-0 h-full">
        <CardHeader className="pb-1">
          <CardTitle className="text-sm font-semibold tracking-wide text-white">
            板块排行
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {Array.from({ length: 10 }).map((_, i) => (
              <div
                key={i}
                className="flex items-center gap-2 animate-pulse"
              >
                <div className="w-5 h-4 rounded bg-white/[0.03]" />
                <div className="flex-1 h-4 rounded bg-white/[0.03]" />
                <div className="w-16 h-4 rounded bg-white/[0.03]" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  const mid = Math.floor(sectors.length / 2)
  const gainers = sectors.slice(0, mid)
  const losers = [...sectors.slice(mid)].reverse()

  return (
    <Card className="glass border-0 h-full">
      <CardHeader className="pb-1">
        <CardTitle className="text-sm font-semibold tracking-wide text-white">
          板块涨跌排行
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-5">
          {/* Gainers */}
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-wider text-[#FF3B5C] mb-2">
              涨幅前列
            </p>
            <div className="space-y-1">
              {gainers.slice(0, 8).map((s, i) => (
                <div
                  key={s.code}
                  className="flex items-center gap-2 text-sm group/item hover:bg-white/[0.03] rounded px-1.5 py-0.5 -mx-1.5 transition-colors"
                >
                  <span className="w-5 text-[10px] text-[#5B6090] tabular-nums text-right shrink-0">
                    {i + 1}
                  </span>
                  <span className="flex-1 truncate text-[#EDEFF5] text-xs">
                    {s.name}
                  </span>
                  <span className="text-xs font-mono font-medium tabular-nums text-[#FF3B5C] shrink-0">
                    +{s.change_pct.toFixed(2)}%
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Losers */}
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-wider text-[#00C853] mb-2">
              跌幅前列
            </p>
            <div className="space-y-1">
              {losers.slice(0, 8).map((s, i) => (
                <div
                  key={s.code}
                  className="flex items-center gap-2 text-sm group/item hover:bg-white/[0.03] rounded px-1.5 py-0.5 -mx-1.5 transition-colors"
                >
                  <span className="w-5 text-[10px] text-[#5B6090] tabular-nums text-right shrink-0">
                    {i + 1}
                  </span>
                  <span className="flex-1 truncate text-[#EDEFF5] text-xs">
                    {s.name}
                  </span>
                  <span
                    className={`text-xs font-mono font-medium tabular-nums shrink-0 ${
                      s.change_pct >= 0 ? "text-[#FF3B5C]" : "text-[#00C853]"
                    }`}
                  >
                    {s.change_pct >= 0 ? "+" : ""}
                    {s.change_pct.toFixed(2)}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
