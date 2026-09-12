"""
Fin-Trace: Reviewer Agent
Synthesizes raw findings from the investigation into a final, structured report:
conclusion, confidence, key factors, reasoning chain, and contradictions.
"""

import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent / "analysis"))
from financial_analyst import analyze, format_for_llm

load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)

REVIEWER_PROMPT = """You are the reviewer in a financial investigation system. You have been given the original question, a set of findings gathered by research agents (with cited evidence), and a set of VERIFIED financial metrics computed directly from structured data (treat these as ground truth — they override any conflicting numbers in the findings).

Your job is to synthesize these into a final investigation report. Think like a financial analyst writing an executive summary. When the findings and verified metrics disagree on a number, use the verified metric and note the correction.

Respond ONLY with a JSON object in this exact structure, nothing else:
{{
  "conclusion": "1-3 sentence direct answer to the original question",
  "confidence": <integer 0-100>,
  "key_factors": [
    {{"factor": "short name", "explanation": "1-2 sentences", "evidence_source": "filename"}}
  ],
  "contradictions_or_gaps": "note any conflicting evidence or missing information across findings, or 'None identified' if none",
  "reasoning_chain": "one short paragraph showing how the factors connect causally (e.g. X led to Y which led to Z)"
}}

Base "confidence" on how complete and consistent the evidence is — lower it if findings mention missing data or gaps.

ORIGINAL QUESTION:
{question}

VERIFIED FINANCIAL METRICS:
{verified_metrics}

FINDINGS:
{findings}

JSON REPORT:"""

def review_investigation(original_question: str, findings: list[dict]) -> dict:
    """Synthesize findings into a final structured investigation report."""
    findings_text = ""
    for i, f in enumerate(findings, 1):
        findings_text += f"\n--- Finding {i}: {f['sub_question']} ---\n{f['answer']}\nSources: {set(f['sources'])}\n"

    verified_metrics_text = format_for_llm(analyze())

    prompt = REVIEWER_PROMPT.format(
        question=original_question,
        verified_metrics=verified_metrics_text,
        findings=findings_text
    )
    response = llm.invoke(prompt)
    # ... rest of the function stays exactly the same


    raw = response.content.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        report = json.loads(raw)
    except json.JSONDecodeError:
        print(f"⚠️  Could not parse reviewer output as JSON:\n{raw}")
        report = {
            "conclusion": raw,
            "confidence": None,
            "key_factors": [],
            "contradictions_or_gaps": "Parsing failed — see raw conclusion.",
            "reasoning_chain": ""
        }

    return report


def print_report(question: str, report: dict):
    """Pretty-print the final investigation report, matching the original spec's format."""
    print("\n" + "=" * 60)
    print("FIN-TRACE — INVESTIGATION REPORT")
    print("=" * 60)
    print(f"\nQuestion: {question}\n")
    print(f"Conclusion:\n{report['conclusion']}\n")
    print(f"Confidence: {report['confidence']}%\n")
    print("Key Factors:")
    for i, kf in enumerate(report.get("key_factors", []), 1):
        print(f"  {i}. {kf.get('factor', '')}")
        print(f"     {kf.get('explanation', '')}")
        print(f"     Evidence: {kf.get('evidence_source', '')}")
    print(f"\nReasoning:\n{report.get('reasoning_chain', '')}")
    print(f"\nContradictions/Gaps:\n{report.get('contradictions_or_gaps', '')}")
    print("=" * 60)


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).resolve().parent.parent / "rag"))

    from investigate import investigate

    question = "Why did Microsoft's profitability change in fiscal year 2023?"
    inv_result = investigate(question)

    report = review_investigation(inv_result["original_question"], inv_result["findings"])
    print_report(question, report)