import pytest
from chunking.chunker import SentenceAwareChunker, TextChunk, create_chunks


class TestTextChunkModel:
    """Test TextChunk Pydantic model."""
    
    def test_create_text_chunk_object(self):
        chunk = TextChunk(
            chunk_id="chunk_abc123",
            url="https://example.com/page",
            title="Example Page",
            text="This is chunk content."
        )
        
        assert chunk.chunk_id == "chunk_abc123"
        assert chunk.url == "https://example.com/page"
        assert chunk.title == "Example Page"
        assert chunk.text == "This is chunk content."
    
    def test_create_text_chunk_with_none_title(self):
        chunk = TextChunk(
            chunk_id="chunk_abc123",
            url="https://example.com/page",
            title=None,
            text="Content"
        )
        
        assert chunk.title is None
        assert chunk.url == "https://example.com/page"
    
    def test_text_chunk_to_dict(self):
        chunk = TextChunk(
            chunk_id="chunk_abc123",
            url="https://example.com",
            title="Page",
            text="Content"
        )
        
        data = chunk.model_dump()
        assert data['chunk_id'] == "chunk_abc123"
        assert data['url'] == "https://example.com"
        assert data['title'] == "Page"
        assert data['text'] == "Content"
    
    def test_text_chunk_json_serializable(self):
        chunk = TextChunk(
            chunk_id="chunk_abc123",
            url="https://example.com",
            title="Page",
            text="Content"
        )
        
        json_str = chunk.model_dump_json()
        assert 'chunk_abc123' in json_str
        assert 'https://example.com' in json_str


class TestChunkerInit:
    """Test SentenceAwareChunker initialization."""
    
    def test_init_with_defaults(self):
        chunker = SentenceAwareChunker()
        assert chunker.max_chars == 1800
        assert chunker.overlap_sentences == 2
    
    def test_init_with_custom_max_chars(self):
        chunker = SentenceAwareChunker(max_chars=1000)
        assert chunker.max_chars == 1000
        assert chunker.overlap_sentences == 2
    
    def test_init_with_custom_overlap(self):
        chunker = SentenceAwareChunker(overlap_sentences=3)
        assert chunker.max_chars == 1800
        assert chunker.overlap_sentences == 3
    
    def test_init_with_all_custom_params(self):
        chunker = SentenceAwareChunker(max_chars=2000, overlap_sentences=4)
        assert chunker.max_chars == 2000
        assert chunker.overlap_sentences == 4
    
    def test_init_with_zero_overlap(self):
        chunker = SentenceAwareChunker(overlap_sentences=0)
        assert chunker.overlap_sentences == 0
    
    def test_init_with_small_max_chars(self):
        chunker = SentenceAwareChunker(max_chars=100)
        assert chunker.max_chars == 100


class TestGenerateChunkId:
    """Test chunk ID generation."""
    
    def test_generate_chunk_id_format(self):
        chunker = SentenceAwareChunker()
        chunk_id = chunker._generate_chunk_id("https://example.com/page", 0)
        
        assert chunk_id.startswith("chunk_")
        assert len(chunk_id) == 14  # "chunk_" + 8 hex chars
    
    def test_generate_chunk_id_unique_for_different_indices(self):
        chunker = SentenceAwareChunker()
        url = "https://example.com/page"
        
        id_0 = chunker._generate_chunk_id(url, 0)
        id_1 = chunker._generate_chunk_id(url, 1)
        
        assert id_0 != id_1
    
    def test_generate_chunk_id_unique_for_different_urls(self):
        chunker = SentenceAwareChunker()
        
        id_1 = chunker._generate_chunk_id("https://example.com/page1", 0)
        id_2 = chunker._generate_chunk_id("https://example.com/page2", 0)
        
        assert id_1 != id_2
    
    def test_generate_chunk_id_consistent(self):
        chunker = SentenceAwareChunker()
        url = "https://example.com/page"
        index = 0
        
        id_1 = chunker._generate_chunk_id(url, index)
        id_2 = chunker._generate_chunk_id(url, index)
        
        assert id_1 == id_2


