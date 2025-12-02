import os
from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod
import logging
import pandas as pd
from pathlib import Path

from models import QueryRequest, AgentResponse, Source
from rag import get_rag_pipeline

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all agents"""
    
    @abstractmethod
    def can_handle(self, query: str) -> bool:
        """Determine if this agent can handle the query"""
        pass
    
    @abstractmethod
    async def process(self, query: str, context: Dict[str, Any]) -> AgentResponse:
        """Process the query and return response"""
        pass


class DocumentAgent(BaseAgent):
    """Agent for document-based queries using RAG"""
    
    def __init__(self):
        self.rag_pipeline = get_rag_pipeline()
        self.keywords = [
            "document", "policy", "circular", "guideline", "procedure",
            "sop", "standard", "regulation", "rule", "manual"
        ]
    
    def can_handle(self, query: str) -> bool:
        """Check if query is about documents"""
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.keywords)
    
    async def process(self, query: str, context: Dict[str, Any]) -> AgentResponse:
        """Process document query using RAG"""
        top_k = context.get("top_k", 4)
        filter = context.get("filter")
        
        response = await self.rag_pipeline.query(query, top_k=top_k, filter=filter)
        
        return AgentResponse(
            answer=response.answer,
            sources=response.sources,
            confidence=response.confidence or 0.0,
            metadata={"agent": "document", "fallback": response.fallback}
        )


class GISAgent(BaseAgent):
    """Agent for geo-spatial queries about complaints and locations"""
    
    def __init__(self):
        self.keywords = [
            "ward", "location", "area", "map", "latitude", "longitude",
            "nearby", "pothole", "complaint", "where", "geographical"
        ]
        self.complaints_data = self._load_complaints()
    
    def _load_complaints(self) -> Optional[pd.DataFrame]:
        """Load complaints data from CSV"""
        try:
            data_path = Path("../test-data/complaints.csv")
            if data_path.exists():
                df = pd.read_csv(data_path)
                df['date'] = pd.to_datetime(df['date'])
                logger.info(f"Loaded {len(df)} complaints")
                return df
            else:
                logger.warning("Complaints CSV not found")
                return None
        except Exception as e:
            logger.error(f"Error loading complaints: {e}")
            return None
    
    def can_handle(self, query: str) -> bool:
        """Check if query is geo-spatial"""
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.keywords)
    
    async def process(self, query: str, context: Dict[str, Any]) -> AgentResponse:
        """Process geo-spatial query"""
        if self.complaints_data is None:
            return AgentResponse(
                answer="Geo-spatial data is not currently available. Please ensure complaints data is loaded.",
                sources=[],
                confidence=0.0,
                metadata={"agent": "gis", "error": "No data"}
            )
        
        # Extract ward if mentioned
        ward = self._extract_ward(query)
        
        # Filter data
        filtered = self.complaints_data
        if ward:
            filtered = filtered[filtered['ward'] == ward]
        
        # Extract date range if mentioned
        days = self._extract_days(query)
        if days:
            cutoff_date = pd.Timestamp.now() - pd.Timedelta(days=days)
            filtered = filtered[filtered['date'] >= cutoff_date]
        
        # Generate summary
        answer = self._generate_summary(filtered, ward, days)
        
        return AgentResponse(
            answer=answer,
            sources=[Source(
                id="complaints_db",
                title="Complaints Database",
                snippet=f"Analyzed {len(filtered)} complaint records",
                score=1.0
            )],
            confidence=0.95,
            metadata={
                "agent": "gis",
                "total_complaints": len(filtered),
                "ward": ward,
                "days": days
            }
        )
    
    def _extract_ward(self, query: str) -> Optional[str]:
        """Extract ward number from query"""
        import re
        match = re.search(r'ward\s*(\d+)', query.lower())
        if match:
            return f"Ward {match.group(1)}"
        return None
    
    def _extract_days(self, query: str) -> Optional[int]:
        """Extract number of days from query"""
        import re
        
        # Check for "last X days"
        match = re.search(r'last\s*(\d+)\s*days?', query.lower())
        if match:
            return int(match.group(1))
        
        # Check for "past X days"
        match = re.search(r'past\s*(\d+)\s*days?', query.lower())
        if match:
            return int(match.group(1))
        
        return None
    
    def _generate_summary(
        self,
        data: pd.DataFrame,
        ward: Optional[str],
        days: Optional[int]
    ) -> str:
        """Generate summary of geo-spatial data"""
        if len(data) == 0:
            return f"No complaints found{' for ' + ward if ward else ''}{' in the last ' + str(days) + ' days' if days else ''}."
        
        # Count by type
        type_counts = data['type'].value_counts()
        
        # Build response
        parts = [f"Found {len(data)} complaints"]
        if ward:
            parts[0] += f" in {ward}"
        if days:
            parts[0] += f" in the last {days} days"
        parts[0] += ":"
        
        # Top complaint types
        parts.append("\n**Complaint Breakdown:**")
        for complaint_type, count in type_counts.head(5).items():
            parts.append(f"- {complaint_type}: {count}")
        
        # Status summary if available
        if 'status' in data.columns:
            open_count = len(data[data['status'] == 'open'])
            parts.append(f"\n**Status:** {open_count} open, {len(data) - open_count} resolved")
        
        # Recommendations
        parts.append("\n**Recommended Actions:**")
        top_type = type_counts.index[0] if len(type_counts) > 0 else "N/A"
        parts.append(f"1. Prioritize {top_type} complaints")
        parts.append(f"2. Deploy maintenance teams to high-complaint areas")
        parts.append(f"3. Review resource allocation for affected ward(s)")
        
        return "\n".join(parts)


class SummaryAgent(BaseAgent):
    """Agent for summarizing documents and generating reports"""
    
    def __init__(self):
        self.rag_pipeline = get_rag_pipeline()
        self.keywords = [
            "summarize", "summary", "overview", "brief", "extract",
            "key points", "highlights", "action items", "main points"
        ]
    
    def can_handle(self, query: str) -> bool:
        """Check if query requests summary"""
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.keywords)
    
    async def process(self, query: str, context: Dict[str, Any]) -> AgentResponse:
        """Generate summary using RAG"""
        # Use higher top_k for summaries
        top_k = context.get("top_k", 6)
        
        response = await self.rag_pipeline.query(query, top_k=top_k)
        
        # Enhance response with summary framing
        enhanced_answer = f"**Summary:**\n\n{response.answer}"
        
        return AgentResponse(
            answer=enhanced_answer,
            sources=response.sources,
            confidence=response.confidence or 0.0,
            metadata={"agent": "summary"}
        )


class ComplianceAgent(BaseAgent):
    """Agent for compliance and regulation checks"""
    
    def __init__(self):
        self.rag_pipeline = get_rag_pipeline()
        self.keywords = [
            "compliant", "compliance", "regulation", "legal", "violation",
            "breach", "requirement", "mandatory", "permitted", "allowed"
        ]
    
    def can_handle(self, query: str) -> bool:
        """Check if query is about compliance"""
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.keywords)
    
    async def process(self, query: str, context: Dict[str, Any]) -> AgentResponse:
        """Check compliance using RAG"""
        response = await self.rag_pipeline.query(query, top_k=4)
        
        # Add compliance framing
        compliance_answer = self._format_compliance_response(response.answer)
        
        return AgentResponse(
            answer=compliance_answer,
            sources=response.sources,
            confidence=response.confidence or 0.0,
            metadata={"agent": "compliance"}
        )
    
    def _format_compliance_response(self, answer: str) -> str:
        """Format response with compliance framing"""
        return f"""**Compliance Assessment:**

