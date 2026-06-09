from src.providers.polymarket_provider import PolymarketProvider


def test_fetch_events_uses_public_search_events_and_respects_limit(monkeypatch):
    provider = PolymarketProvider()

    def fake_public_search(keyword, limit=50, active=True, closed=False):
        assert keyword == "recession"
        assert limit == 1
        assert active is True
        assert closed is False
        return {
            "events": [
                {
                    "id": "event-1",
                    "slug": "us-recession-2026",
                    "title": "US recession in 2026?",
                    "category": "Economics",
                    "volume": "1000",
                    "liquidity": "250",
                    "endDate": "2026-12-31T00:00:00Z",
                    "markets": [
                        {
                            "id": "market-1",
                            "question": "US recession in 2026?",
                            "outcomes": '["Yes", "No"]',
                            "outcomePrices": '["0.38", "0.62"]',
                        },
                        {
                            "id": "market-2",
                            "question": "Second recession market",
                            "outcomes": '["Yes", "No"]',
                            "outcomePrices": '["0.45", "0.55"]',
                        },
                    ],
                }
            ],
            "markets": [],
        }

    monkeypatch.setattr(provider, "_public_search", fake_public_search)
    df = provider.fetch_events("recession", limit=1)

    assert len(df) == 1
    assert df.loc[0, "question"] == "US recession in 2026?"
    assert df.loc[0, "implied_probability"] == 0.38
    assert df.loc[0, "event_title"] == "US recession in 2026?"


def test_public_search_status_params(monkeypatch):
    provider = PolymarketProvider()
    captured = {}

    def fake_request_json(endpoint, params):
        captured["endpoint"] = endpoint
        captured["params"] = params
        return {"events": [], "markets": []}

    monkeypatch.setattr(provider, "_request_json", fake_request_json)
    provider._public_search("inflation", limit=5, active=True, closed=False)

    assert captured["endpoint"] == "public-search"
    assert captured["params"]["q"] == "inflation"
    assert captured["params"]["limit_per_type"] == 5
    assert captured["params"]["events_status"] == "active"


def test_fetch_events_filters_unrelated_public_search_rows(monkeypatch):
    provider = PolymarketProvider()

    def fake_public_search(keyword, limit=50, active=True, closed=False):
        return {
            "events": [
                {
                    "id": "event-1",
                    "slug": "japan-recession-2026",
                    "title": "Japan recession in 2026?",
                    "markets": [
                        {
                            "id": "market-1",
                            "question": "Japan recession in 2026?",
                            "outcomes": '["Yes", "No"]',
                            "outcomePrices": '["0.30", "0.70"]',
                        }
                    ],
                },
                {
                    "id": "event-2",
                    "slug": "warsh-press-conference",
                    "title": "What will Kevin Warsh say during June Press Conference?",
                    "markets": [
                        {
                            "id": "market-2",
                            "question": 'Will Warsh say "Rate" or "Cut" during June Press Conference?',
                            "outcomes": '["Yes", "No"]',
                            "outcomePrices": '["0.67", "0.33"]',
                        }
                    ],
                },
            ],
            "markets": [],
        }

    monkeypatch.setattr(provider, "_public_search", fake_public_search)
    df = provider.fetch_events("recession", limit=10)

    assert len(df) == 1
    assert df.loc[0, "question"] == "Japan recession in 2026?"
