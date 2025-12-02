"""
Document model for uploaded files
"""

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.session import Base


class Document(Base):
    """Document model"""
    
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String)  # pdf, docx, txt, etc.
    file_size = Column(Integer)  # in bytes
    
    title = Column(String)
    description = Column(Text)
    
    # Vector store metadata
    vector_store_id = Column(String)  # ID in vector database
    chunk_count = Column(Integer, default=0)
    
    # Processing status
    status = Column(String, default="pending")  # pending, processing, completed, failed
    error_message = Column(Text)
    
    # Metadata
    metadata = Column(JSON)  # Additional metadata
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="documents")
    
    def __repr__(self):
        return f"<Document {self.filename}>"
