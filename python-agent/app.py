import os
import sys
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv
import logging
from datetime import datetime
from typing import Optional
import json

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from models import (
    QueryRequest, QueryResponse, IngestResponse,
    StatusResponse, DocumentMetadata
)
from ingest import get_ingester
from agents import get_orchestrator
from vector_store import get_vector_store

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Smart City AI Agent",
    description="Multi-Agent RAG system for smart city management",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global stats
stats = {
    "queries_today": 0,
    "documents_ingested": 0,
    "start_time": datetime.utcnow()
}


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Smart City AI Agent service...")
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    use_mock = os.getenv("USE_MOCK_LLM", "false").lower() == "true"
    
    if not api_key and not use_mock:
        logger.warning(
            "No OPENAI_API_KEY found. Set USE_MOCK_LLM=true for development mode."
        )
    
    # Initialize components
    try:
        get_vector_store()
        get_ingester()
        get_orchestrator()
        logger.info("All services initialized successfully")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint"""
    return {
        "service": "Smart City AI Agent",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/status", response_model=StatusResponse, tags=["Health"])
async def get_status():
    """
    Get service status and statistics
    
    Returns comprehensive health check and usage statistics
    """
    try:
        vector_store = get_vector_store()
        vector_stats = vector_store.get_collection_stats()
        
        return StatusResponse(
            status="healthy",
            stats={
                "documents": vector_stats.get("total_documents", 0),
                "queries_today": stats["queries_today"],
                "documents_ingested": stats["documents_ingested"],
                "uptime_seconds": (datetime.utcnow() - stats["start_time"]).total_seconds(),
                "use_mock_llm": os.getenv("USE_MOCK_LLM", "false").lower() == "true"
            },
            version="1.0.0"
        )
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving status: {str(e)}"
        )


@app.post("/ingest", response_model=IngestResponse, tags=["Ingestion"])
async def ingest_document(
    file: UploadFile = File(...),
    metadata: Optional[str] = Form(None)
):
    """
    Ingest a document into the knowledge base
    
    - **file**: PDF, DOCX, or TXT file
    - **metadata**: Optional JSON metadata (source_name, uploaded_by, geo, ward, tags)
    
    Returns ingestion status and document IDs
    """
    try:
        # Parse metadata if provided
        doc_metadata = None
        if metadata:
            try:
                meta_dict = json.loads(metadata)
                doc_metadata = DocumentMetadata(**meta_dict)
            except Exception as e:
                logger.warning(f"Error parsing metadata: {e}")
        
        # Read file
        contents = await file.read()
        
        # Create file-like object
        from io import BytesIO
        file_obj = BytesIO(contents)
        
        # Ingest
        ingester = get_ingester()
        response = await ingester.ingest_file(
            file=file_obj,
            filename=file.filename or "unknown.txt",
            metadata=doc_metadata
        )
        
        # Update stats
        stats["documents_ingested"] += 1
        
        logger.info(f"Successfully ingested {file.filename}: {response.ingested} chunks")
        return response
        
    except Exception as e:
        logger.error(f"Error ingesting document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting document: {str(e)}"
        )


@app.post("/query", response_model=QueryResponse, tags=["Query"])
async def query_knowledge_base(request: QueryRequest):
    """
    Query the knowledge base using natural language
    
    - **query**: Natural language question
    - **top_k**: Number of documents to retrieve (1-10)
    - **agents**: Optional list of specific agents to use
    - **filters**: Optional metadata filters
    
    Returns AI-generated answer with source citations
    """
    try:
        # Route to appropriate agent
        orchestrator = get_orchestrator()
        agent_response = await orchestrator.route_query(request)
        
        # Update stats
        stats["queries_today"] += 1
        
        # Convert to QueryResponse
        response = QueryResponse(
            answer=agent_response.answer,
            sources=agent_response.sources,
            agent_used=agent_response.metadata.get("agent", "unknown"),
            confidence=agent_response.confidence,
            fallback=agent_response.metadata.get("fallback", False),
            raw_llm_output=agent_response.answer,
            metadata=agent_response.metadata
        )
        
        logger.info(f"Query processed by {response.agent_used} agent")
        return response
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )


@app.get("/health", tags=["Health"])
async def health_check():
    """Simple health check endpoint"""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal error occurred",
            "error": str(exc)
        }
    )


if __name__ == "__main__":
    port = int(os.getenv("PYTHON_AGENT_PORT", 8000))
    
    logger.info(f"Starting server on port {port}")
    logger.info(f"API documentation: http://localhost:{port}/docs")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
