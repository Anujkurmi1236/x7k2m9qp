from datetime import date, datetime, time, timedelta, timezone
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Wind forecast API")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["GET"], allow_headers=["*"]
)

DATA = Path(__file__).resolve().parent / "data"


@lru_cache
def load():
    act = pd.read_parquet(DATA / "actuals.parquet").rename(columns={"generation": "actual"})
    fc = pd.read_parquet(DATA / "forecasts.parquet").rename(columns={"generation": "forecast"})
    return act, fc


def cutoff_for(delivery: date, cutoff: str) -> pd.Timestamp:
    """Decision time on D-1. Assumes UTC (= UK time in January)."""
    try:
        t = time.fromisoformat(cutoff)
    except ValueError:
        raise HTTPException(400, "cutoff must look like HH:MM")
    d = datetime.combine(delivery - timedelta(days=1), t, tzinfo=timezone.utc)
    return pd.Timestamp(d)


def forecast_at_cutoff(fc: pd.DataFrame, delivery: date, cutoff: str) -> pd.DataFrame:
    """For each half-hour of the delivery day, the latest forecast published at or before the cutoff."""
    start = pd.Timestamp(delivery, tz="UTC")
    end = start + pd.Timedelta(days=1)
    cut = cutoff_for(delivery, cutoff)
    d = fc[(fc.startTime >= start) & (fc.startTime < end) & (fc.publishTime <= cut)]
    d = d.sort_values("publishTime").drop_duplicates("startTime", keep="last")
    return d.sort_values("startTime")


def build_day(delivery: date, cutoff: str) -> pd.DataFrame:
    act, fc = load()
    d = forecast_at_cutoff(fc, delivery, cutoff)
    d = d.merge(act, on="startTime", how="left")
    d["error"] = d["forecast"] - d["actual"]
    d["horizon_h"] = (d["startTime"] - d["publishTime"]).dt.total_seconds() / 3600
    return d


def clean(df: pd.DataFrame):
    return df.replace({np.nan: None}).to_dict("records")


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/forecast")
def forecast(date: date, cutoff: str = "09:00"):
    """Forecast the client had at the cutoff on D-1, next to the actuals."""
    d = build_day(date, cutoff)
    if d.empty:
        raise HTTPException(404, "No forecast available before that cutoff")
    return clean(d[["startTime", "publishTime", "forecast", "actual", "error"]])


@app.get("/api/accuracy")
def accuracy(date_from: date, date_to: date, cutoff: str = "09:00"):
    days = pd.date_range(date_from, date_to).date
    frames = [build_day(d, cutoff) for d in days]
    m = pd.concat(frames).dropna(subset=["actual", "error"])
    if m.empty:
        raise HTTPException(404, "No overlapping data")
    abs_err = m["error"].abs()
    return {
        "count": int(len(m)),
        "mae": float(abs_err.mean()),
        "rmse": float(np.sqrt((m["error"] ** 2).mean())),
        "bias": float(m["error"].mean()),
        "p90_abs_error": float(abs_err.quantile(0.9)),
        "mean_actual": float(m["actual"].mean()),
        "mae_pct_of_mean": float(abs_err.mean() / m["actual"].mean() * 100),
    }