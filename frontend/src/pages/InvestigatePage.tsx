
import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { Search, Loader2 } from "lucide-react"
import { runInvestigation, type InvestigationResult } from "@/lib/api"

const EXAMPLE_QUESTIONS = [
  "Why did Microsoft's profitability change in fiscal year 2023?",
  "Why did Tesla's net income rise despite falling margins in 2023?",
]

const AGENT_STEPS = [
  "Planning investigation…",
  "Retrieving evidence from filings…",
  "Checking for contradictions…",
  "Synthesizing report…",
]

export default function InvestigatePage() {
  const [question, setQuestion] = useState("")
  const [loading, setLoading] = useState(false)
  const [stepIndex, setStepIndex] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  async function handleInvestigate() {
    if (!question.trim()) return

    setLoading(true)
    setError(null)
    setStepIndex(0)

    const interval = setInterval(() => {
      setStepIndex((i) => (i + 1) % AGENT_STEPS.length)
    }, 3500)

    try {
      const result: InvestigationResult = await runInvestigation(question)

      // Store the result so the Report page can read it.
      // (Swapped for real state management / backend history once persistence exists.)
      sessionStorage.setItem("fin-trace-last-result", JSON.stringify(result))

      clearInterval(interval)
      navigate("/report")
    } catch (err) {
      clearInterval(interval)
      setError(
        err instanceof Error
          ? `Investigation failed: ${err.message}. Confirm the API is running at http://127.0.0.1:8000.`
          : "Investigation failed."
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto px-8 py-16">
      <div className="text-xs font-mono tracking-widest text-amber-400 mb-3">
        FIN-TRACE
      </div>
      <h1 className="text-3xl font-serif font-semibold mb-3">
        AI Financial Investigation Engine
      </h1>
      <p className="text-slate-400 text-sm mb-8 max-w-lg">
        Ask why a company's financial performance changed. Fin-Trace plans an
        investigation, retrieves evidence from its filings, checks for
        contradictions, and returns a grounded, cited conclusion.
      </p>

      <div className="flex gap-2 border border-slate-800 bg-slate-900 rounded-lg p-1.5">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleInvestigate()}
          placeholder="Why did Tesla's net income rise despite falling margins in 2023?"
          className="flex-1 bg-transparent outline-none px-3 py-2 text-sm placeholder:text-slate-500"
          disabled={loading}
        />
        <button
          onClick={handleInvestigate}
          disabled={loading}
          className="flex items-center gap-2 bg-amber-400 text-slate-950 font-semibold text-sm px-4 py-2 rounded-md disabled:opacity-50"
        >
          {loading ? <Loader2 size={16} className="animate-spin" /> : <Search size={16} />}
          Investigate
        </button>
      </div>

      <div className="flex gap-2 mt-3 flex-wrap">
        {EXAMPLE_QUESTIONS.map((q) => (
          <button
            key={q}
            onClick={() => setQuestion(q)}
            disabled={loading}
            className="text-xs font-mono text-slate-400 border border-slate-800 rounded-md px-2.5 py-1.5 hover:border-slate-600 hover:text-slate-200 disabled:opacity-50"
          >
            {q}
          </button>
        ))}
      </div>

      {loading && (
        <div className="mt-8 flex items-center gap-2 text-sm font-mono text-slate-400">
          <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
          {AGENT_STEPS[stepIndex]}
        </div>
      )}

      {error && (
        <div className="mt-8 border border-red-900 bg-red-950/30 text-red-400 text-sm rounded-md p-4">
          {error}
        </div>
      )}
    </div>
  )
}