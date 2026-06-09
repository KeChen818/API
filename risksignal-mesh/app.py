from __future__ import annotations

from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

from src.config.settings import get_fred_api_key, load_fred_series_config, load_risk_theme_config
from src.providers.fred_provider import FredProvider
from src.providers.polymarket_provider import PolymarketProvider
from src.services.narrative_generator import generate_risk_profile_summary
from src.services.risk_mapping import map_signals_to_risk_themes, theme_severity_summary
from src.services.severity_scoring import severity_rank
from src.services.signal_normalizer import normalize_fred_signals, normalize_polymarket_signals
from src.ui.components import apply_page_style, display_dataframe, render_data_caveats, render_kpis
from src.ui.pages_events import render_events_page
from src.ui.pages_macro import render_macro_page
from src.ui.pages_mapping import render_mapping_page
from src.ui.pages_summary import render_summary_page


st.set_page_config(page_title="RiskSignal Mesh", layout="wide")
apply_page_style()


@st.cache_data(show_spinner=False)
def cached_fred_config() -> pd.DataFrame:
    return load_fred_series_config()


@st.cache_data(show_spinner=False)
def cached_risk_theme_config() -> pd.DataFrame:
    return load_risk_theme_config()


@st.cache_data(ttl=3600, show_spinner=False)
def cached_fetch_fred(
    api_key: str | None,
    selected_series: tuple[str, ...],
    observation_start: str,
) -> tuple[pd.DataFrame, str | None]:
    provider = FredProvider(api_key)
    config_df = load_fred_series_config()
    df = provider.fetch_from_config(config_df, list(selected_series), observation_start)
    return df, provider.last_error


@st.cache_data(ttl=300, show_spinner=False)
def cached_fetch_polymarket(
    keyword: str,
    limit: int,
    active: bool,
    closed: bool,
) -> tuple[pd.DataFrame, str | None]:
    provider = PolymarketProvider()
    df = provider.fetch_events(keyword, limit=limit, active=active, closed=closed)
    if df.empty and provider.last_error is None:
        df = provider.fetch_markets(keyword, limit=limit, active=active, closed=closed)
    return df, provider.last_error


def _safe_concat(frames: list[pd.DataFrame]) -> pd.DataFrame:
    non_empty = [frame for frame in frames if frame is not None and not frame.empty]
    if not non_empty:
        return pd.DataFrame()
    return pd.concat(non_empty, ignore_index=True, sort=False)


def _highest_severity_theme(mapped_signals_df: pd.DataFrame) -> str:
    if mapped_signals_df.empty:
        return "None loaded"

    rows = []
    for theme, group in mapped_signals_df.groupby("related_risk_theme"):
        highest = max(group["severity"].fillna("unknown").str.lower(), key=severity_rank)
        rows.append((theme, highest, severity_rank(highest), len(group)))
    rows = sorted(rows, key=lambda item: (item[2], item[3]), reverse=True)
    return f"{rows[0][0]} ({rows[0][1]})"


