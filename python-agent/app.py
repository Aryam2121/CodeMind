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
from github_loader import GitHubLoader
from conversation_manager import get_conversation_manager
from code_formatter import get_code_formatter
from llm_config import get_llm_settings, LLMConfig
from export_manager import get_export_manager

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
async def query_knowledge_base(
    request: QueryRequest,
    session_id: Optional[str] = None
):
    """
    Query the knowledge base using natural language
    
    - **query**: Natural language question
    - **top_k**: Number of documents to retrieve (1-10)
    - **agents**: Optional list of specific agents to use
    - **filters**: Optional metadata filters
    - **session_id**: Optional session ID for conversation history
    
    Returns AI-generated answer with source citations
    """
    try:
        # Save user message if session provided
        conv_manager = get_conversation_manager()
        if session_id:
            conv_manager.add_message(
                session_id=session_id,
                role="user",
                content=request.query
            )
        
        # Route to appropriate agent
        orchestrator = get_orchestrator()
        agent_response = await orchestrator.route_query(request)
        
        # Update stats
        stats["queries_today"] += 1
        
        # Format code in response
        formatter = get_code_formatter()
        formatted = formatter.format_response(agent_response.answer)
        
        # Convert to QueryResponse
        response = QueryResponse(
            answer=agent_response.answer,
            sources=agent_response.sources,
            agent_used=agent_response.metadata.get("agent", "unknown"),
            confidence=agent_response.confidence,
            fallback=agent_response.metadata.get("fallback", False),
            raw_llm_output=agent_response.answer,
            metadata={
                **agent_response.metadata,
                'code_blocks': formatted['code_blocks'],
                'has_code': formatted['has_code']
            }
        )
        
        # Save assistant message if session provided
        if session_id:
            conv_manager.add_message(
                session_id=session_id,
                role="assistant",
                content=response.answer,
                sources=response.sources,
                agent_used=response.agent_used
            )
        
        logger.info(f"Query processed by {response.agent_used} agent")
        return response
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )


