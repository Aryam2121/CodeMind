"""
Code Agent - Specialized for code analysis, debugging, and generation
"""

import logging
from typing import Dict, Any, Optional, List
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from app.agents.base_agent import BaseAgent, AgentResponse
from app.rag.code_rag import code_rag_system

logger = logging.getLogger(__name__)


CODE_AGENT_PROMPT = """You are an expert code analysis and generation assistant. You have access to the user's entire codebase through RAG.

Your capabilities:
- Explain code functionality
- Find bugs and suggest fixes
- Analyze architecture and design patterns
- Generate new code or functions
- Refactor existing code
- Create documentation
- Suggest improvements

When analyzing code, be:
- Precise and technical
- Provide examples
- Cite specific files and line numbers when relevant
- Suggest best practices

Context from codebase:
{context}

User query: {query}

Provide a detailed, helpful response:"""


class CodeAgent(BaseAgent):
    """Agent specialized in code-related tasks"""
    
    def __init__(self):
        super().__init__(
            name="Code Agent",
            description="Expert in code analysis, debugging, and generation",
            system_prompt="You are an expert software engineer and code analyst.",
            temperature=0.3  # Lower temperature for more precise code responses
        )
        
        self.code_keywords = [
            'code', 'function', 'class', 'bug', 'error', 'debug',
            'implement', 'refactor', 'optimize', 'algorithm',
            'syntax', 'compile', 'test', 'api', 'method',
            'variable', 'parameter', 'return', 'import'
        ]
    
    def can_handle(self, query: str, context: Optional[Dict[str, Any]] = None) -> float:
        """Determine if this agent should handle the query"""
        query_lower = query.lower()
        
        # Check for code-related keywords
        keyword_matches = sum(1 for keyword in self.code_keywords if keyword in query_lower)
        
        # Check if code context is provided
        has_code_context = context and context.get('project_id')
        
        # Calculate confidence
        confidence = (keyword_matches / 5.0) + (0.3 if has_code_context else 0)
        
        return min(confidence, 1.0)
    
    async def process(
        self,
        query: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process code-related query"""
        try:
            logger.info(f"Code Agent processing query for user {user_id}")
            
            # Get relevant code snippets from RAG
            project_id = context.get('project_id') if context else None
            
            code_results = code_rag_system.search_code(
                query=query,
                user_id=user_id,
                project_id=project_id,
                k=10
            )
            
            # Format context
            if code_results:
                context_text = "\n\n".join([
                    f"File: {r['metadata'].get('file_path', 'unknown')}\n"
                    f"Lines: {r['metadata'].get('chunk_index', 0) * 100}-"
                    f"{(r['metadata'].get('chunk_index', 0) + 1) * 100}\n"
                    f"Code:\n```\n{r['content']}\n```"
                    for r in code_results[:5]
                ])
            else:
                context_text = "No relevant code found in the codebase."
            
            # Create prompt
            prompt = PromptTemplate(
                input_variables=["context", "query"],
                template=CODE_AGENT_PROMPT
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
                        "file": r['metadata'].get('file_path'),
                        "content": r['content'][:200] + "...",
                        "score": r.get('similarity_score')
                    }
                    for r in code_results[:5]
                ],
                metadata={
                    "code_snippets_found": len(code_results),
                    "project_id": project_id
                }
            )
            
            return agent_response.to_dict()
        
        except Exception as e:
            logger.error(f"Error in Code Agent: {str(e)}")
            return {
                "agent_name": self.name,
                "content": f"I encountered an error while analyzing the code: {str(e)}",
                "error": str(e)
            }


# Create singleton instance
code_agent = CodeAgent()
