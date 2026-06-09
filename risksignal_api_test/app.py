import json
from typing import Any

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


st.set_page_config(
    page_title="FRED + Polymarket API Smoke Test",
    layout="wide",
)


st.write("✅ App started")

st.title("FRED + Polymarket API Smoke Test")
st.caption("Simple one-file test before building the enterprise RiskSignal Mesh demo.")


# -----------------------------
# Config
# -----------------------------

FRED_SERIES = {
    "Fed Funds Rate": "FEDFUNDS",
    "10Y Treasury": "DGS10",
    "2Y Treasury": "DGS2",
    "Unemployment Rate": "UNRATE",
    "CPI": "CPIAUCSL",
    "HY Credit Spread": "BAMLH0A0HYM2",
    "IG Credit Spread": "BAMLC0A0CM",
    "Financial Stress Index": "STLFSI4",
}

POLYMARKET_PRESETS = [
    "recession",
    "inflation",
    "Fed rates",
    "banking crisis",
    "oil",
    "election",
    "commercial real estate",
]


def get_fred_api_key() -> str | None:
    try:
        return st.secrets.get("FRED_API_KEY")
    except Exception:
        return None


# -----------------------------
# FRED API
# -----------------------------

@st.cache_data(ttl=3600)
def fetch_fred_series(
    series_id: str,
    api_key: str,
    observation_start: str = "2020-01-01",
) -> pd.DataFrame:
    url = "https://api.stlouisfed.org/fred/series/observations"

    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": observation_start,
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()

    payload = response.json()

    if "observations" not in payload:
        raise ValueError(f"Unexpected FRED response: {payload}")

    df = pd.DataFrame(payload["observations"])

    if df.empty:
        return df

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["date", "value"])

    df["series_id"] = series_id

    return df[["date", "value", "series_id"]]


# -----------------------------
# Polymarket API
# -----------------------------

def safe_json_loads(value: Any) -> Any:
    """
    Polymarket sometimes returns list-like fields either as JSON strings or lists.
    This helper makes parsing safer.
    """
    if isinstance(value, list):
        return value

    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return value

    return value


def parse_yes_probability(outcomes: Any, outcome_prices: Any) -> float | None:
    outcomes = safe_json_loads(outcomes)
    outcome_prices = safe_json_loads(outcome_prices)

    if not isinstance(outcomes, list) or not isinstance(outcome_prices, list):
        return None

    if len(outcomes) != len(outcome_prices):
        return None

    for outcome, price in zip(outcomes, outcome_prices):
        if str(outcome).strip().lower() == "yes":
            try:
                return float(price)
            except Exception:
                return None

    return None


