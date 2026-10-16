from .. import tools

async def run(state):
    slot = tools.schedule_interview(state["applicant_id"])
    state["interview_slot"] = slot
    state["status"] = "shortlisted"
    tools.update_status(state["applicant_id"], "shortlisted", interview_slot=slot)
    tools.log_audit(state["applicant_id"], "scheduler_agent", "slot_proposed", {"slot": slot})
    return state
