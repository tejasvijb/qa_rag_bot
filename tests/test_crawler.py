import pytest
from unittest.mock import patch, MagicMock
from crawling.crawler import WebCrawler


class TestWebCrawlerInit:
    """Test WebCrawler initialization."""
    
    def test_init_with_https_url(self):
        crawler = WebCrawler("https://example.com/page")
        assert crawler.base_url == "https://example.com/page"
        assert crawler.domain == "example.com"
        assert crawler.scheme == "https"
        assert crawler.max_depth == 2
        assert crawler.max_pages == 50
    
    def test_init_with_http_url(self):
        crawler = WebCrawler("http://test.org")
        assert crawler.domain == "test.org"
        assert crawler.scheme == "http"
    
    def test_init_with_custom_params(self):
        crawler = WebCrawler("https://example.com", max_depth=5, max_pages=100, timeout=20)
        assert crawler.max_depth == 5
        assert crawler.max_pages == 100
        assert crawler.timeout == 20


class TestShouldSkipUrl:
    """Test URL skipping logic."""
    
    def test_skip_login_pattern(self):
        crawler = WebCrawler("https://example.com")
        assert crawler.should_skip_url("https://example.com/login") == True
    
    def test_skip_admin_pattern(self):
        crawler = WebCrawler("https://example.com")
        assert crawler.should_skip_url("https://example.com/admin/panel") == True
    
    def test_skip_case_insensitive(self):
        crawler = WebCrawler("https://example.com")
        assert crawler.should_skip_url("https://example.com/LOGIN") == True
    
    def test_dont_skip_valid_url(self):
        crawler = WebCrawler("https://example.com")
        assert crawler.should_skip_url("https://example.com/about") == False
    
    def test_dont_skip_url_with_pattern_in_domain(self):
        crawler = WebCrawler("https://login-portal.com")
        # Pattern is in path, not domain
        assert crawler.should_skip_url("https://login-portal.com/page") == False
    
    def test_skip_all_patterns(self):
        crawler = WebCrawler("https://example.com")
        patterns = ['/login', '/signup', '/admin', '/terms', '/privacy', '/contact']
        for pattern in patterns:
            assert crawler.should_skip_url(f"https://example.com{pattern}") == True


class TestIsInternalLink:
    """Test internal link detection."""
    
    def test_same_domain_internal(self):
        crawler = WebCrawler("https://example.com")
        assert crawler.is_internal_link("https://example.com/page") == True
    
    def test_subdomain_internal(self):
        crawler = WebCrawler("https://example.com")
        assert crawler.is_internal_link("https://api.example.com/page") == False
    
    def test_different_domain_external(self):
        crawler = WebCrawler("https://example.com")
        assert crawler.is_internal_link("https://other.com/page") == False
    
    def test_internal_different_scheme(self):
        crawler = WebCrawler("https://example.com")
        # Same domain is internal even with different scheme
        assert crawler.is_internal_link("http://example.com/page") == True


class TestExtractLinks:
    """Test link extraction from HTML."""
    
    def test_extract_absolute_links(self):
        crawler = WebCrawler("https://example.com")
        html = '<a href="https://example.com/page1">Link</a><a href="https://example.com/page2">Link</a>'
        links = crawler.extract_links(html, "https://example.com")
        assert len(links) == 2
        assert "https://example.com/page1" in links
    
    def test_extract_relative_links(self):
        crawler = WebCrawler("https://example.com")
        html = '<a href="/about">About</a><a href="contact">Contact</a>'
        links = crawler.extract_links(html, "https://example.com/")
        assert "https://example.com/about" in links
    
    def test_remove_fragments(self):
        crawler = WebCrawler("https://example.com")
        html = '<a href="/page#section">Link</a>'
        links = crawler.extract_links(html, "https://example.com/")
        assert links[0] == "https://example.com/page"
    
    def test_skip_external_links(self):
        crawler = WebCrawler("https://example.com")
        html = '<a href="https://other.com">External</a>'
        links = crawler.extract_links(html, "https://example.com")
        assert len(links) == 0
    
    def test_skip_pattern_links(self):
        crawler = WebCrawler("https://example.com")
        html = '<a href="/login">Login</a><a href="/about">About</a>'
        links = crawler.extract_links(html, "https://example.com/")
        assert "/login" not in [l for l in links]
        assert "https://example.com/about" in links
    
    def test_extract_from_malformed_html(self):
        crawler = WebCrawler("https://example.com")
        html = '<a href="/page">Link</a><invalid>broken'
        links = crawler.extract_links(html, "https://example.com/")
        assert len(links) == 1
    
    def test_extract_from_empty_html(self):
        crawler = WebCrawler("https://example.com")
        html = ""
        links = crawler.extract_links(html, "https://example.com/")
        assert len(links) == 0
    
    def test_skip_links_without_href(self):
        crawler = WebCrawler("https://example.com")
        html = '<a>No href</a><a href="/page">Valid</a>'
        links = crawler.extract_links(html, "https://example.com/")
        assert len(links) == 1


