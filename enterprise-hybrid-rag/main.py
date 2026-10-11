import json
from pathlib import Path
from src.chunking import chunk_text
from src.retrievers import DenseRetriever, SparseRetriever, HybridRetriever
from src.evaluate import evaluate

kb = json.loads(Path("data/knowledge_base.json").read_text())
eval_set = json.loads(Path("data/eval_set.json").read_text())
chunks = [{"id": d["id"], "text": f"{d['title']}. {c}"} for d in kb for c in chunk_text(d["text"])]
by_id = {d["id"]: d for d in kb}

retrievers = {"Sparse (BM25)": SparseRetriever(chunks), "Dense": DenseRetriever(chunks), "Hybrid (RRF)": HybridRetriever(chunks)}
print(f"Dense backend: {retrievers['Dense'].backend}\n")
print(f"{'Retriever':<16}{'Recall@3':>10}{'MRR':>8}")
for name, r in retrievers.items():
    m = evaluate(r, eval_set, k=3)
    print(f"{name:<16}{m['recall@k']:>10}{m['mrr']:>8}")

query = "getting E401 error when opening billing"
print(f"\nQuery: {query}")
for doc_id in retrievers["Hybrid (RRF)"].search(query, k=2):
    print(f"  [{doc_id}] {by_id[doc_id]['title']}")
print("\nThe retrieved passages are passed to the LLM as grounded context with citations.")
