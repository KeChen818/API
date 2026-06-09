from typing import List, Optional

from pydantic import BaseModel


class EventMarket(BaseModel):
    market_id: str
    question: str
    category: Optional[str] = None
    volume: Optional[float] = None
    liquidity: Optional[float] = None
    end_date: Optional[str] = None
    outcomes: Optional[List[str]] = None
    outcome_prices: Optional[List[float]] = None
    implied_probability: Optional[float] = None
    url: Optional[str] = None

