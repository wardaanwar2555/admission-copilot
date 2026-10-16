import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Applicant, AuditLog
from ..schemas import ApplicationIn
from ..security import require_staff
from ..config import settings
from agents.graph import process_applicant

router = APIRouter(prefix="/applications", tags=["applications"])
PROFILE_KEYS = ["gpa", "gre", "toefl", "sop", "lor", "research", "univ_rating"]

def public_view(a: Applicant) -> dict:
    return {"id": a.id, "status": a.status, "program": a.program, "interview_slot": a.interview_slot,
            "decision": a.decision if a.status in ("admitted", "waitlisted", "rejected") else None}

def staff_view(a: Applicant) -> dict:
    d = public_view(a)
    d.update(name=a.name, email=a.email, route=a.route, admit_prob=a.admit_prob, essay_quality=a.essay_quality,
             program_fit=a.program_fit, final_score=a.final_score, explanation=a.explanation,
             bias_flags=a.bias_flags, summary=a.summary, profile=a.parsed_profile or a.form_profile,
             decision=a.decision, decision_notes=a.decision_notes, decided_by=a.decided_by, essay=a.essay)
    return d

@router.post("", status_code=201)
def create(body: ApplicationIn, db: Session = Depends(get_db)):
    data = body.model_dump()
    a = Applicant(name=data["name"], email=data["email"], program=data["program"], gender=data["gender"],
                  region=data["region"], essay=data["essay"], form_profile={k: data[k] for k in PROFILE_KEYS})
    db.add(a); db.commit()
    return {"id": a.id}

@router.post("/{aid}/documents")
async def upload(aid: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    a = db.get(Applicant, aid)
    if not a: raise HTTPException(404)
    if not (file.filename or "").lower().endswith((".pdf", ".txt", ".docx")):
        raise HTTPException(400, "Only PDF, TXT or DOCX files are accepted")
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    dest = Path(settings.upload_dir) / f"{aid}_{uuid.uuid4().hex[:6]}_{Path(file.filename).name}"
    dest.write_bytes(await file.read())          # production: S3 pre-signed upload + virus scan
    a.documents = [*a.documents, str(dest)]; db.commit()
    return {"stored": dest.name}

@router.post("/{aid}/process")
async def process(aid: str, db: Session = Depends(get_db)):
    if not db.get(Applicant, aid): raise HTTPException(404)
    s = await process_applicant(aid)
    return {"status": s["status"], "route": s["eligibility"]["route"], "score": s.get("ml_score"),
            "recommendation": s.get("recommendation")}

@router.get("/{aid}/status")
def status(aid: str, db: Session = Depends(get_db)):
    a = db.get(Applicant, aid)
    if not a: raise HTTPException(404)
    return public_view(a)

@router.get("", dependencies=[Depends(require_staff)])
def queue(db: Session = Depends(get_db), program: str | None = None, status: str | None = None,
          min_score: float | None = None, limit: int = Query(100, le=1000)):
    q = db.query(Applicant)
    if program: q = q.filter(Applicant.program == program)
    if status: q = q.filter(Applicant.status == status)
    if min_score is not None: q = q.filter(Applicant.final_score >= min_score)
    rows = q.order_by(Applicant.final_score.desc().nullslast()).limit(limit).all()
    return [staff_view(a) | {"essay": None} for a in rows]

@router.get("/{aid}", dependencies=[Depends(require_staff)])
def detail(aid: str, db: Session = Depends(get_db)):
    a = db.get(Applicant, aid)
    if not a: raise HTTPException(404)
    return staff_view(a)

@router.get("/{aid}/audit", dependencies=[Depends(require_staff)])
def audit_trail(aid: str, db: Session = Depends(get_db)):
    rows = db.query(AuditLog).filter(AuditLog.applicant_id == aid).order_by(AuditLog.id).all()
    return [{"ts": r.ts, "actor": r.actor, "step": r.step, "payload": r.payload} for r in rows]
