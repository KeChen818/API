from __future__ import annotations

import pandas as pd
import streamlit as st

from src.services.risk_mapping import theme_severity_summary
from src.ui.components import display_dataframe, render_kpis


def render_mapping_page(mapped_signals_df: pd.DataFrame) -> None:
    st.subheader("Risk Theme Mapping")

    if mapped_signals_df is None or mapped_signals_df.empty:
        st.info("No unified signals are loaded yet.")
        return

    filter_cols = st.columns(3)
    with filter_cols[0]:
        selected_themes = st.multiselect(
            "Risk theme",
            sorted(mapped_signals_df["related_risk_theme"].dropna().unique().tolist()),
            default=sorted(mapped_signals_df["related_risk_theme"].dropna().unique().tolist()),
        )
    with filter_cols[1]:
        selected_sources = st.multiselect(
            "Source",
            sorted(mapped_signals_df["source"].dropna().unique().tolist()),
            default=sorted(mapped_signals_df["source"].dropna().unique().tolist()),
        )
    with filter_cols[2]:
        selected_severities = st.multiselect(
            "Severity",
            ["high", "medium", "low", "unknown"],
            default=["high", "medium", "low", "unknown"],
        )

    filtered = mapped_signals_df[
        mapped_signals_df["related_risk_theme"].isin(selected_themes)
        & mapped_signals_df["source"].isin(selected_sources)
        & mapped_signals_df["severity"].fillna("unknown").str.lower().isin(selected_severities)
    ]

    summary = theme_severity_summary(filtered)
    high_count = int((filtered["severity"].fillna("").str.lower() == "high").sum())
    medium_count = int((filtered["severity"].fillna("").str.lower() == "medium").sum())
    low_count = int((filtered["severity"].fillna("").str.lower() == "low").sum())
    render_kpis(
        [
            ("Mapped Signals", len(filtered), "Signals after current filters"),
            ("High Severity", high_count, "High severity signals"),
            ("Medium Severity", medium_count, "Medium severity signals"),
            ("Low Severity", low_count, "Low severity signals"),
        ]
    )

    st.markdown("**Signal Counts By Theme**")
    display_dataframe(summary, height=220)

    st.download_button(
        "Download Mapped Signals CSV",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="risksignal_mesh_mapped_signals.csv",
        mime="text/csv",
    )

    st.markdown("**Unified Signal Table**")
    display_dataframe(
        filtered,
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
        height=430,
    )

