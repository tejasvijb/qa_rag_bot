import nltk
from nltk.tokenize import sent_tokenize
from typing import List, Dict, Optional
from pydantic import BaseModel
import hashlib

# Download punkt_tab tokenizer if not already present
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')


class TextChunk(BaseModel):
    """Model for a text chunk with metadata."""
    chunk_id: str
    url: str
    title: Optional[str]
    text: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "chunk_id": "chunk_abc123",
                "url": "https://example.com/page",
                "title": "Example Page",
                "text": "This is a chunk of text..."
            }
        }


class SentenceAwareChunker:
    """
    Splits text into sentence-aware chunks with overlap support.
    
    Features:
    - Respects sentence boundaries
    - Configurable maximum chunk size
    - Sentence-level overlap between chunks
    - Automatic chunk ID generation
    """
    
    def __init__(self, max_chars: int = 1800, overlap_sentences: int = 2):
        """
        Initialize the chunker.
        
        Args:
            max_chars: Maximum characters per chunk (default: 1800)
            overlap_sentences: Number of sentences to overlap between chunks (default: 2)
        """
        self.max_chars = max_chars
        self.overlap_sentences = overlap_sentences
    
    def _generate_chunk_id(self, url: str, index: int) -> str:
        """Generate a unique chunk ID based on URL and index."""
        base = f"{url}_{index}"
        hash_obj = hashlib.md5(base.encode())
        return f"chunk_{hash_obj.hexdigest()[:8]}"
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Splits text into sentence-aware chunks with overlap.
        
        Args:
            text: The text to chunk
            
        Returns:
            List of text chunks
        """
        sentences = sent_tokenize(text)
        chunks = []
        
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            # If adding this sentence exceeds max size, finalize chunk
            if current_length + sentence_length > self.max_chars and current_chunk:
                chunks.append(" ".join(current_chunk))
                
                # Overlap last N sentences
                current_chunk = current_chunk[-self.overlap_sentences:]
                current_length = sum(len(s) for s in current_chunk)
            
            current_chunk.append(sentence)
            current_length += sentence_length
        
        # Add remaining sentences
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    def process_extracted_pages(
        self,
        extracted_pages: List[Dict],
        max_chars: Optional[int] = None,
        overlap_sentences: Optional[int] = None
    ) -> List[TextChunk]:
        """
        Process extracted pages and create chunks with metadata.
        
        Args:
            extracted_pages: List of extracted page dictionaries with url, title, cleaned_text
            max_chars: Override default max_chars for this batch
            overlap_sentences: Override default overlap_sentences for this batch
            
        Returns:
            List of TextChunk objects with chunk_id, url, title, and text
        """
        # Use provided parameters or fall back to instance defaults
        max_chars = max_chars or self.max_chars
        overlap_sentences = overlap_sentences or self.overlap_sentences
        
        # Create a temporary chunker with potentially different parameters
        chunker = SentenceAwareChunker(max_chars=max_chars, overlap_sentences=overlap_sentences)
        
        chunks = []
        
        for page in extracted_pages:
            text = page.get('cleaned_text') or page.get('text', '')
            url = page.get('url')
            title = page.get('title')
            
            if not text or not url:
                continue
            
            # Chunk the text
            text_chunks = chunker.chunk_text(text)
            
            # Create TextChunk objects with metadata
            for idx, chunk_text in enumerate(text_chunks):
                chunk_id = chunker._generate_chunk_id(url, idx)
                chunks.append(
                    TextChunk(
                        chunk_id=chunk_id,
                        url=url,
                        title=title,
                        text=chunk_text
                    )
                )
        
        return chunks


# Convenience function for simple usage
def create_chunks(
    extracted_pages: List[Dict],
    max_chars: int = 1800,
    overlap_sentences: int = 2
) -> List[TextChunk]:
    """
    Quick function to create chunks from extracted pages.
    
    Args:
        extracted_pages: List of extracted page dictionaries
        max_chars: Maximum characters per chunk
        overlap_sentences: Number of sentences to overlap
        
    Returns:
        List of TextChunk objects
    """
    chunker = SentenceAwareChunker(max_chars=max_chars, overlap_sentences=overlap_sentences)
    return chunker.process_extracted_pages(extracted_pages)
