import pandas as pd

from src.providers.base import BaseSignalProvider


class OECDProvider(BaseSignalProvider):
    provider_name = "OECD"

    def fetch(self, *args, **kwargs) -> pd.DataFrame:
        raise NotImplementedError("OECD provider will be implemented in Phase 3.")

    def normalize(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError("OECD normalization will be implemented in Phase 3.")

