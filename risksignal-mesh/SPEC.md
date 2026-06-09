# RiskSignal Mesh Specification

## 1. Product Summary

RiskSignal Mesh is an enterprise-style Streamlit demo that maps external signals to risk taxonomy themes. The MVP focuses on two external providers:

- FRED Macro API for macroeconomic and market stress indicators
- Polymarket Gamma API for event probabilities and prediction-market signals

The goal is to create a risk intelligence layer that normalizes signals, scores severity, maps evidence to risk themes, and generates deterministic management narratives.

## 2. Users

Primary users:

- Enterprise risk identification teams
- CRO staff
- Risk taxonomy owners
- Committee reporting teams

Secondary users:

- Business risk officers
- Portfolio risk analysts
- Internal audit or control reviewers evaluating signal coverage

## 3. MVP Scope

### In Scope

- FRED macro signal monitor
- Polymarket event signal monitor
- Unified signal schema
- Transparent severity scoring
- Config-driven risk theme mapping
- Deterministic risk profile summaries
- Streamlit enterprise demo UI
- Configurable FRED API key through Streamlit secrets or `.env`
- Extensible provider interface
- Placeholder providers for future phases
- Unit tests for transformation and mapping logic

### Out Of Scope

- Authentication
- Database persistence
- Enterprise deployment
- User management
- Full LLM integration
- Internal document upload
- Meeting minutes ingestion
- Yahoo Finance, SEC EDGAR, Finnhub, OECD, or news provider implementation

## 4. Functional Requirements

### Executive Overview

The app must show:

- App title and subtitle
- Count of loaded FRED signals
- Count of loaded Polymarket event signals
- Count of mapped risk themes
- Highest severity theme
- Theme severity table
- Theme severity heatmap
- Short executive summary
- Data caveats

### FRED Macro Signals

The app must allow users to:

- Select multiple configured FRED series
- Choose an observation start date
- Refresh cached FRED data
- Filter results by risk theme
- View selected series in a Plotly line chart
- View latest-value metric cards
- View percentile, direction, severity, and normalized signal tables

### Polymarket Event Signals

The app must allow users to:

- Search by keyword
- Use preset keywords such as recession, inflation, Fed rates, banking crisis, oil, election, and commercial real estate
- Choose a result limit
- Include active and closed filters
- View event and market metadata
- View top events by volume
- View top events by implied probability
- View event-to-risk-theme mappings

The provider should prefer Gamma public search and then apply local keyword relevance filtering before showing results.

### Risk Theme Mapping

The app must provide a unified table with:

- Date
- Source
- Signal name
- Signal type
- Signal value
- Unit
- Direction
- Severity
- Related risk theme
- Evidence text

Users must be able to filter by:

- Risk theme
- Source
- Severity

Users must be able to download the mapped signal table as CSV.

### Risk Profile Summary

The app must generate a deterministic template-based summary for a selected theme. It must include:

- Current Risk Profile
- What changed
- Why it matters
- Key supporting signals
- Suggested management attention
- Data caveats

No LLM call is required for the MVP.

## 5. Data Model

### Unified Signal Schema

```text
date
source
signal_name
signal_type
signal_value
signal_text
unit
direction
severity
related_risk_theme
evidence_text
url
```

### RiskSignal

Implemented in [src/models/signal.py](./src/models/signal.py).

Required behavior:

- Accept numeric or text-based signals
- Preserve source and signal type
- Carry a severity, direction, related theme, evidence text, and optional URL

### EventMarket

Implemented in [src/models/event_market.py](./src/models/event_market.py).

Required behavior:

- Store Polymarket market or event metadata
- Preserve outcomes and outcome prices
- Store parsed implied probability when available

## 6. Provider Architecture

All providers inherit from `BaseSignalProvider` in [src/providers/base.py](./src/providers/base.py).

Required methods:

```python
def fetch(self, *args, **kwargs) -> pd.DataFrame:
    ...

def normalize(self, raw_df: pd.DataFrame) -> pd.DataFrame:
    ...
```

Implemented providers:

- `FredProvider`
- `PolymarketProvider`

Placeholder providers:

- `YahooProvider`
- `SECProvider`
- `FinnhubProvider`
- `OECDProvider`

## 7. FRED Provider

Implemented in [src/providers/fred_provider.py](./src/providers/fred_provider.py).

Requirements:

