"""
Fin-Trace: Contradiction Detection Agent
Compares findings against each other to flag genuine conflicts or
inconsistencies in the evidence, separate from the Reviewer's synthesis.
"""

import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)

CONTRADICTION_PROMPT = """You are a contradiction-detection agent in a financial investigation system. You will be given several findings, each with cited evidence, gathered by other research agents while investigating the same company.

Your ONLY job is to identify genuine contradictions or inconsistencies between findings — not to summarize or answer the original question. Look for:
- Two findings stating opposite directions for the same metric (e.g. "margin improved" vs "margin declined")
- Numbers for the same metric that don't match across findings
- Management's stated explanation conflicting with what the data shows
- One finding implying something that another finding's evidence contradicts

If you find NO genuine contradictions, say so clearly — do not invent conflicts that aren't there.

Respond ONLY with a JSON object in this structure:
{{
  "contradictions_found": <true or false>,
  "contradictions": [
    {{"finding_a": "short reference to finding A", "finding_b": "short reference to finding B", "conflict": "what specifically conflicts", "severity": "low|medium|high"}}
  ]
}}

FINDINGS:
{findings}

JSON RESULT:"""


def detect_contradictions(findings: list[dict]) -> dict:
    """Compare all findings for genuine contradictions using the LLM."""
    findings_text = ""
    for i, f in enumerate(findings, 1):
        findings_text += f"\n--- Finding {i}: {f['sub_question']} ---\n{f['answer']}\n"

    prompt = CONTRADICTION_PROMPT.format(findings=findings_text)
    response = llm.invoke(prompt)

    raw = response.content.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        print(f"⚠️  Could not parse contradiction output as JSON:\n{raw}")
        result = {"contradictions_found": False, "contradictions": []}

    return result


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).resolve().parent.parent / "rag"))
    sys.path.append(str(Path(__file__).resolve().parent.parent / "graph"))

    from workflow import run_investigation

    question = "Why did Microsoft's profitability change in fiscal year 2023?"
    result = run_investigation(question)

    print("\n--- Checking for contradictions ---")
    contradiction_result = detect_contradictions(result["findings"])

    if contradiction_result["contradictions_found"]:
        print(f"\n⚠️  {len(contradiction_result['contradictions'])} contradiction(s) found:\n")
        for c in contradiction_result["contradictions"]:
            print(f"  Severity: {c['severity'].upper()}")
            print(f"  {c['finding_a']}  vs  {c['finding_b']}")
            print(f"  Conflict: {c['conflict']}\n")
    else:
        print("\n✅ No genuine contradictions found across findings.")