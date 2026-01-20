"""
Test script for the ASK API endpoint.

This demonstrates how to use the newly created /ask endpoint that:
1. Takes a user query
2. Retrieves relevant context from ChromaDB collection
3. Sends the context to OpenAI
4. Returns the generated answer along with the context used
5. Returns "No relevant context found" if no context is available
"""

import requests
import json

# Base URL of the API
BASE_URL = "http://localhost:8000"


def test_ask_endpoint():
    """Test the POST /ask endpoint"""
    
    print("=" * 60)
    print("Testing POST /ask endpoint")
    print("=" * 60)
    
    # Sample question
    ask_request = {
        "query": "What is the main purpose of this project?",
        "n_results": 5,
        "collection_name": "rag_bot"
    }
    
    print(f"\nRequest:")
    print(json.dumps(ask_request, indent=2))
    
    try:
        response = requests.post(
            f"{BASE_URL}/ask",
            json=ask_request,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nResponse:")
            print(f"Status: {result['status']}")
            print(f"Query: {result['query']}")
            print(f"\nAnswer:")
            print(result['answer'])
            
            if result['context_used']:
                print(f"\nContext Used ({len(result['context_used'])} chunks):")
                for i, ctx in enumerate(result['context_used'], 1):
                    print(f"\n  [{i}] URL: {ctx['url']}")
                    print(f"      Title: {ctx['title']}")
                    print(f"      Distance: {ctx['distance']}")
                    print(f"      Text Preview: {ctx['text'][:100]}...")
            else:
                print("\nNo context was used - likely no relevant documents found")
                print(f"Collection: {result['collection_name']}")
        else:
            print(f"\nError: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"Error: {e}")


def test_ask_endpoint_get():
    """Test the GET /ask endpoint"""
    
    print("\n" + "=" * 60)
    print("Testing GET /ask endpoint")
    print("=" * 60)
    
    params = {
        "query": "How does the chunking work?",
        "n_results": 3,
        "collection_name": "rag_bot"
    }
    
    print(f"\nRequest Parameters:")
    print(json.dumps(params, indent=2))
    
    try:
        response = requests.get(
            f"{BASE_URL}/ask",
            params=params,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nResponse:")
            print(f"Status: {result['status']}")
            print(f"Query: {result['query']}")
            print(f"\nAnswer:")
            print(result['answer'])
            
            if result['context_used']:
                print(f"\nContext Used ({len(result['context_used'])} chunks):")
                for i, ctx in enumerate(result['context_used'], 1):
                    print(f"\n  [{i}] URL: {ctx['url']}")
                    print(f"      Text Preview: {ctx['text'][:100]}...")
            else:
                print("\nNo relevant context found")
        else:
            print(f"\nError: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"Error: {e}")


def test_no_context_scenario():
    """Test scenario where no relevant context is found"""
    
    print("\n" + "=" * 60)
    print("Testing 'No Context Found' Scenario")
    print("=" * 60)
    
    # A query that might not have relevant context
    ask_request = {
        "query": "Tell me about quantum computing",
        "n_results": 5,
        "collection_name": "rag_bot"
    }
    
    print(f"\nRequest:")
    print(json.dumps(ask_request, indent=2))
    
    try:
        response = requests.post(
            f"{BASE_URL}/ask",
            json=ask_request,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nResponse Status: {result['status']}")
            print(f"\nAnswer:")
            print(result['answer'])
            
            if result['status'] == 'no_context':
                print("\n✓ Correctly handled case with no relevant context")
        else:
            print(f"\nError: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("\nNote: Make sure the API is running and has ingested documents")
    print("Start the API with: python -m uvicorn api.main:app --reload")
    print("\nFirst ingest a website using /ingest endpoint before testing /ask\n")
    
    test_ask_endpoint()
    test_ask_endpoint_get()
    test_no_context_scenario()
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)
