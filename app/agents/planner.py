"""
Fin-Trace: Planner Agent
Breaks a broad financial investigation question into concrete sub-questions.
"""

import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)

PLANNER_PROMPT = """You are a financial investigation planner. Your job is to break a broad financial question into 3-5 specific, answerable sub-questions that together would let an analyst fully answer the original question.

Focus on sub-questions that can be answered using a company's financial documents (annual reports, 10-Ks, earnings calls) — things like revenue drivers, expense changes, margin shifts, segment performance, one-off events (acquisitions, restructuring, write-offs), and management commentary.

Respond ONLY with a JSON array of strings, nothing else. Example format:
["sub-question 1", "sub-question 2", "sub-question 3"]

ORIGINAL QUESTION:
{question}

SUB-QUESTIONS (JSON array only):"""


def plan_investigation(question: str) -> list[str]:
    """Break a broad question into sub-questions using the LLM."""
    prompt = PLANNER_PROMPT.format(question=question)
    response = llm.invoke(prompt)

    raw = response.content.strip()

    # Strip markdown code fences if the model adds them despite instructions
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        sub_questions = json.loads(raw)
    except json.JSONDecodeError:
        print(f"⚠️  Could not parse planner output as JSON:\n{raw}")
        sub_questions = [question]  # fallback: just use the original question

    return sub_questions


if __name__ == "__main__":
    question = "Why did Microsoft's profitability change in fiscal year 2023?"

    sub_questions = plan_investigation(question)

    print(f"\n❓ Original question: {question}\n")
    print("📋 Investigation plan:")
    for i, sq in enumerate(sub_questions, 1):
        print(f"  {i}. {sq}")