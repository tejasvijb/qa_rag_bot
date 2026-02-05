from contextlib import asynccontextmanager
import time
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
from dotenv import load_dotenv
import logging
from api.v1.routes.userRoutes import router as auth_router
from api.v1.config.dbconnection import Base, init_db
from api.v1.models import *

# Import the crawler, text extractor, and chunker
from crawling.crawler import WebCrawler
from text_extraction.text_extract import TextExtractor, ExtractedText
from chunking.chunker import SentenceAwareChunker, TextChunk

# Import embeddings module
from embeddings.embeddings import add_embeddings, query_embeddings, get_or_create_collection

# Import ask module
from ask.ask import ask_question

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
# print(Base.metadata.tables.keys())



# Define lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database tables
    logger.info("Initializing database tables...")
    init_db()
    logger.info("Database tables initialized successfully")
    yield
    # Shutdown: Clean up if needed
    logger.info("Application shutting down...")

app = FastAPI(title="QA RAG Bot API", version="1.0.0", lifespan=lifespan)

# CORS Configuration
cors_options = {
    "allow_origins": os.getenv("FRONTEND_URL", "http://localhost:3000").split(","),
    "allow_credentials": True,
    "allow_methods": ["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization", "Cookie"],
}

# Add CORS middleware
app.add_middleware(CORSMiddleware, **cors_options)

# Add session middleware for cookie support
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "your-secret-key-change-this"))

# Request/Response models
class CrawlRequest(BaseModel):
    base_url: str
    max_depth: Optional[int] = 2
    max_pages: Optional[int] = 50


class IngestRequest(BaseModel):
    base_url: str
    max_depth: Optional[int] = 2
    max_pages: Optional[int] = 50
    max_chars: Optional[int] = 1800
    overlap_sentences: Optional[int] = 2
    collection_name: Optional[str] = "rag_bot"


class IngestResponse(BaseModel):
    status: str
    message: str
    crawled_pages: int
    extracted_pages: int
    total_chunks: int
    embeddings_added: int
    collection_name: str
    details: Dict


class PageData(BaseModel):
    url: str
    title: Optional[str]
    html: Optional[str]
    error: Optional[str]


class CrawlResponse(BaseModel):
    total_pages: int
    successful_pages: int
    failed_pages: int
    pages: List[PageData]


class ExtractRequest(BaseModel):
    base_url: str
    max_depth: Optional[int] = 2
    max_pages: Optional[int] = 50


class ExtractResponse(BaseModel):
    total_extracted: int
    extracted_pages: List[ExtractedText]


class ChunkRequest(BaseModel):
    base_url: str
    max_depth: Optional[int] = 2
    max_pages: Optional[int] = 50
    max_chars: Optional[int] = 1800
    overlap_sentences: Optional[int] = 2


class ChunkRequestWithPages(BaseModel):
    extracted_pages: List[ExtractedText]
    max_chars: Optional[int] = 1800
    overlap_sentences: Optional[int] = 2


class ChunkResponse(BaseModel):
    total_chunks: int
    chunks: List[TextChunk]


class RetrieveRequest(BaseModel):
    query: str
    n_results: Optional[int] = 5
    collection_name: Optional[str] = "rag_bot"


class RetrieveResult(BaseModel):
    rank: int
    text: str
    url: str
    title: Optional[str]
    distance: Optional[float] = None


class RetrieveResponse(BaseModel):
    status: str
    query: str
    collection_name: str
    total_results: int
    results: List[RetrieveResult]


class ContextUsed(BaseModel):
    text: str
    url: str
    title: Optional[str]
    distance: Optional[float] = None


class AskRequest(BaseModel):
    query: str
    n_results: Optional[int] = 5
    collection_name: Optional[str] = "rag_bot"


class AskResponse(BaseModel):
    status: str
    query: str
    answer: str
    context_used: List[ContextUsed]
    total_context_chunks: Optional[int] = None
    collection_name: str
    error: Optional[str] = None

app.include_router(auth_router)

@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "message": "QA RAG Bot API",
        "version": "1.0.0",
        "endpoints": {
            "crawl": "/crawl",
            "extract": "/extract",
            "chunk": "/chunk",
            "chunk-pages": "/chunk-pages",
            "ingest": "/ingest",
            "retrieve": "/retrieve",
            "ask": "/ask"
        }
    }


