"""
Unit tests for CatalogService.
"""
import pytest
from unittest.mock import Mock, MagicMock
from catalog.catalog_service import CatalogService


class TestCatalogService:
    """Test cases for CatalogService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_spark_driver = Mock()
        self.catalog_service = CatalogService(self.mock_spark_driver)
    
    def test_build_catalog_name_valid_layers(self):
        """Test building catalog names for valid layers."""
        # Test all valid layers
        assert self.catalog_service.build_catalog_name("bronze", "customers") == "bronze.customers"
        assert self.catalog_service.build_catalog_name("silver", "customers") == "silver.customers"
        assert self.catalog_service.build_catalog_name("gold", "customers") == "gold.customers"
        
        # Test case insensitive
        assert self.catalog_service.build_catalog_name("BRONZE", "customers") == "bronze.customers"
        assert self.catalog_service.build_catalog_name("Silver", "customers") == "silver.customers"
    
    def test_build_catalog_name_invalid_layer(self):
        """Test building catalog names with invalid layer."""
        with pytest.raises(ValueError, match="Invalid data lake layer"):
            self.catalog_service.build_catalog_name("invalid", "customers")
    
    def test_is_in_catalog(self):
        """Test checking if table exists in catalog."""
        # Mock spark driver response
        self.mock_spark_driver.table_exists.return_value = True
        
        result = self.catalog_service.is_in_catalog("silver.customers")
        
        assert result is True
        self.mock_spark_driver.table_exists.assert_called_once_with("silver.customers")
    
    def test_get_table_columns_existing_table(self):
        """Test getting columns for existing table."""
        # Mock table exists and columns
        self.mock_spark_driver.table_exists.return_value = True
        mock_columns = [
            {'name': 'customer_id', 'type': 'string', 'nullable': False},
            {'name': 'name', 'type': 'string', 'nullable': True}
        ]
        self.mock_spark_driver.get_table_columns.return_value = mock_columns
        
        result = self.catalog_service.get_table_columns("silver.customers")
        
        assert result == mock_columns
        self.mock_spark_driver.get_table_columns.assert_called_once_with("silver.customers")
    
    def test_get_table_columns_nonexistent_table(self):
        """Test getting columns for non-existent table."""
        self.mock_spark_driver.table_exists.return_value = False
        
        with pytest.raises(ValueError, match="Table .* not found in catalog"):
            self.catalog_service.get_table_columns("silver.nonexistent")
    
    def test_is_scd2_table_valid_scd2(self):
        """Test detecting valid SCD2 table."""
        columns = [
            {'name': 'customer_id', 'type': 'string', 'nullable': False},
            {'name': 'valid_from', 'type': 'timestamp', 'nullable': False},
            {'name': 'valid_to', 'type': 'timestamp', 'nullable': True},
            {'name': 'is_current', 'type': 'boolean', 'nullable': False}
        ]
        
        assert self.catalog_service.is_scd2_table(columns) is True
    
    def test_is_scd2_table_alternative_scd2(self):
        """Test detecting SCD2 table with alternative column names."""
        columns = [
            {'name': 'customer_id', 'type': 'string', 'nullable': False},
            {'name': 'effective_date', 'type': 'timestamp', 'nullable': False},
            {'name': 'end_date', 'type': 'timestamp', 'nullable': True}
        ]
        
        assert self.catalog_service.is_scd2_table(columns) is True
    
    def test_is_scd2_table_not_scd2(self):
        """Test detecting non-SCD2 table."""
        columns = [
            {'name': 'customer_id', 'type': 'string', 'nullable': False},
            {'name': 'name', 'type': 'string', 'nullable': True},
            {'name': 'email', 'type': 'string', 'nullable': True}
        ]
        
        assert self.catalog_service.is_scd2_table(columns) is False
    
    def test_is_scd2_table_minimal_scd2(self):
        """Test detecting SCD2 table with minimal SCD2 columns."""
        columns = [
            {'name': 'customer_id', 'type': 'string', 'nullable': False},
            {'name': 'valid_from', 'type': 'timestamp', 'nullable': False},
            {'name': 'is_current', 'type': 'boolean', 'nullable': False}
        ]
        
        assert self.catalog_service.is_scd2_table(columns) is True
    
    def test_get_business_columns_without_scd2(self):
        """Test getting business columns without SCD2 technical columns."""
        columns = [
            {'name': 'customer_id', 'type': 'string', 'nullable': False},
            {'name': 'customer_hk', 'type': 'string', 'nullable': False},  # Hash key
            {'name': 'name', 'type': 'string', 'nullable': True},
            {'name': 'email', 'type': 'string', 'nullable': True},
            {'name': 'valid_from', 'type': 'timestamp', 'nullable': False},  # SCD2
            {'name': 'valid_to', 'type': 'timestamp', 'nullable': True},      # SCD2
            {'name': 'is_current', 'type': 'boolean', 'nullable': False}      # SCD2
        ]
        
        result = self.catalog_service.get_business_columns(columns, include_scd2_cols=False)
        
        expected = ['customer_id', 'customer_hk', 'name', 'email']
        assert result == expected
    
    def test_get_business_columns_with_scd2(self):
        """Test getting business columns with SCD2 technical columns."""
        columns = [
            {'name': 'customer_id', 'type': 'string', 'nullable': False},
            {'name': 'customer_hk', 'type': 'string', 'nullable': False},  # Hash key
            {'name': 'name', 'type': 'string', 'nullable': True},
            {'name': 'valid_from', 'type': 'timestamp', 'nullable': False},  # SCD2
            {'name': 'is_current', 'type': 'boolean', 'nullable': False}      # SCD2
        ]
        
        result = self.catalog_service.get_business_columns(columns, include_scd2_cols=True)
        
        expected = ['customer_id', 'customer_hk', 'name', 'valid_from', 'is_current']
        assert result == expected
    
    def test_get_business_columns_hash_key_patterns(self):
        """Test that various hash key patterns are always included."""
        columns = [
            {'name': 'hash_key', 'type': 'string', 'nullable': False},
            {'name': 'hk_customer', 'type': 'string', 'nullable': False},
            {'name': 'customer_hk', 'type': 'string', 'nullable': False},
            {'name': 'dim_hash_key', 'type': 'string', 'nullable': False},
            {'name': 'regular_column', 'type': 'string', 'nullable': False},
            {'name': 'valid_from', 'type': 'timestamp', 'nullable': False}  # SCD2
        ]
        
        result = self.catalog_service.get_business_columns(columns, include_scd2_cols=False)
        
        # All hash keys should be included even without SCD2 cols
        expected = ['hash_key', 'hk_customer', 'customer_hk', 'dim_hash_key', 'regular_column']
        assert result == expected
    
    def test_get_scd2_columns(self):
        """Test getting SCD2 technical columns."""
        columns = [
            {'name': 'customer_id', 'type': 'string', 'nullable': False},
            {'name': 'name', 'type': 'string', 'nullable': True},
            {'name': 'valid_from', 'type': 'timestamp', 'nullable': False},
            {'name': 'valid_to', 'type': 'timestamp', 'nullable': True},
            {'name': 'is_current', 'type': 'boolean', 'nullable': False},
            {'name': 'created_at', 'type': 'timestamp', 'nullable': False}
        ]
        
        result = self.catalog_service.get_scd2_columns(columns)
        
        expected = ['valid_from', 'valid_to', 'is_current', 'created_at']
        assert result == expected