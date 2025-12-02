"""
Agent endpoints
"""

from fastapi import APIRouter, Depends
import logging

from app.core.security import get_current_user
from app.agents.agent_router import agent_router

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/list")
async def list_agents(
    current_user: dict = Depends(get_current_user)
):
    """List all available agents"""
    return agent_router.get_available_agents()


@router.get("/status")
async def agents_status(
    current_user: dict = Depends(get_current_user)
):
    """Get agents status"""
    agents = agent_router.get_available_agents()
    
    return {
        "total_agents": len(agents),
        "agents": agents,
        "status": "operational"
    }
