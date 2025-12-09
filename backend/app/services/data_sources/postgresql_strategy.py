import pandas as pd
from typing import Dict, Any
from .base import DataSourceStrategy

try:
    import psycopg2
    import psycopg2.extras
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False
    psycopg2 = None


class PostgreSQLStrategy(DataSourceStrategy):
    """Strategy for PostgreSQL database data sources"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.connection = None

    def connect(self) -> None:
        """Establish PostgreSQL connection"""
        if not POSTGRESQL_AVAILABLE:
            raise Exception("PostgreSQL connector not available. Please install psycopg2.")

        try:
            self.connection = psycopg2.connect(
                host=self.config.get('host', 'localhost'),
                port=self.config.get('port', 5432),
                user=self.config.get('user'),
                password=self.config.get('password'),
                database=self.config.get('database'),
                cursor_factory=psycopg2.extras.RealDictCursor
            )
            self.connection.autocommit = True
        except Exception as e:
            raise Exception(f"Failed to connect to PostgreSQL: {str(e)}")

    def get_schema(self) -> Dict[str, Any]:
        """Return schema information for PostgreSQL database"""
        if not self.connection:
            self.connect()

        cursor = self.connection.cursor()
        schema = {
            'columns': [],
            'row_count': 0,
            'database_type': 'postgresql'
        }

        try:
            # Get tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            """)
            tables = cursor.fetchall()
            
            if tables:
                # Get schema from first table for now
                table_name = tables[0][0]
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = %s AND table_schema = 'public'
                """, (table_name,))
                columns = cursor.fetchall()
                
                schema['row_count'] = self._get_table_row_count(cursor, table_name)
                
                for col in columns:
                    col_info = {
                        'name': col[0],
                        'type': col[1],
                        'nullable': col[2] == 'YES',
                        'default': col[3]
                    }
                    schema['columns'].append(col_info)
        except Exception as e:
            raise Exception(f"Failed to get PostgreSQL schema: {str(e)}")
        finally:
            cursor.close()

        return schema

    def get_data(self, query: str = None, limit: int = None) -> pd.DataFrame:
        """Get data from PostgreSQL"""
        if not self.connection:
            self.connect()

        cursor = self.connection.cursor()
        
        try:
            if query:
                sql_query = query
            else:
                # Default query - get first table data
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                    LIMIT 1
                """)
                result = cursor.fetchone()
                if result:
                    table_name = result[0]
                    sql_query = f"SELECT * FROM {table_name}"
                else:
                    return pd.DataFrame()

            if limit:
                sql_query += f" LIMIT {limit}"

            cursor.execute(sql_query)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            # Convert to DataFrame
            if rows:
                df = pd.DataFrame(rows, columns=columns)
            else:
                df = pd.DataFrame()
            
            return df
        except Exception as e:
            raise Exception(f"Failed to query PostgreSQL: {str(e)}")
        finally:
            cursor.close()

    def disconnect(self) -> None:
        """Close PostgreSQL connection"""
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