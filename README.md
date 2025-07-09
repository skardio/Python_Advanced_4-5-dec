# SCD2 Delta Table Reader

A Python library for reading snapshots from historical SCD2 (Slowly Changing Dimension Type 2) Delta tables in data lakes. This library provides a clean, easy-to-use interface for data engineers working with SCD2 tables in Bronze, Silver, and Gold layers of a Delta Lake architecture.

## Features

- 📊 **Read SCD2 snapshots** at any point in time or get the latest snapshot
- 🏗️ **Automatic SCD2 detection** - identifies SCD2 tables by their column structure
- 🎯 **Smart column selection** - returns business columns by default, optionally includes technical SCD2 columns
- 🔧 **Flexible architecture** - supports dependency injection and custom implementations
- 🏷️ **Hash key preservation** - always includes hash keys needed for table relationships
- 📋 **Multiple SCD2 patterns** - supports various SCD2 column naming conventions
- 🛡️ **Robust error handling** - clear error messages for common issues
- ⚡ **Optimized queries** - generates efficient SQL for snapshot retrieval

## Installation

```bash
pip install -r requirements.txt
```

### Requirements

- PySpark >= 3.4.0
- Delta Lake >= 2.4.0
- Python >= 3.8

## Quick Start

```python
from factory import get_table_reader_client

# Create a reader client
reader = get_table_reader_client()

# Read latest snapshot from Silver layer
df = reader.read_snapshot_scd2("silver", "customers")

# Read snapshot at specific point in time
df = reader.read_snapshot_scd2(
    "gold", 
    "dim_customer", 
    snapshot_dt="2024-01-01 10:00:00"
)

# Include SCD2 technical columns
df = reader.read_snapshot_scd2(
    "silver", 
    "customers", 
    include_scd2_cols=True
)
```

## Architecture

The library follows a clean architecture with dependency inversion:

```
factory.py                    # Factory for creating configured clients
├── common/
│   ├── protocols.py          # Interfaces for dependency inversion
│   └── spark_driver.py       # Spark operations implementation
├── catalog/
│   └── catalog_service.py    # Catalog operations and SCD2 detection
├── storage/table_readers/
│   ├── table_reader_client.py # Main client interface
│   └── query_service.py      # SQL query building
└── tests/                    # Comprehensive test suite
```

### Core Components

- **TableReaderClient**: Main interface for reading SCD2 snapshots
- **CatalogService**: Handles catalog operations and SCD2 table detection
- **QueryService**: Builds optimized SQL queries for snapshot retrieval
- **SparkDriver**: Manages Spark/Databricks interactions
- **Factory**: Provides easy instantiation with dependency injection

## Usage Examples

### Basic Usage

```python
from factory import create_scd2_reader

# Quick setup
reader = create_scd2_reader()

# Read latest customer data
customers_df = reader.read_snapshot_scd2("silver", "customers")
print(f"Read {customers_df.count()} customer records")
```

### Advanced Usage

```python
from factory import get_table_reader_client
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("MyApp").getOrCreate()
reader = get_table_reader_client(spark_session=spark)

# Read snapshot with all options
df = reader.read_snapshot_scd2(
    dlk_layer="gold",
    table_name="dim_customer",
    snapshot_dt="2024-01-01 12:00:00",
    view_name="customer_snapshot",  # Creates temporary view
    include_scd2_cols=True         # Include technical columns
)

# Use the temporary view
spark.sql("SELECT * FROM customer_snapshot WHERE region = 'Europe'").show()
```

### Table Inspection

```python
# Get information about a table
info = reader.get_table_info("silver", "customers")

print(f"Table exists: {info['exists']}")
print(f"Is SCD2: {info['is_scd2_table']}")
print(f"Business columns: {info['business_columns']}")
print(f"SCD2 columns: {info['scd2_columns']}")

# Get sample data
sample_df = reader.sample_data("silver", "customers", limit=5)
sample_df.show()
```

### Custom Implementations

```python
from catalog.catalog_service import CatalogService

# Custom catalog service with different naming convention
class CustomCatalogService(CatalogService):
    def build_catalog_name(self, dlk_layer: str, table_name: str) -> str:
        return f"prod_{dlk_layer}.{table_name}"

# Use custom implementation
reader = get_table_reader_client(
    catalog_service_class=CustomCatalogService
)
```

## SCD2 Table Support

The library automatically detects SCD2 tables by looking for technical columns such as:

### Standard SCD2 Columns
- `valid_from`, `valid_to`, `is_current`
- `effective_date`, `end_date`, `current_flag`
- `created_at`, `updated_at`, `load_date`
- `scd_start_date`, `scd_end_date`, `version`

### Hash Key Patterns
The library preserves hash keys needed for table relationships:
- `hash_key`, `hashkey`
- `hk_*`, `*_hk`
- `dim_hash_key`

