"""
Fin-Trace: Knowledge Graph
Builds a NetworkX graph from the investigation's key factors, showing
causal relationships between financial events and outcomes.
"""

import json
import networkx as nx
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)

GRAPH_EXTRACTION_PROMPT = """You are building a knowledge graph from a financial investigation report. Extract the causal relationships between the key factors as a list of edges.

Each edge should be: {{"source": "concept A", "relation": "short verb phrase", "target": "concept B"}}

Use short, consistent node names (e.g. "Revenue Growth", "Operating Expenses", "Net Income", "Q2 Charge") so the same concept is always named the same way across edges.

Respond ONLY with a JSON array of edge objects, nothing else.

KEY FACTORS:
{factors}

REASONING CHAIN:
{reasoning}

EDGES (JSON array only):"""


def extract_relationships(report: dict) -> list[dict]:
    """Use the LLM to extract causal edges from the report's factors and reasoning."""
    factors_text = "\n".join(
        f"- {kf.get('factor', '')}: {kf.get('explanation', '')}"
        for kf in report.get("key_factors", [])
    )

    prompt = GRAPH_EXTRACTION_PROMPT.format(
        factors=factors_text,
        reasoning=report.get("reasoning_chain", "")
    )
    response = llm.invoke(prompt)

    raw = response.content.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        edges = json.loads(raw)
    except json.JSONDecodeError:
        print(f"⚠️  Could not parse graph edges as JSON:\n{raw}")
        edges = []

    return edges


def build_graph(edges: list[dict]) -> nx.DiGraph:
    """Build a directed NetworkX graph from extracted edges."""
    G = nx.DiGraph()
    for edge in edges:
        source = edge.get("source", "").strip()
        target = edge.get("target", "").strip()
        relation = edge.get("relation", "").strip()
        if source and target:
            G.add_edge(source, target, relation=relation)
    return G


def describe_graph(G: nx.DiGraph):
    """Print a readable summary of the graph structure."""
    print(f"\n📊 Knowledge Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges\n")
    for source, target, data in G.edges(data=True):
        print(f"  {source} --[{data.get('relation', '')}]--> {target}")

import matplotlib
matplotlib.use("Agg")  # non-interactive backend, safe for Streamlit
import matplotlib.pyplot as plt


def render_graph_image(G: nx.DiGraph, output_path: str = "knowledge_graph.png"):
    """Render the graph to a readable PNG image using matplotlib."""
    import textwrap

    plt.figure(figsize=(20, 14))
    pos = nx.spring_layout(G, k=2.5, iterations=100, seed=42)

    # Wrap long node labels onto multiple lines instead of letting them run together
    wrapped_labels = {
        node: "\n".join(textwrap.wrap(node, width=14))
        for node in G.nodes()
    }

    # Size nodes to fit their (wrapped) label instead of using a fixed size
    node_sizes = [max(3000, len(node) * 90) for node in G.nodes()]

    nx.draw_networkx_nodes(G, pos, node_color="#4A90D9", node_size=node_sizes, alpha=0.85)
    nx.draw_networkx_labels(G, pos, labels=wrapped_labels, font_size=7, font_weight="bold")
    nx.draw_networkx_edges(
        G, pos, edge_color="#AAAAAA", arrows=True, arrowsize=12,
        connectionstyle="arc3,rad=0.15", width=1.2, node_size=node_sizes
    )

    edge_labels = nx.get_edge_attributes(G, "relation")
    nx.draw_networkx_edge_labels(
        G, pos, edge_labels=edge_labels, font_size=6,
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.7, "pad": 0.5}
    )

    plt.axis("off")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close()

    return output_path

if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).resolve().parent.parent / "agents"))
    sys.path.append(str(Path(__file__).resolve().parent.parent / "rag"))

    from workflow import run_investigation

    question = "Why did Microsoft's profitability change in fiscal year 2023?"
    result = run_investigation(question)
    report = result["report"]

    print("\n--- Extracting relationships ---")
    edges = extract_relationships(report)

    G = build_graph(edges)
    describe_graph(G)