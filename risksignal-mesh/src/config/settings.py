"""Application settings and configuration loading."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

import pandas as pd
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "src" / "data"
FRED_SERIES_CONFIG_PATH = DATA_DIR / "fred_series_config.csv"
RISK_THEME_CONFIG_PATH = DATA_DIR / "risk_theme_config.csv"


def load_environment() -> None:
    """Load local environment variables from .env when present."""
    load_dotenv(PROJECT_ROOT / ".env")


def get_fred_api_key(streamlit_module: object | None = None) -> str | None:
    """Return the FRED API key from Streamlit secrets first, then env vars."""
    if streamlit_module is not None:
        try:
            value = getattr(streamlit_module, "secrets", {}).get("FRED_API_KEY")
            if value:
                return str(value)
        except Exception:
            pass

    load_environment()
    value = os.getenv("FRED_API_KEY")
    return value or None


def load_csv_config(path: Path, required_columns: Iterable[str]) -> pd.DataFrame:
    """Load a CSV config file and validate expected columns."""
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    df = pd.read_csv(path)
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"Configuration file {path.name} is missing columns: {joined}")
    return df


def load_fred_series_config() -> pd.DataFrame:
    return load_csv_config(
        FRED_SERIES_CONFIG_PATH,
        [
            "display_name",
            "series_id",
            "category",
            "risk_theme",
            "unit",
            "frequency",
            "description",
        ],
    )


def load_risk_theme_config() -> pd.DataFrame:
    return load_csv_config(
        RISK_THEME_CONFIG_PATH,
        [
            "risk_theme",
            "risk_category",
            "description",
            "fred_series_keywords",
            "polymarket_keywords",
        ],
    )

