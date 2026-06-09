import pandas as pd

from src.providers.base import BaseSignalProvider


class YahooProvider(BaseSignalProvider):
    provider_name = "Yahoo Finance"

    def fetch(self, *args, **kwargs) -> pd.DataFrame:
        raise NotImplementedError("Yahoo Finance provider will be implemented in Phase 2.")

    def normalize(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError("Yahoo Finance normalization will be implemented in Phase 2.")

