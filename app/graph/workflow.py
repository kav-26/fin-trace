"""
Fin-Trace: LangGraph Orchestration
Defines the investigation as a state graph: Planner -> Research -> Reviewer.
"""

import sys
from pathlib import Path
from typing import TypedDict
from contradiction import detect_contradictions

sys.path.append(str(Path(__file__).resolve().parent.parent / "rag"))
sys.path.append(str(Path(__file__).resolve().parent.parent / "agents"))

from langgraph.graph import StateGraph, END

from planner import plan_investigation
from qa import answer_question
from reviewer import review_investigation


class InvestigationState(TypedDict):
    """The shared state that flows through every node in the graph."""
    original_question: str
    sub_questions: list[str]
    findings: list[dict]
    report: dict


class InvestigationState(TypedDict):
    original_question: str
    sub_questions: list[str]
    findings: list[dict]
    contradictions: dict
    report: dict

def planner_node(state: InvestigationState) -> dict:
    """Node 1: break the question into sub-questions."""
    print("🧭 [Planner] Breaking down question...")
    sub_questions = plan_investigation(state["original_question"])
    return {"sub_questions": sub_questions}


def research_node(state: InvestigationState) -> dict:
    """Node 2: answer every sub-question using RAG."""
    print(f"🔎 [Research] Answering {len(state['sub_questions'])} sub-questions...")
    findings = []
    for sub_q in state["sub_questions"]:
        result = answer_question(sub_q, k=4)
        findings.append({
            "sub_question": sub_q,
            "answer": result["answer"],
            "sources": result["sources"]
        })
    return {"findings": findings}


def reviewer_node(state: InvestigationState) -> dict:
    """Node 3: synthesize findings into a final report."""
    print("📝 [Reviewer] Synthesizing final report...")
    report = review_investigation(state["original_question"], state["findings"])
    return {"report": report}


def contradiction_node(state: InvestigationState) -> dict:
    """Node: check findings for genuine contradictions."""
    print("⚡ [Contradiction] Checking for inconsistencies...")
    result = detect_contradictions(state["findings"])
    return {"contradictions": result}

def build_graph():
    graph = StateGraph(InvestigationState)

    graph.add_node("planner", planner_node)
    graph.add_node("research", research_node)
    graph.add_node("contradiction", contradiction_node)
    graph.add_node("reviewer", reviewer_node)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "research")
    graph.add_edge("research", "contradiction")
    graph.add_edge("contradiction", "reviewer")
    graph.add_edge("reviewer", END)

    return graph.compile()


def run_investigation(question: str) -> dict:
    """Run a full investigation through the compiled graph."""
    app = build_graph()
    result = app.invoke({"original_question": question})
    return result


if __name__ == "__main__":
    from reviewer import print_report

    question = "Why did Microsoft's profitability change in fiscal year 2023?"
    result = run_investigation(question)

    print_report(question, result["report"])