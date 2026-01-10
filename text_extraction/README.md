# Text Extraction Module

This module extracts clean, visible text from HTML content for the QA RAG Bot pipeline. It removes noise (navbars, footers, scripts, ads, cookie banners) and preserves semantic structure with heading boundaries.

## Features

✨ **Comprehensive Noise Removal**

-   Navigation bars and menus
-   Footers and copyright sections
-   JavaScript and CSS code
-   Cookie consent banners
-   Modal dialogs and popups
-   Advertisement containers
-   Breadcrumb navigation
-   Pagination elements

✨ **Smart Text Extraction**

-   Extracts only visible text content
-   Preserves heading hierarchy with line breaks
-   Removes HTML comments
-   Cleans up extra whitespace and empty lines
-   Maintains text flow and readability

✨ **Type-Safe**

-   Pydantic models for all data structures
-   Full type hints throughout the codebase
-   Validation of input and output data

## Components

### `TextExtractor` Class

The main class for extracting clean text from HTML.

#### Methods

**`extract(html: str) -> str`**

-   Extracts clean text from raw HTML
-   Returns cleaned text with heading boundaries marked

**`process_pages(pages: List[Dict]) -> List[ExtractedText]`**

-   Processes a list of crawled pages (from WebCrawler)
-   Skips pages with errors
-   Returns list of `ExtractedText` objects

### `ExtractedText` Model

Pydantic model representing extracted text from a page:

```python
class ExtractedText(BaseModel):
    url: str                    # Page URL
    title: Optional[str]        # Page title
    cleaned_text: str           # Cleaned text content
```

### Convenience Functions

**`extract_text_from_html(html: str) -> str`**

-   Quick function for extracting text from HTML
-   Creates a TextExtractor instance internally

## Usage

### Basic Usage

```python
from text_extraction.text_extract import TextExtractor

extractor = TextExtractor()

html = """
<html>
<body>
    <nav>...</nav>
    <article>
        <h1>Title</h1>
        <p>Content here</p>
    </article>
    <footer>...</footer>
</body>
</html>
"""

cleaned_text = extractor.extract(html)
print(cleaned_text)
# Output:
# Title
# Content here
```

### Processing Crawler Output

```python
from crawling.crawler import WebCrawler
from text_extraction.text_extract import TextExtractor

# Crawl a website
crawler = WebCrawler(base_url="https://example.com", max_pages=10)
pages = crawler.crawl()

# Extract text from all pages
extractor = TextExtractor()
extracted = extractor.process_pages(pages)

# Use the results
for page in extracted:
    print(f"{page.title}: {len(page.cleaned_text)} chars")
```

### Using the API

**POST Request:**

```bash
curl -X POST "http://localhost:8000/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "base_url": "https://example.com",
    "max_depth": 2,
    "max_pages": 50
  }'
```

**GET Request:**

```bash
curl "http://localhost:8000/extract?base_url=https://example.com&max_depth=2&max_pages=50"
```

**Response:**

```json
{
    "total_extracted": 8,
    "extracted_pages": [
        {
            "url": "https://example.com/page1",
            "title": "Page Title",
            "cleaned_text": "Extracted clean text here..."
        }
    ]
}
```

## Noise Removal Strategy

The module uses CSS selectors for precise element targeting:

```python
NOISE_SELECTORS = [
    'nav',                      # Navigation elements
    'footer',                   # Footer sections
    'script',                   # JavaScript code
    'style',                    # CSS styles
    '[class*="cookie"]',        # Cookie banners
    '[class*="modal"]',         # Modal dialogs
    '[class*="popup"]',         # Popups
    '[class*="advertisement"]', # Ads
    # ... and many more
]
```

## Text Extraction Strategy

1. **Parse HTML** using BeautifulSoup
2. **Remove noise elements** using CSS selectors
3. **Extract text** recursively from remaining elements
4. **Mark heading boundaries** with line breaks (h1-h6 tags)
5. **Filter comments** to exclude HTML comments
6. **Clean up** whitespace and empty lines

## Examples

See `example_usage.py` for complete working examples:

```bash
python example_usage.py
```

## Integration with RAG Pipeline

The text extraction module is the **second stage** of the pipeline:

```
Crawler → Text Extraction → Chunking → Embeddings → Storage → Retrieval
```

-   **Input**: Raw HTML from crawled pages
-   **Output**: Clean text ready for chunking and embedding
-   **Next Stage**: Text chunking for optimal embedding size

## Testing

Run the test suite:

```bash
python test_extractor.py
```

Tests verify:

-   ✓ Noise removal (navbars, footers, scripts, etc.)
-   ✓ Main content extraction
-   ✓ Heading boundary preservation
-   ✓ Comment filtering
-   ✓ Whitespace cleanup
-   ✓ Batch page processing

## Error Handling

The module gracefully handles:

-   Pages with errors from crawler (skipped with logging)
-   Invalid HTML (BeautifulSoup handles gracefully)
-   Pages with no extractable text (skipped)
-   Missing title or URL fields (marked as Optional)

## Performance

-   Fast CSS selector-based filtering
-   Efficient recursive traversal
-   Minimal memory overhead
-   Can process thousands of pages

## Future Enhancements

Potential improvements for future versions:

-   [ ] Support for different languages
-   [ ] Semantic structure preservation (list items, tables)
-   [ ] Customizable noise patterns
-   [ ] Language detection and encoding handling
-   [ ] Metadata extraction (author, date, etc.)
-   [ ] Performance optimization for large documents
