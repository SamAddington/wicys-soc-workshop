from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any
import os
import math

app = FastAPI(title="WiCyS SOC Detector", version="0.1.0")

USE_ML = os.getenv("USE_ML", "0") == "1"
ML_COEFFS = {
    "intercept": -2.0,
    "contains_link": 1.0,
    "contains_password": 1.5,
    "contains_urgent": 0.8,
    "contains_reward": 0.7,
}


class DetectorInput(BaseModel):
    anon_record: Dict[str, Any]
    features: Dict[str, Any]


def ml_risk_score(features: Dict[str, Any]) -> float:
    z = ML_COEFFS["intercept"]
    for name, weight in ML_COEFFS.items():
        if name == "intercept":
            continue
        val = 1.0 if features.get(name) else 0.0
        z += weight * val
    return 1.0 / (1.0 + math.exp(-z))


def score(features: Dict[str, Any]) -> Dict[str, Any]:
    risk = 0.0
    reasons = []

    if features.get("contains_link"):
        risk += 0.3
        reasons.append("Message contains a clickable link.")

    if features.get("contains_password"):
        risk += 0.4
        reasons.append("Mentions passwords or passphrases.")

    if features.get("contains_urgent"):
        risk += 0.2
        reasons.append("Uses urgent language (e.g., 'urgent', 'immediately').")

    if features.get("contains_reward"):
        risk += 0.2
        reasons.append("Offers rewards such as gift cards or bonuses.")

    if features.get("len_message", 0) > 400:
        risk += 0.1
        reasons.append("Unusually long message for this source.")

    risk = max(0.0, min(1.0, risk))

    if USE_ML:
        try:
            ml_risk = ml_risk_score(features)
            if ml_risk > risk:
                reasons.append("ML safety model suggested higher risk based on feature pattern.")
                risk = ml_risk
        except Exception:
            pass

    if risk >= 0.7:
        label = "high_risk"
        action = "escalate"
    elif risk >= 0.4:
        label = "medium_risk"
        action = "queue_for_review"
    else:
        label = "low_risk"
        action = "allow"

    explanation = " / ".join(reasons) if reasons else "No obvious phishing indicators detected."

    return {
        "risk_score": float(risk),
        "label": label,
        "action": action,
        "explanation": explanation,
    }


@app.post("/score")
def score_endpoint(payload: DetectorInput):
    return score(payload.features)


@app.get("/health")
def health():
    return {"status": "up"}
