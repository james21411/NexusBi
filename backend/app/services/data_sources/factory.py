from typing import Dict, Any

from .base import DataSourceStrategy
from .csv_strategy import CSVStrategy


class DataSourceFactory:
    """Factory for creating data source strategies"""

    @staticmethod
    def get_source(source_type: str, config: Dict[str, Any]) -> DataSourceStrategy:
        """Create appropriate data source strategy based on type"""
        if source_type.lower() == "csv":
            return CSVStrategy(config)
        elif source_type.lower() == "excel":
            # TODO: Implement ExcelStrategy
            raise NotImplementedError("Excel strategy not implemented yet")
        elif source_type.lower() == "mysql":
            # TODO: Implement MySQLStrategy
            raise NotImplementedError("MySQL strategy not implemented yet")
        elif source_type.lower() == "postgresql":
            # TODO: Implement PostgreSQLStrategy
            raise NotImplementedError("PostgreSQL strategy not implemented yet")
        elif source_type.lower() == "sql_dump":
            # TODO: Implement SQLDumpStrategy
            raise NotImplementedError("SQL dump strategy not implemented yet")
        else:
            raise ValueError(f"Unsupported data source type: {source_type}")