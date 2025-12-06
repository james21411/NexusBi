import pandas as pd
from typing import Dict, Any

from .base import DataSourceStrategy


class CSVStrategy(DataSourceStrategy):
    """Strategy for CSV file data sources"""

    def connect(self) -> None:
        """Load CSV file into memory"""
        try:
            self.df = pd.read_csv(self.config['file_path'])
        except Exception as e:
            raise Exception(f"Failed to load CSV file: {str(e)}")

    def get_schema(self) -> Dict[str, Any]:
        """Return schema information for CSV"""
        if not hasattr(self, 'df'):
            self.connect()

        schema = {
            'columns': [],
            'row_count': len(self.df),
            'file_type': 'csv'
        }

        for col in self.df.columns:
            col_info = {
                'name': col,
                'type': str(self.df[col].dtype),
                'nullable': self.df[col].isnull().any(),
                'unique_count': self.df[col].nunique()
            }
            schema['columns'].append(col_info)

        return schema

    def get_data(self, query: str = None, limit: int = None) -> pd.DataFrame:
        """Get data from CSV"""
        if not hasattr(self, 'df'):
            self.connect()

        df = self.df.copy()

        if query:
            # Simple query support - could be enhanced
            try:
                df = df.query(query)
            except Exception:
                pass  # Ignore invalid queries for now

        if limit:
            df = df.head(limit)

        return df

    def disconnect(self) -> None:
        """Clean up - nothing to do for CSV"""
        if hasattr(self, 'df'):
            del self.df