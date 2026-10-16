import json
from datetime import date
from pathlib import Path
from api.config import settings
from .. import tools

RULES_DIR = Path(__file__).parent.parent / "rules"

async def run(state):
    p = state["parsed_profile"]
    rules = json.loads((RULES_DIR / f"{p['program']}.json").read_text())
    triggered, route = [], "auto_pass"

    missing = [f for f in rules["required_fields"] if p.get(f) is None]
    state["missing"] = missing
    if missing:
        triggered.append(f"missing_fields:{','.join(missing)}"); route = "needs_review"
    gpa = p.get("gpa")
    if gpa is not None and gpa < rules["min_gpa"]:
        triggered.append(f"gpa<{rules['min_gpa']}"); route = "needs_review"
    if gpa is not None and gpa < rules["reject_below_gpa"]:
        triggered.append(f"gpa<{rules['reject_below_gpa']}")
        if settings.auto_reject_enabled:
            route = "auto_reject"
        else:
            triggered.append("auto_reject_disabled->human_review")   # human-in-the-loop for rejections
    if date.today() > date.fromisoformat(rules["deadline"]):
        triggered.append("past_deadline"); route = "needs_review"

    state["eligibility"] = {"route": route, "rules_triggered": triggered}
    if route == "auto_reject":
        state["recommendation"] = "reject"
    tools.update_status(state["applicant_id"], "under_review", route=route)
    tools.log_audit(state["applicant_id"], "screening_agent", "screened", state["eligibility"])
    return state
