"""Map normalized signals to configured enterprise risk themes."""

from __future__ import annotations

from typing import Any

import pandas as pd


UNMAPPED_THEME = "Unmapped / Emerging Risk"


def _clean(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    return str(value).strip()


def split_keywords(value: Any) -> list[str]:
    text = _clean(value)
    if not text:
        return []
    return [part.strip() for part in text.split(";") if part.strip()]


def _match_count(text: str, keywords: list[str]) -> int:
    lowered = text.lower()
    return sum(1 for keyword in keywords if keyword.lower() in lowered)


def _source_text(row: pd.Series, source: str) -> str:
    if source == "fred":
        return " ".join(
            _clean(row.get(column))
            for column in ["signal_name", "display_name", "series_id", "signal_text", "evidence_text"]
        )
    return " ".join(
        _clean(row.get(column))
        for column in [
            "question",
            "category",
            "market_title",
            "event_title",
            "signal_name",
            "signal_text",
            "evidence_text",
        ]
    )


def map_signal_to_theme(row: pd.Series, risk_theme_config_df: pd.DataFrame) -> str:
    if risk_theme_config_df is None or risk_theme_config_df.empty:
        existing = _clean(row.get("related_risk_theme"))
        return existing or UNMAPPED_THEME

    source = _clean(row.get("source")).lower()
    keyword_column = "fred_series_keywords" if source == "fred" else "polymarket_keywords"
    match_text = _source_text(row, source)

    best_theme = ""
    best_count = 0
    for _, theme_row in risk_theme_config_df.iterrows():
        keywords = split_keywords(theme_row.get(keyword_column))
        count = _match_count(match_text, keywords)
        if count > best_count:
            best_theme = _clean(theme_row.get("risk_theme"))
            best_count = count

    if best_count > 0 and best_theme:
        return best_theme

    existing = _clean(row.get("related_risk_theme"))
    return existing or UNMAPPED_THEME


def map_signals_to_risk_themes(
    signals_df: pd.DataFrame,
    risk_theme_config_df: pd.DataFrame,
) -> pd.DataFrame:
    if signals_df is None or signals_df.empty:
        output = pd.DataFrame() if signals_df is None else signals_df.copy()
        if "related_risk_theme" not in output.columns:
            output["related_risk_theme"] = pd.Series(dtype="object")
        return output

    mapped = signals_df.copy()
    mapped["related_risk_theme"] = mapped.apply(
        lambda row: map_signal_to_theme(row, risk_theme_config_df),
        axis=1,
    )
    return mapped


def theme_severity_summary(mapped_signals_df: pd.DataFrame) -> pd.DataFrame:
    if mapped_signals_df is None or mapped_signals_df.empty:
        return pd.DataFrame(columns=["related_risk_theme", "signal_count", "high", "medium", "low", "unknown"])

    summary = (
        mapped_signals_df.assign(severity=mapped_signals_df["severity"].fillna("unknown").str.lower())
        .pivot_table(
            index="related_risk_theme",
            columns="severity",
            values="signal_name",
            aggfunc="count",
            fill_value=0,
        )
        .reset_index()
    )
    for severity in ["high", "medium", "low", "unknown"]:
        if severity not in summary.columns:
            summary[severity] = 0
    summary["signal_count"] = summary[["high", "medium", "low", "unknown"]].sum(axis=1)
    return summary[["related_risk_theme", "signal_count", "high", "medium", "low", "unknown"]]

