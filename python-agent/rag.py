import os
from typing import List, Optional, Dict, Any
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import logging

from vector_store import get_vector_store
from models import QueryRequest, QueryResponse, Source, AgentResponse

logger = logging.getLogger(__name__)


class RAGPipeline:
    """Retrieval-Augmented Generation pipeline"""
    
    def __init__(self):
        self.vector_store = get_vector_store()
        self.llm = self._initialize_llm()
        self.use_mock = os.getenv("USE_MOCK_LLM", "false").lower() == "true"
    
    def _initialize_llm(self):
        """Initialize LLM"""
        use_mock = os.getenv("USE_MOCK_LLM", "false").lower() == "true"
        
        if use_mock:
            logger.info("Using mock LLM (development mode)")
            return MockLLM()
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("No OPENAI_API_KEY found, falling back to mock LLM")
            return MockLLM()
        
        model = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
        return ChatOpenAI(
            openai_api_key=api_key,
            model=model,
            temperature=0.7
        )
    
    async def query(
        self,
        query: str,
        top_k: int = 4,
        filter: Optional[Dict[str, Any]] = None
    ) -> QueryResponse:
        """
        Execute RAG query pipeline
        
        Args:
            query: User's natural language query
            top_k: Number of documents to retrieve
            filter: Optional metadata filter
            
        Returns:
            QueryResponse with answer and sources
        """
        try:
            # Retrieve relevant documents
            docs_with_scores = self.vector_store.similarity_search_with_score(
                query=query,
                k=top_k,
                filter=filter
            )
            
            if not docs_with_scores:
                return self._fallback_response(
                    query,
                    "No relevant documents found in the knowledge base."
                )
            
            # Separate docs and scores
            docs = [doc for doc, score in docs_with_scores]
            scores = [score for doc, score in docs_with_scores]
            
            # Generate answer using LLM
            answer = await self._generate_answer(query, docs)
            
            # Create source citations
            sources = self._create_sources(docs, scores)
            
            # Calculate confidence (based on retrieval scores)
            confidence = self._calculate_confidence(scores)
            
            return QueryResponse(
                answer=answer,
                sources=sources,
                agent_used="document",
                confidence=confidence,
                fallback=self.use_mock,
                raw_llm_output=answer
            )
            
        except Exception as e:
            logger.error(f"Error in RAG pipeline: {e}")
            return self._fallback_response(
                query,
                f"An error occurred while processing your query: {str(e)}"
            )
    
    async def _generate_answer(self, query: str, docs: List[Document]) -> str:
        """Generate answer using LLM and retrieved documents"""
        
        # Prepare context from documents
        context = self._format_context(docs)
        
        # Create prompt
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful AI assistant for government officers managing a smart city.
Use the following document excerpts to answer the user's question accurately and concisely.

IMPORTANT INSTRUCTIONS:
- Base your answer ONLY on the provided documents
- If the documents don't contain enough information, say so
- Keep answers under 200 words
- Use professional, clear language
- When referencing information, mention the source document
- For compliance questions, cite specific clauses or sections

Context from documents:
{context}"""),
            ("human", "{query}")
        ])
        
        # Generate response
        if isinstance(self.llm, MockLLM):
            return self.llm.generate(query, context)
        else:
            messages = prompt_template.format_messages(query=query, context=context)
            response = await self.llm.ainvoke(messages)
            return response.content
    
    def _format_context(self, docs: List[Document]) -> str:
        """Format documents into context string"""
        context_parts = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "Unknown")
            page = doc.metadata.get("page", "")
            page_str = f" (Page {page})" if page else ""
            
            context_parts.append(
                f"[Source {i}: {source}{page_str}]\n{doc.page_content}\n"
            )
        
        return "\n---\n".join(context_parts)
    
    def _create_sources(self, docs: List[Document], scores: List[float]) -> List[Source]:
        """Create source citations from documents"""
        sources = []
        for doc, score in zip(docs, scores):
            # Extract snippet (first 200 chars)
            snippet = doc.page_content[:200]
            if len(doc.page_content) > 200:
                snippet += "..."
            
            sources.append(Source(
                id=doc.metadata.get("doc_id", "unknown"),
                title=doc.metadata.get("source", "Unknown Document"),
                page=doc.metadata.get("page"),
                snippet=snippet,
                score=float(score) if score else None
            ))
        
        return sources
    
    def _calculate_confidence(self, scores: List[float]) -> float:
        """Calculate confidence score from retrieval scores"""
        if not scores:
            return 0.0
        
        # Lower distance = higher confidence
        # Normalize to 0-1 range (assuming distances are typically 0-2)
        avg_score = sum(scores) / len(scores)
        confidence = max(0.0, min(1.0, 1.0 - (avg_score / 2.0)))
        return round(confidence, 2)
    
    def _fallback_response(self, query: str, message: str) -> QueryResponse:
        """Create fallback response when no documents found or error occurs"""
        return QueryResponse(
            answer=message,
            sources=[],
            agent_used="fallback",
            confidence=0.0,
            fallback=True
        )


class MockLLM:
    """Mock LLM for development without API key"""
    
    def generate(self, query: str, context: str) -> str:
        """Generate mock response based on query keywords"""
        query_lower = query.lower()
        
        # Keyword-based responses
        if any(word in query_lower for word in ["pothole", "road", "repair"]):
            return """Based on the standard operating procedures, pothole repairs should be completed within 7-10 business days of reporting. The maintenance team must:

1. Inspect and assess the severity within 24 hours
2. Prioritize based on traffic volume and safety risk
3. Deploy repair crew within the specified timeframe
4. Update the complaint status in the system

For urgent cases affecting major roads, the timeline is reduced to 48 hours."""

        elif any(word in query_lower for word in ["water", "supply", "quality"]):
            return """According to water supply management guidelines, water quality must meet WHO standards. Key requirements include:

1. Daily testing of pH, turbidity, and chlorine levels
2. Monthly testing for bacteriological parameters
3. Quarterly comprehensive analysis including heavy metals
4. Immediate notification to health department if standards are breached

Citizens should report water quality issues through the complaint portal."""

        elif any(word in query_lower for word in ["complaint", "ward", "status"]):
            return """The complaint management system tracks all citizen grievances by ward. Statistics show:

- Average resolution time: 5-7 days
- Most common complaint types: Road maintenance, water supply, street lighting
- Wards with highest complaints typically receive additional resource allocation

Officers can filter complaints by ward, type, date range, and status in the dashboard."""

        elif any(word in query_lower for word in ["compliance", "sop", "regulation"]):
            return """All municipal operations must comply with established SOPs and regulations. Key compliance requirements:

1. Document all actions and decisions
2. Follow prescribed timelines for citizen services
3. Maintain transparency in procurement and contracting
4. Regular audits and reporting to oversight committees

Non-compliance may result in disciplinary action and legal consequences."""

        else:
            # Generic response
            return f"""I understand you're asking about: "{query}"

Based on the available information in the knowledge base, I can provide general guidance. However, for specific details and authoritative answers, I recommend:

1. Consulting the relevant policy documents
2. Checking with the department specialists
3. Reviewing recent circulars and updates

Please upload relevant documents to the system for more accurate, context-specific answers."""


# Singleton instance
_rag_pipeline_instance: Optional[RAGPipeline] = None


def get_rag_pipeline() -> RAGPipeline:
    """Get or create RAG pipeline singleton"""
    global _rag_pipeline_instance
    if _rag_pipeline_instance is None:
        _rag_pipeline_instance = RAGPipeline()
    return _rag_pipeline_instance
