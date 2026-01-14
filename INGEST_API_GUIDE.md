# Ingest API Guide

## Overview

The `/ingest` endpoint provides a complete one-stop solution for ingesting website data into your RAG system. It performs the entire pipeline in sequence:

1. **Crawl** - Crawls the website starting from a base URL
2. **Extract** - Extracts clean text from all crawled pages
3. **Chunk** - Splits text into sentence-aware chunks with overlap
4. **Embed** - Stores embeddings in a Chroma vector database collection

All operations include detailed logging for progress tracking.

## Endpoints

### POST /ingest

**Complete ingestion pipeline with JSON body**

#### Request Body

```json
{
    "base_url": "https://example.com",
    "max_depth": 2,
    "max_pages": 50,
    "max_chars": 1800,
    "overlap_sentences": 2,
    "collection_name": "rag_bot"
}
```

#### Parameters

-   `base_url` (required): The starting URL to crawl
-   `max_depth` (optional, default: 2): Maximum depth of links to follow (1-10)
-   `max_pages` (optional, default: 50): Maximum number of pages to crawl (1-500)
-   `max_chars` (optional, default: 1800): Maximum characters per chunk (100-10000)
-   `overlap_sentences` (optional, default: 2): Number of sentences to overlap between chunks (0-10)
-   `collection_name` (optional, default: "rag_bot"): Chroma collection name for storage

#### Response

```json
{
    "status": "success",
    "message": "Successfully ingested website and stored 42 embeddings",
    "crawled_pages": 15,
    "extracted_pages": 15,
    "total_chunks": 42,
    "embeddings_added": 42,
    "collection_name": "rag_bot",
    "details": {
        "crawl_summary": {
            "total_pages": 15,
            "successful_pages": 15,
            "failed_pages": 0
        },
        "extraction_summary": {
            "total_extracted": 15
        },
        "chunk_summary": {
            "total_chunks": 42,
            "average_chunk_size": 1750
        },
        "embedding_summary": {
            "embeddings_added": 42,
            "collection": "rag_bot"
        }
    }
}
```

### GET /ingest

**Complete ingestion pipeline with query parameters**

#### Query Parameters

```
GET /ingest?base_url=https://example.com&max_depth=2&max_pages=50&max_chars=1800&overlap_sentences=2&collection_name=rag_bot
```

Same parameters as POST request, passed as query parameters.

## Usage Examples

### Using cURL (POST)

```bash
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "base_url": "https://example.com",
    "max_depth": 2,
    "max_pages": 50,
    "max_chars": 1800,
    "overlap_sentences": 2,
    "collection_name": "rag_bot"
  }'
```

### Using cURL (GET)

```bash
curl -X GET "http://localhost:8000/ingest?base_url=https://example.com&max_depth=2&max_pages=50"
```

### Using Python (requests library)

```python
import requests

url = "http://localhost:8000/ingest"
payload = {
    "base_url": "https://example.com",
    "max_depth": 2,
    "max_pages": 50,
    "max_chars": 1800,
    "overlap_sentences": 2,
    "collection_name": "rag_bot"
}

response = requests.post(url, json=payload)
print(response.json())
```

### Using FastAPI TestClient

```python
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

response = client.post(
    "/ingest",
    json={
        "base_url": "https://example.com",
        "max_depth": 2,
        "max_pages": 50
    }
)
print(response.json())
```

## Logging Output

The ingest pipeline provides detailed logging at each stage. When running the API, you'll see logs like:

```
2026-01-14 10:30:45,123 - api.main - INFO - Starting ingest pipeline for URL: https://example.com
2026-01-14 10:30:45,456 - api.main - INFO - [CRAWL] Starting crawl with max_depth=2, max_pages=50
2026-01-14 10:30:52,789 - api.main - INFO - [CRAWL] Completed: 15 successful, 0 failed pages
2026-01-14 10:30:52,890 - api.main - INFO - [EXTRACT] Starting text extraction from 15 pages
2026-01-14 10:30:55,123 - api.main - INFO - [EXTRACT] Completed: 15 pages extracted
2026-01-14 10:30:55,234 - api.main - INFO - [CHUNK] Starting chunking with max_chars=1800, overlap_sentences=2
2026-01-14 10:30:56,456 - api.main - INFO - [CHUNK] Completed: 42 chunks created
2026-01-14 10:30:56,567 - api.main - INFO - [EMBED] Starting embedding storage to collection 'rag_bot'
2026-01-14 10:30:57,789 - embeddings.embeddings - INFO - Retrieved existing collection: rag_bot
2026-01-14 10:30:57,890 - embeddings.embeddings - INFO - Successfully added 42 embeddings to collection 'rag_bot'
2026-01-14 10:30:57,901 - api.main - INFO - [EMBED] Completed: 42 embeddings stored
2026-01-14 10:30:57,912 - api.main - INFO - [INGEST] Pipeline completed successfully. Total embeddings added: 42
```

## Error Handling

The endpoint validates all inputs and returns appropriate HTTP status codes:

-   **400 Bad Request**: Invalid parameters or malformed input
    -   Invalid base URL format
    -   Parameters out of range
-   **500 Internal Server Error**: Processing error during pipeline
    -   Crawling failures
    -   Text extraction errors
    -   Chunking failures
    -   Embedding storage errors

Error responses include detailed messages:

```json
{
    "detail": "URL must start with http:// or https://"
}
```

## Storage Format in Chroma

Each chunk is stored in Chroma with the following structure:

```python
{
    "id": "chunk_abc12345",  # Unique chunk identifier
    "document": "The actual text content of the chunk...",
    "metadata": {
        "url": "https://example.com/page",
        "title": "Page Title"
    }
}
```

This format allows for:

-   **Full-text search** on chunk content
-   **Metadata filtering** by URL or title
-   **Source tracking** back to original pages

## Collection Management

### Creating Multiple Collections

You can ingest different websites into different collections by specifying different `collection_name` values:

```json
{
    "base_url": "https://docs.example.com",
    "collection_name": "docs_collection"
}
```

### Querying Embeddings

After ingestion, query your embeddings using the `query_embeddings` function from the embeddings module:

```python
from embeddings.embeddings import query_embeddings

results = query_embeddings(
    query_text="How do I install the software?",
    n_results=5,
    collection_name="rag_bot"
)
```

## Performance Considerations

-   **Crawling time** depends on website size and network speed
-   **Extraction/chunking** is fast (typically < 1s per page)
-   **Embedding storage** is near-instant for typical document sizes
-   Total time for 50 pages: typically 1-5 minutes depending on website

## Tips

1. **Start small**: Test with `max_pages=5` to verify the process works
2. **Monitor logs**: Check console output for detailed progress information
3. **Adjust chunk size**: Larger `max_chars` values create fewer, larger chunks
4. **Use overlap**: Non-zero `overlap_sentences` helps maintain context between chunks
5. **Separate collections**: Use different collection names for different knowledge bases
