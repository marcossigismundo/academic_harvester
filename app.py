"""
Academic Harvester - Main Streamlit Application
A lightweight tool for searching and analyzing academic publications
Enhanced with advanced search capabilities
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import os
import time
import traceback
from apis.crossref import CrossRefAPI
from apis.openalex import OpenAlexAPI
from logic.metrics import calculate_metrics
from logic.dublin_mapper import map_to_dublin_core

# Configure Streamlit page
st.set_page_config(
    page_title="Academic Harvester",
    page_icon="📚",
    layout="wide"
)

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = []
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False
if 'last_query' not in st.session_state:
    st.session_state.last_query = {}
if 'export_data' not in st.session_state:
    st.session_state.export_data = None
if 'export_metrics' not in st.session_state:
    st.session_state.export_metrics = None

def build_advanced_query(params):
    """Build advanced query string from parameters"""
    query_parts = []
    
    # Main query with boolean operators
    if params.get('main_query'):
        query_parts.append(params['main_query'])
    
    # Additional fields for combined search
    if params.get('author_query'):
        query_parts.append(f"author:({params['author_query']})")
    
    if params.get('title_query'):
        query_parts.append(f"title:({params['title_query']})")
    
    if params.get('abstract_query'):
        query_parts.append(f"abstract:({params['abstract_query']})")
    
    if params.get('affiliation_query'):
        query_parts.append(f"affiliation:({params['affiliation_query']})")
    
    if params.get('journal_query'):
        query_parts.append(f"container-title:({params['journal_query']})")
    
    # Combine with boolean operator
    operator = params.get('boolean_operator', 'AND')
    final_query = f" {operator} ".join(query_parts) if query_parts else ""
    
    return final_query

def perform_search(params):
    """Execute search based on parameters"""
    results = []
    
    # Store search parameters
    st.session_state.last_query = params
    
    # Initialize API
    if params['source'] == "CrossRef":
        api = CrossRefAPI()
    else:
        api = OpenAlexAPI()
    
    # Perform search based on search mode
    if params['search_mode'] == 'simple':
        # Simple search
        if params['search_type'] == "Author":
            results = api.search_by_author(
                params['query'], 
                params.get('from_year'),
                params.get('to_year'),
                params.get('max_results', 100),
                params
            )
        elif params['search_type'] == "Title":
            results = api.search_by_title(
                params['query'],
                params.get('from_year'),
                params.get('to_year'),
                params.get('max_results', 100),
                params
            )
        elif params['search_type'] == "Keyword":
            results = api.search_by_keyword(
                params['query'],
                params.get('from_year'),
                params.get('to_year'),
                params.get('max_results', 100),
                params
            )
        elif params['search_type'] == "Affiliation":
            results = api.search_by_affiliation(
                params['query'],
                params.get('from_year'),
                params.get('to_year'),
                params.get('max_results', 100),
                params
            )
        else:  # All Fields
            results = api.search_all_fields(
                params['query'],
                params.get('from_year'),
                params.get('to_year'),
                params.get('max_results', 100),
                params
            )
    else:
        # Advanced search
        advanced_query = build_advanced_query(params)
        results = api.search_advanced(
            advanced_query,
            params.get('from_year'),
            params.get('to_year'),
            params.get('max_results', 100),
            params
        )
    
    return results

def export_data(results, metrics, export_format):
    """Export data in the specified format with proper CSV handling"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("data/resultados", exist_ok=True)
    
    # Prepare DataFrame
    df = pd.DataFrame(results)
    
    # Handle list columns - convert to semicolon-separated strings
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].apply(
                lambda x: '; '.join(map(str, x)) if isinstance(x, list) else str(x) if x else ''
            )
    
    # Clean problematic characters that break CSV
    text_columns = ['title', 'abstract', 'description', 'journal', 'publisher']
    for col in text_columns:
        if col in df.columns:
            # Remove line breaks and tabs
            df[col] = df[col].str.replace('\n', ' ', regex=False)
            df[col] = df[col].str.replace('\r', ' ', regex=False)
            df[col] = df[col].str.replace('\t', ' ', regex=False)
            # Clean multiple spaces
            df[col] = df[col].str.replace('  +', ' ', regex=True)
            # Remove any null bytes
            df[col] = df[col].str.replace('\x00', '', regex=False)
    
    # Clean data - replace NaN with empty strings
    df = df.fillna('')
    
    export_files = []
    
    if export_format == "CSV":
        # Export main data with proper quoting
        filename = f"data/resultados/publications_{timestamp}.csv"
        df.to_csv(
            filename, 
            index=False, 
            encoding='utf-8-sig',
            sep=',',
            quoting=1,  # QUOTE_ALL - quotes all fields
            quotechar='"',
            escapechar='\\',
            doublequote=True  # Escape quotes by doubling them
        )
        
        # Export metrics
        metrics_filename = f"data/resultados/metrics_{timestamp}.csv"
        metrics_df = pd.DataFrame([metrics])
        metrics_df.to_csv(
            metrics_filename, 
            index=False, 
            encoding='utf-8-sig',
            quoting=1
        )
        
        export_files = [
            (filename, "Publications CSV"),
            (metrics_filename, "Metrics CSV")
        ]
    
    elif export_format == "Excel":
        filename = f"data/resultados/publications_{timestamp}.xlsx"
        
        # Use xlsxwriter for better control
        with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
            # Get workbook
            workbook = writer.book
            
            # Define formats
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#D3D3D3',
                'border': 1
            })
            
            # Write data in chunks if too large
            max_rows = 50000
            if len(df) > max_rows:
                for i in range(0, len(df), max_rows):
                    sheet_name = f'Publications_{i//max_rows + 1}'
                    df.iloc[i:i+max_rows].to_excel(
                        writer, 
                        sheet_name=sheet_name, 
                        index=False,
                        freeze_panes=(1, 0)  # Freeze header row
                    )
            else:
                df.to_excel(
                    writer, 
                    sheet_name='Publications', 
                    index=False,
                    freeze_panes=(1, 0)
                )
            
            # Add metrics sheet
            metrics_df = pd.DataFrame([metrics])
            metrics_df.to_excel(writer, sheet_name='Metrics', index=False)
        
        export_files = [(filename, "Excel File")]
    
    else:  # Tainacan CSV
        filename = f"data/resultados/tainacan_{timestamp}.csv"
        dublin_data = [map_to_dublin_core(pub) for pub in results]
        dublin_df = pd.DataFrame(dublin_data)
        
        # Clean text fields for Tainacan
        for col in dublin_df.columns:
            if dublin_df[col].dtype == 'object':
                dublin_df[col] = dublin_df[col].astype(str)
                # Remove problematic characters
                dublin_df[col] = dublin_df[col].str.replace('\n', ' ', regex=False)
                dublin_df[col] = dublin_df[col].str.replace('\r', ' ', regex=False)
                dublin_df[col] = dublin_df[col].str.replace('\t', ' ', regex=False)
                dublin_df[col] = dublin_df[col].str.replace('  +', ' ', regex=True)
        
        dublin_df.to_csv(
            filename, 
            index=False, 
            encoding='utf-8-sig',
            sep=',',
            quoting=1,  # Quote all fields
            quotechar='"',
            doublequote=True
        )
        
        export_files = [(filename, "Tainacan Import")]
    
    return export_files

