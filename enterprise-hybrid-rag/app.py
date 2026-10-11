import json
from pathlib import Path
import pandas as pd
import streamlit as st
from src.chunking import chunk_text
from src.retrievers import DenseRetriever, SparseRetriever, HybridRetriever
from src.evaluate import evaluate
from src.generate import generate_answer

st.set_page_config(page_title="Enterprise Hybrid RAG", page_icon="📚", layout="wide")
st.title("📚 Enterprise Hybrid RAG")
st.caption("Dense + BM25 retrieval fused with weighted Reciprocal Rank Fusion · synthetic support knowledge base")


@st.cache_resource
def load():
    kb = json.loads(Path("data/knowledge_base.json").read_text())
    chunks = [{"id": d["id"], "text": f"{d['title']}. {c}"} for d in kb for c in chunk_text(d["text"])]
    return kb, chunks, json.loads(Path("data/eval_set.json").read_text())


@st.cache_resource
def retriever(dense_weight):
    return HybridRetriever(load()[1], dense_weight, round(1 - dense_weight, 2))


kb, chunks, eval_set = load()
by_id = {d["id"]: d for d in kb}

with st.sidebar:
    st.header("Retrieval settings")
    dense_w = st.slider("Dense weight", 0.0, 1.0, 0.8, 0.05, help="Sparse (BM25) weight = 1 − dense weight")
    k = st.slider("Top-K passages", 1, 5, 3)

query = st.text_input("Ask a support question", "getting E401 error when opening billing")
if query:
    r = retriever(dense_w)
    ids = r.search(query, k)
    answer, mode = generate_answer(query, [by_id[i] for i in ids])
    st.subheader("Answer")
    st.success(answer)
    st.caption(f"Generation mode: {mode}")

    st.subheader("Retrieved sources")
    for i in ids:
        with st.expander(f"[{i}] {by_id[i]['title']}"):
            st.write(by_id[i]["text"])

    c1, c2, c3 = st.columns(3)
    c1.markdown("**Dense ranking**")
    c1.write(r.dense.search(query, k))
    c2.markdown("**BM25 ranking**")
    c2.write(r.sparse.search(query, k))
    c3.markdown("**Hybrid (RRF)**")
    c3.write(ids)

with st.expander("Retrieval evaluation on the labelled query set"):
    rows = []
    for name, ret in {"Sparse (BM25)": SparseRetriever(chunks), "Dense": DenseRetriever(chunks),
                      "Hybrid (RRF)": retriever(dense_w)}.items():
        rows.append({"Retriever": name, **evaluate(ret, eval_set, k=3)})
    st.dataframe(pd.DataFrame(rows), hide_index=True)
