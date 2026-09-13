import { useEffect, useState } from "react"
import { CheckCircle2, FileText } from "lucide-react"
import { getCompanies, switchCompany, type CompanyRegistry } from "@/lib/api"

export default function DataSourcesPage() {
  const [registry, setRegistry] = useState<CompanyRegistry | null>(null)
  const [switching, setSwitching] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function loadCompanies() {
    try {
      const data = await getCompanies()
      setRegistry(data)
    } catch {
      setError("Could not load company registry. Is the API running?")
    }
  }

  useEffect(() => {
    loadCompanies()
  }, [])

  async function handleSwitch(companyId: string) {
    if (!registry || companyId === registry.current) return
    setSwitching(companyId)
    try {
      await switchCompany(companyId)
      await loadCompanies()
    } catch {
      setError("Failed to switch company.")
    } finally {
      setSwitching(null)
    }
  }

  if (error) return <div className="p-8 text-sm text-red-400">{error}</div>
  if (!registry) return <div className="p-8 text-sm text-slate-500">Loading…</div>

  return (
    <div className="max-w-2xl mx-auto px-8 py-12">
      <div className="text-xs font-mono tracking-widest text-amber-400 mb-2">
        DATA &amp; SOURCES
      </div>
      <h1 className="text-2xl font-serif font-semibold text-slate-100 mb-1">
        Companies
      </h1>
      <p className="text-sm text-slate-500 mb-10">
        Select which company's filings and financial data are active for
        investigations. Both the retrieval index and verified metrics switch
        together.
      </p>

      <div className="space-y-3">
        {Object.entries(registry.companies).map(([id, info]) => {
          const isActive = id === registry.current
          return (
            <div
              key={id}
              className={`border rounded-lg p-5 flex items-center justify-between transition-colors ${
                isActive
                  ? "border-amber-400/40 bg-amber-400/5"
                  : "border-slate-800 bg-slate-900"
              }`}
            >
              <div>
                <div className="flex items-center gap-2">
                  <div className="font-medium text-slate-100">{info.label}</div>
                  <span className="text-xs font-mono text-slate-500">
                    {info.ticker}
                  </span>
                  {isActive && (
                    <span className="flex items-center gap-1 text-xs text-amber-400 font-mono">
                      <CheckCircle2 size={12} /> ACTIVE
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-1.5 text-xs text-slate-500 mt-1.5">
                  <FileText size={12} />
                  {info.pdf}
                </div>
              </div>

              {!isActive && (
                <button
                  onClick={() => handleSwitch(id)}
                  disabled={switching === id}
                  className="text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 px-3.5 py-2 rounded-md disabled:opacity-50"
                >
                  {switching === id ? "Switching…" : "Switch"}
                </button>
              )}
            </div>
          )
        })}
      </div>

      <p className="text-xs text-slate-600 mt-8">
        Adding a new company currently requires uploading its 10-K and
        rebuilding its index manually — a document upload flow is a planned
        addition here.
      </p>
    </div>
  )
}