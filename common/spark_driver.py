"""
Spark driver for SCD2 Delta table operations.
"""
from typing import List, Dict, Any
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.utils import AnalysisException


class SparkDriver:
    """Driver for Spark/Databricks operations."""
    
    def __init__(self, spark_session: SparkSession = None, **kwargs):
        """
        Initialize Spark driver.
        
        Args:
            spark_session: Optional existing Spark session
            **kwargs: Additional parameters for configuration
        """
        self._spark = spark_session or SparkSession.getActiveSession()
        if self._spark is None:
            self._spark = SparkSession.builder.appName("SCD2TableReader").getOrCreate()
    
    def get_table_columns(self, catalog_name: str) -> List[Dict[str, str]]:
        """
        Get table columns from catalog.
        
        Args:
            catalog_name: Full table name (catalog.schema.table)
            
        Returns:
            List of column metadata dictionaries
            
        Raises:
            ValueError: If table doesn't exist
        """
        try:
            # Get table schema
            df = self._spark.table(catalog_name)
            columns = []
            
            for field in df.schema:
                columns.append({
                    'name': field.name,
                    'type': str(field.dataType),
                    'nullable': field.nullable
                })
            
            return columns
            
        except AnalysisException as e:
            raise ValueError(f"Table {catalog_name} not found in catalog: {str(e)}")
    
    def run_query(self, query: str) -> DataFrame:
        """
        Execute SQL query and return DataFrame.
        
        Args:
            query: SQL query string
            
        Returns:
            PySpark DataFrame
        """
        return self._spark.sql(query)
    
    def create_or_replace_temp_view(self, df: DataFrame, view_name: str) -> None:
        """
        Create or replace temporary view.
        
        Args:
            df: DataFrame to create view from
            view_name: Name of the temporary view
        """
        df.createOrReplaceTempView(view_name)
    
    def table_exists(self, catalog_name: str) -> bool:
        """
        Check if table exists in catalog.
        
        Args:
            catalog_name: Full table name (catalog.schema.table)
            
        Returns:
            True if table exists, False otherwise
        """
        try:
            self._spark.table(catalog_name)
            return True
        except AnalysisException:
            return False
    
    @property
    def spark_session(self) -> SparkSession:
        """Get the underlying Spark session."""
        return self._spark