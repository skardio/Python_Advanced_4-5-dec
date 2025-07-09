"""
Unit tests for TableReaderClient.
"""
import pytest
from unittest.mock import Mock
from storage.table_readers.table_reader_client import TableReaderClient


class TestTableReaderClient:
    """Test cases for TableReaderClient."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_catalog_service = Mock()
        self.mock_query_service = Mock()
        self.mock_spark_driver = Mock()
        
        self.client = TableReaderClient(
            catalog_service=self.mock_catalog_service,
            query_service=self.mock_query_service,
            spark_driver=self.mock_spark_driver
        )
    
    def test_read_snapshot_scd2_success(self):
        """Test successful SCD2 snapshot reading."""
        # Setup mocks
        self.mock_catalog_service.build_catalog_name.return_value = "silver.customers"
        self.mock_catalog_service.is_in_catalog.return_value = True
        
        mock_columns = [
            {'name': 'customer_id', 'type': 'string'},
            {'name': 'name', 'type': 'string'},
            {'name': 'valid_from', 'type': 'timestamp'},
            {'name': 'is_current', 'type': 'boolean'}
        ]
        self.mock_catalog_service.get_table_columns.return_value = mock_columns
        self.mock_catalog_service.is_scd2_table.return_value = True
        self.mock_catalog_service.get_business_columns.return_value = ['customer_id', 'name']
        
        mock_query = "SELECT customer_id, name FROM silver.customers WHERE is_current = true"
        self.mock_query_service.build_snapshot_scd2_query.return_value = mock_query
        
        mock_df = Mock()
        self.mock_query_service.run_query.return_value = mock_df
        
        # Execute
        result = self.client.read_snapshot_scd2("silver", "customers")
        
        # Verify
        assert result == mock_df
        self.mock_catalog_service.build_catalog_name.assert_called_once_with("silver", "customers")
        self.mock_catalog_service.is_in_catalog.assert_called_once_with("silver.customers")
        self.mock_catalog_service.get_table_columns.assert_called_once_with("silver.customers")
        self.mock_catalog_service.is_scd2_table.assert_called_once_with(mock_columns)
        self.mock_catalog_service.get_business_columns.assert_called_once_with(mock_columns, include_scd2_cols=False)
        self.mock_query_service.build_snapshot_scd2_query.assert_called_once_with("silver.customers", None, ['customer_id', 'name'])
        self.mock_query_service.run_query.assert_called_once_with(mock_query)
    
    def test_read_snapshot_scd2_with_view_name(self):
        """Test SCD2 snapshot reading with temporary view creation."""
        # Setup mocks
        self.mock_catalog_service.build_catalog_name.return_value = "gold.dim_customer"
        self.mock_catalog_service.is_in_catalog.return_value = True
        self.mock_catalog_service.get_table_columns.return_value = [
            {'name': 'customer_hk', 'type': 'string'},
            {'name': 'valid_from', 'type': 'timestamp'},
            {'name': 'is_current', 'type': 'boolean'}
        ]
        self.mock_catalog_service.is_scd2_table.return_value = True
        self.mock_catalog_service.get_business_columns.return_value = ['customer_hk']
        
        self.mock_query_service.build_snapshot_scd2_query.return_value = "SELECT customer_hk FROM gold.dim_customer"
        mock_df = Mock()
        self.mock_query_service.run_query.return_value = mock_df
        
        # Execute
        result = self.client.read_snapshot_scd2("gold", "dim_customer", view_name="customers_view")
        
        # Verify
        assert result == mock_df
        self.mock_spark_driver.create_or_replace_temp_view.assert_called_once_with(mock_df, "customers_view")
    
    def test_read_snapshot_scd2_with_scd2_columns(self):
        """Test SCD2 snapshot reading with SCD2 columns included."""
        # Setup mocks
        self.mock_catalog_service.build_catalog_name.return_value = "silver.customers"
        self.mock_catalog_service.is_in_catalog.return_value = True
        self.mock_catalog_service.get_table_columns.return_value = [
            {'name': 'customer_id', 'type': 'string'},
            {'name': 'valid_from', 'type': 'timestamp'},
            {'name': 'is_current', 'type': 'boolean'}
        ]
        self.mock_catalog_service.is_scd2_table.return_value = True
        self.mock_catalog_service.get_business_columns.return_value = ['customer_id', 'valid_from', 'is_current']
        
        self.mock_query_service.build_snapshot_scd2_query.return_value = "SELECT * FROM silver.customers"
        mock_df = Mock()
        self.mock_query_service.run_query.return_value = mock_df
        
        # Execute
        result = self.client.read_snapshot_scd2("silver", "customers", include_scd2_cols=True)
        
        # Verify
        assert result == mock_df
        self.mock_catalog_service.get_business_columns.assert_called_once_with(
            self.mock_catalog_service.get_table_columns.return_value, 
            include_scd2_cols=True
        )
    
    def test_read_snapshot_scd2_with_snapshot_datetime(self):
        """Test SCD2 snapshot reading with specific datetime."""
        # Setup mocks
        self.mock_catalog_service.build_catalog_name.return_value = "gold.facts"
        self.mock_catalog_service.is_in_catalog.return_value = True
        self.mock_catalog_service.get_table_columns.return_value = [
            {'name': 'fact_id', 'type': 'string'},
            {'name': 'valid_from', 'type': 'timestamp'},
            {'name': 'valid_to', 'type': 'timestamp'}
        ]
        self.mock_catalog_service.is_scd2_table.return_value = True
        self.mock_catalog_service.get_business_columns.return_value = ['fact_id']
        
        snapshot_dt = "2024-01-01 12:00:00"
        self.mock_query_service.build_snapshot_scd2_query.return_value = "SELECT fact_id FROM gold.facts WHERE ..."
        mock_df = Mock()
        self.mock_query_service.run_query.return_value = mock_df
        
        # Execute
        result = self.client.read_snapshot_scd2("gold", "facts", snapshot_dt=snapshot_dt)
        
        # Verify
        assert result == mock_df
        self.mock_query_service.build_snapshot_scd2_query.assert_called_once_with(
            "gold.facts", snapshot_dt, ['fact_id']
        )
    
    def test_read_snapshot_scd2_table_not_found(self):
        """Test error when table is not found."""
        self.mock_catalog_service.build_catalog_name.return_value = "silver.nonexistent"
        self.mock_catalog_service.is_in_catalog.return_value = False
        
        with pytest.raises(ValueError, match="Table silver.nonexistent not found in catalog"):
            self.client.read_snapshot_scd2("silver", "nonexistent")
    
    def test_read_snapshot_scd2_not_scd2_table(self):
        """Test error when table is not SCD2."""
        self.mock_catalog_service.build_catalog_name.return_value = "bronze.raw"
        self.mock_catalog_service.is_in_catalog.return_value = True
        
        mock_columns = [
            {'name': 'id', 'type': 'string'},
            {'name': 'data', 'type': 'string'}
        ]
        self.mock_catalog_service.get_table_columns.return_value = mock_columns
        self.mock_catalog_service.is_scd2_table.return_value = False
        self.mock_catalog_service.get_scd2_columns.return_value = []
        
        with pytest.raises(ValueError, match="does not appear to be an SCD2 table"):
            self.client.read_snapshot_scd2("bronze", "raw")
    
    def test_read_snapshot_scd2_no_columns_selected(self):
        """Test error when no columns are selected."""
        self.mock_catalog_service.build_catalog_name.return_value = "silver.empty"
        self.mock_catalog_service.is_in_catalog.return_value = True
        self.mock_catalog_service.get_table_columns.return_value = [
            {'name': 'valid_from', 'type': 'timestamp'},
            {'name': 'valid_to', 'type': 'timestamp'}
        ]
        self.mock_catalog_service.is_scd2_table.return_value = True
        self.mock_catalog_service.get_business_columns.return_value = []  # No columns selected
        
        with pytest.raises(ValueError, match="No columns selected for table"):
            self.client.read_snapshot_scd2("silver", "empty")
    
    def test_get_table_info_existing_table(self):
        """Test getting table info for existing table."""
        self.mock_catalog_service.build_catalog_name.return_value = "silver.customers"
        self.mock_catalog_service.is_in_catalog.return_value = True
        
        mock_columns = [
            {'name': 'customer_id', 'type': 'string'},
            {'name': 'name', 'type': 'string'},
            {'name': 'valid_from', 'type': 'timestamp'},
            {'name': 'is_current', 'type': 'boolean'}
        ]
        self.mock_catalog_service.get_table_columns.return_value = mock_columns
        self.mock_catalog_service.is_scd2_table.return_value = True
        self.mock_catalog_service.get_scd2_columns.return_value = ['valid_from', 'is_current']
        self.mock_catalog_service.get_business_columns.side_effect = [
            ['customer_id', 'name'],  # Without SCD2 cols
            ['customer_id', 'name', 'valid_from', 'is_current']  # With SCD2 cols
        ]
        
        result = self.client.get_table_info("silver", "customers")
        
        expected = {
            'exists': True,
            'catalog_name': 'silver.customers',
            'is_scd2_table': True,
            'total_columns': 4,
            'all_columns': ['customer_id', 'name', 'valid_from', 'is_current'],
            'scd2_columns': ['valid_from', 'is_current'],
            'business_columns': ['customer_id', 'name'],
            'business_columns_with_scd2': ['customer_id', 'name', 'valid_from', 'is_current'],
            'column_details': mock_columns
        }
        
        assert result == expected
    
    def test_get_table_info_nonexistent_table(self):
        """Test getting table info for non-existent table."""
        self.mock_catalog_service.build_catalog_name.return_value = "silver.nonexistent"
        self.mock_catalog_service.is_in_catalog.return_value = False
        
        result = self.client.get_table_info("silver", "nonexistent")
        
        expected = {
            'exists': False,
            'catalog_name': 'silver.nonexistent',
            'error': 'Table silver.nonexistent not found'
        }
        
        assert result == expected
    
    def test_sample_data_success(self):
        """Test getting sample data from table."""
        self.mock_catalog_service.build_catalog_name.return_value = "gold.dim_customer"
        self.mock_catalog_service.is_in_catalog.return_value = True
        
        mock_query = "SELECT * FROM gold.dim_customer LIMIT 5"
        self.mock_query_service.build_sample_query.return_value = mock_query
        
        mock_df = Mock()
        self.mock_query_service.run_query.return_value = mock_df
        
        result = self.client.sample_data("gold", "dim_customer", limit=5)
        
        assert result == mock_df
        self.mock_query_service.build_sample_query.assert_called_once_with("gold.dim_customer", 5)
        self.mock_query_service.run_query.assert_called_once_with(mock_query)
    
    def test_sample_data_table_not_found(self):
        """Test error when sampling data from non-existent table."""
        self.mock_catalog_service.build_catalog_name.return_value = "bronze.nonexistent"
        self.mock_catalog_service.is_in_catalog.return_value = False
        
        with pytest.raises(ValueError, match="Table bronze.nonexistent not found in catalog"):
            self.client.sample_data("bronze", "nonexistent")