"""
Fin-Trace: FastAPI Backend
Exposes the investigation pipeline as a REST API for the frontend to call.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "graph"))
sys.path.append(str(Path(__file__).resolve().parent.parent / "rag"))
sys.path.append(str(Path(__file__).resolve().parent.parent / "agents"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from workflow import run_investigation
from knowledge_graph import extract_relationships, build_graph, render_graph_image

app = FastAPI(title="Fin-Trace API")

# Allow the frontend (opened as a local file or served separately) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated images (like the knowledge graph PNG) so the frontend can display them
IMAGES_DIR = Path(__file__).resolve().parent / "static_output"
IMAGES_DIR.mkdir(exist_ok=True)
app.mount("/images", StaticFiles(directory=str(IMAGES_DIR)), name="images")


class InvestigationRequest(BaseModel):
    question: str


@app.get("/")
def health_check():
    return {"status": "Fin-Trace API is running"}


@app.post("/investigate")
def investigate(request: InvestigationRequest):
    """Run a full investigation and return the report + knowledge graph."""
    result = run_investigation(request.question)
    report = result["report"]

    # Build and save the knowledge graph image
    edges = extract_relationships(report)
    graph_image_url = None
    if edges:
        G = build_graph(edges)
        if G.number_of_nodes() > 0:
            image_path = IMAGES_DIR / "knowledge_graph.png"
            render_graph_image(G, output_path=str(image_path))
            graph_image_url = "/images/knowledge_graph.png"

    return {
        "question": request.question,
        "sub_questions": result["sub_questions"],
        "findings": result["findings"],
        "contradictions": result.get("contradictions", {}),
        "report": report,
        "graph_image_url": graph_image_url
    }