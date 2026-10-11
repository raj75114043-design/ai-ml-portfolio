import json
from pathlib import Path
from src.ingest import load_chunks
from src.retrieval import HybridRetriever
from src.copilot import answer

chunks = load_chunks()
retriever = HybridRetriever(chunks)
eval_set = json.loads(Path("data/eval_set.json").read_text())

hits = sum(any(h["sop_id"] == e["sop"] for h in retriever.search(e["question"], 3)) for e in eval_set)
top1 = sum(retriever.search(e["question"], 1)[0]["sop_id"] == e["sop"] for e in eval_set)
print(f"Indexed {len(chunks)} SOP sections from {len({c['sop_id'] for c in chunks})} SOPs")
print(f"Retrieval: Hit@3 = {hits / len(eval_set):.2f}, Hit@1 = {top1 / len(eval_set):.2f} on {len(eval_set)} questions\n")
for q in ["How long do we have to complete a Phase Ib OOS investigation?", "What is the capital of France?"]:
    r = answer(q, retriever)
    print(f"Q: {q}\nA: {r['answer']}\n")
