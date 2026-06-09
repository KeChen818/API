from src.services.severity_scoring import classify_percentile, classify_polymarket_probability


def test_low_percentile_returns_low():
    assert classify_percentile(59.9) == "low"


def test_medium_percentile_returns_medium():
    assert classify_percentile(60) == "medium"


def test_high_percentile_returns_high():
    assert classify_percentile(85) == "high"


def test_polymarket_probability_below_025_returns_low():
    assert classify_polymarket_probability(0.24) == "low"


def test_polymarket_probability_above_050_returns_high():
    assert classify_polymarket_probability(0.51) == "high"

