import pytest
from bs4 import BeautifulSoup, Comment, NavigableString
from text_extraction.text_extract import TextExtractor, ExtractedText, extract_text_from_html


class TestRemoveNoise:
    """Test noise removal from HTML."""
    
    def test_remove_nav_elements(self):
        html = '<html><body><nav>Navigation</nav><p>Content</p></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        extractor = TextExtractor()
        extractor.remove_noise(soup)
        
        assert soup.find('nav') is None
        assert soup.find('p') is not None
    
    def test_remove_footer_elements(self):
        html = '<html><body><p>Content</p><footer>Footer</footer></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        extractor = TextExtractor()
        extractor.remove_noise(soup)
        
        assert soup.find('footer') is None
        assert soup.find('p') is not None
    
    def test_remove_script_tags(self):
        html = '<html><body><script>var x = 1;</script><p>Content</p></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        extractor = TextExtractor()
        extractor.remove_noise(soup)
        
        assert soup.find('script') is None
        assert soup.find('p') is not None
    
    def test_remove_style_tags(self):
        html = '<html><body><style>.class { color: red; }</style><p>Content</p></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        extractor = TextExtractor()
        extractor.remove_noise(soup)
        
        assert soup.find('style') is None
        assert soup.find('p') is not None
    
    def test_remove_cookie_banner_by_class(self):
        html = '<html><body><div class="cookie-banner">Cookies</div><p>Content</p></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        extractor = TextExtractor()
        extractor.remove_noise(soup)
        
        cookie_div = soup.find('div', class_='cookie-banner')
        assert cookie_div is None
        assert soup.find('p') is not None
    
    def test_remove_cookie_banner_by_id(self):
        html = '<html><body><div id="cookie-consent">Cookies</div><p>Content</p></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        extractor = TextExtractor()
        extractor.remove_noise(soup)
        
        cookie_div = soup.find('div', id='cookie-consent')
        assert cookie_div is None
        assert soup.find('p') is not None
    
    def test_remove_modal_by_class(self):
        html = '<html><body><div class="modal">Modal</div><p>Content</p></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        extractor = TextExtractor()
        extractor.remove_noise(soup)
        
        modal = soup.find('div', class_='modal')
        assert modal is None
    
    def test_remove_popup_by_id(self):
        html = '<html><body><div id="popup-overlay">Popup</div><p>Content</p></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        extractor = TextExtractor()
        extractor.remove_noise(soup)
        
        popup = soup.find('div', id='popup-overlay')
        assert popup is None
    
    def test_remove_advertisement(self):
        html = '<html><body><div class="advertisement">Ad</div><p>Content</p></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        extractor = TextExtractor()
        extractor.remove_noise(soup)
        
        ad = soup.find('div', class_='advertisement')
        assert ad is None
    
    def test_remove_banner(self):
        html = '<html><body><div class="banner">Banner</div><p>Content</p></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        extractor = TextExtractor()
        extractor.remove_noise(soup)
        
        banner = soup.find('div', class_='banner')
        assert banner is None
    
    def test_remove_multiple_noise_elements(self):
        html = '''<html><body>
        <nav>Nav</nav>
        <p>Content</p>
        <script>var x = 1;</script>
        <footer>Footer</footer>
        <div class="cookie-banner">Cookies</div>
        </body></html>'''
        soup = BeautifulSoup(html, 'html.parser')
        extractor = TextExtractor()
        extractor.remove_noise(soup)
        
        assert soup.find('nav') is None
        assert soup.find('script') is None
        assert soup.find('footer') is None
        assert soup.find('div', class_='cookie-banner') is None
        assert soup.find('p') is not None


