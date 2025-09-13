import requests
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
import time
import hashlib

from config import IEEE_XPLORE_API_KEY, IEEE_XPLORE_API_URL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IEEEXploreAPI:
    """Enhanced IEEE Xplore API class with caching and rate limiting"""
    
    def __init__(self):
        self.api_key = IEEE_XPLORE_API_KEY
        self.base_url = IEEE_XPLORE_API_URL
        self.cache = {}  # Simple in-memory cache
        self.cache_duration = timedelta(hours=1)  # Cache for 1 hour
        self.rate_limit_delay = 1.0  # Delay between requests
        self.last_request_time = 0
        self.logger = logging.getLogger(__name__)
        
    def _enforce_rate_limit(self):
        """Enforce rate limiting between API calls"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last_request
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _get_cache_key(self, query: str, max_results: int, filters: Dict) -> str:
        """Generate cache key for query"""
        cache_data = {
            'query': query,
            'max_results': max_results,
            'filters': filters
        }
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def _is_cache_valid(self, timestamp: datetime) -> bool:
        """Check if cached data is still valid"""
        return datetime.now() - timestamp < self.cache_duration
    
    def _make_request(self, params: Dict) -> Optional[Dict]:
        """Make API request with error handling and rate limiting"""
        if not self.api_key:
            self.logger.error("IEEE Xplore API key is not configured")
            return None
        
        self._enforce_rate_limit()
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 403:
                self.logger.error("IEEE Xplore API authentication failed. Please check your API key.")
                return None
            elif response.status_code == 429:
                self.logger.warning("IEEE Xplore API rate limit exceeded. Waiting...")
                time.sleep(5)  # Wait 5 seconds and try once more
                response = requests.get(self.base_url, params=params, timeout=30)
                if response.status_code == 200:
                    return response.json()
                else:
                    self.logger.error("IEEE Xplore API rate limit still exceeded after retry")
                    return None
            else:
                self.logger.error(f"IEEE Xplore API error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error accessing IEEE Xplore API: {str(e)}")
            return None
    
    def search_papers(self, query: str, max_results: int = 10, start_year: Optional[int] = None, 
                     end_year: Optional[int] = None, author: Optional[str] = None,
                     publication_title: Optional[str] = None) -> List[Dict]:
        """
        Enhanced search for papers on IEEE Xplore with filtering options
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return (default: 10)
            start_year: Filter by start year (optional)
            end_year: Filter by end year (optional)
            author: Filter by author name (optional)
            publication_title: Filter by publication/conference name (optional)
            
        Returns:
            List of paper dictionaries with relevant information
        """
        # Create filters dict for caching
        filters = {
            'start_year': start_year,
            'end_year': end_year,
            'author': author,
            'publication_title': publication_title
        }
        
        # Check cache first
        cache_key = self._get_cache_key(query, max_results, filters)
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if self._is_cache_valid(timestamp):
                self.logger.info(f"Returning cached results for query: {query}")
                return cached_data
        
        params = {
            "apikey": self.api_key,
            "format": "json",
            "max_records": max_results,
            "querytext": query,
            "sort_order": "desc",
            "sort_field": "article_number"
        }
        
        # Add optional filters
        if start_year:
            params["start_year"] = start_year
        if end_year:
            params["end_year"] = end_year
        if author:
            params["author"] = author
        if publication_title:
            params["publication_title"] = publication_title
        
        data = self._make_request(params)
        if not data:
            return []
        
        papers = []
        for article in data.get("articles", []):
            # Extract authors
            authors_data = article.get("authors", {})
            if isinstance(authors_data, dict) and "authors" in authors_data:
                authors = [author.get("full_name", "") for author in authors_data["authors"]]
            else:
                authors = []
            
            # Extract keywords and terms
            index_terms = article.get("index_terms", {})
            ieee_terms = []
            author_keywords = []
            
            if isinstance(index_terms, dict):
                ieee_terms_data = index_terms.get("ieee_terms", {})
                if isinstance(ieee_terms_data, dict) and "terms" in ieee_terms_data:
                    ieee_terms = ieee_terms_data["terms"]
                
                author_terms_data = index_terms.get("author_terms", {})
                if isinstance(author_terms_data, dict) and "terms" in author_terms_data:
                    author_keywords = author_terms_data["terms"]
            
            paper = {
                "title": article.get("title", "").strip(),
                "authors": authors,
                "abstract": article.get("abstract", "").strip(),
                "publication_year": article.get("publication_year"),
                "publication_date": article.get("publication_date", ""),
                "publication_title": article.get("publication_title", "").strip(),
                "volume": article.get("volume", ""),
                "issue": article.get("issue", ""),
                "start_page": article.get("start_page", ""),
                "end_page": article.get("end_page", ""),
                "doi": article.get("doi", "").strip(),
                "isbn": article.get("isbn", ""),
                "issn": article.get("issn", ""),
                "pdf_url": article.get("pdf_url", "").strip(),
                "html_url": article.get("html_url", "").strip(),
                "ieee_terms": ieee_terms,
                "author_keywords": author_keywords,
                "document_type": article.get("content_type", ""),
                "citation_count": article.get("citing_paper_count", 0),
                "source": "IEEE Xplore",
                "url": f"https://ieeexplore.ieee.org/document/{article.get('article_number', '')}",
                "retrieved_at": datetime.now().isoformat()
            }
            
            # Only add papers with meaningful content
            if paper["title"] and (paper["abstract"] or paper["authors"]):
                papers.append(paper)
        
        # Cache the results
        self.cache[cache_key] = (papers, datetime.now())
        
        self.logger.info(f"Retrieved {len(papers)} papers from IEEE Xplore for query: {query}")
        return papers
    
    def get_paper_by_doi(self, doi: str) -> Optional[Dict]:
        """
        Get a specific paper by its DOI with enhanced metadata
        
        Args:
            doi: Digital Object Identifier of the paper
            
        Returns:
            Paper dictionary if found, None otherwise
        """
        cache_key = f"doi_{doi}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if self._is_cache_valid(timestamp):
                return cached_data
        
        params = {
            "apikey": self.api_key,
            "format": "json",
            "doi": doi
        }
        
        data = self._make_request(params)
        if not data or not data.get("articles"):
            return None
        
        article = data["articles"][0]
        
        # Extract detailed information
        authors_data = article.get("authors", {})
        if isinstance(authors_data, dict) and "authors" in authors_data:
            authors = [
                {
                    "name": author.get("full_name", ""),
                    "affiliation": author.get("affiliation", ""),
                    "author_id": author.get("author_id", "")
                }
                for author in authors_data["authors"]
            ]
        else:
            authors = []
        
        paper = {
            "title": article.get("title", "").strip(),
            "authors": authors,
            "abstract": article.get("abstract", "").strip(),
            "publication_year": article.get("publication_year"),
            "publication_date": article.get("publication_date", ""),
            "publication_title": article.get("publication_title", "").strip(),
            "volume": article.get("volume", ""),
            "issue": article.get("issue", ""),
            "start_page": article.get("start_page", ""),
            "end_page": article.get("end_page", ""),
            "doi": article.get("doi", "").strip(),
            "pdf_url": article.get("pdf_url", "").strip(),
            "html_url": article.get("html_url", "").strip(),
            "source": "IEEE Xplore",
            "url": f"https://ieeexplore.ieee.org/document/{article.get('article_number', '')}",
            "retrieved_at": datetime.now().isoformat()
        }
        
        # Cache the result
        self.cache[cache_key] = (paper, datetime.now())
        
        return paper
    
    def search_by_author(self, author_name: str, max_results: int = 20) -> List[Dict]:
        """Search papers by author name"""
        return self.search_papers(
            query="",  # Empty query to search all
            max_results=max_results,
            author=author_name
        )
    
    def search_by_conference(self, conference_name: str, year: Optional[int] = None, 
                           max_results: int = 50) -> List[Dict]:
        """Search papers from a specific conference"""
        return self.search_papers(
            query="",
            max_results=max_results,
            publication_title=conference_name,
            start_year=year,
            end_year=year
        )
    
    def get_trending_papers(self, days: int = 30, max_results: int = 20) -> List[Dict]:
        """Get trending papers from the last N days"""
        end_year = datetime.now().year
        
        # Search for recent papers
        papers = self.search_papers(
            query="",
            max_results=max_results,
            start_year=end_year,
            end_year=end_year
        )
        
        # Sort by citation count if available
        papers.sort(key=lambda x: x.get("citation_count", 0), reverse=True)
        
        return papers
    
    def clear_cache(self):
        """Clear the API cache"""
        self.cache.clear()
        self.logger.info("IEEE Xplore API cache cleared")

# Create global instance
ieee_xplore_api = IEEEXploreAPI() 