{answer}

**Note:** This assessment is based on available documentation. For authoritative compliance decisions, please consult with the legal department or relevant regulatory authority.
"""


class AgentOrchestrator:
    """Orchestrates multiple agents using MCP pattern"""
    
    def __init__(self):
        self.agents: List[BaseAgent] = [
            GISAgent(),           # Check geo first (most specific)
            ComplianceAgent(),    # Then compliance
            SummaryAgent(),       # Then summary
            DocumentAgent(),      # Finally general documents (fallback)
        ]
        self.default_agent = DocumentAgent()
        logger.info(f"Initialized orchestrator with {len(self.agents)} agents")
    
    async def route_query(
        self,
        request: QueryRequest
    ) -> AgentResponse:
        """
        Route query to appropriate agent(s)
        
        Args:
            request: Query request
            
        Returns:
            Agent response
        """
        query = request.query
        
        # If specific agents requested, try those first
        if request.agents:
            selected_agent = self._get_agent_by_name(request.agents[0])
            if selected_agent:
                logger.info(f"Using requested agent: {request.agents[0]}")
                context = {
                    "top_k": request.top_k,
                    "filter": request.filters
                }
                return await selected_agent.process(query, context)
        
        # Otherwise, find best agent
        for agent in self.agents:
            if agent.can_handle(query):
                agent_name = agent.__class__.__name__
                logger.info(f"Routing to {agent_name}")
                context = {
                    "top_k": request.top_k,
                    "filter": request.filters
                }
                return await agent.process(query, context)
        
        # Fallback to default document agent
        logger.info("Using default document agent")
        context = {"top_k": request.top_k, "filter": request.filters}
        return await self.default_agent.process(query, context)
    
    def _get_agent_by_name(self, name: str) -> Optional[BaseAgent]:
        """Get agent by name"""
        name_lower = name.lower()
        for agent in self.agents:
            agent_name = agent.__class__.__name__.lower()
            if name_lower in agent_name:
                return agent
        return None


# Singleton instance
_orchestrator_instance: Optional[AgentOrchestrator] = None


def get_orchestrator() -> AgentOrchestrator:
    """Get or create orchestrator singleton"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = AgentOrchestrator()
    return _orchestrator_instance
