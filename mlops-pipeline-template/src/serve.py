import json
from pathlib import Path
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

ARTIFACTS = Path("artifacts")
app = FastAPI(title="Model Serving API", version="1.0.0")
model = joblib.load(ARTIFACTS / "model.joblib")
meta = json.loads((ARTIFACTS / "metadata.json").read_text())


class PredictRequest(BaseModel):
    features: dict[str, float]


@app.get("/health")
def health():
    return {"status": "ok", "metrics": meta["metrics"]}


@app.post("/predict")
def predict(req: PredictRequest):
    missing = set(meta["features"]) - set(req.features)
    if missing:
        raise HTTPException(422, f"Missing features: {sorted(missing)[:5]}")
    row = pd.DataFrame([req.features])[meta["features"]]
    return {"prediction": int(model.predict(row)[0]),
            "probability": round(float(model.predict_proba(row)[0, 1]), 4)}
