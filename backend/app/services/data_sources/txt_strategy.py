import pandas as pd
import csv
from typing import Dict, Any
from .base import DataSourceStrategy


class TXTStrategy(DataSourceStrategy):
    """Strategy for TXT file data sources"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.df = None
        self.delimiter = config.get('delimiter', '\t')  # Default to tab-separated
        self.has_header = config.get('has_header', True)

    def connect(self) -> None:
        """Load TXT file into memory"""
        try:
            file_path = self.config['file_path']
            
            # Try to detect delimiter if not specified
            if self.delimiter is None:
                self.delimiter = self._detect_delimiter(file_path)
            
            # Read the file
            self.df = pd.read_csv(
                file_path, 
                delimiter=self.delimiter,
                header=0 if self.has_header else None,
                encoding='utf-8'
            )
            
        except UnicodeDecodeError:
            # Try with different encodings
            try:
                self.df = pd.read_csv(
                    file_path, 
                    delimiter=self.delimiter,
                    header=0 if self.has_header else None,
                    encoding='latin-1'
                )
            except Exception as e:
                raise Exception(f"Failed to load TXT file with latin-1 encoding: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to load TXT file: {str(e)}")

    def get_schema(self) -> Dict[str, Any]:
        """Return schema information for TXT file"""
        if self.df is None:
            self.connect()

        schema = {
            'columns': [],
            'row_count': len(self.df),
            'file_type': 'txt',
            'delimiter': self.delimiter
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
        """Get data from TXT file"""
        if self.df is None:
            self.connect()

        df = self.df.copy()

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
        """Clean up - nothing to do for TXT"""
        if self.df is not None:
            del self.df
            self.df = None

    def _detect_delimiter(self, file_path: str) -> str:
        """Auto-detect delimiter by analyzing the file"""
        delimiters = ['\t', ',', ';', '|']
        
        with open(file_path, 'r', encoding='utf-8') as f:
            # Read first few lines
            lines = [f.readline() for _ in range(5)]
        
        delimiter_counts = {}
        for delimiter in delimiters:
            counts = []
            for line in lines:
                if line.strip():
                    counts.append(line.count(delimiter))
            
            # Use delimiter with most consistent counts
            if counts:
                delimiter_counts[delimiter] = max(counts) if max(counts) > 0 else 0
        
        # Return delimiter with highest count, default to tab
        if delimiter_counts:
            return max(delimiter_counts, key=delimiter_counts.get)
        
        return '\t'