#!/usr/bin/env python3
"""
Multi-Source Academic Paper API Integration
Integrates multiple academic databases for comprehensive paper search
"""

import requests
import json
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from urllib.parse import quote, urlencode
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PaperResult:
    """Standardized paper result format"""
    title: str
    authors: List[str]
    abstract: str
    publication_year: Optional[int]
    doi: Optional[str]
    url: str
    source: str
    pdf_url: Optional[str] = None
    citation_count: Optional[int] = None
    keywords: List[str] = None
    journal: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None

class SemanticScholarAPI:
    """Semantic Scholar API integration"""
    
    BASE_URL = "https://api.semanticscholar.org/graph/v1"
    
    def __init__(self):
        self.session = requests.Session()
        # Add retry logic for resilience
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        self.session.headers.update({
            'User-Agent': 'Sentino-AI-Research-Platform/1.0'
        })
        self.rate_limit_delay = 0.6  # 100 requests/minute
    
    def search_papers(self, query: str, max_results: int = 20, 
                     fields: str = "paperId,title,authors,abstract,year,doi,url,citationCount,venue,journal") -> List[PaperResult]:
        """Search papers using Semantic Scholar API"""
        try:
            params = {
                'query': query,
                'limit': min(max_results, 100),  # API limit
                'fields': fields,
                'sort': 'relevance'
            }
            
            response = self.session.get(f"{self.BASE_URL}/paper/search", params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                papers = []
                
                for item in data.get('data', []):
                    authors = [author.get('name', '') for author in item.get('authors', [])]
                    
                    paper = PaperResult(
                        title=item.get('title', ''),
                        authors=authors,
                        abstract=item.get('abstract', ''),
                        publication_year=item.get('year'),
                        doi=item.get('doi'),
                        url=item.get('url', ''),
                        source='Semantic Scholar',
                        citation_count=item.get('citationCount'),
                        journal=item.get('venue') or item.get('journal', {}).get('name') if item.get('journal') else None
                    )
                    papers.append(paper)
                
                time.sleep(self.rate_limit_delay)
                return papers
            
            else:
                logger.error(f"Semantic Scholar API error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error accessing Semantic Scholar API: {str(e)}")
            return []

class CoreAPI:
    """CORE API integration for open access papers"""
    
    BASE_URL = "https://core.ac.uk/api-v2"
    
    def __init__(self):
        self.session = requests.Session()
        # Add retry logic
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        self.session.headers.update({
            'User-Agent': 'Sentino-AI-Research-Platform/1.0'
        })
    
    def search_papers(self, query: str, max_results: int = 20) -> List[PaperResult]:
        """Search open access papers using CORE API"""
        try:
            params = {
                'q': query,
                'page': 1,
                'pageSize': min(max_results, 100),
                'format': 'json'
            }
            
            response = self.session.get(f"{self.BASE_URL}/search", params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                papers = []
                
                for item in data.get('data', []):
                    authors = []
                    if item.get('authors'):
                        authors = [author.get('name', '') for author in item['authors']]
                    
                    # Extract publication year
                    year = None
                    if item.get('publishedDate'):
                        try:
                            year = int(item['publishedDate'][:4])
                        except:
                            pass
                    
                    paper = PaperResult(
                        title=item.get('title', ''),
                        authors=authors,
                        abstract=item.get('abstract', ''),
                        publication_year=year,
                        doi=item.get('doi'),
                        url=item.get('downloadUrl') or item.get('links', [{}])[0].get('url', ''),
                        source='CORE',
                        pdf_url=item.get('downloadUrl'),
                        journal=item.get('publisher')
                    )
                    papers.append(paper)
                
                return papers
            
            else:
                logger.error(f"CORE API error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error accessing CORE API: {str(e)}")
            return []

class PubMedAPI:
    """PubMed API integration for biomedical papers"""
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    def __init__(self):
        self.session = requests.Session()
        # Add retry logic
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        self.session.headers.update({
            'User-Agent': 'Sentino-AI-Research-Platform/1.0'
        })
    
    def search_papers(self, query: str, max_results: int = 20) -> List[PaperResult]:
        """Search biomedical papers using PubMed API"""
        try:
            # Step 1: Search for PMIDs
            search_params = {
                'db': 'pubmed',
                'term': query,
                'retmax': min(max_results, 100),
                'retmode': 'json'
            }
            
            search_response = self.session.get(f"{self.BASE_URL}/esearch.fcgi", params=search_params, timeout=30)
            
            if search_response.status_code != 200:
                return []
            
            search_data = search_response.json()
            pmids = search_data.get('esearchresult', {}).get('idlist', [])
            
            if not pmids:
                return []
            
            # Step 2: Get detailed information
            fetch_params = {
                'db': 'pubmed',
                'id': ','.join(pmids),
                'retmode': 'xml'
            }
            
            fetch_response = self.session.get(f"{self.BASE_URL}/efetch.fcgi", params=fetch_params, timeout=30)
            
            if fetch_response.status_code != 200:
                return []
            
            # Parse XML response (simplified)
            papers = self._parse_pubmed_xml(fetch_response.text)
            return papers
            
        except Exception as e:
            logger.error(f"Error accessing PubMed API: {str(e)}")
            return []
    
    def _parse_pubmed_xml(self, xml_content: str) -> List[PaperResult]:
        """Parse PubMed XML response (simplified implementation)"""
        # This is a simplified parser - in production, use proper XML parsing
        papers = []
        # Implementation would parse XML and extract paper details
        # For now, return empty list
        return papers

class CrossrefAPI:
    """Crossref API integration for DOI metadata"""
    
    BASE_URL = "https://api.crossref.org"
    
    def __init__(self):
        self.session = requests.Session()
        # Add retry logic
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        self.session.headers.update({
            'User-Agent': 'Sentino-AI-Research-Platform/1.0 (mailto:your-email@example.com)',
            'Accept': 'application/json'
        })
    
    def search_papers(self, query: str, max_results: int = 20) -> List[PaperResult]:
        """Search papers using Crossref API"""
        try:
            params = {
                'query': query,
                'rows': min(max_results, 100),
                'sort': 'relevance'
            }
            
            response = self.session.get(f"{self.BASE_URL}/works", params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                papers = []
                
                for item in data.get('message', {}).get('items', []):
                    authors = []
                    if item.get('author'):
                        authors = [f"{author.get('given', '')} {author.get('family', '')}".strip() 
                                 for author in item['author']]
                    
                    # Extract publication year
                    year = None
                    if item.get('published-print', {}).get('date-parts'):
                        year = item['published-print']['date-parts'][0][0]
                    elif item.get('published-online', {}).get('date-parts'):
                        year = item['published-online']['date-parts'][0][0]
                    
                    paper = PaperResult(
                        title=item.get('title', [''])[0] if item.get('title') else '',
                        authors=authors,
                        abstract=item.get('abstract', ''),
                        publication_year=year,
                        doi=item.get('DOI'),
                        url=item.get('URL', ''),
                        source='Crossref',
                        journal=item.get('container-title', [''])[0] if item.get('container-title') else None
                    )
                    papers.append(paper)
                
                return papers
            
            else:
                logger.error(f"Crossref API error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error accessing Crossref API: {str(e)}")
            return []

class MultiSourceAPI:
    """Main class to coordinate multiple academic paper sources"""
    
    def __init__(self):
        self.semantic_scholar = SemanticScholarAPI()
        self.core = CoreAPI()
        self.pubmed = PubMedAPI()
        self.crossref = CrossrefAPI()
        
    def search_all_sources(self, query: str, max_results_per_source: int = 10, 
                          sources: List[str] = None) -> Dict[str, List[PaperResult]]:
        """Search across all available sources"""
        
        if sources is None:
            sources = ['semantic_scholar', 'core', 'crossref']
        
        results = {}
        
        if 'semantic_scholar' in sources:
            logger.info("Searching Semantic Scholar...")
            results['semantic_scholar'] = self.semantic_scholar.search_papers(query, max_results_per_source)
        
        if 'core' in sources:
            logger.info("Searching CORE...")
            results['core'] = self.core.search_papers(query, max_results_per_source)
        
        if 'crossref' in sources:
            logger.info("Searching Crossref...")
            results['crossref'] = self.crossref.search_papers(query, max_results_per_source)
        
        if 'pubmed' in sources:
            logger.info("Searching PubMed...")
            results['pubmed'] = self.pubmed.search_papers(query, max_results_per_source)
        
        return results
    
    def search_combined(self, query: str, max_total_results: int = 50, 
                       sources: List[str] = None) -> List[PaperResult]:
        """Search and combine results from multiple sources, removing duplicates"""
        
        # Calculate results per source
        available_sources = sources or ['semantic_scholar', 'core', 'crossref']
        max_per_source = max_total_results // len(available_sources)
        
        # Search all sources
        all_results = self.search_all_sources(query, max_per_source, available_sources)
        
        # Combine and deduplicate
        combined_papers = []
        seen_dois = set()
        seen_titles = set()
        
        for source_name, papers in all_results.items():
            for paper in papers:
                # Deduplicate by DOI first, then by title
                if paper.doi and paper.doi in seen_dois:
                    continue
                if paper.title.lower() in seen_titles:
                    continue
                
                seen_dois.add(paper.doi)
                seen_titles.add(paper.title.lower())
                combined_papers.append(paper)
        
        # Sort by relevance (citation count, year, etc.)
        combined_papers.sort(key=lambda x: (
            x.citation_count or 0,
            x.publication_year or 0
        ), reverse=True)
        
        return combined_papers[:max_total_results]
    
    def get_source_stats(self, query: str, sources: List[str] = None) -> Dict[str, int]:
        """Get statistics about available papers across sources"""
        results = self.search_all_sources(query, 5, sources)  # Small sample for stats
        return {source: len(papers) for source, papers in results.items()}

# Global instance
multi_source_api = MultiSourceAPI()