# Main UI
st.title("📚 Academic Harvester - Enhanced Search")
st.markdown("Advanced search and analysis tool for academic publications")

# Search mode selector
search_mode = st.radio(
    "Search Mode",
    ["Simple Search", "Advanced Search"],
    horizontal=True,
    help="Simple: Quick search in one field | Advanced: Complex multi-field search"
)

if search_mode == "Simple Search":
    # Simple search interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_type = st.selectbox(
            "Search Type",
            ["Author", "Title", "Keyword", "Affiliation", "All Fields"],
            help="Choose where to search. 'All Fields' searches everywhere."
        )
        
        query = st.text_input(
            f"Enter {search_type}",
            placeholder=f"Type {search_type.lower()} here...",
            help=f"Enter the {search_type.lower()} you want to search for"
        )
    
    with col2:
        source = st.selectbox(
            "Data Source",
            ["CrossRef", "OpenAlex"],
            help="Select which API to use"
        )
        
        # Year range
        current_year = datetime.now().year
        year_col1, year_col2 = st.columns(2)
        with year_col1:
            from_year = st.number_input(
                "From Year",
                min_value=1900,
                max_value=current_year,
                value=current_year - 10,
                help="Start year"
            )
        with year_col2:
            to_year = st.number_input(
                "To Year",
                min_value=1900,
                max_value=current_year,
                value=current_year,
                help="End year"
            )
    
    # Advanced filters in expander
    with st.expander("⚙️ Advanced Filters"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            open_access_only = st.checkbox(
                "Open Access Only",
                help="Show only open access publications"
            )
            
            has_abstract = st.checkbox(
                "Has Abstract",
                help="Only publications with abstracts"
            )
        
        with col2:
            max_results = st.number_input(
                "Maximum Results",
                min_value=10,
                max_value=5000,
                value=500,
                step=50,
                help="Maximum number of results to fetch"
            )
            
            min_citations = st.number_input(
                "Minimum Citations",
                min_value=0,
                value=0,
                help="Minimum citation count (OpenAlex only)"
            )
        
        with col3:
            sort_by = st.selectbox(
                "Sort By",
                ["Relevance", "Date (Newest)", "Date (Oldest)", "Citations (High to Low)"],
                help="How to order results"
            )
            
            doc_type = st.multiselect(
                "Document Types",
                ["journal-article", "book-chapter", "conference-paper", "preprint", "report"],
                help="Filter by document type"
            )
    
    # Search button
    search_button = st.button("🔍 Search", type="primary", use_container_width=True)
    
    # Build search parameters
    search_params = {
        'search_mode': 'simple',
        'search_type': search_type,
        'query': query,
        'source': source,
        'from_year': from_year,
        'to_year': to_year,
        'open_access_only': open_access_only,
        'has_abstract': has_abstract,
        'max_results': max_results,
        'min_citations': min_citations,
        'sort_by': sort_by,
        'doc_type': doc_type
    }

else:
    # Advanced search interface
    st.markdown("### 🔬 Advanced Multi-Field Search")
    st.info("Use boolean operators (AND, OR, NOT) to combine search terms. Leave fields empty to skip them.")
    
    # Boolean operator selector
    boolean_operator = st.radio(
        "Combine fields with:",
        ["AND", "OR"],
        horizontal=True,
        help="AND: All conditions must match | OR: Any condition can match"
    )
    
    # Multi-field search
    col1, col2 = st.columns(2)
    
    with col1:
        main_query = st.text_input(
            "Main Query (All Fields)",
            placeholder="e.g., machine learning NOT deep learning",
            help="Search across all fields. Use AND, OR, NOT operators."
        )
        
        author_query = st.text_input(
            "Author(s)",
            placeholder="e.g., Silva OR Santos",
            help="Author names. Use OR for multiple authors."
        )
        
        title_query = st.text_input(
            "Title Contains",
            placeholder="e.g., COVID-19 AND Brazil",
            help="Words in the title"
        )
    
    with col2:
        affiliation_query = st.text_input(
            "Affiliation/Institution",
            placeholder="e.g., University of São Paulo",
            help="Author affiliation or institution"
        )
        
        journal_query = st.text_input(
            "Journal/Source",
            placeholder="e.g., Nature OR Science",
            help="Publication source"
        )
        
        abstract_query = st.text_input(
            "Abstract Contains",
            placeholder="e.g., methodology AND results",
            help="Words in the abstract"
        )
    
    # Source and year range
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        source = st.selectbox(
            "Data Source",
            ["OpenAlex", "CrossRef"],
            help="OpenAlex recommended for advanced search"
        )
    
    with col2:
        current_year = datetime.now().year
        from_year = st.number_input(
            "From Year",
            min_value=1900,
            max_value=current_year,
            value=current_year - 5
        )
    
    with col3:
        to_year = st.number_input(
            "To Year",
            min_value=1900,
            max_value=current_year,
            value=current_year
        )
    
    # Advanced filters
    with st.expander("⚙️ Additional Filters"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            open_access_only = st.checkbox("Open Access Only")
            has_abstract = st.checkbox("Has Abstract")
            has_doi = st.checkbox("Has DOI")
        
        with col2:
            max_results = st.number_input(
                "Maximum Results",
                min_value=10,
                max_value=5000,
                value=1000,
                step=100
            )
            min_citations = st.number_input(
                "Minimum Citations",
                min_value=0,
                value=0
            )
        
        with col3:
            sort_by = st.selectbox(
                "Sort By",
                ["Relevance", "Date (Newest)", "Date (Oldest)", "Citations (High to Low)"]
            )
            doc_type = st.multiselect(
                "Document Types",
                ["journal-article", "book-chapter", "conference-paper", "preprint", "report"]
            )
    
    # Search button
    search_button = st.button("🔍 Advanced Search", type="primary", use_container_width=True)
    
    # Build search parameters
    search_params = {
        'search_mode': 'advanced',
        'main_query': main_query,
        'author_query': author_query,
        'title_query': title_query,
        'abstract_query': abstract_query,
        'affiliation_query': affiliation_query,
        'journal_query': journal_query,
        'boolean_operator': boolean_operator,
        'source': source,
        'from_year': from_year,
        'to_year': to_year,
        'open_access_only': open_access_only,
        'has_abstract': has_abstract,
        'has_doi': has_doi,
        'max_results': max_results,
        'min_citations': min_citations,
        'sort_by': sort_by,
        'doc_type': doc_type
    }

# Perform search
if search_button:
    # Validate input
    if search_mode == "Simple Search" and not query:
        st.error("Please enter a search term.")
    elif search_mode == "Advanced Search" and not any([main_query, author_query, title_query, 
                                                       abstract_query, affiliation_query, journal_query]):
        st.error("Please enter at least one search term.")
    else:
        with st.spinner(f"Searching {search_params['source']} for up to {search_params['max_results']} publications..."):
            try:
                # Create progress placeholder
                progress_text = st.empty()
                progress_bar = st.progress(0)
                
                # Perform search
                results = perform_search(search_params)
                
                # Apply post-search filters
                if search_params.get('open_access_only'):
                    original_count = len(results)
                    results = [r for r in results if r.get('is_open_access', False)]
                    if original_count > len(results):
                        st.info(f"Filtered {original_count - len(results)} non-open access publications")
                
                if search_params.get('has_abstract'):
                    results = [r for r in results if r.get('abstract', '').strip()]
                
                if search_params.get('has_doi'):
                    results = [r for r in results if r.get('doi', '').strip()]
                
                if search_params.get('min_citations', 0) > 0:
                    results = [r for r in results if r.get('citations', 0) >= search_params['min_citations']]
                
                if search_params.get('doc_type'):
                    results = [r for r in results if r.get('type', '') in search_params['doc_type']]
                
                st.session_state.results = results
                st.session_state.search_performed = True
                
                # Clear progress
                progress_text.empty()
                progress_bar.empty()
                
                if results:
                    st.success(f"Found {len(results)} unique results!")
                    
                    # Show deduplication info
                    unique_dois = len(set([r.get('doi', '') for r in results if r.get('doi')]))
                    if unique_dois > 0:
                        st.info(f"✓ {unique_dois} publications with unique DOIs")
                else:
                    st.warning("No results found. Try different search terms or broaden your filters.")
                    
            except Exception as e:
                st.error(f"Error during search: {str(e)}")
                progress_text.empty()
                progress_bar.empty()

# Display results
if st.session_state.search_performed and st.session_state.results:
    st.markdown("---")
    st.subheader("📊 Search Results")
    
    # Show search query used
    with st.expander("🔍 Search Query Details"):
        st.json(st.session_state.last_query)
    
    # Convert results to DataFrame for display
    display_data = []
    for r in st.session_state.results:
        display_data.append({
            'Title': r.get('title', 'N/A'),
            'Authors': ', '.join(r.get('authors', [])) if isinstance(r.get('authors'), list) else r.get('authors', 'N/A'),
            'Year': r.get('year', 'N/A'),
            'Journal': r.get('journal', 'N/A'),
            'Citations': r.get('citations', 0),
            'DOI': r.get('doi', 'N/A'),
            'Type': r.get('type', 'N/A'),
            'Open Access': '✓' if r.get('is_open_access', False) else '✗'
        })
    
    df_display = pd.DataFrame(display_data)
    st.dataframe(df_display, use_container_width=True)
    
    # Calculate metrics
    st.markdown("---")
    st.subheader("📈 Citation Metrics")
    
    citations = [r.get('citations', 0) for r in st.session_state.results]
    metrics = calculate_metrics(citations)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Publications", metrics['total_publications'])
    with col2:
        st.metric("Total Citations", metrics['total_citations'])
    with col3:
        st.metric("h-index", metrics['h_index'])
    with col4:
        st.metric("g-index", metrics['g_index'])
    
    st.metric("Average Citations per Paper", f"{metrics['avg_citations']:.2f}")
    
    # Store metrics for export
    st.session_state.export_metrics = metrics
    
    # Export section
    st.markdown("---")
    st.subheader("📥 Export Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        export_format = st.selectbox(
            "Export Format",
            ["CSV", "Excel", "Tainacan CSV"],
            help="Choose export format"
        )
    
    with col2:
        st.info(f"📊 {len(st.session_state.results)} records")
    
    with col3:
        num_records = len(st.session_state.results)
        if num_records < 500:
            time_estimate = "< 5 seconds"
        elif num_records < 2000:
            time_estimate = "10-30 seconds"
        else:
            time_estimate = "1-2 minutes"
        st.info(f"⏱️ {time_estimate}")
    
    # Export button
    if st.button("💾 Export Data", type="primary", use_container_width=True):
        # Create container for progress feedback
        export_container = st.container()
        
        with export_container:
            with st.spinner("Processing export..."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # Step 1: Prepare data
                    status_text.text("Preparing data...")
                    progress_bar.progress(25)
                    time.sleep(0.5)  # Give visual feedback
                    
                    # Step 2: Export
                    status_text.text(f"Exporting {len(st.session_state.results)} records to {export_format}...")
                    progress_bar.progress(50)
                    
                    export_files = export_data(
                        st.session_state.results,
                        st.session_state.export_metrics,
                        export_format
                    )
                    
                    # Step 3: Prepare downloads
                    status_text.text("Preparing downloads...")
                    progress_bar.progress(75)
                    time.sleep(0.5)
                    
                    # Store in session state
                    st.session_state.export_data = export_files
                    
                    # Complete
                    progress_bar.progress(100)
                    status_text.text("Export completed!")
                    time.sleep(0.5)
                    
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Show success and download buttons
                    st.success(f"✅ Export completed! {len(st.session_state.results)} records processed.")
                    
                    # Display download buttons
                    download_cols = st.columns(len(export_files))
                    for idx, (filepath, label) in enumerate(export_files):
                        if os.path.exists(filepath):
                            with open(filepath, 'rb') as f:
                                file_data = f.read()
                            
                            file_size = len(file_data) / 1024
                            size_str = f"{file_size:.1f} KB" if file_size < 1024 else f"{file_size/1024:.1f} MB"
                            
                            with download_cols[idx]:
                                st.download_button(
                                    label=f"📥 {label}\n({size_str})",
                                    data=file_data,
                                    file_name=os.path.basename(filepath),
                                    mime="text/csv" if filepath.endswith('.csv') else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    key=f"download_{idx}_{datetime.now().timestamp()}"
                                )
                
                except Exception as e:
                    progress_bar.empty()
                    status_text.empty()
                    st.error(f"❌ Export failed: {str(e)}")
                    st.code(traceback.format_exc())
                    
                    # Try emergency export
                    try:
                        st.warning("Attempting emergency export...")
                        emergency_file = f"data/resultados/emergency_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                        pd.DataFrame(st.session_state.results).to_csv(emergency_file, index=False, encoding='utf-8-sig')
                        
                        with open(emergency_file, 'rb') as f:
                            st.download_button(
                                "📥 Download Emergency Export",
                                data=f.read(),
                                file_name=os.path.basename(emergency_file),
                                mime="text/csv"
                            )
                    except Exception as e2:
                        st.error(f"Emergency export also failed: {str(e2)}")

# Footer
st.markdown("---")
st.markdown("*Academic Harvester v4.0 - Enhanced search capabilities for comprehensive results*")