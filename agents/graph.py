from langgraph.graph import StateGraph, END
from .state import AdmissionState
from .nodes import intake, screening, scoring, audit, scheduler, communication

def build_graph():
    g = StateGraph(AdmissionState)
    for name, mod in [("intake", intake), ("screening", screening), ("scoring", scoring),
                      ("audit", audit), ("scheduler", scheduler), ("communication", communication)]:
        g.add_node(name, mod.run)
    g.set_entry_point("intake")
    g.add_edge("intake", "screening")
    g.add_conditional_edges("screening", lambda s: s["eligibility"]["route"],
                            {"auto_reject": "communication", "auto_pass": "scoring", "needs_review": "scoring"})
    g.add_edge("scoring", "audit")
    g.add_conditional_edges("audit", lambda s: "shortlist" if s["recommendation"] == "shortlist" else "hold",
                            {"shortlist": "scheduler", "hold": "communication"})
    g.add_edge("scheduler", "communication")
    g.add_edge("communication", END)
    return g.compile()

_graph = None
async def process_applicant(applicant_id: str) -> dict:
    global _graph
    _graph = _graph or build_graph()
    return await _graph.ainvoke({"applicant_id": applicant_id, "audit_log": []})
