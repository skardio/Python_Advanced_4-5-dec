"""
Table reader client for SCD2 Delta table operations.
"""
from typing import Optional, List, Dict
from pyspark.sql import DataFrame

from common.protocols import SparkDriverProtocol, CatalogServiceProtocol, QueryServiceProtocol


class TableReaderClient:
    """Client for reading SCD2 snapshots from Delta tables."""
    
    def __init__(
        self,
        catalog_service: CatalogServiceProtocol,
        query_service: QueryServiceProtocol,
        spark_driver: SparkDriverProtocol,
        **kwargs
    ):
        """
        Initialize table reader client.
        
        Args:
            catalog_service: Catalog service implementation
            query_service: Query service implementation  
            spark_driver: Spark driver implementation
            **kwargs: Additional parameters
        """
        self._catalog_service = catalog_service
        self._query_service = query_service
        self._spark_driver = spark_driver
    
    def read_snapshot_scd2(
        self,
        dlk_layer: str,
        table_name: str,
        snapshot_dt: Optional[str] = None,
        view_name: Optional[str] = None,
        include_scd2_cols: bool = False,
        **kwargs
    ) -> DataFrame:
        """
        Read SCD2 snapshot from Delta table.
        
        Args:
            dlk_layer: Data lake layer (bronze, silver, gold)
            table_name: Table name
            snapshot_dt: Snapshot datetime (ISO format) or None for latest
            view_name: Optional temporary view name to create
            include_scd2_cols: Include SCD2 technical columns in output
            **kwargs: Additional parameters
            
        Returns:
            PySpark DataFrame with snapshot data
            
        Raises:
            ValueError: If table not found or not SCD2 table
        """
        # Build catalog name
        catalog_name = self._catalog_service.build_catalog_name(dlk_layer, table_name)
        
        # Check if table exists
        if not self._catalog_service.is_in_catalog(catalog_name):
            raise ValueError(f"Table {catalog_name} not found in catalog")
        
        # Get table columns
        columns = self._catalog_service.get_table_columns(catalog_name)
        
        # Verify it's an SCD2 table
        if not self._catalog_service.is_scd2_table(columns):
            scd2_cols = self._catalog_service.get_scd2_columns(columns)
            available_cols = [col['name'] for col in columns]
            raise ValueError(
                f"Table {catalog_name} does not appear to be an SCD2 table. "
                f"Expected SCD2 columns like valid_from, valid_to, is_current, etc. "
                f"Found SCD2 columns: {scd2_cols}. Available columns: {available_cols}"
            )
        
        # Get relevant columns to select
        selected_columns = self._catalog_service.get_business_columns(
            columns, include_scd2_cols=include_scd2_cols
        )
        
        if not selected_columns:
            raise ValueError(f"No columns selected for table {catalog_name}")
        
        # Build and execute query
        query = self._query_service.build_snapshot_scd2_query(
            catalog_name, snapshot_dt, selected_columns
        )
        
        # Execute query
        df = self._query_service.run_query(query)
        
        # Create temporary view if requested
        if view_name:
            self._spark_driver.create_or_replace_temp_view(df, view_name)
        
        return df
    
    def get_table_info(self, dlk_layer: str, table_name: str) -> Dict:
        """
        Get information about a table.
        
        Args:
            dlk_layer: Data lake layer
            table_name: Table name
            
        Returns:
            Dictionary with table information
        """
        catalog_name = self._catalog_service.build_catalog_name(dlk_layer, table_name)
        
        if not self._catalog_service.is_in_catalog(catalog_name):
            return {
                'exists': False,
                'catalog_name': catalog_name,
                'error': f"Table {catalog_name} not found"
            }
        
        columns = self._catalog_service.get_table_columns(catalog_name)
        is_scd2 = self._catalog_service.is_scd2_table(columns)
        scd2_columns = self._catalog_service.get_scd2_columns(columns)
        business_columns = self._catalog_service.get_business_columns(columns, include_scd2_cols=False)
        all_business_columns = self._catalog_service.get_business_columns(columns, include_scd2_cols=True)
        
        return {
            'exists': True,
            'catalog_name': catalog_name,
            'is_scd2_table': is_scd2,
            'total_columns': len(columns),
            'all_columns': [col['name'] for col in columns],
            'scd2_columns': scd2_columns,
            'business_columns': business_columns,
            'business_columns_with_scd2': all_business_columns,
            'column_details': columns
        }
    
    def sample_data(self, dlk_layer: str, table_name: str, limit: int = 10) -> DataFrame:
        """
        Get sample data from table.
        
        Args:
            dlk_layer: Data lake layer
            table_name: Table name
            limit: Number of rows to sample
            
        Returns:
            PySpark DataFrame with sample data
        """
        catalog_name = self._catalog_service.build_catalog_name(dlk_layer, table_name)
        
        if not self._catalog_service.is_in_catalog(catalog_name):
            raise ValueError(f"Table {catalog_name} not found in catalog")
        
        query = self._query_service.build_sample_query(catalog_name, limit)
        return self._query_service.run_query(query)