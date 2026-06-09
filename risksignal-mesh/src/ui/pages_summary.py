from __future__ import annotations

import pandas as pd
import streamlit as st

from src.services.narrative_generator import generate_risk_profile_summary
from src.ui.components import display_dataframe


def render_summary_page(mapped_signals_df: pd.DataFrame, fallback_themes: list[str]) -> None:
    st.subheader("Risk Profile Summary")

    if mapped_signals_df is None or mapped_signals_df.empty:
        themes = fallback_themes
    else:
        themes = sorted(mapped_signals_df["related_risk_theme"].dropna().unique().tolist())
        if not themes:
            themes = fallback_themes

    selected_theme = st.selectbox("Select risk theme", themes)
    generate = st.button("Generate Summary", type="primary")

    if generate:
        summary = generate_risk_profile_summary(mapped_signals_df, selected_theme)
        st.markdown(summary)

        support = pd.DataFrame()
        if mapped_signals_df is not None and not mapped_signals_df.empty:
            support = mapped_signals_df[mapped_signals_df["related_risk_theme"] == selected_theme]

        st.markdown("**Supporting Evidence**")
        display_dataframe(
            support,
            [
                "date",
                "source",
                "signal_name",
                "signal_value",
                "unit",
                "direction",
                "severity",
                "evidence_text",
            ],
            height=260,
        )
    else:
        st.info("Select a risk theme and generate a deterministic summary.")

