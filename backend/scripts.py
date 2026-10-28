import os
import time 
from datetime import date, datetime, timedelta

import pandas as pd
import requests 

BASE = "https://data.elexon.co.uk/bmrs/api/v1"

session = requests.Session()


def get_json(path, params, retries=3):
    params = {**params, "format": "json"}
    for attempt in range(retries):
        r = session.get(f"{BASE}{path}", params=params, timeout=60)
        if r.status_code == 429:  # rate limited
            time.sleep(2 ** attempt)
            continue
        r.raise_for_status()
        return r.json()
    raise RuntimeError(f"Failed after {retries} tries: {path} {params}")


def daterange_chunks(start: date, end: date, days: int):
    cur = start
    while cur <= end:
        nxt = min(cur + timedelta(days=days - 1), end)
        yield cur, nxt
        cur = nxt + timedelta(days=1)


def fetch_actuals(start: date, end: date) -> pd.DataFrame:
    rows = []
    for a, b in daterange_chunks(start, end, 7):
        data = get_json(
            "/datasets/FUELHH/stream",
            {
                "settlementDateFrom": a.isoformat(),
                "settlementDateTo": b.isoformat(),
                "fuelType": "WIND",
            },
        )
        rows.extend(data)
    df = pd.DataFrame(rows)
    df["startTime"] = pd.to_datetime(df["startTime"], utc=True)
    return df[["startTime", "generation"]].drop_duplicates("startTime")


def fetch_forecasts(pub_from: datetime, pub_to: datetime) -> pd.DataFrame:
    rows = []
    cur = pub_from
    while cur < pub_to:
        nxt = min(cur + timedelta(days=3), pub_to)
        data = get_json(
            "/datasets/WINDFOR/stream",
            {
                "publishDateTimeFrom": cur.strftime("%Y-%m-%dT%H:%MZ"),
                "publishDateTimeTo": nxt.strftime("%Y-%m-%dT%H:%MZ"),
            },
        )
        rows.extend(data)
        cur = nxt
    df = pd.DataFrame(rows)
    for c in ("startTime", "publishTime"):
        df[c] = pd.to_datetime(df[c], utc=True)
    return df[["startTime", "publishTime", "generation"]].drop_duplicates()


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    fetch_actuals(date(2026, 1, 1), date(2026, 10, 31)).to_parquet("data/actuals.parquet")
    fetch_forecasts(
        datetime(2025, 12, 25),
        datetime(2026, 10, 30),
    ).to_parquet("data/forecasts.parquet")

