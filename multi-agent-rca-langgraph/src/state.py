from typing import TypedDict, List, Dict, Any


class RCAState(TypedDict, total=False):
    """Shared, structured state passed between all agents."""
    query: str
    intent: str
    site_id: str
    plan: List[str]
    evidence: List[Dict[str, Any]]
    iterations: int
    answer: str
