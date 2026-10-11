from langgraph.graph import StateGraph, END
from .state import RCAState
from .agents import orchestrator, planner, traversal, response, should_continue


def build_graph():
    g = StateGraph(RCAState)
    g.add_node("orchestrator", orchestrator)
    g.add_node("planner", planner)
    g.add_node("traversal", traversal)
    g.add_node("response", response)
    g.set_entry_point("orchestrator")
    g.add_edge("orchestrator", "planner")
    g.add_conditional_edges("planner", should_continue, {"traversal": "traversal", "response": "response"})
    g.add_edge("traversal", "response")
    g.add_edge("response", END)
    return g.compile()
