from pathlib import Path
from typing import Any

import joblib
import numpy as np
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from prometheus_fastapi_instrumentator import Instrumentator


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model.pkl"


class HouseInput(BaseModel):
    # The model expects the same feature names as the California housing dataset.
    MedInc: float = Field(..., ge=0, description="Median income")
    HouseAge: float = Field(..., ge=0, description="Median house age")
    AveRooms: float = Field(..., ge=0, description="Average rooms")
    AveBedrms: float = Field(..., ge=0, description="Average bedrooms")
    Population: float = Field(..., ge=0, description="Population")
    AveOccup: float = Field(..., ge=0, description="Average occupancy")
    Latitude: float = Field(..., ge=-90, le=90, description="Latitude")
    Longitude: float = Field(..., ge=-180, le=180, description="Longitude")


app = FastAPI(title="House Price Prediction API", version="1.0.0")

# Serve the simple HTML form and any static assets from the same app.
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


def load_model() -> Any:
    if not MODEL_PATH.exists():
        raise RuntimeError(
            "model.pkl was not found. Run app/train.py before starting the API."
        )
    return joblib.load(MODEL_PATH)


model = load_model()

# Expose Prometheus metrics on /metrics so Prometheus can scrape the app.
Instrumentator().instrument(app).expose(app)


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/predict")
def predict(payload: HouseInput) -> dict[str, int]:
    features = np.array(
        [[
            payload.MedInc,
            payload.HouseAge,
            payload.AveRooms,
            payload.AveBedrms,
            payload.Population,
            payload.AveOccup,
            payload.Latitude,
            payload.Longitude,
        ]]
    )

    prediction_in_hundreds_of_thousands = model.predict(features)[0]
    prediction_in_dollars = int(round(prediction_in_hundreds_of_thousands * 100000))

    return {"prediction": prediction_in_dollars}