@app.get("/conversations", tags=["Conversations"])
async def get_conversations(limit: int = 50):
    """Get list of all conversations"""
    try:
        conv_manager = get_conversation_manager()
        conversations = conv_manager.get_all_conversations(limit=limit)
        return {"conversations": conversations}
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/conversations/{session_id}", tags=["Conversations"])
async def get_conversation_history(session_id: str, limit: Optional[int] = None):
    """Get conversation history by session ID"""
    try:
        conv_manager = get_conversation_manager()
        
        # Get conversation metadata
        conversation = conv_manager.get_conversation(session_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Get messages
        messages = conv_manager.get_conversation_history(session_id, limit=limit)
        
        return {
            "conversation": conversation,
            "messages": messages
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.delete("/conversations/{session_id}", tags=["Conversations"])
async def delete_conversation(session_id: str):
    """Delete a conversation"""
    try:
        conv_manager = get_conversation_manager()
        conv_manager.delete_conversation(session_id)
        return {"status": "ok", "message": "Conversation deleted"}
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/conversations/{session_id}/export", tags=["Conversations"])
async def export_conversation(session_id: str, format: str = "json"):
    """
    Export conversation in various formats
    
    - **format**: json, markdown, or txt
    """
    try:
        conv_manager = get_conversation_manager()
        export_manager = get_export_manager()
        
        # Get conversation data
        conversation = conv_manager.get_conversation(session_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        messages = conv_manager.get_conversation_history(session_id)
        
        # Export in requested format
        if format == "json":
            content = export_manager.export_conversation_json(conversation, messages)
            media_type = "application/json"
            filename = f"conversation_{session_id}.json"
        elif format == "markdown":
            content = export_manager.export_conversation_markdown(conversation, messages)
            media_type = "text/markdown"
            filename = f"conversation_{session_id}.md"
        elif format == "txt":
            content = export_manager.export_conversation_txt(conversation, messages)
            media_type = "text/plain"
            filename = f"conversation_{session_id}.txt"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid format. Use: json, markdown, or txt"
            )
        
        from fastapi.responses import Response
        return Response(
            content=content,
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/conversations/{session_id}/summary", tags=["Conversations"])
async def get_conversation_summary(session_id: str):
    """Get summary statistics for a conversation"""
    try:
        conv_manager = get_conversation_manager()
        export_manager = get_export_manager()
        
        # Get conversation data
        conversation = conv_manager.get_conversation(session_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        messages = conv_manager.get_conversation_history(session_id)
        summary = export_manager.generate_summary(messages)
        
        return {
            "conversation": conversation,
            "summary": summary
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/conversations/search", tags=["Conversations"])
async def search_conversations(q: str, limit: int = 20):
    """Search conversations by content"""
    try:
        conv_manager = get_conversation_manager()
        results = conv_manager.search_conversations(q, limit=limit)
        return {"results": results}
    except Exception as e:
        logger.error(f"Error searching conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/settings", tags=["Settings"])
async def get_settings():
    """Get current LLM settings"""
    try:
        settings = get_llm_settings()
        return {
            "llm": settings.to_dict(),
            "available_models": list(LLMConfig.OPENAI_MODELS.keys()),
            "use_mock_llm": os.getenv("USE_MOCK_LLM", "false").lower() == "true"
        }
    except Exception as e:
        logger.error(f"Error getting settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/settings/llm", tags=["Settings"])
async def update_llm_settings(
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    streaming: Optional[bool] = None
):
    """Update LLM settings"""
    try:
        settings = get_llm_settings()
        settings.update(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=streaming
        )
        
        return {
            "status": "ok",
            "message": "Settings updated",
            "settings": settings.to_dict()
        }
    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/models", tags=["Settings"])
async def get_available_models():
    """Get list of available LLM models with info"""
    models = []
    for model_name, info in LLMConfig.OPENAI_MODELS.items():
        models.append({
            'name': model_name,
            'provider': 'openai',
            'context_window': info['context'],
            'cost_per_1k_tokens': info['cost_per_1k']
        })
    return {"models": models}


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
@app.post("/ingest/github", tags=["Ingestion"])
async def ingest_github_repo(
    repo_url: str = Form(...),
    branch: str = Form("main")
):
    """
    Ingest an entire GitHub repository
    
    - **repo_url**: GitHub repository URL (e.g., https://github.com/user/repo)
    - **branch**: Branch name (default: main)
    
    Returns ingestion statistics
    """
    try:
        loader = GitHubLoader()
        
        # Load documents from repository
        documents = loader.load_from_url(repo_url, branch)
        
        if not documents:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "No supported files found in repository"}
            )
        
        # Get file statistics
        file_stats = loader.get_file_stats(documents)
        
        # Ingest into vector store
        ingester = get_ingester()
        result = await ingester.ingest_documents(documents)
        
        stats["documents_ingested"] += len(documents)
        
        return {
            "status": "ok",
            "repo_url": repo_url,
            "branch": branch,
            "files_processed": len(documents),
            "chunks_created": result["chunk_count"],
            "file_stats": file_stats,
            "ingested": len(result["ids"])
        }
        
    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail="Repository clone timeout. Repository may be too large."
        )
    except Exception as e:
        logger.error(f"Error ingesting GitHub repo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting repository: {str(e)}"
        )


@app.post("/ingest/local", tags=["Ingestion"])
async def ingest_local_directory(
    directory_path: str = Form(...)
):
    """
    Ingest files from a local directory
    
    - **directory_path**: Absolute path to local directory
    
    Returns ingestion statistics
    """
    try:
        loader = GitHubLoader()
        
        # Load documents from local directory
        documents = loader.load_from_local(directory_path)
        
        if not documents:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "No supported files found in directory"}
            )
        
        # Get file statistics
        file_stats = loader.get_file_stats(documents)
        
        # Ingest into vector store
        ingester = get_ingester()
        result = await ingester.ingest_documents(documents)
        
        stats["documents_ingested"] += len(documents)
        
        return {
            "status": "ok",
            "directory": directory_path,
            "files_processed": len(documents),
            "chunks_created": result["chunk_count"],
            "file_stats": file_stats,
            "ingested": len(result["ids"])
        }
        
    except Exception as e:
        logger.error(f"Error ingesting local directory: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting directory: {str(e)}"
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
