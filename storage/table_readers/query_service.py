"""
Query service for SCD2 Delta table operations.
"""
from typing import List, Optional
from datetime import datetime
from pyspark.sql import DataFrame
from common.protocols import SparkDriverProtocol


class QueryService:
    """Service for building and executing SCD2 queries."""
    
    def __init__(self, spark_driver: SparkDriverProtocol, **kwargs):
        """
        Initialize query service.
        
        Args:
            spark_driver: Spark driver implementation
            **kwargs: Additional parameters
        """
        self._spark_driver = spark_driver
    
    def build_snapshot_scd2_query(
        self, 
        catalog_name: str, 
        snapshot_dt: Optional[str], 
        selected_cols: List[str]
    ) -> str:
        """
        Build SQL query for SCD2 snapshot.
        
        Args:
            catalog_name: Full catalog name
            snapshot_dt: Snapshot datetime (ISO format) or None for latest
            selected_cols: Columns to select
            
        Returns:
            SQL query string
        """
        columns_str = ", ".join([f"`{col}`" for col in selected_cols])
        
        if snapshot_dt is None:
            # Get most recent snapshot (current records)
            query = f"""
            SELECT {columns_str}
            FROM {catalog_name}
            WHERE is_current = true
            OR (is_current IS NULL AND valid_to IS NULL)
            OR (current_flag = 'Y')
            OR (current_flag = true)
            OR (valid_to = '9999-12-31' OR valid_to = '2099-12-31')
            """
        else:
            # Get snapshot at specific point in time
            # Convert snapshot_dt to proper timestamp format if needed
            snapshot_timestamp = self._normalize_timestamp(snapshot_dt)
            
            query = f"""
            SELECT {columns_str}
            FROM {catalog_name}
            WHERE (
                -- Standard SCD2 with valid_from/valid_to
                (valid_from <= '{snapshot_timestamp}' AND 
                 (valid_to > '{snapshot_timestamp}' OR valid_to IS NULL OR 
                  valid_to = '9999-12-31' OR valid_to = '2099-12-31'))
                OR
                -- Alternative SCD2 with effective_date/end_date
                (effective_date <= '{snapshot_timestamp}' AND 
                 (end_date > '{snapshot_timestamp}' OR end_date IS NULL OR 
                  end_date = '9999-12-31' OR end_date = '2099-12-31'))
                OR
                -- SCD2 with created_at/updated_at pattern
                (created_at <= '{snapshot_timestamp}' AND 
                 (updated_at > '{snapshot_timestamp}' OR updated_at IS NULL))
            )
            """
        
        return query.strip()
    
    def run_query(self, query: str) -> DataFrame:
        """
        Execute query and return DataFrame.
        
        Args:
            query: SQL query string
            
        Returns:
            PySpark DataFrame
        """
        return self._spark_driver.run_query(query)
    
    def _normalize_timestamp(self, timestamp_str: str) -> str:
        """
        Normalize timestamp string to standard format.
        
        Args:
            timestamp_str: Input timestamp string
            
        Returns:
            Normalized timestamp string
        """
        # Try to parse common timestamp formats
        formats_to_try = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%d',
        ]
        
        for fmt in formats_to_try:
            try:
                dt = datetime.strptime(timestamp_str, fmt)
                # Return in standard format for SQL
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                continue
        
        # If parsing fails, return as-is and let Spark handle it
        return timestamp_str
    
    def build_table_info_query(self, catalog_name: str) -> str:
        """
        Build query to get table information.
        
        Args:
            catalog_name: Full catalog name
            
        Returns:
            SQL query to describe table
        """
        return f"DESCRIBE TABLE {catalog_name}"
    
    def build_sample_query(self, catalog_name: str, limit: int = 10) -> str:
        """
        Build query to get sample data.
        
        Args:
            catalog_name: Full catalog name
            limit: Number of rows to sample
            
        Returns:
            SQL query to sample data
        """
        return f"SELECT * FROM {catalog_name} LIMIT {limit}"