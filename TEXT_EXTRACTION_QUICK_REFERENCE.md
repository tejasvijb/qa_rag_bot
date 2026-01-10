% # Text Extraction Module - Quick Reference

## What Was Built

A complete text extraction module that converts raw HTML into clean, readable text by:

1. **Removing Noise** - Uses CSS selectors to eliminate navbars, footers, ads, cookies, etc.
2. **Extracting Text** - Pulls visible text while preserving semantic structure
3. **Cleaning Up** - Removes extra whitespace and empty lines
4. **Preserving Structure** - Marks heading boundaries with line breaks

## File Structure

```
qa_rag_bot/
├── text_extraction/
│   ├── text_extract.py          ← Main implementation (242 lines)
│   └── README.md                ← Full documentation
├── api/
│   └── main.py                  ← Updated with /extract endpoints
├── test_extractor.py            ← Comprehensive test suite
├── example_usage.py             ← Working examples
└── IMPLEMENTATION_SUMMARY.md    ← This summary
```

## Core Classes & Models

### TextExtractor

Main class for text extraction with these methods:

| Method                   | Input                 | Output              | Purpose                        |
| ------------------------ | --------------------- | ------------------- | ------------------------------ |
| `extract()`              | HTML string           | Clean text          | Extract text from single page  |
| `process_pages()`        | List of crawler pages | List[ExtractedText] | Batch process crawler output   |
| `remove_noise()`         | BeautifulSoup object  | None                | Remove noise elements in-place |
| `extract_visible_text()` | BeautifulSoup object  | String              | Extract and flatten text       |
| `clean_text()`           | Raw text              | Clean text          | Final whitespace cleanup       |

### ExtractedText (Pydantic Model)

Output data structure:

```python
ExtractedText(
    url: str,              # Page URL
    title: Optional[str],  # Page title
    cleaned_text: str      # Clean extracted text
)
```

## Quick Start

### 1. Extract Text from HTML

```python
from text_extraction.text_extract import TextExtractor

extractor = TextExtractor()
html = "<html><body><h1>Title</h1><p>Content</p><footer>Footer</footer></body></html>"
clean_text = extractor.extract(html)
# Output: "Title\nContent"
```

### 2. Process Crawled Pages

```python
crawler = WebCrawler("https://example.com", max_pages=10)
pages = crawler.crawl()

extractor = TextExtractor()
results = extractor.process_pages(pages)
# Results: List of ExtractedText objects
```

### 3. Use the API

```bash
# Extract from a website via API
curl -X POST "http://localhost:8000/extract" \
  -H "Content-Type: application/json" \
  -d '{"base_url": "https://example.com", "max_depth": 2, "max_pages": 10}'
```

## Noise Removal Strategy

**CSS Selectors used** (20+ patterns):

-   Navigation: `nav`, `.navbar`, `[role="navigation"]`
-   Footers: `footer`, `.footer`, `[role="contentinfo"]`
-   Scripts/Styles: `script`, `style`, `noscript`
-   Cookie Banners: `[class*="cookie"]`, `[id*="cookie"]`
-   Modals/Popups: `[class*="modal"]`, `[class*="popup"]`
-   Ads: `[class*="advertisement"]`, `[class*="ad-"]`
-   Other: `sidebar`, `breadcrumb`, `pagination`, `meta`, `link`

## Text Processing Flow

```
Raw HTML
   ↓
[Parse with BeautifulSoup]
   ↓
[Remove Noise via CSS Selectors]
   ↓
[Extract Visible Text Recursively]
   ↓
[Mark Heading Boundaries]
   ↓
[Filter HTML Comments]
   ↓
[Clean Whitespace]
   ↓
Clean Text Ready for Chunking
```

## Integration with RAG Pipeline

```
┌─────────┐    ┌──────────────┐    ┌──────────┐    ┌──────────┐    ┌────────┐    ┌───────────┐
│ Crawler │───→│ Text Extract │───→│ Chunking │───→│Embeddings│───→│Storage │───→│ Retrieval │
└─────────┘    └──────────────┘    └──────────┘    └──────────┘    └────────┘    └───────────┘
```

**Stage 2 of 6** - Converts raw HTML to clean text

## API Endpoints

### POST /extract

**Request:**

```json
{
    "base_url": "https://example.com",
    "max_depth": 2,
    "max_pages": 50
}
```

**Response:**

```json
{
    "total_extracted": 8,
    "extracted_pages": [
        {
            "url": "https://example.com/page1",
            "title": "Page Title",
            "cleaned_text": "Clean extracted text..."
        }
    ]
}
```

### GET /extract

**Query Parameters:**

```
?base_url=https://example.com&max_depth=2&max_pages=50
```

## Testing

Run tests to verify everything works:

```bash
python test_extractor.py
```

**Test Results:**

-   ✅ Noise removal verified (nav, footer, scripts, cookies, ads, modals, sidebars)
-   ✅ Main content extraction verified
-   ✅ Heading boundaries preserved
-   ✅ Comment filtering works
-   ✅ Whitespace cleaned
-   ✅ Batch processing works
-   ✅ Error handling correct

## Key Features

| Feature                 | Status | Details                                  |
| ----------------------- | ------ | ---------------------------------------- |
| Remove navbars/footers  | ✅     | CSS selectors for precise targeting      |
| Remove scripts/styles   | ✅     | Eliminates `<script>` and `<style>` tags |
| Remove cookie banners   | ✅     | Matches class/id patterns with "cookie"  |
| Remove ads              | ✅     | Matches patterns: ad-, advertisement     |
| Remove modals/popups    | ✅     | Matches modal and popup classes          |
| Extract visible text    | ✅     | Recursive traversal of DOM               |
| Mark heading boundaries | ✅     | Line breaks between h1-h6 sections       |
| Remove empty lines      | ✅     | Regex cleanup of whitespace              |
| Type safety             | ✅     | Pydantic models for all data             |
| Error handling          | ✅     | Graceful degradation for failed pages    |
| Batch processing        | ✅     | Process crawler output efficiently       |
| API integration         | ✅     | POST and GET endpoints available         |

## Example Output

### Input HTML

```html
<html>
    <body>
        <nav><a href="/">Home</a></nav>
        <article>
            <h1>10 Python Tips</h1>
            <p>Python is great. Here are tips.</p>
            <h2>Tip 1: List Comprehensions</h2>
            <p>They are efficient.</p>
        </article>
        <footer><p>Copyright 2026</p></footer>
        <div id="cookie-consent">We use cookies...</div>
    </body>
</html>
```

### Output Text

```
10 Python Tips
Python is great. Here are tips.
Tip 1: List Comprehensions
They are efficient.
```

Notice:

-   ✅ Navigation removed
-   ✅ Footer removed
-   ✅ Cookie banner removed
-   ✅ Main content preserved
-   ✅ Heading boundaries marked with newlines

## Requirements

-   Python 3.8+
-   beautifulsoup4==4.14.3
-   pydantic==2.12.5
-   requests==2.32.5 (for crawler)
-   fastapi==0.124.4 (for API)

## Running Examples

```bash
# See all usage examples
python example_usage.py

# Run tests
python test_extractor.py

# Start API server
python api/main.py
```

## Next Phase: Chunking

After text extraction, the next stage is **text chunking** to prepare data for embeddings:

-   Split cleaned text into optimal-sized chunks
-   Maintain context between chunks
-   Handle overlap for semantic continuity
-   Prepare metadata for retrieval

## Support

For detailed information:

-   See [text_extraction/README.md](text_extraction/README.md) for full documentation
-   See [example_usage.py](example_usage.py) for usage patterns
-   See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for complete summary
