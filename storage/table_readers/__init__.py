"""
Table reader services for SCD2 Delta tables.
"""

from .table_reader_client import TableReaderClient
from .query_service import QueryService

__all__ = ['TableReaderClient', 'QueryService']