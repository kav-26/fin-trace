"""
Fin-Trace: Investigation Orchestrator (pre-LangGraph version)
Runs the Planner to get sub-questions, then answers each one using RAG.
This is a simple sequential version — we'll upgrade it to a proper
LangGraph state machine once more agents exist.
"""

import sys
from pathlib import Path

# Allow importing from app/rag/ and app/agents/ regardless of cwd
sys.path.append(str(Path(__file__).resolve().parent.parent / "rag"))

from planner import plan_investigation
from qa import answer_question


def investigate(question: str) -> dict:
    """Run a full investigation: plan sub-questions, answer each with evidence."""
    print(f"🔍 Investigating: {question}\n")

    sub_questions = plan_investigation(question)
    print(f"📋 Plan: {len(sub_questions)} sub-questions\n")

    findings = []
    for i, sub_q in enumerate(sub_questions, 1):
        print(f"  [{i}/{len(sub_questions)}] {sub_q}")
        result = answer_question(sub_q, k=4)
        findings.append({
            "sub_question": sub_q,
            "answer": result["answer"],
            "sources": result["sources"]
        })

    return {
        "original_question": question,
        "sub_questions": sub_questions,
        "findings": findings
    }


if __name__ == "__main__":
    question = "Why did Microsoft's profitability change in fiscal year 2023?"

    report = investigate(question)

    print("\n" + "=" * 60)
    print("INVESTIGATION FINDINGS")
    print("=" * 60)

    for i, finding in enumerate(report["findings"], 1):
        print(f"\n--- Finding {i}: {finding['sub_question']} ---")
        print(finding["answer"])
        print(f"Sources: {set(finding['sources'])}")