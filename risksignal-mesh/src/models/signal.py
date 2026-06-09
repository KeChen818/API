from datetime import date
from typing import Optional

from pydantic import BaseModel


class RiskSignal(BaseModel):
    date: date
    source: str
    signal_name: str
    signal_type: str
    signal_value: Optional[float] = None
    signal_text: Optional[str] = None
    unit: Optional[str] = None
    direction: Optional[str] = None
    severity: str = "low"
    related_risk_theme: Optional[str] = None
    evidence_text: Optional[str] = None
    url: Optional[str] = None

