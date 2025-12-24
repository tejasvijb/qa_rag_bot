import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional
import time


class WebCrawler:
    """
    Web crawler that crawls internal links of the same domain.
    Stores URL, title, raw HTML, and errors for each page.
    """
    
    # Pages to skip (patterns)
    SKIP_PATTERNS = [
        '/login',
        '/signup',
        '/register',
        '/auth',
        '/cart',
        '/checkout',
        '/admin',
        '/account',
        '/profile',
        '/settings',
        '/password',
        '/logout',
        '/terms',
        '/privacy',
        '/contact',
    ]
    
    def __init__(self, base_url: str, max_depth: int = 2, max_pages: int = 50, timeout: int = 10):
        """
        Initialize the crawler.
        
        Args:
            base_url: The starting URL to crawl
            max_depth: Maximum depth of links to follow (default: 2)
            max_pages: Maximum number of pages to crawl (default: 50)
            timeout: Timeout for each request in seconds (default: 10)
        """
        self.base_url = base_url
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.timeout = timeout
        
        # Parse the base domain
        parsed = urlparse(base_url)
        self.domain = parsed.netloc
        self.scheme = parsed.scheme or 'https'
        
        # Storage for crawled pages
        self.crawled_pages: List[Dict] = []
        self.visited_urls = set()
        
        # Headers to mimic a browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def should_skip_url(self, url: str) -> bool:
        """Check if URL should be skipped based on patterns."""
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        for pattern in self.SKIP_PATTERNS:
            if pattern in path:
                return True
        
        return False
    
    def is_internal_link(self, url: str) -> bool:
        """Check if URL is from the same domain."""
        parsed = urlparse(url)
        return parsed.netloc == self.domain
    
    def extract_links(self, html: str, current_url: str) -> List[str]:
        """Extract all links from HTML content."""
        links = []
        try:
            soup = BeautifulSoup(html, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                # Convert relative URLs to absolute
                absolute_url = urljoin(current_url, href)
                # Remove fragments
                absolute_url = absolute_url.split('#')[0]
                
                if absolute_url and self.is_internal_link(absolute_url) and not self.should_skip_url(absolute_url):
                    links.append(absolute_url)
        except Exception as e:
            print(f"Error extracting links from {current_url}: {e}")
        
        return links
    
    def get_page_title(self, html: str) -> str:
        """Extract page title from HTML."""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            title_tag = soup.find('title')
            return title_tag.text.strip() if title_tag else 'No title found'
        except Exception:
            return 'Error extracting title'
    
    def fetch_page(self, url: str) -> Dict:
        """
        Fetch a single page.
        
        Returns a dictionary with:
        - url: The page URL
        - title: Page title
        - html: Raw HTML content
        - error: Error message if any (None if successful)
        """
        page_data = {
            'url': url,
            'title': None,
            'html': None,
            'error': None
        }
        
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            html = response.text
            page_data['html'] = html
            page_data['title'] = self.get_page_title(html)
            
        except requests.exceptions.Timeout:
            page_data['error'] = f'Timeout after {self.timeout}s'
        except requests.exceptions.ConnectionError:
            page_data['error'] = 'Connection error'
        except requests.exceptions.HTTPError as e:
            page_data['error'] = f'HTTP error {e.response.status_code}'
        except Exception as e:
            page_data['error'] = str(e)
        
        return page_data
    
    def crawl(self) -> List[Dict]:
        """
        Crawl the website starting from base_url.
        
        Returns a list of crawled pages with metadata and errors.
        """
        to_visit = [(self.base_url, 0)]  # (url, depth)
        
        while to_visit and len(self.crawled_pages) < self.max_pages:
            current_url, current_depth = to_visit.pop(0)
            
            # Skip if already visited
            if current_url in self.visited_urls:
                continue
            
            self.visited_urls.add(current_url)
            
            print(f"[{len(self.crawled_pages) + 1}] Crawling: {current_url} (depth: {current_depth})")
            
            # Fetch the page
            page_data = self.fetch_page(current_url)
            self.crawled_pages.append(page_data)
            
            # If page fetch was successful and we haven't reached max depth, extract links
            if page_data['error'] is None and current_depth < self.max_depth:
                links = self.extract_links(page_data['html'], current_url)
                for link in links:
                    if link not in self.visited_urls and len(self.crawled_pages) < self.max_pages:
                        to_visit.append((link, current_depth + 1))
        
        return self.crawled_pages
