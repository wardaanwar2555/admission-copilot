from ..nlp import parse_pdf, extract_entities
from .. import tools

async def run(state):
    a = tools.load_applicant(state["applicant_id"])
    text = "\n".join(parse_pdf(p) for p in a["documents"])
    extracted = extract_entities(text) if text else {}
    profile = {**extracted, **{k: v for k, v in a["form_profile"].items() if v is not None}}  # form data wins
    profile["essay"] = a["essay"]
    profile["program"] = a["program"]
    state["parsed_profile"] = profile
    state["raw_documents"] = a["documents"]
    tools.update_status(a["id"], "under_review", parsed_profile={k: v for k, v in profile.items() if k != "essay"})
    tools.log_audit(a["id"], "intake_agent", "parsed", {"fields": sorted(profile), "from_documents": sorted(extracted)})
    state["status"] = "under_review"
    return state
