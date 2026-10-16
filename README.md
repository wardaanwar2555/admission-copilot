# Admissions Copilot

Agentic university-admissions platform: intake -> screening -> scoring -> bias audit -> scheduling -> communication,
orchestrated with LangGraph, with a FastAPI backend and a Next.js reviewer/admin UI.

## Quick start (local, no Docker, no API keys)
```bash
cp .env.example .env
pip install -r requirements.txt
python -m ml.train_admit            # trains XGBoost on synthetic data -> ml/artifacts/
pytest -q tests                     # end-to-end test of the agent graph + API
uvicorn api.main:app --reload       # http://localhost:8000/docs
curl -X POST "localhost:8000/dev/seed?n=300" -H "X-API-Key: change-me-staff-key"   # demo data

cd web && cp .env.local.example .env.local && npm install && npm run dev   # http://localhost:3000
```
Pages: `/` apply, `/status/<id>` live status (WebSocket), `/reviewer` ranked queue + SHAP, `/admin` funnel + fairness.

## Docker
`docker compose up --build` starts Postgres + API (port 8000). Run the web app with `npm run dev`.

## How it works
- `agents/graph.py` wires the 6 agents; every agent writes to `audit_log` (view at `GET /applications/{id}/audit`).
- Rejections are NOT automatic by default (`AUTO_REJECT_ENABLED=false`): they go to a human.
- Overriding the model recommendation requires reviewer notes (HTTP 422 otherwise) and is audit-logged.
- Gender/region are stored only for fairness audits; they are never model features.
- `final_score = 0.5*admit_prob + 0.3*essay_quality + 0.2*program_fit`; shortlist at `SHORTLIST_THRESHOLD`.

## Honest status: what is real vs. a stub
| Area | State |
|---|---|
| Agent graph, rules engine, audit log, decisions, fairness audit, API, UI | Working, tested |
| Admit model | XGBoost on synthetic data (AUC ~0.82). Retrain on real data: `python -m ml.train_admit --csv your.csv` (needs columns gpa,gre,toefl,sop,lor,research,univ_rating,admit) |
| Essay scorer | Heuristic baseline in `ml/serving.py::score_essay`. Fine-tune DeBERTa and keep the same signature |
| NER | Regex in `agents/nlp.py`. Swap in a custom spaCy model; add Tesseract OCR for scanned PDFs |
| Email | Console log; set `RESEND_API_KEY` for real sends. `OPENAI_API_KEY` enables optional tone polish |
| Calendar | `tools.schedule_interview` is a stub; implement Google Calendar freebusy + events.insert |
| Auth | Shared `X-API-Key`. Replace with Clerk/NextAuth JWT + roles before any real use. The staff key in the web `.env.local` is demo-only |
| Not built | S3 uploads, Redis/Celery, Pinecone plagiarism check, Metabase, Terraform, chat assistant |

Metrics in the blueprint (AUC 0.87, bias 0.31 -> 0.14, 45 -> 6 min) are targets; measure your own before citing them.
Admissions decisions are high-stakes: get legal/compliance review (FERPA/GDPR, local AI-in-hiring/education rules) before real use.

## Next steps (suggested order)
1. Real data + retrain; add calibration plot. 2. Real auth/RBAC. 3. S3 + Celery for async processing.
4. Fine-tune essay model. 5. Google Calendar. 6. Load test (Locust) and OWASP review.
