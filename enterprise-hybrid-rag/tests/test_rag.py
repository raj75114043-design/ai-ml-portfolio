import json
from pathlib import Path
from src.chunking import chunk_text
from src.retrievers import HybridRetriever
from src.evaluate import evaluate
from src.generate import extractive_answer

kb = json.loads(Path("data/knowledge_base.json").read_text())
chunks = [{"id": d["id"], "text": f"{d['title']}. {c}"} for d in kb for c in chunk_text(d["text"])]
r = HybridRetriever(chunks)


def test_error_code_retrieved_first():
    assert r.search("what does error E401 mean", 3)[0] == "KB-001"


def test_recall_at_3():
    eval_set = json.loads(Path("data/eval_set.json").read_text())
    assert evaluate(r, eval_set, k=3)["recall@k"] >= 0.85


def test_extractive_answer_cites_source():
    docs = [d for d in kb if d["id"] == "KB-001"]
    assert "[KB-001]" in extractive_answer("E401 session token expired", docs)


def test_no_answer_when_unrelated():
    docs = [d for d in kb if d["id"] == "KB-001"]
    assert "does not contain" in extractive_answer("capital of France", docs)
