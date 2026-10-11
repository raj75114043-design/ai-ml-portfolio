import os
from pathlib import Path

# Run from this project's folder so relative data paths work locally, in Docker and on Streamlit Cloud
os.chdir(Path(__file__).resolve().parent)

import pandas as pd
import streamlit as st
from src.graph import build_graph

st.set_page_config(page_title="Multi-Agent RCA", page_icon="🤖", layout="wide")
st.title("🤖 Multi-Agent Root-Cause Analysis")
st.caption("LangGraph workflow: Orchestrator → Planner → Traversal → Response · synthetic telecom data")


@st.cache_resource
def get_app():
    return build_graph()


samples = ["Why is SITE-101 down?", "Why is SITE-103 delayed?", "What is the status of SITE-102?", "Why is SITE-999 down?"]
cols = st.columns(len(samples))
for col, sample in zip(cols, samples):
    if col.button(sample, use_container_width=True):
        st.session_state["query"] = sample

query = st.text_input("Ask an operational question", key="query", placeholder="e.g. Why is SITE-101 down?")

if query:
    trace, final = [], {}
    for step in get_app().stream({"query": query}):
        for node, update in step.items():
            trace.append(node)
            final.update(update or {})

    st.subheader("Answer")
    st.success(final.get("answer", "No answer produced."))

    left, right = st.columns([1, 2])
    with left:
        st.subheader("Agent trace")
        for i, node in enumerate(trace, 1):
            st.markdown(f"**{i}. {node.title()}**")
        st.caption(f"Intent: `{final.get('intent', '-')}` · Plan: `{final.get('plan', [])}`")
    with right:
        st.subheader("Evidence collected")
        if final.get("evidence"):
            st.dataframe(pd.DataFrame(final["evidence"]).fillna("").astype(str), hide_index=True)
        else:
            st.info("No evidence was collected for this query.")

with st.expander("How it works"):
    st.markdown(
        "- **Orchestrator** detects intent and extracts the site ID\n"
        "- **Planner** decides which relationships to traverse\n"
        "- **Traversal** calls read-only tools (MCP-ready) and collects evidence\n"
        "- **Response** answers strictly from collected evidence\n\n"
        "Explicit graph transitions and an iteration cap prevent infinite loops."
    )
