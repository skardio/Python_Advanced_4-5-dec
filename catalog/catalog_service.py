"""
Catalog service for SCD2 Delta table operations.
"""
from typing import List, Dict, Set
from common.protocols import SparkDriverProtocol


class CatalogService:
    """Service for catalog operations."""
    
    # Standard SCD2 technical columns
    SCD2_TECHNICAL_COLUMNS = {
        'valid_from', 'valid_to', 'is_current', 'created_at', 'updated_at',
        'load_date', 'effective_date', 'end_date', 'current_flag',
        'version', 'record_version', 'scd_start_date', 'scd_end_date'
    }
    
    # Hash key patterns (case insensitive)
    HASH_KEY_PATTERNS = {'hash_key', 'hk_', '_hk', 'hashkey', 'dim_hash_key'}
    
    def __init__(self, spark_driver: SparkDriverProtocol, **kwargs):
        """
        Initialize catalog service.
        
        Args:
            spark_driver: Spark driver implementation
            **kwargs: Additional parameters
        """
        self._spark_driver = spark_driver
    
    def build_catalog_name(self, dlk_layer: str, table_name: str) -> str:
        """
        Build catalog name from layer and table name.
        
        Args:
            dlk_layer: Data lake layer (bronze, silver, gold)
            table_name: Table name
            
        Returns:
            Full catalog name in format layer.table_name
        """
        layer = dlk_layer.lower()
        if layer not in ['bronze', 'silver', 'gold']:
            raise ValueError(f"Invalid data lake layer: {dlk_layer}. Must be 'bronze', 'silver', or 'gold'")
        
        return f"{layer}.{table_name}"
    
    def is_in_catalog(self, catalog_name: str) -> bool:
        """
        Check if table exists in catalog.
        
        Args:
            catalog_name: Full catalog name
            
        Returns:
            True if table exists, False otherwise
        """
        return self._spark_driver.table_exists(catalog_name)
    
    def get_table_columns(self, catalog_name: str) -> List[Dict[str, str]]:
        """
        Get table columns metadata.
        
        Args:
            catalog_name: Full catalog name
            
        Returns:
            List of column metadata
            
        Raises:
            ValueError: If table doesn't exist
        """
        if not self.is_in_catalog(catalog_name):
            raise ValueError(f"Table {catalog_name} not found in catalog")
        
        return self._spark_driver.get_table_columns(catalog_name)
    
    def is_scd2_table(self, columns: List[Dict[str, str]]) -> bool:
        """
        Check if table has SCD2 structure.
        
        Args:
            columns: List of column metadata
            
        Returns:
            True if table appears to be SCD2, False otherwise
        """
        column_names = {col['name'].lower() for col in columns}
        
        # Check for at least some SCD2 technical columns
        scd2_cols_found = column_names.intersection(self.SCD2_TECHNICAL_COLUMNS)
        
        # We need at least 2 SCD2 columns to consider it an SCD2 table
        # Common combinations: valid_from + valid_to, or is_current + valid_from, etc.
        return len(scd2_cols_found) >= 2
    
    def get_business_columns(self, columns: List[Dict[str, str]], include_scd2_cols: bool = False) -> List[str]:
        """
        Get relevant columns based on business rules.
        
        Args:
            columns: List of column metadata
            include_scd2_cols: Whether to include SCD2 technical columns
            
        Returns:
            List of column names to include in output
        """
        business_columns = []
        
        for col in columns:
            col_name = col['name']
            col_name_lower = col_name.lower()
            
            # Always include hash keys (needed for relationships)
            is_hash_key = any(pattern in col_name_lower for pattern in self.HASH_KEY_PATTERNS)
            
            # Check if it's a technical SCD2 column
            is_scd2_technical = col_name_lower in self.SCD2_TECHNICAL_COLUMNS
            
            # Include column if:
            # 1. It's a hash key (always needed for relationships)
            # 2. It's not an SCD2 technical column (business column)
            # 3. It's an SCD2 technical column and user wants them included
            if is_hash_key or not is_scd2_technical or (is_scd2_technical and include_scd2_cols):
                business_columns.append(col_name)
        
        return business_columns
    
    def get_scd2_columns(self, columns: List[Dict[str, str]]) -> List[str]:
        """
        Get SCD2 technical columns from table.
        
        Args:
            columns: List of column metadata
            
        Returns:
            List of SCD2 technical column names
        """
        scd2_columns = []
        
        for col in columns:
            col_name = col['name']
            col_name_lower = col_name.lower()
            
            if col_name_lower in self.SCD2_TECHNICAL_COLUMNS:
                scd2_columns.append(col_name)
        
        return scd2_columns