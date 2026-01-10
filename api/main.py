from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
from dotenv import load_dotenv

# Import the crawler and text extractor
from crawling.crawler import WebCrawler
from text_extraction.text_extract import TextExtractor, ExtractedText

# Load environment variables
load_dotenv()

app = FastAPI(title="QA RAG Bot API", version="1.0.0")

# Request/Response models
class CrawlRequest(BaseModel):
    base_url: str
    max_depth: Optional[int] = 2
    max_pages: Optional[int] = 50


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


@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "message": "QA RAG Bot API",
        "version": "1.0.0",
        "endpoints": {
            "crawl": "/crawl",
            "extract": "/extract"
        }
    }


@app.post("/crawl", response_model=CrawlResponse)
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


@app.get("/crawl", response_model=CrawlResponse)
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


@app.post("/extract", response_model=ExtractResponse)
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


@app.get("/extract", response_model=ExtractResponse)
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
