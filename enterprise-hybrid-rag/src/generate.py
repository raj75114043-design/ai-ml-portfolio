"""Grounded answer generation.

Uses Claude when ANTHROPIC_API_KEY is set; otherwise falls back to an extractive answer built
from the retrieved passages, so the application always works offline and never invents content.
"""
import os
import re

STOP = set("a an the is are was were be to of in on for and or with my me i it this that what how do does "
           "can when why where which who our we you your not".split())


def _tokens(text):
    return {t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in STOP}


def extractive_answer(query, docs, n=2):
    q = _tokens(query)
    scored = []
    for d in docs:
        for s in re.split(r"(?<=[.!?])\s+", d["text"]):
            scored.append((len(q & _tokens(s)), s, d["id"]))
    best = [b for b in sorted(scored, key=lambda x: -x[0]) if b[0] > 0][:n]
    if not best:
        return "The knowledge base does not contain an answer to this question."
    return " ".join(f"{s} [{i}]" for _, s, i in best)


def generate_answer(query, docs):
    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            import anthropic
            context = "\n\n".join(f"[{d['id']}] {d.get('title', '')}: {d['text']}" for d in docs)
            msg = anthropic.Anthropic().messages.create(
                model=os.getenv("LLM_MODEL", "claude-sonnet-5-5"),
                max_tokens=400,
                system=("Answer only from the provided context and cite sources as [ID]. "
                        "If the context does not contain the answer, say so."),
                messages=[{"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}],
            )
            return msg.content[0].text, "LLM (Claude)"
        except Exception as exc:  # fall back rather than fail
            return extractive_answer(query, docs), f"extractive (LLM unavailable: {type(exc).__name__})"
    return extractive_answer(query, docs), "extractive (set ANTHROPIC_API_KEY for LLM generation)"
