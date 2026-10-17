"""FastAPI simulation serving the versioned traffic-volume model."""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field


MODEL_VERSION = "1.0.0"
MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "traffic_volume_regressor.joblib"
MODEL = joblib.load(MODEL_PATH)
app = FastAPI(title="Traffic Volume Model API", version=MODEL_VERSION)


class TrafficPredictionRequest(BaseModel):
    hour: int = Field(ge=0, le=23)
    day_of_week: int = Field(ge=0, le=6)
    is_weekend: int = Field(ge=0, le=1)
    holiday_flag: int = Field(ge=0, le=1)
    month: int = Field(ge=1, le=12)
    temp: float
    rain_1h: float = Field(ge=0)
    snow_1h: float = Field(ge=0)
    clouds_all: float = Field(ge=0, le=100)
    weather_main: str = Field(min_length=1)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "model_version": MODEL_VERSION}


@app.post("/predict")
def predict(request: TrafficPredictionRequest) -> dict[str, object]:
    features = pd.DataFrame([request.model_dump()])
    predicted_volume = float(MODEL.predict(features)[0])
    return {"model_version": MODEL_VERSION, "predicted_traffic_volume": predicted_volume}