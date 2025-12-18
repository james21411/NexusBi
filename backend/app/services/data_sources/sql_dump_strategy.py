import re
import pandas as pd
from typing import Dict, Any, List
from .base import DataSourceStrategy

try:
    import chardet
    HAS_CHARDET = True
except ImportError:
    HAS_CHARDET = False


class SQLDumpStrategy(DataSourceStrategy):
    """Strategy for SQL dump file data sources"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.file_path = config.get('file_path')
        self.encoding = config.get('encoding', 'utf-8')
        self.tables_info = []
        self.sample_data = {}
        self.schema_info = {}

    def connect(self) -> None:
        """Load and parse SQL dump file"""
        try:
            # Try auto-detection or fallback encodings
            encodings_to_try = []
            
            if self.encoding == 'utf-8':
                if HAS_CHARDET:
                    # Use chardet if available
                    with open(self.file_path, 'rb') as file:
                        raw_data = file.read()
                    
                    detected = chardet.detect(raw_data)
                    detected_encoding = detected['encoding'] or 'utf-8'
                    encodings_to_try.append(detected_encoding)
                    print(f"🔍 Auto-detected encoding: {detected_encoding} (confidence: {detected.get('confidence', 0):.2f})")
                else:
                    # Fallback: try UTF-16 first (common for SQL dumps)
                    print(f"🔍 chardet not available, trying common encodings...")
                    encodings_to_try = ['utf-16', 'utf-8', 'latin1']
            else:
                encodings_to_try = [self.encoding]
            
            content = None
            successful_encoding = None
            
            # Try each encoding until one works
            for encoding in encodings_to_try:
                try:
                    with open(self.file_path, 'r', encoding=encoding) as file:
                        content = file.read()
                    
                    successful_encoding = encoding
                    print(f"✅ Successfully read file with encoding: {encoding}")
                    break
                    
                except (UnicodeDecodeError, UnicodeError) as e:
                    print(f"⚠️  Failed with encoding {encoding}: {str(e)[:100]}")
                    continue
                except Exception as e:
                    print(f"❌ Unexpected error with encoding {encoding}: {str(e)[:100]}")
                    continue
            
            if content is None:
                raise Exception(f"Could not decode file with any encoding. Tried: {encodings_to_try}")
            
            self.encoding = successful_encoding
            self._parse_sql_dump(content)
            
        except Exception as e:
            raise Exception(f"Failed to load SQL dump file: {str(e)}")

    def _parse_sql_dump(self, content: str) -> None:
        """Parse SQL dump content to extract schema and sample data"""
        
        # Remove comments and split into statements
        lines = content.split('\n')
        clean_lines = []
        
        for line in lines:
            # Remove SQL comments
            line = line.strip()
            if line.startswith('--') or line.startswith('/*') or line.startswith('*'):
                continue
            if line and not line.startswith('LOCK TABLES') and not line.startswith('UNLOCK TABLES'):
                clean_lines.append(line)
        
        sql_content = ' '.join(clean_lines)
        
        # Extract CREATE TABLE statements
        self._extract_create_tables(sql_content)
        
        # Extract INSERT statements for sample data
        self._extract_insert_statements(sql_content)
        
        # Generate schema info
        self._generate_schema_info()

    def _extract_create_tables(self, content: str) -> None:
        """Extract CREATE TABLE statements"""
        
        # Pattern to match CREATE TABLE statements
        create_table_pattern = r'CREATE TABLE\s+`?(\w+)`?\s*\((.*?)\);'
        
        matches = re.findall(create_table_pattern, content, re.IGNORECASE | re.DOTALL)
        
        for table_name, columns_def in matches:
            columns = self._parse_columns(columns_def)
            
            table_info = {
                'name': table_name,
                'columns': columns,
                'row_count': 0  # Will be updated from INSERT statements
            }
            
            self.tables_info.append(table_info)

    def _parse_columns(self, columns_def: str) -> List[Dict[str, Any]]:
        """Parse column definitions from CREATE TABLE"""
        columns = []
        
        # Split by comma but be careful with nested parentheses
        column_defs = self._split_sql_columns(columns_def)
        
        for col_def in column_defs:
            col_def = col_def.strip()
            if not col_def:
                continue
                
            # Parse column name and type
            parts = col_def.split()
            if len(parts) >= 2:
                col_name = parts[0].strip('`"')
                col_type = ' '.join(parts[1:]).split('(')[0].upper()
                
                # Determine pandas dtype
                pd_dtype = self._map_sql_type_to_pandas(col_type)
                
                column_info = {
                    'name': col_name,
                    'type': col_type,
                    'pandas_dtype': pd_dtype,
                    'nullable': 'NOT NULL' not in col_def.upper(),
                    'primary_key': 'PRIMARY KEY' in col_def.upper(),
                    'auto_increment': 'AUTO_INCREMENT' in col_def.upper() or 'SERIAL' in col_def.upper()
                }
                
                columns.append(column_info)
        
        return columns

    def _split_sql_columns(self, columns_def: str) -> List[str]:
        """Split column definitions handling nested parentheses"""
        columns = []
        current_col = ''
        paren_count = 0
        
        for char in columns_def:
            if char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
            elif char == ',' and paren_count == 0:
                columns.append(current_col)
                current_col = ''
                continue
            
            current_col += char
        
        if current_col.strip():
            columns.append(current_col)
        
        return columns

    def _map_sql_type_to_pandas(self, sql_type: str) -> str:
        """Map SQL types to pandas dtypes"""
        sql_type = sql_type.upper()
        
        if any(t in sql_type for t in ['INT', 'BIGINT', 'SMALLINT', 'TINYINT']):
            return 'int64'
        elif any(t in sql_type for t in ['DECIMAL', 'NUMERIC', 'FLOAT', 'DOUBLE', 'REAL']):
            return 'float64'
        elif any(t in sql_type for t in ['BOOL', 'BOOLEAN']):
            return 'bool'
        elif any(t in sql_type for t in ['DATE', 'TIME', 'DATETIME', 'TIMESTAMP']):
            return 'datetime64'
        else:
            return 'object'  # Default for strings and unknown types

    def _extract_insert_statements(self, content: str) -> None:
        """Extract INSERT statements to get sample data"""
        
        # Pattern to match INSERT statements - handle both forms:
        # 1. INSERT INTO table (columns) VALUES (...)
        # 2. INSERT INTO table VALUES (...)
        insert_pattern = r'INSERT INTO\s+`?(\w+)`?\s*(?:\((.*?)\))?\s*VALUES\s*(.*?);'
        
        matches = re.findall(insert_pattern, content, re.IGNORECASE | re.DOTALL)
        
        print(f"🔍 Found {len(matches)} INSERT statements")
        
        for table_name, columns_str, values_str in matches:
            # Parse column names if provided
            if columns_str:
                columns = [col.strip('`"') for col in columns_str.split(',')]
            else:
                columns = []  # Will be inferred from first row
            
            # Parse values - handle different value formats
            values_list = self._parse_insert_values(values_str)
            
            if values_list:
                # Convert to DataFrame - include ALL data from file
                df_data = []
                for values in values_list:  # Process ALL rows, not just first 10
                    if len(values) >= 1:  # At least one value
                        if not columns:
                            # Infer column names from row length
                            columns = [f'col_{i+1}' for i in range(len(values))]
                        
                        if len(values) == len(columns):
                            row_dict = dict(zip(columns, values))
                            df_data.append(row_dict)
                
                if df_data:
                    df = pd.DataFrame(df_data)
                    
                    # Update table row count
                    for table in self.tables_info:
                        if table['name'] == table_name:
                            table['row_count'] = len(values_list)
                            break
                    
                    self.sample_data[table_name] = df
                    print(f"✅ Extracted {len(df_data)} rows from table {table_name}")

    def _parse_insert_values(self, values_str: str) -> List[List[str]]:
        """Parse VALUES clause from INSERT statement"""
        values_list = []
        rows = []
        current_row = []
        current_value = ''
        in_string = False
        string_char = None
        paren_count = 0
        
        i = 0
        while i < len(values_str):
            char = values_str[i]
            
            if not in_string:
                if char in ["'", '"']:
                    in_string = True
                    string_char = char
                    current_value += char
                elif char == '(':
                    paren_count += 1
                    if paren_count == 1:
                        current_value = ''
                    else:
                        current_value += char
                elif char == ')':
                    paren_count -= 1
                    current_value += char
                    if paren_count == 0:
                        # End of row
                        row_values = self._parse_row_values([current_value.strip('()')])
                        rows.append(row_values)
                elif char == ',' and paren_count == 0:
                    # This might be a separator between rows or values
                    # We need to be more careful here
                    pass
                else:
                    current_value += char
            else:
                if char == string_char:
                    # Check if it's escaped
                    if i + 1 < len(values_str) and values_str[i + 1] == string_char:
                        current_value += char + char
                        i += 1  # Skip next char
                    else:
                        in_string = False
                        string_char = None
                        current_value += char
                else:
                    current_value += char
            
            i += 1
        
        # If no complex parsing worked, try a simpler approach
        if not rows:
            # Try to split by rows using regex or simple string methods
            try:
                # Split by closing and opening parentheses that represent new rows
                row_pattern = r'\([^)]+\)'
                matches = re.findall(row_pattern, values_str)
                for match in matches:
                    # Remove parentheses and split by comma
                    values = match.strip('()').split(',')
                    row_values = []
                    for val in values:
                        val = val.strip()
                        if val.upper() == 'NULL':
                            row_values.append(None)
                        elif (val.startswith("'") and val.endswith("'")) or \
                             (val.startswith('"') and val.endswith('"')):
                            row_values.append(val[1:-1])
                        else:
                            row_values.append(val)
                    rows.append(row_values)
            except Exception as e:
                print(f"⚠️  Failed to parse INSERT values with simple method: {e}")
                # Return empty list as fallback
                return []
        
        return rows

    def _parse_row_values(self, values: List[str]) -> List[str]:
        """Parse individual values from a row"""
        parsed_values = []
        
        for value in values:
            value = value.strip()
            if not value:
                parsed_values.append(None)
                continue
            
            # Remove quotes if present
            if (value.startswith("'") and value.endswith("'")) or \
               (value.startswith('"') and value.endswith('"')):
                value = value[1:-1]
            
            # Handle NULL values
            if value.upper() == 'NULL':
                parsed_values.append(None)
            else:
                parsed_values.append(value)
        
        return parsed_values

    def _generate_schema_info(self) -> None:
        """Generate comprehensive schema information"""
        
        self.schema_info = {
            'file_type': 'sql_dump',
            'encoding': self.encoding,
            'tables': []
        }
        
        for table in self.tables_info:
            table_schema = {
                'name': table['name'],
                'columns': table['columns'],
                'row_count': table['row_count'],
                'sample_data_available': table['name'] in self.sample_data
            }
            
            self.schema_info['tables'].append(table_schema)

    def get_schema(self) -> Dict[str, Any]:
        """Return schema information for SQL dump"""
        if not hasattr(self, 'schema_info') or not self.schema_info:
            self.connect()

        return self.schema_info

    def get_data(self, query: str = None, limit: int = None) -> pd.DataFrame:
        """Get all data from SQL dump, combined from all tables"""
        if not hasattr(self, 'sample_data') or not self.sample_data:
            self.connect()

        # Combine all tables into a single DataFrame with table identification
        if self.sample_data:
            all_dataframes = []
            
            for table_name, table_df in self.sample_data.items():
                # Add table name column to identify source
                table_df_with_source = table_df.copy()
                table_df_with_source.insert(0, '_source_table', table_name)
                all_dataframes.append(table_df_with_source)
            
            if all_dataframes:
                # Concatenate all dataframes
                combined_df = pd.concat(all_dataframes, ignore_index=True, sort=False)
                
                if limit:
                    combined_df = combined_df.head(limit)
                
                return combined_df
        
        # Return empty DataFrame if no sample data
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
        if not hasattr(self, 'tables_info') or not self.tables_info:
            self.connect()
        
        return [table['name'] for table in self.tables_info]

    def disconnect(self) -> None:
        """Clean up - nothing to do for SQL dump"""
        if hasattr(self, 'sample_data'):
            for table_name, df in self.sample_data.items():
                del df
            del self.sample_data
        
        if hasattr(self, 'tables_info'):
            del self.tables_info
        
        if hasattr(self, 'schema_info'):
            del self.schema_info