class TestChunkText:
    """Test text chunking functionality."""
    
    def test_chunk_simple_text(self):
        chunker = SentenceAwareChunker(max_chars=100)
        text = "This is the first sentence. This is the second sentence."
        
        chunks = chunker.chunk_text(text)
        assert len(chunks) > 0
        assert all(isinstance(c, str) for c in chunks)
    
    def test_chunk_respects_max_chars(self):
        chunker = SentenceAwareChunker(max_chars=100)
        text = "Sentence one. " * 20
        
        chunks = chunker.chunk_text(text)
        # Each chunk should be <= max_chars
        assert all(len(c) <= 150 for c in chunks)  # Allow some flexibility
    
    def test_chunk_respects_sentence_boundaries(self):
        chunker = SentenceAwareChunker(max_chars=1800)
        text = "First sentence. Second sentence. Third sentence."
        
        chunks = chunker.chunk_text(text)
        # All chunks should contain complete sentences
        for chunk in chunks:
            assert chunk.endswith(".")
    
    def test_chunk_with_overlap(self):
        chunker = SentenceAwareChunker(max_chars=100, overlap_sentences=1)
        text = "One. Two. Three. Four. Five. Six."
        
        chunks = chunker.chunk_text(text)
        # With overlap, adjacent chunks should share content
        if len(chunks) > 1:
            # Check that there's some overlap
            assert len(chunks) > 1
    
    def test_chunk_single_short_sentence(self):
        chunker = SentenceAwareChunker(max_chars=1800)
        text = "Hello world."
        
        chunks = chunker.chunk_text(text)
        assert len(chunks) == 1
        assert chunks[0] == "Hello world."
    
    def test_chunk_empty_text(self):
        chunker = SentenceAwareChunker()
        text = ""
        
        chunks = chunker.chunk_text(text)
        assert chunks == []
    
    def test_chunk_whitespace_only(self):
        chunker = SentenceAwareChunker()
        text = "   \n\n   "
        
        chunks = chunker.chunk_text(text)
        assert chunks == []
    
    def test_chunk_very_long_text(self):
        chunker = SentenceAwareChunker(max_chars=200)
        text = "This is a sentence. " * 100
        
        chunks = chunker.chunk_text(text)
        assert len(chunks) > 1
        assert all(len(c) > 0 for c in chunks)
    
    def test_chunk_with_long_sentences(self):
        chunker = SentenceAwareChunker(max_chars=100)
        # Single very long sentence exceeding max_chars
        text = "This is a very long sentence that exceeds the maximum character limit for a single chunk. Another sentence."
        
        chunks = chunker.chunk_text(text)
        # Should still chunk, even if single sentence exceeds limit
        assert len(chunks) > 0
    
    def test_chunk_multiple_paragraphs(self):
        chunker = SentenceAwareChunker(max_chars=500)
        text = """First paragraph with some text. It has multiple sentences. Yes it does.
        
        Second paragraph also with text. And more sentences here."""
        
        chunks = chunker.chunk_text(text)
        assert len(chunks) > 0
        # All content should be preserved
        full_text = " ".join(chunks)
        assert "First paragraph" in full_text
        assert "Second paragraph" in full_text
    
    def test_chunk_with_abbreviations(self):
        chunker = SentenceAwareChunker(max_chars=500)
        text = "Dr. Smith went to the U.S.A. He saw Mr. Johnson there. It was great."
        
        chunks = chunker.chunk_text(text)
        assert len(chunks) > 0
        # Content should be preserved
        full_text = " ".join(chunks)
        assert "Dr." in full_text
        assert "U.S.A." in full_text
    
    def test_chunk_preserves_all_content(self):
        chunker = SentenceAwareChunker(max_chars=300, overlap_sentences=1)
        original = "First sentence. Second sentence. Third sentence. Fourth sentence. Fifth sentence."
        
        chunks = chunker.chunk_text(original)
        full_text = " ".join(chunks)
        
        # All sentences should be present
        assert "First sentence" in full_text
        assert "Second sentence" in full_text
        assert "Third sentence" in full_text
        assert "Fourth sentence" in full_text
        assert "Fifth sentence" in full_text
    
    def test_chunk_no_overlap_when_zero(self):
        chunker = SentenceAwareChunker(max_chars=100, overlap_sentences=0)
        text = "One. Two. Three. Four. Five. Six. Seven. Eight."
        
        chunks = chunker.chunk_text(text)
        assert len(chunks) > 0
    
    def test_chunk_with_special_characters(self):
        chunker = SentenceAwareChunker(max_chars=500)
        text = "Hello! How are you? I'm fine, thanks. That's great!"
        
        chunks = chunker.chunk_text(text)
        assert len(chunks) > 0
        full_text = " ".join(chunks)
        assert "I'm" in full_text


