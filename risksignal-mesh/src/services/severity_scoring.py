"""Transparent heuristic severity scoring for normalized signals."""

from __future__ import annotations

from typing import Any

import pandas as pd


SEVERITY_RANK = {"unknown": 0, "low": 1, "medium": 2, "high": 3}


def safe_float(value: Any) -> float | None:
    """Coerce a value to float, returning None for blanks or malformed inputs."""
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except TypeError:
        pass

    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed


def normalize_probability_value(value: Any) -> float | None:
    """Normalize a raw probability value to a 0-1 range when possible."""
    parsed = safe_float(value)
    if parsed is None:
        return None
    if 0 <= parsed <= 1:
        return parsed
    if 1 < parsed <= 100:
        return parsed / 100
    return None


def classify_percentile(percentile_rank: float | None) -> str:
    if percentile_rank is None:
        return "unknown"
    if percentile_rank >= 85:
        return "high"
    if percentile_rank >= 60:
        return "medium"
    return "low"


def classify_polymarket_probability(probability: float | None) -> str:
    normalized = normalize_probability_value(probability)
    if normalized is None:
        return "unknown"
    if normalized >= 0.50:
        return "high"
    if normalized >= 0.25:
        return "medium"
    return "low"


def polymarket_direction(probability: float | None) -> str:
    normalized = normalize_probability_value(probability)
    if normalized is None:
        return "unknown"
    return "elevated" if normalized >= 0.25 else "contained"


def severity_rank(severity: str | None) -> int:
    return SEVERITY_RANK.get(str(severity or "unknown").lower(), 0)


def highest_severity(severities: pd.Series) -> str:
    if severities.empty:
        return "unknown"
    return max((str(item).lower() for item in severities.dropna()), key=severity_rank, default="unknown")


def _is_rate_signal(signal_name: str, category: str) -> bool:
    text = f"{signal_name} {category}".lower()
    return any(token in text for token in ["rate", "treasury", "funds"])


def _fred_direction(latest_value: float, median_value: float, signal_name: str, category: str) -> str:
    text = f"{signal_name} {category}".lower()
    if latest_value < median_value:
        return "easing" if _is_rate_signal(signal_name, category) else "improving"
    if latest_value == median_value:
        return "stable"
    if "spread" in text:
        return "widening"
    if any(token in text for token in ["stress", "unemployment", "cpi", "inflation"]):
        return "worsening"
    if _is_rate_signal(signal_name, category):
        return "tightening"
    return "elevated"


def score_fred_series(series_df: pd.DataFrame) -> dict[str, float | str | None]:
    """Score one FRED series over the selected observation window."""
    if series_df.empty or "value" not in series_df.columns:
        return {
            "latest_value": None,
            "prior_value": None,
            "change": None,
            "percentile_rank": None,
            "severity": "unknown",
            "direction": "unknown",
        }

    working = series_df.copy()
    working["date"] = pd.to_datetime(working.get("date"), errors="coerce")
    working["value"] = pd.to_numeric(working.get("value"), errors="coerce")
    working = working.dropna(subset=["date", "value"]).sort_values("date")

    if working.empty:
        return {
            "latest_value": None,
            "prior_value": None,
            "change": None,
            "percentile_rank": None,
            "severity": "unknown",
            "direction": "unknown",
        }

    latest_row = working.iloc[-1]
    latest_value = float(latest_row["value"])
    latest_date = latest_row["date"]

    prior_candidates = working[working["date"] <= latest_date - pd.Timedelta(days=30)]
    if not prior_candidates.empty:
        prior_value = float(prior_candidates.iloc[-1]["value"])
    elif len(working) > 1:
        prior_value = float(working.iloc[-2]["value"])
    else:
        prior_value = latest_value

    percentile_rank = float((working["value"] <= latest_value).mean() * 100)
    median_value = float(working["value"].median())

    signal_name = str(latest_row.get("display_name", latest_row.get("series_id", "")))
    category = str(latest_row.get("category", ""))

    return {
        "latest_value": latest_value,
        "prior_value": prior_value,
        "change": latest_value - prior_value,
        "percentile_rank": percentile_rank,
        "severity": classify_percentile(percentile_rank),
        "direction": _fred_direction(latest_value, median_value, signal_name, category),
    }


def score_fred_dataframe(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Return one scored latest row per FRED series."""
    if raw_df.empty:
        return pd.DataFrame()

    group_column = "series_id" if "series_id" in raw_df.columns else "display_name"
    if group_column not in raw_df.columns:
        return pd.DataFrame()

    rows: list[dict[str, Any]] = []
    for _, group in raw_df.groupby(group_column, dropna=False):
        working = group.copy()
        working["date"] = pd.to_datetime(working.get("date"), errors="coerce")
        working["value"] = pd.to_numeric(working.get("value"), errors="coerce")
        working = working.dropna(subset=["date", "value"]).sort_values("date")
        if working.empty:
            continue

        latest_row = working.iloc[-1].to_dict()
        latest_row["date"] = working.iloc[-1]["date"].date()
        latest_row.update(score_fred_series(working))
        rows.append(latest_row)

    return pd.DataFrame(rows)