def _render_overview(
    mapped_signals_df: pd.DataFrame,
    fred_signals_df: pd.DataFrame,
    polymarket_signals_df: pd.DataFrame,
    risk_theme_config_df: pd.DataFrame,
) -> None:
    st.title("RiskSignal Mesh")
    st.markdown(
        '<p class="risk-caption">A signal-driven layer connecting risk inventory, macro data, and event probabilities.</p>',
        unsafe_allow_html=True,
    )
    st.write(
        "RiskSignal Mesh connects external evidence to enterprise risk themes so risk identification teams "
        "can review macro pressure, event probabilities, and mapped risk narratives in one place."
    )

    mapped_theme_count = (
        mapped_signals_df["related_risk_theme"].nunique() if not mapped_signals_df.empty else 0
    )
    render_kpis(
        [
            ("FRED Signals Loaded", len(fred_signals_df), "Latest normalized FRED signals"),
            ("Polymarket Events Loaded", len(polymarket_signals_df), "Normalized event probability signals"),
            ("Mapped Risk Themes", mapped_theme_count, "Themes with at least one mapped signal"),
            ("Highest Severity Theme", _highest_severity_theme(mapped_signals_df), "Highest current severity"),
        ]
    )

    st.markdown("**Risk Themes By Severity**")
    summary = theme_severity_summary(mapped_signals_df)
    if summary.empty:
        display_dataframe(risk_theme_config_df[["risk_theme", "risk_category", "description"]], height=260)
    else:
        display_dataframe(summary, height=260)

    if not summary.empty:
        chart_df = summary.melt(
            id_vars="related_risk_theme",
            value_vars=["high", "medium", "low", "unknown"],
            var_name="severity",
            value_name="severity_signal_count",
        )
        fig = px.density_heatmap(
            chart_df,
            x="severity",
            y="related_risk_theme",
            z="severity_signal_count",
            histfunc="sum",
            color_continuous_scale=["#f2f4f7", "#fdb022", "#b42318"],
            title="Mapped Signal Heatmap",
        )
        fig.update_layout(height=330, margin=dict(l=20, r=20, t=55, b=20), yaxis_title="", xaxis_title="")
        st.plotly_chart(fig, width="stretch")

    if not mapped_signals_df.empty:
        top_themes = (
            summary.sort_values(["high", "medium", "signal_count"], ascending=False)["related_risk_theme"]
            .head(2)
            .tolist()
        )
        st.markdown(
            "Current signal environment shows elevated attention around "
            f"{' and '.join(top_themes)}. Macro indicators provide rate, spread, inflation, and labor context, "
            "while prediction markets add event-based signals around recession, inflation, policy, and geopolitical outcomes."
        )
    else:
        st.markdown(
            "Current signal environment has not been loaded yet. Add a FRED API key for macro data and search "
            "Polymarket keywords to populate the unified risk intelligence layer."
        )

    if not mapped_signals_df.empty:
        first_theme = _highest_severity_theme(mapped_signals_df).split(" (")[0]
        with st.expander("Preview Deterministic Risk Narrative", expanded=False):
            st.markdown(generate_risk_profile_summary(mapped_signals_df, first_theme))

    render_data_caveats()


def _render_architecture_page() -> None:
    st.subheader("Architecture / Roadmap")
    st.code(
        """External Signal Providers
    |-- FRED
    |-- Polymarket
    |-- Yahoo Finance - future
    |-- SEC EDGAR - future
    |-- Finnhub - future
    `-- OECD - future

Signal Normalization Layer
    |-- schema alignment
    |-- severity scoring
    |-- risk theme mapping
    `-- evidence text generation

Risk Intelligence Layer
    |-- risk profile summary
    |-- inventory linkage - future
    |-- meeting minutes linkage - future
    `-- internal PDF linkage - future

Streamlit Enterprise Demo UI
    |-- executive overview
    |-- macro signals
    |-- event signals
    |-- mapped risk themes
    `-- risk profile summary""",
        language="text",
    )

    st.markdown(
        """
**Phased Roadmap**

1. Phase 1: FRED + Polymarket MVP
2. Phase 2: Yahoo Finance + SEC EDGAR
3. Phase 3: Finnhub + OECD + News
4. Phase 4: Internal PDF and meeting minutes ingestion
5. Phase 5: LLM-generated CRO-ready risk profile
6. Phase 6: Enterprise deployment with database, auth, audit trail, and API services
"""
    )
    render_data_caveats()


def _load_configs() -> tuple[pd.DataFrame, pd.DataFrame]:
    try:
        return cached_fred_config(), cached_risk_theme_config()
    except (FileNotFoundError, ValueError) as exc:
        st.error(f"Configuration could not be loaded. {exc}")
        st.stop()


