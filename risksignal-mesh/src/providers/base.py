from abc import ABC, abstractmethod

import pandas as pd


class BaseSignalProvider(ABC):
    provider_name: str

    @abstractmethod
    def fetch(self, *args, **kwargs) -> pd.DataFrame:
        pass

    @abstractmethod
    def normalize(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        pass

