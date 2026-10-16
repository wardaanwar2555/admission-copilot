from .. import tools

def _compose(name: str, state: dict) -> tuple[str, str]:
    rec = state.get("recommendation")
    if state.get("missing"):
        return ("Action needed: missing information",
                f"Hi {name},\n\nTo complete your application we still need: {', '.join(state['missing'])}.\nPlease upload it in your portal.\n\nAdmissions Office")
    if rec == "shortlist":
        return ("You're invited to interview",
                f"Hi {name},\n\nThank you for applying. We would like to invite you to an interview on {state.get('interview_slot')} (UTC). A video link will follow.\n\nAdmissions Office")
    if rec == "reject":
        return ("Update on your application",
                f"Hi {name},\n\nAfter careful review we are unable to offer you a place this cycle. Thank you for your interest.\n\nAdmissions Office")
    return ("Your application is under review",
            f"Hi {name},\n\nWe have received your application and it is being reviewed by our team. You can follow progress in your portal.\n\nAdmissions Office")

async def run(state):
    a = tools.load_applicant(state["applicant_id"])
    subject, body = _compose(a["name"], state)
    body = tools.llm_polish(body)
    sent = tools.send_email(a["id"], a["email"], subject, body)
    if state.get("recommendation") == "reject":
        state["status"] = "rejected"; tools.update_status(a["id"], "rejected", decision="rejected", decided_by="system")
    tools.log_audit(a["id"], "communication_agent", "email_sent", {"subject": subject, "sent": sent})
    return state
