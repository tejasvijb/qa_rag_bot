# Ask API Reference

## Overview

The `/ask` endpoint is a powerful question-answering endpoint that combines:

1. **Semantic Search** - Retrieves relevant context from ChromaDB using embeddings
2. **OpenAI Integration** - Generates intelligent answers based on retrieved context
3. **Source Attribution** - Returns the documents used to generate the answer

Unlike the `/retrieve` endpoint which returns raw search results, the `/ask` endpoint generates answers using OpenAI's language model.

## Endpoints

### POST /ask

**Query the knowledge base with JSON body**

#### Request

```json
{
    "query": "How do I install the software?",
    "n_results": 5,
    "collection_name": "rag_bot"
}
```

#### Parameters

-   `query` (required): Your question or search query
-   `n_results` (optional, default: 5): Number of results to return (1-20)
-   `collection_name` (optional, default: "rag_bot"): Which collection to search

#### Response (Success)

```json
{
    "status": "success",
    "query": "How do I install the software?",
    "collection_name": "rag_bot",
    "total_results": 3,
    "results": [
        {
            "rank": 1,
            "text": "To install the software, download the installer from our website and run it. Follow the on-screen instructions...",
            "url": "https://example.com/installation",
            "title": "Installation Guide",
            "distance": 0.45
        },
        {
            "rank": 2,
            "text": "System requirements: Windows 10 or later, 4GB RAM minimum. The installation process typically takes 5-10 minutes...",
            "url": "https://example.com/system-requirements",
            "title": "System Requirements",
            "distance": 0.62
        },
        {
            "rank": 3,
            "text": "If you encounter any issues during installation, please check our troubleshooting guide...",
            "url": "https://example.com/troubleshooting",
            "title": "Troubleshooting",
            "distance": 0.75
        }
    ]
}
```

#### Response (No Results)

```json
{
    "status": "success",
    "query": "some obscure query",
    "collection_name": "rag_bot",
    "total_results": 0,
    "results": []
}
```

### GET /ask

**Query the knowledge base with query parameters**

```
GET /ask?query=How+do+I+install+the+software&n_results=5&collection_name=rag_bot
```

Same parameters and responses as POST request.

## Usage Examples

### Using cURL (POST)

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I install the software?",
    "n_results": 5,
    "collection_name": "rag_bot"
  }'
```

### Using cURL (GET)

```bash
curl -X GET "http://localhost:8000/ask?query=How+do+I+install+the+software&n_results=5"
```

### Using Python (requests)

```python
import requests

response = requests.post(
    "http://localhost:8000/ask",
    json={
        "query": "How do I install the software?",
        "n_results": 5,
        "collection_name": "rag_bot"
    }
)

results = response.json()
print(f"Found {results['total_results']} results:")
for result in results['results']:
    print(f"\n[{result['rank']}] {result['title']} ({result['url']})")
    print(f"    {result['text'][:100]}...")
    print(f"    Relevance: {result['distance']}")
```

### Using Python (with FastAPI TestClient)

```python
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

response = client.post(
    "/ask",
    json={
        "query": "How do I troubleshoot installation errors?",
        "n_results": 3
    }
)

print(response.json())
```

### Using JavaScript (fetch)

```javascript
const response = await fetch("http://localhost:8000/ask", {
    method: "POST",
    headers: {
        "Content-Type": "application/json",
    },
    body: JSON.stringify({
        query: "How do I install the software?",
        n_results: 5,
        collection_name: "rag_bot",
    }),
});

const data = await response.json();
console.log(`Found ${data.total_results} results:`);
data.results.forEach((result) => {
    console.log(`\n[${result.rank}] ${result.title}`);
    console.log(`URL: ${result.url}`);
    console.log(`Text: ${result.text.substring(0, 100)}...`);
});
```

## Response Fields

### AskResult Object

-   **rank**: Position in results (1 = most relevant)
-   **text**: The actual chunk content (snippet from the document)
-   **url**: Source URL where this content came from
-   **title**: Page title or heading
-   **distance**: Semantic distance score (lower = more relevant, 0 = perfect match)

### AskResponse Object

-   **status**: Always "success" on successful queries
-   **query**: The original query string
-   **collection_name**: Which collection was searched
-   **total_results**: Number of results returned
-   **results**: List of AskResult objects

## Logging

Queries are logged with the `[ASK]` prefix:

```
2026-01-14 10:45:23,456 - api.main - INFO - [ASK] Query received: How do I install the software?
2026-01-14 10:45:23,567 - api.main - INFO - [ASK] Querying collection 'rag_bot' with n_results=5
2026-01-14 10:45:24,123 - embeddings.embeddings - INFO - Query returned 3 results
2026-01-14 10:45:24,234 - api.main - INFO - [ASK] Found 3 results for query
```

## Error Handling

### Empty Query (400)

```json
{
    "detail": "Query cannot be empty"
}
```

### Invalid n_results (400)

```json
{
    "detail": "n_results must be between 1 and 20"
}
```

### Collection Not Found (500)

```json
{
    "detail": "Query error: [error details]"
}
```

## Tips & Best Practices

1. **Better Questions = Better Results**: More specific, detailed queries generally return more relevant results

    - ❌ Bad: "help"
    - ✅ Good: "How do I troubleshoot connection errors?"

2. **Use Natural Language**: Ask questions naturally, not in keywords

    - ❌ Bad: "install steps procedure"
    - ✅ Good: "What are the steps to install?"

3. **Adjust n_results**:

    - Use 1-3 for specific answers
    - Use 5-10 for comprehensive overviews
    - Use 15-20 for research or analysis

4. **Source Verification**: Always check the `url` to verify information came from an authorized source

5. **Multiple Queries**: Ask follow-up questions to refine results
    - First: "What is the system requirements?"
    - Follow-up: "Does it work on Windows?"

## Complete Workflow Example

```python
import requests

BASE_URL = "http://localhost:8000"

# Step 1: Ingest a website
ingest_response = requests.post(
    f"{BASE_URL}/ingest",
    json={
        "base_url": "https://docs.example.com",
        "max_depth": 2,
        "max_pages": 50
    }
)
print(f"Ingested: {ingest_response.json()['embeddings_added']} embeddings")

# Step 2: Ask questions
questions = [
    "How do I get started?",
    "What are the system requirements?",
    "How do I troubleshoot errors?",
    "How do I update the software?"
]

for question in questions:
    response = requests.post(
        f"{BASE_URL}/ask",
        json={
            "query": question,
            "n_results": 3
        }
    )

    data = response.json()
    print(f"\n{'='*60}")
    print(f"Q: {question}")
    print(f"{'='*60}")

    for result in data['results']:
        print(f"\n[{result['rank']}] {result['title']}")
        print(f"    Source: {result['url']}")
        print(f"    {result['text'][:150]}...")
```

## Performance Notes

-   **Query Speed**: Typically <500ms per query
-   **Supported Query Length**: Any length (short phrases to full paragraphs)
-   **Collection Size**: Supports 1000s to 10000s of chunks efficiently
-   **Concurrent Queries**: API handles multiple concurrent requests
