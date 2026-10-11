"""Question answering over SOPs with mandatory citations and an out-of-scope guardrail."""
import math
import os
import re
from .retrieval import tokenize

MIN_BM25 = 0.5  # below this, the SOP library is assumed not to cover the question
REFUSAL = ("I could not find this in the approved SOP library. Please consult Quality Assurance "
           "rather than relying on an unsupported answer.")


TIMING_Q = re.compile(r"\b(how long|how many (days|hours|months)|when|timeline|deadline|within|how often|how soon)\b", re.I)
TIMING_S = re.compile(r"\b(\d+|one|two|three|five|thirty|ninety|six|twenty-four|twenty-five)\b[\w\s-]*\b(day|days|hour|hours|month|months|year|years)\b|\bsame working day\b", re.I)


def _stem(token):
    for suffix in ("ing", "ed", "es", "s", "d"):
        if token.endswith(suffix) and len(token) > len(suffix) + 2:
            return token[: -len(suffix)]
    return token


def _terms(text):
    return {_stem(t) for t in tokenize(text)}


def _extractive(question, hits, corpus, n=2):
    """Pick the sentences that best match the question, weighting rare terms (IDF) higher."""
    docs = [_terms(c["body"]) for c in corpus]
    idf = lambda t: math.log((1 + len(docs)) / (1 + sum(t in d for d in docs))) + 1
    q = _terms(question)
    asks_timing = bool(TIMING_Q.search(question))
    scored = []
    for h in hits:
        heading_bonus = sum(idf(t) for t in q & _terms(h["section"]))  # e.g. "ALCOA+ Principles"
        for s in re.split(r"(?<=[.!?])\s+", h["body"]):
            score = sum(idf(t) for t in q & _terms(s)) + heading_bonus
            if asks_timing and score > 0 and TIMING_S.search(s):
                score += 3  # a timing question should surface the sentence that states the timeline
            scored.append((score, s, h["id"]))
    best = [b for b in sorted(scored, key=lambda x: -x[0]) if b[0] > 0][:n]
    if not best:  # the section matched (e.g. on its heading) but no single sentence did
        top = hits[0]
        lead = re.split(r"(?<=[.!?])\s+", top["body"])[:n]
        return " ".join(f"{s} [{top['id']}]" for s in lead)
    return " ".join(f"{s} [{i}]" for _, s, i in best)


def answer(question, retriever, k=3):
    hits = retriever.search(question, k)
    if not hits or max(h["bm25"] for h in hits) < MIN_BM25:
        return {"answer": REFUSAL, "sources": [], "mode": "guardrail"}
    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            import anthropic
            context = "\n\n".join(f"[{h['id']}] {h['sop_title']} — {h['section']}\n{h['body']}" for h in hits)
            msg = anthropic.Anthropic().messages.create(
                model=os.getenv("LLM_MODEL", "claude-sonnet-5-5"),
                max_tokens=500,
                system=("You are a pharmaceutical quality assistant. Answer strictly from the SOP excerpts "
                        "provided and cite every statement as [SOP-ID §section]. If the excerpts do not "
                        "answer the question, say so and recommend consulting Quality Assurance."),
                messages=[{"role": "user", "content": f"SOP excerpts:\n{context}\n\nQuestion: {question}"}],
            )
            return {"answer": msg.content[0].text, "sources": hits, "mode": "LLM (Claude)"}
        except Exception as exc:
            return {"answer": _extractive(question, hits, retriever.chunks), "sources": hits,
                    "mode": f"extractive (LLM unavailable: {type(exc).__name__})"}
    return {"answer": _extractive(question, hits, retriever.chunks), "sources": hits,
            "mode": "extractive (set ANTHROPIC_API_KEY for LLM answers)"}
