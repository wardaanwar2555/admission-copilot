import pandas as pd
from api.config import settings
from api.db import SessionLocal
from api.models import Applicant
from ml.fairness import audit as fairness_audit
from .. import tools

def population_bias(threshold: float | None = None) -> list[dict]:
    """Audit current shortlist-vs-rest rates across sensitive attributes."""
    with SessionLocal() as db:
        rows = db.query(Applicant).filter(Applicant.final_score.isnot(None)).all()
    if len(rows) < 60:
        return []
    df = pd.DataFrame([{"gender": r.gender, "region": r.region,
                        "selected": int(r.final_score >= settings.shortlist_threshold)} for r in rows])
    return [fairness_audit(df, col, ratio_threshold=threshold or settings.bias_ratio_threshold)
            for col in ("gender", "region")]

async def run(state):
    flags = [f"{r['attribute']}: disparity {r['disparity_ratio']} > {settings.bias_ratio_threshold}"
             for r in population_bias() if r["status"] == "flagged"]
    state["bias_flags"] = flags
    rec = "shortlist" if state["ml_score"] >= settings.shortlist_threshold else "hold"
    if state["eligibility"]["route"] == "auto_reject":
        rec = "reject"
    state["recommendation"] = rec
    tools.update_status(state["applicant_id"], state["status"], bias_flags=flags)
    tools.log_audit(state["applicant_id"], "audit_agent", "audited",
                    {"recommendation": rec, "bias_flags": flags, "threshold": settings.shortlist_threshold})
    return state
