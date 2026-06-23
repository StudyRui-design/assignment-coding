import type { MarketOverview } from "@/types/market"

const BACKEND_BASE = "http://localhost:8000/api/v1"

async function fetchJSON<T>(url: string): Promise<T> {
  const res = await fetch(url, { cache: "no-store" })
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`)
  }
  return res.json()
}

export async function fetchOverview(): Promise<MarketOverview> {
  return fetchJSON<MarketOverview>(`${BACKEND_BASE}/market/overview`)
}

export async function fetchIndexHistory(code: string, days = 30) {
  return fetchJSON<{ code: string; data: Array<Record<string, unknown>> }>(
    `${BACKEND_BASE}/market/indices/history?code=${code}&days=${days}`
  )
}