@st.cache_data(ttl=300)
def fetch_polymarket_events(
    keyword: str,
    limit: int = 25,
    active: bool = True,
    closed: bool = False,
) -> pd.DataFrame:
    url = "https://gamma-api.polymarket.com/events"

    params = {
        "search": keyword,
        "limit": limit,
        "active": str(active).lower(),
        "closed": str(closed).lower(),
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()

    data = response.json()
    df = pd.DataFrame(data)

    return df


@st.cache_data(ttl=300)
def fetch_polymarket_markets(
    keyword: str,
    limit: int = 25,
    active: bool = True,
    closed: bool = False,
) -> pd.DataFrame:
    url = "https://gamma-api.polymarket.com/markets"

    params = {
        "search": keyword,
        "limit": limit,
        "active": str(active).lower(),
        "closed": str(closed).lower(),
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()

    data = response.json()
    df = pd.DataFrame(data)

    if df.empty:
        return df

    # Normalize useful fields if present.
    for col in ["volume", "liquidity"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "endDate" in df.columns:
        df["endDate"] = pd.to_datetime(df["endDate"], errors="coerce")

    if "outcomes" in df.columns and "outcomePrices" in df.columns:
        df["yes_probability"] = df.apply(
            lambda row: parse_yes_probability(
                row.get("outcomes"),
                row.get("outcomePrices"),
            ),
            axis=1,
        )

    return df


# -----------------------------
# UI
# -----------------------------

fred_tab, polymarket_tab, combined_tab = st.tabs(
    ["1. FRED Test", "2. Polymarket Test", "3. Simple Combined Signal View"]
)


with fred_tab:
    st.subheader("FRED Macro API Test")

    fred_api_key = get_fred_api_key()

    if not fred_api_key:
        st.error(
            "Missing FRED_API_KEY. Add it to `.streamlit/secrets.toml` first."
        )
    else:
        col1, col2 = st.columns([1, 1])

        with col1:
            selected_name = st.selectbox(
                "Select FRED series",
                list(FRED_SERIES.keys()),
                index=5,
            )

        with col2:
            observation_start = st.date_input(
                "Observation start",
                value=pd.to_datetime("2020-01-01"),
            )

        series_id = FRED_SERIES[selected_name]

        try:
            fred_df = fetch_fred_series(
                series_id=series_id,
                api_key=fred_api_key,
                observation_start=str(observation_start),
            )

            if fred_df.empty:
                st.warning("FRED returned no observations.")
            else:
                latest_row = fred_df.iloc[-1]

                c1, c2, c3 = st.columns(3)
                c1.metric("Series", selected_name)
                c2.metric("Latest Value", round(float(latest_row["value"]), 4))
                c3.metric("Latest Date", str(latest_row["date"].date()))

                fig = px.line(
                    fred_df,
                    x="date",
                    y="value",
                    title=f"{selected_name} ({series_id})",
                )
                st.plotly_chart(fig, use_container_width=True)

                st.dataframe(fred_df.tail(20), use_container_width=True)

        except requests.HTTPError as e:
            st.error(f"FRED API HTTP error: {e}")
        except Exception as e:
            st.error(f"FRED API test failed: {e}")


with polymarket_tab:
    st.subheader("Polymarket Gamma API Test")

    col1, col2, col3 = st.columns([1.5, 1, 1])

    with col1:
        keyword = st.text_input("Search keyword", value="recession")

    with col2:
        limit = st.slider("Limit", min_value=5, max_value=100, value=25, step=5)

    with col3:
        api_mode = st.radio("Endpoint", ["events", "markets"], horizontal=True)

    st.write("Preset keywords:")
    preset_cols = st.columns(len(POLYMARKET_PRESETS))

    for i, preset in enumerate(POLYMARKET_PRESETS):
        with preset_cols[i]:
            if st.button(preset):
                keyword = preset

    try:
        if api_mode == "events":
            poly_df = fetch_polymarket_events(keyword=keyword, limit=limit)

            st.success(f"Polymarket events endpoint worked. Rows returned: {len(poly_df)}")

            if poly_df.empty:
                st.warning("No events found. Try another keyword.")
            else:
                useful_cols = [
                    "id",
                    "ticker",
                    "slug",
                    "title",
                    "description",
                    "category",
                    "active",
                    "closed",
                    "volume",
                    "liquidity",
                    "startDate",
                    "endDate",
                ]
                useful_cols = [c for c in useful_cols if c in poly_df.columns]

                st.dataframe(poly_df[useful_cols], use_container_width=True)

                with st.expander("Raw first event JSON"):
                    st.json(poly_df.iloc[0].to_dict())

        else:
            poly_df = fetch_polymarket_markets(keyword=keyword, limit=limit)

            st.success(f"Polymarket markets endpoint worked. Rows returned: {len(poly_df)}")

            if poly_df.empty:
                st.warning("No markets found. Try another keyword.")
            else:
                useful_cols = [
                    "id",
                    "question",
                    "category",
                    "volume",
                    "liquidity",
                    "endDate",
                    "active",
                    "closed",
                    "outcomes",
                    "outcomePrices",
                    "yes_probability",
                ]
                useful_cols = [c for c in useful_cols if c in poly_df.columns]

                st.dataframe(poly_df[useful_cols], use_container_width=True)

                if "yes_probability" in poly_df.columns:
                    prob_df = poly_df.dropna(subset=["yes_probability"]).copy()

                    if not prob_df.empty:
                        prob_df = prob_df.sort_values(
                            "yes_probability",
                            ascending=False,
                        ).head(10)

                        fig = px.bar(
                            prob_df,
                            x="yes_probability",
                            y="question",
                            orientation="h",
                            title=f"Top Yes Probabilities for '{keyword}'",
                        )
                        st.plotly_chart(fig, use_container_width=True)

                with st.expander("Raw first market JSON"):
                    st.json(poly_df.iloc[0].to_dict())

    except requests.HTTPError as e:
        st.error(f"Polymarket API HTTP error: {e}")
    except Exception as e:
        st.error(f"Polymarket API test failed: {e}")


with combined_tab:
    st.subheader("Simple Combined Signal View")

    st.caption(
        "This is only a quick proof-of-concept view. The enterprise version will normalize these into a formal signal schema."
    )

    fred_api_key = get_fred_api_key()

    if not fred_api_key:
        st.warning("FRED key is missing, so only Polymarket can be tested.")
    else:
        try:
            fred_test = fetch_fred_series(
                series_id="BAMLH0A0HYM2",
                api_key=fred_api_key,
                observation_start="2020-01-01",
            )

            latest_fred = fred_test.iloc[-1]

            fred_signal = {
                "source": "FRED",
                "signal_name": "HY Credit Spread",
                "signal_type": "macro_time_series",
                "latest_value": round(float(latest_fred["value"]), 4),
                "unit": "Percent",
                "latest_date": str(latest_fred["date"].date()),
                "risk_theme": "Credit Spread Risk",
            }

            poly_test = fetch_polymarket_markets(
                keyword="recession",
                limit=10,
            )

            poly_signal = {
                "source": "Polymarket",
                "signal_name": "Recession-related event markets",
                "signal_type": "prediction_event",
                "latest_value": None,
                "unit": "Probability",
                "latest_date": pd.Timestamp.today().date().isoformat(),
                "risk_theme": "Credit / Macro Risk",
            }

            if not poly_test.empty and "yes_probability" in poly_test.columns:
                prob_df = poly_test.dropna(subset=["yes_probability"])
                if not prob_df.empty:
                    top = prob_df.sort_values("yes_probability", ascending=False).iloc[0]
                    poly_signal["signal_name"] = top.get("question", poly_signal["signal_name"])
                    poly_signal["latest_value"] = round(float(top["yes_probability"]), 4)

            combined_df = pd.DataFrame([fred_signal, poly_signal])
            st.dataframe(combined_df, use_container_width=True)

        except Exception as e:
            st.error(f"Combined signal test failed: {e}")