"""
Example usage of the SCD2 Delta table reader.

This script demonstrates how to use the SCD2 table reader to read snapshots
from historical SCD2 Delta tables in your data lake.
"""

from pyspark.sql import SparkSession
from factory import get_table_reader_client, create_scd2_reader


def basic_usage_example():
    """Basic usage example."""
    print("=== Basic Usage Example ===")
    
    # Create Spark session (in Databricks this would be available as 'spark')
    spark = SparkSession.builder.appName("SCD2ReaderExample").getOrCreate()
    
    # Create SCD2 table reader client
    reader = get_table_reader_client(spark_session=spark)
    
    # Read latest snapshot from Silver layer
    df = reader.read_snapshot_scd2("silver", "customers")
    
    print(f"Read {df.count()} rows from silver.customers")
    df.show(5)


def advanced_usage_example():
    """Advanced usage example with all options."""
    print("\n=== Advanced Usage Example ===")
    
    spark = SparkSession.builder.appName("SCD2ReaderAdvanced").getOrCreate()
    reader = get_table_reader_client(spark_session=spark)
    
    # Read snapshot at specific point in time with SCD2 columns included
    df = reader.read_snapshot_scd2(
        dlk_layer="gold",
        table_name="dim_customer", 
        snapshot_dt="2024-01-01 10:00:00",
        view_name="customer_snapshot_jan1",
        include_scd2_cols=True
    )
    
    print(f"Read {df.count()} rows from gold.dim_customer at 2024-01-01 10:00:00")
    print("Columns:", df.columns)
    df.show(3)
    
    # The data is also available as a temporary view
    spark.sql("SELECT * FROM customer_snapshot_jan1 LIMIT 2").show()


def table_inspection_example():
    """Example of inspecting table information."""
    print("\n=== Table Inspection Example ===")
    
    spark = SparkSession.builder.appName("SCD2TableInspection").getOrCreate()
    reader = get_table_reader_client(spark_session=spark)
    
    # Get information about a table
    info = reader.get_table_info("silver", "customers")
    
    print(f"Table exists: {info['exists']}")
    print(f"Is SCD2 table: {info['is_scd2_table']}")
    print(f"Total columns: {info['total_columns']}")
    print(f"Business columns: {info['business_columns']}")
    print(f"SCD2 columns: {info['scd2_columns']}")
    
    # Get sample data
    sample_df = reader.sample_data("silver", "customers", limit=3)
    print("\nSample data:")
    sample_df.show()


def error_handling_example():
    """Example of error handling."""
    print("\n=== Error Handling Example ===")
    
    spark = SparkSession.builder.appName("SCD2ErrorHandling").getOrCreate()
    reader = get_table_reader_client(spark_session=spark)
    
    try:
        # Try to read from non-existent table
        df = reader.read_snapshot_scd2("silver", "nonexistent_table")
    except ValueError as e:
        print(f"Expected error for non-existent table: {e}")
    
    try:
        # Try to read from non-SCD2 table (if it exists)
        df = reader.read_snapshot_scd2("bronze", "raw_logs")
    except ValueError as e:
        print(f"Expected error for non-SCD2 table: {e}")


def custom_implementation_example():
    """Example with custom service implementations."""
    print("\n=== Custom Implementation Example ===")
    
    from catalog.catalog_service import CatalogService
    from common.protocols import SparkDriverProtocol
    
    # Custom catalog service that uses different naming convention
    class CustomCatalogService(CatalogService):
        def build_catalog_name(self, dlk_layer: str, table_name: str) -> str:
            """Custom catalog naming with environment prefix."""
            layer = dlk_layer.lower()
            return f"prod_{layer}.{table_name}"
    
    spark = SparkSession.builder.appName("SCD2Custom").getOrCreate()
    
    # Create reader with custom catalog service
    reader = get_table_reader_client(
        spark_session=spark,
        catalog_service_class=CustomCatalogService
    )
    
    # This will look for table "prod_silver.customers" instead of "silver.customers"
    try:
        df = reader.read_snapshot_scd2("silver", "customers")
        print("Successfully used custom catalog service")
    except ValueError as e:
        print(f"Custom catalog service attempted to access: prod_silver.customers")
        print(f"Error: {e}")


def convenience_function_example():
    """Example using the convenience function."""
    print("\n=== Convenience Function Example ===")
    
    # Quick setup using convenience function
    reader = create_scd2_reader()
    
    # Check if a table exists and get info
    info = reader.get_table_info("gold", "dim_product")
    
    if info['exists']:
        print(f"Found table: {info['catalog_name']}")
        print(f"SCD2 table: {info['is_scd2_table']}")
        
        if info['is_scd2_table']:
            # Read the data
            df = reader.read_snapshot_scd2("gold", "dim_product")
            print(f"Successfully read {df.count()} rows")
    else:
        print("Table not found")


def databricks_notebook_usage():
    """
    Example for use in Databricks notebook.
    
    In a Databricks notebook, you would typically use it like this:
    """
    
    # Note: In Databricks, 'spark' is already available
    # from factory import get_table_reader_client
    
    # # Create reader (spark session is automatically detected)
    # reader = get_table_reader_client()
    # 
    # # Read latest customer data
    # customers_df = reader.read_snapshot_scd2("gold", "dim_customer")
    # 
    # # Read product data at specific date with technical columns
    # products_df = reader.read_snapshot_scd2(
    #     "gold", 
    #     "dim_product", 
    #     snapshot_dt="2024-01-01",
    #     include_scd2_cols=True,
    #     view_name="products_jan1"
    # )
    # 
    # # Use in further analysis
    # result_df = customers_df.join(products_df, "product_id")
    
    print("\n=== Databricks Notebook Usage ===")
    print("See comments in the function for typical Databricks usage patterns.")


if __name__ == "__main__":
    """
    Run examples. Note: These examples assume you have appropriate 
    Delta tables set up in your environment.
    """
    
    print("SCD2 Delta Table Reader - Usage Examples")
    print("=" * 50)
    
    try:
        basic_usage_example()
        advanced_usage_example()
        table_inspection_example()
        error_handling_example()
        custom_implementation_example()
        convenience_function_example()
        databricks_notebook_usage()
        
    except Exception as e:
        print(f"\nNote: Examples require actual Delta tables to be present.")
        print(f"Error encountered: {e}")
        print("\nTo run these examples successfully:")
        print("1. Set up Spark with Delta Lake support")
        print("2. Create some SCD2 Delta tables in your catalog")
        print("3. Adjust the table names in the examples to match your tables")
    
    print("\n" + "=" * 50)
    print("Examples completed!")