- Accept an API key
- Fetch observations from `fred/series/observations`
- Support `observation_start`
- Convert values to numeric
- Drop missing observations
- Join configured metadata from [src/data/fred_series_config.csv](./src/data/fred_series_config.csv)
- Return friendly error messages instead of crashing the app

Key loading order:

1. Streamlit secrets
2. Environment variable
3. UI warning

## 8. Polymarket Provider

Implemented in [src/providers/polymarket_provider.py](./src/providers/polymarket_provider.py).

Requirements:

- Use Gamma API without authentication
- Prefer `/public-search` with keyword parameter `q`
- Return event-level and market-level metadata
- Parse outcomes and outcome prices
- Extract a Yes-side implied probability where possible
- Handle malformed outcome prices
- Apply local keyword relevance filtering
- Return friendly errors on timeout, response errors, or malformed payloads

## 9. Severity Scoring

Implemented in [src/services/severity_scoring.py](./src/services/severity_scoring.py).

### FRED

For each selected series, calculate:

- Latest value
- Prior 30-day or prior available value
- Change
- Percentile rank over selected window

Severity:

```text
low: percentile < 60
medium: percentile >= 60 and < 85
high: percentile >= 85
```

Direction:

- Credit spreads, financial stress, unemployment, CPI: higher is worsening
- Rates: higher is tightening
- Values below median: easing or improving

### Polymarket

Use implied probability when available.

Severity:

```text
low: probability < 0.25
medium: probability >= 0.25 and < 0.50
high: probability >= 0.50
unknown: probability unavailable
```

Direction:

```text
elevated: probability >= 0.25
contained: probability < 0.25
unknown: probability unavailable
```

## 10. Risk Mapping

Implemented in [src/services/risk_mapping.py](./src/services/risk_mapping.py).

Mapping inputs:

- Normalized signals dataframe
- Risk theme config dataframe

FRED mapping:

- Match `signal_name`, `display_name`, `series_id`, `signal_text`, and `evidence_text`
- Use `fred_series_keywords`

Polymarket mapping:

- Match question, category, market title, event title, signal text, and evidence text
- Use `polymarket_keywords`

Fallback:

```text
Unmapped / Emerging Risk
```

## 11. Narrative Generator

Implemented in [src/services/narrative_generator.py](./src/services/narrative_generator.py).

The MVP uses deterministic templates. A placeholder exists for future LLM-generated summaries.

## 12. UI Specification

The Streamlit app uses:

```python
st.set_page_config(page_title="RiskSignal Mesh", layout="wide")
```

Tabs:

1. Executive Overview
2. FRED Macro Signals
3. Polymarket Event Signals
4. Risk Theme Mapping
5. Risk Profile Summary
6. Architecture / Roadmap

UI principles:

- Enterprise-style layout
- Clear controls and table views
- Grey and red visual theme modes
- Embedded Apache ECharts visuals for table-adjacent summaries
- No hardcoded API keys
- Cached API calls
- Friendly errors
- Data caveats visible in the app

## 13. Testing

Current test areas:

- FRED normalization
- Polymarket normalization
- Severity scoring
- Risk mapping
- Overview heatmap shaping
- Polymarket provider public search behavior

Run:

```bash
python -m pytest -q -p no:capture tests
```

## 14. Acceptance Criteria

The MVP is complete when:

- `streamlit run app.py` starts successfully
- FRED series can be selected and charted when `FRED_API_KEY` is configured
- Polymarket events can be searched by keyword
- FRED and Polymarket signals normalize into one table
- Signals map to configured risk themes
- Signals have severity and direction
- Users can generate a deterministic risk profile summary
- Missing API keys and failed API calls do not crash the app
- Mapped signals can be downloaded as CSV
- Future provider placeholders exist
- Unit tests pass

## 15. Future Roadmap

Phase 1: FRED + Polymarket MVP

Phase 2: Yahoo Finance + SEC EDGAR

Phase 3: Finnhub + OECD + News

Phase 4: Internal PDF and meeting minutes ingestion

Phase 5: LLM-generated CRO-ready risk profile

Phase 6: Enterprise deployment with database, auth, audit trail, and API services

## 16. Caveats

This demo is for risk intelligence prototyping and management discussion support only.

FRED data may be delayed, revised, or subject to reporting frequency differences.

Polymarket prices are market-implied event signals, not official forecasts or regulatory data.

Prediction market probabilities may be affected by liquidity, market structure, participant composition, and contract design.

Severity scores are transparent heuristic scores for demo purposes and should not be treated as validated risk models.

The application does not provide investment, trading, legal, or regulatory advice.
