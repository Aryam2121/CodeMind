"""
Agent Router - Routes queries to the most appropriate agent
"""

import logging
from typing import Dict, Any, Optional, List
from app.agents.code_agent import code_agent
from app.agents.document_agent import document_agent
from app.agents.task_agent import task_agent
from app.agents.research_agent import research_agent
from app.core.config import settings

logger = logging.getLogger(__name__)


class AgentRouter:
    """Routes queries to the most appropriate specialized agent"""
    
    def __init__(self):
        """Initialize router with all available agents"""
        self.agents = []
        
        # Register agents based on settings
        if settings.ENABLE_CODE_AGENT:
            self.agents.append(code_agent)
            logger.info("Code Agent registered")
        
        if settings.ENABLE_DOCUMENT_AGENT:
            self.agents.append(document_agent)
            logger.info("Document Agent registered")
        
        if settings.ENABLE_TASK_AGENT:
            self.agents.append(task_agent)
            logger.info("Task Agent registered")
        
        if settings.ENABLE_RESEARCH_AGENT:
            self.agents.append(research_agent)
            logger.info("Research Agent registered")
        
        logger.info(f"Agent Router initialized with {len(self.agents)} agents")
    
    def route_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Determine which agent should handle the query
        
        Args:
            query: User query
            context: Additional context
        
        Returns:
            Name of the selected agent
        """
        # Calculate confidence scores for each agent
        scores = []
        for agent in self.agents:
            confidence = agent.can_handle(query, context)
            scores.append((agent.name, confidence))
            logger.debug(f"{agent.name} confidence: {confidence:.2f}")
        
        # Sort by confidence
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Select agent with highest confidence
        if scores and scores[0][1] > 0.3:
            selected_agent = scores[0][0]
            logger.info(f"Routed to {selected_agent} (confidence: {scores[0][1]:.2f})")
            return selected_agent
        
        # Default to research agent for general queries
        logger.info("Using Research Agent as fallback")
        return "Research Agent"
    
    async def process_query(
        self,
        query: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Route and process a query
        
        Args:
            query: User query
            user_id: User ID
            context: Additional context
        
        Returns:
            Agent response
        """
        try:
            # Route to appropriate agent
            agent_name = self.route_query(query, context)
            
            # Find and execute agent
            agent = next((a for a in self.agents if a.name == agent_name), None)
            
            if agent:
                response = await agent.process(query, user_id, context)
                return response
            else:
                logger.error(f"Agent {agent_name} not found")
                return {
                    "agent_name": "Error",
                    "content": "Could not find appropriate agent to handle your query.",
                    "error": "Agent not found"
                }
        
        except Exception as e:
            logger.error(f"Error in agent router: {str(e)}")
            return {
                "agent_name": "Error",
                "content": f"An error occurred while processing your query: {str(e)}",
                "error": str(e)
            }
    
    def get_available_agents(self) -> List[Dict[str, str]]:
        """Get list of available agents"""
        return [
            {
                "name": agent.name,
                "description": agent.description
            }
            for agent in self.agents
        ]


# Create singleton instance
agent_router = AgentRouter()
