import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
import logging

logger = logging.getLogger(__name__)


class VectorStore:
    """Manages vector storage and retrieval using Chroma"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.embeddings = self._initialize_embeddings()
        self.vectorstore = self._initialize_vectorstore()
        
    def _initialize_embeddings(self):
        """Initialize embeddings model"""
        use_mock = os.getenv("USE_MOCK_LLM", "false").lower() == "true"
        
        if use_mock:
            logger.info("Using mock embeddings (development mode)")
            return MockEmbeddings()
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("No OPENAI_API_KEY found, falling back to mock embeddings")
            return MockEmbeddings()
            
        model = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
        return OpenAIEmbeddings(
            openai_api_key=api_key,
            model=model
        )
    
    def _initialize_vectorstore(self):
        """Initialize or load existing Chroma vectorstore"""
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
        
        try:
            vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
                collection_name="smart_city_docs"
            )
            logger.info(f"Initialized vector store at {self.persist_directory}")
            return vectorstore
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            raise
    
    def add_documents(
        self,
        documents: List[Document],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> List[str]:
        """
        Add documents to the vector store
        
        Args:
            documents: List of LangChain Document objects
            metadatas: Optional list of metadata dicts
            
        Returns:
            List of document IDs
        """
        try:
            if metadatas:
                for doc, meta in zip(documents, metadatas):
                    doc.metadata.update(meta)
            
            ids = self.vectorstore.add_documents(documents)
            logger.info(f"Added {len(ids)} documents to vector store")
            return ids
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            k: Number of results to return
            filter: Optional metadata filter
            
        Returns:
            List of matching documents
        """
        try:
            results = self.vectorstore.similarity_search(
                query,
                k=k,
                filter=filter
            )
            logger.info(f"Retrieved {len(results)} documents for query")
            return results
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            return []
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[tuple[Document, float]]:
        """
        Search with relevance scores
        
        Returns:
            List of (document, score) tuples
        """
        try:
            results = self.vectorstore.similarity_search_with_score(
                query,
                k=k,
                filter=filter
            )
            return results
        except Exception as e:
            logger.error(f"Error in similarity search with score: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        try:
            collection = self.vectorstore._collection
            count = collection.count()
            return {
                "total_documents": count,
                "persist_directory": self.persist_directory
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"total_documents": 0, "error": str(e)}
    
    def delete_collection(self):
        """Delete the entire collection (use with caution!)"""
        try:
            self.vectorstore._client.delete_collection("smart_city_docs")
            logger.info("Deleted collection")
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")


class MockEmbeddings:
    """Mock embeddings for development without API key"""
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Return mock embeddings for documents"""
        # Return simple hash-based embeddings
        return [[float(hash(text) % 100) / 100 for _ in range(1536)] for text in texts]
    
    def embed_query(self, text: str) -> List[float]:
        """Return mock embedding for query"""
        return [float(hash(text) % 100) / 100 for _ in range(1536)]


# Singleton instance
_vector_store_instance: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """Get or create vector store singleton"""
    global _vector_store_instance
    if _vector_store_instance is None:
        persist_dir = os.getenv("CHROMA_DB_DIR", "./chroma_db")
        _vector_store_instance = VectorStore(persist_directory=persist_dir)
    return _vector_store_instance
