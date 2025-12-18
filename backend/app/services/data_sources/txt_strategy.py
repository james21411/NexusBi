import re
import pandas as pd
import chardet
from typing import Dict, Any, List, Optional
from .base import DataSourceStrategy


class TXTStrategy(DataSourceStrategy):
    """Strategy for TXT file data sources with automatic detection"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.file_path = config.get('file_path')
        self.encoding = config.get('encoding', 'utf-8')
        self.separator = config.get('separator')
        self.has_header = config.get('has_header', True)
        self.sample_data = {}
        self.schema_info = {}

    def connect(self) -> None:
        """Load and parse TXT file with automatic detection"""
        try:
            # Auto-detect encoding if not specified
            if self.encoding == 'utf-8':
                with open(self.file_path, 'rb') as file:
                    raw_data = file.read()
                
                # Detect encoding
                detected = chardet.detect(raw_data)
                detected_encoding = detected['encoding'] or 'utf-8'
                
                # Try common encodings for text files
                encodings_to_try = [detected_encoding, 'utf-8', 'latin1', 'cp1252', 'iso-8859-1']
                
                content = None
                successful_encoding = None
                
                for encoding in encodings_to_try:
                    try:
                        with open(self.file_path, 'r', encoding=encoding) as file:
                            content = file.read()
                        successful_encoding = encoding
                        print(f"✅ Successfully read TXT file with encoding: {encoding}")
                        break
                    except (UnicodeDecodeError, UnicodeError):
                        continue
                
                if content is None:
                    raise Exception(f"Could not decode TXT file with any encoding. Tried: {encodings_to_try}")
                
                self.encoding = successful_encoding
            else:
                # Use specified encoding
                with open(self.file_path, 'r', encoding=self.encoding) as file:
                    content = file.read()
            
            self._parse_txt_content(content)
            
        except Exception as e:
            raise Exception(f"Failed to load TXT file: {str(e)}")

    def _parse_txt_content(self, content: str) -> None:
        """Parse TXT content with automatic separator detection"""
        
        # Auto-detect separator if not specified
        if not self.separator:
            self.separator = self._detect_separator(content)
            print(f"🔍 Auto-detected separator: '{self.separator}'")
        
        # Split content into lines
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        if not lines:
            raise Exception("No data found in TXT file")
        
        # Detect if first row is header
        if self.has_header is None:
            self.has_header = self._detect_header(lines)
            print(f"🔍 Auto-detected header: {self.has_header}")
        
        # Parse data
        data_rows = []
        headers = []
        
        if self.has_header:
            headers = self._parse_line(lines[0])
            data_lines = lines[1:]
        else:
            # Generate column names
            first_row = self._parse_line(lines[0])
            headers = [f'col_{i+1}' for i in range(len(first_row))]
            data_lines = lines
        
        # Parse data rows
        for line in data_lines:
            values = self._parse_line(line)
            if len(values) == len(headers):
                row_dict = dict(zip(headers, values))
                data_rows.append(row_dict)
            elif values:  # Skip empty or malformed rows
                # Pad or trim to match header count
                if len(values) < len(headers):
                    values.extend([''] * (len(headers) - len(values)))
                else:
                    values = values[:len(headers)]
                row_dict = dict(zip(headers, values))
                data_rows.append(row_dict)
        
        # Create DataFrame
        if data_rows:
            df = pd.DataFrame(data_rows)
            
            # Auto-detect data types
            df = self._auto_detect_types(df)
            
            self.sample_data['txt_data'] = df
            
            # Generate schema info
            self._generate_schema_info(headers, len(data_rows))
            
            print(f"✅ Parsed {len(data_rows)} rows with {len(headers)} columns")
        else:
            raise Exception("No valid data rows found")

    def _detect_separator(self, content: str) -> str:
        """Auto-detect the separator used in the TXT file"""
        
        # Common separators to test
        separators = [',', ';', '\t', '|', ' ']
        
        lines = [line.strip() for line in content.split('\n') if line.strip()][:10]  # Test first 10 lines
        
        best_separator = ','
        best_score = 0
        
        for sep in separators:
            scores = []
            for line in lines:
                # Count separator occurrences
                count = line.count(sep)
                # Check if separator creates consistent column count
                parts = line.split(sep)
                if len(parts) > 1:
                    scores.append(len(parts))
            
            if scores:
                # Calculate consistency score
                consistency = len(set(scores))
                avg_columns = sum(scores) / len(scores)
                score = avg_columns - consistency  # Higher score = more consistent
                
                if score > best_score:
                    best_score = score
                    best_separator = sep
        
        return best_separator

    def _detect_header(self, lines: List[str]) -> bool:
        """Auto-detect if first row is header"""
        if len(lines) < 2:
            return True
        
        first_row = self._parse_line(lines[0])
        second_row = self._parse_line(lines[1])
        
        # Heuristic: if first row has fewer numeric values than second row, it's likely a header
        first_numeric = sum(1 for val in first_row if self._is_numeric(val))
        second_numeric = sum(1 for val in second_row if self._is_numeric(val))
        
        # If second row has significantly more numeric values, first row is likely header
        return second_numeric > first_numeric

    def _parse_line(self, line: str) -> List[str]:
        """Parse a single line with the detected separator"""
        return [field.strip() for field in line.split(self.separator)]

    def _is_numeric(self, value: str) -> bool:
        """Check if a value is numeric"""
        if not value or value.lower() in ['null', 'none', 'nan', '']:
            return False
        try:
            float(value.replace(',', ''))  # Handle comma decimals
            return True
        except ValueError:
            return False

    def _auto_detect_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Auto-detect pandas dtypes for columns"""
        
        for col in df.columns:
            # Sample values to determine type
            sample_values = df[col].dropna().head(100).astype(str)
            
            # Check for numeric values
            numeric_count = sum(1 for val in sample_values if self._is_numeric(val))
            total_count = len(sample_values)
            
            if total_count > 0:
                numeric_ratio = numeric_count / total_count
                
                if numeric_ratio > 0.8:  # 80% numeric values
                    # Try to convert to numeric
                    try:
                        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')
                    except:
                        pass  # Keep as object if conversion fails
                elif numeric_ratio > 0.6:  # 60% numeric, might be mixed
                    # Keep as object for now
                    pass
            
            # Check for datetime patterns
            datetime_count = 0
            for val in sample_values.head(20):
                if self._is_datetime(val):
                    datetime_count += 1
            
            if datetime_count > 10:  # More than half look like dates
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                except:
                    pass
        
        return df

    def _is_datetime(self, value: str) -> bool:
        """Check if a value looks like a datetime"""
        if not value:
            return False
        
        # Common datetime patterns
        datetime_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
            r'\d{4}/\d{2}/\d{2}',  # YYYY/MM/DD
            r'\d{2}:\d{2}:\d{2}',  # HH:MM:SS
        ]
        
        for pattern in datetime_patterns:
            if re.search(pattern, value):
                return True
        
        return False

    def _generate_schema_info(self, headers: List[str], row_count: int) -> None:
        """Generate comprehensive schema information"""
        
        columns_info = []
        for i, header in enumerate(headers):
            column_info = {
                'name': header,
                'type': 'object',  # Will be updated based on actual data
                'pandas_dtype': 'object',
                'nullable': True,
                'primary_key': False,
                'auto_increment': False
            }
            columns_info.append(column_info)
        
        self.schema_info = {
            'file_type': 'txt',
            'encoding': self.encoding,
            'separator': self.separator,
            'has_header': self.has_header,
            'tables': [{
                'name': 'txt_data',
                'columns': columns_info,
                'row_count': row_count,
                'sample_data_available': True
            }]
        }

    def get_schema(self) -> Dict[str, Any]:
        """Return schema information for TXT file"""
        if not hasattr(self, 'schema_info') or not self.schema_info:
            self.connect()

        return self.schema_info

    def get_data(self, query: str = None, limit: int = None) -> pd.DataFrame:
        """Get data from TXT file"""
        if not hasattr(self, 'sample_data') or not self.sample_data:
            self.connect()

        if 'txt_data' in self.sample_data:
            df = self.sample_data['txt_data'].copy()
            if limit:
                df = df.head(limit)
            return df
        
        return pd.DataFrame()

    def get_all_table_data(self, limit: int = None) -> Dict[str, pd.DataFrame]:
        """Get data from all tables as a dictionary"""
        if not hasattr(self, 'sample_data') or not self.sample_data:
            self.connect()

        result = {}
        for table_name, table_df in self.sample_data.items():
            if limit:
                result[table_name] = table_df.head(limit)
            else:
                result[table_name] = table_df.copy()
        
        return result

    def get_table_data(self, table_name: str, limit: int = None) -> pd.DataFrame:
        """Get data from specific table"""
        if table_name in self.sample_data:
            df = self.sample_data[table_name].copy()
            if limit:
                df = df.head(limit)
            return df
        
        return pd.DataFrame()

    def get_all_tables(self) -> List[str]:
        """Get list of all table names"""
        if not hasattr(self, 'sample_data') or not self.sample_data:
            self.connect()
        
        return list(self.sample_data.keys())

    def disconnect(self) -> None:
        """Clean up - nothing to do for TXT files"""
        if hasattr(self, 'sample_data'):
            for table_name, df in self.sample_data.items():
                del df
            del self.sample_data
        
        if hasattr(self, 'schema_info'):
            del self.schema_info