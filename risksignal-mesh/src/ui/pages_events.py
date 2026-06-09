from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.ui.components import display_dataframe


def render_events_page(raw_df: pd.DataFrame, signals_df: pd.DataFrame, keyword: str) -> None:
    st.subheader("Polymarket Event Signals")

    if raw_df is None or raw_df.empty:
        st.info(
            "No active Polymarket markets were found for this keyword. Try another keyword such as "
            "recession, inflation, Fed rates, oil, or election."
        )
        return

    display_cols = [
        "event_title",
        "question",
        "category",
        "end_date",
        "volume",
        "liquidity",
        "outcomes",
        "outcome_prices",
        "implied_probability",
    ]
    st.markdown(f"**Event Markets For `{keyword}`**")
    display_dataframe(raw_df, display_cols)

    chart_cols = st.columns(2)
    with chart_cols[0]:
        volume_df = raw_df.dropna(subset=["volume"]).sort_values("volume", ascending=False).head(10)
        if not volume_df.empty:
            fig = px.bar(
                volume_df,
                x="volume",
                y="question",
                orientation="h",
                title="Top Events By Volume",
                labels={"volume": "Volume", "question": ""},
            )
            fig.update_layout(height=430, margin=dict(l=10, r=20, t=55, b=20), yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("Volume data is not available for the current results.")

    with chart_cols[1]:
        probability_df = signals_df.dropna(subset=["signal_value"]).sort_values("signal_value", ascending=False).head(10)
        if not probability_df.empty:
            fig = px.bar(
                probability_df,
                x="signal_value",
                y="question",
                orientation="h",
                title="Top Events By Implied Probability",
                labels={"signal_value": "Implied probability", "question": ""},
                range_x=[0, 1],
            )
            fig.update_layout(height=430, margin=dict(l=10, r=20, t=55, b=20), yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("Implied probability could not be parsed for the current results.")

    st.markdown("**Event-To-Risk-Theme Mapping**")
    display_dataframe(
        signals_df,
        [
            "event_title",
            "question",
            "category",
            "end_date",
            "volume",
            "liquidity",
            "outcomes",
            "outcome_prices",
            "signal_value",
            "related_risk_theme",
            "severity",
            "direction",
            "url",
        ],
    )
