"""
Unit tests for QueryService.
"""
import pytest
from unittest.mock import Mock
from storage.table_readers.query_service import QueryService


class TestQueryService:
    """Test cases for QueryService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_spark_driver = Mock()
        self.query_service = QueryService(self.mock_spark_driver)
    
    def test_build_snapshot_scd2_query_latest(self):
        """Test building query for latest snapshot."""
        catalog_name = "silver.customers"
        selected_cols = ["customer_id", "name", "email"]
        
        query = self.query_service.build_snapshot_scd2_query(
            catalog_name, None, selected_cols
        )
        
        # Check query structure
        assert "SELECT `customer_id`, `name`, `email`" in query
        assert "FROM silver.customers" in query
        assert "is_current = true" in query
        assert "current_flag = 'Y'" in query
        assert "valid_to IS NULL" in query
    
    def test_build_snapshot_scd2_query_specific_date(self):
        """Test building query for specific date."""
        catalog_name = "gold.dim_customer"
        selected_cols = ["customer_hk", "name"]
        snapshot_dt = "2024-01-01 10:00:00"
        
        query = self.query_service.build_snapshot_scd2_query(
            catalog_name, snapshot_dt, selected_cols
        )
        
        # Check query structure
        assert "SELECT `customer_hk`, `name`" in query
        assert "FROM gold.dim_customer" in query
        assert "valid_from <= '2024-01-01 10:00:00'" in query
        assert "valid_to > '2024-01-01 10:00:00'" in query
        assert "effective_date <= '2024-01-01 10:00:00'" in query
        assert "end_date > '2024-01-01 10:00:00'" in query
    
    def test_build_snapshot_scd2_query_single_column(self):
        """Test building query with single column."""
        catalog_name = "bronze.raw_data"
        selected_cols = ["id"]
        
        query = self.query_service.build_snapshot_scd2_query(
            catalog_name, None, selected_cols
        )
        
        assert "SELECT `id`" in query
        assert "FROM bronze.raw_data" in query
    
    def test_normalize_timestamp_standard_format(self):
        """Test normalizing standard timestamp format."""
        timestamp_str = "2024-01-01 10:30:00"
        
        result = self.query_service._normalize_timestamp(timestamp_str)
        
        assert result == "2024-01-01 10:30:00"
    
    def test_normalize_timestamp_iso_format(self):
        """Test normalizing ISO timestamp format."""
        timestamp_str = "2024-01-01T10:30:00"
        
        result = self.query_service._normalize_timestamp(timestamp_str)
        
        assert result == "2024-01-01 10:30:00"
    
    def test_normalize_timestamp_iso_with_z(self):
        """Test normalizing ISO timestamp with Z suffix."""
        timestamp_str = "2024-01-01T10:30:00Z"
        
        result = self.query_service._normalize_timestamp(timestamp_str)
        
        assert result == "2024-01-01 10:30:00"
    
    def test_normalize_timestamp_date_only(self):
        """Test normalizing date-only format."""
        timestamp_str = "2024-01-01"
        
        result = self.query_service._normalize_timestamp(timestamp_str)
        
        assert result == "2024-01-01 00:00:00"
    
    def test_normalize_timestamp_with_microseconds(self):
        """Test normalizing timestamp with microseconds."""
        timestamp_str = "2024-01-01 10:30:00.123456"
        
        result = self.query_service._normalize_timestamp(timestamp_str)
        
        assert result == "2024-01-01 10:30:00"
    
    def test_normalize_timestamp_invalid_format(self):
        """Test normalizing invalid timestamp format."""
        timestamp_str = "invalid-timestamp"
        
        # Should return as-is if parsing fails
        result = self.query_service._normalize_timestamp(timestamp_str)
        
        assert result == "invalid-timestamp"
    
    def test_run_query(self):
        """Test running query through spark driver."""
        query = "SELECT * FROM test_table"
        mock_df = Mock()
        self.mock_spark_driver.run_query.return_value = mock_df
        
        result = self.query_service.run_query(query)
        
        assert result == mock_df
        self.mock_spark_driver.run_query.assert_called_once_with(query)
    
    def test_build_table_info_query(self):
        """Test building table info query."""
        catalog_name = "silver.customers"
        
        query = self.query_service.build_table_info_query(catalog_name)
        
        assert query == "DESCRIBE TABLE silver.customers"
    
    def test_build_sample_query_default_limit(self):
        """Test building sample query with default limit."""
        catalog_name = "gold.facts"
        
        query = self.query_service.build_sample_query(catalog_name)
        
        assert query == "SELECT * FROM gold.facts LIMIT 10"
    
    def test_build_sample_query_custom_limit(self):
        """Test building sample query with custom limit."""
        catalog_name = "bronze.raw"
        limit = 5
        
        query = self.query_service.build_sample_query(catalog_name, limit)
        
        assert query == "SELECT * FROM bronze.raw LIMIT 5"
    
    def test_build_snapshot_scd2_query_column_escaping(self):
        """Test that column names are properly escaped with backticks."""
        catalog_name = "test.table"
        selected_cols = ["column with spaces", "normal_column", "123numeric"]
        
        query = self.query_service.build_snapshot_scd2_query(
            catalog_name, None, selected_cols
        )
        
        # Check that all columns are escaped with backticks
        assert "`column with spaces`" in query
        assert "`normal_column`" in query
        assert "`123numeric`" in query
    
    def test_build_snapshot_scd2_query_comprehensive_conditions(self):
        """Test that query includes all SCD2 condition patterns."""
        catalog_name = "silver.test"
        selected_cols = ["id"]
        snapshot_dt = "2024-01-01"
        
        query = self.query_service.build_snapshot_scd2_query(
            catalog_name, snapshot_dt, selected_cols
        )
        
        # Should include multiple SCD2 patterns
        assert "valid_from" in query and "valid_to" in query
        assert "effective_date" in query and "end_date" in query  
        assert "created_at" in query and "updated_at" in query
        assert "9999-12-31" in query  # End of time marker
        assert "2099-12-31" in query  # Alternative end of time marker