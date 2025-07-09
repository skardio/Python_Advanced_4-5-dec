"""
Factory for creating SCD2 table reader client.
"""
from typing import Optional, Type, Any, Dict
from pyspark.sql import SparkSession

from common.spark_driver import SparkDriver
from catalog.catalog_service import CatalogService
from storage.table_readers.query_service import QueryService
from storage.table_readers.table_reader_client import TableReaderClient
from common.protocols import (
    SparkDriverProtocol, 
    CatalogServiceProtocol, 
    QueryServiceProtocol,
    TableReaderClientProtocol
)


def get_table_reader_client(
    spark_session: Optional[SparkSession] = None,
    spark_driver_class: Optional[Type[SparkDriverProtocol]] = None,
    catalog_service_class: Optional[Type[CatalogServiceProtocol]] = None,
    query_service_class: Optional[Type[QueryServiceProtocol]] = None,
    table_reader_client_class: Optional[Type[TableReaderClientProtocol]] = None,
    **kwargs
) -> TableReaderClientProtocol:
    """
    Factory function to create a configured table reader client.
    
    This factory allows for dependency injection and customization of all components.
    Users can override any class implementation by providing their own classes.
    
    Args:
        spark_session: Optional Spark session (will create/get active if None)
        spark_driver_class: Custom SparkDriver class (defaults to SparkDriver)
        catalog_service_class: Custom CatalogService class (defaults to CatalogService)
        query_service_class: Custom QueryService class (defaults to QueryService)
        table_reader_client_class: Custom TableReaderClient class (defaults to TableReaderClient)
        **kwargs: Additional parameters passed to class constructors
        
    Returns:
        Configured TableReaderClient instance
        
    Example:
        >>> # Basic usage
        >>> client = get_table_reader_client()
        >>> df = client.read_snapshot_scd2("silver", "customers")
        
        >>> # With custom Spark session
        >>> spark = SparkSession.builder.appName("MyApp").getOrCreate()
        >>> client = get_table_reader_client(spark_session=spark)
        
        >>> # With custom service implementations
        >>> class CustomCatalogService(CatalogService):
        ...     def build_catalog_name(self, dlk_layer, table_name):
        ...         return f"custom_{dlk_layer}.{table_name}"
        >>> 
        >>> client = get_table_reader_client(catalog_service_class=CustomCatalogService)
    """
    # Use default classes if not provided
    spark_driver_class = spark_driver_class or SparkDriver
    catalog_service_class = catalog_service_class or CatalogService
    query_service_class = query_service_class or QueryService
    table_reader_client_class = table_reader_client_class or TableReaderClient
    
    # Extract class-specific kwargs
    spark_kwargs = _extract_kwargs(kwargs, 'spark_')
    catalog_kwargs = _extract_kwargs(kwargs, 'catalog_')
    query_kwargs = _extract_kwargs(kwargs, 'query_')
    client_kwargs = _extract_kwargs(kwargs, 'client_')
    
    # Add spark_session to spark_kwargs if provided
    if spark_session is not None:
        spark_kwargs['spark_session'] = spark_session
    
    # Create instances
    spark_driver = spark_driver_class(**spark_kwargs)
    catalog_service = catalog_service_class(spark_driver=spark_driver, **catalog_kwargs)
    query_service = query_service_class(spark_driver=spark_driver, **query_kwargs)
    
    # Create table reader client
    table_reader_client = table_reader_client_class(
        catalog_service=catalog_service,
        query_service=query_service,
        spark_driver=spark_driver,
        **client_kwargs
    )
    
    return table_reader_client


def _extract_kwargs(kwargs: Dict[str, Any], prefix: str) -> Dict[str, Any]:
    """
    Extract keyword arguments with a specific prefix.
    
    Args:
        kwargs: Dictionary of keyword arguments
        prefix: Prefix to filter by (e.g., 'spark_')
        
    Returns:
        Dictionary with matching kwargs (prefix removed from keys)
    """
    extracted = {}
    for key, value in kwargs.items():
        if key.startswith(prefix):
            new_key = key[len(prefix):]
            extracted[new_key] = value
    return extracted


# Convenience function for quick usage
def create_scd2_reader(spark_session: Optional[SparkSession] = None, **kwargs) -> TableReaderClientProtocol:
    """
    Convenience function to create an SCD2 table reader.
    
    This is a simplified version of get_table_reader_client for common use cases.
    
    Args:
        spark_session: Optional Spark session
        **kwargs: Additional parameters
        
    Returns:
        Configured TableReaderClient instance
        
    Example:
        >>> # Quick setup
        >>> reader = create_scd2_reader()
        >>> df = reader.read_snapshot_scd2("gold", "dim_customer", snapshot_dt="2024-01-01")
    """
    return get_table_reader_client(spark_session=spark_session, **kwargs)