class TestGetPageTitle:
    """Test page title extraction."""
    
    def test_extract_valid_title(self):
        crawler = WebCrawler("https://example.com")
        html = '<html><head><title>My Page</title></head></html>'
        title = crawler.get_page_title(html)
        assert title == "My Page"
    
    def test_extract_title_with_whitespace(self):
        crawler = WebCrawler("https://example.com")
        html = '<title>  Padded Title  </title>'
        title = crawler.get_page_title(html)
        assert title == "Padded Title"
    
    def test_missing_title_tag(self):
        crawler = WebCrawler("https://example.com")
        html = '<html><body>Content</body></html>'
        title = crawler.get_page_title(html)
        assert title == "No title found"
    
    def test_extract_from_malformed_html(self):
        crawler = WebCrawler("https://example.com")
        html = '<title>Title</title><invalid unclosed tag'
        title = crawler.get_page_title(html)
        assert title == "Title"
    
    def test_extract_from_empty_html(self):
        crawler = WebCrawler("https://example.com")
        html = ""
        title = crawler.get_page_title(html)
        assert title == "No title found"


class TestFetchPage:
    """Test page fetching."""
    
    @patch('crawling.crawler.requests.get')
    def test_fetch_successful_page(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = '<html><title>Test Page</title></html>'
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        crawler = WebCrawler("https://example.com")
        result = crawler.fetch_page("https://example.com/page")
        
        assert result['url'] == "https://example.com/page"
        assert result['title'] == "Test Page"
        assert result['error'] is None
        assert result['html'] is not None
    
    @patch('crawling.crawler.requests.get')
    def test_fetch_timeout(self, mock_get):
        import requests
        mock_get.side_effect = requests.exceptions.Timeout()
        
        crawler = WebCrawler("https://example.com", timeout=5)
        result = crawler.fetch_page("https://example.com/page")
        
        assert result['error'] is not None
        assert "Timeout" in result['error']
    
    @patch('crawling.crawler.requests.get')
    def test_fetch_connection_error(self, mock_get):
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        crawler = WebCrawler("https://example.com")
        result = crawler.fetch_page("https://example.com/page")
        
        assert result['error'] == "Connection error"
    
    @patch('crawling.crawler.requests.get')
    def test_fetch_http_error_404(self, mock_get):
        import requests
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        
        crawler = WebCrawler("https://example.com")
        result = crawler.fetch_page("https://example.com/missing")
        
        assert result['error'] is not None
        assert "404" in result['error']
    
    @patch('crawling.crawler.requests.get')
    def test_fetch_generic_exception(self, mock_get):
        mock_get.side_effect = Exception("Unknown error")
        
        crawler = WebCrawler("https://example.com")
        result = crawler.fetch_page("https://example.com/page")
        
        assert result['error'] == "Unknown error"


class TestCrawl:
    """Test crawling functionality."""
    
    @patch('crawling.crawler.requests.get')
    def test_crawl_single_page(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = '<html><title>Home</title><body><a href="/about">About</a></body></html>'
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        crawler = WebCrawler("https://example.com", max_depth=0)
        results = crawler.crawl()
        
        assert len(results) == 1
        assert results[0]['url'] == "https://example.com"
        assert results[0]['error'] is None
    
    @patch('crawling.crawler.requests.get')
    def test_crawl_respects_max_pages(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = '<html><title>Page</title><body><a href="/page1">1</a><a href="/page2">2</a></body></html>'
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        crawler = WebCrawler("https://example.com", max_depth=5, max_pages=2)
        results = crawler.crawl()
        
        assert len(results) <= 2
    
    @patch('crawling.crawler.requests.get')
    def test_crawl_respects_max_depth(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = '<html><title>Page</title><body><a href="/page">Link</a></body></html>'
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        crawler = WebCrawler("https://example.com", max_depth=0, max_pages=100)
        results = crawler.crawl()
        
        assert len(results) == 1
    
    @patch('crawling.crawler.requests.get')
    def test_crawl_no_duplicate_visits(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = '<html><title>Page</title><body><a href="/">Home</a></body></html>'
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        crawler = WebCrawler("https://example.com", max_depth=5)
        results = crawler.crawl()
        
        urls = [r['url'] for r in results]
        assert len(urls) == len(set(urls))
    
    @patch('crawling.crawler.requests.get')
    def test_crawl_with_errors(self, mock_get):
        mock_get.side_effect = Exception("Network error")
        
        crawler = WebCrawler("https://example.com", max_pages=1)
        results = crawler.crawl()
        
        assert len(results) == 1
        assert results[0]['error'] is not None
