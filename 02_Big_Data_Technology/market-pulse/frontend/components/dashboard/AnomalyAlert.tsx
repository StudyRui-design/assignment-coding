import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { AnomalyEvent } from "@/types/market"

const LEVEL_META: Record<
  string,
  { label: string; ring: string; bg: string; text: string; dot: string }
> = {
  alert: {
    label: "预警",
    ring: "ring-[#FF3B5C]/30",
    bg: "bg-[#FF3B5C]/10",
    text: "text-[#FF3B5C]",
    dot: "bg-[#FF3B5C]",
  },
  warning: {
    label: "注意",
    ring: "ring-[#F5A623]/30",
    bg: "bg-[#F5A623]/10",
    text: "text-[#F5A623]",
    dot: "bg-[#F5A623]",
  },
  info: {
    label: "提示",
    ring: "ring-[#5B8DEF]/30",
    bg: "bg-[#5B8DEF]/10",
    text: "text-[#5B8DEF]",
    dot: "bg-[#5B8DEF]",
  },
}

interface Props {
  anomalies: AnomalyEvent[]
}

export function AnomalyAlert({ anomalies }: Props) {
  if (!anomalies.length) {
    return (
      <Card className="glass border-0">
        <CardHeader className="pb-1">
          <CardTitle className="text-sm font-semibold tracking-wide text-white">
            异动提醒
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-4 text-center">
            <div className="w-8 h-8 rounded-full bg-emerald-400/10 flex items-center justify-center mb-2">
              <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400" />
            </div>
            <p className="text-xs text-[#8B90B5]">市场平稳</p>
            <p className="text-[10px] text-[#5B6090] mt-0.5">
              暂无异常波动
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  const alertCount = anomalies.filter((a) => a.level === "alert").length
  const warningCount = anomalies.filter((a) => a.level === "warning").length

  return (
    <Card
      className={`glass border-0 ${alertCount > 0 ? "ring-1 ring-[#FF3B5C]/20" : ""}`}
    >
      <CardHeader className="pb-1">
        <CardTitle className="text-sm font-semibold tracking-wide text-white flex items-center gap-2">
          异动提醒
          {alertCount > 0 && (
            <span className="inline-flex items-center gap-1 text-[10px] font-bold text-[#FF3B5C]">
              <span className="relative flex h-1.5 w-1.5">
                <span className="animate-pulse-dot absolute inset-0 rounded-full bg-[#FF3B5C]" />
                <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-[#FF3B5C]" />
              </span>
              {alertCount + warningCount}
            </span>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-1.5">
          {anomalies.map((a, i) => {
            const meta = LEVEL_META[a.level] ?? LEVEL_META.info
            return (
              <div
                key={i}
                className="flex items-start gap-2 text-xs group/item hover:bg-white/[0.03] rounded-md px-2 py-1.5 -mx-2 transition-colors"
              >
                {/* Level dot */}
                <span
                  className={`inline-block w-1.5 h-1.5 rounded-full ${meta.dot} mt-1.5 shrink-0`}
                />
                {/* Badge */}
                <span
                  className={`inline-flex items-center rounded px-1.5 py-0.5 text-[10px] font-medium ${meta.bg} ${meta.text} shrink-0`}
                >
                  {meta.label}
                </span>
                {/* Message */}
                <span className="text-[#EDEFF5] leading-relaxed">
                  {a.message}
                </span>
              </div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}
