"""FRED macro signal provider."""

from __future__ import annotations

from typing import Any

import pandas as pd
import requests

from src.providers.base import BaseSignalProvider
from src.services.signal_normalizer import normalize_fred_signals


class FredProvider(BaseSignalProvider):
    provider_name = "FRED"

    BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

    def __init__(self, api_key: str | None):
        self.api_key = api_key
        self.last_error: str | None = None

    def fetch(self, *args: Any, **kwargs: Any) -> pd.DataFrame:
        return self.fetch_from_config(*args, **kwargs)

    def fetch_series(
        self,
        series_id: str,
        observation_start: str = "2020-01-01",
    ) -> pd.DataFrame:
        if not self.api_key:
            self.last_error = "FRED API key is missing. Please add FRED_API_KEY to Streamlit secrets or environment variables."
            return pd.DataFrame()

        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
            "observation_start": observation_start,
        }
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=20)
            response.raise_for_status()
            payload = response.json()
        except requests.Timeout:
            self.last_error = "The FRED request timed out. Please try again."
            return pd.DataFrame()
        except requests.RequestException:
            self.last_error = "FRED data could not be loaded right now. Please check the API key or try again later."
            return pd.DataFrame()
        except ValueError:
            self.last_error = "FRED returned an unexpected response format."
            return pd.DataFrame()

        observations = payload.get("observations", [])
        if not observations:
            return pd.DataFrame(columns=["date", "value", "series_id", "source"])

        df = pd.DataFrame(observations)
        df["date"] = pd.to_datetime(df.get("date"), errors="coerce").dt.date
        df["value"] = pd.to_numeric(df.get("value"), errors="coerce")
        df["series_id"] = series_id
        df["source"] = self.provider_name
        df = df.dropna(subset=["date", "value"])
        return df[["date", "value", "series_id", "source"]]

    def fetch_from_config(
        self,
        config_df: pd.DataFrame,
        selected_series: list[str],
        observation_start: str = "2020-01-01",
    ) -> pd.DataFrame:
        if config_df is None or config_df.empty or not selected_series:
            return pd.DataFrame()

        frames: list[pd.DataFrame] = []
        for series_id in selected_series:
            meta_rows = config_df[config_df["series_id"] == series_id]
            if meta_rows.empty:
                continue

            raw = self.fetch_series(series_id, observation_start=observation_start)
            if raw.empty:
                continue

            meta = meta_rows.iloc[0].to_dict()
            for column, value in meta.items():
                raw[column] = value
            raw["source"] = self.provider_name
            frames.append(raw)

        if not frames:
            return pd.DataFrame()
        return pd.concat(frames, ignore_index=True)

    def normalize(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        return normalize_fred_signals(raw_df)

