"""Four agents: Orchestrator, Planner, Traversal and Response.

The agents are deterministic so the demo runs without an API key. Each node can be
swapped for an LLM call without changing the graph or the state contract.
"""
import re
from .state import RCAState
from . import tools

MAX_ITERATIONS = 5


def orchestrator(state: RCAState) -> RCAState:
    q = state["query"]
    match = re.search(r"SITE-\d+", q.upper())
    intent = "root_cause" if any(k in q.lower() for k in ["why", "cause", "down", "delay"]) else "status"
    return {"intent": intent, "site_id": match.group(0) if match else "", "iterations": 0, "evidence": []}


def planner(state: RCAState) -> RCAState:
    if not state.get("site_id"):
        return {"plan": []}
    if state["site_id"] not in tools.DATA["sites"]:
        return {"plan": [], "answer": f"{state['site_id']} was not found in the network inventory."}
    plan =["site"] + (["activities", "materials", "vendors"] if state["intent"] == "root_cause" else [])
    return {"plan": plan}


def traversal(state: RCAState) -> RCAState:
    evidence = list(state.get("evidence", []))
    site = tools.get_site(state["site_id"])
    evidence.append({"type": "site", **site})
    if "activities" in state["plan"]:
        for act_id in site["activities"]:
            act = tools.get_activity(act_id)
            evidence.append({"type": "activity", **act})
            mat = tools.get_material(act["material"])
            evidence.append({"type": "material", **mat})
            evidence.append({"type": "vendor", **tools.get_vendor(mat["vendor"])})
    return {"evidence": evidence, "iterations": state.get("iterations", 0) + 1}


def response(state: RCAState) -> RCAState:
    if not state.get("evidence"):
        return {"answer": state.get("answer") or "Please specify a site ID (for example SITE-101)."}
    ev =state["evidence"]
    site = next(e for e in ev if e["type"] == "site")
    if state["intent"] == "status":
        return {"answer": f"{site['site_id']} is currently {site['status']}."}
    issues = []
    for e in ev:
        if e["type"] == "activity" and e["status"] in ("DELAYED", "IN_PROGRESS"):
            mat = next(m for m in ev if m["type"] == "material" and m["material_id"] == e["material"])
            ven = next(v for v in ev if v["type"] == "vendor" and v["vendor_id"] == mat["vendor"])
            if mat["delivery"] != "ON_TIME":
                issues.append(f"'{e['name']}' is {e['status']} because '{mat['name']}' from "
                              f"{ven['name']} is {mat['delivery'].replace('_', ' ').lower()} "
                              f"({ven['open_escalations']} open escalations)")
    if not issues:
        return {"answer": f"{site['site_id']} is {site['status']}; no material or vendor issue found."}
    return {"answer": f"{site['site_id']} is {site['status']}. Root cause: " + "; ".join(issues) + "."}


def should_continue(state: RCAState) -> str:
    if not state.get("plan"):
        return "response"
    if state.get("iterations", 0) >= MAX_ITERATIONS:
        return "response"
    return "traversal"
