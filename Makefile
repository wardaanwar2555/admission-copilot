install:  ; pip install -r requirements.txt && cd web && npm install
train:    ; python -m ml.train_admit
api:      ; uvicorn api.main:app --reload --port 8000
web:      ; cd web && npm run dev
test:     ; pytest -q tests
seed:     ; curl -X POST "localhost:8000/dev/seed?n=300" -H "X-API-Key: change-me-staff-key"
