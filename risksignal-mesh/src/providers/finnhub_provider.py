import pandas as pd

from src.providers.base import BaseSignalProvider


class FinnhubProvider(BaseSignalProvider):
    provider_name = "Finnhub"

    def fetch(self, *args, **kwargs) -> pd.DataFrame:
        raise NotImplementedError("Finnhub provider will be implemented in Phase 3.")

    def normalize(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError("Finnhub normalization will be implemented in Phase 3.")

