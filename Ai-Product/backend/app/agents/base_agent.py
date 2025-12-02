"""
Base Agent class for all specialized agents
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage

from app.core.config import settings

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(
        self,
        name: str,
        description: str,
        system_prompt: str,
        model: str = None,
        temperature: float = None
    ):
        """
        Initialize base agent
        
        Args:
            name: Agent name
            description: Agent description
            system_prompt: System prompt for the agent
            model: LLM model to use
            temperature: Temperature for generation
        """
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=model or settings.DEFAULT_LLM_MODEL,
            temperature=temperature or settings.DEFAULT_TEMPERATURE,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        logger.info(f"Initialized {self.name} agent")
    
    def format_messages(
        self,
        query: str,
        context: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None
    ) -> List[Any]:
        """Format messages for the LLM"""
        messages = [SystemMessage(content=self.system_prompt)]
        
        # Add history
        if history:
            for msg in history:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))
        
        # Add context if provided
        if context:
            query = f"Context:\n{context}\n\nQuery: {query}"
        
        # Add current query
        messages.append(HumanMessage(content=query))
        
        return messages
    
    @abstractmethod
    async def process(
        self,
        query: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a query
        
        Args:
            query: User query
            user_id: User ID
            context: Additional context
        
        Returns:
            Response dictionary
        """
        pass
    
    def can_handle(self, query: str, context: Optional[Dict[str, Any]] = None) -> float:
        """
        Determine if this agent can handle the query
        
        Returns:
            Confidence score (0-1)
        """
        return 0.0


class AgentResponse:
    """Structured agent response"""
    
    def __init__(
        self,
        agent_name: str,
        content: str,
        sources: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        confidence: float = 1.0
    ):
        self.agent_name = agent_name
        self.content = content
        self.sources = sources or []
        self.metadata = metadata or {}
        self.confidence = confidence
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "agent_name": self.agent_name,
            "content": self.content,
            "sources": self.sources,
            "metadata": self.metadata,
            "confidence": self.confidence
        }
