import unittest
from datetime import date
from unittest.mock import patch

import numpy as np
import pandas as pd
from fastapi import HTTPException

import app


def forecast_frame(rows):
    return pd.DataFrame(rows).assign(
        startTime=lambda df: pd.to_datetime(df["startTime"], utc=True),
        publishTime=lambda df: pd.to_datetime(df["publishTime"], utc=True),
    )


class ForecastSelectionTests(unittest.TestCase):
    def test_cutoff_is_on_the_previous_day_in_utc(self):
        result = app.cutoff_for(date(2026, 1, 8), "09:00")

        self.assertEqual(result, pd.Timestamp("2026-01-07 09:00:00+00:00"))

    def test_invalid_cutoff_raises_bad_request(self):
        with self.assertRaisesRegex(HTTPException, "cutoff must look like HH:MM"):
            app.cutoff_for(date(2026, 1, 8), "not-a-time")

    def test_forecast_at_cutoff_uses_latest_eligible_publication_per_slot(self):
        forecasts = forecast_frame(
            [
                {
                    "startTime": "2026-01-08T00:00:00Z",
                    "publishTime": "2026-01-07T08:00:00Z",
                    "forecast": 10,
                },
                {
                    "startTime": "2026-01-08T00:00:00Z",
                    "publishTime": "2026-01-07T08:30:00Z",
                    "forecast": 20,
                },
                {
                    "startTime": "2026-01-08T00:00:00Z",
                    "publishTime": "2026-01-07T09:30:00Z",
                    "forecast": 30,
                },
                {
                    "startTime": "2026-01-08T00:30:00Z",
                    "publishTime": "2026-01-07T08:00:00Z",
                    "forecast": 40,
                },
                {
                    "startTime": "2026-01-09T00:00:00Z",
                    "publishTime": "2026-01-07T08:00:00Z",
                    "forecast": 50,
                },
            ]
        )

        result = app.forecast_at_cutoff(forecasts, date(2026, 1, 8), "09:00")

        self.assertEqual(result["forecast"].tolist(), [20, 40])
        self.assertEqual(
            result["publishTime"].tolist(),
            [
                pd.Timestamp("2026-01-07 08:30:00+00:00"),
                pd.Timestamp("2026-01-07 08:00:00+00:00"),
            ],
        )


class DayAndEndpointTests(unittest.TestCase):
    def test_build_day_merges_actuals_and_calculates_error_and_horizon(self):
        forecasts = forecast_frame(
            [
                {
                    "startTime": "2026-01-08T00:00:00Z",
                    "publishTime": "2026-01-07T08:00:00Z",
                    "forecast": 120,
                }
            ]
        )
        actuals = pd.DataFrame(
            {
                "startTime": pd.to_datetime(["2026-01-08T00:00:00Z"], utc=True),
                "actual": [100],
            }
        )

        with patch.object(app, "load", return_value=(actuals, forecasts)):
            result = app.build_day(date(2026, 1, 8), "09:00")

        self.assertEqual(result.loc[0, "error"], 20)
        self.assertEqual(result.loc[0, "horizon_h"], 16)

    def test_clean_converts_nan_values_to_none(self):
        result = app.clean(pd.DataFrame({"value": [1, np.nan]}))

        self.assertEqual(result, [{"value": 1.0}, {"value": None}])

    def test_forecast_returns_not_found_when_no_data_is_available(self):
        with patch.object(app, "build_day", return_value=pd.DataFrame()):
            with self.assertRaisesRegex(
                HTTPException, "No forecast available before that cutoff"
            ):
                app.forecast(date(2026, 1, 8))

    def test_accuracy_returns_expected_metrics(self):
        day_one = pd.DataFrame({"actual": [100, 200], "error": [10, -20]})
        day_two = pd.DataFrame({"actual": [300], "error": [30]})

        with patch.object(app, "build_day", side_effect=[day_one, day_two]):
            result = app.accuracy(date(2026, 1, 8), date(2026, 1, 9))

        self.assertEqual(result["count"], 3)
        self.assertAlmostEqual(result["mae"], 20)
        self.assertAlmostEqual(result["rmse"], np.sqrt(1400 / 3))
        self.assertAlmostEqual(result["bias"], 20 / 3)
        self.assertAlmostEqual(result["p90_abs_error"], 28)
        self.assertAlmostEqual(result["mean_actual"], 200)
        self.assertAlmostEqual(result["mae_pct_of_mean"], 10)


if __name__ == "__main__":
    unittest.main()
