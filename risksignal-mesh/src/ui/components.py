"""Reusable Streamlit UI helpers."""

from __future__ import annotations

import html
from typing import Iterable

import pandas as pd
import streamlit as st


SEVERITY_COLORS = {
    "high": "#b42318",
    "medium": "#b54708",
    "low": "#027a48",
    "unknown": "#667085",
}


def apply_page_style() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 2.75rem;
            padding-bottom: 2rem;
        }
        div[data-testid="stTabs"] > div[data-baseweb="tab-list"] {
            position: sticky;
            top: 2.65rem;
            z-index: 100;
            background: var(--background-color, #0e1117);
            border-bottom: 1px solid rgba(148, 163, 184, 0.28);
            min-height: 3.25rem;
            overflow: visible;
            padding: 0.75rem 0 0.45rem 0;
        }
        button[data-baseweb="tab"] {
            min-height: 2.65rem;
            align-items: center;
        }
        button[data-baseweb="tab"] p {
            white-space: nowrap;
            line-height: 1.2;
        }
        [data-testid="stMetric"] {
            background: #f8fafc;
            border: 1px solid #d0d5dd;
            border-radius: 8px;
            padding: 0.85rem 1rem;
            min-height: 7.25rem;
        }
        .metric-card {
            background: #f8fafc;
            border: 1px solid #d0d5dd;
            border-radius: 8px;
            min-height: 7.25rem;
            padding: 0.9rem 1rem;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .metric-label {
            color: #344054;
            font-size: 0.82rem;
            line-height: 1.25;
            overflow-wrap: anywhere;
        }
        .metric-value {
            color: #101828;
            font-size: clamp(1.6rem, 2.2vw, 2.15rem);
            font-weight: 650;
            line-height: 1.08;
            overflow-wrap: anywhere;
        }
        .metric-help {
            color: #667085;
            font-size: 0.72rem;
            line-height: 1.25;
            margin-top: 0.35rem;
            overflow-wrap: anywhere;
        }
        [data-testid="stMetricLabel"] p {
            color: #344054;
            font-size: 0.82rem;
            line-height: 1.2;
            white-space: normal;
            overflow-wrap: anywhere;
        }
        [data-testid="stMetricValue"],
        [data-testid="stMetricValue"] div {
            color: #101828;
            font-size: clamp(1.45rem, 2vw, 2rem);
            line-height: 1.12;
            white-space: normal;
            overflow-wrap: anywhere;
        }
        [data-testid="stMetricDelta"],
        [data-testid="stMetricDelta"] div {
            color: #475467;
        }
        .risk-caption {
            color: #98a2b3;
            font-size: 0.92rem;
            line-height: 1.45;
        }
        .section-note {
            border-left: 4px solid #2e90fa;
            padding: 0.6rem 0.9rem;
            background: #eff8ff;
            border-radius: 6px;
            color: #184e77;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def severity_sort_value(severity: str | None) -> int:
    return {"high": 3, "medium": 2, "low": 1, "unknown": 0}.get(str(severity or "unknown").lower(), 0)


def severity_color(severity: str | None) -> str:
    return SEVERITY_COLORS.get(str(severity or "unknown").lower(), SEVERITY_COLORS["unknown"])


def render_kpis(metrics: Iterable[tuple[str, str | int | float, str | None]]) -> None:
    metrics = list(metrics)
    columns = st.columns(len(metrics) or 1)
    for column, (label, value, help_text) in zip(columns, metrics):
        safe_label = html.escape(str(label))
        safe_value = html.escape(str(value))
        safe_help = html.escape(str(help_text or ""))
        help_html = f'<div class="metric-help">{safe_help}</div>' if safe_help else ""
        column.markdown(
            f"""
            <div class="metric-card" title="{safe_help}">
              <div class="metric-label">{safe_label}</div>
              <div>
                <div class="metric-value">{safe_value}</div>
                {help_html}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def format_probability(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{float(value):.0%}"


def display_dataframe(df: pd.DataFrame, columns: list[str] | None = None, height: int = 360) -> None:
    if df is None or df.empty:
        st.info("No signals are available for the current filters.")
        return

    shown = df.copy()
    if columns:
        shown = shown[[column for column in columns if column in shown.columns]]
    st.dataframe(shown, width="stretch", height=height, hide_index=True)


def render_data_caveats() -> None:
    st.caption(
        "This demo is for risk intelligence prototyping and management discussion support only. "
        "FRED data may be delayed or revised. Polymarket probabilities are market-implied signals, "
        "not official forecasts or regulatory data. Severity scores are transparent heuristics and "
        "are not validated risk models. The application does not provide investment, trading, legal, "
        "or regulatory advice."
    )