class TestExtractVisibleText:
    """Test visible text extraction from HTML."""
    
    def test_extract_simple_text(self):
        html = '<html><body><p>Hello World</p></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        extractor = TextExtractor()
        
        text = extractor.extract_visible_text(soup)
        assert "Hello World" in text
    
    def test_extract_multiple_paragraphs(self):
        html = '<html><body><p>First</p><p>Second</p></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        extractor = TextExtractor()
        
        text = extractor.extract_visible_text(soup)
        assert "First" in text
        assert "Second" in text
    
    def test_extract_with_headings(self):
        html = '<html><body><h1>Title</h1><p>Content</p></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        extractor = TextExtractor()
        
        text = extractor.extract_visible_text(soup)
        assert "Title" in text
        assert "Content" in text
    
    def test_heading_adds_line_break(self):
        html = '<html><body><h1>Title</h1><p>Content</p></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        extractor = TextExtractor()
        
        text = extractor.extract_visible_text(soup)
        # Should have newlines around heading
        assert '\n' in text
    
    def test_extract_without_body_tag(self):
        html = '<p>Content without body</p>'
        soup = BeautifulSoup(html, 'html.parser')
        extractor = TextExtractor()
        
        text = extractor.extract_visible_text(soup)
        assert "Content without body" in text
    
    def test_skip_html_comments(self):
        html = '<html><body><!-- This is a comment --><p>Content</p></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        extractor = TextExtractor()
        
        text = extractor.extract_visible_text(soup)
        assert "This is a comment" not in text
        assert "Content" in text
    
    def test_extract_nested_elements(self):
        html = '<html><body><div><p>Nested <span>content</span></p></div></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        extractor = TextExtractor()
        
        text = extractor.extract_visible_text(soup)
        assert "Nested" in text
        assert "content" in text
    
    def test_extract_empty_body(self):
        html = '<html><body></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        extractor = TextExtractor()
        
        text = extractor.extract_visible_text(soup)
        assert text == ""
    
    def test_extract_whitespace_only(self):
        html = '<html><body>   \n\n   </body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        extractor = TextExtractor()
        
        text = extractor.extract_visible_text(soup)
        assert text == ""
    
    def test_extract_all_heading_levels(self):
        html = '''<html><body>
        <h1>H1</h1>
        <h2>H2</h2>
        <h3>H3</h3>
        <h4>H4</h4>
        <h5>H5</h5>
        <h6>H6</h6>
        </body></html>'''
        soup = BeautifulSoup(html, 'html.parser')
        extractor = TextExtractor()
        
        text = extractor.extract_visible_text(soup)
        for i in range(1, 7):
            assert f"H{i}" in text


class TestCleanText:
    """Test text cleanup."""
    
    def test_remove_multiple_spaces(self):
        extractor = TextExtractor()
        text = "Hello    world"
        cleaned = extractor.clean_text(text)
        assert "Hello world" in cleaned
    
    def test_remove_multiple_newlines(self):
        extractor = TextExtractor()
        text = "First\n\n\nSecond"
        cleaned = extractor.clean_text(text)
        assert cleaned.count('\n') <= 1
    
    def test_strip_leading_trailing_whitespace(self):
        extractor = TextExtractor()
        text = "   Content   "
        cleaned = extractor.clean_text(text)
        assert cleaned == "Content"
    
    def test_preserve_single_newlines(self):
        extractor = TextExtractor()
        text = "First\nSecond"
        cleaned = extractor.clean_text(text)
        assert "First" in cleaned
        assert "Second" in cleaned
    
    def test_clean_complex_whitespace(self):
        extractor = TextExtractor()
        text = "  Multiple   spaces  \n\n\nand  newlines  \n  mixed  "
        cleaned = extractor.clean_text(text)
        
        assert not cleaned.startswith(' ')
        assert not cleaned.endswith(' ')
        # Should have reduced newlines but may still have some
        assert "Multiple" in cleaned
        assert "spaces" in cleaned
        assert "and" in cleaned
        assert "newlines" in cleaned
        assert "mixed" in cleaned


class TestExtract:
    """Test main extraction method."""
    
    def test_extract_valid_html(self):
        html = '<html><body><h1>Title</h1><p>Content</p></body></html>'
        extractor = TextExtractor()
        
        text = extractor.extract(html)
        assert "Title" in text
        assert "Content" in text
    
    def test_extract_with_noise_removal(self):
        html = '''<html><body>
        <nav>Navigation</nav>
        <h1>Title</h1>
        <p>Content</p>
        <footer>Footer info</footer>
        </body></html>'''
        extractor = TextExtractor()
        
        text = extractor.extract(html)
        assert "Title" in text
        assert "Content" in text
        assert "Navigation" not in text
        assert "Footer info" not in text
    
    def test_extract_empty_html(self):
        html = '<html><body></body></html>'
        extractor = TextExtractor()
        
        text = extractor.extract(html)
        assert text == ""
    
    def test_extract_only_noise_elements(self):
        html = '<html><body><nav>Nav</nav><footer>Footer</footer></body></html>'
        extractor = TextExtractor()
        
        text = extractor.extract(html)
        assert text == ""
    
    def test_extract_malformed_html(self):
        html = '<html><body><p>Content<script>var x;</body></html>'
        extractor = TextExtractor()
        
        text = extractor.extract(html)
        assert "Content" in text
    
    def test_extract_invalid_html_returns_empty(self):
        html = None
        extractor = TextExtractor()
        
        # Should handle None gracefully
        try:
            text = extractor.extract(html)
            # May return empty string or raise exception
        except (AttributeError, TypeError):
            # Expected behavior for invalid input
            pass
    
    def test_extract_preserves_content_structure(self):
        html = '''<html><body>
        <h1>Main Title</h1>
        <p>First paragraph.</p>
        <h2>Subsection</h2>
        <p>Second paragraph.</p>
        </body></html>'''
        extractor = TextExtractor()
        
        text = extractor.extract(html)
        assert "Main Title" in text
        assert "First paragraph" in text
        assert "Subsection" in text
        assert "Second paragraph" in text
    
    def test_extract_with_special_characters(self):
        html = '<html><body><p>Special chars: &amp; &lt; &gt; &quot;</p></body></html>'
        extractor = TextExtractor()
        
        text = extractor.extract(html)
        assert len(text) > 0


