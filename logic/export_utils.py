"""
Export Utilities - Enhanced Version with Large Dataset Support
Handles exports of 1000+ records with proper error handling and chunking
"""

import pandas as pd
import os
from datetime import datetime
import traceback
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows
from typing import List, Dict, Any, Tuple
import time

def prepare_data_for_export(results: List[Dict]) -> pd.DataFrame:
    """
    Prepare and clean data for export, handling all edge cases
    
    Args:
        results: List of publication dictionaries
        
    Returns:
        Cleaned DataFrame ready for export
    """
    # Convert to DataFrame
    df = pd.DataFrame(results)
    
    # Handle list columns - convert to string with semicolon separator
    list_columns = ['authors', 'subjects', 'keywords', 'issn', 'isbn', 
                   'institutions', 'affiliations', 'countries', 'related_works']
    
    for col in list_columns:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: '; '.join(x) if isinstance(x, list) else str(x) if x else '')
    
    # Handle nested dictionaries
    if 'biblio' in df.columns:
        df = df.drop('biblio', axis=1, errors='ignore')
    
    if 'sustainable_development_goals' in df.columns:
        df['sustainable_development_goals'] = df['sustainable_development_goals'].apply(
            lambda x: '; '.join([sdg.get('display_name', '') for sdg in x]) if isinstance(x, list) else ''
        )
    
    if 'mesh' in df.columns:
        df['mesh_terms'] = df['mesh'].apply(
            lambda x: '; '.join([m.get('descriptor_name', '') for m in x if isinstance(m, dict)]) if isinstance(x, list) else ''
        )
        df = df.drop('mesh', axis=1, errors='ignore')
    
    # Clean DOI
    if 'doi' in df.columns:
        df['doi'] = df['doi'].str.replace('https://doi.org/', '', regex=False)
    
    # Ensure boolean columns
    if 'is_open_access' in df.columns:
        df['is_open_access'] = df['is_open_access'].apply(lambda x: 'Yes' if x else 'No')
    
    # Remove problematic columns that might cause issues
    columns_to_drop = ['link', 'license', 'published_online', 'published_print', 
                      'funder', 'editor', 'authorships']
    for col in columns_to_drop:
        df = df.drop(col, axis=1, errors='ignore')
    
    # Replace NaN with empty strings
    df = df.fillna('')
    
    # Ensure all columns are string type to prevent Excel issues
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str)
    
    return df

