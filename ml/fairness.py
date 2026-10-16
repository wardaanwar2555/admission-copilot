"""Group-fairness audit using Fairlearn's MetricFrame on selection rates."""
import pandas as pd
from fairlearn.metrics import MetricFrame, selection_rate

def audit(df: pd.DataFrame, sensitive_col: str, outcome_col: str = "selected",
          ratio_threshold: float = 1.2, min_group: int = 30) -> dict:
    """disparity_ratio = highest group selection rate / lowest. 1.0 = parity."""
    d = df.dropna(subset=[sensitive_col])
    counts = d[sensitive_col].value_counts()
    d = d[d[sensitive_col].isin(counts[counts >= min_group].index)]   # ignore tiny groups (noise)
    if d[sensitive_col].nunique() < 2:
        return {"attribute": sensitive_col, "status": "insufficient_data", "rates": {}}
    mf = MetricFrame(metrics=selection_rate, y_true=d[outcome_col], y_pred=d[outcome_col],
                     sensitive_features=d[sensitive_col])
    rates = mf.by_group.to_dict()
    lo, hi = min(rates.values()), max(rates.values())
    ratio = (hi / lo) if lo > 0 else float("inf")
    return {"attribute": sensitive_col, "rates": {k: round(v, 3) for k, v in rates.items()},
            "disparity_ratio": round(ratio, 3) if ratio != float("inf") else None,
            "status": "flagged" if ratio > ratio_threshold else "ok"}
