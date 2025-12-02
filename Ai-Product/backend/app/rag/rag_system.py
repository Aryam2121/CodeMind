"""
RAG (Retrieval Augmented Generation) System
Handles document embeddings and retrieval
"""

import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    UnstructuredMarkdownLoader
)
import os

from app.core.config import settings

logger = logging.getLogger(__name__)


class RAGSystem:
    """RAG System for document processing and retrieval"""
    
    def __init__(self):
        """Initialize RAG system"""
        self.embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Initialize ChromaDB client
        self.chroma_client = chromadb.HttpClient(
            host=settings.CHROMA_HOST,
            port=settings.CHROMA_PORT
        )
        
        # Text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        logger.info("RAG System initialized")
    
    def get_collection(self, user_id: str, collection_type: str = "documents"):
        """Get or create a collection for a user"""
        collection_name = f"{user_id}_{collection_type}"
        
        try:
            collection = self.chroma_client.get_or_create_collection(
                name=collection_name,
                metadata={"user_id": user_id, "type": collection_type}
            )
            return collection
        except Exception as e:
            logger.error(f"Error getting collection: {str(e)}")
            raise
    
    def load_document(self, file_path: str, file_type: str) -> List[Any]:
        """Load document based on file type"""
        try:
            if file_type == "pdf":
                loader = PyPDFLoader(file_path)
            elif file_type in ["docx", "doc"]:
                loader = Docx2txtLoader(file_path)
            elif file_type == "txt":
                loader = TextLoader(file_path)
            elif file_type == "md":
                loader = UnstructuredMarkdownLoader(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} pages from {file_path}")
            return documents
        
        except Exception as e:
            logger.error(f"Error loading document: {str(e)}")
            raise
    
    def process_document(
        self,
        file_path: str,
        file_type: str,
        user_id: str,
        document_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a document: load, chunk, embed, and store in vector DB
        
        Returns:
            Dictionary with processing results
        """
        try:
            # Load document
            documents = self.load_document(file_path, file_type)
            
            # Split into chunks
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"Split document into {len(chunks)} chunks")
            
            # Add metadata to chunks
            for i, chunk in enumerate(chunks):
                chunk.metadata.update({
                    "document_id": document_id,
                    "user_id": user_id,
                    "chunk_index": i,
                    "source": file_path,
                    **(metadata or {})
                })
            
            # Get collection
            collection = self.get_collection(user_id, "documents")
            
            # Create vector store and add documents
            vector_store = Chroma(
                client=self.chroma_client,
                collection_name=collection.name,
                embedding_function=self.embeddings
            )
            
            # Add documents to vector store
            ids = [f"{document_id}_{i}" for i in range(len(chunks))]
            vector_store.add_documents(chunks, ids=ids)
            
            logger.info(f"Successfully processed document {document_id}")
            
            return {
                "success": True,
                "document_id": document_id,
                "chunk_count": len(chunks),
                "vector_store_id": collection.name
            }
        
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def search_documents(
        self,
        query: str,
        user_id: str,
        k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search documents using semantic similarity
        
        Args:
            query: Search query
            user_id: User ID
            k: Number of results to return
            filter_metadata: Optional metadata filters
        
        Returns:
            List of relevant document chunks with metadata
        """
        try:
            collection = self.get_collection(user_id, "documents")
            
            vector_store = Chroma(
                client=self.chroma_client,
                collection_name=collection.name,
                embedding_function=self.embeddings
            )
            
            # Perform similarity search
            results = vector_store.similarity_search_with_score(
                query,
                k=k,
                filter=filter_metadata
            )
            
            # Format results
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": float(score)
                })
            
            logger.info(f"Found {len(formatted_results)} results for query")
            return formatted_results
        
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return []
    
    def delete_document(self, user_id: str, document_id: str) -> bool:
        """Delete a document from vector store"""
        try:
            collection = self.get_collection(user_id, "documents")
            
            # Get all chunk IDs for this document
            results = collection.get(
                where={"document_id": document_id}
            )
            
            if results and results["ids"]:
                collection.delete(ids=results["ids"])
                logger.info(f"Deleted document {document_id}")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            return False
    
    def get_retriever(self, user_id: str, k: int = 5):
        """Get a LangChain retriever for a user's documents"""
        collection = self.get_collection(user_id, "documents")
        
        vector_store = Chroma(
            client=self.chroma_client,
            collection_name=collection.name,
            embedding_function=self.embeddings
        )
        
        return vector_store.as_retriever(search_kwargs={"k": k})


# Create singleton instance
rag_system = RAGSystem()
