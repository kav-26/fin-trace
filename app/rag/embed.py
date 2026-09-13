"""
Fin-Trace: Embeddings + Vector Store
Converts document chunks into vectors and builds a searchable FAISS index.
"""

import os
import json
import pickle
from pathlib import Path
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
import faiss
import numpy as np

from ingest import load_all_documents, chunk_documents

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
INDEX_DIR = PROJECT_ROOT / "data" / "index"
INDEX_DIR.mkdir(parents=True, exist_ok=True)

COMPANIES_CONFIG_PATH = PROJECT_ROOT / "data" / "companies.json"


def get_current_company() -> str:
    """Read the currently active company ID from the registry."""
    with open(COMPANIES_CONFIG_PATH) as f:
        config = json.load(f)
    return config["current"]


def get_index_paths(company_id: str = None):
    """Get the FAISS index + metadata paths for a specific company (or current if unspecified)."""
    if company_id is None:
        company_id = get_current_company()
    return (
        INDEX_DIR / f"{company_id}_fin_trace.index",
        INDEX_DIR / f"{company_id}_fin_trace_metadata.pkl",
    )


def build_vector_store(chunks: list[dict]):
    """Embed all chunks and build a FAISS index. Saves index + metadata to disk."""
    faiss_index_path, metadata_path = get_index_paths()

    embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    texts = [chunk["text"] for chunk in chunks]
    print(f"🔢 Embedding {len(texts)} chunks... (this calls the OpenAI API)")

    vectors = embeddings_model.embed_documents(texts)
    vectors_np = np.array(vectors, dtype="float32")

    dimension = vectors_np.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(vectors_np)

    faiss.write_index(index, str(faiss_index_path))
    with open(metadata_path, "wb") as f:
        pickle.dump(chunks, f)

    print(f"✅ FAISS index built: {index.ntotal} vectors, dimension {dimension}")
    print(f"✅ Saved index to {faiss_index_path}")
    print(f"✅ Saved metadata to {metadata_path}")

    return index, chunks


def load_vector_store():
    """Load the previously built FAISS index + its metadata for the current company."""
    faiss_index_path, metadata_path = get_index_paths()

    if not faiss_index_path.exists():
        raise FileNotFoundError(
            f"No FAISS index found for current company ({get_current_company()}). "
            f"Run build_vector_store() first."
        )

    index = faiss.read_index(str(faiss_index_path))
    with open(metadata_path, "rb") as f:
        chunks = pickle.load(f)

    return index, chunks


def search(query: str, k: int = 5):
    """Embed a query and return the top-k most similar chunks."""
    embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    index, chunks = load_vector_store()

    query_vector = embeddings_model.embed_query(query)
    query_np = np.array([query_vector], dtype="float32")

    distances, indices = index.search(query_np, k)

    results = []
    for rank, idx in enumerate(indices[0]):
        chunk = chunks[idx]
        results.append({
            "rank": rank + 1,
            "source": chunk["source"],
            "text": chunk["text"],
            "distance": float(distances[0][rank])
        })

    return results


if __name__ == "__main__":
    print(f"📌 Building index for current company: {get_current_company().upper()}")

    docs = load_all_documents()
    chunks = chunk_documents(docs)

    build_vector_store(chunks)

    print("\n--- Test search ---")
    query = "Why did revenue or profitability change?"
    results = search(query, k=3)

    for r in results:
        print(f"\n[{r['rank']}] Source: {r['source']} | Distance: {r['distance']:.4f}")
        print(r["text"][:300])