def export_to_csv_chunked(results: List[Dict], metrics: Dict, chunk_size: int = 1000) -> Tuple[str, str]:
    """
    Export data to CSV with chunking for large datasets
    
    Args:
        results: List of publication dictionaries
        metrics: Citation metrics dictionary
        chunk_size: Number of records per chunk
        
    Returns:
        Tuple of (main_file_path, metrics_file_path)
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    total_records = len(results)
    
    # Ensure directory exists
    os.makedirs("data/resultados", exist_ok=True)
    
    print(f"Starting export of {total_records} records...")
    
    try:
        if total_records <= chunk_size:
            # Small dataset - export directly
            df = prepare_data_for_export(results)
            filename = f"data/resultados/publications_{timestamp}.csv"
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"Exported {total_records} records to {filename}")
        else:
            # Large dataset - export in chunks
            filename = f"data/resultados/publications_{timestamp}_complete.csv"
            
            # Process and write in chunks
            for i in range(0, total_records, chunk_size):
                chunk = results[i:i+chunk_size]
                df_chunk = prepare_data_for_export(chunk)
                
                if i == 0:
                    # First chunk - write with headers
                    df_chunk.to_csv(filename, index=False, encoding='utf-8-sig', mode='w')
                else:
                    # Subsequent chunks - append without headers
                    df_chunk.to_csv(filename, index=False, encoding='utf-8-sig', mode='a', header=False)
                
                print(f"Exported chunk {i//chunk_size + 1}/{(total_records-1)//chunk_size + 1} ({len(chunk)} records)")
                
                # Small delay to prevent memory issues
                time.sleep(0.1)
        
        # Save metrics
        metrics_filename = filename.replace('.csv', '_metrics.csv')
        metrics_df = pd.DataFrame([metrics])
        metrics_df.to_csv(metrics_filename, index=False, encoding='utf-8-sig')
        print(f"Metrics saved to {metrics_filename}")
        
        return filename, metrics_filename
        
    except Exception as e:
        print(f"Error during CSV export: {e}")
        traceback.print_exc()
        
        # Try emergency backup export with minimal processing
        emergency_filename = f"data/resultados/emergency_export_{timestamp}.csv"
        try:
            basic_df = pd.DataFrame(results)
            basic_df.to_csv(emergency_filename, index=False, encoding='utf-8-sig')
            print(f"Emergency export saved to {emergency_filename}")
            return emergency_filename, ""
        except:
            raise

def export_to_excel_optimized(results: List[Dict], metrics: Dict, max_rows_per_sheet: int = 50000) -> str:
    """
    Export to Excel with optimization for large datasets
    
    Args:
        results: List of publication dictionaries
        metrics: Citation metrics dictionary
        max_rows_per_sheet: Maximum rows per Excel sheet
        
    Returns:
        Path to saved Excel file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/resultados/publications_{timestamp}.xlsx"
    total_records = len(results)
    
    # Ensure directory exists
    os.makedirs("data/resultados", exist_ok=True)
    
    print(f"Starting Excel export of {total_records} records...")
    
    try:
        # Prepare data
        df = prepare_data_for_export(results)
        
        # Create Excel writer with xlsxwriter engine for better performance
        with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
            # Write data in sheets if too large
            if total_records <= max_rows_per_sheet:
                df.to_excel(writer, sheet_name='Publications', index=False)
                print(f"Exported {total_records} records to single sheet")
            else:
                # Split into multiple sheets
                num_sheets = (total_records - 1) // max_rows_per_sheet + 1
                for i in range(num_sheets):
                    start_idx = i * max_rows_per_sheet
                    end_idx = min((i + 1) * max_rows_per_sheet, total_records)
                    sheet_name = f'Publications_{i+1}'
                    
                    df.iloc[start_idx:end_idx].to_excel(writer, sheet_name=sheet_name, index=False)
                    print(f"Exported sheet {i+1}/{num_sheets} ({end_idx-start_idx} records)")
            
            # Add metrics sheet
            metrics_df = pd.DataFrame([metrics])
            metrics_df.to_excel(writer, sheet_name='Metrics', index=False)
            
            # Add summary sheet
            summary_data = {
                'Total Records': [total_records],
                'Export Date': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                'Data Sources': ['; '.join(df['source'].unique()) if 'source' in df.columns else 'Unknown'],
                'Year Range': [f"{df['year'].min()}-{df['year'].max()}" if 'year' in df.columns else 'Unknown'],
                'Open Access Count': [len(df[df['is_open_access'] == 'Yes'])] if 'is_open_access' in df.columns else [0]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        print(f"Excel export completed: {filename}")
        return filename
        
    except Exception as e:
        print(f"Error during Excel export: {e}")
        traceback.print_exc()
        
        # Fall back to CSV if Excel fails
        print("Falling back to CSV export...")
        csv_file, _ = export_to_csv_chunked(results, metrics)
        return csv_file

def export_for_tainacan(results: List[Dict], metrics: Dict) -> str:
    """
    Export specifically formatted for Tainacan import
    
    Args:
        results: List of publication dictionaries
        metrics: Citation metrics dictionary
        
    Returns:
        Path to saved file
    """
    from logic.dublin_mapper import map_to_dublin_core
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/resultados/tainacan_import_{timestamp}.csv"
    
    # Ensure directory exists
    os.makedirs("data/resultados", exist_ok=True)
    
    print(f"Preparing Tainacan export for {len(results)} records...")
    
    try:
        # Map to Dublin Core
        dublin_core_data = []
        for i, pub in enumerate(results):
            if i % 100 == 0:
                print(f"Processing record {i}/{len(results)}...")
            dublin_core_data.append(map_to_dublin_core(pub))
        
        # Convert to DataFrame
        df = pd.DataFrame(dublin_core_data)
        
        # Ensure all required Tainacan columns are present
        required_columns = [
            'dc:title', 'dc:creator', 'dc:subject', 'dc:description',
            'dc:publisher', 'dc:contributor', 'dc:date', 'dc:type',
            'dc:format', 'dc:identifier', 'dc:source', 'dc:language',
            'dc:relation', 'dc:coverage', 'dc:rights'
        ]
        
        for col in required_columns:
            if col not in df.columns:
                df[col] = ''
        
        # Reorder columns with Dublin Core first
        dublin_cols = [col for col in df.columns if col.startswith('dc:')]
        other_cols = [col for col in df.columns if not col.startswith('dc:')]
        df = df[dublin_cols + other_cols]
        
        # Export with UTF-8 BOM for proper character encoding
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        
        print(f"Tainacan export completed: {filename}")
        return filename
        
    except Exception as e:
        print(f"Error during Tainacan export: {e}")
        traceback.print_exc()
        
        # Fall back to standard CSV
        csv_file, _ = export_to_csv_chunked(results, metrics)
        return csv_file

def validate_export_data(results: List[Dict]) -> Tuple[bool, List[str]]:
    """
    Validate data before export to identify potential issues
    
    Args:
        results: List of publication dictionaries
        
    Returns:
        Tuple of (is_valid, list_of_warnings)
    """
    warnings = []
    
    if not results:
        warnings.append("No data to export")
        return False, warnings
    
    # Check for required fields
    sample = results[0] if results else {}
    if 'title' not in sample:
        warnings.append("Missing 'title' field in data")
    
    # Check data size
    if len(results) > 10000:
        warnings.append(f"Large dataset ({len(results)} records) - export may take several minutes")
    
    # Check for problematic characters
    for i, record in enumerate(results[:10]):  # Check first 10 records
        if 'title' in record and record['title']:
            if '\x00' in str(record['title']):
                warnings.append(f"Record {i} contains null characters")
    
    is_valid = len([w for w in warnings if "No data" in w]) == 0
    return is_valid, warnings

# Main export function to be called from app.py
def export_to_csv(results: List[Dict], metrics: Dict) -> Tuple[str, str]:
    """
    Main export function with automatic handling of large datasets
    
    Args:
        results: List of publication dictionaries
        metrics: Citation metrics dictionary
        
    Returns:
        Tuple of (main_file_path, metrics_file_path)
    """
    # Validate data first
    is_valid, warnings = validate_export_data(results)
    
    if warnings:
        for warning in warnings:
            print(f"Warning: {warning}")
    
    if not is_valid:
        raise ValueError("Invalid data for export")
    
    # Choose export method based on size
    if len(results) <= 1000:
        # Small dataset - standard export
        return export_to_csv_chunked(results, metrics, chunk_size=1000)
    else:
        # Large dataset - chunked export
        return export_to_csv_chunked(results, metrics, chunk_size=500)