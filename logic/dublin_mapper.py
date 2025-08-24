"""
Dublin Core Metadata Mapper
Maps publication data to comprehensive Dublin Core fields
Following Dublin Core Metadata Element Set Version 1.1
"""

from typing import Dict, Any, List
from datetime import datetime

def map_to_dublin_core(publication: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map publication data to comprehensive Dublin Core metadata standard
    
    Args:
        publication: Dictionary containing publication data
        
    Returns:
        Dictionary with extended Dublin Core fields
    """
    # Extract and format authors
    creators = publication.get('authors', [])
    creator_string = '; '.join(creators) if creators else 'Unknown'
    
    # Format date
    year = publication.get('year')
    date_string = str(year) if year else 'Unknown'
    
    # Full date if available
    full_date = publication.get('publication_date', '')
    if not full_date and publication.get('published_online'):
        full_date = format_date_from_parts(publication['published_online'])
    elif not full_date and publication.get('published_print'):
        full_date = format_date_from_parts(publication['published_print'])
    
    # Determine type
    pub_type = publication.get('type', 'article')
    dc_type = map_publication_type(pub_type)
    
    # Format subjects/keywords
    subjects = []
    if publication.get('subjects'):
        subjects.extend(publication['subjects'])
    if publication.get('keywords'):
        subjects.extend(publication['keywords'])
    subjects = list(set(subjects))  # Remove duplicates
    subject_string = '; '.join(subjects) if subjects else ''
    
    # Format identifiers
    identifiers = []
    if publication.get('doi'):
        identifiers.append(format_identifier(publication['doi']))
    if publication.get('openalex_id'):
        identifiers.append(publication['openalex_id'])
    if publication.get('issn'):
        for issn in publication['issn']:
            identifiers.append(f'ISSN:{issn}')
    if publication.get('isbn'):
        for isbn in publication['isbn']:
            identifiers.append(f'ISBN:{isbn}')
    
    # Format contributors (editors, funders, institutions)
    contributors = []
    if publication.get('editor'):
        for editor in publication['editor']:
            contributors.append(f'Editor:{editor}')
    if publication.get('funder'):
        for funder in publication['funder']:
            contributors.append(f'Funder:{funder}')
    if publication.get('institutions'):
        for inst in publication['institutions']:
            contributors.append(f'Institution:{inst}')
    
    # Format coverage (countries, time period)
    coverage = []
    if publication.get('countries'):
        coverage.extend([f'Country:{c}' for c in publication['countries']])
    if year:
        coverage.append(f'Temporal:{year}')
    
    # Format relations
    relations = []
    if publication.get('journal'):
        relations.append(f'Published in: {publication["journal"]}')
    if publication.get('volume'):
        relations.append(f'Volume: {publication["volume"]}')
    if publication.get('issue'):
        relations.append(f'Issue: {publication["issue"]}')
    if publication.get('pages'):
        relations.append(f'Pages: {publication["pages"]}')
    if publication.get('related_works'):
        relations.extend([f'Related:{work}' for work in publication['related_works'][:5]])  # Limit to 5
    
    # Format rights/license
    rights = []
    if publication.get('is_open_access'):
        rights.append('Open Access')
    if publication.get('license'):
        for license_info in publication['license']:
            if isinstance(license_info, dict):
                rights.append(license_info.get('URL', ''))
            else:
                rights.append(str(license_info))
    
    # Build comprehensive Dublin Core mapping
    dublin_core = {
        # Core Dublin Core Elements (15 elements)
        'dc:title': publication.get('title', 'No title'),
        'dc:creator': creator_string,
        'dc:subject': subject_string,
        'dc:description': publication.get('abstract', ''),
        'dc:publisher': publication.get('publisher', ''),
        'dc:contributor': '; '.join(contributors) if contributors else '',
        'dc:date': full_date if full_date else date_string,
        'dc:type': dc_type,
        'dc:format': 'text',  # Most academic publications are text
        'dc:identifier': '; '.join(identifiers),
        'dc:source': publication.get('journal', ''),
        'dc:language': publication.get('language', 'en'),
        'dc:relation': '; '.join(relations),
        'dc:coverage': '; '.join(coverage) if coverage else '',
        'dc:rights': '; '.join(rights) if rights else '',
        
        # Additional metadata (extended) - Keep as separate columns
        'citations': publication.get('citations', 0),
        'year': year if year else '',
        'doi': publication.get('doi', ''),
        'url': publication.get('url', ''),
        'data_source': publication.get('source', ''),
        'original_type': pub_type,
        'volume': publication.get('volume', ''),
        'issue': publication.get('issue', ''),
        'pages': publication.get('pages', ''),
        'issn': '; '.join(publication.get('issn', [])) if publication.get('issn') else '',
        'isbn': '; '.join(publication.get('isbn', [])) if publication.get('isbn') else '',
        'is_open_access': publication.get('is_open_access', False),
        'open_access_url': publication.get('open_access_url', ''),
        'references_count': publication.get('references_count', 0),
        'referenced_works_count': publication.get('referenced_works_count', 0),
        'is_referenced_by_count': publication.get('is_referenced_by_count', 0),
        'mesh_terms': '; '.join([m.get('descriptor_name', '') for m in publication.get('mesh', []) if isinstance(m, dict)]),
        'sustainable_development_goals': '; '.join([sdg.get('display_name', '') for sdg in publication.get('sustainable_development_goals', []) if isinstance(sdg, dict)])
    }
    
    # Add source-specific IDs
    if 'openalex_id' in publication:
        dublin_core['openalex_id'] = publication['openalex_id']
    
    # Add links if available
    if publication.get('link'):
        link_urls = []
        for link in publication['link']:
            if isinstance(link, dict) and 'URL' in link:
                link_urls.append(link['URL'])
        if link_urls:
            dublin_core['alternative_urls'] = '; '.join(link_urls)
    
    return dublin_core

def map_publication_type(original_type: str) -> str:
    """
    Map publication types to Dublin Core type vocabulary
    
    Args:
        original_type: Original publication type
        
    Returns:
        Dublin Core type
    """
    # Comprehensive mappings
    type_mapping = {
        'journal-article': 'Text',
        'article': 'Text',
        'book': 'Text',
        'book-chapter': 'Text',
        'book-section': 'Text',
        'book-part': 'Text',
        'book-series': 'Text',
        'book-set': 'Text',
        'book-track': 'Text',
        'reference-book': 'Text',
        'monograph': 'Text',
        'conference-paper': 'Text',
        'proceedings-article': 'Text',
        'proceedings': 'Text',
        'dataset': 'Dataset',
        'component': 'Dataset',
        'data-set': 'Dataset',
        'software': 'Software',
        'report': 'Text',
        'report-series': 'Text',
        'thesis': 'Text',
        'dissertation': 'Text',
        'preprint': 'Text',
        'posted-content': 'Text',
        'peer-review': 'Text',
        'journal': 'Collection',
        'journal-issue': 'Collection',
        'journal-volume': 'Collection',
        'standard': 'Text',
        'standard-series': 'Text',
        'edited-book': 'Text',
        'reference-entry': 'Text',
        'other': 'Other'
    }
    
    return type_mapping.get(original_type.lower(), 'Text')

def format_identifier(doi: str) -> str:
    """
    Format DOI as proper identifier
    
    Args:
        doi: DOI string
        
    Returns:
        Formatted identifier
    """
    if not doi:
        return ''
    
    # Clean DOI
    doi = doi.strip()
    
    # Ensure DOI has proper prefix
    if not doi.startswith('http'):
        if doi.startswith('10.'):
            return f'https://doi.org/{doi}'
        else:
            return f'DOI:{doi}'
    
    return doi

def format_date_from_parts(date_info: Dict) -> str:
    """
    Format date from date-parts structure
    
    Args:
        date_info: Dictionary with date-parts
        
    Returns:
        Formatted date string
    """
    date_parts = date_info.get('date-parts', [[]])
    if date_parts and date_parts[0]:
        parts = date_parts[0]
        if len(parts) >= 3:
            return f'{parts[0]:04d}-{parts[1]:02d}-{parts[2]:02d}'
        elif len(parts) == 2:
            return f'{parts[0]:04d}-{parts[1]:02d}'
        elif len(parts) == 1:
            return str(parts[0])
    return ''

def export_dublin_core_metadata(publications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert a list of publications to Dublin Core format
    
    Args:
        publications: List of publication dictionaries
        
    Returns:
        List of Dublin Core formatted dictionaries
    """
    return [map_to_dublin_core(pub) for pub in publications]