from fastapi import Header, HTTPException
from .config import settings

def require_staff(x_api_key: str = Header(default="")):
    """Placeholder auth. Replace with Clerk/NextAuth JWT verification + role claims (applicant/reviewer/admin)."""
    if x_api_key != settings.staff_api_key:
        raise HTTPException(401, "Missing or invalid X-API-Key")
