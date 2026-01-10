from bs4 import BeautifulSoup, NavigableString, Comment
from typing import List, Dict, Optional
from pydantic import BaseModel
import re


class ExtractedText(BaseModel):
    """Model for cleaned text extracted from a web page."""
    url: str
    title: Optional[str]
    cleaned_text: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com/page",
                "title": "Example Page",
                "cleaned_text": "# Heading\nParagraph content..."
            }
        }


class TextExtractor:
    """
    Extracts clean, visible text from HTML content.
    
    Features:
    - Removes navbars, footers, scripts, styles, and cookie banners
    - Extracts visible text only
    - Marks heading boundaries with line breaks
    - Removes noise and empty lines
    """
    
    # CSS selectors for elements to remove
    NOISE_SELECTORS = [
        'nav',                          # Navigation elements
        'footer',                       # Footer sections
        'script',                       # JavaScript code
        'style',                        # CSS styles
        'noscript',                     # No-script fallbacks
        '[class*="cookie"]',            # Cookie banners/consent
        '[id*="cookie"]',               # Cookie related elements by ID
        '[class*="modal"]',             # Modal dialogs
        '[id*="modal"]',                # Modal IDs
        '[class*="popup"]',             # Popup elements
        '[id*="popup"]',                # Popup IDs
        '[class*="advertisement"]',     # Ads
        '[class*="ad-"]',               # Ad containers
        '[class*="banner"]',            # Banners
        '[role="navigation"]',          # Navigation role
        '[role="contentinfo"]',         # Footer role
        'navbar',                       # Navbar class
        '.footer',                      # Footer class
        '.sidebar',                     # Sidebar elements
        '.breadcrumb',                  # Breadcrumb navigation
        '.pagination',                  # Pagination elements
        'meta',                         # Meta tags
        'link',                         # Link tags
    ]
    
    # Headings that should be marked as boundaries
    HEADING_TAGS = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
    
    def __init__(self):
        """Initialize the text extractor."""
        pass
    
    def remove_noise(self, soup: BeautifulSoup) -> None:
        """
        Remove noise elements from the soup in-place using CSS selectors.
        
        Args:
            soup: BeautifulSoup object to clean
        """
        for selector in self.NOISE_SELECTORS:
            for element in soup.select(selector):
                element.decompose()
    
    def extract_visible_text(self, soup: BeautifulSoup) -> str:
        """
        Extract visible text from soup, marking heading boundaries.
        
        Args:
            soup: BeautifulSoup object to extract text from
            
        Returns:
            Cleaned text with heading boundaries marked by line breaks
        """
        # Remove body and html tags to get just the content
        body = soup.find('body')
        if not body:
            # If no body tag, use the entire soup
            body = soup
        
        text_parts = []
        
        # Recursively process all elements
        self._process_element(body, text_parts)
        
        # Join parts and clean up
        full_text = ''.join(text_parts)
        
        # Remove extra whitespace while preserving meaningful line breaks
        lines = full_text.split('\n')
        cleaned_lines = [line.strip() for line in lines if line.strip()]
        
        return '\n'.join(cleaned_lines)
    
    def _process_element(self, element, text_parts: List[str]) -> None:
        """
        Recursively process elements and extract text.
        Marks heading boundaries with line breaks.
        Skips comments.
        
        Args:
            element: BeautifulSoup element to process
            text_parts: List to accumulate text parts
        """
        # Skip HTML comments
        if isinstance(element, Comment):
            return
        
        if isinstance(element, NavigableString):
            # Add text content
            text = str(element).strip()
            if text:
                text_parts.append(text + ' ')
        else:
            # Check if it's a heading tag
            if element.name in self.HEADING_TAGS:
                text_parts.append('\n')
            
            # Process children
            for child in element.children:
                self._process_element(child, text_parts)
            
            # Add line break after heading or block-level elements
            if element.name in self.HEADING_TAGS or element.name in ['p', 'div', 'article', 'section']:
                text_parts.append('\n')
    
    def clean_text(self, text: str) -> str:
        """
        Final cleanup of extracted text.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Fully cleaned text
        """
        # Remove multiple spaces
        text = re.sub(r' +', ' ', text)
        
        # Remove multiple newlines
        text = re.sub(r'\n\n+', '\n', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def extract(self, html: str) -> str:
        """
        Main extraction method: parse HTML, remove noise, and extract clean text.
        
        Args:
            html: Raw HTML content
            
        Returns:
            Cleaned text
        """
        try:
            # Parse HTML
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove noise elements
            self.remove_noise(soup)
            
            # Extract visible text with heading boundaries
            text = self.extract_visible_text(soup)
            
            # Final cleanup
            text = self.clean_text(text)
            
            return text
        except Exception as e:
            print(f"Error extracting text: {e}")
            return ""
    
    def process_pages(self, pages: List[Dict]) -> List[ExtractedText]:
        """
        Process a list of crawled pages and extract clean text.
        
        Args:
            pages: List of page dictionaries from crawler (with url, title, html, error)
            
        Returns:
            List of ExtractedText objects with cleaned content
        """
        extracted_pages = []
        
        for page in pages:
            # Skip pages with errors (no HTML content)
            if page.get('error') is not None:
                print(f"Skipping {page['url']} - Error: {page['error']}")
                continue
            
            # Extract text if HTML is available
            if page.get('html'):
                cleaned_text = self.extract(page['html'])
                
                # Only include pages with extracted text
                if cleaned_text:
                    extracted_pages.append(
                        ExtractedText(
                            url=page['url'],
                            title=page.get('title'),
                            cleaned_text=cleaned_text
                        )
                    )
                else:
                    print(f"No text extracted from {page['url']}")
            else:
                print(f"No HTML content for {page['url']}")
        
        return extracted_pages


# Convenience function for simple usage
def extract_text_from_html(html: str) -> str:
    """
    Quick function to extract clean text from HTML.
    
    Args:
        html: Raw HTML content
        
    Returns:
        Cleaned text
    """
    extractor = TextExtractor()
    return extractor.extract(html)
