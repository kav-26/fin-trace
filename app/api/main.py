"""
Fin-Trace: FastAPI Backend
Exposes the investigation pipeline as a REST API for the frontend to call.
"""

import sys
import json
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "graph"))
sys.path.append(str(Path(__file__).resolve().parent.parent / "rag"))
sys.path.append(str(Path(__file__).resolve().parent.parent / "agents"))
sys.path.append(str(Path(__file__).resolve().parent.parent / "analysis"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

COMPANIES_CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "companies.json"

from .mock_data import MOCK_INVESTIGATION_RESPONSE
from workflow import run_investigation
from knowledge_graph import extract_relationships, build_graph, render_graph_image
from financial_analyst import analyze
from .database import init_db, save_investigation, list_investigations, get_investigation

app = FastAPI(title="Fin-Trace API")

USE_MOCK_DATA = False  # <-- flip to False for real (token-consuming) investigations
init_db()
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

class SwitchCompanyRequest(BaseModel):
    company_id: str


class InvestigationRequest(BaseModel):
    question: str


@app.get("/")
def health_check():
    return {"status": "Fin-Trace API is running"}

@app.post("/investigate")
def investigate(request: InvestigationRequest):
    """Run a full investigation, save it to history, and return the report + graph."""

    with open(COMPANIES_CONFIG_PATH) as f:
        config = json.load(f)
    current_company = config["companies"][config["current"]]["label"]

    if USE_MOCK_DATA:
        print("🎭 Using mock data (no Groq tokens consumed)")
        result = MOCK_INVESTIGATION_RESPONSE
        investigation_id = save_investigation(request.question, current_company, result)
        return {**result, "id": investigation_id}

    result = run_investigation(request.question)
    report = result["report"]

    edges = extract_relationships(report)
    graph_image_url = None
    if edges:
        G = build_graph(edges)
        if G.number_of_nodes() > 0:
            image_path = IMAGES_DIR / "knowledge_graph.png"
            render_graph_image(G, output_path=str(image_path))
            graph_image_url = "/images/knowledge_graph.png"

    full_result = {
        "question": request.question,
        "sub_questions": result["sub_questions"],
        "findings": result["findings"],
        "contradictions": result.get("contradictions", {}),
        "report": report,
        "graph_image_url": graph_image_url,
        "graph_edges": edges,
    }

    investigation_id = save_investigation(request.question, current_company, full_result)
    return {**full_result, "id": investigation_id}


@app.get("/financial-data")
def financial_data():
    """Return computed financial metrics (YoY changes, margins) for the current company."""
    return analyze()

@app.get("/companies")
def list_companies():
    """Return the company registry: all available companies + which is currently active."""
    with open(COMPANIES_CONFIG_PATH) as f:
        config = json.load(f)
    return config


@app.post("/companies/switch")
def switch_company(request: SwitchCompanyRequest):
    """Switch the active company. Requires that company's FAISS index already exists."""
    with open(COMPANIES_CONFIG_PATH) as f:
        config = json.load(f)

    if request.company_id not in config["companies"]:
        return {"error": f"Unknown company '{request.company_id}'"}, 400

    config["current"] = request.company_id

    with open(COMPANIES_CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)

    return {"status": "switched", "current": request.company_id}

@app.get("/history")
def get_history():
    """Return recent past investigations (summary only)."""
    return list_investigations()


@app.get("/history/{investigation_id}")
def get_history_item(investigation_id: int):
    """Return the full result for one past investigation."""
    result = get_investigation(investigation_id)
    if result is None:
        return {"error": "Investigation not found"}, 404
    return result