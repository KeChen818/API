"""Template-based risk profile narratives."""

from __future__ import annotations

import pandas as pd

from src.services.severity_scoring import highest_severity


def _theme_frame(mapped_signals_df: pd.DataFrame, selected_risk_theme: str) -> pd.DataFrame:
    if mapped_signals_df is None or mapped_signals_df.empty:
        return pd.DataFrame()
    return mapped_signals_df[
        mapped_signals_df["related_risk_theme"].fillna("") == selected_risk_theme
    ].copy()


def _profile_word(severity: str) -> str:
    return {
        "high": "highly elevated",
        "medium": "moderately elevated",
        "low": "contained",
        "unknown": "uncertain",
    }.get(severity, "uncertain")


def _supporting_bullets(theme_df: pd.DataFrame) -> list[str]:
    bullets: list[str] = []
    if theme_df.empty:
        return ["No mapped external signals are available for this theme yet."]

    for _, row in theme_df.head(6).iterrows():
        value = row.get("signal_value")
        unit = row.get("unit") or ""
        if pd.notna(value):
            if unit == "probability":
                value_text = f"{float(value):.0%}"
            else:
                value_text = f"{float(value):,.2f}".rstrip("0").rstrip(".")
        else:
            value_text = "n/a"
        bullets.append(
            f"{row.get('source', 'Signal')}: {row.get('signal_name', 'Unnamed signal')} "
            f"({row.get('severity', 'unknown')} severity, {value_text} {unit}).".strip()
        )
    return bullets


def generate_risk_profile_summary(
    mapped_signals_df: pd.DataFrame,
    selected_risk_theme: str,
) -> str:
    """Generate a deterministic CRO-style narrative for one risk theme."""
    theme_df = _theme_frame(mapped_signals_df, selected_risk_theme)
    severity = highest_severity(theme_df["severity"]) if not theme_df.empty else "unknown"
    profile_word = _profile_word(severity)
    macro_count = int((theme_df.get("source", pd.Series(dtype=str)) == "FRED").sum()) if not theme_df.empty else 0
    event_count = int((theme_df.get("source", pd.Series(dtype=str)) == "Polymarket").sum()) if not theme_df.empty else 0

    if theme_df.empty:
        changed = "- No mapped FRED or Polymarket signals are currently available for this theme."
        matters = "- The theme should remain in the taxonomy, but current external evidence is insufficient for a directional view."
    else:
        changed = (
            f"- {macro_count} macro signal(s) and {event_count} event probability signal(s) "
            f"are mapped to this theme.\n"
            f"- The highest mapped severity is {severity}."
        )
        matters = (
            "- External signals can indicate emerging pressure before it appears in internal loss or issue data.\n"
            "- Persistent medium or high readings should be reviewed alongside portfolio exposure, controls, and recent management commentary."
        )

    supporting = "\n".join(f"- {bullet}" for bullet in _supporting_bullets(theme_df))

    return f"""Current Risk Profile: {selected_risk_theme}

{selected_risk_theme} appears {profile_word} based on the currently mapped FRED and Polymarket signals.

What changed:
{changed}

Why it matters:
{matters}

Key supporting signals:
{supporting}

Suggested management attention:
- Review internal exposures, limits, and recent risk inventory entries linked to this theme.
- Monitor whether medium or high severity signals persist across the next reporting cycle.
- Include this theme in the next risk identification workshop if external evidence continues to build.

Data caveats:
- FRED data may be delayed, revised, or subject to reporting frequency differences.
- Polymarket probabilities are market-implied event signals and should not be treated as official forecasts.
- Severity scores are transparent heuristic scores for demo purposes and should not be treated as validated risk models.
"""


def generate_llm_risk_profile_summary_placeholder(*args: object, **kwargs: object) -> str:
    """Placeholder for a future LLM-backed narrative generator."""
    raise NotImplementedError("LLM-generated risk profiles are planned for a future phase.")

