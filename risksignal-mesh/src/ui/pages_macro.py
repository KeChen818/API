from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.ui.components import display_dataframe, render_kpis


def render_macro_page(raw_df: pd.DataFrame, signals_df: pd.DataFrame, api_key_available: bool) -> None:
    st.subheader("FRED Macro Signals")

    if not api_key_available:
        st.warning("FRED API key is missing. Please add FRED_API_KEY to Streamlit secrets or environment variables.")

    if raw_df is None or raw_df.empty:
        st.info("No FRED observations are loaded for the current selection.")
        return

    theme_options = ["All"] + sorted(raw_df["risk_theme"].dropna().unique().tolist())
    selected_theme = st.selectbox("Risk theme filter", theme_options, key="fred_risk_theme_filter")
    filtered_raw = raw_df if selected_theme == "All" else raw_df[raw_df["risk_theme"] == selected_theme]
    filtered_signals = (
        signals_df if selected_theme == "All" else signals_df[signals_df["related_risk_theme"] == selected_theme]
    )

    fig = px.line(
        filtered_raw,
        x="date",
        y="value",
        color="display_name",
        labels={"date": "Date", "value": "Value", "display_name": "Series"},
        title="Selected FRED Series",
    )
    fig.update_layout(height=430, legend_title_text="", margin=dict(l=20, r=20, t=55, b=20))
    st.plotly_chart(fig, width="stretch")

    if not filtered_signals.empty:
        latest_metrics = []
        for _, row in filtered_signals.head(4).iterrows():
            value = row.get("signal_value")
            unit = row.get("unit") or ""
            formatted = "n/a" if pd.isna(value) else f"{float(value):,.2f}".rstrip("0").rstrip(".")
            latest_metrics.append(
                (
                    str(row.get("signal_name")),
                    f"{formatted} {unit}".strip(),
                    f"{row.get('severity', 'unknown')} severity; {row.get('direction', 'unknown')} direction",
                )
            )
        render_kpis(latest_metrics)

    st.markdown("**Percentile And Severity**")
    display_dataframe(
        filtered_signals,
        [
            "signal_name",
            "signal_value",
            "unit",
            "prior_value",
            "change",
            "percentile_rank",
            "direction",
            "severity",
            "related_risk_theme",
        ],
        height=260,
    )

    st.markdown("**Normalized Signal Table**")
    display_dataframe(
        filtered_signals,
        [
            "date",
            "source",
            "signal_name",
            "signal_type",
            "signal_value",
            "unit",
            "direction",
            "severity",
            "related_risk_theme",
            "evidence_text",
        ],
    )