base_url = '/api/v1'

@app.post(f"{base_url}/crawl", response_model=CrawlResponse)
async def crawl_website(request: CrawlRequest):
    """
    Crawl a website starting from the given base URL.
    
    - **base_url**: The starting URL to crawl
    - **max_depth**: Maximum depth of links to follow (default: 2)
    - **max_pages**: Maximum number of pages to crawl (default: 50)
    
    Returns crawled pages with URL, title, HTML content, and any errors.
    """
    
    # Validate base_url
    if not request.base_url.startswith(('http://', 'https://')):
        raise HTTPException(status_code=400, detail="URL must start with http:// or https://")
    
    # Validate parameters
    if request.max_depth < 1 or request.max_depth > 10:
        raise HTTPException(status_code=400, detail="max_depth must be between 1 and 10")
    
    if request.max_pages < 1 or request.max_pages > 500:
        raise HTTPException(status_code=400, detail="max_pages must be between 1 and 500")
    
    try:
        # Create and run crawler
        crawler = WebCrawler(
            base_url=request.base_url,
            max_depth=request.max_depth,
            max_pages=request.max_pages,
            timeout=10  # 10 second timeout for each page
        )
        
        pages = crawler.crawl()
        
        # Calculate statistics
        successful = sum(1 for page in pages if page['error'] is None)
        failed = sum(1 for page in pages if page['error'] is not None)
        
        return CrawlResponse(
            total_pages=len(pages),
            successful_pages=successful,
            failed_pages=failed,
            pages=[PageData(**page) for page in pages]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crawling error: {str(e)}")


@app.get(f"{base_url}/crawl", response_model=CrawlResponse)
async def crawl_website_get(
    base_url: str = Query(..., description="The starting URL to crawl"),
    max_depth: int = Query(2, description="Maximum depth of links to follow"),
    max_pages: int = Query(50, description="Maximum number of pages to crawl")
):
    """
    Crawl a website using GET request parameters.
    
    - **base_url**: The starting URL to crawl
    - **max_depth**: Maximum depth of links to follow (default: 2)
    - **max_pages**: Maximum number of pages to crawl (default: 50)
    """
    request = CrawlRequest(base_url=base_url, max_depth=max_depth, max_pages=max_pages)
    return await crawl_website(request)


@app.post(f"{base_url}/extract", response_model=ExtractResponse)
async def extract_text(request: ExtractRequest):
    """
    Crawl a website and extract clean text from all pages.
    
    - **base_url**: The starting URL to crawl
    - **max_depth**: Maximum depth of links to follow (default: 2)
    - **max_pages**: Maximum number of pages to crawl (default: 50)
    
    Returns cleaned text with URL and title, with noise removed and heading boundaries marked.
    """
    
    # Validate base_url
    if not request.base_url.startswith(('http://', 'https://')):
        raise HTTPException(status_code=400, detail="URL must start with http:// or https://")
    
    # Validate parameters
    if request.max_depth < 1 or request.max_depth > 10:
        raise HTTPException(status_code=400, detail="max_depth must be between 1 and 10")
    
    if request.max_pages < 1 or request.max_pages > 500:
        raise HTTPException(status_code=400, detail="max_pages must be between 1 and 500")
    
    try:
        # Create and run crawler
        crawler = WebCrawler(
            base_url=request.base_url,
            max_depth=request.max_depth,
            max_pages=request.max_pages,
            timeout=10
        )
        
        pages = crawler.crawl()
        
        # Extract text from crawled pages
        extractor = TextExtractor()
        extracted_pages = extractor.process_pages(pages)
        
        return ExtractResponse(
            total_extracted=len(extracted_pages),
            extracted_pages=extracted_pages
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction error: {str(e)}")


@app.get(f"{base_url}/extract", response_model=ExtractResponse)
async def extract_text_get(
    base_url: str = Query(..., description="The starting URL to crawl"),
    max_depth: int = Query(2, description="Maximum depth of links to follow"),
    max_pages: int = Query(50, description="Maximum number of pages to crawl")
):
    """
    Crawl a website and extract clean text using GET request parameters.
    
    - **base_url**: The starting URL to crawl
    - **max_depth**: Maximum depth of links to follow (default: 2)
    - **max_pages**: Maximum number of pages to crawl (default: 50)
    """
    request = ExtractRequest(base_url=base_url, max_depth=max_depth, max_pages=max_pages)
    return await extract_text(request)


@app.post(f"{base_url}/chunk", response_model=ChunkResponse)
async def chunk_pages(request: ChunkRequest):
    """
    Chunk a website starting from base URL and return chunked data.
    
    - **base_url**: The starting URL to crawl
    - **max_depth**: Maximum depth of links to follow (default: 2)
    - **max_pages**: Maximum number of pages to crawl (default: 50)
    - **max_chars**: Maximum characters per chunk (default: 1800)
    - **overlap_sentences**: Number of sentences to overlap between chunks (default: 2)
    
    Returns chunks with chunk_id, url, title, and text.
    """
    
    # Validate base_url
    if not request.base_url.startswith(('http://', 'https://')):
        raise HTTPException(status_code=400, detail="URL must start with http:// or https://")
    
    # Validate parameters
    if request.max_depth < 1 or request.max_depth > 10:
        raise HTTPException(status_code=400, detail="max_depth must be between 1 and 10")
    
    if request.max_pages < 1 or request.max_pages > 500:
        raise HTTPException(status_code=400, detail="max_pages must be between 1 and 500")
    
    if request.max_chars < 100 or request.max_chars > 10000:
        raise HTTPException(status_code=400, detail="max_chars must be between 100 and 10000")
    
    if request.overlap_sentences < 0 or request.overlap_sentences > 10:
        raise HTTPException(status_code=400, detail="overlap_sentences must be between 0 and 10")
    
    try:
        # Create and run crawler
        crawler = WebCrawler(
            base_url=request.base_url,
            max_depth=request.max_depth,
            max_pages=request.max_pages,
            timeout=10
        )
        
        pages = crawler.crawl()
        
        # Extract text from crawled pages
        extractor = TextExtractor()
        extracted_pages = extractor.process_pages(pages)
        
        # Create chunker
        chunker = SentenceAwareChunker(
            max_chars=request.max_chars,
            overlap_sentences=request.overlap_sentences
        )
        
        # Convert ExtractedText objects to dictionaries for processing
        pages_data = [
            {
                'url': page.url,
                'title': page.title,
                'cleaned_text': page.cleaned_text
            }
            for page in extracted_pages
        ]
        
        # Process and create chunks
        chunks = chunker.process_extracted_pages(pages_data)
        
        return ChunkResponse(
            total_chunks=len(chunks),
            chunks=chunks
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chunking error: {str(e)}")


@app.get(f"{base_url}/chunk", response_model=ChunkResponse)
async def chunk_pages_get(
    base_url: str = Query(..., description="The starting URL to crawl"),
    max_depth: int = Query(2, description="Maximum depth of links to follow"),
    max_pages: int = Query(50, description="Maximum number of pages to crawl"),
    max_chars: int = Query(1800, description="Maximum characters per chunk"),
    overlap_sentences: int = Query(2, description="Number of sentences to overlap between chunks")
):
    """
    Chunk a website using GET request parameters.
    
    - **base_url**: The starting URL to crawl
    - **max_depth**: Maximum depth of links to follow (default: 2)
    - **max_pages**: Maximum number of pages to crawl (default: 50)
    - **max_chars**: Maximum characters per chunk (default: 1800)
    - **overlap_sentences**: Number of sentences to overlap between chunks (default: 2)
    """
    request = ChunkRequest(
        base_url=base_url,
        max_depth=max_depth,
        max_pages=max_pages,
        max_chars=max_chars,
        overlap_sentences=overlap_sentences
    )
    return await chunk_pages(request)


@app.post(f"{base_url}/chunk-pages", response_model=ChunkResponse)
async def chunk_extracted_pages(request: ChunkRequestWithPages):
    """
    Chunk already-extracted pages into sentence-aware chunks.
    
    - **extracted_pages**: List of ExtractedText objects with cleaned text
    - **max_chars**: Maximum characters per chunk (default: 1800)
    - **overlap_sentences**: Number of sentences to overlap between chunks (default: 2)
    
    Returns chunks with chunk_id, url, title, and text.
    """
    
    # Validate parameters
    if request.max_chars < 100 or request.max_chars > 10000:
        raise HTTPException(status_code=400, detail="max_chars must be between 100 and 10000")
    
    if request.overlap_sentences < 0 or request.overlap_sentences > 10:
        raise HTTPException(status_code=400, detail="overlap_sentences must be between 0 and 10")
    
    try:
        # Create chunker
        chunker = SentenceAwareChunker(
            max_chars=request.max_chars,
            overlap_sentences=request.overlap_sentences
        )
        
        # Convert ExtractedText objects to dictionaries for processing
        pages_data = [
            {
                'url': page.url,
                'title': page.title,
                'cleaned_text': page.cleaned_text
            }
            for page in request.extracted_pages
        ]
        
        # Process and create chunks
        chunks = chunker.process_extracted_pages(pages_data)
        
        return ChunkResponse(
            total_chunks=len(chunks),
            chunks=chunks
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chunking error: {str(e)}")


@app.post(f"{base_url}/ingest", response_model=IngestResponse)
async def ingest_website(request: IngestRequest):
    """
    Complete ingestion pipeline: crawl, extract, chunk, and store embeddings.
    
    - **base_url**: The starting URL to crawl
    - **max_depth**: Maximum depth of links to follow (default: 2)
    - **max_pages**: Maximum number of pages to crawl (default: 50)
    - **max_chars**: Maximum characters per chunk (default: 1800)
    - **overlap_sentences**: Number of sentences to overlap between chunks (default: 2)
    - **collection_name**: Chroma collection name (default: "rag_bot")
    
    Returns ingestion status with crawl, extraction, chunking, and embedding statistics.
    """
    
    logger.info(f"Starting ingest pipeline for URL: {request.base_url}")
    
    # Validate base_url
    if not request.base_url.startswith(('http://', 'https://')):
        raise HTTPException(status_code=400, detail="URL must start with http:// or https://")
    
    # Validate parameters
    if request.max_depth < 1 or request.max_depth > 10:
        raise HTTPException(status_code=400, detail="max_depth must be between 1 and 10")
    
    if request.max_pages < 1 or request.max_pages > 500:
        raise HTTPException(status_code=400, detail="max_pages must be between 1 and 500")
    
    if request.max_chars < 100 or request.max_chars > 10000:
        raise HTTPException(status_code=400, detail="max_chars must be between 100 and 10000")
    
    if request.overlap_sentences < 0 or request.overlap_sentences > 10:
        raise HTTPException(status_code=400, detail="overlap_sentences must be between 0 and 10")
    
    try:
        details = {}
        
        # Step 1: Crawl the website
        logger.info(f"[CRAWL] Starting crawl with max_depth={request.max_depth}, max_pages={request.max_pages}")
        crawler = WebCrawler(
            base_url=request.base_url,
            max_depth=request.max_depth,
            max_pages=request.max_pages,
            timeout=10
        )
        
        pages = crawler.crawl()
        successful_pages = sum(1 for page in pages if page['error'] is None)
        failed_pages = sum(1 for page in pages if page['error'] is not None)
        
        logger.info(f"[CRAWL] Completed: {successful_pages} successful, {failed_pages} failed pages")
        details['crawl_summary'] = {
            'total_pages': len(pages),
            'successful_pages': successful_pages,
            'failed_pages': failed_pages
        }
        
        # Step 2: Extract text from crawled pages
        logger.info(f"[EXTRACT] Starting text extraction from {successful_pages} pages")
        extractor = TextExtractor()
        extracted_pages = extractor.process_pages(pages)
        
        logger.info(f"[EXTRACT] Completed: {len(extracted_pages)} pages extracted")
        details['extraction_summary'] = {
            'total_extracted': len(extracted_pages)
        }
        
        # Step 3: Chunk the extracted text
        logger.info(f"[CHUNK] Starting chunking with max_chars={request.max_chars}, overlap_sentences={request.overlap_sentences}")
        chunker = SentenceAwareChunker(
            max_chars=request.max_chars,
            overlap_sentences=request.overlap_sentences
        )
        
        # Convert ExtractedText objects to dictionaries
        pages_data = [
            {
                'url': page.url,
                'title': page.title,
                'cleaned_text': page.cleaned_text
            }
            for page in extracted_pages
        ]
        
        chunks = chunker.process_extracted_pages(pages_data)
        logger.info(f"[CHUNK] Completed: {len(chunks)} chunks created")
        details['chunk_summary'] = {
            'total_chunks': len(chunks),
            'average_chunk_size': int(sum(len(c.text) for c in chunks) / len(chunks)) if chunks else 0
        }
        
        # Step 4: Store embeddings to Chroma collection
        logger.info(f"[EMBED] Starting embedding storage to collection '{request.collection_name}'")
        
        # Convert TextChunk objects to dictionaries for embedding storage
        chunk_dicts = [
            {
                'chunk_id': chunk.chunk_id,
                'url': chunk.url,
                'title': chunk.title,
                'text': chunk.text
            }
            for chunk in chunks
        ]
        
        embed_result = add_embeddings(chunk_dicts, request.collection_name)
        
        if embed_result['status'] != 'success':
            logger.error(f"[EMBED] Failed: {embed_result['message']}")
            raise HTTPException(status_code=500, detail=f"Embedding storage failed: {embed_result['message']}")
        
        embeddings_added = embed_result.get('count', 0)
        logger.info(f"[EMBED] Completed: {embeddings_added} embeddings stored")
        details['embedding_summary'] = {
            'embeddings_added': embeddings_added,
            'collection': request.collection_name
        }
        
        # Final summary
        logger.info(f"[INGEST] Pipeline completed successfully. Total embeddings added: {embeddings_added}")
        
        return IngestResponse(
            status="success",
            message=f"Successfully ingested website and stored {embeddings_added} embeddings",
            crawled_pages=len(pages),
            extracted_pages=len(extracted_pages),
            total_chunks=len(chunks),
            embeddings_added=embeddings_added,
            collection_name=request.collection_name,
            details=details
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[INGEST] Pipeline failed with error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ingestion pipeline error: {str(e)}")


@app.get(f"{base_url}/ingest", response_model=IngestResponse)
async def ingest_website_get(
    base_url: str = Query(..., description="The starting URL to crawl"),
    max_depth: int = Query(2, description="Maximum depth of links to follow"),
    max_pages: int = Query(50, description="Maximum number of pages to crawl"),
    max_chars: int = Query(1800, description="Maximum characters per chunk"),
    overlap_sentences: int = Query(2, description="Number of sentences to overlap between chunks"),
    collection_name: str = Query("rag_bot", description="Chroma collection name")
):
    """
    Complete ingestion pipeline using GET request parameters.
    
    - **base_url**: The starting URL to crawl
    - **max_depth**: Maximum depth of links to follow (default: 2)
    - **max_pages**: Maximum number of pages to crawl (default: 50)
    - **max_chars**: Maximum characters per chunk (default: 1800)
    - **overlap_sentences**: Number of sentences to overlap between chunks (default: 2)
    - **collection_name**: Chroma collection name (default: "rag_bot")
    """
    request = IngestRequest(
        base_url=base_url,
        max_depth=max_depth,
        max_pages=max_pages,
        max_chars=max_chars,
        overlap_sentences=overlap_sentences,
        collection_name=collection_name
    )
    return await ingest_website(request)



@app.post(f"{base_url}/retrieve", response_model=RetrieveResponse)
async def retrieve_query(request: RetrieveRequest):
    """
    Query the ingested embeddings and return relevant results.
    
    - **query**: The question or search query
    - **n_results**: Number of results to return (default: 5, max: 20)
    - **collection_name**: Chroma collection name (default: "rag_bot")
    
    Returns the most relevant chunks from the ingested documents.
    """
    
    logger.info(f"[RETRIEVE] Query received: {request.query}")
    
    # Validate query
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    # Validate n_results
    if request.n_results < 1 or request.n_results > 20:
        raise HTTPException(status_code=400, detail="n_results must be between 1 and 20")
    
    try:
        logger.info(f"[RETRIEVE] Querying collection '{request.collection_name}' with n_results={request.n_results}")
        
        # Query embeddings
        results = query_embeddings(
            query_text=request.query,
            n_results=request.n_results,
            collection_name=request.collection_name
        )
        
        if not results or not results.get('documents'):
            logger.warning(f"[RETRIEVE] No results found for query: {request.query}")
            return RetrieveResponse(
                status="success",
                query=request.query,
                collection_name=request.collection_name,
                total_results=0,
                results=[]
            )
        
        # Parse results
        documents = results.get('documents', [[]])[0]
        metadatas = results.get('metadatas', [[]])[0]
        distances = results.get('distances', [[]])[0] if results.get('distances') else [None] * len(documents)
        
        retrieve_results = []
        for rank, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances), 1):
            retrieve_results.append(
                RetrieveResult(
                    rank=rank,
                    text=doc,
                    url=metadata.get('url', ''),
                    title=metadata.get('title'),
                    distance=distance
                )
            )
        
        logger.info(f"[RETRIEVE] Found {len(retrieve_results)} results for query")
        
        return RetrieveResponse(
            status="success",
            query=request.query,
            collection_name=request.collection_name,
            total_results=len(retrieve_results),
            results=retrieve_results
        )
    
    except Exception as e:
        logger.error(f"[RETRIEVE] Query failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Query error: {str(e)}")


@app.get(f"{base_url}/retrieve", response_model=RetrieveResponse)
async def retrieve_query_get(
    query: str = Query(..., description="The question or search query"),
    n_results: int = Query(5, description="Number of results to return"),
    collection_name: str = Query("rag_bot", description="Chroma collection name")
):
    """
    Query the ingested embeddings using GET request parameters.
    
    - **query**: The question or search query
    - **n_results**: Number of results to return (default: 5, max: 20)
    - **collection_name**: Chroma collection name (default: "rag_bot")
    """
    request = RetrieveRequest(
        query=query,
        n_results=n_results,
        collection_name=collection_name
    )
    return await retrieve_query(request)


@app.post(f"{base_url}/ask", response_model=AskResponse)
async def ask_endpoint(request: AskRequest):
    """
    Ask a question and get an answer based on ingested documents.
    
    - **query**: The question to ask
    - **n_results**: Number of context chunks to retrieve (default: 5, max: 20)
    - **collection_name**: Chroma collection name (default: "rag_bot")
    
    Returns the AI-generated answer based on the most relevant context from the ingested documents.
    If no relevant context is found, returns "No relevant context found".
    """
    
    logger.info(f"[ASK] Question received: {request.query}")
    
    # Validate query
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    # Validate n_results
    if request.n_results < 1 or request.n_results > 20:
        raise HTTPException(status_code=400, detail="n_results must be between 1 and 20")
    
    try:
        # Step 1: Query embeddings from ChromaDB
        logger.info(f"[ASK] Retrieving context with n_results={request.n_results}")
        context_results = query_embeddings(
            query_text=request.query,
            n_results=request.n_results,
            collection_name=request.collection_name
        )
        
        # Step 2: Ask question using OpenAI with context
        logger.info("[ASK] Generating answer using OpenAI")
        answer_response = ask_question(
            query=request.query,
            context_results=context_results,
            collection_name=request.collection_name
        )
        
        # Convert context_used to ContextUsed objects
        context_used = [
            ContextUsed(
                text=ctx['text'],
                url=ctx['url'],
                title=ctx.get('title'),
                distance=ctx.get('distance')
            )
            for ctx in answer_response.get('context_used', [])
        ]
        
        logger.info(f"[ASK] Answer generated successfully with {len(context_used)} context chunks")
        
        return AskResponse(
            status=answer_response['status'],
            query=request.query,
            answer=answer_response['answer'],
            context_used=context_used,
            total_context_chunks=answer_response.get('total_context_chunks'),
            collection_name=request.collection_name,
            error=answer_response.get('error')
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ASK] Error processing question: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")


@app.get(f"{base_url}/ask", response_model=AskResponse)
async def ask_endpoint_get(
    query: str = Query(..., description="The question to ask"),
    n_results: int = Query(5, description="Number of context chunks to retrieve"),
    collection_name: str = Query("rag_bot", description="Chroma collection name")
):
    """
    Ask a question using GET request parameters.
    
    - **query**: The question to ask
    - **n_results**: Number of context chunks to retrieve (default: 5, max: 20)
    - **collection_name**: Chroma collection name (default: "rag_bot")
    """
    request = AskRequest(
        query=query,
        n_results=n_results,
        collection_name=collection_name
    )
    return await ask_endpoint(request)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