class TestProcessPages:
    """Test processing multiple pages."""
    
    def test_process_single_valid_page(self):
        pages = [
            {
                'url': 'https://example.com/page1',
                'title': 'Page 1',
                'html': '<html><body><p>Content 1</p></body></html>',
                'error': None
            }
        ]
        extractor = TextExtractor()
        
        results = extractor.process_pages(pages)
        assert len(results) == 1
        assert results[0].url == 'https://example.com/page1'
        assert results[0].title == 'Page 1'
        assert 'Content 1' in results[0].cleaned_text
    
    def test_process_multiple_valid_pages(self):
        pages = [
            {
                'url': 'https://example.com/page1',
                'title': 'Page 1',
                'html': '<html><body><p>Content 1</p></body></html>',
                'error': None
            },
            {
                'url': 'https://example.com/page2',
                'title': 'Page 2',
                'html': '<html><body><p>Content 2</p></body></html>',
                'error': None
            }
        ]
        extractor = TextExtractor()
        
        results = extractor.process_pages(pages)
        assert len(results) == 2
        assert results[0].url == 'https://example.com/page1'
        assert results[1].url == 'https://example.com/page2'
    
    def test_skip_pages_with_errors(self):
        pages = [
            {
                'url': 'https://example.com/page1',
                'title': 'Page 1',
                'html': '<html><body><p>Content 1</p></body></html>',
                'error': None
            },
            {
                'url': 'https://example.com/page2',
                'title': 'Page 2',
                'html': None,
                'error': 'Connection error'
            }
        ]
        extractor = TextExtractor()
        
        results = extractor.process_pages(pages)
        assert len(results) == 1
        assert results[0].url == 'https://example.com/page1'
    
    def test_skip_pages_with_no_html(self):
        pages = [
            {
                'url': 'https://example.com/page1',
                'title': 'Page 1',
                'html': None,
                'error': None
            }
        ]
        extractor = TextExtractor()
        
        results = extractor.process_pages(pages)
        assert len(results) == 0
    
    def test_skip_pages_with_no_extractable_text(self):
        pages = [
            {
                'url': 'https://example.com/page1',
                'title': 'Page 1',
                'html': '<html><body></body></html>',
                'error': None
            }
        ]
        extractor = TextExtractor()
        
        results = extractor.process_pages(pages)
        assert len(results) == 0
    
    def test_process_empty_list(self):
        pages = []
        extractor = TextExtractor()
        
        results = extractor.process_pages(pages)
        assert results == []
    
    def test_process_mixed_valid_invalid_pages(self):
        pages = [
            {
                'url': 'https://example.com/page1',
                'title': 'Valid',
                'html': '<html><body><p>Content</p></body></html>',
                'error': None
            },
            {
                'url': 'https://example.com/page2',
                'title': 'Error',
                'html': None,
                'error': 'Timeout'
            },
            {
                'url': 'https://example.com/page3',
                'title': 'Empty',
                'html': '<html><body></body></html>',
                'error': None
            },
            {
                'url': 'https://example.com/page4',
                'title': 'Valid 2',
                'html': '<html><body><h1>Title</h1></body></html>',
                'error': None
            }
        ]
        extractor = TextExtractor()
        
        results = extractor.process_pages(pages)
        assert len(results) == 2
        assert results[0].url == 'https://example.com/page1'
        assert results[1].url == 'https://example.com/page4'
    
    def test_returned_objects_are_extracted_text(self):
        pages = [
            {
                'url': 'https://example.com/page1',
                'title': 'Page 1',
                'html': '<html><body><p>Content</p></body></html>',
                'error': None
            }
        ]
        extractor = TextExtractor()
        
        results = extractor.process_pages(pages)
        assert isinstance(results[0], ExtractedText)
        assert hasattr(results[0], 'url')
        assert hasattr(results[0], 'title')
        assert hasattr(results[0], 'cleaned_text')


