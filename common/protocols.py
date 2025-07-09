"""
Protocols for dependency inversion in SCD2 Delta table reader.
"""
from typing import Protocol, List, Dict, Any, Optional
from pyspark.sql import DataFrame


class SparkDriverProtocol(Protocol):
    """Protocol for Spark operations."""
    
    def get_table_columns(self, catalog_name: str) -> List[Dict[str, str]]:
        """Get table columns from catalog."""
        ...
    
    def run_query(self, query: str) -> DataFrame:
        """Execute SQL query and return DataFrame."""
        ...
    
    def create_or_replace_temp_view(self, df: DataFrame, view_name: str) -> None:
        """Create or replace temporary view."""
        ...
    
    def table_exists(self, catalog_name: str) -> bool:
        """Check if table exists in catalog."""
        ...


class CatalogServiceProtocol(Protocol):
    """Protocol for catalog operations."""
    
    def build_catalog_name(self, dlk_layer: str, table_name: str) -> str:
        """Build catalog name from layer and table name."""
        ...
    
    def is_in_catalog(self, catalog_name: str) -> bool:
        """Check if table exists in catalog."""
        ...
    
    def get_table_columns(self, catalog_name: str) -> List[Dict[str, str]]:
        """Get table columns metadata."""
        ...
    
    def is_scd2_table(self, columns: List[Dict[str, str]]) -> bool:
        """Check if table has SCD2 structure."""
        ...
    
    def get_business_columns(self, columns: List[Dict[str, str]], include_scd2_cols: bool = False) -> List[str]:
        """Get relevant columns based on business rules."""
        ...


class QueryServiceProtocol(Protocol):
    """Protocol for query building and execution."""
    
    def build_snapshot_scd2_query(
        self, 
        catalog_name: str, 
        snapshot_dt: Optional[str], 
        selected_cols: List[str]
    ) -> str:
        """Build SQL query for SCD2 snapshot."""
        ...
    
    def run_query(self, query: str) -> DataFrame:
        """Execute query and return DataFrame."""
        ...


class TableReaderClientProtocol(Protocol):
    """Protocol for table reader client."""
    
    def read_snapshot_scd2(
        self,
        dlk_layer: str,
        table_name: str,
        snapshot_dt: Optional[str] = None,
        view_name: Optional[str] = None,
        include_scd2_cols: bool = False,
        **kwargs
    ) -> DataFrame:
        """Read SCD2 snapshot from Delta table."""
        ...