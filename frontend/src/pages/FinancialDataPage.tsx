import { useEffect, useState } from "react"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts"
import { getFinancialData, type FinancialAnalysis } from "@/lib/api"

export default function FinancialDataPage() {
  const [data, setData] = useState<FinancialAnalysis | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getFinancialData()
      .then(setData)
      .catch(() => setError("Could not load financial data. Is the API running?"))
  }, [])

  if (error) {
    return <div className="p-8 text-sm text-red-400">{error}</div>
  }

  if (!data) {
    return <div className="p-8 text-sm text-slate-500">Loading…</div>
  }

  const revenueBySegment = data.yoy_table
    .filter((r) => r.metric === "revenue" && r.segment !== "Total")
    .map((r) => ({
      segment: r.segment,
      FY2022: r.fy2022,
      FY2023: r.fy2023,
    }))

  const totalMetrics = data.yoy_table.filter((r) => r.segment === "Total")

  return (
    <div className="max-w-4xl mx-auto px-8 py-12">
      <div className="text-xs font-mono tracking-widest text-amber-400 mb-2">
        FINANCIAL DATA
      </div>
      <h1 className="text-2xl font-serif font-semibold text-slate-100 mb-1">
        Verified Metrics
      </h1>
      <p className="text-sm text-slate-500 mb-10">
        Computed via Pandas from structured filing data — not LLM-estimated.
      </p>

      {/* Margins */}
      <section className="mb-12">
        <div className="text-xs font-mono text-slate-500 mb-4">MARGINS</div>
        <div className="grid grid-cols-2 gap-4">
          {Object.entries(data.margins).map(([key, value]) => (
            <div
              key={key}
              className="border border-slate-800 rounded-lg p-4 bg-slate-900"
            >
              <div className="text-xs text-slate-500 mb-1 capitalize">
                {key.replace(/_/g, " ")}
              </div>
              <div className="font-mono text-2xl text-amber-400 font-semibold">
                {value}%
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Revenue by segment chart */}
      {revenueBySegment.length > 0 && (
        <section className="mb-12">
          <div className="text-xs font-mono text-slate-500 mb-4">
            REVENUE BY SEGMENT ($M)
          </div>
          <div className="border border-slate-800 rounded-lg bg-slate-900 p-4" style={{ height: 320 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={revenueBySegment}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="segment" tick={{ fill: "#94a3b8", fontSize: 11 }} />
                <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} />
                <Tooltip
                  contentStyle={{
                    background: "#0f172a",
                    border: "1px solid #334155",
                    borderRadius: 8,
                    fontSize: 12,
                  }}
                />
                <Bar dataKey="FY2022" fill="#475569" radius={[4, 4, 0, 0]} />
                <Bar dataKey="FY2023" fill="#C9A24B" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>
      )}

      {/* Full table */}
      <section>
        <div className="text-xs font-mono text-slate-500 mb-4">ALL METRICS</div>
        <div className="border border-slate-800 rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-900 text-slate-400 text-xs">
                <th className="text-left px-4 py-2.5 font-medium">Metric</th>
                <th className="text-left px-4 py-2.5 font-medium">Segment</th>
                <th className="text-right px-4 py-2.5 font-medium">FY2022</th>
                <th className="text-right px-4 py-2.5 font-medium">FY2023</th>
                <th className="text-right px-4 py-2.5 font-medium">Δ %</th>
              </tr>
            </thead>
            <tbody>
              {data.yoy_table.map((row, i) => (
                <tr key={i} className="border-t border-slate-800">
                  <td className="px-4 py-2.5 text-slate-300 capitalize">
                    {row.metric.replace(/_/g, " ")}
                  </td>
                  <td className="px-4 py-2.5 text-slate-500">{row.segment}</td>
                  <td className="px-4 py-2.5 text-right font-mono text-slate-400">
                    {row.fy2022.toLocaleString()}
                  </td>
                  <td className="px-4 py-2.5 text-right font-mono text-slate-400">
                    {row.fy2023.toLocaleString()}
                  </td>
                  <td
                    className={`px-4 py-2.5 text-right font-mono ${
                      row.yoy_pct_change >= 0 ? "text-emerald-400" : "text-red-400"
                    }`}
                  >
                    {row.yoy_pct_change >= 0 ? "+" : ""}
                    {row.yoy_pct_change}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}