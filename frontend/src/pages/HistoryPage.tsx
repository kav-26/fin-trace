import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { Clock } from "lucide-react"
import { api } from "@/lib/api"

interface HistoryItem {
  id: number
  question: string
  company: string
  confidence: number | null
  conclusion: string
  created_at: string
}

export default function HistoryPage() {
  const [items, setItems] = useState<HistoryItem[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  useEffect(() => {
    api
      .get<HistoryItem[]>("/history")
      .then((res) => setItems(res.data))
      .catch(() => setError("Could not load history. Is the API running?"))
  }, [])

  async function openInvestigation(id: number) {
    const res = await api.get(`/history/${id}`)
    sessionStorage.setItem("fin-trace-last-result", JSON.stringify(res.data))
    navigate("/report")
  }

  if (error) return <div className="p-8 text-sm text-red-400">{error}</div>
  if (!items) return <div className="p-8 text-sm text-slate-500">Loading…</div>

  return (
    <div className="max-w-3xl mx-auto px-8 py-12">
      <div className="text-xs font-mono tracking-widest text-amber-400 mb-2">
        HISTORY
      </div>
      <h1 className="text-2xl font-serif font-semibold text-slate-100 mb-1">
        Past Investigations
      </h1>
      <p className="text-sm text-slate-500 mb-10">
        {items.length} investigation{items.length !== 1 ? "s" : ""} on record.
      </p>

      {items.length === 0 ? (
        <p className="text-sm text-slate-500">
          No investigations yet — run one from the Investigate page.
        </p>
      ) : (
        <div className="space-y-3">
          {items.map((item) => (
            <button
              key={item.id}
              onClick={() => openInvestigation(item.id)}
              className="w-full text-left border border-slate-800 bg-slate-900 rounded-lg p-5 hover:border-slate-600 transition-colors"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-mono text-slate-500">
                  {item.company}
                </span>
                <span className="flex items-center gap-1 text-xs text-slate-600">
                  <Clock size={11} />
                  {new Date(item.created_at).toLocaleString()}
                </span>
              </div>
              <div className="font-medium text-slate-100 mb-1.5">
                {item.question}
              </div>
              <div className="text-sm text-slate-400 line-clamp-2">
                {item.conclusion}
              </div>
              {item.confidence !== null && (
                <div className="text-xs font-mono text-amber-400 mt-2">
                  {item.confidence}% confidence
                </div>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}