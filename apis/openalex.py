"""
OpenAlex API Module - Enhanced Version
Handles all interactions with the OpenAlex API for academic publication searches
Supports advanced queries, filters, and large-scale data retrieval
"""

import requests
import time
from typing import List, Dict, Any
from urllib.parse import urlencode, quote

# API Configuration - Easy to modify
OPENALEX_BASE_URL = "https://api.openalex.org/works"
USER_EMAIL = "your-email@example.com"  # Change this to your email
RESULTS_PER_PAGE = 200  # OpenAlex allows up to 200 per page
MAX_RESULTS = 5000  # Maximum total results to fetch
REQUEST_DELAY = 0.05  # OpenAlex is generous with rate limits
MAX_RETRIES = 3  # Number of retries for failed requests

class OpenAlexAPI:
    """OpenAlex API client for searching academic publications"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': f'Academic-Harvester/1.0 (mailto:{USER_EMAIL})'
        })
        self.seen_ids = set()  # Track IDs to avoid duplicates
    
    def _build_filters(self, base_filters: List[str], params: Dict[str, Any]) -> List[str]:
        """Build filter list from parameters"""
        filters = base_filters.copy()
        
        # Year filters
        if params.get('from_year') and params.get('to_year'):
            filters.append(f'publication_year:{params["from_year"]}-{params["to_year"]}')
        elif params.get('from_year'):
            filters.append(f'publication_year:>{params["from_year"]-1}')
        elif params.get('to_year'):
            filters.append(f'publication_year:<{params["to_year"]+1}')
        
        # Type filter
        if params.get('doc_type'):
            type_filters = []
            for doc_type in params['doc_type']:
                # Map CrossRef types to OpenAlex types
                type_map = {
                    'journal-article': 'article',
                    'book-chapter': 'book-chapter',
                    'conference-paper': 'proceedings-article',
                    'preprint': 'preprint',
                    'report': 'report'
                }
                oa_type = type_map.get(doc_type, doc_type)
                type_filters.append(f'type:{oa_type}')
            if type_filters:
                filters.append(f'({"|".join(type_filters)})')
        
        # Open access filter
        if params.get('open_access_only'):
            filters.append('is_oa:true')
        
        # Has DOI filter
        if params.get('has_doi'):
            filters.append('has_doi:true')
        
        # Minimum citations filter
        if params.get('min_citations', 0) > 0:
            filters.append(f'cited_by_count:>{params["min_citations"]-1}')
        
        return filters
    
    def _get_sort_order(self, sort_by: str) -> str:
        """Convert sort preference to API parameter"""
        sort_map = {
            'Relevance': 'relevance_score:desc',
            'Date (Newest)': 'publication_date:desc',
            'Date (Oldest)': 'publication_date:asc',
            'Citations (High to Low)': 'cited_by_count:desc'
        }
        return sort_map.get(sort_by, 'relevance_score:desc')
    
    def _make_request(self, params: Dict[str, Any], max_results: int = MAX_RESULTS) -> List[Dict]:
        """Make paginated requests to OpenAlex API and return parsed results"""
        all_results = []
        page = 1
        
        # Add default parameters
        params['per-page'] = RESULTS_PER_PAGE
        params['mailto'] = USER_EMAIL
        
        while len(all_results) < max_results:
            try:
                # Set page for pagination
                params['page'] = page
                
                # Make request with retries
                response = None
                for attempt in range(MAX_RETRIES):
                    try:
                        response = self.session.get(OPENALEX_BASE_URL, params=params, timeout=30)
                        response.raise_for_status()
                        break
                    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                        if attempt == MAX_RETRIES - 1:
                            raise
                        print(f"Retry {attempt + 1}/{MAX_RETRIES} after error: {e}")
                        time.sleep(1)
                
                # Parse response
                data = response.json()
                meta = data.get('meta', {})
                items = data.get('results', [])
                total_count = meta.get('count', 0)
                
                print(f"OpenAlex: Retrieved {len(items)} items from page {page}, total available: {total_count}")
                
                if not items:
                    break
                
                # Parse and deduplicate results
                parsed_items = self._parse_results(items)
                
                # Add only new items (not seen before)
                for item in parsed_items:
                    # Use OpenAlex ID for deduplication
                    item_id = item.get('openalex_id', '')
                    doi = item.get('doi', '')
                    
                    # Try DOI first, then OpenAlex ID
                    if doi and doi not in self.seen_ids:
                        self.seen_ids.add(doi)
                        all_results.append(item)
                    elif item_id and item_id not in self.seen_ids:
                        self.seen_ids.add(item_id)
                        all_results.append(item)
                    elif not doi and not item_id:
                        # If neither ID available, use title
                        title = item.get('title', '').lower().strip()
                        if title and title not in self.seen_ids:
                            self.seen_ids.add(title)
                            all_results.append(item)
                
                print(f"OpenAlex: Total unique results collected: {len(all_results)}")
                
                # Check if we have enough results or reached the end
                if len(all_results) >= max_results or page * RESULTS_PER_PAGE >= total_count:
                    break
                
                # Prepare for next page
                page += 1
                
                # Be polite to the API
                time.sleep(REQUEST_DELAY)
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching from OpenAlex: {e}")
                break
        
        # Return only the requested number of results
        return all_results[:max_results]
    
    def _parse_results(self, items: List[Dict]) -> List[Dict]:
        """Parse OpenAlex results into standardized format"""
        results = []
        
        for item in items:
            # Extract authors
            authors = []
            affiliations = []
            for authorship in item.get('authorships', []):
                author = authorship.get('author', {})
                if author.get('display_name'):
                    authors.append(author['display_name'])
                
                # Extract affiliations
                for inst in authorship.get('institutions', []):
                    if inst.get('display_name'):
                        affiliations.append(inst['display_name'])
            
            # Extract journal/source
            source = item.get('primary_location', {})
            journal = ''
            issn = []
            if source.get('source'):
                journal = source['source'].get('display_name', '')
                issn = source['source'].get('issn', [])
            
            # Extract keywords/concepts
            concepts = []
            for concept in item.get('concepts', []):
                if concept.get('display_name') and concept.get('score', 0) > 0.3:  # Only high-relevance concepts
                    concepts.append(concept['display_name'])
            
            # Extract institutions
            institutions = list(set(affiliations))  # Remove duplicates
            
            # Extract open access info
            open_access = item.get('open_access', {})
            is_open_access = open_access.get('is_oa', False)
            oa_url = open_access.get('oa_url', '')
            
            # Build result
            result = {
                'title': item.get('title', 'No title'),
                'authors': authors,
                'year': item.get('publication_year'),
                'journal': journal,
                'doi': item.get('doi', '').replace('https://doi.org/', ''),
                'abstract': item.get('abstract', ''),  # Note: OpenAlex may provide abstracts in some cases
                'citations': item.get('cited_by_count', 0),
                'url': item.get('doi', ''),
                'publisher': '',  # Not directly available
                'type': item.get('type', 'article'),
                'source': 'OpenAlex',
                'openalex_id': item.get('id', ''),
                # Additional Dublin Core relevant fields
                'issn': issn,
                'language': item.get('language', 'en'),
                'subjects': concepts,
                'keywords': concepts,  # Using concepts as keywords
                'institutions': institutions,
                'affiliations': affiliations,
                'is_open_access': is_open_access,
                'open_access_url': oa_url,
                'referenced_works_count': len(item.get('referenced_works', [])),
                'related_works': item.get('related_works', [])[:5],  # Limit to 5
                'publication_date': item.get('publication_date', ''),
                'countries': self._extract_countries(item.get('authorships', [])),
                'sustainable_development_goals': item.get('sustainable_development_goals', []),
                'mesh': item.get('mesh', []),
                'biblio': item.get('biblio', {}),
                'score': item.get('relevance_score', 0)  # Relevance score
            }
            
            # Extract volume, issue, pages from biblio
            biblio = item.get('biblio', {})
            if biblio:
                result['volume'] = biblio.get('volume', '')
                result['issue'] = biblio.get('issue', '')
                result['first_page'] = biblio.get('first_page', '')
                result['last_page'] = biblio.get('last_page', '')
                if result['first_page'] and result['last_page']:
                    result['pages'] = f"{result['first_page']}-{result['last_page']}"
                else:
                    result['pages'] = result['first_page'] or result['last_page'] or ''
            
            results.append(result)
        
        return results
    
    def _extract_countries(self, authorships: List[Dict]) -> List[str]:
        """Extract unique countries from authorships"""
        countries = set()
        for authorship in authorships:
            for inst in authorship.get('institutions', []):
                if inst.get('country_code'):
                    countries.add(inst['country_code'])
        return list(countries)
    
    def _parse_advanced_query(self, query: str) -> Dict[str, str]:
        """Parse advanced query into field-specific searches"""
        # This is a simplified parser - could be enhanced
        parts = {}
        
        # Extract field-specific queries
        if 'author:' in query:
            start = query.find('author:') + 7
            end = query.find(' ', start) if ' ' in query[start:] else len(query)
            parts['author'] = query[start:end].strip('()')
        
        if 'title:' in query:
            start = query.find('title:') + 6
            end = query.find(' ', start) if ' ' in query[start:] else len(query)
            parts['title'] = query[start:end].strip('()')
        
        if 'abstract:' in query:
            start = query.find('abstract:') + 9
            end = query.find(' ', start) if ' ' in query[start:] else len(query)
            parts['abstract'] = query[start:end].strip('()')
        
        if 'affiliation:' in query:
            start = query.find('affiliation:') + 12
            end = query.find(' ', start) if ' ' in query[start:] else len(query)
            parts['affiliation'] = query[start:end].strip('()')
        
        return parts
    
    def search_by_author(self, author_name: str, from_year: int = None, to_year: int = None,
                        max_results: int = MAX_RESULTS, extra_params: Dict = None) -> List[Dict]:
        """Search publications by author name"""
        self.seen_ids.clear()  # Clear deduplication set
        
        # Build filters
        filters = [f'display_name.search:{author_name}']
        if extra_params:
            extra_params['from_year'] = from_year
            extra_params['to_year'] = to_year
            filters = self._build_filters(filters, extra_params)
        elif from_year:  # Legacy support
            filters.append(f'publication_year:>{from_year-1}')
        
        params = {
            'filter': ','.join(filters),
            'sort': self._get_sort_order(extra_params.get('sort_by', 'Relevance')) if extra_params else 'cited_by_count:desc'
        }
        
        return self._make_request(params, max_results)
    
    def search_by_title(self, title: str, from_year: int = None, to_year: int = None,
                       max_results: int = MAX_RESULTS, extra_params: Dict = None) -> List[Dict]:
        """Search publications by title"""
        self.seen_ids.clear()  # Clear deduplication set
        
        # Build filters
        filters = [f'title.search:{title}']
        if extra_params:
            extra_params['from_year'] = from_year
            extra_params['to_year'] = to_year
            filters = self._build_filters(filters, extra_params)
        elif from_year:  # Legacy support
            filters.append(f'publication_year:>{from_year-1}')
        
        params = {
            'filter': ','.join(filters),
            'sort': self._get_sort_order(extra_params.get('sort_by', 'Relevance')) if extra_params else 'relevance_score:desc'
        }
        
        return self._make_request(params, max_results)
    
    def search_by_keyword(self, keyword: str, from_year: int = None, to_year: int = None,
                         max_results: int = MAX_RESULTS, extra_params: Dict = None) -> List[Dict]:
        """Search publications by keyword"""
        self.seen_ids.clear()  # Clear deduplication set
        
        # Build params
        params = {
            'search': keyword,
            'sort': self._get_sort_order(extra_params.get('sort_by', 'Relevance')) if extra_params else 'relevance_score:desc'
        }
        
        # Add filters if needed
        filters = []
        if extra_params:
            extra_params['from_year'] = from_year
            extra_params['to_year'] = to_year
            filters = self._build_filters(filters, extra_params)
        elif from_year:  # Legacy support
            filters.append(f'publication_year:>{from_year-1}')
        
        if filters:
            params['filter'] = ','.join(filters)
        
        return self._make_request(params, max_results)
    
    def search_by_affiliation(self, affiliation: str, from_year: int = None, to_year: int = None,
                             max_results: int = MAX_RESULTS, extra_params: Dict = None) -> List[Dict]:
        """Search publications by affiliation/institution"""
        self.seen_ids.clear()  # Clear deduplication set
        
        # Build filters
        filters = [f'institutions.display_name.search:{affiliation}']
        if extra_params:
            extra_params['from_year'] = from_year
            extra_params['to_year'] = to_year
            filters = self._build_filters(filters, extra_params)
        elif from_year:  # Legacy support
            filters.append(f'publication_year:>{from_year-1}')
        
        params = {
            'filter': ','.join(filters),
            'sort': self._get_sort_order(extra_params.get('sort_by', 'Relevance')) if extra_params else 'cited_by_count:desc'
        }
        
        return self._make_request(params, max_results)
    
    def search_all_fields(self, query: str, from_year: int = None, to_year: int = None,
                         max_results: int = MAX_RESULTS, extra_params: Dict = None) -> List[Dict]:
        """Search across all fields using default search"""
        self.seen_ids.clear()  # Clear deduplication set
        
        # Use default search which searches across multiple fields
        params = {
            'search': query,
            'sort': self._get_sort_order(extra_params.get('sort_by', 'Relevance')) if extra_params else 'relevance_score:desc'
        }
        
        # Add filters if needed
        filters = []
        if extra_params:
            extra_params['from_year'] = from_year
            extra_params['to_year'] = to_year
            filters = self._build_filters(filters, extra_params)
        elif from_year:  # Legacy support
            filters.append(f'publication_year:>{from_year-1}')
        
        if filters:
            params['filter'] = ','.join(filters)
        
        return self._make_request(params, max_results)
    
    def search_advanced(self, query: str, from_year: int = None, to_year: int = None,
                       max_results: int = MAX_RESULTS, extra_params: Dict = None) -> List[Dict]:
        """Advanced search with complex query supporting field-specific searches"""
        self.seen_ids.clear()  # Clear deduplication set
        
        # Build complex filter from advanced query parameters
        filters = []
        
        # Handle main query
        if extra_params.get('main_query'):
            # Use search parameter for main query
            params = {
                'search': extra_params['main_query'],
                'sort': self._get_sort_order(extra_params.get('sort_by', 'Relevance'))
            }
        else:
            params = {
                'sort': self._get_sort_order(extra_params.get('sort_by', 'Relevance'))
            }
        
        # Add field-specific filters
        if extra_params.get('author_query'):
            filters.append(f'display_name.search:{extra_params["author_query"]}')
        
        if extra_params.get('title_query'):
            filters.append(f'title.search:{extra_params["title_query"]}')
        
        if extra_params.get('abstract_query'):
            # OpenAlex doesn't have abstract search in filters, use search instead
            if 'search' in params:
                params['search'] += f' {extra_params["abstract_query"]}'
            else:
                params['search'] = extra_params['abstract_query']
        
        if extra_params.get('affiliation_query'):
            filters.append(f'institutions.display_name.search:{extra_params["affiliation_query"]}')
        
        if extra_params.get('journal_query'):
            filters.append(f'host_venue.display_name.search:{extra_params["journal_query"]}')
        
        # Add other filters
        extra_params['from_year'] = from_year
        extra_params['to_year'] = to_year
        filters = self._build_filters(filters, extra_params)
        
        if filters:
            # Handle boolean operator
            if extra_params.get('boolean_operator') == 'OR':
                # OpenAlex uses | for OR operations within filters
                params['filter'] = '|'.join(filters)
            else:
                # Default to AND
                params['filter'] = ','.join(filters)
        
        return self._make_request(params, max_results)