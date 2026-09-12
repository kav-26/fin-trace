"""
Fin-Trace: RAG Question Answering
Retrieves relevant chunks from FAISS and asks Groq to answer using them as evidence.
"""

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from embed import search

load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)

PROMPT_TEMPLATE = """You are a financial investigation assistant. Answer the question using ONLY the evidence provided below. Cite the source filename for each claim you make. If the evidence doesn't fully answer the question, say what's missing.

EVIDENCE:
{evidence}

QUESTION:
{question}

ANSWER (with citations):"""


def answer_question(question: str, k: int = 5):
    """Retrieve top-k relevant chunks and generate a cited answer."""
    results = search(question, k=k)

    evidence_blocks = []
    for r in results:
        evidence_blocks.append(f"[Source: {r['source']}]\n{r['text']}")
    evidence_text = "\n\n---\n\n".join(evidence_blocks)

    prompt = PROMPT_TEMPLATE.format(evidence=evidence_text, question=question)
    response = llm.invoke(prompt)

    return {
        "question": question,
        "answer": response.content,
        "sources": [r["source"] for r in results],
        "evidence_used": results
    }


if __name__ == "__main__":
    question = "Why did Microsoft's operating expenses or margins change, according to this report?"

    result = answer_question(question)

    print(f"\n❓ Question: {result['question']}\n")
    print(f"💡 Answer:\n{result['answer']}\n")
    print(f"📚 Sources used: {set(result['sources'])}")