class TestExtractTextFromHtml:
    """Test convenience function."""
    
    def test_extract_text_from_html_valid(self):
        html = '<html><body><p>Hello World</p></body></html>'
        
        text = extract_text_from_html(html)
        assert "Hello World" in text
    
    def test_extract_text_from_html_with_noise(self):
        html = '''<html><body>
        <nav>Navigation</nav>
        <p>Content</p>
        <footer>Footer</footer>
        </body></html>'''
        
        text = extract_text_from_html(html)
        assert "Content" in text
        assert "Navigation" not in text
        assert "Footer" not in text
    
    def test_extract_text_from_html_empty(self):
        html = '<html><body></body></html>'
        
        text = extract_text_from_html(html)
        assert text == ""
    
    def test_extract_text_from_html_returns_string(self):
        html = '<html><body><p>Test</p></body></html>'
        
        text = extract_text_from_html(html)
        assert isinstance(text, str)


class TestExtractedTextModel:
    """Test ExtractedText Pydantic model."""
    
    def test_create_extracted_text_object(self):
        obj = ExtractedText(
            url='https://example.com',
            title='Example',
            cleaned_text='Content here'
        )
        
        assert obj.url == 'https://example.com'
        assert obj.title == 'Example'
        assert obj.cleaned_text == 'Content here'
    
    def test_extracted_text_with_none_title(self):
        obj = ExtractedText(
            url='https://example.com',
            title=None,
            cleaned_text='Content'
        )
        
        assert obj.title is None
        assert obj.cleaned_text == 'Content'
    
    def test_extracted_text_to_dict(self):
        obj = ExtractedText(
            url='https://example.com',
            title='Page',
            cleaned_text='Content'
        )
        
        data = obj.model_dump()
        assert data['url'] == 'https://example.com'
        assert data['title'] == 'Page'
        assert data['cleaned_text'] == 'Content'
    
    def test_extracted_text_json_serializable(self):
        obj = ExtractedText(
            url='https://example.com',
            title='Page',
            cleaned_text='Content'
        )
        
        json_str = obj.model_dump_json()
        assert 'https://example.com' in json_str
        assert 'Page' in json_str
        assert 'Content' in json_str


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_very_long_html(self):
        # HTML with 10000 paragraphs
        html = '<html><body>' + '<p>Paragraph</p>' * 10000 + '</body></html>'
        extractor = TextExtractor()
        
        text = extractor.extract(html)
        assert len(text) > 0
    
    def test_deeply_nested_elements(self):
        # Create deeply nested HTML
        html = '<html><body><div>' * 100 + 'Content' + '</div>' * 100 + '</body></html>'
        extractor = TextExtractor()
        
        text = extractor.extract(html)
        assert "Content" in text
    
    def test_html_with_unicode_characters(self):
        html = '<html><body><p>Hello 世界 مرحبا мир</p></body></html>'
        extractor = TextExtractor()
        
        text = extractor.extract(html)
        assert len(text) > 0
    
    def test_html_with_entities(self):
        html = '<html><body><p>&copy; 2024 &nbsp; &amp; &lt;test&gt;</p></body></html>'
        extractor = TextExtractor()
        
        text = extractor.extract(html)
        assert len(text) > 0
    
    def test_html_with_cdata_sections(self):
        html = '<html><body><p>Text</p><![CDATA[This is CDATA]]></body></html>'
        extractor = TextExtractor()
        
        text = extractor.extract(html)
        # Should not crash
        assert isinstance(text, str)
    
    def test_extract_from_pages_missing_required_keys(self):
        # Page missing 'url' key
        pages = [
            {
                'title': 'Page',
                'html': '<html><body><p>Content</p></body></html>',
                'error': None
            }
        ]
        extractor = TextExtractor()
        
        # Should handle gracefully or raise KeyError
        try:
            results = extractor.process_pages(pages)
        except KeyError:
            pass
    
    def test_html_with_only_script_and_style(self):
        html = '<html><body><script>var x = 1;</script><style>body{}</style></body></html>'
        extractor = TextExtractor()
        
        text = extractor.extract(html)
        assert text == ""
    
    def test_html_with_table_content(self):
        html = '''<html><body>
        <table>
            <tr><td>Cell 1</td><td>Cell 2</td></tr>
            <tr><td>Cell 3</td><td>Cell 4</td></tr>
        </table>
        </body></html>'''
        extractor = TextExtractor()
        
        text = extractor.extract(html)
        assert "Cell 1" in text
        assert "Cell 2" in text
    
    def test_html_with_list_content(self):
        html = '''<html><body>
        <ul>
            <li>Item 1</li>
            <li>Item 2</li>
        </ul>
        </body></html>'''
        extractor = TextExtractor()
        
        text = extractor.extract(html)
        assert "Item 1" in text
        assert "Item 2" in text
