# RiskSignal Mesh

RiskSignal Mesh is a Streamlit enterprise demo for connecting external risk signals to an internal-style risk taxonomy. It combines FRED macro indicators and Polymarket event probabilities into one mapped signal layer, then generates deterministic CRO-style risk profile summaries.

Subtitle:

```text
A signal-driven layer connecting risk inventory, macro data, and event probabilities.
```

## Purpose

The application helps risk identification teams connect macro data, prediction-market events, risk themes, and evidence text in one workflow. It is designed as a prototype risk intelligence layer, not just a chart viewer.

## Business Use Case

RiskSignal Mesh supports enterprise risk management workflows such as:

- Monitoring macroeconomic pressure against risk taxonomy themes
- Tracking event probabilities from prediction markets
- Mapping external evidence to risk inventory themes
- Preparing CRO or committee-style discussion summaries
- Identifying themes that may need management attention

Example narrative style:

```text
Credit risk pressure appears moderately elevated due to widening high-yield spreads, higher-for-longer rates, and rising recession-related event probabilities.
```

## Architecture

```text
External Signal Providers
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
    `-- risk profile summary
```

See [SPEC.md](./SPEC.md) for the detailed product and technical specification.

## Data Sources

### FRED Macro API

Used for macroeconomic and market stress signals including:

- Fed funds rate
- Treasury rates
- Unemployment
- CPI
- High-yield and investment-grade credit spreads
- St. Louis Fed Financial Stress Index

FRED series are configured in [src/data/fred_series_config.csv](./src/data/fred_series_config.csv).

### Polymarket Gamma API

Used for event probability and prediction-market signals.

The app uses Polymarket Gamma public search for keyword-driven event discovery and does not require authentication for this MVP.

Risk theme keywords are configured in [src/data/risk_theme_config.csv](./src/data/risk_theme_config.csv).

## Setup

macOS and Linux:

```bash
cd risksignal-mesh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Windows:

```bash
cd risksignal-mesh
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Configuration

Copy the environment example:

```bash
cp .env.example .env
```

Then set:

```env
FRED_API_KEY=replace_with_your_fred_api_key
```

Alternatively, copy the Streamlit secrets example:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Then set:

```toml
FRED_API_KEY = "replace_with_your_fred_api_key"
```

The app loads the FRED key in this order:

1. `st.secrets["FRED_API_KEY"]`
2. Environment variable `FRED_API_KEY`
3. Warning in the Streamlit UI

If `.env` is changed while the app is running, restart Streamlit so the process loads the new value.

## Running The App

```bash
streamlit run app.py
```

The app opens with six tabs:

1. Executive Overview
2. FRED Macro Signals
3. Polymarket Event Signals
4. Risk Theme Mapping
5. Risk Profile Summary
6. Architecture / Roadmap

## Testing

Run:

```bash
python -m pytest -q -p no:capture tests
```

The `-p no:capture` flag avoids a local pytest capture/readline issue observed in this desktop environment. The application tests cover severity scoring, signal normalization, risk mapping, overview table shaping, and Polymarket provider behavior.

## Project Structure

```text
risksignal-mesh/
|-- app.py
|-- README.md
|-- SPEC.md
|-- requirements.txt
|-- .env.example
|-- .streamlit/
|   `-- secrets.toml.example
|-- src/
|   |-- config/
|   |-- data/
|   |-- models/
|   |-- providers/
|   |-- services/
|   `-- ui/
`-- tests/
```

## Roadmap

1. Phase 1: FRED + Polymarket MVP
2. Phase 2: Yahoo Finance + SEC EDGAR
3. Phase 3: Finnhub + OECD + News
4. Phase 4: Internal PDF and meeting minutes ingestion
5. Phase 5: LLM-generated CRO-ready risk profile
6. Phase 6: Enterprise deployment with database, auth, audit trail, and API services

## Caveats

This demo is for risk intelligence prototyping and management discussion support only.

FRED data may be delayed, revised, or subject to reporting frequency differences.

Polymarket prices are market-implied event signals, not official forecasts or regulatory data.

Prediction market probabilities may be affected by liquidity, market structure, participant composition, and contract design.

Severity scores are transparent heuristic scores for demo purposes and should not be treated as validated risk models.

The application does not provide investment, trading, legal, or regulatory advice.

