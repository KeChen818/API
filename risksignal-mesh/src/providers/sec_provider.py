import pandas as pd

from src.providers.base import BaseSignalProvider


class SECProvider(BaseSignalProvider):
    provider_name = "SEC EDGAR"

    def fetch(self, *args, **kwargs) -> pd.DataFrame:
        raise NotImplementedError("SEC EDGAR provider will be implemented in Phase 2.")

    def normalize(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError("SEC EDGAR normalization will be implemented in Phase 2.")

