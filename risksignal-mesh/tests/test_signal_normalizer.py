import pandas as pd

from src.services.signal_normalizer import (
    SIGNAL_COLUMNS,
    normalize_fred_signals,
    normalize_polymarket_signals,
)


def test_fred_raw_data_normalizes_into_expected_signal_schema():
    raw = pd.DataFrame(
        [
            {
                "date": "2024-01-01",
                "value": "3.0",
                "series_id": "BAMLH0A0HYM2",
                "display_name": "HY Credit Spread",
                "category": "Credit",
                "risk_theme": "Credit Spread Risk",
                "unit": "Percent",
                "frequency": "Daily",
                "description": "High yield spread",
            },
            {
                "date": "2024-02-01",
                "value": "4.0",
                "series_id": "BAMLH0A0HYM2",
                "display_name": "HY Credit Spread",
                "category": "Credit",
                "risk_theme": "Credit Spread Risk",
                "unit": "Percent",
                "frequency": "Daily",
                "description": "High yield spread",
            },
        ]
    )

    normalized = normalize_fred_signals(raw)

    assert set(SIGNAL_COLUMNS).issubset(normalized.columns)
    assert normalized.loc[0, "signal_name"] == "HY Credit Spread"
    assert normalized.loc[0, "signal_value"] == 4.0
    assert normalized.loc[0, "signal_type"] == "macro_time_series"


def test_polymarket_raw_data_normalizes_into_expected_signal_schema():
    raw = pd.DataFrame(
        [
            {
                "market_id": "m1",
                "question": "Will there be a US recession in 2026?",
                "category": "Economics",
                "outcomes": '["Yes", "No"]',
                "outcome_prices": '["0.38", "0.62"]',
                "volume": 1000,
                "liquidity": 500,
            }
        ]
    )

    normalized = normalize_polymarket_signals(raw)

    assert set(SIGNAL_COLUMNS).issubset(normalized.columns)
    assert normalized.loc[0, "signal_type"] == "prediction_event"
    assert normalized.loc[0, "signal_value"] == 0.38
    assert normalized.loc[0, "severity"] == "medium"


def test_missing_fields_do_not_crash_polymarket_normalization():
    normalized = normalize_polymarket_signals(pd.DataFrame([{}]))

    assert len(normalized) == 1
    assert normalized.loc[0, "signal_name"] == "Polymarket event"
    assert normalized.loc[0, "severity"] == "unknown"

