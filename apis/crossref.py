"""
CrossRef API Module - Enhanced Version
Handles all interactions with the CrossRef API for academic publication searches
Supports advanced queries, pagination, and multiple search modes
"""

import requests
import time
from typing import List, Dict, Any
from urllib.parse import quote

# API Configuration - Easy to modify
CROSSREF_BASE_URL = "https://api.crossref.org/works"
USER_AGENT = "Academic-Harvester/1.0 (mailto:your-email@example.com)"
RESULTS_PER_PAGE = 100  # Maximum allowed by CrossRef
MAX_RESULTS = 5000  # Maximum total results to fetch
REQUEST_DELAY = 0.1  # Reduced delay for bulk fetching
MAX_RETRIES = 3  # Number of retries for failed requests

class CrossRefAPI:
    """CrossRef API client for searching academic publications"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT
        })
        self.seen_dois = set()  # Track DOIs to avoid duplicates
    
    def _build_filters(self, params: Dict[str, Any]) -> str:
        """Build filter string from parameters"""
        filters = []
        
        # Year filters
        if params.get('from_year'):
            filters.append(f"from-pub-date:{params['from_year']}")
        if params.get('to_year'):
            filters.append(f"until-pub-date:{params['to_year']}")
        
        # Type filter
        if params.get('doc_type'):
            for doc_type in params['doc_type']:
                filters.append(f"type:{doc_type}")
        
        # Has DOI filter
        if params.get('has_doi'):
            filters.append("has-doi:true")
        
        # Has abstract filter
        if params.get('has_abstract'):
            filters.append("has-abstract:true")
        
        # Open access filter (via license)
        if params.get('open_access_only'):
            filters.append("has-license:true")
        
        return ','.join(filters) if filters else None
    
    def _get_sort_order(self, sort_by: str) -> str:
        """Convert sort preference to API parameter"""
        sort_map = {
            'Relevance': 'relevance',
            'Date (Newest)': 'published:desc',
            'Date (Oldest)': 'published:asc',
            'Citations (High to Low)': 'is-referenced-by-count:desc'
        }
        return sort_map.get(sort_by, 'relevance')
    
    def _make_request(self, params: Dict[str, Any], max_results: int = MAX_RESULTS) -> List[Dict]:
        """Make paginated requests to CrossRef API and return parsed results"""
        all_results = []
        offset = 0
        
        # Set initial parameters
        params['rows'] = RESULTS_PER_PAGE
        
        while len(all_results) < max_results:
            try:
                # Set offset for pagination
                params['offset'] = offset
                
                # Make request with retries
                response = None
                for attempt in range(MAX_RETRIES):
                    try:
                        response = self.session.get(CROSSREF_BASE_URL, params=params, timeout=30)
                        response.raise_for_status()
                        break
                    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                        if attempt == MAX_RETRIES - 1:
                            raise
                        print(f"Retry {attempt + 1}/{MAX_RETRIES} after error: {e}")
                        time.sleep(1)
                
                # Parse response
                data = response.json()
                message = data.get('message', {})
                items = message.get('items', [])
                total_results = message.get('total-results', 0)
                
                print(f"CrossRef: Retrieved {len(items)} items from offset {offset}, total available: {total_results}")
                
                if not items:
                    break
                
                # Parse and deduplicate results
                parsed_items = self._parse_results(items)
                
                # Add only new items (not seen before)
                for item in parsed_items:
                    doi = item.get('doi', '')
                    if doi and doi not in self.seen_dois:
                        self.seen_dois.add(doi)
                        all_results.append(item)
                    elif not doi:
                        # If no DOI, use title for deduplication
                        title = item.get('title', '').lower().strip()
                        if title and title not in self.seen_dois:
                            self.seen_dois.add(title)
                            all_results.append(item)
                
                print(f"CrossRef: Total unique results collected: {len(all_results)}")
                
                # Check if we have enough results or reached the end
                if len(all_results) >= max_results or offset + RESULTS_PER_PAGE >= total_results:
                    break
                
                # Prepare for next page
                offset += RESULTS_PER_PAGE
                
                # Be polite to the API
                time.sleep(REQUEST_DELAY)
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching from CrossRef: {e}")
                break
        
        # Return only the requested number of results
        return all_results[:max_results]
    
    def _parse_results(self, items: List[Dict]) -> List[Dict]:
        """Parse CrossRef results into standardized format"""
        results = []
        
        for item in items:
            # Extract authors
            authors = []
            for author in item.get('author', []):
                name_parts = []
                if 'given' in author:
                    name_parts.append(author['given'])
                if 'family' in author:
                    name_parts.append(author['family'])
                if name_parts:
                    authors.append(' '.join(name_parts))
            
            # Extract year
            date_parts = item.get('published-print', {}).get('date-parts', [[]])
            if not date_parts:
                date_parts = item.get('published-online', {}).get('date-parts', [[]])
            year = date_parts[0][0] if date_parts and date_parts[0] else None
            
            # Extract open access information
            is_open_access = False
            open_access_url = ''
            
            # Check license for open access
            licenses = item.get('license', [])
            for license_info in licenses:
                if isinstance(license_info, dict):
                    license_url = license_info.get('URL', '')
                    if 'creativecommons.org' in license_url:
                        is_open_access = True
                        open_access_url = license_url
                        break
            
            # Check for other OA indicators
            if item.get('is-referenced-by-count', 0) > 0 and not is_open_access:
                # Check if has open link
                links = item.get('link', [])
                for link in links:
                    if isinstance(link, dict):
                        if link.get('content-type') == 'unspecified' and link.get('URL'):
                            is_open_access = True
                            open_access_url = link['URL']
                            break
            
            # Build result
            result = {
                'title': item.get('title', [''])[0] if item.get('title') else 'No title',
                'authors': authors,
                'year': year,
                'journal': item.get('container-title', [''])[0] if item.get('container-title') else '',
                'doi': item.get('DOI', ''),
                'abstract': item.get('abstract', ''),
                'citations': item.get('is-referenced-by-count', 0),
                'url': item.get('URL', ''),
                'publisher': item.get('publisher', ''),
                'type': item.get('type', 'article'),
                'source': 'CrossRef',
                # Additional Dublin Core relevant fields
                'issn': item.get('ISSN', []),
                'isbn': item.get('ISBN', []),
                'volume': item.get('volume', ''),
                'issue': item.get('issue', ''),
                'pages': item.get('page', ''),
                'language': item.get('language', 'en'),
                'subjects': item.get('subject', []),
                'license': item.get('license', []),
                'references_count': item.get('references-count', 0),
                'is_referenced_by_count': item.get('is-referenced-by-count', 0),
                'published_print': item.get('published-print', {}),
                'published_online': item.get('published-online', {}),
                'editor': self._extract_editors(item.get('editor', [])),
                'funder': self._extract_funders(item.get('funder', [])),
                'link': item.get('link', []),
                'is_open_access': is_open_access,
                'open_access_url': open_access_url,
                'score': item.get('score', 0)  # Relevance score
            }
            
            results.append(result)
        
        return results
    
    def _extract_editors(self, editors: List[Dict]) -> List[str]:
        """Extract editor names from CrossRef data"""
        editor_names = []
        for editor in editors:
            name_parts = []
            if 'given' in editor:
                name_parts.append(editor['given'])
            if 'family' in editor:
                name_parts.append(editor['family'])
            if name_parts:
                editor_names.append(' '.join(name_parts))
        return editor_names
    
    def _extract_funders(self, funders: List[Dict]) -> List[str]:
        """Extract funder information from CrossRef data"""
        funder_info = []
        for funder in funders:
            if 'name' in funder:
                funder_info.append(funder['name'])
        return funder_info
    
    def search_by_author(self, author_name: str, from_year: int = None, to_year: int = None, 
                        max_results: int = MAX_RESULTS, extra_params: Dict = None) -> List[Dict]:
        """Search publications by author name"""
        self.seen_dois.clear()  # Clear deduplication set
        
        params = {
            'query.author': author_name,
            'sort': self._get_sort_order(extra_params.get('sort_by', 'Relevance')) if extra_params else 'relevance'
        }
        
        # Add filters
        if extra_params:
            filters = self._build_filters(extra_params)
            if filters:
                params['filter'] = filters
        elif from_year:  # Legacy support
            params['filter'] = f'from-pub-date:{from_year}'
        
        return self._make_request(params, max_results)
    
    def search_by_title(self, title: str, from_year: int = None, to_year: int = None,
                       max_results: int = MAX_RESULTS, extra_params: Dict = None) -> List[Dict]:
        """Search publications by title"""
        self.seen_dois.clear()  # Clear deduplication set
        
        params = {
            'query.title': title,
            'sort': self._get_sort_order(extra_params.get('sort_by', 'Relevance')) if extra_params else 'relevance'
        }
        
        # Add filters
        if extra_params:
            filters = self._build_filters(extra_params)
            if filters:
                params['filter'] = filters
        elif from_year:  # Legacy support
            params['filter'] = f'from-pub-date:{from_year}'
        
        return self._make_request(params, max_results)
    
    def search_by_keyword(self, keyword: str, from_year: int = None, to_year: int = None,
                         max_results: int = MAX_RESULTS, extra_params: Dict = None) -> List[Dict]:
        """Search publications by keyword"""
        self.seen_dois.clear()  # Clear deduplication set
        
        params = {
            'query': keyword,
            'sort': self._get_sort_order(extra_params.get('sort_by', 'Relevance')) if extra_params else 'relevance'
        }
        
        # Add filters
        if extra_params:
            filters = self._build_filters(extra_params)
            if filters:
                params['filter'] = filters
        elif from_year:  # Legacy support
            params['filter'] = f'from-pub-date:{from_year}'
        
        return self._make_request(params, max_results)
    
    def search_by_affiliation(self, affiliation: str, from_year: int = None, to_year: int = None,
                             max_results: int = MAX_RESULTS, extra_params: Dict = None) -> List[Dict]:
        """Search publications by affiliation"""
        self.seen_dois.clear()  # Clear deduplication set
        
        params = {
            'query.affiliation': affiliation,
            'sort': self._get_sort_order(extra_params.get('sort_by', 'Relevance')) if extra_params else 'relevance'
        }
        
        # Add filters
        if extra_params:
            filters = self._build_filters(extra_params)
            if filters:
                params['filter'] = filters
        elif from_year:  # Legacy support
            params['filter'] = f'from-pub-date:{from_year}'
        
        return self._make_request(params, max_results)
    
    def search_all_fields(self, query: str, from_year: int = None, to_year: int = None,
                         max_results: int = MAX_RESULTS, extra_params: Dict = None) -> List[Dict]:
        """Search across all fields"""
        self.seen_dois.clear()  # Clear deduplication set
        
        # For all fields search, use bibliographic query
        params = {
            'query.bibliographic': query,
            'sort': self._get_sort_order(extra_params.get('sort_by', 'Relevance')) if extra_params else 'relevance'
        }
        
        # Add filters
        if extra_params:
            filters = self._build_filters(extra_params)
            if filters:
                params['filter'] = filters
        elif from_year:  # Legacy support
            params['filter'] = f'from-pub-date:{from_year}'
        
        return self._make_request(params, max_results)
    
    def search_advanced(self, query: str, from_year: int = None, to_year: int = None,
                       max_results: int = MAX_RESULTS, extra_params: Dict = None) -> List[Dict]:
        """Advanced search with complex query"""
        self.seen_dois.clear()  # Clear deduplication set
        
        # For advanced search, parse the query to determine fields
        # This is a simplified implementation - could be enhanced
        params = {
            'query': query,
            'sort': self._get_sort_order(extra_params.get('sort_by', 'Relevance')) if extra_params else 'relevance'
        }
        
        # Add filters
        if extra_params:
            filters = self._build_filters(extra_params)
            if filters:
                params['filter'] = filters
        elif from_year:  # Legacy support
            params['filter'] = f'from-pub-date:{from_year}'
        
        return self._make_request(params, max_results)