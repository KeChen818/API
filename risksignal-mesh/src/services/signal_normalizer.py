"""Provider-specific normalization into the unified RiskSignal schema."""

from __future__ import annotations

import ast
import json
from datetime import date
from typing import Any

import pandas as pd

from src.models.signal import RiskSignal
from src.services.severity_scoring import (
    classify_polymarket_probability,
    normalize_probability_value,
    polymarket_direction,
    score_fred_dataframe,
    safe_float,
)


SIGNAL_COLUMNS = [
    "date",
    "source",
    "signal_name",
    "signal_type",
    "signal_value",
    "signal_text",
    "unit",
    "direction",
    "severity",
    "related_risk_theme",
    "evidence_text",
    "url",
]


def empty_signal_frame(extra_columns: list[str] | None = None) -> pd.DataFrame:
    columns = SIGNAL_COLUMNS + [column for column in (extra_columns or []) if column not in SIGNAL_COLUMNS]
    return pd.DataFrame(columns=columns)


def _clean_text(value: Any, fallback: str = "") -> str:
    if value is None:
        return fallback
    try:
        if pd.isna(value):
            return fallback
    except TypeError:
        pass
    text = str(value).strip()
    return text or fallback


def _format_number(value: float | None) -> str:
    if value is None:
        return "unavailable"
    return f"{value:,.2f}".rstrip("0").rstrip(".")


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    try:
        if pd.isna(value):
            return []
    except (TypeError, ValueError):
        pass
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return []
        for parser in (json.loads, ast.literal_eval):
            try:
                parsed = parser(stripped)
            except (ValueError, SyntaxError, TypeError, json.JSONDecodeError):
                continue
            if isinstance(parsed, list):
                return parsed
        return [part.strip() for part in stripped.split(",") if part.strip()]
    return [value]


def coerce_outcomes(value: Any) -> list[str]:
    return [_clean_text(item) for item in _as_list(value) if _clean_text(item)]


def coerce_outcome_prices(value: Any) -> list[float]:
    prices: list[float] = []
    for item in _as_list(value):
        parsed = normalize_probability_value(item)
        if parsed is not None:
            prices.append(parsed)
    return prices


def extract_implied_probability(
    outcomes: Any,
    outcome_prices: Any,
    explicit_probability: Any = None,
) -> float | None:
    explicit = normalize_probability_value(explicit_probability)
    if explicit is not None:
        return explicit

    parsed_outcomes = [item.lower() for item in coerce_outcomes(outcomes)]
    parsed_prices = coerce_outcome_prices(outcome_prices)
    if not parsed_prices:
        return None

    yes_labels = {"yes", "y"}
    for index, outcome in enumerate(parsed_outcomes):
        if outcome in yes_labels and index < len(parsed_prices):
            return parsed_prices[index]

    return parsed_prices[0]


def normalize_fred_signals(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Convert FRED observations into one normalized latest signal per series."""
    if raw_df is None or raw_df.empty:
        return empty_signal_frame(["series_id", "display_name", "percentile_rank", "prior_value", "change"])

    scored_df = score_fred_dataframe(raw_df)
    if scored_df.empty:
        return empty_signal_frame(["series_id", "display_name", "percentile_rank", "prior_value", "change"])

    rows: list[dict[str, Any]] = []
    for _, row in scored_df.iterrows():
        latest_value = safe_float(row.get("latest_value", row.get("value")))
        signal_name = _clean_text(row.get("display_name"), _clean_text(row.get("series_id"), "FRED series"))
        unit = _clean_text(row.get("unit"))
        severity = _clean_text(row.get("severity"), "unknown")
        percentile = safe_float(row.get("percentile_rank"))
        unit_text = unit.lower() if unit else "units"
        evidence_text = (
            f"{signal_name} latest value is {_format_number(latest_value)} {unit_text}. "
            f"Selected-window percentile is {_format_number(percentile)}."
        )

        signal = RiskSignal(
            date=pd.to_datetime(row.get("date"), errors="coerce").date(),
            source="FRED",
            signal_name=signal_name,
            signal_type="macro_time_series",
            signal_value=latest_value,
            signal_text=_clean_text(row.get("description")),
            unit=unit or None,
            direction=_clean_text(row.get("direction"), "unknown"),
            severity=severity,
            related_risk_theme=_clean_text(row.get("risk_theme")) or None,
            evidence_text=evidence_text,
            url=None,
        ).model_dump()
        signal.update(
            {
                "series_id": row.get("series_id"),
                "display_name": signal_name,
                "category": row.get("category"),
                "frequency": row.get("frequency"),
                "percentile_rank": percentile,
                "prior_value": safe_float(row.get("prior_value")),
                "change": safe_float(row.get("change")),
            }
        )
        rows.append(signal)

    return pd.DataFrame(rows)


def normalize_polymarket_signals(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Convert Polymarket events or markets into normalized prediction signals."""
    extra_columns = [
        "market_id",
        "question",
        "category",
        "volume",
        "liquidity",
        "end_date",
        "outcomes",
        "outcome_prices",
        "event_title",
        "market_title",
    ]
    if raw_df is None or len(raw_df.index) == 0:
        return empty_signal_frame(extra_columns)

    rows: list[dict[str, Any]] = []
    for _, row in raw_df.iterrows():
        question = _clean_text(
            row.get("question"),
            _clean_text(row.get("market_title"), _clean_text(row.get("event_title"), "Polymarket event")),
        )
        outcomes = coerce_outcomes(row.get("outcomes"))
        outcome_prices = coerce_outcome_prices(row.get("outcome_prices"))
        probability = extract_implied_probability(
            outcomes,
            outcome_prices,
            row.get("implied_probability"),
        )
        severity = classify_polymarket_probability(probability)
        percent_text = f"{probability:.0%}" if probability is not None else "unavailable"
        evidence_text = f"Polymarket market-implied probability for {question} is {percent_text}."

        signal = RiskSignal(
            date=date.today(),
            source="Polymarket",
            signal_name=question,
            signal_type="prediction_event",
            signal_value=probability,
            signal_text=question,
            unit="probability",
            direction=polymarket_direction(probability),
            severity=severity,
            related_risk_theme=_clean_text(row.get("related_risk_theme")) or None,
            evidence_text=evidence_text,
            url=_clean_text(row.get("url")) or None,
        ).model_dump()
        signal.update(
            {
                "market_id": row.get("market_id"),
                "question": question,
                "category": row.get("category"),
                "volume": safe_float(row.get("volume")),
                "liquidity": safe_float(row.get("liquidity")),
                "end_date": row.get("end_date"),
                "outcomes": outcomes,
                "outcome_prices": outcome_prices,
                "event_title": row.get("event_title"),
                "market_title": row.get("market_title"),
            }
        )
        rows.append(signal)

    return pd.DataFrame(rows)


def normalize_signals(source: str, raw_df: pd.DataFrame) -> pd.DataFrame:
    source_key = source.strip().lower()
    if source_key == "fred":
        return normalize_fred_signals(raw_df)
    if source_key == "polymarket":
        return normalize_polymarket_signals(raw_df)
    raise ValueError(f"Unsupported signal source: {source}")
