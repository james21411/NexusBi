from abc import ABC, abstractmethod
from typing import Dict, Any
import pandas as pd


class DataSourceStrategy(ABC):
    """Abstract base class for data source strategies"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abstractmethod
    def connect(self) -> None:
        """Establish connection or load file"""
        pass

    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Return schema information (columns, types, etc.)"""
        pass

    @abstractmethod
    def get_data(self, query: str = None, limit: int = None) -> pd.DataFrame:
        """Get data as pandas DataFrame"""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Clean up connections"""
        pass