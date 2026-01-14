import chromadb
from typing import List, Dict, Optional
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Chroma client
chroma_client = chromadb.Client()


def get_or_create_collection(collection_name: str = "rag_bot"):
    """
    Get or create a Chroma collection.
    
    Args:
        collection_name: Name of the collection
        
    Returns:
        Chroma collection object
    """
    try:
        # Try to get existing collection
        collection = chroma_client.get_collection(name=collection_name)
        logger.info(f"Retrieved existing collection: {collection_name}")
    except:
        # Create new collection if it doesn't exist
        collection = chroma_client.create_collection(name=collection_name)
        logger.info(f"Created new collection: {collection_name}")
    
    return collection


def add_embeddings(
    chunks: List[Dict],
    collection_name: str = "rag_bot"
) -> Dict:
    """
    Add chunks as embeddings to a Chroma collection.
    
    Args:
        chunks: List of chunk dictionaries with chunk_id, url, title, text
        collection_name: Name of the collection to store in
        
    Returns:
        Dictionary with status and count of added embeddings
    """
    if not chunks:
        logger.warning("No chunks provided to add_embeddings")
        return {"status": "error", "message": "No chunks provided", "count": 0}
    
    try:
        collection = get_or_create_collection(collection_name)
        
        # Prepare data for Chroma
        ids = []
        documents = []
        metadatas = []
        
        for chunk in chunks:
            ids.append(chunk.get('chunk_id'))
            documents.append(chunk.get('text'))
            metadatas.append({
                'url': chunk.get('url'),
                'title': chunk.get('title', 'Unknown'),
            })
        
        # Add to collection
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        
        logger.info(f"Successfully added {len(ids)} embeddings to collection '{collection_name}'")
        return {
            "status": "success",
            "message": f"Added {len(ids)} embeddings",
            "count": len(ids),
            "collection": collection_name
        }
    
    except Exception as e:
        logger.error(f"Error adding embeddings: {str(e)}")
        return {"status": "error", "message": str(e), "count": 0}


def query_embeddings(
    query_text: str,
    n_results: int = 5,
    collection_name: str = "rag_bot"
) -> List[Dict]:
    """
    Query embeddings from a Chroma collection.
    
    Args:
        query_text: The text to query
        n_results: Number of results to return
        collection_name: Name of the collection to query
        
    Returns:
        List of matching documents with metadata
    """
    try:
        collection = get_or_create_collection(collection_name)
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        
        logger.info(f"Query returned {len(results['documents'][0])} results")
        return results
    
    except Exception as e:
        logger.error(f"Error querying embeddings: {str(e)}")
        return []