def main() -> None:
    fred_config_df, risk_theme_config_df = _load_configs()
    fred_api_key = get_fred_api_key(st)

    tabs = st.tabs(
        [
            "Executive Overview",
            "FRED Macro Signals",
            "Polymarket Event Signals",
            "Risk Theme Mapping",
            "Risk Profile Summary",
            "Architecture / Roadmap",
        ]
    )

    with tabs[1]:
        st.subheader("Macro Signal Controls")
        default_series = ["FEDFUNDS", "DGS10", "UNRATE", "BAMLH0A0HYM2"]
        selected_series = st.multiselect(
            "FRED series",
            fred_config_df["series_id"].tolist(),
            default=[series for series in default_series if series in fred_config_df["series_id"].tolist()],
            format_func=lambda series_id: fred_config_df.loc[
                fred_config_df["series_id"] == series_id, "display_name"
            ].iloc[0],
        )
        control_cols = st.columns([1, 1, 2])
        with control_cols[0]:
            observation_start = st.date_input("Start date", value=date(2020, 1, 1))
        with control_cols[1]:
            refresh_fred = st.button("Refresh FRED Data")
        with control_cols[2]:
            st.caption("FRED calls are cached for one hour.")

        if refresh_fred:
            cached_fetch_fred.clear()

        if fred_api_key:
            with st.spinner("Loading FRED observations..."):
                fred_raw_df, fred_error = cached_fetch_fred(
                    fred_api_key,
                    tuple(selected_series),
                    observation_start.isoformat(),
                )
        else:
            fred_raw_df, fred_error = pd.DataFrame(), (
                "FRED API key is missing. Please add FRED_API_KEY to Streamlit secrets or environment variables."
            )

        if fred_error:
            st.warning(fred_error)

        fred_signals_df = map_signals_to_risk_themes(
            normalize_fred_signals(fred_raw_df),
            risk_theme_config_df,
        )
        render_macro_page(fred_raw_df, fred_signals_df, api_key_available=bool(fred_api_key))

    with tabs[2]:
        st.subheader("Event Signal Controls")
        if "polymarket_keyword" not in st.session_state:
            st.session_state.polymarket_keyword = "recession"

        presets = [
            "recession",
            "inflation",
            "Fed rates",
            "banking crisis",
            "oil",
            "election",
            "commercial real estate",
        ]
        preset_cols = st.columns(len(presets))
        for column, preset in zip(preset_cols, presets):
            if column.button(preset, key=f"preset_{preset}"):
                st.session_state.polymarket_keyword = preset

        keyword = st.text_input("Keyword", key="polymarket_keyword")
        event_control_cols = st.columns([1, 1, 1, 1])
        with event_control_cols[0]:
            limit = st.selectbox("Limit", [10, 25, 50, 100], index=1)
        with event_control_cols[1]:
            active = st.checkbox("Active", value=True)
        with event_control_cols[2]:
            closed = st.checkbox("Closed", value=False)
        with event_control_cols[3]:
            refresh_polymarket = st.button("Refresh Polymarket Data")

        if refresh_polymarket:
            cached_fetch_polymarket.clear()

        with st.spinner("Loading Polymarket events..."):
            polymarket_raw_df, polymarket_error = cached_fetch_polymarket(keyword, int(limit), active, closed)

        if polymarket_error:
            st.warning(polymarket_error)

        polymarket_signals_df = map_signals_to_risk_themes(
            normalize_polymarket_signals(polymarket_raw_df),
            risk_theme_config_df,
        )
        render_events_page(polymarket_raw_df, polymarket_signals_df, keyword)

    mapped_signals_df = _safe_concat([fred_signals_df, polymarket_signals_df])

    with tabs[0]:
        _render_overview(mapped_signals_df, fred_signals_df, polymarket_signals_df, risk_theme_config_df)

    with tabs[3]:
        render_mapping_page(mapped_signals_df)

    with tabs[4]:
        render_summary_page(mapped_signals_df, sorted(risk_theme_config_df["risk_theme"].dropna().tolist()))

    with tabs[5]:
        _render_architecture_page()


if __name__ == "__main__":
    main()
