from typing import TypedDict, Optional

class AdmissionState(TypedDict, total=False):
    applicant_id: str
    raw_documents: list[str]
    parsed_profile: dict
    missing: list[str]
    eligibility: dict            # {"route": auto_reject|auto_pass|needs_review, "rules_triggered": [...]}
    admit_prob: float
    essay_quality: float
    program_fit: float
    ml_score: float              # final priority score
    shap_explanation: list[dict]
    bias_flags: list[str]
    recommendation: str          # shortlist | hold | reject
    interview_slot: Optional[str]
    status: str
    audit_log: list[dict]