### Business Logic
- **Default behavior**: Returns business columns + hash keys (excludes SCD2 technical columns)
- **With `include_scd2_cols=True`**: Returns all columns including SCD2 technical columns
- **Hash keys**: Always included regardless of `include_scd2_cols` setting

## Generated SQL Examples

### Latest Snapshot Query
```sql
SELECT `customer_id`, `customer_hk`, `name`, `email`
FROM silver.customers
WHERE is_current = true
   OR (is_current IS NULL AND valid_to IS NULL)
   OR (current_flag = 'Y')
   OR (current_flag = true)
   OR (valid_to = '9999-12-31' OR valid_to = '2099-12-31')
```

### Point-in-Time Snapshot Query
```sql
SELECT `customer_id`, `customer_hk`, `name`, `email`
FROM silver.customers
WHERE (
    -- Standard SCD2 with valid_from/valid_to
    (valid_from <= '2024-01-01 10:00:00' AND 
     (valid_to > '2024-01-01 10:00:00' OR valid_to IS NULL OR 
      valid_to = '9999-12-31' OR valid_to = '2099-12-31'))
    OR
    -- Alternative SCD2 with effective_date/end_date
    (effective_date <= '2024-01-01 10:00:00' AND 
     (end_date > '2024-01-01 10:00:00' OR end_date IS NULL OR 
      end_date = '9999-12-31' OR end_date = '2099-12-31'))
    OR
    -- SCD2 with created_at/updated_at pattern
    (created_at <= '2024-01-01 10:00:00' AND 
     (updated_at > '2024-01-01 10:00:00' OR updated_at IS NULL))
)
```

## Error Handling

The library provides clear error messages for common scenarios:

```python
try:
    df = reader.read_snapshot_scd2("silver", "nonexistent_table")
except ValueError as e:
    print(f"Table not found: {e}")

try:
    df = reader.read_snapshot_scd2("bronze", "raw_logs")  # Not SCD2
except ValueError as e:
    print(f"Not an SCD2 table: {e}")
```

## Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-mock

# Run all tests
pytest

# Run specific test files
pytest tests/test_catalog_service.py
pytest tests/test_query_service.py
pytest tests/test_table_reader_client.py
pytest tests/test_integration.py

# Run with coverage
pytest --cov=. --cov-report=html
```

### Test Structure
- **Unit tests**: Individual component testing with mocks
- **Integration tests**: End-to-end workflow testing
- **Mock-based**: No external dependencies required for testing

## Development

### Project Structure
```
scd2-delta-reader/
├── factory.py                 # Factory functions
├── common/                    # Common utilities and protocols
├── catalog/                   # Catalog service
├── storage/table_readers/     # Table reader services  
├── tests/                     # Test suite
├── requirements.txt           # Dependencies
├── example_usage.py           # Usage examples
└── README.md                  # This file
```

### Adding Custom Services

1. **Implement the protocol**:
```python
from common.protocols import CatalogServiceProtocol

class MyCatalogService:
    def __init__(self, spark_driver, **kwargs):
        # Your implementation
        pass
    
    def build_catalog_name(self, dlk_layer: str, table_name: str) -> str:
        # Your custom logic
        pass
```

2. **Use with factory**:
```python
reader = get_table_reader_client(
    catalog_service_class=MyCatalogService,
    custom_param="value"
)
```

## Databricks Usage

In Databricks notebooks, the usage is even simpler:

```python
# Cell 1: Import and setup
from factory import get_table_reader_client

# Create reader (automatically uses active Spark session)
reader = get_table_reader_client()

# Cell 2: Read data
customers_df = reader.read_snapshot_scd2("gold", "dim_customer")
display(customers_df)

# Cell 3: Point-in-time analysis
jan_snapshot = reader.read_snapshot_scd2(
    "gold", "dim_customer", 
    snapshot_dt="2024-01-01",
    view_name="customers_jan1"
)

feb_snapshot = reader.read_snapshot_scd2(
    "gold", "dim_customer", 
    snapshot_dt="2024-02-01",
    view_name="customers_feb1"
)

# Compare snapshots
changes_df = spark.sql("""
    SELECT * FROM customers_feb1 
    WHERE customer_id NOT IN (SELECT customer_id FROM customers_jan1)
""")
display(changes_df)
```

## Performance Considerations

- **Partition pruning**: The generated queries work well with Delta table partitioning
- **Column selection**: Only requested columns are selected, reducing data transfer
- **Predicate pushdown**: Delta Lake optimizations apply to the generated queries
- **Caching**: Consider caching frequently accessed snapshots

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions and support:
- Check the example usage in `example_usage.py`
- Review the test cases for implementation details
- Open an issue for bugs or feature requests