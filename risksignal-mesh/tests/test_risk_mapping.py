import pandas as pd

from src.services.risk_mapping import UNMAPPED_THEME, map_signals_to_risk_themes


def risk_config() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "risk_theme": "Credit Spread Risk",
                "risk_category": "Credit Risk",
                "description": "Stress from widening credit spreads",
                "fred_series_keywords": "HY Credit Spread;IG Credit Spread",
                "polymarket_keywords": "recession;default;credit crisis",
            },
            {
                "risk_theme": "Interest Rate Risk",
                "risk_category": "Market Risk",
                "description": "Rate level volatility",
                "fred_series_keywords": "Fed Funds Rate;10Y Treasury;2Y Treasury",
                "polymarket_keywords": "Fed rates;interest rates;rate cuts",
            },
            {
                "risk_theme": "Inflation Risk",
                "risk_category": "Macro Risk",
                "description": "Inflation pressure",
                "fred_series_keywords": "CPI",
                "polymarket_keywords": "inflation;CPI",
            },
            {
                "risk_theme": "CRE Risk",
                "risk_category": "Credit Risk",
                "description": "Commercial real estate stress",
                "fred_series_keywords": "10Y Treasury;Unemployment Rate",
                "polymarket_keywords": "recession;commercial real estate;housing",
            },
        ]
    )


def map_one(signal: dict) -> str:
    mapped = map_signals_to_risk_themes(pd.DataFrame([signal]), risk_config())
    return mapped.loc[0, "related_risk_theme"]


def test_hy_credit_spread_maps_to_credit_spread_risk():
    assert map_one({"source": "FRED", "signal_name": "HY Credit Spread"}) == "Credit Spread Risk"


def test_fed_funds_rate_maps_to_interest_rate_risk():
    assert map_one({"source": "FRED", "signal_name": "Fed Funds Rate"}) == "Interest Rate Risk"


def test_cpi_maps_to_inflation_risk():
    assert map_one({"source": "FRED", "signal_name": "CPI"}) == "Inflation Risk"


def test_recession_keyword_maps_to_credit_or_cre_risk():
    mapped = map_one({"source": "Polymarket", "question": "Will the US enter a recession in 2026?"})
    assert mapped in {"Credit Spread Risk", "CRE Risk"}


def test_unknown_signal_maps_to_unmapped_emerging_risk():
    assert map_one({"source": "Polymarket", "question": "Unknown unrelated signal"}) == UNMAPPED_THEME

