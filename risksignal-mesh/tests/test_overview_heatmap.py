import pandas as pd

from src.services.risk_mapping import theme_severity_summary


def test_overview_heatmap_melt_avoids_signal_count_collision():
    mapped = pd.DataFrame(
        [
            {"related_risk_theme": "Credit Spread Risk", "severity": "high", "signal_name": "HY Credit Spread"},
            {"related_risk_theme": "Credit Spread Risk", "severity": "medium", "signal_name": "Recession Event"},
        ]
    )
    summary = theme_severity_summary(mapped)

    chart_df = summary.melt(
        id_vars="related_risk_theme",
        value_vars=["high", "medium", "low", "unknown"],
        var_name="severity",
        value_name="severity_signal_count",
    )

    assert "signal_count" in summary.columns
    assert "severity_signal_count" in chart_df.columns
    assert chart_df["severity_signal_count"].sum() == 2

