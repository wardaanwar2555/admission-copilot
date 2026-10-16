import pandas as pd
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Applicant
from ..security import require_staff
from ..config import settings
from ml.fairness import audit

router = APIRouter(prefix="/analytics", tags=["analytics"], dependencies=[Depends(require_staff)])
ORDER = ["submitted", "under_review", "shortlisted", "admitted", "waitlisted", "rejected"]

@router.get("/funnel")
def funnel(db: Session = Depends(get_db)):
    rows = db.query(Applicant.status).all()
    s = pd.Series([r[0] for r in rows], dtype="object").value_counts().to_dict()
    scored = db.query(Applicant).filter(Applicant.final_score.isnot(None)).count()
    return {"total": len(rows), "scored": scored, "by_status": {k: int(s.get(k, 0)) for k in ORDER}}

@router.get("/bias")
def bias(db: Session = Depends(get_db)):
    rows = db.query(Applicant).filter(Applicant.final_score.isnot(None)).all()
    if not rows:
        return {"results": [], "threshold": settings.bias_ratio_threshold}
    df = pd.DataFrame([{"gender": r.gender, "region": r.region,
                        "selected": int(r.final_score >= settings.shortlist_threshold)} for r in rows])
    return {"threshold": settings.bias_ratio_threshold,
            "results": [audit(df, c, ratio_threshold=settings.bias_ratio_threshold) for c in ("gender", "region")]}
