"""Tool layer: every tool audits itself. Swap bodies for real integrations (Resend,
Google Calendar) without touching the agents."""
import json
from datetime import datetime, timedelta, timezone
import httpx
from api.config import settings
from api.db import SessionLocal
from api.models import Applicant, AuditLog, EmailLog

def log_audit(applicant_id: str, actor: str, step: str, payload: dict) -> None:
    with SessionLocal() as db:
        db.add(AuditLog(applicant_id=applicant_id, actor=actor, step=step, payload=json.loads(json.dumps(payload, default=str))))
        db.commit()

def update_status(applicant_id: str, status: str, **fields) -> None:
    with SessionLocal() as db:
        a = db.get(Applicant, applicant_id)
        a.status = status
        for k, v in fields.items():
            setattr(a, k, v)
        db.commit()

def load_applicant(applicant_id: str) -> dict:
    with SessionLocal() as db:
        a = db.get(Applicant, applicant_id)
        return {c.name: getattr(a, c.name) for c in Applicant.__table__.columns}

def send_email(applicant_id: str, to: str, subject: str, body: str) -> bool:
    with SessionLocal() as db:
        db.add(EmailLog(applicant_id=applicant_id, to=to, subject=subject, body=body))
        db.commit()
    if not settings.resend_api_key:
        print(f"[email:console] to={to} | {subject}")
        return True
    r = httpx.post("https://api.resend.com/emails", timeout=10,
                   headers={"Authorization": f"Bearer {settings.resend_api_key}"},
                   json={"from": settings.email_from, "to": [to], "subject": subject, "text": body})
    return r.status_code < 300

def schedule_interview(applicant_id: str) -> str:
    """Stub: next free weekday 10:00 UTC. Replace with Google Calendar freebusy + events.insert."""
    d = datetime.now(timezone.utc).replace(hour=10, minute=0, second=0, microsecond=0) + timedelta(days=7)
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d.isoformat()

def llm_polish(text: str) -> str:
    """Optional: rewrite a template email in a warmer tone with an LLM. No-op without a key."""
    if not settings.openai_api_key:
        return text
    try:
        r = httpx.post("https://api.openai.com/v1/chat/completions", timeout=20,
                       headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                       json={"model": "gpt-4o-mini", "messages": [
                           {"role": "system", "content": "Polish this admissions email. Keep every fact, date and link unchanged. Do not add promises."},
                           {"role": "user", "content": text}]})
        return r.json()["choices"][0]["message"]["content"]
    except Exception:
        return text
