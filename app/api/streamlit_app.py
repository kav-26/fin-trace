"""
Fin-Trace: Streamlit UI
Simple investigation interface — ask a question, see the full report.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "graph"))
sys.path.append(str(Path(__file__).resolve().parent.parent / "rag"))
sys.path.append(str(Path(__file__).resolve().parent.parent / "agents"))
sys.path.append(str(Path(__file__).resolve().parent.parent / "graph"))
from knowledge_graph import extract_relationships, build_graph, render_graph_image

import streamlit as st
from workflow import run_investigation

st.set_page_config(page_title="Fin-Trace", page_icon="🔍", layout="wide")

st.title("🔍 Fin-Trace")
st.caption("AI Financial Investigation Engine")

st.markdown(
    "Ask a complex question about a company's financial performance. "
    "Fin-Trace will plan an investigation, research evidence, and synthesize a report."
)

question = st.text_input(
    "Investigation question",
    placeholder="e.g. Why did Microsoft's profitability change in fiscal year 2023?"
)

run_button = st.button("🚀 Investigate", type="primary")

if run_button and question.strip():
    with st.status("Running investigation...", expanded=True) as status:
        st.write("🧭 Planning investigation...")
        result = run_investigation(question)
        status.update(label="Investigation complete", state="complete")

    report = result["report"]

    st.divider()
    st.header("Investigation Report")

    st.subheader("Conclusion")
    st.write(report.get("conclusion", ""))

    confidence = report.get("confidence", 0) or 0
    st.subheader(f"Confidence: {confidence}%")
    st.progress(confidence / 100)

    st.subheader("Key Factors")
    for kf in report.get("key_factors", []):
        with st.container(border=True):
            st.markdown(f"**{kf.get('factor', '')}**")
            st.write(kf.get("explanation", ""))
            st.caption(f"📄 Evidence: {kf.get('evidence_source', '')}")

    st.subheader("Reasoning Chain")
    st.write(report.get("reasoning_chain", ""))

    st.subheader("Contradictions / Gaps")
    st.write(report.get("contradictions_or_gaps", ""))

    with st.expander("🔬 Show raw sub-question findings"):
        for i, f in enumerate(result["sub_questions"], 1):
            st.markdown(f"**{i}. {f}**")
        st.divider()
        for i, finding in enumerate(result["findings"], 1):
            st.markdown(f"**Finding {i}: {finding['sub_question']}**")
            st.write(finding["answer"])
            st.caption(f"Sources: {set(finding['sources'])}")
            st.divider()
            
    contradiction_result = result.get("contradictions", {})
    if contradiction_result.get("contradictions_found"):
        st.subheader("⚡ Detected Inconsistencies")
        for c in contradiction_result["contradictions"]:
            severity = c.get("severity", "low")
            severity_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(severity, "🟢")
            with st.container(border=True):
                st.markdown(f"{severity_color} **{severity.upper()} severity**")
                st.write(c.get("conflict", ""))
                st.caption(f"{c.get('finding_a', '')} vs {c.get('finding_b', '')}")

    st.subheader("Knowledge Graph")
    with st.spinner("Building evidence relationship graph..."):
        edges = extract_relationships(report)
        G = build_graph(edges)
        if G.number_of_nodes() > 0:
            image_path = render_graph_image(G)
            st.image(image_path, caption=f"{G.number_of_nodes()} concepts, {G.number_of_edges()} causal relationships")
        else:
            st.info("Not enough structured factors to build a graph for this report.")

elif run_button:
    st.warning("Please enter a question first.")