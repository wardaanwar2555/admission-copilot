from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Applicant
from ..schemas import DecisionIn
from ..security import require_staff
from agents import tools

router = APIRouter(prefix="/decisions", tags=["decisions"], dependencies=[Depends(require_staff)])

TEMPLATES = {
    "admitted": ("Congratulations - admission offer", "Hi {n},\n\nWe are delighted to offer you a place in {p}.\n\nAdmissions Office"),
    "waitlisted": ("You have been waitlisted", "Hi {n},\n\nYou are on our waitlist for {p}. We will update you as soon as possible.\n\nAdmissions Office"),
    "rejected": ("Update on your application", "Hi {n},\n\nAfter careful review we are unable to offer you a place for {p} this cycle.\n\nAdmissions Office"),
}

@router.post("/{aid}")
def decide(aid: str, body: DecisionIn, db: Session = Depends(get_db)):
    a = db.get(Applicant, aid)
    if not a: raise HTTPException(404)
    model_rec = "shortlist" if (a.final_score or 0) >= 0.65 else "hold"
    override = (body.decision in ("rejected", "hold") and model_rec == "shortlist") or \
               (body.decision in ("admitted", "shortlisted") and model_rec == "hold")
    if override and not body.notes.strip():
        raise HTTPException(422, "Overriding the model recommendation requires notes")   # audit requirement
    a.status = "under_review" if body.decision == "hold" else body.decision
    a.decision, a.decision_notes, a.decided_by = body.decision, body.notes, body.reviewer
    db.commit()
    tools.log_audit(aid, body.reviewer, "human_decision",
                    {"decision": body.decision, "notes": body.notes, "model_recommendation": model_rec,
                     "model_score": a.final_score, "override": override})
    if body.decision in TEMPLATES:
        s, t = TEMPLATES[body.decision]
        tools.send_email(aid, a.email, s, t.format(n=a.name, p=a.program))
    return {"ok": True, "override": override}
