import requests
import json
import time
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from urllib.parse import urlparse, urljoin
import hashlib
import re
from bs4 import BeautifulSoup
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SciHubAPI:
    """
    Sci-Hub API integration for academic paper access
    
    This class provides methods to:
    - Search for papers on Sci-Hub
    - Download papers by DOI, URL, or title
    - Handle multiple Sci-Hub mirrors
    - Cache results for performance
    """
    
    def __init__(self):
        # List of known Sci-Hub mirrors (updated as of 2024)
        self.mirrors = [
            "https://sci-hub.se/",
            "https://sci-hub.st/",
            "https://sci-hub.ru/",
            "https://sci-hub.ren/",
            "https://sci-hub.wf/",
        ]
        
        self.active_mirror = None
        self.cache = {}  # Simple in-memory cache
        self.cache_duration = timedelta(hours=6)  # Cache for 6 hours
        self.rate_limit_delay = 2.0  # Delay between requests (be respectful)
        self.last_request_time = 0
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        
        # Set up session headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Initialize active mirror
        self._find_active_mirror()
    
    def _enforce_rate_limit(self):
        """Enforce rate limiting between API calls to be respectful"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last_request
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _get_cache_key(self, identifier: str, search_type: str) -> str:
        """Generate cache key for requests"""
        cache_data = f"{search_type}_{identifier}"
        return hashlib.md5(cache_data.encode()).hexdigest()
    
    def _is_cache_valid(self, timestamp: datetime) -> bool:
        """Check if cached data is still valid"""
        return datetime.now() - timestamp < self.cache_duration
    
    def _find_active_mirror(self):
        """Find an active Sci-Hub mirror"""
        for mirror in self.mirrors:
            try:
                response = requests.get(mirror, timeout=10, headers=self.session.headers)
                if response.status_code == 200:
                    self.active_mirror = mirror
                    self.logger.info(f"Active Sci-Hub mirror found: {mirror}")
                    return
            except Exception as e:
                self.logger.debug(f"Mirror {mirror} not accessible: {str(e)}")
                continue
        
        self.logger.warning("No active Sci-Hub mirror found")
        self.active_mirror = self.mirrors[0]  # Fallback to first mirror
    
    def _make_request(self, url: str, params: Dict = None) -> Optional[requests.Response]:
        """Make HTTP request with error handling and rate limiting"""
        if not self.active_mirror:
            self._find_active_mirror()
        
        if not self.active_mirror:
            self.logger.error("No active Sci-Hub mirror available")
            return None
        
        self._enforce_rate_limit()
        
        try:
            full_url = urljoin(self.active_mirror, url) if not url.startswith('http') else url
            response = self.session.get(full_url, params=params, timeout=30)
            
            if response.status_code == 200:
                return response
            elif response.status_code in [403, 404, 503]:
                self.logger.warning(f"Sci-Hub returned {response.status_code}, trying next mirror")
                # Try next mirror
                current_index = self.mirrors.index(self.active_mirror)
                next_index = (current_index + 1) % len(self.mirrors)
                self.active_mirror = self.mirrors[next_index]
                return self._make_request(url, params)
            else:
                self.logger.error(f"Sci-Hub request failed: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error accessing Sci-Hub: {str(e)}")
            return None
    
    def _extract_pdf_url(self, html_content: str) -> Optional[str]:
        """Extract PDF download URL from Sci-Hub page"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for PDF embed or iframe
            pdf_embed = soup.find('embed', {'type': 'application/pdf'})
            if pdf_embed and pdf_embed.get('src'):
                return urljoin(self.active_mirror, pdf_embed['src'])
            
            # Look for PDF iframe
            pdf_iframe = soup.find('iframe', {'src': True})
            if pdf_iframe:
                src = pdf_iframe['src']
                if 'pdf' in src.lower() or src.endswith('.pdf'):
                    return urljoin(self.active_mirror, src)
            
            # Look for direct PDF links
            pdf_links = soup.find_all('a', href=True)
            for link in pdf_links:
                href = link['href']
                if href.endswith('.pdf') or 'pdf' in href.lower():
                    return urljoin(self.active_mirror, href)
            
            # Look for button or link with PDF download
            download_buttons = soup.find_all(['button', 'a'], text=re.compile(r'download|pdf', re.I))
            for button in download_buttons:
                if button.get('href'):
                    return urljoin(self.active_mirror, button['href'])
                elif button.get('onclick'):
                    # Extract URL from onclick if present
                    onclick = button['onclick']
                    url_match = re.search(r'["\']([^"\']*\.pdf[^"\']*)["\']', onclick)
                    if url_match:
                        return urljoin(self.active_mirror, url_match.group(1))
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting PDF URL: {str(e)}")
            return None
    
    def get_paper_by_doi(self, doi: str) -> Optional[Dict]:
        """
        Get paper from Sci-Hub using DOI
        
        Args:
            doi: Digital Object Identifier of the paper
            
        Returns:
            Dictionary with paper information and download URL if found
        """
        cache_key = self._get_cache_key(doi, "doi")
        
        # Check cache first
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if self._is_cache_valid(timestamp):
                self.logger.info(f"Returning cached result for DOI: {doi}")
                return cached_data
        
        try:
            # Clean DOI
            clean_doi = doi.strip()
            if clean_doi.startswith('http'):
                # Extract DOI from URL
                doi_match = re.search(r'10\.\d+/[^\s]+', clean_doi)
                if doi_match:
                    clean_doi = doi_match.group(0)
            
            self.logger.info(f"Searching Sci-Hub for DOI: {clean_doi}")
            
            # Make request to Sci-Hub
            response = self._make_request(clean_doi)
            if not response:
                return None
            
            # Extract PDF URL
            pdf_url = self._extract_pdf_url(response.text)
            if not pdf_url:
                self.logger.warning(f"No PDF found for DOI: {clean_doi}")
                return None
            
            # Extract paper metadata from the page
            soup = BeautifulSoup(response.text, 'html.parser')
            title = ""
            authors = ""
            
            # Try to extract title
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text().strip()
            
            # Try to extract more metadata if available
            meta_tags = soup.find_all('meta')
            for meta in meta_tags:
                if meta.get('name') == 'citation_title':
                    title = meta.get('content', title)
                elif meta.get('name') == 'citation_author':
                    authors = meta.get('content', authors)
            
            paper_data = {
                'doi': clean_doi,
                'title': title,
                'authors': authors,
                'pdf_url': pdf_url,
                'scihub_url': response.url,
                'source': 'Sci-Hub',
                'retrieved_at': datetime.now().isoformat(),
                'available': True
            }
            
            # Cache the result
            self.cache[cache_key] = (paper_data, datetime.now())
            
            self.logger.info(f"Successfully found paper on Sci-Hub: {clean_doi}")
            return paper_data
            
        except Exception as e:
            self.logger.error(f"Error getting paper by DOI: {str(e)}")
            return None
    
    def get_paper_by_url(self, paper_url: str) -> Optional[Dict]:
        """
        Get paper from Sci-Hub using paper URL
        
        Args:
            paper_url: URL of the paper (from publisher, arXiv, etc.)
            
        Returns:
            Dictionary with paper information and download URL if found
        """
        cache_key = self._get_cache_key(paper_url, "url")
        
        # Check cache first
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if self._is_cache_valid(timestamp):
                self.logger.info(f"Returning cached result for URL: {paper_url}")
                return cached_data
        
        try:
            self.logger.info(f"Searching Sci-Hub for URL: {paper_url}")
            
            # Make request to Sci-Hub with the URL
            response = self._make_request(paper_url)
            if not response:
                return None
            
            # Extract PDF URL
            pdf_url = self._extract_pdf_url(response.text)
            if not pdf_url:
                self.logger.warning(f"No PDF found for URL: {paper_url}")
                return None
            
            # Extract metadata
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.find('title').get_text().strip() if soup.find('title') else ""
            
            paper_data = {
                'original_url': paper_url,
                'title': title,
                'pdf_url': pdf_url,
                'scihub_url': response.url,
                'source': 'Sci-Hub',
                'retrieved_at': datetime.now().isoformat(),
                'available': True
            }
            
            # Cache the result
            self.cache[cache_key] = (paper_data, datetime.now())
            
            self.logger.info(f"Successfully found paper on Sci-Hub for URL: {paper_url}")
            return paper_data
            
        except Exception as e:
            self.logger.error(f"Error getting paper by URL: {str(e)}")
            return None
    
    def search_paper_by_title(self, title: str) -> Optional[Dict]:
        """
        Search for paper on Sci-Hub by title
        
        Args:
            title: Title of the paper
            
        Returns:
            Dictionary with paper information and download URL if found
        """
        cache_key = self._get_cache_key(title, "title")
        
        # Check cache first
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if self._is_cache_valid(timestamp):
                self.logger.info(f"Returning cached result for title: {title[:50]}...")
                return cached_data
        
        try:
            self.logger.info(f"Searching Sci-Hub for title: {title[:50]}...")
            
            # Make request to Sci-Hub with the title
            response = self._make_request("", params={'q': title})
            if not response:
                return None
            
            # Extract PDF URL
            pdf_url = self._extract_pdf_url(response.text)
            if not pdf_url:
                self.logger.warning(f"No PDF found for title: {title[:50]}...")
                return None
            
            paper_data = {
                'title': title,
                'pdf_url': pdf_url,
                'scihub_url': response.url,
                'source': 'Sci-Hub',
                'retrieved_at': datetime.now().isoformat(),
                'available': True
            }
            
            # Cache the result
            self.cache[cache_key] = (paper_data, datetime.now())
            
            self.logger.info(f"Successfully found paper on Sci-Hub for title: {title[:50]}...")
            return paper_data
            
        except Exception as e:
            self.logger.error(f"Error searching paper by title: {str(e)}")
            return None
    
    def download_paper(self, pdf_url: str) -> Optional[bytes]:
        """
        Download paper PDF from Sci-Hub
        
        Args:
            pdf_url: Direct PDF URL from Sci-Hub
            
        Returns:
            PDF content as bytes if successful
        """
        try:
            self._enforce_rate_limit()
            
            response = self.session.get(pdf_url, timeout=60)
            if response.status_code == 200 and response.headers.get('content-type', '').startswith('application/pdf'):
                self.logger.info(f"Successfully downloaded PDF from: {pdf_url}")
                return response.content
            else:
                self.logger.error(f"Failed to download PDF: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error downloading PDF: {str(e)}")
            return None
    
    def enhance_paper_with_scihub(self, paper: Dict) -> Dict:
        """
        Enhance existing paper data with Sci-Hub access information
        
        Args:
            paper: Paper dictionary (from arXiv, IEEE, etc.)
            
        Returns:
            Enhanced paper dictionary with Sci-Hub information
        """
        enhanced_paper = paper.copy()
        scihub_data = None
        
        # Try DOI first if available
        if paper.get('doi'):
            scihub_data = self.get_paper_by_doi(paper['doi'])
        
        # Try URL if DOI didn't work
        if not scihub_data and paper.get('url'):
            scihub_data = self.get_paper_by_url(paper['url'])
        
        # Try PDF URL if available
        if not scihub_data and paper.get('pdf_url'):
            scihub_data = self.get_paper_by_url(paper['pdf_url'])
        
        # Try title as last resort
        if not scihub_data and paper.get('title'):
            scihub_data = self.search_paper_by_title(paper['title'])
        
        # Add Sci-Hub information to paper
        if scihub_data:
            enhanced_paper['scihub_available'] = True
            enhanced_paper['scihub_pdf_url'] = scihub_data.get('pdf_url')
            enhanced_paper['scihub_url'] = scihub_data.get('scihub_url')
            self.logger.info(f"Enhanced paper with Sci-Hub access: {paper.get('title', 'Unknown')[:50]}...")
        else:
            enhanced_paper['scihub_available'] = False
            self.logger.info(f"No Sci-Hub access found for: {paper.get('title', 'Unknown')[:50]}...")
        
        return enhanced_paper
    
    def batch_enhance_papers(self, papers: List[Dict]) -> List[Dict]:
        """
        Enhance multiple papers with Sci-Hub access information
        
        Args:
            papers: List of paper dictionaries
            
        Returns:
            List of enhanced paper dictionaries
        """
        enhanced_papers = []
        
        for i, paper in enumerate(papers):
            self.logger.info(f"Enhancing paper {i+1}/{len(papers)} with Sci-Hub data")
            enhanced_paper = self.enhance_paper_with_scihub(paper)
            enhanced_papers.append(enhanced_paper)
            
            # Add small delay between requests to be respectful
            if i < len(papers) - 1:
                time.sleep(1)
        
        return enhanced_papers
    
    def get_availability_stats(self, papers: List[Dict]) -> Dict:
        """
        Get statistics on Sci-Hub availability for a list of papers
        
        Args:
            papers: List of paper dictionaries
            
        Returns:
            Dictionary with availability statistics
        """
        total_papers = len(papers)
        available_papers = sum(1 for paper in papers if paper.get('scihub_available', False))
        
        return {
            'total_papers': total_papers,
            'available_on_scihub': available_papers,
            'availability_rate': (available_papers / total_papers * 100) if total_papers > 0 else 0,
            'unavailable_papers': total_papers - available_papers
        }
    
    def clear_cache(self):
        """Clear the API cache"""
        self.cache.clear()
        self.logger.info("Sci-Hub API cache cleared")
    
    def get_mirror_status(self) -> Dict:
        """Get status of all Sci-Hub mirrors"""
        mirror_status = {}
        
        for mirror in self.mirrors:
            try:
                response = requests.get(mirror, timeout=10, headers=self.session.headers)
                mirror_status[mirror] = {
                    'status': 'active' if response.status_code == 200 else 'inactive',
                    'response_time': response.elapsed.total_seconds(),
                    'status_code': response.status_code
                }
            except Exception as e:
                mirror_status[mirror] = {
                    'status': 'error',
                    'error': str(e),
                    'response_time': None,
                    'status_code': None
                }
        
        return mirror_status

# Create global instance
scihub_api = SciHubAPI()

