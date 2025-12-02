"""
Tests for agent orchestration
"""
import pytest
from unittest.mock import Mock, AsyncMock

from agents import (
    DocumentAgent, GISAgent, SummaryAgent, ComplianceAgent,
    AgentOrchestrator
)
from models import QueryRequest


@pytest.fixture
def orchestrator():
    """Create orchestrator instance"""
    return AgentOrchestrator()


def test_document_agent_can_handle():
    """Test document agent query detection"""
    agent = DocumentAgent()
    
    assert agent.can_handle("What does the policy document say?")
    assert agent.can_handle("Show me the SOP for this")
    assert not agent.can_handle("Where are the potholes?")


def test_gis_agent_can_handle():
    """Test GIS agent query detection"""
    agent = GISAgent()
    
    assert agent.can_handle("Show complaints in Ward 12")
    assert agent.can_handle("Where are the potholes?")
    assert agent.can_handle("Nearby complaints")
    assert not agent.can_handle("What is the policy?")


def test_summary_agent_can_handle():
    """Test summary agent query detection"""
    agent = SummaryAgent()
    
    assert agent.can_handle("Summarize the document")
    assert agent.can_handle("Give me an overview")
    assert agent.can_handle("Extract key points")
    assert not agent.can_handle("Where is Ward 5?")


def test_compliance_agent_can_handle():
    """Test compliance agent query detection"""
    agent = ComplianceAgent()
    
    assert agent.can_handle("Is this compliant with regulations?")
    assert agent.can_handle("Check compliance")
    assert agent.can_handle("Legal requirements?")
    assert not agent.can_handle("Show map")


@pytest.mark.asyncio
async def test_orchestrator_routing(orchestrator):
    """Test query routing to correct agent"""
    
    # GIS query
    request = QueryRequest(query="Show complaints in Ward 12")
    # Note: This would call real agents, so we'll just test routing logic
    
    # Check which agent would handle it
    gis_agent = orchestrator._get_agent_by_name("gis")
    assert gis_agent is not None
    assert gis_agent.can_handle(request.query)


def test_extract_ward():
    """Test ward extraction from query"""
    agent = GISAgent()
    
    assert agent._extract_ward("Show Ward 12 complaints") == "Ward 12"
    assert agent._extract_ward("complaints in ward 5") == "Ward 5"
    assert agent._extract_ward("all complaints") is None


def test_extract_days():
    """Test days extraction from query"""
    agent = GISAgent()
    
    assert agent._extract_days("last 30 days") == 30
    assert agent._extract_days("past 7 days") == 7
    assert agent._extract_days("complaints in the last 14 days") == 14
    assert agent._extract_days("all complaints") is None