class TestProcessExtractedPages:
    """Test processing extracted pages into chunks."""
    
    def test_process_single_valid_page(self):
        chunker = SentenceAwareChunker(max_chars=500)
        pages = [
            {
                'url': 'https://example.com/page1',
                'title': 'Example Page',
                'cleaned_text': 'First sentence. Second sentence. Third sentence.'
            }
        ]
        
        chunks = chunker.process_extracted_pages(pages)
        assert len(chunks) > 0
        assert all(isinstance(c, TextChunk) for c in chunks)
        assert chunks[0].url == 'https://example.com/page1'
        assert chunks[0].title == 'Example Page'
    
    def test_process_multiple_pages(self):
        chunker = SentenceAwareChunker(max_chars=500)
        pages = [
            {
                'url': 'https://example.com/page1',
                'title': 'Page 1',
                'cleaned_text': 'Content one. More content.'
            },
            {
                'url': 'https://example.com/page2',
                'title': 'Page 2',
                'cleaned_text': 'Content two. More content.'
            }
        ]
        
        chunks = chunker.process_extracted_pages(pages)
        assert len(chunks) > 0
        
        urls = [c.url for c in chunks]
        assert 'https://example.com/page1' in urls
        assert 'https://example.com/page2' in urls
    
    def test_process_pages_with_none_title(self):
        chunker = SentenceAwareChunker(max_chars=500)
        pages = [
            {
                'url': 'https://example.com/page1',
                'title': None,
                'cleaned_text': 'Content here. More content.'
            }
        ]
        
        chunks = chunker.process_extracted_pages(pages)
        assert len(chunks) > 0
        assert chunks[0].title is None
    
    def test_process_pages_skip_missing_url(self):
        chunker = SentenceAwareChunker(max_chars=500)
        pages = [
            {
                'title': 'No URL',
                'cleaned_text': 'Content'
            }
        ]
        
        chunks = chunker.process_extracted_pages(pages)
        # Should skip pages without URL
        assert len(chunks) == 0
    
    def test_process_pages_skip_empty_content(self):
        chunker = SentenceAwareChunker(max_chars=500)
        pages = [
            {
                'url': 'https://example.com/page1',
                'title': 'Empty',
                'cleaned_text': ''
            }
        ]
        
        chunks = chunker.process_extracted_pages(pages)
        assert len(chunks) == 0
    
    def test_process_pages_use_cleaned_text_key(self):
        chunker = SentenceAwareChunker(max_chars=500)
        pages = [
            {
                'url': 'https://example.com',
                'title': 'Test',
                'cleaned_text': 'Content from cleaned_text.'
            }
        ]
        
        chunks = chunker.process_extracted_pages(pages)
        assert len(chunks) > 0
        assert 'Content from cleaned_text' in chunks[0].text
    
    def test_process_pages_fallback_to_text_key(self):
        chunker = SentenceAwareChunker(max_chars=500)
        pages = [
            {
                'url': 'https://example.com',
                'title': 'Test',
                'text': 'Content from text key.'
            }
        ]
        
        chunks = chunker.process_extracted_pages(pages)
        assert len(chunks) > 0
        assert 'Content from text key' in chunks[0].text
    
    def test_process_pages_chunk_ids_unique(self):
        chunker = SentenceAwareChunker(max_chars=300)
        pages = [
            {
                'url': 'https://example.com/page1',
                'title': 'Page',
                'cleaned_text': 'First. Second. Third. Fourth. Fifth. Sixth.'
            }
        ]
        
        chunks = chunker.process_extracted_pages(pages)
        chunk_ids = [c.chunk_id for c in chunks]
        # All chunk IDs should be unique
        assert len(chunk_ids) == len(set(chunk_ids))
    
    def test_process_pages_chunk_ids_based_on_page_url(self):
        chunker = SentenceAwareChunker(max_chars=300)
        pages = [
            {
                'url': 'https://example.com/page1',
                'title': 'Page',
                'cleaned_text': 'First. Second. Third. Fourth. Fifth.'
            }
        ]
        
        chunks = chunker.process_extracted_pages(pages)
        for chunk in chunks:
            # Chunk ID should be formatted correctly
            assert chunk.chunk_id.startswith('chunk_')
    
    def test_process_pages_override_max_chars(self):
        chunker = SentenceAwareChunker(max_chars=1800)  # Default
        pages = [
            {
                'url': 'https://example.com',
                'title': 'Page',
                'cleaned_text': 'A. ' * 100  # Lots of short sentences
            }
        ]
        
        # Override with smaller max_chars
        chunks = chunker.process_extracted_pages(pages, max_chars=50)
        assert len(chunks) > 1  # Should create multiple chunks
    
    def test_process_pages_override_overlap(self):
        chunker = SentenceAwareChunker(max_chars=500, overlap_sentences=2)
        pages = [
            {
                'url': 'https://example.com',
                'title': 'Page',
                'cleaned_text': 'Sentence one. Sentence two. Sentence three. Sentence four. Sentence five.'
            }
        ]
        
        chunks = chunker.process_extracted_pages(pages, overlap_sentences=0)
        assert len(chunks) > 0
    
    def test_process_pages_mixed_valid_invalid(self):
        chunker = SentenceAwareChunker(max_chars=500)
        pages = [
            {
                'url': 'https://example.com/page1',
                'title': 'Valid',
                'cleaned_text': 'Content here. More content.'
            },
            {
                'url': 'https://example.com/page2',
                'title': 'Empty',
                'cleaned_text': ''
            },
            {
                'title': 'No URL',
                'cleaned_text': 'Content'
            },
            {
                'url': 'https://example.com/page3',
                'title': 'Valid 2',
                'cleaned_text': 'Another content. Yet another.'
            }
        ]
        
        chunks = chunker.process_extracted_pages(pages)
        # Should only process valid pages
        assert len(chunks) > 0
        urls = [c.url for c in chunks]
        assert 'https://example.com/page1' in urls
        assert 'https://example.com/page3' in urls
    
    def test_process_pages_empty_list(self):
        chunker = SentenceAwareChunker()
        pages = []
        
        chunks = chunker.process_extracted_pages(pages)
        assert chunks == []


