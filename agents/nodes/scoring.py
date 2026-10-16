from ml import serving
from .. import tools

W_ML, W_ESSAY, W_FIT = 0.5, 0.3, 0.2

async def run(state):
    p, aid = state["parsed_profile"], state["applicant_id"]
    prob = serving.predict_admission(p)
    essay_q = serving.score_essay(p.get("essay", ""))
    fit = serving.program_fit(p["program"], p.get("essay", ""))
    expl = serving.explain(p)
    final = round(W_ML * prob + W_ESSAY * essay_q + W_FIT * fit, 4)
    state.update(admit_prob=prob, essay_quality=essay_q, program_fit=fit, ml_score=final, shap_explanation=expl)
    tools.update_status(aid, "under_review", admit_prob=prob, essay_quality=essay_q, program_fit=fit,
                        final_score=final, explanation=expl, summary=serving.summarize(p, p.get("essay", "")))
    tools.log_audit(aid, "scoring_agent", "scored",
                    {"final": final, "admit_prob": prob, "essay": essay_q, "fit": fit,
                     "formula": f"{W_ML}*ml+{W_ESSAY}*essay+{W_FIT}*fit", "top_features": expl})
    return state
