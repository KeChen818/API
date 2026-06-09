"""Polymarket Gamma API provider."""

from __future__ import annotations

import re
from typing import Any

import pandas as pd
import requests

from src.providers.base import BaseSignalProvider
from src.services.signal_normalizer import (
    coerce_outcome_prices,
    coerce_outcomes,
    extract_implied_probability,
    normalize_polymarket_signals,
)
from src.services.severity_scoring import safe_float


class PolymarketProvider(BaseSignalProvider):
    provider_name = "Polymarket"

    BASE_URL = "https://gamma-api.polymarket.com"

    def __init__(self) -> None:
        self.last_error: str | None = None

    def fetch(self, *args: Any, **kwargs: Any) -> pd.DataFrame:
        return self.fetch_events(*args, **kwargs)

    def _request_json(self, endpoint: str, params: dict[str, Any]) -> Any:
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        try:
            response = requests.get(url, params=params, timeout=20)
            response.raise_for_status()
            return response.json()
        except requests.Timeout:
            self.last_error = "The Polymarket request timed out. Please try again."
            return None
        except requests.RequestException:
            self.last_error = "Polymarket data could not be loaded right now. Please try another keyword or try again later."
            return None
        except ValueError:
            self.last_error = "Polymarket returned an unexpected response format."
            return None

    def _request(self, endpoint: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        payload = self._request_json(endpoint, params)
        if payload is None:
            return []

        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        if isinstance(payload, dict):
            for key in ["data", "events", "markets"]:
                value = payload.get(key)
                if isinstance(value, list):
                    return [item for item in value if isinstance(item, dict)]
        return []

    @staticmethod
    def _bool_param(value: bool) -> str:
        return "true" if value else "false"

    @staticmethod
    def _events_status(active: bool, closed: bool) -> str | None:
        if active and not closed:
            return "active"
        if closed and not active:
            return "closed"
        return None

    @staticmethod
    def _polymarket_url(slug: Any, event_slug: Any = None) -> str | None:
        selected_slug = event_slug or slug
        if not selected_slug:
            return None
        return f"https://polymarket.com/event/{selected_slug}"

    @staticmethod
    def _search_terms(text: Any) -> list[str]:
        raw_terms = re.findall(r"[a-z0-9]+", str(text or "").lower())
        terms: list[str] = []
        for term in raw_terms:
            if term.endswith("ing") and len(term) > 5:
                term = term[:-3]
            elif term.endswith("s") and not term.endswith(("is", "ss")) and len(term) > 3:
                term = term[:-1]
            terms.append(term)
        return terms

    @classmethod
    def _matches_keyword(cls, row: dict[str, Any], keyword: str) -> bool:
        keyword_terms = cls._search_terms(keyword)
        if not keyword_terms:
            return True

        searchable_text = " ".join(
            str(row.get(column) or "")
            for column in [
                "question",
                "event_title",
                "market_title",
                "category",
                "event_description",
                "market_description",
            ]
        )
        searchable_terms = set(cls._search_terms(searchable_text))
        return all(term in searchable_terms for term in keyword_terms)

    def _market_row(
        self,
        market: dict[str, Any],
        event: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        event = event or {}
        outcomes = coerce_outcomes(market.get("outcomes"))
        prices = coerce_outcome_prices(market.get("outcomePrices", market.get("outcome_prices")))
        probability = extract_implied_probability(
            outcomes,
            prices,
            market.get("impliedProbability", market.get("implied_probability")),
        )
        question = (
            market.get("question")
            or market.get("title")
            or event.get("title")
            or event.get("question")
            or "Polymarket event"
        )
        event_slug = event.get("slug")
        market_slug = market.get("slug")

        return {
            "event_id": event.get("id"),
            "event_title": event.get("title") or event.get("question"),
            "event_description": event.get("description"),
            "market_id": str(market.get("id") or market.get("conditionId") or question),
            "market_title": market.get("title") or question,
            "market_description": market.get("description"),
            "question": question,
            "category": market.get("category") or event.get("category"),
            "volume": safe_float(market.get("volume", event.get("volume"))),
            "liquidity": safe_float(market.get("liquidity", event.get("liquidity"))),
            "end_date": market.get("endDate") or market.get("end_date") or event.get("endDate"),
            "outcomes": outcomes,
            "outcome_prices": prices,
            "implied_probability": probability,
            "url": self._polymarket_url(market_slug, event_slug),
            "source": self.provider_name,
        }

    def _event_row(self, event: dict[str, Any]) -> dict[str, Any]:
        title = event.get("title") or event.get("question") or "Polymarket event"
        outcomes = coerce_outcomes(event.get("outcomes"))
        prices = coerce_outcome_prices(event.get("outcomePrices", event.get("outcome_prices")))
        probability = extract_implied_probability(outcomes, prices, event.get("impliedProbability"))
        return {
            "event_id": event.get("id"),
            "event_title": title,
            "event_description": event.get("description"),
            "market_id": str(event.get("id") or title),
            "market_title": title,
            "market_description": None,
            "question": title,
            "category": event.get("category"),
            "volume": safe_float(event.get("volume")),
            "liquidity": safe_float(event.get("liquidity")),
            "end_date": event.get("endDate") or event.get("end_date"),
            "outcomes": outcomes,
            "outcome_prices": prices,
            "implied_probability": probability,
            "url": self._polymarket_url(event.get("slug")),
            "source": self.provider_name,
        }

    def _rows_from_events(
        self,
        events: list[dict[str, Any]],
        limit: int | None = None,
        keyword: str | None = None,
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for event in events:
            markets = event.get("markets")
            if isinstance(markets, list) and markets:
                rows.extend(self._market_row(market, event=event) for market in markets if isinstance(market, dict))
            else:
                rows.append(self._event_row(event))

        if keyword:
            rows = [row for row in rows if self._matches_keyword(row, keyword)]

        if limit is not None:
            return rows[:limit]
        return rows

    def _public_search(
        self,
        keyword: str,
        limit: int = 50,
        active: bool = True,
        closed: bool = False,
    ) -> dict[str, list[dict[str, Any]]]:
        params: dict[str, Any] = {
            "q": keyword,
            "limit_per_type": limit,
            "search_profiles": "false",
        }
        events_status = self._events_status(active, closed)
        if events_status:
            params["events_status"] = events_status

        payload = self._request_json("public-search", params)
        if not isinstance(payload, dict):
            return {"events": [], "markets": []}

        events = payload.get("events")
        markets = payload.get("markets")
        return {
            "events": [item for item in events if isinstance(item, dict)] if isinstance(events, list) else [],
            "markets": [item for item in markets if isinstance(item, dict)] if isinstance(markets, list) else [],
        }

    def fetch_markets(
        self,
        keyword: str,
        limit: int = 50,
        active: bool = True,
        closed: bool = False,
    ) -> pd.DataFrame:
        if not keyword.strip():
            self.last_error = "Please enter a Polymarket keyword."
            return pd.DataFrame()

        search_results = self._public_search(keyword, limit=limit, active=active, closed=closed)
        markets = [
            market
            for market in search_results["markets"]
            if self._matches_keyword(self._market_row(market), keyword)
        ]
        if not markets and not search_results["markets"]:
            params = {
                "limit": limit,
                "active": self._bool_param(active),
                "closed": self._bool_param(closed),
            }
            markets = self._request("markets", params)
        rows = [self._market_row(market) for market in markets]
        return pd.DataFrame(rows[:limit])

    def fetch_events(
        self,
        keyword: str,
        limit: int = 50,
        active: bool = True,
        closed: bool = False,
    ) -> pd.DataFrame:
        if not keyword.strip():
            self.last_error = "Please enter a Polymarket keyword."
            return pd.DataFrame()

        search_results = self._public_search(keyword, limit=limit, active=active, closed=closed)
        rows = self._rows_from_events(search_results["events"], limit=limit, keyword=keyword)

        if not rows and not search_results["events"]:
            params = {
                "limit": limit,
                "active": self._bool_param(active),
                "closed": self._bool_param(closed),
            }
            events = self._request("events", params)
            rows = self._rows_from_events(events, limit=limit, keyword=keyword)

        return pd.DataFrame(rows)

    def normalize(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        return normalize_polymarket_signals(raw_df)
