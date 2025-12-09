import pandas as pd
from typing import Dict, Any
from .base import DataSourceStrategy

try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    mysql = None


class MySQLStrategy(DataSourceStrategy):
    """Strategy for MySQL database data sources"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.connection = None

    def connect(self) -> None:
        """Establish MySQL connection"""
        if not MYSQL_AVAILABLE:
            raise Exception("MySQL connector not available. Please install mysql-connector-python.")

        try:
            self.connection = mysql.connector.connect(
                host=self.config.get('host', 'localhost'),
                port=self.config.get('port', 3306),
                user=self.config.get('user'),
                password=self.config.get('password'),
                database=self.config.get('database'),
                charset='utf8mb4',
                autocommit=True
            )
        except Exception as e:
            raise Exception(f"Failed to connect to MySQL: {str(e)}")

    def get_schema(self) -> Dict[str, Any]:
        """Return schema information for MySQL database"""
        if not self.connection:
            self.connect()

        cursor = self.connection.cursor()
        schema = {
            'columns': [],
            'row_count': 0,
            'database_type': 'mysql'
        }

        try:
            # Get tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            if tables:
                # Get schema from first table for now
                table_name = tables[0][0]
                cursor.execute(f"DESCRIBE {table_name}")
                columns = cursor.fetchall()
                
                schema['row_count'] = self._get_table_row_count(cursor, table_name)
                
                for col in columns:
                    col_info = {
                        'name': col[0],
                        'type': col[1],
                        'nullable': col[2] == 'YES',
                        'key': col[3],
                        'default': col[4],
                        'extra': col[5]
                    }
                    schema['columns'].append(col_info)
        except Exception as e:
            raise Exception(f"Failed to get MySQL schema: {str(e)}")
        finally:
            cursor.close()

        return schema

    def get_data(self, query: str = None, limit: int = None) -> pd.DataFrame:
        """Get data from MySQL"""
        if not self.connection:
            self.connect()

        cursor = self.connection.cursor(dictionary=True)
        
        try:
            if query:
                sql_query = query
            else:
                # Default query - get first table data
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                if tables:
                    table_name = tables[0][0]
                    sql_query = f"SELECT * FROM {table_name}"
                else:
                    return pd.DataFrame()

            if limit:
                sql_query += f" LIMIT {limit}"

            cursor.execute(sql_query)
            rows = cursor.fetchall()
            
            # Convert to DataFrame
            if rows:
                df = pd.DataFrame(rows)
            else:
                df = pd.DataFrame()
            
            return df
        except Exception as e:
            raise Exception(f"Failed to query MySQL: {str(e)}")
        finally:
            cursor.close()

    def disconnect(self) -> None:
        """Close MySQL connection"""
        if self.connection:
            self.connection.close()
            self.connection = None

    def _get_table_row_count(self, cursor, table_name: str) -> int:
        """Get row count for a table"""
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            return cursor.fetchone()[0]
        except:
            return 0