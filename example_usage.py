"""
Example usage of the text extraction module

This demonstrates how to:
1. Extract text from raw HTML
2. Process crawled pages and clean the text
3. Use the API endpoints for end-to-end crawling + extraction
"""

from text_extraction.text_extract import TextExtractor, extract_text_from_html

# Example 1: Extract text from a single HTML string
print("=" * 70)
print("EXAMPLE 1: Extract text from raw HTML")
print("=" * 70)

sample_html = """
<html>
<head>
    <title>Blog Post: Python Tips</title>
    <script>
        // Analytics script
        function track() { }
    </script>
</head>
<body>
    <nav class="navbar">
        <a href="/home">Home</a>
        <a href="/blog">Blog</a>
    </nav>
    
    <article>
        <h1>10 Python Tips and Tricks</h1>
        <p>Python is a great language. Here are 10 tips to improve your code.</p>
        
        <h2>Tip 1: Use List Comprehensions</h2>
        <p>List comprehensions are more efficient than loops.</p>
        
        <h2>Tip 2: Use Type Hints</h2>
        <p>Type hints make your code more maintainable.</p>
    </article>
    
    <aside class="sidebar">
        <h3>Popular Posts</h3>
        <p>Related content...</p>
    </aside>
    
    <footer>
        <p>© 2026 My Blog. All rights reserved.</p>
    </footer>
    
    <div id="cookie-consent" class="cookie-banner">
        <p>We use cookies for analytics...</p>
    </div>
</body>
</html>
"""

# Quick extraction
cleaned_text = extract_text_from_html(sample_html)
print("Cleaned Text:")
print(cleaned_text)

print("\n" + "=" * 70)
print("EXAMPLE 2: Process multiple crawled pages")
print("=" * 70)

# Example 2: Process crawled pages
extractor = TextExtractor()

# Simulate output from the crawler
crawled_pages = [
    {
        'url': 'https://example.com/article1',
        'title': 'First Article',
        'html': sample_html,
        'error': None
    },
    {
        'url': 'https://example.com/article2',
        'title': 'Second Article',
        'html': '<h1>Article 2</h1><p>Content here</p>',
        'error': None
    },
    {
        'url': 'https://example.com/article3',
        'title': None,
        'html': None,
        'error': 'Timeout while fetching page'
    }
]

# Extract text from all pages
extracted_pages = extractor.process_pages(crawled_pages)

print(f"\nProcessed {len(extracted_pages)} pages successfully\n")
for page in extracted_pages:
    print(f"URL: {page.url}")
    print(f"Title: {page.title}")
    print(f"Text preview: {page.cleaned_text[:100]}...")
    print()

print("=" * 70)
print("EXAMPLE 3: Using the TextExtractor with custom options")
print("=" * 70)

# You can extend TextExtractor to customize noise removal
extractor = TextExtractor()

# The extractor removes:
# - Navigation bars (nav, .navbar, etc.)
# - Footers (footer, [role="contentinfo"])
# - Scripts and styles
# - Cookie banners and modals
# - Advertisements
# - And other common noise patterns

# Create an instance and use it
html_with_ads = """
<html>
<body>
    <div class="advertisement">
        <p>Buy our product!</p>
    </div>
    <article>
        <h1>Real Content</h1>
        <p>This is the actual article content.</p>
    </article>
    <div id="popup-modal" class="modal">
        <p>Subscribe to our newsletter!</p>
    </div>
</body>
</html>
"""

cleaned = extractor.extract(html_with_ads)
print("Text after removing ads and popups:")
print(cleaned)

print("\n" + "=" * 70)
print("API USAGE (with curl or similar):")
print("=" * 70)
print("""
# POST request to extract text from a website
curl -X POST "http://localhost:8000/extract" \\
  -H "Content-Type: application/json" \\
  -d '{
    "base_url": "https://example.com",
    "max_depth": 2,
    "max_pages": 10
  }'

# GET request
curl "http://localhost:8000/extract?base_url=https://example.com&max_depth=2&max_pages=10"

# Response structure:
{
  "total_extracted": 8,
  "extracted_pages": [
    {
      "url": "https://example.com/page1",
      "title": "Page Title",
      "cleaned_text": "Cleaned text content..."
    },
    ...
  ]
}
""")
