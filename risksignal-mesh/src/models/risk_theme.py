from typing import Optional

from pydantic import BaseModel


class RiskTheme(BaseModel):
    risk_theme: str
    risk_category: str
    description: str
    fred_series_keywords: Optional[str] = None
    polymarket_keywords: Optional[str] = None

