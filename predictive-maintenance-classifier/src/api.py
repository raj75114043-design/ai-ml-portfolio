"""FastAPI service: scores one machine reading and returns failure probability and risk level."""
import json
import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field
from .features import engineer
from .train import ARTIFACTS, main as train

if not (ARTIFACTS / "model.joblib").exists():
    train()
model = joblib.load(ARTIFACTS / "model.joblib")
meta = json.loads((ARTIFACTS / "metadata.json").read_text())
app = FastAPI(title="Predictive Maintenance API", version="1.0.0")


class Reading(BaseModel):
    air_temp_k: float = Field(..., ge=280, le=320)
    process_temp_k: float = Field(..., ge=290, le=330)
    rotational_speed_rpm: float = Field(..., ge=500, le=3500)
    torque_nm: float = Field(..., ge=0, le=100)
    tool_wear_min: float = Field(..., ge=0, le=300)
    vibration_mm_s: float = Field(..., ge=0, le=20)


def score(reading: dict) -> dict:
    p = float(model.predict_proba(engineer(pd.DataFrame([reading])))[0, 1])
    t = meta["threshold"]
    level = "HIGH" if p >= t else ("MEDIUM" if p >= t / 2 else "LOW")
    return {"failure_probability": round(p, 4), "threshold": t, "maintenance_required": p >= t, "risk": level}


@app.get("/health")
def health():
    return {"status": "ok", "model": meta["model"]}


@app.post("/predict")
def predict(reading: Reading):
    return score(reading.model_dump())
