"""
Fin-Trace: Document Ingestion
Extracts text from PDFs and splits it into chunks ready for embedding.
"""

import os
from pathlib import Path
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DOCS_DIR = PROJECT_ROOT / "data" / "documents"


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract raw text from a single PDF file, page by page. Skips unreadable pages."""
    reader = PdfReader(str(pdf_path), strict=False)
    full_text = []

    for page_num, page in enumerate(reader.pages):
        try:
            text = page.extract_text() or ""
        except Exception as e:
            print(f"   ⚠️  Skipping page {page_num + 1} (unreadable): {type(e).__name__}")
            continue

        if text.strip():
            full_text.append(f"[Page {page_num + 1}]\n{text}")

    return "\n\n".join(full_text)


def load_all_documents() -> list[dict]:
    """Load every PDF in data/documents/ and return raw text + metadata."""
    documents = []

    pdf_files = list(DOCS_DIR.glob("*.pdf"))
    if not pdf_files:
        print(f"⚠️  No PDFs found in {DOCS_DIR}/. Add some and re-run.")
        return documents

    for pdf_path in pdf_files:
        print(f"📄 Extracting: {pdf_path.name}")
        text = extract_text_from_pdf(pdf_path)
        documents.append({
            "source": pdf_path.name,
            "text": text
        })

    return documents


def chunk_documents(documents: list[dict], chunk_size: int = 1000, chunk_overlap: int = 200) -> list[dict]:
    """Split each document's text into overlapping chunks, preserving source metadata."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    all_chunks = []
    for doc in documents:
        chunks = splitter.split_text(doc["text"])
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "source": doc["source"],
                "chunk_id": f"{doc['source']}_{i}",
                "text": chunk
            })

    return all_chunks


if __name__ == "__main__":
    docs = load_all_documents()
    print(f"\n✅ Loaded {len(docs)} document(s)")

    chunks = chunk_documents(docs)
    print(f"✅ Split into {len(chunks)} chunk(s)")

    if chunks:
        print("\n--- Sample chunk ---")
        print(f"Source: {chunks[0]['source']}")
        print(f"Text: {chunks[0]['text'][:300]}...")