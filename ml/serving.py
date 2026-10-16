"""Model-serving helpers used by the Scoring Agent (in-process; wrap in FastAPI routes to
run as a separate microservice). SHAP values come from XGBoost's native exact TreeSHAP."""
from pathlib import Path
import re
import numpy as np
import xgboost as xgb
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .synthetic import FEATURES, generate
from .train_admit import train, ART

DEFAULTS = {"gpa": 3.0, "gre": 310, "toefl": 95, "sop": 3.0, "lor": 3.0, "research": 0, "univ_rating": 3}
_model = None

def _load() -> xgb.XGBClassifier:
    global _model
    if _model is None:
        if not (ART / "admit.json").exists():
            train(generate())
        _model = xgb.XGBClassifier()
        _model.load_model(str(ART / "admit.json"))
    return _model

def _row(profile: dict) -> np.ndarray:
    return np.array([[float(profile.get(f) if profile.get(f) is not None else DEFAULTS[f]) for f in FEATURES]])

def predict_admission(profile: dict) -> float:
    return float(_load().predict_proba(_row(profile))[0, 1])

def explain(profile: dict, k: int = 5) -> list[dict]:
    """Top-k feature contributions (log-odds) for this applicant."""
    model = _load()
    contribs = model.get_booster().predict(xgb.DMatrix(_row(profile), feature_names=FEATURES), pred_contribs=True)[0]
    items = [{"feature": f, "value": float(_row(profile)[0][i]), "impact": float(contribs[i])}
             for i, f in enumerate(FEATURES)]
    return sorted(items, key=lambda d: abs(d["impact"]), reverse=True)[:k]

def score_essay(text: str) -> float:
    """0-1 quality. Heuristic baseline (length, lexical variety, sentence structure).
    Swap for the fine-tuned DeBERTa regressor in production (same signature)."""
    words = re.findall(r"[A-Za-z']+", text)
    if len(words) < 20:
        return 0.1
    sents = [s for s in re.split(r"[.!?]+", text) if s.strip()]
    length = min(len(words) / 350, 1.0)
    variety = min(len({w.lower() for w in words}) / len(words) / 0.7, 1.0)
    avg_len = len(words) / max(len(sents), 1)
    structure = 1.0 - min(abs(avg_len - 20) / 20, 1.0)
    return round(0.4 * length + 0.35 * variety + 0.25 * structure, 3)

PROGRAMS = {
    "MS_CS": "machine learning data systems software engineering research algorithms cloud security nlp vision robotics",
    "MS_DS": "data science statistics machine learning analytics visualization big data modeling",
    "MBA": "leadership management strategy finance entrepreneurship operations marketing startup",
}

def program_fit(program: str, essay: str) -> float:
    desc = PROGRAMS.get(program, PROGRAMS["MS_CS"])
    if not essay.strip():
        return 0.3
    vec = TfidfVectorizer(stop_words="english").fit([desc, essay])
    sim = cosine_similarity(vec.transform([desc]), vec.transform([essay]))[0, 0]
    return float(min(1.0, 0.3 + 3 * sim))   # rescale into a usable 0.3-1.0 range

def summarize(profile: dict, essay: str) -> str:
    first = re.split(r"(?<=[.!?])\s+", essay.strip())[0] if essay.strip() else "No essay provided."
    return (f"GPA {profile.get('gpa')} | GRE {profile.get('gre')} | TOEFL {profile.get('toefl')} | "
            f"Research: {'yes' if profile.get('research') else 'no'}. Essay opens: {first[:160]}")
