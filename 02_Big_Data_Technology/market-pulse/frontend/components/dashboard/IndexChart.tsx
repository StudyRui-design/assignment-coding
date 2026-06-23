"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useEffect, useState } from "react"
import { fetchIndexHistory } from "@/lib/api"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts"

const INDEX_META: Record<string, { name: string; color: string }> = {
  "000001": { name: "上证指数", color: "#FF3B5C" },
  "399001": { name: "深证成指", color: "#5B8DEF" },
  "000300": { name: "沪深300", color: "#A78BFA" },
  "399006": { name: "创业板指", color: "#F5A623" },
  "000688": { name: "科创50", color: "#00C853" },
}

type ChartDataPoint = Record<string, number | string> & { date: string }

export function IndexChart() {
  const [days, setDays] = useState("5")
  const [data, setData] = useState<ChartDataPoint[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    setLoading(true)

    async function load() {
      const allCodes = Object.keys(INDEX_META)
      const results = await Promise.allSettled(
        allCodes.map((code) => fetchIndexHistory(code, Number(days)))
      )

      const dateMap = new Map<string, Record<string, number>>()

      results.forEach((result, i) => {
        if (result.status !== "fulfilled") return
        const code = allCodes[i]
        for (const row of result.value.data) {
          const date = String(row.date)
          if (!dateMap.has(date)) dateMap.set(date, {})
          const entry = dateMap.get(date)!
          entry[`close_${code}`] = Number(row.close)
        }
      })

      const chartData: ChartDataPoint[] = []
      for (const [date, values] of dateMap) {
        chartData.push({ date, ...values })
      }
      chartData.sort((a, b) => a.date.localeCompare(b.date))

      if (chartData.length > 0) {
        const normalized: ChartDataPoint[] = []
        for (const point of chartData) {
          const norm: ChartDataPoint = { date: point.date }
          for (const code of allCodes) {
            const key = `close_${code}`
            const firstClose = chartData[0][key]
            const curClose = point[key]
            if (
              typeof firstClose === "number" &&
              typeof curClose === "number" &&
              firstClose > 0
            ) {
              norm[key] = ((curClose - firstClose) / firstClose) * 100
            }
          }
          normalized.push(norm)
        }
        if (!cancelled) setData(normalized)
      }

      if (!cancelled) setLoading(false)
    }

    load()
    return () => {
      cancelled = true
    }
  }, [days])

  return (
    <Card className="glass border-0">
      <CardHeader className="flex flex-row items-center justify-between pb-1">
        <CardTitle className="text-sm font-semibold tracking-wide text-white">
          指数走势对比
          <span className="text-xs font-normal text-[#8B90B5] ml-2">归一化 %</span>
        </CardTitle>
        <Tabs value={days} onValueChange={setDays}>
          <TabsList className="h-7 bg-[#0F1535]">
            <TabsTrigger
              value="5"
              className="text-[10px] px-2.5 data-active:bg-[#161E48] data-active:text-white"
            >
              5日
            </TabsTrigger>
            <TabsTrigger
              value="10"
              className="text-[10px] px-2.5 data-active:bg-[#161E48] data-active:text-white"
            >
              10日
            </TabsTrigger>
            <TabsTrigger
              value="30"
              className="text-[10px] px-2.5 data-active:bg-[#161E48] data-active:text-white"
            >
              30日
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="h-[300px] flex items-center justify-center">
            <div className="flex items-center gap-2 text-[#8B90B5] text-sm">
              <span className="inline-block w-2 h-2 rounded-full bg-[#5B8DEF] animate-pulse-dot" />
              加载走势数据…
            </div>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data}>
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="#1E2760"
                strokeOpacity={0.6}
                vertical={false}
              />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 10, fill: "#5B6090" }}
                tickFormatter={(d: string) => d.slice(5)}
                axisLine={{ stroke: "#1E2760" }}
                tickLine={false}
              />
              <YAxis
                tick={{ fontSize: 10, fill: "#5B6090" }}
                tickFormatter={(v: number) => `${v.toFixed(0)}%`}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip
                contentStyle={{
                  background: "#0F1535",
                  border: "1px solid #1E2760",
                  borderRadius: 8,
                  fontSize: 12,
                  color: "#EDEFF5",
                }}
                formatter={(value, name) => {
                  const v = Number(value)
                  const code = String(name).replace("close_", "")
                  return [
                    `${v >= 0 ? "+" : ""}${v.toFixed(2)}%`,
                    INDEX_META[code]?.name ?? code,
                  ]
                }}
                labelFormatter={(label) => `日期: ${label}`}
              />
              <Legend
                formatter={(value: string) => {
                  const code = String(value).replace("close_", "")
                  return INDEX_META[code]?.name || code
                }}
                wrapperStyle={{ fontSize: 11, color: "#8B90B5" }}
              />
              {Object.entries(INDEX_META).map(([code, meta]) => (
                <Line
                  key={code}
                  type="monotone"
                  dataKey={`close_${code}`}
                  stroke={meta.color}
                  strokeWidth={2}
                  dot={false}
                  activeDot={{
                    r: 4,
                    stroke: meta.color,
                    strokeWidth: 2,
                    fill: "#0F1535",
                  }}
                  name={`close_${code}`}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  )
}
