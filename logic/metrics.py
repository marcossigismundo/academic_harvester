"""
Citation Metrics Calculator
Computes h-index, g-index, and other bibliometric indicators
"""

from typing import List, Dict

def calculate_metrics(citations: List[int]) -> Dict[str, float]:
    """
    Calculate various citation metrics from a list of citation counts
    
    Args:
        citations: List of citation counts for each publication
        
    Returns:
        Dictionary containing calculated metrics
    """
    # Remove None values and ensure all are integers
    citations = [int(c) for c in citations if c is not None]
    
    # Basic metrics
    total_publications = len(citations)
    total_citations = sum(citations)
    avg_citations = total_citations / total_publications if total_publications > 0 else 0
    
    # Sort citations in descending order for h-index and g-index
    sorted_citations = sorted(citations, reverse=True)
    
    # Calculate h-index
    h_index = calculate_h_index(sorted_citations)
    
    # Calculate g-index
    g_index = calculate_g_index(sorted_citations)
    
    return {
        'total_publications': total_publications,
        'total_citations': total_citations,
        'avg_citations': round(avg_citations, 2),
        'h_index': h_index,
        'g_index': g_index
    }

def calculate_h_index(sorted_citations: List[int]) -> int:
    """
    Calculate h-index: A scientist has index h if h of their papers have 
    at least h citations each, and the other papers have no more than h citations each.
    
    Args:
        sorted_citations: List of citations sorted in descending order
        
    Returns:
        h-index value
    """
    h_index = 0
    
    for i, citations in enumerate(sorted_citations):
        # The paper number (1-indexed)
        paper_number = i + 1
        
        # h-index is the largest number h such that h papers have at least h citations
        if citations >= paper_number:
            h_index = paper_number
        else:
            break
    
    return h_index

def calculate_g_index(sorted_citations: List[int]) -> int:
    """
    Calculate g-index: The largest number g such that the top g articles 
    received (together) at least g² citations.
    
    Args:
        sorted_citations: List of citations sorted in descending order
        
    Returns:
        g-index value
    """
    g_index = 0
    cumulative_citations = 0
    
    for i, citations in enumerate(sorted_citations):
        # Add current paper's citations to cumulative sum
        cumulative_citations += citations
        
        # The paper number (1-indexed)
        paper_number = i + 1
        
        # Check if cumulative citations >= g²
        if cumulative_citations >= paper_number ** 2:
            g_index = paper_number
        else:
            break
    
    return g_index