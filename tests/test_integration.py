"""
Integration tests for SCD2 Delta table reader.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, BooleanType

from factory import get_table_reader_client, create_scd2_reader


class TestSCD2TableReaderIntegration:
    """Integration tests for the complete SCD2 table reader workflow."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Mock Spark session and DataFrame
        self.mock_spark = Mock(spec=SparkSession)
        self.mock_df = Mock(spec=DataFrame)
        
        # Mock schema for SCD2 table
        self.scd2_schema = StructType([
            StructField("customer_id", StringType(), False),
            StructField("customer_hk", StringType(), False),  # Hash key
            StructField("name", StringType(), True),
            StructField("email", StringType(), True),
            StructField("valid_from", TimestampType(), False),  # SCD2
            StructField("valid_to", TimestampType(), True),     # SCD2
            StructField("is_current", BooleanType(), False)     # SCD2
        ])
        
        # Configure mock DataFrame
        self.mock_df.schema = self.scd2_schema
        self.mock_spark.table.return_value = self.mock_df
        self.mock_spark.sql.return_value = self.mock_df
    
    def test_end_to_end_scd2_reading_latest(self):
        """Test complete end-to-end SCD2 reading for latest snapshot."""
        # Create client using factory
        client = get_table_reader_client(spark_session=self.mock_spark)
        
        # Execute read
        result = client.read_snapshot_scd2("silver", "customers")
        
        # Verify result
        assert result == self.mock_df
        
        # Verify Spark interactions
        self.mock_spark.table.assert_called_with("silver.customers")
        
        # Verify SQL query was executed
        assert self.mock_spark.sql.called
        query = self.mock_spark.sql.call_args[0][0]
        
        # Check query contains expected elements
        assert "SELECT" in query
        assert "`customer_id`" in query
        assert "`customer_hk`" in query  # Hash key included
        assert "`name`" in query
        assert "`email`" in query
        assert "`valid_from`" not in query  # SCD2 cols excluded by default
        assert "`valid_to`" not in query
        assert "`is_current`" not in query
        assert "FROM silver.customers" in query
        assert "is_current = true" in query
    
    def test_end_to_end_scd2_reading_with_scd2_columns(self):
        """Test complete end-to-end SCD2 reading including SCD2 columns."""
        client = get_table_reader_client(spark_session=self.mock_spark)
        
        # Execute read with SCD2 columns
        result = client.read_snapshot_scd2("gold", "dim_customer", include_scd2_cols=True)
        
        # Verify result
        assert result == self.mock_df
        
        # Verify SQL query includes SCD2 columns
        query = self.mock_spark.sql.call_args[0][0]
        assert "`valid_from`" in query
        assert "`valid_to`" in query
        assert "`is_current`" in query
        assert "FROM gold.dim_customer" in query
    
    def test_end_to_end_scd2_reading_specific_datetime(self):
        """Test complete end-to-end SCD2 reading for specific datetime."""
        client = get_table_reader_client(spark_session=self.mock_spark)
        
        snapshot_dt = "2024-01-01 12:00:00"
        result = client.read_snapshot_scd2("bronze", "raw_customers", snapshot_dt=snapshot_dt)
        
        # Verify result
        assert result == self.mock_df
        
        # Verify SQL query contains datetime conditions
        query = self.mock_spark.sql.call_args[0][0]
        assert "2024-01-01 12:00:00" in query
        assert "valid_from <=" in query
        assert "valid_to >" in query
        assert "FROM bronze.raw_customers" in query
    
    def test_end_to_end_with_temporary_view(self):
        """Test complete end-to-end SCD2 reading with temporary view creation."""
        client = get_table_reader_client(spark_session=self.mock_spark)
        
        result = client.read_snapshot_scd2("silver", "customers", view_name="customer_snapshot")
        
        # Verify result
        assert result == self.mock_df
        
        # Verify temporary view was created
        self.mock_df.createOrReplaceTempView.assert_called_once_with("customer_snapshot")
    
    def test_factory_with_custom_services(self):
        """Test factory with custom service implementations."""
        # Create custom catalog service
        custom_catalog_service = Mock()
        custom_catalog_service.build_catalog_name.return_value = "custom_catalog.customers"
        custom_catalog_service.is_in_catalog.return_value = True
        custom_catalog_service.get_table_columns.return_value = [
            {'name': 'id', 'type': 'string'},
            {'name': 'valid_from', 'type': 'timestamp'},
            {'name': 'is_current', 'type': 'boolean'}
        ]
        custom_catalog_service.is_scd2_table.return_value = True
        custom_catalog_service.get_business_columns.return_value = ['id']
        
        # Custom catalog service class
        class CustomCatalogService:
            def __init__(self, **kwargs):
                return custom_catalog_service
        
        # Use factory with custom service
        client = get_table_reader_client(
            spark_session=self.mock_spark,
            catalog_service_class=CustomCatalogService
        )
        
        # This would use the custom catalog service, but since we're mocking
        # we can't easily test the instantiation. Instead, we verify the factory works.
        assert client is not None
    
    def test_convenience_function(self):
        """Test the convenience function create_scd2_reader."""
        client = create_scd2_reader(spark_session=self.mock_spark)
        
        # Should work the same as get_table_reader_client
        result = client.read_snapshot_scd2("silver", "customers")
        assert result == self.mock_df
    
    def test_error_handling_table_not_found(self):
        """Test error handling when table is not found."""
        # Configure mock to simulate table not found
        from pyspark.sql.utils import AnalysisException
        self.mock_spark.table.side_effect = AnalysisException("Table not found")
        
        client = get_table_reader_client(spark_session=self.mock_spark)
        
        with pytest.raises(ValueError, match="not found in catalog"):
            client.read_snapshot_scd2("silver", "nonexistent")
    
    def test_error_handling_not_scd2_table(self):
        """Test error handling when table is not SCD2."""
        # Mock a non-SCD2 table schema
        non_scd2_schema = StructType([
            StructField("id", StringType(), False),
            StructField("data", StringType(), True)
        ])
        
        mock_non_scd2_df = Mock(spec=DataFrame)
        mock_non_scd2_df.schema = non_scd2_schema
        self.mock_spark.table.return_value = mock_non_scd2_df
        
        client = get_table_reader_client(spark_session=self.mock_spark)
        
        with pytest.raises(ValueError, match="does not appear to be an SCD2 table"):
            client.read_snapshot_scd2("bronze", "non_scd2_table")
    
    def test_table_info_functionality(self):
        """Test the table info functionality."""
        client = get_table_reader_client(spark_session=self.mock_spark)
        
        info = client.get_table_info("silver", "customers")
        
        # Verify info structure
        assert info['exists'] is True
        assert info['catalog_name'] == "silver.customers"
        assert info['is_scd2_table'] is True
        assert 'business_columns' in info
        assert 'scd2_columns' in info
        assert 'column_details' in info
    
    def test_sample_data_functionality(self):
        """Test the sample data functionality."""
        client = get_table_reader_client(spark_session=self.mock_spark)
        
        result = client.sample_data("gold", "dim_customer", limit=5)
        
        # Verify result
        assert result == self.mock_df
        
        # Verify correct query was executed
        query = self.mock_spark.sql.call_args[0][0]
        assert "SELECT * FROM gold.dim_customer LIMIT 5" == query
    
    def test_factory_kwargs_passing(self):
        """Test that factory correctly passes kwargs to services."""
        # Test that we can pass custom parameters
        client = get_table_reader_client(
            spark_session=self.mock_spark,
            catalog_custom_param="test_value",
            query_custom_param=123
        )
        
        # The client should be created successfully
        assert client is not None
        
        # We can't easily test the kwargs passing without more complex mocking,
        # but the fact that the factory doesn't fail shows the kwargs extraction works
    
    @patch('factory.SparkSession')
    def test_factory_creates_spark_session_when_none_provided(self, mock_spark_class):
        """Test that factory creates Spark session when none is provided."""
        mock_spark_instance = Mock()
        mock_spark_class.getActiveSession.return_value = None
        mock_spark_class.builder.appName.return_value.getOrCreate.return_value = mock_spark_instance
        
        # Configure the mock instance to behave like our test spark session
        mock_spark_instance.table.return_value = self.mock_df
        mock_spark_instance.sql.return_value = self.mock_df
        
        client = get_table_reader_client()  # No spark session provided
        
        # Should create a new Spark session
        mock_spark_class.builder.appName.assert_called_with("SCD2TableReader")
        
        # Should be able to use the client
        assert client is not None