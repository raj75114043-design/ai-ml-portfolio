import json
from pathlib import Path
from src.ingest import load_chunks
from src.retrieval import HybridRetriever
from src.copilot import answer, REFUSAL

chunks = load_chunks()
retriever = HybridRetriever(chunks)


def test_all_sops_indexed():
    assert len({c["sop_id"] for c in chunks}) == 6


def test_retrieval_hit_at_3():
    eval_set = json.loads(Path("data/eval_set.json").read_text())
    hits = sum(any(h["sop_id"] == e["sop"] for h in retriever.search(e["question"], 3)) for e in eval_set)
    assert hits / len(eval_set) >= 0.85


def test_answer_is_cited():
    r = answer("How long do we have to complete a Phase Ib OOS investigation?", retriever)
    assert "SOP-QA-001" in r["answer"] and "five working days" in r["answer"]


def test_out_of_scope_refused():
    assert answer("What is the capital of France?", retriever)["answer"] == REFUSAL


def test_timing_question_surfaces_timeline():
    r = answer("How long is a Phase II OOS investigation?", retriever)
    assert "thirty calendar days" in r["answer"]


def test_sample_questions_are_answered():
    for q in ["What does ALCOA+ mean?", "Can retest results be averaged?", "When must a deviation be recorded?"]:
        assert answer(q, retriever)["answer"] != REFUSAL
    assert "Attributable" in answer("What does ALCOA+ mean?", retriever)["answer"]
    assert "Averaging" in answer("Can retest results be averaged?", retriever)["answer"]
