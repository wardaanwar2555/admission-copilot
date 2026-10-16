from typing import Optional
from pydantic import BaseModel, Field

class ApplicationIn(BaseModel):
    name: str
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    program: str = "MS_CS"
    gender: Optional[str] = None
    region: Optional[str] = None
    gpa: Optional[float] = Field(None, ge=0, le=4)
    gre: Optional[float] = Field(None, ge=260, le=340)
    toefl: Optional[float] = Field(None, ge=0, le=120)
    sop: Optional[float] = Field(None, ge=1, le=5)
    lor: Optional[float] = Field(None, ge=1, le=5)
    research: Optional[int] = Field(None, ge=0, le=1)
    univ_rating: Optional[int] = Field(None, ge=1, le=5)
    essay: str = ""

class DecisionIn(BaseModel):
    decision: str = Field(pattern="^(shortlisted|admitted|waitlisted|rejected|hold)$")
    notes: str = ""
    reviewer: str = "reviewer"
