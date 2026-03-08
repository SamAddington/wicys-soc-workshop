from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict, Any
import hashlib
import os
import requests
import json
from datetime import datetime

DETECTOR_URL = os.getenv("DETECTOR_URL", "http://detector:8000/score")

app = FastAPI(title="WiCyS SOC Collector", version="0.1.0")


class LogEvent(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    source: str
    message: str
    event_type: Optional[str] = None
    language: Optional[str] = None
    timestamp: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None


def hash_identifier(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def extract_features(event: LogEvent) -> Dict[str, Any]:
    msg = event.message.lower()
    return {
        "source": event.source,
        "event_type": event.event_type or "unknown",
        "lang": event.language or "unknown",
        "len_message": len(event.message),
        "contains_link": "http" in msg or "https" in msg,
        "contains_password": "password" in msg or "passphrase" in msg,
        "contains_urgent": any(x in msg for x in ["urgent", "immediately", "now"]),
        "contains_reward": any(x in msg for x in ["gift card", "bonus", "reward"]),
    }


@app.post("/ingest")
def ingest(event: LogEvent):
    anon_user = hash_identifier(event.user_id or event.email)
    domain = None
    if event.email and "@" in event.email:
        domain = event.email.split("@", 1)[1]

    anon_record = {
        "anon_user": anon_user,
        "domain": domain,
        "source": event.source,
        "event_type": event.event_type,
        "language": event.language,
        "timestamp": event.timestamp or datetime.utcnow().isoformat(),
        "message": event.message,
    }

    features = extract_features(event)

    try:
        resp = requests.post(
            DETECTOR_URL,
            json={"anon_record": anon_record, "features": features},
            timeout=3,
        )
        resp.raise_for_status()
        detector_result = resp.json()
    except Exception as e:
        detector_result = {
            "risk_score": 0.0,
            "label": "error",
            "action": "queue_for_review",
            "explanation": f"Detector unavailable: {e}",
        }

    log_line = {
        "anon_record": anon_record,
        "features": features,
        "detector_result": detector_result,
    }
    log_path = "/app/data/ingested_events.jsonl"
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_line) + "\n")
    except Exception:
        pass

    return {
        "status": "ok",
        "detector_result": detector_result,
        "human_triage_hint": detector_result.get("explanation"),
    }


@app.get("/health")
def health():
    return {"status": "up"}
