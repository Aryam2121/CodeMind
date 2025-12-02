"""
Document endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
from pathlib import Path
import logging

from app.db.session import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.document import Document
from app.rag.rag_system import rag_system

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and process a document"""
    try:
        user_id = current_user["id"]
        
        # Validate file size
        content = await file.read()
        if len(content) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=413, detail="File too large")
        
        # Get file extension
        file_ext = Path(file.filename).suffix.lower()
        file_type = file_ext.lstrip('.')
        
        # Validate file type
        allowed_types = ['.pdf', '.docx', '.doc', '.txt', '.md']
        if file_ext not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type not supported. Allowed: {', '.join(allowed_types)}"
            )
        
        # Create document record
        document_id = str(uuid.uuid4())
        file_path = os.path.join(
            settings.UPLOAD_DIR,
            user_id,
            f"{document_id}{file_ext}"
        )
        
        # Create user directory if not exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Create database record
        document = Document(
            id=document_id,
            user_id=user_id,
            filename=file.filename,
            file_path=file_path,
            file_type=file_type,
            file_size=len(content),
            status="processing"
        )
        db.add(document)
        db.commit()
        
        # Process document with RAG system
        try:
            result = rag_system.process_document(
                file_path=file_path,
                file_type=file_type,
                user_id=user_id,
                document_id=document_id,
                metadata={"filename": file.filename}
            )
            
            if result["success"]:
                document.status = "completed"
                document.chunk_count = result["chunk_count"]
                document.vector_store_id = result["vector_store_id"]
            else:
                document.status = "failed"
                document.error_message = result.get("error")
            
            db.commit()
        
        except Exception as e:
            document.status = "failed"
            document.error_message = str(e)
            db.commit()
            logger.error(f"Error processing document: {str(e)}")
        
        return {
            "document_id": document.id,
            "filename": document.filename,
            "status": document.status,
            "chunk_count": document.chunk_count
        }
    
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_documents(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all user documents"""
    documents = db.query(Document).filter(
        Document.user_id == current_user["id"]
    ).order_by(Document.created_at.desc()).all()
    
    return [
        {
            "id": doc.id,
            "filename": doc.filename,
            "file_type": doc.file_type,
            "file_size": doc.file_size,
            "status": doc.status,
            "chunk_count": doc.chunk_count,
            "created_at": doc.created_at
        }
        for doc in documents
    ]


@router.get("/{document_id}")
async def get_document(
    document_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get document details"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user["id"]
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "id": document.id,
        "filename": document.filename,
        "file_type": document.file_type,
        "file_size": document.file_size,
        "status": document.status,
        "chunk_count": document.chunk_count,
        "created_at": document.created_at,
        "updated_at": document.updated_at
    }


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a document"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user["id"]
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete from vector store
    rag_system.delete_document(current_user["id"], document_id)
    
    # Delete file
    try:
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
    
    # Delete from database
    db.delete(document)
    db.commit()
    
    return {"message": "Document deleted successfully"}
