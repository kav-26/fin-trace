import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { AlertTriangle, CheckCircle2, ArrowLeft } from "lucide-react"
import type { InvestigationResult } from "@/lib/api"
import KnowledgeGraphView from "@/components/KnowledgeGraphView"

type Tab = "summary" | "evidence" | "graph"

export default function ReportPage() {
  const [result, setResult] = useState<InvestigationResult | null>(null)
  const [tab, setTab] = useState<Tab>("summary")
  const navigate = useNavigate()

  useEffect(() => {
    const stored = sessionStorage.getItem("fin-trace-last-result")
    if (stored) setResult(JSON.parse(stored))
  }, [])

  if (!result) {
    return (
      <div className="p-8 max-w-2xl mx-auto text-center mt-24">
        <p className="text-slate-400 mb-4">No investigation to show yet.</p>
        <button
          onClick={() => navigate("/")}
          className="text-amber-400 text-sm font-medium hover:underline"
        >
          ← Start an investigation
        </button>
      </div>
    )
  }

  const { report, contradictions, findings, question } = result

  return (
    <div className="max-w-3xl mx-auto px-8 py-12">
      <button
        onClick={() => navigate("/")}
        className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-300 mb-6"
      >
        <ArrowLeft size={14} /> New investigation
      </button>

      <div className="text-xs font-mono tracking-widest text-amber-400 mb-2">
        INVESTIGATION REPORT
      </div>
      <h1 className="text-lg font-medium text-slate-300 mb-8">{question}</h1>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-slate-800 mb-8">
        {(["summary", "evidence", "graph"] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2.5 text-sm font-medium capitalize border-b-2 transition-colors ${
              tab === t
                ? "border-amber-400 text-amber-400"
                : "border-transparent text-slate-500 hover:text-slate-300"
            }`}
          >
            {t === "graph" ? "Knowledge Graph" : t}
          </button>
        ))}
      </div>

      {tab === "summary" && (
        <div className="space-y-10">
          {/* Conclusion */}
          <section>
            <div className="text-xs font-mono text-slate-500 mb-3">CONCLUSION</div>
            <p className="font-serif text-xl leading-relaxed text-slate-100">
              {report.conclusion}
            </p>
            <div className="flex items-center gap-3 mt-5">
              <span className="font-mono text-lg text-amber-400 font-semibold">
                {report.confidence}%
              </span>
              <div className="flex-1 h-1 bg-slate-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-amber-400 rounded-full transition-all"
                  style={{ width: `${report.confidence}%` }}
                />
              </div>
            </div>
          </section>

          {/* Key factors */}
          <section>
            <div className="text-xs font-mono text-slate-500 mb-3">KEY FACTORS</div>
            <div className="divide-y divide-slate-800">
              {report.key_factors.map((kf, i) => (
                <div key={i} className="py-4">
                  <div className="font-medium text-slate-100 mb-1">{kf.factor}</div>
                  <div className="text-sm text-slate-400 leading-relaxed">
                    {kf.explanation}
                  </div>
                  <div className="text-xs font-mono text-slate-500 mt-2">
                    SOURCE — {kf.evidence_source}
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Reasoning */}
          <section>
            <div className="text-xs font-mono text-slate-500 mb-3">REASONING CHAIN</div>
            <p className="text-sm text-slate-400 leading-relaxed">
              {report.reasoning_chain}
            </p>
          </section>

          {/* Detected inconsistencies */}
          <section>
            <div className="text-xs font-mono text-slate-500 mb-3">
              DETECTED INCONSISTENCIES
            </div>
            {contradictions.contradictions_found &&
            contradictions.contradictions.length > 0 ? (
              <div className="space-y-2">
                {contradictions.contradictions.map((c, i) => {
                  const sevColor =
                    c.severity === "high"
                      ? "border-red-500 text-red-400"
                      : c.severity === "medium"
                      ? "border-amber-500 text-amber-400"
                      : "border-emerald-500 text-emerald-400"
                  return (
                    <div
                      key={i}
                      className={`border-l-2 bg-slate-900 rounded-r-md p-3.5 ${sevColor}`}
                    >
                      <div className="text-[10px] font-mono tracking-wide mb-1">
                        {c.severity.toUpperCase()} SEVERITY
                      </div>
                      <div className="text-sm text-slate-200">{c.conflict}</div>
                      <div className="text-xs font-mono text-slate-500 mt-1.5">
                        {c.finding_a} vs {c.finding_b}
                      </div>
                    </div>
                  )
                })}
              </div>
            ) : (
              <div className="flex items-center gap-2 text-sm text-emerald-400">
                <CheckCircle2 size={16} />
                No contradictions detected across findings.
              </div>
            )}
          </section>

          {/* Gaps */}
          <section>
            <div className="text-xs font-mono text-slate-500 mb-3">GAPS IN EVIDENCE</div>
            <div className="flex items-start gap-2 text-sm text-slate-400 leading-relaxed">
              <AlertTriangle size={15} className="text-slate-500 mt-0.5 shrink-0" />
              {report.contradictions_or_gaps || "None identified."}
            </div>
          </section>
        </div>
      )}

      {tab === "evidence" && (
        <div className="space-y-6">
          {findings.map((f, i) => (
            <div key={i} className="border-b border-slate-800 pb-6">
              <div className="font-medium text-sm text-slate-100 mb-2">
                {f.sub_question}
              </div>
              <div className="text-sm text-slate-400 leading-relaxed whitespace-pre-wrap">
                {f.answer}
              </div>
              <div className="text-xs font-mono text-slate-500 mt-2">
                {[...new Set(f.sources)].join(", ")}
              </div>
            </div>
          ))}
        </div>
      )}

      {tab === "graph" && <KnowledgeGraphView edges={result.graph_edges} />}
    </div>
  )
}