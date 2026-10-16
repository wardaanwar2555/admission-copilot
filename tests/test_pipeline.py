import os, asyncio
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
from fastapi.testclient import TestClient
from api.main import app
H = {"X-API-Key": "change-me-staff-key"}

def test_end_to_end():
    c = TestClient(app)
    strong = c.post("/applications", json={"name": "Ada", "email": "ada@x.com", "gpa": 3.9, "gre": 335, "toefl": 115,
              "sop": 5, "lor": 5, "research": 1, "univ_rating": 5,
              "essay": "I love machine learning research and building software systems. " * 12}).json()["id"]
    weak = c.post("/applications", json={"name": "Bob", "email": "bob@x.com", "gpa": 2.2, "gre": 290, "toefl": 80,
              "sop": 2, "lor": 2, "research": 0, "univ_rating": 1, "essay": "short"}).json()["id"]
    r1 = c.post(f"/applications/{strong}/process").json()
    r2 = c.post(f"/applications/{weak}/process").json()
    assert r1["recommendation"] == "shortlist" and r1["status"] == "shortlisted"
    assert r2["recommendation"] == "hold" and r2["status"] == "under_review"   # no auto-reject by default
    assert len(c.get(f"/applications/{strong}/audit", headers=H).json()) >= 5
    assert c.get("/applications", headers=H).json()[0]["id"] == strong
    assert c.get("/applications").status_code == 401
    # override w/o notes is rejected
    assert c.post(f"/decisions/{strong}", headers=H, json={"decision": "rejected"}).status_code == 422
    assert c.post(f"/decisions/{strong}", headers=H, json={"decision": "admitted", "reviewer": "r1"}).json()["ok"]

def test_seed_and_bias():
    c = TestClient(app)
    assert c.post("/dev/seed?n=120", headers=H).json()["seeded"] == 120
    res = c.get("/analytics/bias", headers=H).json()["results"]
    assert {r["attribute"] for r in res} == {"gender", "region"}
    assert c.get("/analytics/funnel", headers=H).json()["total"] >= 122
