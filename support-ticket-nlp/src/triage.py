from .classifier import TEAMS
from .ner import extract_entities, priority


def triage(text: str, model) -> dict:
    proba = model.predict_proba([text])[0]
    ranked = sorted(zip(model.classes_, proba), key=lambda x: -x[1])
    category, confidence = ranked[0]
    return {"category": category, "confidence": round(float(confidence), 3),
            "team": TEAMS[category] if confidence >= 0.5 else "Service Desk (manual triage)",
            "priority": priority(text), "entities": extract_entities(text),
            "probabilities": {c: round(float(p), 3) for c, p in ranked}}