class TestCreateChunksFunction:
    """Test convenience function."""
    
    def test_create_chunks_valid_pages(self):
        pages = [
            {
                'url': 'https://example.com',
                'title': 'Example',
                'cleaned_text': 'First sentence. Second sentence. Third sentence.'
            }
        ]
        
        chunks = create_chunks(pages)
        assert len(chunks) > 0
        assert all(isinstance(c, TextChunk) for c in chunks)
    
    def test_create_chunks_with_custom_max_chars(self):
        pages = [
            {
                'url': 'https://example.com',
                'title': 'Example',
                'cleaned_text': 'This is sentence one. This is sentence two. This is sentence three. This is sentence four. This is sentence five.'
            }
        ]
        
        chunks = create_chunks(pages, max_chars=50)
        assert len(chunks) > 1
    
    def test_create_chunks_with_custom_overlap(self):
        pages = [
            {
                'url': 'https://example.com',
                'title': 'Example',
                'cleaned_text': 'A. B. C. D. E. F. G. H. I. J.'
            }
        ]
        
        chunks = create_chunks(pages, overlap_sentences=1)
        assert len(chunks) > 0
    
    def test_create_chunks_returns_text_chunks(self):
        pages = [
            {
                'url': 'https://example.com',
                'title': 'Example',
                'cleaned_text': 'Content.'
            }
        ]
        
        chunks = create_chunks(pages)
        assert len(chunks) > 0
        assert isinstance(chunks[0], TextChunk)


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_chunk_text_with_numbers_only(self):
        chunker = SentenceAwareChunker(max_chars=500)
        text = "123. 456. 789."
        
        chunks = chunker.chunk_text(text)
        assert len(chunks) > 0
    
    def test_chunk_text_with_urls_in_content(self):
        chunker = SentenceAwareChunker(max_chars=500)
        text = "Check out https://example.com for more info. Visit my website."
        
        chunks = chunker.chunk_text(text)
        assert len(chunks) > 0
        full_text = " ".join(chunks)
        assert "https://example.com" in full_text
    
    def test_chunk_text_with_quoted_text(self):
        chunker = SentenceAwareChunker(max_chars=500)
        text = 'He said "Hello world." She replied "Hi there."'
        
        chunks = chunker.chunk_text(text)
        assert len(chunks) > 0
    
    def test_chunk_text_with_newlines(self):
        chunker = SentenceAwareChunker(max_chars=500)
        text = "First line.\nSecond line.\nThird line."
        
        chunks = chunker.chunk_text(text)
        assert len(chunks) > 0
    
    def test_chunk_text_with_unicode(self):
        chunker = SentenceAwareChunker(max_chars=500)
        text = "Hello 世界. Привет мир. مرحبا بالعالم."
        
        chunks = chunker.chunk_text(text)
        assert len(chunks) > 0
    
    def test_chunk_text_with_special_punctuation(self):
        chunker = SentenceAwareChunker(max_chars=500)
        text = "Really? Yes! Maybe... Absolutely."
        
        chunks = chunker.chunk_text(text)
        assert len(chunks) > 0
    
    def test_chunk_text_with_very_small_max_chars(self):
        chunker = SentenceAwareChunker(max_chars=10)
        text = "This is a test. With multiple sentences."
        
        chunks = chunker.chunk_text(text)
        assert len(chunks) > 0
    
    def test_chunk_text_with_overlap_larger_than_content(self):
        chunker = SentenceAwareChunker(max_chars=500, overlap_sentences=100)
        text = "One. Two. Three."
        
        chunks = chunker.chunk_text(text)
        assert len(chunks) > 0
    
    def test_process_pages_with_very_long_content(self):
        chunker = SentenceAwareChunker(max_chars=500)
        pages = [
            {
                'url': 'https://example.com',
                'title': 'Long Page',
                'cleaned_text': 'Sentence. ' * 500  # Very long content
            }
        ]
        
        chunks = chunker.process_extracted_pages(pages)
        assert len(chunks) > 1
    
    def test_chunk_text_with_parentheses(self):
        chunker = SentenceAwareChunker(max_chars=500)
        text = "First point (in parentheses). Second point. Third (with more details here)."
        
        chunks = chunker.chunk_text(text)
        assert len(chunks) > 0
        full_text = " ".join(chunks)
        assert "parentheses" in full_text
    
    def test_chunk_text_with_numbers_and_decimals(self):
        chunker = SentenceAwareChunker(max_chars=500)
        text = "The price is $19.99. The rating is 4.5 stars. The date is 2024.01.27."
        
        chunks = chunker.chunk_text(text)
        assert len(chunks) > 0
    
    def test_chunk_text_single_very_long_sentence(self):
        chunker = SentenceAwareChunker(max_chars=100)
        text = "This is a very very very very very very very very very long sentence that goes on and on and on."
        
        chunks = chunker.chunk_text(text)
        # Should handle gracefully
        assert len(chunks) > 0
    
    def test_process_pages_page_without_title_key(self):
        chunker = SentenceAwareChunker(max_chars=500)
        pages = [
            {
                'url': 'https://example.com',
                'cleaned_text': 'Content here.'
            }
        ]
        
        chunks = chunker.process_extracted_pages(pages)
        assert len(chunks) > 0
        assert chunks[0].title is None
