import pandas as pd
from typing import Dict, Any
from .base import DataSourceStrategy


class ExcelStrategy(DataSourceStrategy):
    """Strategy for Excel file data sources"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.excel_file = None

    def connect(self) -> None:
        """Load Excel file into memory"""
        try:
            file_path = self.config['file_path']
            # Try to read all sheets or specific sheet
            if 'sheet_name' in self.config:
                self.excel_file = pd.read_excel(file_path, sheet_name=self.config['sheet_name'])
            else:
                # Read first sheet by default
                self.excel_file = pd.read_excel(file_path, sheet_name=0)
        except Exception as e:
            raise Exception(f"Failed to load Excel file: {str(e)}")

    def get_schema(self) -> Dict[str, Any]:
        """Return schema information for Excel file"""
        if self.excel_file is None:
            self.connect()

        schema = {
            'columns': [],
            'row_count': len(self.excel_file),
            'file_type': 'excel'
        }

        for col in self.excel_file.columns:
            col_info = {
                'name': col,
                'type': str(self.excel_file[col].dtype),
                'nullable': self.excel_file[col].isnull().any(),
                'unique_count': self.excel_file[col].nunique()
            }
            schema['columns'].append(col_info)

        return schema

    def get_data(self, query: str = None, limit: int = None) -> pd.DataFrame:
        """Get data from Excel file"""
        if self.excel_file is None:
            self.connect()

        df = self.excel_file.copy()

        if query:
            # Simple query support
            try:
                df = df.query(query)
            except Exception:
                pass  # Ignore invalid queries for now

        if limit:
            df = df.head(limit)

        return df

    def disconnect(self) -> None:
        """Clean up - nothing to do for Excel"""
        if self.excel_file is not None:
            del self.excel_file
            self.excel_file = None