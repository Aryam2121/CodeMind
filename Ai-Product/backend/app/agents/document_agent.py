"""
Document Agent - Specialized for document understanding and Q&A
"""

import logging
from typing import Dict, Any, Optional
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from app.agents.base_agent import BaseAgent, AgentResponse
from app.rag.rag_system import rag_system

logger = logging.getLogger(__name__)


DOCUMENT_AGENT_PROMPT = """You are an expert document analysis assistant with access to the user's personal knowledge base.

Your capabilities:
- Answer questions based on uploaded documents
- Summarize documents
- Extract key information
- Compare and contrast documents
- Find specific information across multiple documents

Always cite your sources when answering.

Relevant documents:
{context}

User query: {query}

Provide a comprehensive answer with citations:"""


class DocumentAgent(BaseAgent):
    """Agent specialized in document understanding"""
    
    def __init__(self):
        super().__init__(
            name="Document Agent",
            description="Expert in document analysis and question answering",
            system_prompt="You are an expert research assistant and document analyzer.",
            temperature=0.5
        )
        
        self.document_keywords = [
            'document', 'pdf', 'file', 'paper', 'article',
            'summarize', 'summary', 'explain', 'what does',
            'according to', 'based on', 'find information',
            'read', 'content', 'extract', 'quote'
        ]
    
    def can_handle(self, query: str, context: Optional[Dict[str, Any]] = None) -> float:
        """Determine if this agent should handle the query"""
        query_lower = query.lower()
        
        # Check for document-related keywords
        keyword_matches = sum(1 for keyword in self.document_keywords if keyword in query_lower)
        
        # Check if documents are mentioned
        has_document_context = context and context.get('document_ids')
        
        # Calculate confidence
        confidence = (keyword_matches / 4.0) + (0.4 if has_document_context else 0)
        
        return min(confidence, 1.0)
    
    async def process(
        self,
        query: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process document-related query"""
        try:
            logger.info(f"Document Agent processing query for user {user_id}")
            
            # Get relevant documents from RAG
            document_results = rag_system.search_documents(
                query=query,
                user_id=user_id,
                k=5
            )
            
            # Format context
            if document_results:
                context_text = "\n\n".join([
                    f"Document: {r['metadata'].get('filename', 'unknown')}\n"
                    f"Source: {r['metadata'].get('source', 'unknown')}\n"
                    f"Content:\n{r['content']}"
                    for r in document_results
                ])
            else:
                context_text = "No relevant documents found. You may need to upload documents first."
            
            # Create prompt
            prompt = PromptTemplate(
                input_variables=["context", "query"],
                template=DOCUMENT_AGENT_PROMPT
            )
            
            chain = LLMChain(llm=self.llm, prompt=prompt)
            
            # Generate response
            response = await chain.arun(
                context=context_text,
                query=query
            )
            
            # Create agent response
            agent_response = AgentResponse(
                agent_name=self.name,
                content=response,
                sources=[
                    {
                        "filename": r['metadata'].get('filename'),
                        "document_id": r['metadata'].get('document_id'),
                        "excerpt": r['content'][:200] + "...",
                        "score": r.get('similarity_score')
                    }
                    for r in document_results
                ],
                metadata={
                    "documents_found": len(document_results)
                }
            )
            
            return agent_response.to_dict()
        
        except Exception as e:
            logger.error(f"Error in Document Agent: {str(e)}")
            return {
                "agent_name": self.name,
                "content": f"I encountered an error while searching documents: {str(e)}",
                "error": str(e)
            }


# Create singleton instance
document_agent = DocumentAgent()
