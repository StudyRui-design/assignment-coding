import type { IndexData } from "@/types/market"

function fmtPrice(n: number): string {
  return n.toLocaleString("zh-CN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}

function fmtPct(n: number): string {
  const sign = n >= 0 ? "+" : ""
  return `${sign}${n.toFixed(2)}%`
}

function fmtVolume(n: number | null): string {
  if (n == null) return "—"
  if (n >= 1e8) return `${(n / 1e8).toFixed(2)}亿`
  if (n >= 1e4) return `${(n / 1e4).toFixed(0)}万`
  return n.toLocaleString()
}

interface Props {
  indices: IndexData[]
}

export function IndexCards({ indices }: Props) {
  if (!indices.length) {
    return (
      <div className="grid grid-cols-5 gap-3">
        {Array.from({ length: 5 }).map((_, i) => (
          <div
            key={i}
            className="glass rounded-xl h-24 animate-pulse"
            style={{
              background:
                "linear-gradient(90deg, rgba(255,255,255,0.02) 25%, rgba(255,255,255,0.05) 50%, rgba(255,255,255,0.02) 75%)",
              backgroundSize: "200% 100%",
              animation: "shimmer 1.5s infinite",
            }}
          />
        ))}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-5 gap-3">
      {indices.map((idx, i) => {
        const isUp = idx.change_pct >= 0
        const accentColor = isUp ? "var(--up)" : "var(--down)"

        return (
          <div
            key={idx.code}
            className="glass rounded-xl px-4 py-3.5 transition-colors duration-300 hover:bg-white/[0.06]"
            style={{ "--stagger": i } as React.CSSProperties}
          >
            {/* Label */}
            <p className="text-xs text-[#8B90B5] tracking-wide truncate">
              {idx.name}
            </p>

            {/* Price — the hero number */}
            <p
              className="mt-1.5 text-[1.65rem] font-mono font-bold tabular-nums leading-tight tracking-tight"
              style={{ color: accentColor }}
            >
              {fmtPrice(idx.price)}
            </p>

            {/* Change + Volume row */}
            <div className="flex items-baseline justify-between mt-1 gap-2">
              <span
                className="text-sm font-mono font-semibold tabular-nums"
                style={{ color: accentColor }}
              >
                {fmtPct(idx.change_pct)}
              </span>
              <span className="text-[10px] text-[#5B6090] tabular-nums truncate">
                量 {fmtVolume(idx.volume)}
              </span>
            </div>
          </div>
        )
      })}
    </div>
  )
}
