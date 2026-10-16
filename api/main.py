import asyncio
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from .db import Base, engine, SessionLocal
from .models import Applicant
from .routers import applications, decisions, analytics
from .security import require_staff
from agents.graph import process_applicant
from ml.synthetic import generate, make_essay

Base.metadata.create_all(engine)
app = FastAPI(title="Admissions Copilot API", version="0.1.0")
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
for r in (applications.router, decisions.router, analytics.router):
    app.include_router(r)
@app.get("/")
def root():
    return {"message": "Admissions Copilot API is running", "docs": "/docs"}
@app.get("/health")
def health():
    return {"ok": True}

@app.post("/dev/seed", dependencies=[Depends(require_staff)])
async def seed(n: int = 100, seed: int = 1):
    """Create n synthetic applicants and run each through the agent graph."""
    df, rng, ids = generate(n, seed), np.random.default_rng(seed), []
    with SessionLocal() as db:
        for i, r in df.iterrows():
            a = Applicant(name=f"Applicant {i}", email=f"applicant{i}@example.com", program="MS_CS",
                          gender=r.gender, region=r.region, essay=make_essay(r.topic, rng),
                          form_profile={k: float(r[k]) for k in ["gpa", "gre", "toefl", "sop", "lor", "research", "univ_rating"]})
            db.add(a); db.flush(); ids.append(a.id)
        db.commit()
    for aid in ids:
        await process_applicant(aid)
    return {"seeded": len(ids)}

@app.websocket("/ws/status/{aid}")
async def ws_status(ws: WebSocket, aid: str):
    """Pushes the applicant's status whenever it changes (poll-based; use Redis pub/sub at scale)."""
    await ws.accept()
    last = None
    try:
        while True:
            with SessionLocal() as db:
                a = db.get(Applicant, aid)
                cur = {"status": a.status, "interview_slot": a.interview_slot} if a else {"status": "not_found"}
            if cur != last:
                await ws.send_json(cur); last = cur
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        pass
