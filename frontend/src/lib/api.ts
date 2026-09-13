import axios from "axios"

const API_BASE_URL = "http://127.0.0.1:8000"

export const api = axios.create({
  baseURL: API_BASE_URL,
})

export interface Finding {
  sub_question: string
  answer: string
  sources: string[]
}

export interface KeyFactor {
  factor: string
  explanation: string
  evidence_source: string
}

export interface Contradiction {
  finding_a: string
  finding_b: string
  conflict: string
  severity: "low" | "medium" | "high"
}

export interface Report {
  conclusion: string
  confidence: number
  key_factors: KeyFactor[]
  contradictions_or_gaps: string
  reasoning_chain: string
}

export interface InvestigationResult {
  question: string
  sub_questions: string[]
  findings: Finding[]
  contradictions: {
    contradictions_found: boolean
    contradictions: Contradiction[]
  }
  report: Report
  graph_image_url: string | null
  graph_edges: { source: string; relation: string; target: string }[]
}

export async function runInvestigation(question: string): Promise<InvestigationResult> {
  const response = await api.post<InvestigationResult>("/investigate", { question })
  return response.data
}

export interface FinancialRow {
  metric: string
  segment: string
  fy2022: number
  fy2023: number
  yoy_change: number
  yoy_pct_change: number
}

export interface FinancialAnalysis {
  yoy_table: FinancialRow[]
  margins: Record<string, number>
}

export async function getFinancialData(): Promise<FinancialAnalysis> {
  const response = await api.get<FinancialAnalysis>("/financial-data")
  return response.data
}

export interface CompanyInfo {
  label: string
  ticker: string
  pdf: string
  financial_csv: string
}

export interface CompanyRegistry {
  current: string
  companies: Record<string, CompanyInfo>
}

export async function getCompanies(): Promise<CompanyRegistry> {
  const response = await api.get<CompanyRegistry>("/companies")
  return response.data
}

export async function switchCompany(companyId: string): Promise<void> {
  await api.post("/companies/switch", { company_id: companyId })
}