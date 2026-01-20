from openai import OpenAI
import os
from dotenv import load_dotenv
import logging
from typing import Dict, List, Optional

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def ask_question(
    query: str,
    context_results: List[Dict],
    collection_name: str = "rag_bot"
) -> Dict:
    """
    Ask a question using retrieved context from ChromaDB.
    
    Args:
        query: The user's question
        context_results: The results from query_embeddings (from embeddings module)
        collection_name: Name of the collection (for logging)
        
    Returns:
        Dictionary with answer, context used, and metadata
    """
    try:
        # Check if we have context results
        if not context_results or not context_results.get('documents') or not context_results['documents'][0]:
            logger.warning(f"No context found for query: {query}")
            return {
                "status": "no_context",
                "query": query,
                "answer": "No relevant context found. Unable to answer the question.",
                "context_used": [],
                "collection_name": collection_name
            }
        
        # Extract documents and metadata from results
        documents = context_results['documents'][0]  # First (and only) query's results
        metadatas = context_results.get('metadatas', [[]])[0]  # Metadata for first query
        distances = context_results.get('distances', [[]])[0] if 'distances' in context_results else None
        
        # Build context string from retrieved documents
        context_text = "\n\n".join([f"Source: {meta.get('url', 'Unknown')}\nTitle: {meta.get('title', 'Unknown')}\n\nContent:\n{doc}" 
                                    for doc, meta in zip(documents, metadatas)])
        
        logger.info(f"Retrieved {len(documents)} relevant context chunks for query")
        
        # Create the prompt for OpenAI
        system_prompt = """You are a helpful assistant that answers questions based on provided context. 
Use only the information from the context to answer questions. 
If the context doesn't contain relevant information, say so clearly."""
        
        user_prompt = f"""Based on the following context, please answer this question: {query}

Context:
{context_text}

Please provide a clear and concise answer based on the context provided."""
        
        # Call OpenAI API
        logger.info("Calling OpenAI API for answer generation")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        answer = response.choices[0].message.content
        
        logger.info("Successfully generated answer from OpenAI")
        
        return {
            "status": "success",
            "query": query,
            "answer": answer,
            "context_used": [
                {
                    "text": doc[:200] + "..." if len(doc) > 200 else doc,
                    "url": meta.get('url', 'Unknown'),
                    "title": meta.get('title', 'Unknown'),
                    "distance": float(distances[i]) if distances else None
                }
                for i, (doc, meta) in enumerate(zip(documents, metadatas))
            ],
            "collection_name": collection_name,
            "total_context_chunks": len(documents)
        }
    
    except Exception as e:
        logger.error(f"Error in ask_question: {str(e)}")
        return {
            "status": "error",
            "query": query,
            "answer": f"Error processing question: {str(e)}",
            "context_used": [],
            "collection_name": collection_name,
            "error": str(e)
        }
