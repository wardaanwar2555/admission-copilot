import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, JSON, DateTime, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

def _now():
    return datetime.now(timezone.utc)

class Applicant(Base):
    __tablename__ = "applicants"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: uuid.uuid4().hex[:12])
    name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String)
    program: Mapped[str] = mapped_column(String, default="MS_CS")
    # Sensitive attributes: stored ONLY for bias auditing, never fed to the models
    gender: Mapped[str | None] = mapped_column(String, nullable=True)
    region: Mapped[str | None] = mapped_column(String, nullable=True)
    form_profile: Mapped[dict] = mapped_column(JSON, default=dict)
    essay: Mapped[str] = mapped_column(Text, default="")
    documents: Mapped[list] = mapped_column(JSON, default=list)
    parsed_profile: Mapped[dict] = mapped_column(JSON, default=dict)
    # submitted | under_review | shortlisted | interview_scheduled | admitted | waitlisted | rejected
    status: Mapped[str] = mapped_column(String, default="submitted")
    route: Mapped[str | None] = mapped_column(String, nullable=True)
    admit_prob: Mapped[float | None] = mapped_column(Float, nullable=True)
    essay_quality: Mapped[float | None] = mapped_column(Float, nullable=True)
    program_fit: Mapped[float | None] = mapped_column(Float, nullable=True)
    final_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    explanation: Mapped[list] = mapped_column(JSON, default=list)
    bias_flags: Mapped[list] = mapped_column(JSON, default=list)
    summary: Mapped[str] = mapped_column(Text, default="")
    interview_slot: Mapped[str | None] = mapped_column(String, nullable=True)
    decision: Mapped[str | None] = mapped_column(String, nullable=True)
    decision_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    decided_by: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

class AuditLog(Base):
    __tablename__ = "audit_log"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    applicant_id: Mapped[str] = mapped_column(String, index=True)
    actor: Mapped[str] = mapped_column(String)          # agent name or reviewer id
    step: Mapped[str] = mapped_column(String)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

class EmailLog(Base):
    __tablename__ = "email_log"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    applicant_id: Mapped[str] = mapped_column(String, index=True)
    to: Mapped[str] = mapped_column(String)
    subject: Mapped[str] = mapped_column(String)
    body: Mapped[str] = mapped_column(Text)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
