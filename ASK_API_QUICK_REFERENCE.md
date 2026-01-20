# ASK API - Quick Reference

## Overview

The ASK API combines ChromaDB vector search with OpenAI to answer questions about your ingested documents.

## Quick Start

### 1. Setup

```bash
# Your .env needs:
OPENAI_API_KEY=sk-your-key-here

# Make sure API is running:
python -m uvicorn api.main:app --reload
```

### 2. Ingest Documents

```bash
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "base_url": "https://docs.example.com",
    "max_pages": 50
  }'
```

### 3. Ask Questions

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the main purpose?",
    "n_results": 5,
    "collection_name": "rag_bot"
  }'
```

## Request Parameters

| Parameter       | Type   | Default   | Min-Max | Required |
| --------------- | ------ | --------- | ------- | -------- |
| query           | string | -         | -       | ✓ Yes    |
| n_results       | int    | 5         | 1-20    | No       |
| collection_name | string | "rag_bot" | -       | No       |

## Response Fields

```json
{
    "status": "success|no_context|error",
    "query": "user's question",
    "answer": "AI-generated answer",
    "context_used": [
        {
            "text": "chunk text",
            "url": "source url",
            "title": "page title",
            "distance": 0.25
        }
    ],
    "total_context_chunks": 1,
    "collection_name": "rag_bot",
    "error": null
}
```

## Status Values

-   **success** - Answer generated with context found
-   **no_context** - No relevant documents found
-   **error** - An error occurred during processing

## Usage Examples

### Python (requests)

```python
import requests

response = requests.post(
    "http://localhost:8000/ask",
    json={
        "query": "How do I install?",
        "n_results": 5,
        "collection_name": "rag_bot"
    }
)

result = response.json()
print(f"Answer: {result['answer']}")
for ctx in result['context_used']:
    print(f"Source: {ctx['url']}")
```

### Python (FastAPI TestClient)

```python
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

response = client.post(
    "/ask",
    json={"query": "What is this?"}
)

print(response.json())
```

### JavaScript (fetch)

```javascript
const response = await fetch("http://localhost:8000/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
        query: "How do I use this?",
        n_results: 5,
    }),
});

const data = await response.json();
console.log(data.answer);
```

### cURL (POST)

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "your question"}'
```

### cURL (GET)

```bash
curl "http://localhost:8000/ask?query=your%20question&n_results=5"
```

## Common Scenarios

### Scenario 1: Good Answer Found

```json
{
  "status": "success",
  "answer": "Based on the documentation, you can...",
  "context_used": [{...}],
  "total_context_chunks": 2
}
```

### Scenario 2: No Context Found

```json
{
    "status": "no_context",
    "answer": "No relevant context found. Unable to answer the question.",
    "context_used": [],
    "total_context_chunks": 0
}
```

### Scenario 3: Empty Query

```
HTTP/1.1 400 Bad Request
{"detail": "Query cannot be empty"}
```

### Scenario 4: Invalid n_results

```
HTTP/1.1 400 Bad Request
{"detail": "n_results must be between 1 and 20"}
```

## Tips & Tricks

✅ **Do's**

-   Ask specific questions: "How do I install on Windows?"
-   Use natural language
-   Adjust n_results (3 for quick, 10 for thorough)
-   Check the source URLs
-   Ask follow-up questions

❌ **Don'ts**

-   Don't use vague questions: "help"
-   Don't expect answers without ingested docs
-   Don't use n_results > 20 (costs money)
-   Don't ignore "no context" responses

## Endpoints

| Method | Path | Purpose                     |
| ------ | ---- | --------------------------- |
| POST   | /ask | Ask question (JSON body)    |
| GET    | /ask | Ask question (query params) |

Both return the same response format.

## Error Handling

| HTTP Code | Meaning      | Example                          |
| --------- | ------------ | -------------------------------- |
| 200       | Success      | Answer or no_context returned    |
| 400       | Bad Request  | Empty query or invalid n_results |
| 500       | Server Error | OpenAI/ChromaDB error            |

## Performance

-   Vector search: <500ms
-   OpenAI response: 1-3 seconds
-   Total: 1-3 seconds per question

## Cost Considerations

Each question consumes OpenAI tokens:

-   Prompt: Query + context chunks
-   Response: Generated answer

**Tips to reduce cost:**

-   Use lower n_results (3-5 instead of 20)
-   Ask specific questions (less context needed)
-   Batch questions efficiently

## Files Created/Modified

-   ✓ [ask/ask.py](ask/ask.py) - Core ask_question function
-   ✓ [api/main.py](api/main.py) - /ask endpoints
-   ✓ [test_ask_api.py](test_ask_api.py) - Test examples
-   ✓ [ASK_API_REFERENCE.md](ASK_API_REFERENCE.md) - Full docs
-   ✓ [ASK_API_IMPLEMENTATION.md](ASK_API_IMPLEMENTATION.md) - Implementation details

## Next Steps

1. Verify `.env` has `OPENAI_API_KEY`
2. Start API: `python -m uvicorn api.main:app --reload`
3. Ingest docs: `POST /ingest`
4. Ask questions: `POST /ask`
5. Check logs for troubleshooting

## Troubleshooting

**"No relevant context found"**

-   Ingest more related documents
-   Try rephrasing your question
-   Check if documents were ingested

**OpenAI error**

-   Check API key in .env
-   Verify API key has credits
-   Check rate limits

**ChromaDB error**

-   Ensure collection exists (auto-created on ingest)
-   Verify correct collection_name parameter

---

**Status**: ✅ Ready to use
**Version**: 1.0.0
**Last Updated**: January 2026
