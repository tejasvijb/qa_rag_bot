"""
Quick test for text extraction functionality
"""
from text_extraction.text_extract import TextExtractor

# Sample HTML with noise (navbar, footer, scripts, etc.)
sample_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
    <script>
        // Some JavaScript code
        console.log('test');
    </script>
    <style>
        body { margin: 0; }
    </style>
</head>
<body>
    <nav class="navbar">
        <a href="/">Home</a>
        <a href="/about">About</a>
    </nav>
    
    <main>
        <h1>Welcome to Test Page</h1>
        <p>This is the main content that should be extracted.</p>
        
        <h2>Section Two</h2>
        <p>More content here that is important.</p>
        <p>And another paragraph.</p>
        
        <div class="sidebar">
            <p>This is sidebar content that should be removed.</p>
        </div>
    </main>
    
    <footer>
        <p>Copyright 2026 - All rights reserved</p>
    </footer>
    
    <!-- Cookie banner -->
    <div id="cookie-consent" class="cookie-banner">
        <p>We use cookies...</p>
    </div>
</body>
</html>
"""

def test_text_extraction():
    """Test the text extraction functionality."""
    extractor = TextExtractor()
    
    # Test basic extraction
    cleaned_text = extractor.extract(sample_html)
    
    print("=" * 60)
    print("EXTRACTED TEXT:")
    print("=" * 60)
    print(cleaned_text)
    print("=" * 60)
    
    # Verify that noise is removed
    assert "navbar" not in cleaned_text.lower()
    assert "footer" not in cleaned_text.lower()
    assert "copyright" not in cleaned_text.lower()
    assert "cookie" not in cleaned_text.lower()
    assert "javascript" not in cleaned_text.lower()
    
    # Verify that main content is present
    assert "Welcome" in cleaned_text
    assert "main content" in cleaned_text
    assert "Section Two" in cleaned_text
    assert "More content here" in cleaned_text
    assert "sidebar" not in cleaned_text.lower()
    
    print("\n[OK] All assertions passed!")
    print(f"[OK] Extracted text length: {len(cleaned_text)} characters")
    print(f"[OK] Number of lines: {len(cleaned_text.split(chr(10)))}")


def test_process_pages():
    """Test processing crawler output."""
    extractor = TextExtractor()
    
    # Simulate crawler output
    crawled_pages = [
        {
            'url': 'https://example.com/page1',
            'title': 'Page 1',
            'html': sample_html,
            'error': None
        },
        {
            'url': 'https://example.com/page2',
            'title': 'Page 2',
            'html': None,
            'error': 'Connection timeout'
        }
    ]
    
    extracted = extractor.process_pages(crawled_pages)
    
    print("\n" + "=" * 60)
    print("PROCESSED PAGES:")
    print("=" * 60)
    
    for page in extracted:
        print(f"\nURL: {page.url}")
        print(f"Title: {page.title}")
        print(f"Text length: {len(page.cleaned_text)} chars")
        print(f"Preview: {page.cleaned_text[:100]}...")
    
    assert len(extracted) == 1
    assert extracted[0].url == 'https://example.com/page1'
    print("\n[OK] Page processing works correctly!")


if __name__ == "__main__":
    print("Testing Text Extractor...\n")
    test_text_extraction()
    test_process_pages()
    print("\n[OK] All tests passed!")
