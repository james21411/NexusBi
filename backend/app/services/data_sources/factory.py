from typing import Dict, Any

from .base import DataSourceStrategy
from .csv_strategy import CSVStrategy
from .excel_strategy import ExcelStrategy
from .json_strategy import JSONStrategy
from .txt_strategy import TXTStrategy

# Optional imports for database connectors
try:
    from .mysql_strategy import MySQLStrategy
    MYSQL_STRATEGY_AVAILABLE = True
except ImportError:
    MYSQL_STRATEGY_AVAILABLE = False
    MySQLStrategy = None

try:
    from .postgresql_strategy import PostgreSQLStrategy
    POSTGRESQL_STRATEGY_AVAILABLE = True
except ImportError:
    POSTGRESQL_STRATEGY_AVAILABLE = False
    PostgreSQLStrategy = None


class DataSourceFactory:
    """Factory for creating data source strategies"""

    @staticmethod
    def get_source(source_type: str, config: Dict[str, Any]) -> DataSourceStrategy:
        """Create appropriate data source strategy based on type"""
        if source_type.lower() == "csv":
            return CSVStrategy(config)
        elif source_type.lower() == "excel":
            return ExcelStrategy(config)
        elif source_type.lower() == "json":
            return JSONStrategy(config)
        elif source_type.lower() == "txt":
            return TXTStrategy(config)
        elif source_type.lower() == "mysql":
            if not MYSQL_STRATEGY_AVAILABLE:
                raise NotImplementedError("MySQL strategy not available. Please install mysql-connector-python.")
            return MySQLStrategy(config)
        elif source_type.lower() == "postgresql":
            if not POSTGRESQL_STRATEGY_AVAILABLE:
                raise NotImplementedError("PostgreSQL strategy not available. Please install psycopg2.")
            return PostgreSQLStrategy(config)
        elif source_type.lower() == "sql_dump":
            # TODO: Implement SQLDumpStrategy
            raise NotImplementedError("SQL dump strategy not implemented yet")
        elif source_type.lower() == "mongodb":
            # TODO: Implement MongoDBStrategy
            raise NotImplementedError("MongoDB strategy not implemented yet")
        elif source_type.lower() == "api":
            # TODO: Implement APIStrategy
            raise NotImplementedError("API strategy not implemented yet")
        elif source_type.lower() == "cloud":
            # TODO: Implement CloudStorageStrategy
            raise NotImplementedError("Cloud storage strategy not implemented yet")
        else:
            raise ValueError(f"Unsupported data source type: {source_type}")