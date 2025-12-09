import pandas as pd
import json
from typing import Dict, Any
from .base import DataSourceStrategy


class JSONStrategy(DataSourceStrategy):
    """Strategy for JSON file data sources"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.json_data = None

    def connect(self) -> None:
        """Load JSON file into memory"""
        try:
            file_path = self.config['file_path']
            with open(file_path, 'r', encoding='utf-8') as f:
                self.json_data = json.load(f)
        except Exception as e:
            raise Exception(f"Failed to load JSON file: {str(e)}")

    def get_schema(self) -> Dict[str, Any]:
        """Return schema information for JSON file"""
        if self.json_data is None:
            self.connect()

        schema = {
            'columns': [],
            'row_count': 0,
            'file_type': 'json'
        }

        # Handle different JSON structures
        if isinstance(self.json_data, list):
            # Array of objects
            if len(self.json_data) > 0 and isinstance(self.json_data[0], dict):
                # Get all unique keys from all objects
                all_keys = set()
                for item in self.json_data[:100]:  # Sample first 100 items
                    if isinstance(item, dict):
                        all_keys.update(item.keys())
                
                for key in sorted(all_keys):
                    values = [item.get(key) for item in self.json_data if isinstance(item, dict) and key in item]
                    schema['columns'].append({
                        'name': key,
                        'type': self._infer_type(values),
                        'nullable': None in values,
                        'unique_count': len(set(values)) if values else 0
                    })
                
                schema['row_count'] = len(self.json_data)
            else:
                # Array of primitives
                schema['row_count'] = len(self.json_data)
                schema['columns'].append({
                    'name': 'value',
                    'type': self._infer_type(self.json_data),
                    'nullable': False,
                    'unique_count': len(set(str(v) for v in self.json_data))
                })
        
        elif isinstance(self.json_data, dict):
            # Object with key-value pairs
            for key, value in self.json_data.items():
                schema['columns'].append({
                    'name': key,
                    'type': self._infer_type([value]),
                    'nullable': value is None,
                    'unique_count': 1
                })
            schema['row_count'] = 1

        return schema

    def get_data(self, query: str = None, limit: int = None) -> pd.DataFrame:
        """Get data from JSON file"""
        if self.json_data is None:
            self.connect()

        df = None
        
        if isinstance(self.json_data, list):
            # Array of objects - convert to DataFrame
            if len(self.json_data) > 0 and isinstance(self.json_data[0], dict):
                df = pd.DataFrame(self.json_data)
            else:
                # Array of primitives
                df = pd.DataFrame({'value': self.json_data})
        
        elif isinstance(self.json_data, dict):
            # Object - convert to single-row DataFrame
            df = pd.DataFrame([self.json_data])
        
        if df is not None:
            if query:
                try:
                    df = df.query(query)
                except Exception:
                    pass  # Ignore invalid queries

            if limit:
                df = df.head(limit)
        
        return df if df is not None else pd.DataFrame()

    def disconnect(self) -> None:
        """Clean up - nothing to do for JSON"""
        if self.json_data is not None:
            del self.json_data
            self.json_data = None

    def _infer_type(self, values):
        """Infer data type from a list of values"""
        if not values:
            return 'object'
        
        # Remove None values for type inference
        non_null_values = [v for v in values if v is not None]
        
        if not non_null_values:
            return 'object'
        
        # Check if all values are the same type
        types = set(type(v).__name__ for v in non_null_values)
        
        if len(types) == 1:
            return types.pop()
        
        # Mixed types - return object
        return 'object'