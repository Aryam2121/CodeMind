from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class DocumentMetadata(BaseModel):
    """Metadata for ingested documents"""
    source_name: str
    uploaded_by: Optional[str] = "system"
    geo: Optional[Dict[str, float]] = None  # {"lat": float, "lon": float}
    ward: Optional[str] = None
    tags: Optional[List[str]] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class IngestRequest(BaseModel):
    """Request model for document ingestion"""
    metadata: Optional[DocumentMetadata] = None


class IngestResponse(BaseModel):
    """Response model for document ingestion"""
    status: str
    ingested: int
    ids: List[str]
    metadata: Dict[str, Any] = {}


class QueryRequest(BaseModel):
    """Request model for AI queries"""
    query: str = Field(..., min_length=1, description="User's natural language query")
    top_k: int = Field(default=4, ge=1, le=10, description="Number of documents to retrieve")
    agents: Optional[List[str]] = Field(
        default=None,
        description="Specific agents to use: document, gis, summary, compliance"
    )
    filters: Optional[Dict[str, Any]] = None


class Source(BaseModel):
    """Source citation for answers"""
    id: str
    title: str
    page: Optional[int] = None
    snippet: str
    score: Optional[float] = None


class QueryResponse(BaseModel):
    """Response model for AI queries"""
    answer: str
    sources: List[Source]
    agent_used: str
    confidence: Optional[float] = None
    fallback: bool = False
    raw_llm_output: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}


class StatusResponse(BaseModel):
    """Response model for system status"""
    status: str
    stats: Dict[str, Any]
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentResponse(BaseModel):
    """Internal agent response model"""
    answer: str
    sources: List[Source]
    confidence: float
    metadata: Dict[str, Any] = {}


class Complaint(BaseModel):
    """Model for geo-tagged complaints"""
    id: str
    lat: float
    lon: float
    type: str
    ward: str
    date: datetime
    description: str
    status: Optional[str] = "open"
