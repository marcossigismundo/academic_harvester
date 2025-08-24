"""
Logic module initialization
"""

from .metrics import calculate_metrics, calculate_h_index, calculate_g_index
from .dublin_mapper import (
    map_to_dublin_core, 
    export_dublin_core_metadata,
    map_publication_type,
    format_identifier
)
from .export_utils import (
    export_to_csv,
    export_to_csv_chunked,
    export_to_excel_optimized,
    export_for_tainacan,
    validate_export_data,
    prepare_data_for_export
)

__all__ = [
    'calculate_metrics',
    'calculate_h_index', 
    'calculate_g_index',
    'map_to_dublin_core',
    'export_dublin_core_metadata',
    'map_publication_type',
    'format_identifier',
    'export_to_csv',
    'export_to_csv_chunked',
    'export_to_excel_optimized',
    'export_for_tainacan',
    'validate_export_data',
    'prepare_data_for_export'
]