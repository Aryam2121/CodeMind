"""
Research Agent - Specialized for research and information gathering
"""

import logging
from typing import Dict, Any, Optional
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from app.agents.base_agent import BaseAgent, AgentResponse

logger = logging.getLogger(__name__)


RESEARCH_AGENT_PROMPT = """You are an expert research assistant with comprehensive knowledge across many domains.

Your capabilities:
- Provide detailed explanations on complex topics
- Research and synthesize information
- Compare and contrast concepts
- Provide educational content
- Answer general knowledge questions
- Create study materials

User query: {query}

Provide a thorough, well-researched response:"""


class ResearchAgent(BaseAgent):
    """Agent specialized in research and general knowledge"""
    
    def __init__(self):
        super().__init__(
            name="Research Agent",
            description="Expert in research and information synthesis",
            system_prompt="You are an expert researcher with broad knowledge across many fields.",
            temperature=0.7
        )
        
        self.research_keywords = [
            'what is', 'who is', 'how does', 'why does',
            'explain', 'research', 'learn', 'study',
            'teach me', 'tell me about', 'information about',
            'history of', 'definition', 'meaning'
        ]
    
    def can_handle(self, query: str, context: Optional[Dict[str, Any]] = None) -> float:
        """Determine if this agent should handle the query"""
        query_lower = query.lower()
        
        # Check for research-related keywords
        keyword_matches = sum(1 for keyword in self.research_keywords if keyword in query_lower)
        
        # Check if query is a question
        is_question = any(query_lower.startswith(q) for q in ['what', 'who', 'how', 'why', 'when', 'where'])
        
        # Calculate confidence
        confidence = (keyword_matches / 3.0) + (0.3 if is_question else 0)
        
        return min(confidence, 1.0)
    
    async def process(
        self,
        query: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process research query"""
        try:
            logger.info(f"Research Agent processing query for user {user_id}")
            
            # Create prompt
            prompt = PromptTemplate(
                input_variables=["query"],
                template=RESEARCH_AGENT_PROMPT
            )
            
            chain = LLMChain(llm=self.llm, prompt=prompt)
            
            # Generate response
            response = await chain.arun(query=query)
            
            # Create agent response
            agent_response = AgentResponse(
                agent_name=self.name,
                content=response,
                metadata={
                    "query_type": "research"
                }
            )
            
            return agent_response.to_dict()
        
        except Exception as e:
            logger.error(f"Error in Research Agent: {str(e)}")
            return {
                "agent_name": self.name,
                "content": f"I encountered an error while researching: {str(e)}",
                "error": str(e)
            }


# Create singleton instance
research_agent = ResearchAgent()
