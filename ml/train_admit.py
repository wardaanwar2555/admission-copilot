"""Train the admission predictor.  Usage: python -m ml.train_admit [--csv path/to/kaggle.csv]
If a Kaggle 'Graduate Admissions' CSV is given, map its columns to FEATURES + 'admit' first."""
import argparse, json
from pathlib import Path
import pandas as pd
import xgboost as xgb
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from .synthetic import generate, FEATURES

ART = Path(__file__).parent / "artifacts"

def train(df: pd.DataFrame) -> dict:
    ART.mkdir(exist_ok=True)
    X, y = df[FEATURES], df["admit"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=7, stratify=y)
    model = xgb.XGBClassifier(n_estimators=250, max_depth=3, learning_rate=0.06,
                              subsample=0.9, colsample_bytree=0.9, eval_metric="auc")
    model.fit(Xtr, ytr)
    auc = float(roc_auc_score(yte, model.predict_proba(Xte)[:, 1]))
    model.save_model(str(ART / "admit.json"))
    (ART / "meta.json").write_text(json.dumps({"auc": auc, "features": FEATURES, "n_train": len(Xtr)}, indent=2))
    return {"auc": auc}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv")
    ap.add_argument("--n", type=int, default=5000)
    a = ap.parse_args()
    data = pd.read_csv(a.csv) if a.csv else generate(a.n)
    print(train(data))
