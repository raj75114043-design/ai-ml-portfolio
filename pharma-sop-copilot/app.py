import os
from pathlib import Path

# Run from this project's folder so relative data paths work locally, in Docker and on Streamlit Cloud
os.chdir(Path(__file__).resolve().parent)

import streamlit as st
from src.ingest import load_chunks
from src.retrieval import HybridRetriever
from src.copilot import answer

st.set_page_config(page_title="Pharma SOP Copilot", page_icon="🧪", layout="wide")
st.title("🧪 Pharma SOP Copilot")
st.caption("Ask questions about quality SOPs · every answer is cited to an SOP section · synthetic SOP library")


@st.cache_resource
def setup():
    chunks = load_chunks()
    return chunks, HybridRetriever(chunks)


chunks, retriever = setup()
with st.sidebar:
    st.header("SOP library")
    for sop in sorted({(c["sop_id"], c["sop_title"]) for c in chunks}):
        st.markdown(f"**{sop[0]}** — {sop[1]}")
    k = st.slider("Sections to retrieve", 1, 5, 3)
    st.caption("Out-of-scope questions are refused instead of answered without evidence.")

if "history" not in st.session_state:
    st.session_state.history = []

examples = ["How long is a Phase II OOS investigation?", "When must a deviation be recorded?",
            "What does ALCOA+ mean?", "Can retest results be averaged?"]
cols = st.columns(len(examples))
clicked = next((e for c, e in zip(cols, examples) if c.button(e, use_container_width=True)), None)

for turn in st.session_state.history:
    with st.chat_message(turn["role"]):
        st.markdown(turn["content"])

question = st.chat_input("Ask about OOS, OOT, deviations, CAPA, change control or data integrity") or clicked
if question:
    st.session_state.history.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    result = answer(question, retriever, k)
    with st.chat_message("assistant"):
        st.markdown(result["answer"])
        st.caption(f"Mode: {result['mode']}")
        for h in result["sources"]:
            with st.expander(f"{h['id']} — {h['sop_title']} · {h['section']}"):
                st.write(h["body"])
    st.session_state.history.append({"role": "assistant", "content": result["answer"]})
